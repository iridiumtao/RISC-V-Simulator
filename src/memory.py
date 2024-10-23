from pathlib import Path


class InstructionMemory(object):
    """
    InstructionMemory simulates the instruction memory in a processor.
    """

    def __init__(self, name, io_dir: Path):
        """
        Initialize the InstructionMemory.

        Args:
            name (str): The name of the instruction memory.
            io_dir (Path): Directory for input/output files.
        """
        self.id = name

        with open(io_dir / "imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def read_instruction(self, read_address):
        """
        Read an instruction from the instruction memory.

        Args:
            read_address (int): The address to read the instruction from.

        Returns:
            str: The 32-bit instruction in hexadecimal format.
        """
        pass


class DataMemory(object):
    """
    DataMemory simulates the data memory in a processor.
    """

    def __init__(self, name, io_dir: Path):
        """
        Initialize the DataMemory.

        Args:
            name (str): The name of the data memory.
            io_dir (Path): Directory for input/output files.
        """
        self.id = name
        self.ioDir = io_dir
        with open(io_dir / "dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def read_instruction(self, read_address):
        """
        Read data from the data memory.

        Args:
            read_address (int): The address to read the data from.

        Returns:
            str: The 32-bit data in hexadecimal format.
        """
        pass

    def write_data_memory(self, address, write_data):
        """
        Write data to the data memory.

        Args:
            address (int): The address to write the data to.
            write_data (str): The data to write in hexadecimal format.
        """
        pass

    def output_data_memory(self):
        """
        Output the state of the data memory to a file.
        """
        res_path = self.ioDir / f"{self.id}_DMEMResult.txt"
        with open(res_path, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])