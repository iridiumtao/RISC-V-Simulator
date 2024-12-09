class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0, "PCWrite": 0, "IFIDWrite": 0, "Flush": False, "PCSrc": 0, "BranchPC": 0}
        """ Instruction Fetch. Read 4 lines of the IMEM file 
        
        { nop: No Operation, 
          PC: Program Counter,
          * PCWrite: Output of Hazard Detection Unit, determines whether IF["PC"] + 4 or not,
          * IFIDWrite: Output of Hazard Detection Unit, determines whether to update ID["Instr"],
          * Flush: When branch is taken, flush IF,
          * PCSrc: Output of Branch Condition, 0: PC + 4, 1: PC + Imm
          * BranchPC: PC + Imm, will be used when branch is taken, comes from ID stage
          }
        
        
        "Instruction fetch: The control signals to read instruction memory and to write the PC are always asserted, so there is nothing special to control in this pipeline stage." Comp.Org P.331
        """

        self.ID = {"nop": False, "Instr": 0, "PC": 0}
        """ Corresponding IF/ID Pipeline register
                 
        { nop: No Operation, 
        Instr: 32 bit binary Instruction stores in int,
        * PC: Program Counter,
}
        
        "Instruction decode/register file read: The two source registers are always in the same location in the RISC-V instruction formats, so there is nothing special to control in this pipeline stage."  Comp.Org P.331
        """

        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0,
                   "is_I_type": False, "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0, "mem_to_reg": 0, "PC":0, "alu_control_func": 0, "branch": 0, "jal": 0, "instr": 0}
        """ ID/EX Pipeline register
        
        "Execution/address calculation: The signals to be set are ALUOp and ALUSrc (see Figures 4.49 and 4.50). The signals select the ALU operation and either Read data 2 or a sign-extended immediate as inputs to the ALU."  Comp.Org P.331
                
        { nop: No Operation, 
          instr: 32 bit binary Instruction stores in int, 
          * PC: Program Counter,
        
          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          
          Read_data1: ID Register output: Read register 1 (rd1), 
          Read_data2: ID Register output: Read register 2 (rd2), 
          
          Imm: ID Imm Gen output, 
          
          Wrt_reg_addr: ID Register input: Write register (rd),
          
          * alu_control_func: 4 bits ALU Control opcode,

          alu_op: 2 bits EX Control: ALUOp (connect to ALU control),
          is_I_type: 2 bits EX Control: ALUSrc, 

          rd_mem: 1 bit MEM Control: MemRead, 
          wrt_mem: 1 bit MEM Control: MemWrite,
          * branch: 1 bit MEM Control: Branch,
          * jal: 1 bit MEM Control: Jump and Link Instruction flag,
          
          wrt_enable: 1 bit WB Control: RegWrite,
          * mem_to_reg: 1 bit WB Control: MemtoReg

        }"""

        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0, "mem_to_reg": 0, "PC": 0, "ALUZero": 0, "bne": 0, "branch": 0, "jal": 0}
        """ EX/MEM Pipeline register
        
        "Memory access: The control lines set in this stage are Branch, MemRead, and MemWrite. The branch if equal, load, and store instructions set these signals, respectively. Recall that PCSrc in Figure 4.50 selects the next sequential address unless control asserts Branch and the ALU result was 0." Comp.Org P.331
                
        { nop: No Operation, 
          * PC: Program Counter,
        
          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          Wrt_reg_addr: ID Register input: Write register,
          
          * ALUZero: ALU zero output,
          ALUresult: ALU output,
          Store_data: (*maybe*) ID Register output: Read register 2 (rd2),
          
          * bne: Branch Not Equal instruction flag, derived from alu_control_func,

          rd_mem: 1 bit MEM Control: MemRead, 
          wrt_mem: 1 bit MEM Control: MemWrite,
          * branch: 1 bit MEM Control: Branch,
          * jal: 1 bit MEM Control: Jump and Link Instruction flag
          
          wrt_enable: 1 bit WB Control: RegWrite,
          * mem_to_reg: 1 bit WB Control: MemtoReg}"""

        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0, "mem_to_reg": 0, "ALUresult": 0, "read_data": 0}
        """ MEM/WB Pipeline register
         
         "Write-back: The two control lines are MemtoReg, which decides between sending the ALU result or the memory value to the register file, and RegWrite, which writes the chosen value." Comp.Org P.331
                 
        { nop: No Operation
        
          * read_data: Data Memory Output "Read data",
          * ALUresult: ALU output,
          Wrt_data: this value is written to the register file via "write data" wire,
        
          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          Wrt_reg_addr: ID Register input: Write register,
          
          wrt_enable: 1 bit Control unit output: RegWrite, 
          * mem_to_reg: 1 bit Control unit output: MemtoReg
        }"""


class SingleStageState(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        """ Instruction Fetch. Read 4 lines of the IMEM file 

        { nop: No Operation, PC: Program Counter }


        "Instruction fetch: The control signals to read instruction memory and to write the PC are always asserted, so there is nothing special to control in this pipeline stage." Comp.Org P.331
        """

        self.ID = {"nop": False, "Instr": 0}
        """ Corresponding IF/ID Pipeline register

        { nop: No Operation, Instr: 32 bit binary Instruction stores in int}

        "Instruction decode/register file read: The two source registers are always in the same location in the RISC-V instruction formats, so there is nothing special to control in this pipeline stage."  Comp.Org P.331
        """

        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0,
                   "is_I_type": False, "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        """ Execute the instruction

        "Execution/address calculation: The signals to be set are ALUOp and ALUSrc (see Figures 4.49 and 4.50). The signals select the ALU operation and either Read data 2 or a sign-extended immediate as inputs to the ALU."  Comp.Org P.331

        { nop: No Operation, 

          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          Wrt_reg_addr: ID Register input: Write register,

          Read_data1: ID Register output: Read register 1 (rd1), 
          Read_data2: ID Register output: Read register 2 (rd2), 

          Imm: Imm Gen output, 

          alu_op: 2 bits Control line output: ALUOp (connect to ALU control),
          is_I_type: 2 bits Control unit output: ALUSrc, 

          rd_mem: 1 bit Control unit output: MemRead, 
          wrt_mem: 1 bit Control unit output: MemWrite,

          wrt_enable: 1 bit Control unit output: RegWrite

        }"""

        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0}
        """ Make sure to access memory.py in this stage.
        LOAD and STORE instructions

        "Memory access: The control lines set in this stage are Branch, MemRead, and MemWrite. The branch if equal, load, and store instructions set these signals, respectively. Recall that PCSrc in Figure 4.50 selects the next sequential address unless control asserts Branch and the ALU result was 0." Comp.Org P.331

        { nop: No Operation, 

          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          Wrt_reg_addr: ID Register input: Write register,

          ALUresult: ALU output,
          Store_data: (*maybe*) ID Register output: Read register 2 (rd2),

          Imm: Imm Gen output, 

          alu_op: 2 bits Control line output: ALUOp (connect to ALU control),
          is_I_type: 2 bits Control unit output: ALUSrc, 

          rd_mem: 1 bit Control unit output: MemRead, 
          wrt_mem: 1 bit Control unit output: MemWrite,

          wrt_enable: 1 bit Control unit output: RegWrite }"""

        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}
        """ Update the values of registers in this stage.
         Eg. loading a value into a register, arithmetic result to be written into register

         "Write-back: The two control lines are MemtoReg, which decides between sending the ALU result or the memory value to the register file, and RegWrite, which writes the chosen value." Comp.Org P.331

        { nop: No Operation

          Wrt_data: WB MUX output, write back to register file,

          Rs: ID Register input: rs1, 
          Rt: ID Register input: rs2,
          Wrt_reg_addr: ID Register input: Write register,

          wrt_enable: 1 bit Control unit output: RegWrite 
        }"""
