from typing import Tuple

from loguru import logger
from src.state import State


def forwarding_unit(state: State) -> (int, int):
    """

    Determines the forwarding paths for the EX stage to resolve data hazards.
    Ref: Comp.Org P.320

    :param state: The current state of the pipeline, containing pipeline registers.
    :return: A tuple (forward_a, forward_b) indicating the forwarding paths for source operands.
    """
    forward_a = 0b00
    forward_b = 0b00

    # EX/MEM forwarding (highest priority)
    if (state.MEM["wrt_enable"] and
            state.MEM["Wrt_reg_addr"] != 0 and
            state.MEM["Wrt_reg_addr"] == state.EX["Rs"]):
        forward_a = 0b10
    if (state.MEM["wrt_enable"] and
            state.MEM["Wrt_reg_addr"] != 0 and
            state.MEM["Wrt_reg_addr"] == state.EX["Rt"]):
        forward_b = 0b10

    # MEM/WB forwarding (only if EX/MEM does not handle it)
    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (state.MEM["wrt_enable"] and
                 state.MEM["Wrt_reg_addr"] == state.EX["Rs"]) and
            state.WB["Wrt_reg_addr"] == state.EX["Rs"]):
        forward_a = 0b01

    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (state.MEM["wrt_enable"] and
                 state.MEM["Wrt_reg_addr"] == state.EX["Rt"]) and
            state.WB["Wrt_reg_addr"] == state.EX["Rt"]):
        forward_b = 0b01


    logger.debug(f"Forwarding: {forward_a:#b}, {forward_b:#b}")

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