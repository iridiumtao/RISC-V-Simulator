# RISC-V 5-Stage Pipelined Simulator

This is a Single-stage and 5-stage pipelined RISC-V Simulator written in Python.
The simulator reads the binary content of dmem.txt (data memory) and imem.txt (instruction memory) in `./iodir` and outputs step-by-step results in RFResult.txt (Register File Result) and StateResult.txt (Pipeline register state), the DMEMResult.txt (Data MEMory Result), and PerformanceMetrics_Result.txt

This project is part of the NYU Master of Science in Computer Engineering (MSCE) course focused on Computing Systems Architecture (CSA).

## Schematic

### Single Stage

![Schematic RISCV Project Single Stage.png](docs/Schematic%20RISCV%20Project%20Single%20Stage.png)
Schematic modified from [Textbook](##Reference) Figure 4.25

**Description:**

The simulator was designed to follow the Simple Implementation Scheme from the textbook Computer Organization and Design RISC-V Edition 2nd. To utilize the pipeline and the State class, I implemented the pipeline registers and Pipelined Control mentioned in Chapter 4.7.
However, the BNE and JAL instructions are not achievable with the Simple Implementation Scheme. So, compared to the single stage datapath from the textbook Figure 4.25, I made the following changes to complete the functionality:
- added 2 control signals (ALUSrcA, JAL)
- added 1 MUX (ALU input A)
- added 2 gates (XOR, OR)
- modified a MUX (ALU input B)
- connected PC to a MUX(ALU input A) and instruction[12] to the XOR gate.

### Five Stage

![Schematic RISCV Project Five Stage.png](docs/Schematic%20RISCV%20Project%20Five%20Stage.png)
Modified from [Textbook](##Reference) Figure 4.62

**Description:**

In the Five-Stage machine, I added the forwarding unit and the hazard control unit to solve hazards introduced in the Mulit-stage pipeline. I kept the design of the control unit and PCSrc (from the result of 3 logic gates) and significantly modified other parts of the branch condition  by moving it from the EX stage to the ID stage. Additionally, I implemented a dedicated forwarding unit to handle branch decision input choices.
## Key Points to Know for Grading But Not Mentioned in the Provided Document

1.	State Results:
- State results are **not graded**.
- Variations in implementation logic can cause differences in state results, which is fine.
2. Grading Criteria:
- Focus on Register File (RF) and Data Memory (DMEM) files; they must match test cases exactly.
- Even minor discrepancies in binary values (e.g., a 1 instead of a 0) will result in point deductions.
3. Performance Metrics:
- Values like IPC and CPI must match expected results.
- The way you format them should be fine, but preferred using the format provided for easier auto-grading.
- Deviations may result in manual grading, which is discouraged due to added complexity.
4. File Format:
- Ensure output files (RF, DMEM) are identical to the provided format and test cases to avoid issues during grading.

## Reference

All references came from:
Computer Organization and Design RISC-V Edition 2nd ED 2021 by **David A. Patterson & John L. Hennessy** 

## License

This repo is licensed under the MIT License