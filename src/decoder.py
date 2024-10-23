from src.instructions import *


class Decoder:
    def __init__(self, raw_data):
        self.raw_data = raw_data


class InstructionDecoder(Decoder):
    opcode = None

    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.opcode = self.extract_opcode()
        pass

    def extract_opcode(self):
        """ extract least 7 bit as opcode """
        return self.raw_data & 0x7F

    def decode(self):
        match self.opcode:
            case 0b0110011:
                return RTypeDecoder(self.raw_data).decode()
            case 0b0010011:
                return ITypeDecoder(self.raw_data).decode()
            case 0b0100011:
                return STypeDecoder(self.raw_data).decode()

            case 0b1100011:
                return BTypeDecoder(self.raw_data).decode()
            case 0b0000000:  # unused
                return UTypeDecoder(self.raw_data).decode()
            case 0b1101111:
                return JTypeDecoder(self.raw_data).decode()
            case _:
                raise ValueError("Unknown opcode")
        pass


class RTypeDecoder(InstructionDecoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        rd = (self.raw_data >> 7) & 0x1F  # bits [11:7]
        funct3 = (self.raw_data >> 12) & 0x7  # bits [14:12]
        rs1 = (self.raw_data >> 15) & 0x1F  # bits [19:15]
        rs2 = (self.raw_data >> 20) & 0x1F  # bits [24:20]
        funct7 = (self.raw_data >> 25) & 0x7F  # bits [31:25]

        return {
            "opcode": self.opcode,
            "rd": rd,
            "rs1": rs1,
            "rs2": rs2,
            "funct3": funct3,
            "funct7": funct7
        }
