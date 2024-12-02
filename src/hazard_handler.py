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

def hazard_detection_unit(state: State) -> bool:

    # Use previous EX.MemRead and previous EX.Rd
    # and the current EX.Rs1 and EX.Rs2
    if (state.EX["rd_mem"] and
            (state.EX["Read_data1"] == state.EX["Rs"] or
             state.EX["Read_data1"] == state.EX["Rt"])):
        stall = True
        logger.info("Hazard Detected.")
    else:
        stall = False
        logger.info("No Hazard Detected.")

    PCWrite = not stall
    IDWrite = not stall

    return PCWrite, IDWrite, stall
