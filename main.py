import argparse
from pathlib import Path

from loguru import logger

from src.core import SingleStageCore, FiveStageCore
from src.generate_metrics import generate_metrics
from src.memory import InstructionMemory, DataMemory

if __name__ == "__main__":
    # logger.remove()
    # logger.add(sys.stderr, level="DEBUG")
    # logger.add(sys.stderr, level="DEBUG", backtrace=True, diagnose=True)

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="iodir", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = Path(args.iodir)

    logger.info(f"List IO Directory: {list(ioDir.iterdir())}")

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

        # if ssCore.halted or fsCore.halted:
        #     break

        # test only
        # if fsCore.cycle > 100:
        #     logger.error("Five Stage Core is taking too long to execute. Exiting...")
        #     break

    # dump SS and FS data mem.
    dmem_ss.output_data_memory()
    dmem_fs.output_data_memory()

    generate_metrics("w", "Single Stage Core Performance Metrics", ssCore.cycle, ssCore.cycle - 1, ioDir)
    generate_metrics("a", "Five Stage Core Performance Metrics", fsCore.cycle, ssCore.cycle - 1, ioDir)
