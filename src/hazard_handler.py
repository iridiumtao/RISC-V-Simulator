from typing import Tuple

from loguru import logger
from src.state import State
from src.components import multiplexer


def forwarding_unit(state: State, next_state: State) -> (int, int):
    """

    Determines the forwarding paths for the EX stage to resolve data hazards.
    Ref: Comp.Org P.320

    :param state: The current state of the pipeline, containing pipeline registers.
    :param next_state:
    :return: A tuple (forward_a, forward_b) indicating the forwarding paths for source operands.
    """
    forward_a = 0b00
    forward_b = 0b00

    hint_a = "EX"
    hint_b = "EX"

    # EX/MEM forwarding (highest priority)
    if (next_state.MEM["wrt_enable"] and
            next_state.MEM["Wrt_reg_addr"] != 0 and
            next_state.MEM["Wrt_reg_addr"] == next_state.EX["Rs"]):
        forward_a = 0b10
        hint_a = "MEM"
    if (next_state.MEM["wrt_enable"] and
            next_state.MEM["Wrt_reg_addr"] != 0 and
            next_state.MEM["Wrt_reg_addr"] == next_state.EX["Rt"]):
        forward_b = 0b10
        hint_b = "MEM"

    # MEM/WB forwarding (only if EX/MEM does not handle it)
    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (next_state.MEM["wrt_enable"] and
                 next_state.MEM["Wrt_reg_addr"] == next_state.EX["Rs"]) and
            state.WB["Wrt_reg_addr"] == next_state.EX["Rs"]):
        forward_a = 0b01
        hint_a = "WB"

    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (next_state.MEM["wrt_enable"] and
                 next_state.MEM["Wrt_reg_addr"] == next_state.EX["Rt"]) and
            state.WB["Wrt_reg_addr"] == next_state.EX["Rt"]):
        forward_b = 0b01
        hint_b = "WB"


    logger.debug(f"Forwarding: {forward_a:#b} (Source:{hint_a}), {forward_b:#b} (Source:{hint_b})")

    return forward_a, forward_b

def hazard_detection_unit(state: State) -> Tuple[bool, bool, bool]:
    """
    Detects hazards in the pipeline and determines whether to stall the pipeline.

    Use previous EX.MemRead and *previous* EX.Rd and the *current* EX.Rs1 and EX.Rs2

    :param state: The current state of the pipeline, containing pipeline registers.
    :return: A tuple (PCWrite, IDWrite, stall) indicating whether to write to the PC,
             whether to write to the ID stage, and whether a stall is needed.
    """
    logger.debug(f"previous EX.rd_mem: {state.EX["rd_mem"]}, previous EX.Rd(Wrt_reg_addr): {state.EX["Wrt_reg_addr"]}")
    logger.debug(f"current EX.Rs1: {state.EX["Rs"]}, current EX.Rs2(Rt): {state.EX["Rt"]}")

    if (state.EX["rd_mem"] and
            state.EX["Wrt_reg_addr"] != 0 and
            (state.EX["Wrt_reg_addr"] == state.EX["Rs"] or
             state.EX["Wrt_reg_addr"] == state.EX["Rt"])):
        stall = True
        logger.warning("Hazard Detected.")
    else:
        stall = False
        logger.info("No Hazard Detected.")

    PCWrite = not stall
    IDWrite = not stall

    return PCWrite, IDWrite, stall


def forwarding_unit_for_branch(rs1: int, rs2: int, state: State, next_state: State) -> (int, int):
    """
    Determines the forwarding paths for the ID stage to resolve data hazards for branch instructions.

    :param rs1: source registers used by the branch instruction.
    :param rs2: source registers used by the branch instruction.
    :param state: The current state of the pipeline, containing pipeline registers.
    :return: A tuple (forward_a, forward_b) indicating the forwarding paths for source operands.
    """
    forward_a = 0b00  # Default: Use value from the register file
    forward_b = 0b00

    # EX/MEM forwarding (highest priority)
    if (next_state.MEM["wrt_enable"] and
            next_state.MEM["Wrt_reg_addr"] != 0 and
            next_state.MEM["Wrt_reg_addr"] == rs1):
        forward_a = 0b10
    if (next_state.MEM["wrt_enable"] and
            next_state.MEM["Wrt_reg_addr"] != 0 and
            next_state.MEM["Wrt_reg_addr"] == rs2):
        forward_b = 0b10

    # MEM/WB forwarding (only if EX/MEM does not handle it)
    if (next_state.WB["wrt_enable"] and
            next_state.WB["Wrt_reg_addr"] != 0 and
            not (next_state.MEM["wrt_enable"] and
                 next_state.MEM["Wrt_reg_addr"] == rs1) and
            next_state.WB["Wrt_reg_addr"] == rs1):
        forward_a = 0b01
    if (next_state.WB["wrt_enable"] and
            next_state.WB["Wrt_reg_addr"] != 0 and
            not (next_state.MEM["wrt_enable"] and
                 next_state.MEM["Wrt_reg_addr"] == rs2) and
            next_state.WB["Wrt_reg_addr"] == rs2):
        forward_b = 0b01

    return forward_a, forward_b


# 模擬不同狀態的 State class
from unittest import TestCase


class TestForwardingUnit(TestCase):

    def setUp(self):
        """ 初始化 state 狀態 """
        self.state = State()

        # 初始化 pipeline registers
        self.state.EX = {"Rs": 1, "Rt": 2, "Wrt_reg_addr": 0, "Read_data1": 0, "Read_data2": 0}
        self.state.MEM = {"wrt_enable": 0, "Wrt_reg_addr": 0, "ALUresult": 0}
        self.state.WB = {"wrt_enable": 0, "Wrt_reg_addr": 0, "Wrt_data": 0}

    def test_ex_mem_forwarding(self):
        """ 測試 EX/MEM forwarding """
        self.state.EX["Rs"] = 1
        self.state.MEM["wrt_enable"] = 1
        self.state.MEM["Wrt_reg_addr"] = 1  # Rs forwarding match

        forward_a, forward_b = forwarding_unit(self.state)
        self.assertEqual(forward_a, 0b10)
        self.assertEqual(forward_b, 0b00)

    def test_mem_wb_forwarding(self):
        """ 測試 MEM/WB forwarding """
        self.state.EX["Rt"] = 2
        self.state.WB["wrt_enable"] = 1
        self.state.WB["Wrt_reg_addr"] = 2  # Rt forwarding match

        forward_a, forward_b = forwarding_unit(self.state)
        self.assertEqual(forward_a, 0b00)
        self.assertEqual(forward_b, 0b01)

    def test_no_forwarding(self):
        """ 測試無 forwarding """
        self.state.EX["Rs"] = 3
        self.state.EX["Rt"] = 4
        self.state.MEM["Wrt_reg_addr"] = 1
        self.state.WB["Wrt_reg_addr"] = 2

        forward_a, forward_b = forwarding_unit(self.state)
        self.assertEqual(forward_a, 0b00)
        self.assertEqual(forward_b, 0b00)

    def test_ex_mem_priority(self):
        """ 測試 EX/MEM forwarding 優先級 """
        self.state.EX["Rs"] = 1
        self.state.MEM["wrt_enable"] = 1
        self.state.MEM["Wrt_reg_addr"] = 1  # Rs forwarding match (EX/MEM)
        self.state.WB["wrt_enable"] = 1
        self.state.WB["Wrt_reg_addr"] = 1  # Rs forwarding match (MEM/WB)

        forward_a, forward_b = forwarding_unit(self.state)
        self.assertEqual(forward_a, 0b10)  # EX/MEM 應優先
        self.assertEqual(forward_b, 0b00)

    def test_forwarding_unit_for_branch(self):
        # 模擬 pipeline 狀態
        state = State()
        state.MEM = {"wrt_enable": True, "Wrt_reg_addr": 3, "ALUresult": 42}
        state.WB = {"wrt_enable": True, "Wrt_reg_addr": 4, "Wrt_data": 99}
        state.ID = {"Rs1": 3, "Rs2": 4, "Read_data1": 10, "Read_data2": 20}
        print(state)

        # 測試 forwarding
        forward_a, forward_b = forwarding_unit_for_branch(3, 4, state)

        # 期望結果
        assert forward_a == 0b10, f"Expected 0b10, got {forward_a}"
        assert forward_b == 0b01, f"Expected 0b01, got {forward_b}"

        # 使用 multiplexer 測試數值
        operand_a = multiplexer(forward_a, state.ID["Read_data1"], state.WB["Wrt_data"], state.MEM["ALUresult"])
        operand_b = multiplexer(forward_b, state.ID["Read_data2"], state.WB["Wrt_data"], state.MEM["ALUresult"])

        assert operand_a == 42, f"Expected 42, got {operand_a}"
        assert operand_b == 99, f"Expected 99, got {operand_b}"

        print("All tests passed!")
