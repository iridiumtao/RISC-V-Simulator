class ADD:
    """
    Type: R
    Full Name: Addition
    Pseudocode: rd = rs1 + rs2
    Details: Store the result of rs1 + rs2 in register rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for ADD


class SUB:
    """
    Type: R
    Full Name: Subtraction
    Pseudocode: rd = rs1 - rs2
    Details: Store the result of rs1 - rs2 in register rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for SUB


class XOR:
    """
    Type: R
    Full Name: Bitwise XOR
    Pseudocode: rd = rs1 ^ rs2
    Details: Store the result of rs1 ^ rs2 in register rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for XOR


class OR:
    """
    Type: R
    Full Name: Bitwise OR
    Pseudocode: rd = rs1 | rs2
    Details: Store the result of rs1 | rs2 in register rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for OR


class AND:
    """
    Type: R
    Full Name: Bitwise AND
    Pseudocode: rd = rs1 & rs2
    Details: Store the result of rs1 & rs2 in register rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for AND


class ADDI:
    """
    Type: I
    Full Name: Add Immediate
    Pseudocode: rd = rs1 + sign_ext(imm)
    Details: Add the sign-extended immediate to register rs1 and store in rd. Overflow bits ignored.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for ADDI


class XORI:
    """
    Type: I
    Full Name: XOR Immediate
    Pseudocode: rd = rs1 ^ sign_ext(imm)
    Details: Bitwise XOR the sign-extended immediate to register rs1 and store result in rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for XORI


class ORI:
    """
    Type: I
    Full Name: OR Immediate
    Pseudocode: rd = rs1 | sign_ext(imm)
    Details: Bitwise OR the sign-extended immediate to register rs1 and store result in rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for ORI


class ANDI:
    """
    Type: I
    Full Name: AND Immediate
    Pseudocode: rd = rs1 & sign_ext(imm)
    Details: Bitwise AND the sign-extended immediate to register rs1 and store result in rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for ANDI


class JAL:
    """
    Type: J
    Full Name: Jump and Link
    Pseudocode: rd = PC + 4; PC = PC + sign_ext(imm)
    Details: Jump to PC = PC + sign_ext(imm) and store the current PC + 4 in rd.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for JAL


class BEQ:
    """
    Type: B
    Full Name: Branch if equal
    Pseudocode: PC = (rs1 == rs2)? PC + sign_ext(imm) : PC + 4
    Details: Take the branch (PC = PC + sign_ext(imm)) if rs1 is equal to rs2.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for BEQ


class BNE:
    """
    Type: B
    Full Name: Branch if not equal
    Pseudocode: PC = (rs1 != rs2)? PC + sign_ext(imm) : PC + 4
    Details: Take the branch (PC = PC + sign_ext(imm)) if rs1 is not equal to rs2.
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for BNE


class LW:
    """
    Type: I
    Full Name: Load Word
    Pseudocode: rd = mem[rs1 + sign_ext(imm)][31:0]
    Details: Load 32-bit value at memory address [rs1 + sign_ext(imm)] and store it in rd.
    """

    def execute(self, state):
        pass  # No execution stage

    def memory(self, state, dmem):
        pass


class SW:
    """
    Type: S
    Full Name: Store Word
    Pseudocode: data[rs1 + sign_ext(imm)][31:0] = rs2
    Details: Store the 32 bits of rs2 to memory address [rs1 value + sign_ext(imm)].
    """

    def execute(self, state):
        pass  # No execution stage

    def memory(self, state, dmem):
        pass


class HALT:
    """
    Type: T
    Full Name: Halt execution
    """

    def execute(self, state):
        pass

    def memory(self, state, dmem):
        pass  # No memory operations for HALT
