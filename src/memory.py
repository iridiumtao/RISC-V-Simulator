from pathlib import Path


class InstructionMemory(object):
    def __init__(self, name, io_dir: Path):
        self.id = name

        with open(io_dir / "imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def read_instruction(self, read_address):
        # read instruction memory
        # return 32 bit hex val
        pass


class DataMemory(object):
    def __init__(self, name, io_dir: Path):
        self.id = name
        self.ioDir = io_dir
        with open(io_dir / "dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def read_instruction(self, read_address):
        #read data memory
        #return 32 bit hex val
        pass

    def write_data_memory(self, address, write_data):
        # write data into byte addressable memory
        pass

    def output_data_memory(self):
        res_path = self.ioDir / f"{self.id}_DMEMResult.txt"
        with open(res_path, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])