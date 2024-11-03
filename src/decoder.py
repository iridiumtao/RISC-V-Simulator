from src.instructions import *
from loguru import logger


class Decoder:
    def __init__(self, raw_data):
        # self.raw_data = int.from_bytes(raw_data.to_bytes(4, byteorder='big'), byteorder='little')
        self.raw_data = raw_data

    def decode(self):
        raise NotImplementedError("Decode method must be implemented by subclasses")


class InstructionDecoder(Decoder):
    opcode = None

    decoder = None

    def __init__(self, raw_data):
        self.raw_data = raw_data
        # extract least 7 bit as opcode
        self.opcode = self.raw_data & 0x7F
        logger.debug(f"Opcode: {self.opcode}")

        self.decoder = self._create_decoder()


    def extract_opcode(self):
        """ extract least 7 bit as opcode """
        return self.raw_data & 0x7F

    def _create_decoder(self):
        match self.opcode:
            case 0b0110011:
                return RTypeDecoder(self.raw_data)
            case 0b0010011:
                return ITypeDecoder(self.raw_data)
            case 0b0000011: # lw, sw
                return ITypeDecoder(self.raw_data)
            case 0b0100011:
                return STypeDecoder(self.raw_data)
            case 0b1100011:
                return BTypeDecoder(self.raw_data)
            case 0b0000000:  # unused
                return UTypeDecoder(self.raw_data)
            case 0b1101111:
                return JTypeDecoder(self.raw_data)
            case None:
                raise ValueError("Opcode is None")
            case _:
                logger.error(f"Opcode {self.opcode} is not supported.")

    def decode(self):
        if self.decoder is None:
            raise ValueError("Decoder is not properly set.")
        return self.decoder.decode()




class RTypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        rd = (self.raw_data >> 7) & 0x1F  # bits [11:7] & 0b1_1111
        funct3 = (self.raw_data >> 12) & 0x7  # bits [14:12]
        rs1 = (self.raw_data >> 15) & 0x1F  # bits [19:15]
        rs2 = (self.raw_data >> 20) & 0x1F  # bits [24:20]
        funct7 = (self.raw_data >> 25) & 0x7F  # bits [31:25]

        return {
            "opcode": 0b0110011,
            "rd": rd,
            "rs1": rs1,
            "rs2": rs2,
            "funct3": funct3,
            "funct7": funct7
        }

    def print_formatted_instruction(instuction: int):
        pass


class ITypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        opcode = self.raw_data & 0x7F
        rd = (self.raw_data >> 7) & 0x1F  # bits [11:7]
        funct3 = (self.raw_data >> 12) & 0x7  # bits [14:12]
        rs1 = (self.raw_data >> 15) & 0x1F  # bits [19:15]
        imm = (self.raw_data >> 20) & 0xFFF  # bits [31:20], 12-bit immediate

        # Sign extension for immediate (if necessary)
        if imm & 0x800:
            imm |= ~0xFFF  # If sign bit is set, extend to 32 bits

        return {
            "opcode": opcode,
            "rd": rd,
            "rs1": rs1,
            "funct3": funct3,
            "imm": imm
        }

## below need modification

class STypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        imm4_0 = (self.raw_data >> 7) & 0x1F  # bits [11:7]
        funct3 = (self.raw_data >> 12) & 0x7  # bits [14:12]
        rs1 = (self.raw_data >> 15) & 0x1F  # bits [19:15]
        rs2 = (self.raw_data >> 20) & 0x1F  # bits [24:20]
        imm11_5 = (self.raw_data >> 25) & 0x7F  # bits [31:25]
        imm = (imm11_5 << 5) | imm4_0  # Combine immediate fields

        # Sign extension for immediate (if necessary)
        if imm & 0x800:
            imm |= ~0xFFF  # If sign bit is set, extend to 32 bits

        return {
            "opcode": self.opcode,
            "rs1": rs1,
            "rs2": rs2,
            "funct3": funct3,
            "imm": imm
        }


class BTypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        imm11 = (self.raw_data >> 7) & 0x1  # bit [11]
        imm4_1 = (self.raw_data >> 8) & 0xF  # bits [10:8, 4:1]
        funct3 = (self.raw_data >> 12) & 0x7  # bits [14:12]
        rs1 = (self.raw_data >> 15) & 0x1F  # bits [19:15]
        rs2 = (self.raw_data >> 20) & 0x1F  # bits [24:20]
        imm10_5 = (self.raw_data >> 25) & 0x3F  # bits [30:25]
        imm12 = (self.raw_data >> 31) & 0x1  # bit [31]
        imm = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)  # Combine immediate fields

        # Sign extension for immediate (if necessary)
        if imm & 0x1000:
            imm |= ~0x1FFF  # If sign bit is set, extend to 32 bits

        return {
            "opcode": self.opcode,
            "rs1": rs1,
            "rs2": rs2,
            "funct3": funct3,
            "imm": imm
        }


class UTypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        rd = (self.raw_data >> 7) & 0x1F  # bits [11:7]
        imm = self.raw_data & 0xFFFFF000  # bits [31:12], 20-bit immediate
        return {
            "opcode": self.opcode,
            "rd": rd,
            "imm": imm
        }


# J-Type Decoder
class JTypeDecoder(Decoder):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def decode(self):
        rd = (self.raw_data >> 7) & 0x1F  # bits [11:7]
        imm19_12 = (self.raw_data >> 12) & 0xFF  # bits [19:12]
        imm11 = (self.raw_data >> 20) & 0x1  # bit [11]
        imm10_1 = (self.raw_data >> 21) & 0x3FF  # bits [10:1]
        imm20 = (self.raw_data >> 31) & 0x1  # bit [20]
        imm = (imm20 << 20) | (imm19_12 << 12) | (imm11 << 11) | (imm10_1 << 1)  # Combine immediate fields

        # Sign extension for immediate (if necessary)
        if imm & 0x100000:
            imm |= ~0x1FFFFF  # If sign bit is set, extend to 32 bits

        return {
            "opcode": self.opcode,
            "rd": rd,
            "imm": imm
        }
