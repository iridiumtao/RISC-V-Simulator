from pathlib import Path

from loguru import logger

from src.components import arithmetic_logic_unit, alu_control_unit, adder, control_unit, imm_gen, multiplexer, and_gate, \
    xor_gate, or_gate
from src.hazard_handler import forwarding_unit, hazard_detection_unit
from src.memory import InstructionMemory, DataMemory
from src.register_file import RegisterFile
from src.state import State


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

        # "The PC address is incremented by 4 and then written
        # back into the PC to be ready for the next clock cycle. This PC is also saved
        # in the IF/ID pipeline register in case it is needed later for an instruction,
        # such as beq." Comp.Org P.300
        if_pc_adder_result = adder(4, self.state.IF["PC"])
        self.state.ID["nop"] = self.state.IF["nop"]
        logger.opt(colors=True).info(f"<green>PC: {self.state.IF['PC']}</green>")

        self.state.ID["Instr"] = self.ext_instruction_memory.read(
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
        alu_src_a = control_signals["ALUSrcA"]

        branch = control_signals["Branch"]  # MEM stage, but not found for Single Stage Machine
        jal = control_signals["JAL"]
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
            logger.opt(colors=True).info(
                f"+-----------------------------+---------------------------------+-----------------------------+")
            logger.opt(colors=True).info(f"| Register      | Mem Addr  | \t\t\tValue Bin (Dec) \t\t  |")
            logger.opt(colors=True).info(
                f"| Rs / Rd1      | {self.state.EX['Rs']:05b} ({self.state.EX['Rs']}) | {self.state.EX['Read_data1']:032b} ({self.state.EX['Read_data1']}) |")
            logger.opt(colors=True).info(
                f"| Rt / Rd2      | {self.state.EX['Rt']:05b} ({self.state.EX['Rt']}) | {self.state.EX['Read_data2']:032b} ({self.state.EX['Read_data2']}) |")
            logger.opt(colors=True).info(
                f"| Wrt_reg_addr  | {self.state.EX['Wrt_reg_addr']:05b} ({self.state.EX['Wrt_reg_addr']}) |")
            logger.opt(colors=True).info(
                f"+-----------------------------+---------------------------------+-----------------------------+")

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

        alu_input_a = multiplexer(alu_src_a, self.state.EX["Read_data1"], program_counter)

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
            a=alu_input_a,
            b=alu_input_b)

        bne_func = (alu_control_func_code & 0x1)
        logger.debug(f"PC Handling debug: alu_control_func_code: {alu_control_func_code}, bne_func: {bne_func}")

        # PC handling
        ex_pc_adder_result = adder(program_counter, self.state.EX["Imm"])
        # Branch handling, BEQ, BNE handling, JAL handling
        pc_src = or_gate(jal, and_gate(branch, xor_gate(zero, bne_func)))
        logger.debug(f"PC Handling debug: pc_src: {pc_src}, branch: {branch}, zero: {zero}, bne_func: {bne_func}")
        program_counter = multiplexer(pc_src, if_pc_adder_result, ex_pc_adder_result)
        logger.debug(f"PC Handling debug: PC: {program_counter}")

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
            self.ext_data_memory.write(self.state.MEM["ALUresult"], self.state.EX["Read_data2"])
        data_memory_output = None  # not found in state machine
        if self.state.MEM["rd_mem"] == 1:
            logger.debug("Read data")
            data_memory_output = self.ext_data_memory.read(self.state.MEM["ALUresult"])

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
        logger.opt(colors=True).info(
            f"<green>-------------- ↑ {self.cycle} cycle |  {self.cycle + 1} cycle ↓ --------------</green>")
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
    if_stage_pc_result = 0
    mem_stage_pc_result = 0
    pc_src = 0
    halt_detected = False

    def __init__(self, io_dir, instruction_memory, data_memory):
        super(FiveStageCore, self).__init__(io_dir / "FS_", instruction_memory, data_memory)
        self.opFilePath = io_dir / "StateResult_FS.txt"

    def step(self):
        # Set the nop states based on the cycle number, REQUIRED by the assignment
        self.set_init_nop_state()

        if (self.halt_detected and
                self.state.ID["nop"] and
                self.state.EX["nop"] and
                self.state.MEM["nop"] and
                self.state.WB["nop"]):
            self.halted = True
        # Your implementation
        temp_nop = {"if": False, "id": False, "ex": False, "mem": False, "wb": False}
        # --------------------- WB stage ---------------------


        self.wb_stage()
        temp_nop["wb"] = self.state.WB["nop"]
        self.state.WB["nop"] = self.update_nop_state(prev_stage_nop=self.state.MEM["nop"],
                                                     halt_detected=self.halt_detected)

        # --------------------- MEM stage --------------------


        self.mem_stage()
        temp_nop["mem"] = self.state.MEM["nop"]
        self.state.MEM["nop"] = self.update_nop_state(prev_stage_nop=self.state.EX["nop"],
                                                      halt_detected=self.halt_detected)

        # --------------------- EX stage ---------------------


        self.ex_stage()
        temp_nop["ex"] = self.state.EX["nop"]
        self.state.EX["nop"] = self.update_nop_state(prev_stage_nop=self.state.ID["nop"],
                                                     halt_detected=self.halt_detected)

        # --------------------- ID stage ---------------------


        self.id_stage()
        temp_nop["id"] = self.state.ID["nop"]
        self.state.ID["nop"] = self.update_nop_state(prev_stage_nop=self.state.IF["nop"],
                                                     halt_detected=self.halt_detected)

        # --------------------- IF stage ---------------------

        # Only fetch new instructions if HALT hasn't been detected
        if not self.halt_detected:
            self.if_stage()
            temp_nop["if"] = self.state.IF["nop"]
        else:
            logger.warning(f"IF stage No Operation")
            self.state.IF["nop"] = True

        # ----------------------- End ------------------------

        logger.opt(colors=True).debug(f"<green>-------------------- stage end ---------------------</green>")
        logger.opt(colors=True).info(
            f"<green>-------------- ↑ {self.cycle} cycle |  {self.cycle + 1} cycle ↓ --------------</green>")
        logger.opt(colors=True).debug(f"<green>-------------------- stage end ---------------------</green>")

        self.register_file.output(self.cycle)  # dump RF
        self.printState(self.state, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.cycle += 1

    def if_stage(self):
        logger.debug(f"--------------------- IF stage ")
        logger.info(f"state: {self.state.IF}")

        # Conform to the assignment hidden requirements
        if self.ext_instruction_memory.read(self.state.IF["PC"]) == 0b11111111111111111111111111111111:
            self.halt_detected = True
            self.state.IF["nop"] = True
            self.state.ID["nop"] = True
            logger.warning(f"HALT detected")
            return


        if self.state.IF["nop"]:
            logger.warning(f"IF stage No Operation")
            return

        # PCWrite from Hazard Detection Unit
        # if PCWrite is 0, the PC is not updated
        self.if_stage_pc_result = multiplexer(self.state.IF["PCWrite"],
                                              self.state.IF["PC"],
                                              adder(4, self.state.IF["PC"]))

        self.state.ID["PC"] = self.state.IF["PC"]
        logger.opt(colors=True).info(f"<green>PC: {self.state.IF['PC']}</green>")

        # Basically a MUX but lazy version
        # if IFIDWrite is 0, the Instr is not updated
        if self.state.IF["IFIDWrite"]:
            self.state.ID["Instr"] = self.ext_instruction_memory.read(self.state.IF["PC"])
        else:
            logger.warning(f"IFIDWrite is 0, Instruction not updated")

        self.logger_instruction()

        program_counter = multiplexer(self.pc_src, self.if_stage_pc_result, self.mem_stage_pc_result)
        logger.debug(f"PC Handling debug: Next PC: {program_counter}")
        # next PC
        self.state.IF["PC"] = program_counter

    def id_stage(self):
        logger.debug(f"--------------------- ID stage ")
        logger.info(f"state: {self.state.ID}")
        if self.state.ID["nop"]:
            logger.warning(f"ID stage No Operation")
            return

        # This will stop the stage in the next cycle
        if self.state.IF["nop"] and self.halt_detected:
            self.state.ID["nop"] = True

        """Instruction Fields Extracting"""
        opcode = self.state.ID["Instr"] & 0x7F
        # See comments in state.py to see more information
        rs1 = (self.state.ID["Instr"] >> 15) & 0x1F  # bits [19:15]
        rs2 = (self.state.ID["Instr"] >> 20) & 0x1F  # bits [24:20]

        # Instruction [30, 14-12] handling
        func7_bit = (self.state.ID["Instr"] >> 30) & 0b1
        func3 = (self.state.ID["Instr"] >> 12) & 0b111
        alu_control_func_code = (func7_bit << 3) | func3

        write_register = (self.state.ID["Instr"] >> 7) & 0x1F  # bits [11:7]

        """Forward to next pipeline register"""
        self.state.EX["Rs"] = rs1
        self.state.EX["Rt"] = rs2
        # According to the assignment testcase, the naming IS MEANT TO BE DIFFERENT
        self.state.EX["instr"] = self.state.ID["Instr"]


        """Hazard Detection Unit"""
        self.state.IF["PCWrite"], self.state.IF["IFIDWrite"], stall = hazard_detection_unit(self.state)

        # Forward to next pipeline register AFTER hazard detection unit
        self.state.EX["Wrt_reg_addr"] = write_register

        """Control Signal mapping"""
        control_signals, halt = control_unit(opcode)
        if halt:
            # todo: potentially missing "halt on next cycle"
            self.halt_detected = True
            self.state.IF["nop"] = True

        # Mux after Control Unit
        if stall:
            self.state.EX["nop"] = True
            self.state.EX["alu_op"] = 0
            self.state.EX["is_I_type"] = 0
            self.state.EX["branch"] = 0
            self.state.EX["jal"] = 0
            self.state.EX["rd_mem"] = 0
            self.state.EX["wrt_mem"] = 0
            self.state.EX["mem_to_reg"] = 0
            self.state.EX["wrt_enable"] = 0
        else:
            logger.debug(f"Control Signals: {control_signals}")
            self.state.EX["alu_op"] = control_signals["ALUOp"]  # EX stage
            self.state.EX["is_I_type"] = control_signals["ALUSrcB"]  # EX stage
            self.state.EX["branch"] = control_signals["Branch"]  # MEM stage, but not found for Single Stage Machine
            self.state.EX["jal"] = control_signals["JAL"]
            self.state.EX["rd_mem"] = control_signals["MemRead"]  # MEM stage
            self.state.EX["wrt_mem"] = control_signals["MemWrite"]  # MEM stage
            self.state.EX["mem_to_reg"] = control_signals[
                "MemtoReg"]  # WB stage, but not found for Single Stage Machine
            self.state.EX["wrt_enable"] = control_signals["RegWrite"]  # WB stage

        self.state.EX["PC"] = self.state.ID["PC"]

        """Register File"""
        # Ref: Comp.Org P.282.e5 Figure e4.5.4
        self.state.EX["Read_data1"] = self.register_file.read(rs1)
        self.state.EX["Read_data2"] = self.register_file.read(rs2)

        """Imm Gen"""
        self.state.EX["Imm"] = imm_gen(opcode=opcode, instr=self.state.EX["instr"])
        # special ALU handling, if I-type, omit the func7 bit
        # I didn't find this in the book, without this, ALU cannot work on I-type
        if opcode == 19:  # I-type
            alu_control_func_code = alu_control_func_code & 0b111
        # todo: see if we can merge the two if statements
        if opcode == 19 or opcode == 3:
            self.state.EX["Rt"] = 0  # I-type doesn't have Rt (prevent problem from hazard detection unit)
        self.state.EX["alu_control_func"] = alu_control_func_code

        self.logger_data_memory_result()

        """Branch condition"""
        # todo: **Assignment Doc: The branch conditions are resolved in the ID/RF stage of the pipeline**
        # Branch handling, BEQ, BNE handling, JAL handling
        self.pc_src = or_gate(self.state.MEM["jal"], and_gate(self.state.MEM["branch"],
                                                              xor_gate(self.state.MEM["ALUZero"],
                                                                       self.state.MEM["bne"])))
        logger.debug(
            f"PC Handling debug: pc_src: {self.pc_src}, branch: {self.state.MEM["branch"]}, zero: {self.state.MEM["ALUZero"]}, bne_func: {self.state.MEM["bne"]}")


        # clear EX stage if stall
        if stall:
            self.state.EX["Read_data1"] = 0
            self.state.EX["Read_data2"] = 0
            self.state.EX["Rs"] = 0
            self.state.EX["Rt"] = 0
            self.state.EX["Wrt_reg_addr"] = 0

    def ex_stage(self):
        logger.debug(f"--------------------- EX stage ")
        logger.info(f"state: {self.state.EX}")
        if self.state.EX["nop"]:
            logger.warning(f"EX stage No Operation")
            return
        # This will stop the stage in the next cycle
        if self.state.ID["nop"] and self.halt_detected:
            self.state.EX["nop"] = True

        # PC adder
        self.state.MEM["PC"] = adder(self.state.EX["PC"], self.state.EX["Imm"])

        """Forwarding Unit"""
        forward_a, forward_b = forwarding_unit(self.state)

        alu_input_a = multiplexer(forward_a,
                                  self.state.EX["Read_data1"],
                                  self.state.MEM["ALUresult"],
                                  self.state.WB["Wrt_data"])
        # forwarding unit alu input b
        forward_b_result = multiplexer(forward_b,
                                  self.state.EX["Read_data2"],
                                  self.state.MEM["ALUresult"],
                                  self.state.WB["Wrt_data"])

        """Passing data to subsequent pipeline registers"""
        self.state.MEM["Rs"] = self.state.EX["Rs"]  # todo: ?
        self.state.MEM["Rt"] = self.state.EX["Rt"]  # todo: ?
        self.state.MEM["Wrt_reg_addr"] = self.state.EX["Wrt_reg_addr"]

        """Passing control signal to subsequent pipeline registers"""
        # (see Comp.Org p.313 Figure 4.52)
        self.state.MEM["branch"] = self.state.EX["branch"]
        self.state.MEM["rd_mem"] = self.state.EX["rd_mem"]
        self.state.MEM["wrt_mem"] = self.state.EX["wrt_mem"]
        self.state.MEM["wrt_enable"] = self.state.EX["wrt_enable"]
        self.state.MEM["mem_to_reg"] = self.state.EX["mem_to_reg"]
        self.state.MEM["Store_data"] = forward_b_result  # ID Register output: Read register 2 (rd2)

        # rd2 or imm ALU input b
        alu_input_b = multiplexer(self.state.EX["is_I_type"],
                                  forward_b_result,
                                  4,  # unnecessary. but we keep this for compatibility
                                  self.state.EX["Imm"])  # extract the least significant bit

        # ALUOp 2-bit, generated from the Main Control Unit
        # indicates whether the operation to be performed should be
        # add (00) for loads and stores, subtract and
        # test if zero (01) for beq, or
        # be determined by the operation encoded in the funct7 and funct3 fields (10).
        alu_control = alu_control_unit(self.state.EX["alu_op"],
                                       self.state.EX["alu_control_func"])
        # ALU control 4-bit
        zero, self.state.MEM["ALUresult"] = arithmetic_logic_unit(
            alu_control=alu_control,
            a=alu_input_a,
            b=alu_input_b)
        bne_func = (self.state.EX["alu_control_func"] & 0x1)
        logger.debug(
            f"PC Handling debug: alu_control_func_code: {self.state.EX["alu_control_func"]}, bne_func: {bne_func}")
        self.state.MEM["bne"] = bne_func
        self.state.MEM["ALUZero"] = zero

    def mem_stage(self):
        logger.debug(f"--------------------- MEM stage ")
        logger.info(f"state: {self.state.MEM}")
        if self.state.MEM["nop"]:
            logger.warning(f"MEM stage No Operation")
            return
        # This will stop the stage in the next cycle
        if self.state.EX["nop"] and self.halt_detected:
            self.state.MEM["nop"] = True

        """Passing data to subsequent pipeline registers"""
        self.state.WB["ALUresult"] = self.state.MEM["ALUresult"]
        self.state.WB["Rs"] = self.state.MEM["Rs"]
        self.state.WB["Rt"] = self.state.MEM["Rt"]
        self.state.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]

        """Passing control signal to subsequent pipeline registers"""
        # (see Comp.Org p.313 Figure 4.52)
        self.state.WB["wrt_enable"] = self.state.MEM["wrt_enable"]
        self.state.WB["mem_to_reg"] = self.state.MEM["mem_to_reg"]

        self.mem_stage_pc_result = self.state.MEM["PC"]

        """Data Memory Unit"""
        if self.state.MEM["wrt_mem"] == 1:
            logger.debug("Write data")
            self.ext_data_memory.write(
                address=self.state.MEM["ALUresult"],
                data=self.state.MEM["Store_data"])  # rd2
        self.state.WB["read_data"] = None
        if self.state.MEM["rd_mem"] == 1:
            logger.debug("Read data")
            self.state.WB["read_data"] = self.ext_data_memory.read(self.state.MEM["ALUresult"])

        self.state.WB["Wrt_data"] = multiplexer(self.state.WB["mem_to_reg"],
                                                self.state.WB["ALUresult"],
                                                self.state.WB["read_data"])

    def wb_stage(self):
        logger.debug(f"--------------------- WB stage ")
        logger.info(f"state: {self.state.WB}")
        if self.state.WB["nop"]:
            logger.warning(f"WB stage No Operation")
            return
        # This will stop the stage in the next cycle
        if self.state.EX["nop"] and self.halt_detected:
            logger.info(f"WB stage will nop in the next cycle")
            self.state.WB["nop"] = True


        logger.debug(f"Write Enable: {bool(self.state.WB['wrt_enable'])}")
        if self.state.WB["wrt_enable"] == 1:
            self.register_file.write(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])

    def logger_instruction(self):
        logger.debug(f"Instruction: +.....-+...-+...-+.-+...-+.....-")
        logger.debug(f"Instruction: func7.|rs2.|rs1.|3.|rd..|opcode|")
        logger.debug(f"Instruction: {self.state.ID['Instr']:032b}")

    def logger_data_memory_result(self):
        logger.opt(colors=True).info(
            f"+-----------------------------+---------------------------------+-----------------------------+")
        logger.opt(colors=True).info(f"| Register      | Mem Addr  | \t\t\tValue Bin (Dec) \t\t  |")
        logger.opt(colors=True).info(
            f"| Rs / Rd1      | {self.state.EX['Rs']:05b} ({self.state.EX['Rs']}) | {self.state.EX['Read_data1']:032b} ({self.state.EX['Read_data1']}) |")
        logger.opt(colors=True).info(
            f"| Rt / Rd2      | {self.state.EX['Rt']:05b} ({self.state.EX['Rt']}) | {self.state.EX['Read_data2']:032b} ({self.state.EX['Read_data2']}) |")
        logger.opt(colors=True).info(
            f"| Wrt_reg_addr  | {self.state.EX['Wrt_reg_addr']:05b} ({self.state.EX['Wrt_reg_addr']}) |")
        logger.opt(colors=True).info(
            f"+-----------------------------+---------------------------------+-----------------------------+")

    def update_nop_state(self, prev_stage_nop, halt_detected):
        """
        update next nop state

        Condition 1: if last cycle is NOP and not HALT, clear NOP
        Condition 2: if last stage is NOP, current stage should be NOP

        :param prev_stage_nop: previous stage NOP state
        :param halt_detected: HALT state, if True, return True。
        :return: updated NOP state
        """
        if halt_detected and prev_stage_nop:
            return True
        # Condition 2
        if prev_stage_nop:
            return True
        # Condition 1
        return False

    def set_init_nop_state(self):
        if self.cycle == 0:
            self.state.IF["nop"] = False
            self.state.ID["nop"] = False
            self.state.EX["nop"] = True
            self.state.MEM["nop"] = True
            self.state.WB["nop"] = True
        # elif self.cycle == 1:
        #     self.state.IF["nop"] = False
        #     self.state.ID["nop"] = False
        #     self.state.EX["nop"] = False
        #     self.state.MEM["nop"] = True
        #     self.state.WB["nop"] = True
        # elif self.cycle == 2:
        #     self.state.IF["nop"] = False
        #     self.state.ID["nop"] = False
        #     self.state.EX["nop"] = False
        #     self.state.MEM["nop"] = False
        #     self.state.WB["nop"] = True
        # elif self.cycle == 3:
        #     self.state.IF["nop"] = False
        #     self.state.ID["nop"] = False
        #     self.state.EX["nop"] = False
        #     self.state.MEM["nop"] = False
        #     self.state.WB["nop"] = False

    def printState(self, state, cycle):
        def format_binary(val, bits=32):
            """Format the value as a binary string and pad it to the specified length."""
            if isinstance(val, int):
                return f"{val:0{bits}b}"
            return str(val)

        printstate = ["-" * 70 + "\n", f"State after executing cycle: {cycle}\n"]

        # Format the output of each pipeline stage as required
        formatted_output = {
            "IF": {"nop": state.IF.get("nop"), "PC": state.IF.get("PC")},
            "ID": {"nop": state.ID.get("nop"), "Instr": format_binary(state.ID.get("Instr"))},
            "EX": {
                "nop": state.EX.get("nop"),
                "instr": format_binary(state.EX.get("instr")),
                "Read_data1": format_binary(state.EX.get("Read_data1")),
                "Read_data2": format_binary(state.EX.get("Read_data2")),
                "Imm": format_binary(state.EX.get("Imm"), 12),
                "Rs": format_binary(state.EX.get("Rs"), 5),
                "Rt": format_binary(state.EX.get("Rt"), 5),
                "Wrt_reg_addr": format_binary(state.EX.get("Wrt_reg_addr"), 5),
                "is_I_type": state.EX.get("is_I_type"),
                "rd_mem": state.EX.get("rd_mem"),
                "wrt_mem": state.EX.get("wrt_mem"),
                "alu_op": format_binary(state.EX.get("alu_op"), 2),
                "wrt_enable": state.EX.get("wrt_enable"),
            },
            "MEM": {
                "nop": state.MEM.get("nop"),
                "ALUresult": format_binary(state.MEM.get("ALUresult")),
                "Store_data": format_binary(state.MEM.get("Store_data")),
                "Rs": format_binary(state.MEM.get("Rs"), 5),
                "Rt": format_binary(state.MEM.get("Rt"), 5),
                "Wrt_reg_addr": format_binary(state.MEM.get("Wrt_reg_addr"), 5),
                "rd_mem": state.MEM.get("rd_mem"),
                "wrt_mem": state.MEM.get("wrt_mem"),
                "wrt_enable": state.MEM.get("wrt_enable"),
            },
            "WB": {
                "nop": state.WB.get("nop"),
                "Wrt_data": format_binary(state.WB.get("Wrt_data")),
                "Rs": format_binary(state.WB.get("Rs"), 5),
                "Rt": format_binary(state.WB.get("Rt"), 5),
                "Wrt_reg_addr": format_binary(state.WB.get("Wrt_reg_addr"), 5),
                "wrt_enable": state.WB.get("wrt_enable"),
            },
        }

        # Add the formatted data to printstate
        for stage, fields in formatted_output.items():
            for key, val in fields.items():
                printstate.append(f"{stage}.{key}: {val}\n")

        # Determine file open mode
        perm = "w" if cycle == 0 else "a"

        # Write file
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)
