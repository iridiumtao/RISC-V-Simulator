from pathlib import Path

# memory.py size, in reality, the memory.py size should be 2^32,
# but for this lab, for the space resaon, we keep it as this large number,
# but the memory.py is still 32-bit addressable.
MEM_SIZE = 1000


class RegisterFile(object):
    """
    RegisterFile simulates a register file in a processor.
    """

    def __init__(self, io_dir: Path):
        """
        Initialize the RegisterFile.

        Args:
            io_dir (Path): Directory for input/output files.
        """
        self.outputFile = io_dir / "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]

    def read(self, reg_addr):
        """
        Read the data from the register file.

        Args:
            reg_addr (int): The address of the register to read from. (0~31)

        Returns:
            int: The data read from the register.
        """
        # Fill in
        pass

    def write(self, reg_addr, write_reg_data):
        """
        Write data to the register file.

        Args:
            reg_addr (int): The address of the register to write to. (0~31)
            write_reg_data (int): The data to write to the register.
        """
        # Fill in
        pass

    def output(self, cycle):
        """
        Output the state of the register file to a file.

        Args:
            cycle (int): The current cycle number.
        """
        op = ["-" * 70 + "\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val) + "\n" for val in self.Registers])
        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)
