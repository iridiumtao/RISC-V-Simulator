from src.NYU_RV32I_6913 import InsMem, DataMem, SingleStageCore, FiveStageCore
import os
import argparse
from pathlib import Path

if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="input", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = Path(args.iodir)


    print("List IO Directory:", list(ioDir.iterdir()))

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

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
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()