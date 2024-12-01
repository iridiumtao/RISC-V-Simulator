from loguru import logger


def forwarding_unit(state) -> (int, int):
    """

    Determines the forwarding paths for the EX stage to resolve data hazards.
    Ref: Comp.Org P.320

    :param state: The current state of the pipeline, containing pipeline registers.
    :return: A tuple (forward_a, forward_b) indicating the forwarding paths for source operands.
    """
    forward_a = 0b00
    forward_b = 0b00

    # EX/MEM forwarding
    if (state.MEM["wrt_enable"] and
            state.MEM["Wrt_reg_addr"] != 0 and
            state.MEM["Wrt_reg_addr"] == state.EX["Rs"]):
        forward_a = 0b10
    if (state.MEM["wrt_enable"] and
            state.MEM["Wrt_reg_addr"] != 0 and
            state.MEM["Wrt_reg_addr"] == state.EX["Rt"]):
        forward_b = 0b10

    # MEM/WB forwarding with additional MEM hazard check
    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (state.MEM["wrt_enable"] and
                 state.MEM["Wrt_reg_addr"] != 0 and
                 state.MEM["Wrt_reg_addr"] == state.EX["Rs"]) and
            state.WB["Wrt_reg_addr"] == state.EX["Rs"]):
        forward_a = 0b01
    if (state.WB["wrt_enable"] and
            state.WB["Wrt_reg_addr"] != 0 and
            not (state.MEM["wrt_enable"] and
                 state.MEM["Wrt_reg_addr"] != 0 and
                 state.MEM["Wrt_reg_addr"] == state.EX["Rt"]) and
            state.WB["Wrt_reg_addr"] == state.EX["Rt"]):
        forward_b = 0b01

    logger.debug(f"Forwarding: {forward_a:#b}, {forward_b:#b}")

    return forward_a, forward_b


def hazard_detection_unit():
    pass
