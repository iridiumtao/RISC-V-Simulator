# Sigle Stage
The simulator was designed to follow the Simple Implementation Scheme from the textbook Computer Organization and Design RISC-V Edition 2nd. To utilize the pipeline and the State class, I implemented the pipeline registers and Pipelined Control mentioned in Chapter 4.7.
However, the BNE and JAL instructions are not achievable with the Simple Implementation Scheme. So, compared to the single stage datapath from the textbook Figure 4.25, I made the following changes to complete the functionality:
- added 2 control signals (ALUSrcA, JAL)
- added 1 MUX (ALU input A)
- added 2 gates (XOR, OR)
- modified a MUX (ALU input B)
- connected PC to a MUX(ALU input A) and instruction[12] to the XOR gate.
 
### Possible optimizations:
Compared to the multistage design shown in Figure e4.5.4, which has a stronger control unit and reduces the use of an Adder and an XOR gate, my simulator can be improved with fewer components and implementing multistage functionality.
In addition, adding Forwarding and Branch Prediction would reduce data hazards and minimize stalls to improve performance.

# Five Stage 

In the Five-Stage machine, I added the forwarding unit and the hazard control unit to solve hazards introduced in the Mulit-stage pipeline. I kept the design of the control unit and PCSrc (from the result of 3 logic gates) and modified other parts of the branch condition significantly by moving it from the EX stage to the ID stage. I added a dedicated forwarding unit to handle branch decision input choices.

### Possible optimizations:
**Dynamic Branch Prediction**: Implement a branch predictor (e.g., a two-bit predictor or branch history table) to improve prediction accuracy and reduce misprediction stalls.
**Instruction-Level Parallelism**: Implement a dynamic scheduling mechanism to resolve dependencies dynamically, enabling out-of-order execution and minimizing pipeline stalls.

### Compare the results from both the single stage and the five stage pipelined processor implementations and explain why one is better than the other. (5 points):

The Single-Stage Machine achieves a near-perfect CPI (1.02564 in testcase 1), as all the steps required to execute an instruction—fetch, decode, execute, memory access, and write-back—are completed in a single cycle. However, this benefit comes with a significant tradeoff: the clock cycle in a Single-Stage Machine must be long enough to accommodate the slowest instruction, resulting in a longer cycle time.

On the other hand, the Five-Stage Pipelined Machine divides these steps across multiple pipeline stages, allowing for much shorter clock cycles. This design enables overlapping execution of multiple instructions, theoretically offering higher throughput. However, due to pipeline overheads like stalls and control hazards, the Five-Stage Machine has a slightly higher CPI (1.17949 in testcase 1). Despite this, as the number of instructions increases, the shorter cycle time of the pipelined architecture should result in better performance compared to the Single-Stage Machine.

Therefore, while the Single-Stage Machine seems more efficient for a small number of instructions due to its simplicity and low CPI, the Five-Stage Pipelined Machine is expected to outperform larger instruction sets thanks to its ability to exploit Pipelined Datapath.
