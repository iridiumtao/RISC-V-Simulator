from pathlib import Path
from loguru import logger



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
        Path(io_dir).mkdir(parents=True, exist_ok=True)

    def read(self, reg_addr):
        """
        Read the data from the register file.

        Args:
            reg_addr (int): The address of the register to read from. (0~31)

        Returns:
            int: The data read from the register.
        """
        data = self.Registers[reg_addr]
        if data is None:
            data = 0
        logger.debug(f"Read register {reg_addr:05b}: {data:032b} ({data})")
        return data


    def write(self, reg_addr, write_reg_data):
        """
        Write data to the register file.

        Args:
            reg_addr (int): The address of the register to write to. (0~31)
            write_reg_data (int): The data to write to the register.
        """

        if reg_addr == 0:  # Avoid writing to register 0
            return

        # Handle negative two's complement conversion
        if write_reg_data < 0:
            write_reg_data = (1 << 32) + write_reg_data  # Convert to 2's complement 32-bit

        self.Registers[reg_addr] = write_reg_data

    def output(self, cycle):
        """
        Output the state of the register file to a file.

        Args:
            cycle (int): The current cycle number.
        """
        op = ["-" * 70 + "\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([format(val, 'b').zfill(32) + "\n" for val in self.Registers])

        if (cycle == 0):
            perm = "w+"
        else:
            perm = "a+"
        with open(self.outputFile, perm) as file:
            file.writelines(op)
