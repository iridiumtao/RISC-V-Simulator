from pathlib import Path

from loguru import logger

# memory.py size, in reality, the memory.py size should be 2^32,
# but for this lab, for the space resaon, we keep it as this large number,
# but the memory.py is still 32-bit addressable.
MEM_SIZE = 1000


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

        # Each line in the files contain a byte of data
        with open(io_dir / "imem.txt") as im:
            self.i_mem = [data.replace("\n", "") for data in im.readlines()]
            self.i_mem += ["0" * 8] * (MEM_SIZE - len(self.i_mem))

    def read(self, read_address: int) -> int:
        """
        Read an instruction from the instruction memory.

        Args:
            read_address (int): The address to read the instruction from.

        Returns:
            int: The 32-bit instruction. can be print as hex: f'{address:#x}, bin: f'{address:#b}'
        """

        # load 4 piece of data and concatenate them
        bin_str = ''.join(self.i_mem[read_address: read_address + 4])
        if bin_str == "":
            return 0
        return int(bin_str, 2)


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
            self.d_mem = [data.replace("\n", "") for data in dm.readlines()]
            self.d_mem += ["0" * 8] * (1000 - len(self.d_mem))

    def read(self, read_address):
        """
        Read data from the data memory.

        Args:
            read_address (int): The address to read the data from.

        Returns:
            int: The 32-bit binary data in integer format
        """
        bin_str = ''.join(self.d_mem[read_address: read_address + 4])
        logger.debug(f"Reading data {bin_str} from address {read_address:05b}")
        return int(bin_str, 2)

    def write(self, address, data):
        """
        Write data to the data memory.

        Args:
            address (int): The address to write the data to.
            data (int): The 32-bit binary data to write in integer format.
        """
        # Convert the integer write_data to a 32-bit binary string
        if address < 0 or address >= MEM_SIZE:
            logger.error(f"Invalid address: {address}")
            return
        logger.debug(f"Writing data {data} to address {address}")

        # Handle negative two's complement conversion
        if data < 0:
            data = (1 << 32) + data  # Convert to 2's complement 32-bit

        # Explain: say write_data = -2
        # (1 << 32) generates 2^32
        # 1 << 32 = 100000000000000000000000000000000 (33 bits)
        #         = 4294967296
        # When add -2
        # 4294967296 + (-2) = 4294967294
        #                   = 11111111111111111111111111111110 (32 bits)

        binary_str = f"{data:032b}"

        # Write each byte (8 bits) to the memory in order
        for i in range(4):
            self.d_mem[address + i] = binary_str[i * 8: (i + 1) * 8]

    def output_data_memory(self):
        """
        Output the state of the data memory to a file.
        """
        res_path = self.ioDir / f"{self.id}_DMEMResult.txt"
        with open(res_path, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.d_mem])
