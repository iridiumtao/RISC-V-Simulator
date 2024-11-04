from loguru import logger

def alu_control_unit(alu_op, func_code):
    """ALU Control logic for RISC-V simulator.

    Determines the ALU operation based on ALUOp, Func3, and Func7 fields.

    `func_code` parameter should be derived as `Instruction[30, 14-12]` in the main code.

    **ALU control define reference Comp.Org p.A-37 is WRONG**

    :param alu_op:
        `00`: Load/store (add operation),
        `01`: Branch (subtract operation),
        `10`: R-type, with operation determined by `func_code` input.

    :param func_code: combination of Instr[30, 14:12] with `func_code` = (Func7Bit << 3) | Func3
    :return: alu_control: 4-bit ALU control signal
    """

    if alu_op == 0b00:
        alu_control = 0b0010  # add for lw/sw
        logger.debug(f"ALU Control: {alu_control} (Load/Store)")
    elif alu_op == 0b01:
        alu_control = 0b0110  # subtract for branch
        logger.debug(f"ALU Control: {alu_control} (Branch)")
    elif alu_op == 0b10:
        if func_code == 0b0000:
            alu_control = 0b0010  # ADD
            logger.debug(f"ALU Control: {alu_control} (ADD)")
        elif func_code == 0b1000:
            alu_control = 0b0110  # SUB
            logger.debug(f"ALU Control: {alu_control} (SUB)")
        elif func_code == 0b0111:
            alu_control = 0b0000  # AND
            logger.debug(f"ALU Control: {alu_control} (AND)")
        elif func_code == 0b0110:
            alu_control = 0b0001  # OR
            logger.debug(f"ALU Control: {alu_control} (OR)")
        elif func_code == 0b0100:
            alu_control = 0b0111  # XOR
            logger.debug(f"ALU Control: {alu_control} (XOR)")
        else:
            alu_control = 0b1111  # Should not happen
            logger.error(f"ALU Control: {alu_control} (Undefined)")
            logger.error(f"alu_op: {alu_op}, func_code: {func_code}")
    else:
        alu_control = 0b1111  # Undefined behavior
        logger.error(f"ALU Control: {alu_control} (Undefined)")
        logger.error(f"alu_op: {alu_op}, func_code: {func_code}")
    return alu_control


def arithmetic_logic_unit(alu_control, a, b):
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

    logger.debug(f"ALU Result: {alu_result}, Zero: {zero}")

    return zero, alu_result

def adder(a, b):
    return a + b


def control_unit(opcode: int):
    control_signals = {
        "ALUSrc": 0x00,
        "MemtoReg": 0,
        "RegWrite": 0,
        "MemRead": 0,
        "MemWrite": 0,
        "Branch": 0,
        "ALUOp": 0x00
    }

    halt = False

    if opcode == 0b0110011:  # R-type
        logger.debug(f"Opcode: {opcode} (R-type)")
        control_signals.update({
            "ALUSrc": 0,
            "MemtoReg": 0,
            "RegWrite": 1,
            "MemRead": 0,
            "MemWrite": 0,
            "Branch": 0,
            "ALUOp": 0b10
        })
    elif opcode == 0b0010011:  # I-type
        logger.debug(f"Opcode: {opcode} (I-type)")
        control_signals.update({
            "ALUSrc": 1,
            "MemtoReg": 0,
            "RegWrite": 1,
            "MemRead": 0,
            "MemWrite": 0,
            "Branch": 0,
            "ALUOp": 0b10
        })
    elif opcode == 0b0000011:  # Load
        logger.debug(f"Opcode: {opcode} (Load)")
        control_signals.update({
            "ALUSrc": 1,
            "MemtoReg": 1,
            "RegWrite": 1,
            "MemRead": 1,
            "MemWrite": 0,
            "Branch": 0,
            "ALUOp": 0b00
        })
    elif opcode == 0b0100011:  # Store
        logger.debug(f"Opcode: {opcode} (Store)")
        control_signals.update({
            "ALUSrc": 1,
            "MemtoReg": None,
            "RegWrite": 0,
            "MemRead": 0,
            "MemWrite": 1,
            "Branch": 0,
            "ALUOp": 0b00
        })
    elif opcode == 0b1100011:  # Branch
        logger.debug(f"Opcode: {opcode} (Branch)")
        control_signals.update({
            "ALUSrc": 0,
            "MemtoReg": None,
            "RegWrite": 0,
            "MemRead": 0,
            "MemWrite": 0,
            "Branch": 1,
            "ALUOp": 0b01
        })
    elif opcode == 0b1101111:  # JAL
        logger.debug(f"Opcode: {opcode} (JAL)")
        control_signals.update({
            "ALUSrc": None,
            "MemtoReg": None,
            "RegWrite": 1,
            "MemRead": 0,
            "MemWrite": 0,
            "Branch": None,
            "ALUOp": None
        })
    elif opcode == 0b1111111: # HALT
        logger.debug(f"Opcode: {opcode} (HALT)")
        halt = True
    elif opcode == 0b0000000:  # 0
        pass
    else:
        raise ValueError("Unsupported opcode")

    return control_signals, halt


def imm_gen(opcode: int, instr: int) -> int:
    """
    Generate the immediate value based on the opcode and instruction.

    :param opcode: The opcode of the instruction
    :param instr: The 32-bit instruction
    :return: The 32-bit immediate value with proper sign extension.
    """
    if opcode == 0b0010011 or opcode == 0b0000011:  # I-type (e.g., addi, lw)
        # Immediate is in bits [31:20]
        imm = (instr >> 20) & 0xFFF  # Extract 12 bits
        if imm & 0x800:  # Check if sign bit (bit 11) is set
            imm |= 0xFFFFF000  # Sign extend to 32 bits
        logger.debug(f"Immediate: {imm:032b} ({imm})")
        return imm

    elif opcode == 0b0100011:  # S-type (e.g., sw)
        # Immediate is in bits [31:25] and [11:7]
        imm = ((instr >> 25) << 5) | ((instr >> 7) & 0x1F)  # Combine bits
        if imm & 0x800:  # Check if sign bit (bit 11) is set
            imm |= 0xFFFFF000  # Sign extend to 32 bits
        logger.debug(f"Immediate: {imm:032b} ({imm})")
        return imm

    elif opcode == 0b1100011:  # B-type (e.g., beq)
        # Immediate is in bits [31], [7], [30:25], and [11:8]
        imm = ((instr >> 31) << 12) | (((instr >> 7) & 0x1) << 11) | \
              (((instr >> 25) & 0x3F) << 5) | ((instr >> 8) & 0xF) << 1
        if imm & 0x1000:  # Check if sign bit (bit 12) is set
            imm |= 0xFFFFE000  # Sign extend to 32 bits
        logger.debug(f"Immediate: {imm:032b} ({imm})")
        return imm

    elif opcode == 0b0110111 or opcode == 0b0010111:  # U-type (e.g., lui, auipc)
        # Immediate is in bits [31:12]
        imm = (instr & 0xFFFFF000)  # Upper 20 bits, zero-extended
        logger.debug(f"Immediate: {imm:032b} ({imm})")
        return imm

    elif opcode == 0b1101111:  # J-type (e.g., jal)
        # Immediate is in bits [31], [19:12], [20], and [30:21]
        imm = ((instr >> 31) << 20) | (((instr >> 12) & 0xFF) << 12) | \
              (((instr >> 20) & 0x1) << 11) | ((instr >> 21) & 0x3FF) << 1
        if imm & 0x100000:  # Check if sign bit (bit 20) is set
            imm |= 0xFFE00000  # Sign extend to 32 bits
        logger.debug(f"Immediate: {imm:032b} ({imm})")
        return imm

    else:
        logger.debug(f"Immediate: 0 (No Imm)")
        return 0 # Default immediate (shouldn't reach here for valid instructions)

def multiplexer(a, b, select):
    if select == 0:
        return a
    else:
        return b