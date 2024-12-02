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

    # MEM/WB forwarding (lower priority)
    elif (state.WB["wrt_enable"] and
          state.WB["Wrt_reg_addr"] != 0 and
          state.WB["Wrt_reg_addr"] == state.EX["Rs"]):
        forward_a = 0b01
    elif (state.WB["wrt_enable"] and
          state.WB["Wrt_reg_addr"] != 0 and
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
