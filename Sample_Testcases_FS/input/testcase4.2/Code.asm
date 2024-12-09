# Arithmetic-Use Hazard (ADD followed by BNE) & Combined Hazard (LW + ADD + BNE)
0:   LW R1, R0, #0          // Load from Mem[R0+0] to R1 = Val 5
4:   LW R2, R0, #4          // Load from Mem[R0+4] to R2 = Val 3
8:         ADD R3, R1, R2     # Add R1 + R2, store result in R3
12:         BNE R3, R4, #8  # Branch if R3 != R4 (depends on R3, result of ADD) 8!=0=>B2
16:         ADDI R6, R6, 1     # Dummy instruction (should not execute if branch is taken)
20: B2:  ADDI R7, R7, 3     # Branch target
24:         HALT


/*
00000000000000000000000010000011
00000000010000000000000100000011
00000000001000001000000110110011 - 0x002081b3
00000000010000011001010001100011 - 0x00419463
00000000000100110000001100010011 - 0x00130313
00000000001100111000001110010011 - 0x00338393
11111111111111111111111111111111 - 0xFFFFFFFF
*/