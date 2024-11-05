from loguru import logger
from pathlib import Path

from src.decoder import InstructionDecoder
from src.register_file import RegisterFile
from src.state import State
from src.memory import InstructionMemory, DataMemory
from src.components import arithmetic_logic_unit, alu_control_unit, adder, control_unit, imm_gen, multiplexer, and_gate


class Core(object):
    def __init__(self,
                 ioDir,
                 instruction_memory: InstructionMemory,
                 data_memory: DataMemory):
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
        logger.debug(f"--------------------- IF stage ")

        # TODO: Temporarily. I'll figure out if this is correct
        # "The PC address is incremented by 4 and then written
        # back into the PC to be ready for the next clock cycle. This PC is also saved
        # in the IF/ID pipeline register in case it is needed later for an instruction,
        # such as beq." Comp.Org P.300
        if_pc_adder_result = adder(4, self.state.IF["PC"])
        self.state.ID["nop"] = self.state.IF["nop"]
        logger.opt(colors=True).info(f"<green>PC: {self.state.IF['PC']}</green>")

        self.state.ID["Instr"] = self.ext_instruction_memory.read_instruction(
            self.state.IF["PC"])
        program_counter = self.state.IF["PC"]

        logger.debug(f"Instruction: +.....-+...-+...-+.-+...-+.....-")
        logger.debug(f"Instruction: func7.|rs2.|rs1.|3.|rd..|opcode|")
        logger.debug(f"Instruction: {self.state.ID['Instr']:032b}")

        # --------------------- ID stage ---------------------
        logger.debug(f"--------------------- ID stage ")

        opcode = self.state.ID["Instr"] & 0x7F

        self.state.EX["nop"] = self.state.ID["nop"]

        control_signals, halt = control_unit(opcode)
        if halt:
            self.state.IF["nop"] = True

        logger.debug(f"Control Signals: {control_signals}")
        self.state.EX["alu_op"] = control_signals["ALUOp"]  # EX stage
        self.state.EX["is_I_type"] = control_signals["ALUSrcB"]  # EX stage

        branch = control_signals["Branch"]  # MEM stage, but not found for Single Stage Machine
        self.state.EX["rd_mem"] = control_signals["MemRead"]  # MEM stage
        self.state.EX["wrt_mem"] = control_signals["MemWrite"]  # MEM stage

        mem_to_reg = control_signals["MemtoReg"]  # WB stage, but not found for Single Stage Machine
        self.state.EX["wrt_enable"] = control_signals["RegWrite"]  # WB stage

        # See comments in state.py to see more information
        self.state.EX["Rs"] = (self.state.ID["Instr"] >> 15) & 0x1F  # bits [19:15]
        self.state.EX["Rt"] = (self.state.ID["Instr"] >> 20) & 0x1F  # bits [24:20]
        self.state.EX["Wrt_reg_addr"] = (self.state.ID["Instr"] >> 7) & 0x1F  # bits [11:7]

        # Ref: Comp.Org P.282.e5 Figure e4.5.4
        self.state.EX["Read_data1"] = self.register_file.read(self.state.EX["Rs"])
        self.state.EX["Read_data2"] = self.register_file.read(self.state.EX["Rt"])

        # an always true condition so I can collapse the block
        if logger.level("DEBUG"):
            logger.opt(colors=True).info(f"+-----------------------------+---------------------------------+-----------------------------+")
            logger.opt(colors=True).info(f"| Register      | Mem Addr  | \t\t\tValue Bin (Dec) \t\t  |")
            logger.opt(colors=True).info(f"| Rs / Rd1      | {self.state.EX['Rs']:05b} ({self.state.EX['Rs']}) | {self.state.EX['Read_data1']:032b} ({self.state.EX['Read_data1']}) |")
            logger.opt(colors=True).info(f"| Rt / Rd2      | {self.state.EX['Rt']:05b} ({self.state.EX['Rt']}) | {self.state.EX['Read_data2']:032b} ({self.state.EX['Read_data2']}) |")
            logger.opt(colors=True).info(f"| Wrt_reg_addr  | {self.state.EX['Wrt_reg_addr']:05b} ({self.state.EX['Wrt_reg_addr']}) |")
            logger.opt(colors=True).info(f"+-----------------------------+---------------------------------+-----------------------------+")



        # todo: Branch/PCSrc, MemtoReg should also be set in this stage, not found in state machine

        # Imm Gen
        self.state.EX["Imm"] = imm_gen(opcode=opcode, instr=self.state.ID["Instr"])

        func7_bit = (self.state.ID["Instr"] >> 30) & 0b1
        func3 = (self.state.ID["Instr"] >> 12) & 0b111
        alu_control_func_code = (func7_bit << 3) | func3

        # special ALU handling, if I-type, omit the func7 bit
        # I didn't find this in the book, without this, ALU cannot work on I-type
        if opcode == 19:  # I-type
            alu_control_func_code = alu_control_func_code & 0b111

        # --------------------- EX stage ---------------------
        logger.debug(f"--------------------- EX stage ")

        # Passing data to subsequent pipeline registers
        self.state.MEM["nop"] = self.state.EX["nop"]
        self.state.MEM["Rs"] = self.state.EX["Rs"]
        self.state.MEM["Rt"] = self.state.EX["Rt"]
        self.state.MEM["Wrt_reg_addr"] = self.state.EX["Wrt_reg_addr"]

        # Passing control signal to subsequent pipeline registers
        # (see Comp.Org p.313 Figure 4.52)
        self.state.MEM["rd_mem"] = self.state.EX["rd_mem"]
        self.state.MEM["wrt_mem"] = self.state.EX["wrt_mem"]
        self.state.MEM["wrt_enable"] = self.state.EX["wrt_enable"]

        alu_input_b = multiplexer(self.state.EX["is_I_type"],
                                  self.state.EX["Read_data2"],
                                  4,
                                  self.state.EX["Imm"])  # extract the least significant bit

        # ALUOp 2-bit, generated from the Main Control Unit
        # indicates whether the operation to be performed should be
        # add (00) for loads and stores, subtract and
        # test if zero (01) for beq, or
        # be determined by the operation encoded in the funct7 and funct3 fields (10).
        alu_control = alu_control_unit(self.state.EX["alu_op"],
                                       alu_control_func_code)

        # ALU control 4-bit
        zero, self.state.MEM["ALUresult"] = arithmetic_logic_unit(
            alu_control=alu_control,
            a=self.state.EX["Read_data1"],
            b=alu_input_b)

        # PC handling
        ex_pc_adder_result = adder(program_counter, self.state.EX["Imm"])
        # Branch handling
        pc_src = and_gate(branch, zero)
        program_counter = multiplexer(pc_src, if_pc_adder_result, ex_pc_adder_result)

        # --------------------- MEM stage --------------------
        logger.debug(f"--------------------- MEM stage ")

        # Passing data to subsequent pipeline registers
        self.state.WB["nop"] = self.state.MEM["nop"]
        self.state.WB["Wrt_data"] = self.state.MEM["ALUresult"]
        self.state.WB["Rs"] = self.state.MEM["Rs"]
        self.state.WB["Rt"] = self.state.MEM["Rt"]

        # Passing control signal to subsequent pipeline registers
        # (see Comp.Org p.313 Figure 4.52)
        self.state.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]
        self.state.WB["wrt_enable"] = self.state.MEM["wrt_enable"]

        # Data Memory Unit
        if self.state.MEM["wrt_mem"] == 1:
            logger.debug("Write data")
            self.ext_data_memory.write_data_memory(
                self.state.MEM["ALUresult"],
                self.state.EX["Read_data2"])
        data_memory_output = None  # not found in state machine
        if self.state.MEM["rd_mem"] == 1:
            logger.debug("Read data")
            data_memory_output = self.ext_data_memory.read_instruction(self.state.MEM["ALUresult"])



        # --------------------- WB stage ---------------------
        logger.debug(f"--------------------- WB stage ")

        self.state.WB["Wrt_data"] = multiplexer(mem_to_reg, self.state.WB["Wrt_data"], data_memory_output)

        if self.state.WB["wrt_enable"] == 1:
            self.register_file.write(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])

        if not self.state.IF["nop"]:
            self.nextState.IF["PC"] = program_counter
        else:
            # 當nop時，保持PC不變
            self.nextState.IF["PC"] = self.state.IF["PC"]

        # ----------------------- End ------------------------
        logger.opt(colors=True).debug(f"<green>-------------------- stage end ---------------------</green>")
        logger.opt(colors=True).debug(f"<green>-------------- ↑ {self.cycle} cycle |  {self.cycle+1} cycle ↓ --------------</green>")
        logger.opt(colors=True).debug(f"<green>-------------------- stage end ---------------------</green>")

        # self.halted = True
        # if self.state.IF["nop"]:
        #     self.halted = True
        if self.state.WB["nop"]:
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

        self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
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
