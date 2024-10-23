import argparse
from pathlib import Path
from src.memory import InstructionMemory, DataMemory
from src.core import SingleStageCore, FiveStageCore

if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="iodir", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = Path(args.iodir)


    print("List IO Directory:", list(ioDir.iterdir()))

    imem = InstructionMemory("Imem", ioDir)
    dmem_ss = DataMemory("SS", ioDir)
    dmem_fs = DataMemory("FS", ioDir)

    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while (True):
        if not ssCore.halted:
            ssCore.step()

        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break

    # dump SS and FS data mem.
    dmem_ss.output_data_memory()
    dmem_fs.output_data_memory()