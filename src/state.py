class State(object):
    def __init__(self):
        # Read 4 lines of the IMEM file
        self.IF = {"nop": False, "PC": 0}

        # Convert the 32 bits into an instruction. (Big endian)
        self.ID = {"nop": False, "Instr": 0}

        # Execute the instruction
        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0,
                   "is_I_type": False, "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}

        # Make sure to access memory.py in this stage.
        # LOAD and STORE instructions
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0}

        # Update the values of registers in this stage.
        # Eg. loading a value into a register, arithmetic result to be written into register
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}
