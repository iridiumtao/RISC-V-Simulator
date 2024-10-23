
from pathlib import Path

MEM_SIZE = 1000  # memory.py size, in reality, the memory.py size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory.py is still 32-bit addressable.


class RegisterFile(object):
    def __init__(self, io_dir: Path):
        self.outputFile = io_dir / "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]

    def readRF(self, reg_addr):
        # Fill in
        pass

    def writeRF(self, reg_addr, write_reg_data):
        # Fill in
        pass

    def outputRF(self, cycle):
        op = ["-" * 70 + "\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val) + "\n" for val in self.Registers])
        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)




