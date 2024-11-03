def alu_control(alu_op, func_code):
    """ALU Control logic to determine the ALU operation code based on ALUOp and FuncCode.

    ALU control defign reference Comp.Org p.A-37"""

    # Initialize alu_control to default value
    alu_control = 15  # Default case, should not happen

    # Determine alu_control based on FuncCode and ALUOp values
    if alu_op == 2:
        if func_code == 32:
            alu_control = 2  # Add
        elif func_code == 34:
            alu_control = 6  # Subtract
        elif func_code == 36:
            alu_control = 0  # AND
        elif func_code == 37:
            alu_control = 1  # OR
        else:
            alu_control = 15  # Default case, should not happen

    return alu_control


def alu(alu_control, a, b):
    """ ALU design reference Comp.Org p.A-36"""

    # Perform ALU operation based on ALU_control value
    if alu_control == 0:
        alu_result = a & b
    elif alu_control == 1:
        alu_result = a | b
    elif alu_control == 2:
        alu_result = a + b
    elif alu_control == 6:
        alu_result = a - b
    elif alu_control == 7:
        alu_result = 1 if a < b else 0
    elif alu_control == 12:
        alu_result = ~(a | b)
    else:
        alu_result = 0

    # Zero is True if alu_result is 0
    zero = (alu_result == 0)

    return alu_result, zero

def adder(a, b):
    return a + b