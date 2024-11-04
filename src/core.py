from loguru import logger
from pathlib import Path

from src.decoder import InstructionDecoder
from src.register_file import RegisterFile
from src.state import State
from src.memory import InstructionMemory, DataMemory
from src.components import alu, alu_control, adder, control_unit, imm_gen


class Core(object):
    def __init__(self, ioDir, instruction_memory: InstructionMemory, data_memory: DataMemory):
        self.register_file = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        """ A flag to indicate STOP """

        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_instruction_memory = instruction_memory
        self.ext_data_memory = data_memory


class SingleStageCore(Core):
    """
    SingleStageCore simulates a single-stage pipeline processor core.
    """

    def __init__(self, io_dir, instruction_memory, data_memory):
        """
        Initialize the SingleStageCore.

        Args:
            io_dir (Path): Directory for input/output files.
            instruction_memory (InstructionMemory): The instruction memory.
            data_memory (DataMemory): The data memory.
        """
        super(SingleStageCore, self).__init__(io_dir / "SS_", instruction_memory, data_memory)
        self.op_file_path = io_dir / "StateResult_SS.txt"

    def step(self):
        """
        Execute one cycle of the processor.
        """
        # Your implementation

        # --------------------- IF stage ---------------------
        logger.debug(f"--------------------- IF stage ---------------------")

        self.state.ID["Instr"] = self.ext_instruction_memory.read_instruction(self.state.IF["PC"])
        logger.debug(f"Instruction: {self.state.ID['Instr']}")

        # TODO: Temporarily. I'll figure out if this is correct
        # "The PC address is incremented by 4 and then written
        # back into the PC to be ready for the next clock cycle. This PC is also saved
        # in the IF/ID pipeline register in case it is needed later for an instruction,
        # such as beq." Comp.Org P.300
        self.state.IF["PC"] = adder(self.state.IF["PC"], 4)
        logger.debug(f"PC: {self.state.IF['PC']}")




        # --------------------- ID stage ---------------------

        # See comments in state.py to see more information
        self.state.EX["Rs"] = (self.state.ID["Instr"] >> 15) & 0x1F # bits [19:15]
        self.state.EX["Rt"] = (self.state.ID["Instr"] >> 20) & 0x1F  # bits [24:20]
        self.state.EX["Wrt_reg_addr"] = (self.state.ID["Instr"] >> 7) & 0x1F  # bits [11:7]

        # Ref: Comp.Org P.282.e5 Figure e4.5.4
        self.state.EX["Read_data1"] = self.register_file.read(self.state.EX["Rs"])
        self.state.EX["Read_data2"] = self.register_file.read(self.state.EX["Rt"])


        opcode = self.state.ID["Instr"] & 0x7F
        self.state.EX["Imm"] = imm_gen(opcode=opcode, instruction=self.state.ID["Instr"])

        control_signals = control_unit(opcode)
        self.state.EX["wrt_enable"] = control_signals["RegWrite"]
        self.state.EX["is_I_type"] = control_signals["ALUSrc"]
        self.state.EX["rd_mem"] = control_signals["MemRead"]
        self.state.EX["alu_op"] = control_signals["ALUOp"]
        self.state.EX["wrt_mem"] = control_signals["MemWrite"]

        # todo: PCSrc, MemtoReg should also be set in this stage, not found in state machine
        # --------------------- EX stage ---------------------

        # todo
        # ALUOp 2-bit, generated from the Main Control Unit
        # indicates whether the operation to be performed should be
        # add (00) for loads and stores, subtract and
        # test if zero (01) for beq, or
        # be determined by the operation encoded in the funct7 and funct3 fields (10).

        # todo
        # ALU control 4-bit

        # --------------------- MEM stage --------------------

        # --------------------- WB stage ---------------------

        self.halted = True
        if self.state.IF["nop"]:
            self.halted = True

        self.register_file.output(self.cycle)  # dump RF
        self.print_state(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        # The end of the cycle
        # and updates the current state with the values calculated in this cycle
        self.state = self.nextState
        self.cycle += 1

    def print_state(self, state, cycle):
        """
        Print the state of the processor after each cycle.

        Args:
            state (State): The current state of the processor.
            cycle (int): The current cycle number.
        """
        printstate = ["-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.op_file_path, perm) as wf:
            wf.writelines(printstate)


class FiveStageCore(Core):
    def __init__(self, io_dir, instruction_memory, data_memory):
        super(FiveStageCore, self).__init__(io_dir / "FS_", instruction_memory, data_memory)
        self.opFilePath = io_dir / "StateResult_FS.txt"

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------

        # --------------------- MEM stage --------------------

        # --------------------- EX stage ---------------------

        # --------------------- ID stage ---------------------

        # --------------------- IF stage ---------------------

        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and \
                self.state.WB["nop"]:
            self.halted = True

        self.register_file.output(self.cycle)  # dump RF
        self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = self.nextState  #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)
