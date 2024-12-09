# Load-Use Hazard with Double Stalls
0:         LW R1, 0(R2)       # Load value from memory address in R2 into R1
4:         LW R3, 4(R2)       # Load another value from memory address in R2+4 into R3
8:         BNE R1, R3, #8  # Branch if R1 != R3 (both depend on load instructions)
12:        ADDI R4, R4, 1     # Dummy instruction (should not execute if branch is taken)
16:B3  ADDI R5, R5, 3     # Branch target
20: HALT

/*
00000000000000010010000010000011
00000000010000010010000110000011
00000000001100001001010001100011
00000000000100100000001000010011
00000000001100101000001010010011
11111111111111111111111111111111 - 0xFFFFFFFF
*/