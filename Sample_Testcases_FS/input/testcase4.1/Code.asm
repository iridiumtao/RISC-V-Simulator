0:         lw R1, 4(R3)       # Load value from memory address in R3+4 into R1
4:         BNE R1, R2, #8  # Branch if R1 != R2 (depends on R1, loaded by LW)
8:         ADDI R4, R4, 1     # Dummy instruction (should not execute if branch is taken)
12: B1:  ADDI R5, R5, 2     # Branch target
16:        ADD R3, R1, R2     # Add R1 + R2, store result in R3
20:        BNE R3, R4, #8  # Branch if R3 != R4 (depends on R3, result of ADD)
24:        SUBI R6, R6, 1     # Dummy instruction (should not execute if branch is taken)
28: B2:  ADDI R7, R7, 3     # Branch target
32:        LW R1, 4(R2)       # Load value from memory address in R2+4 into R1
36:        ADD R3, R1, R2     # Add R1 + R2, store result in R3
40:        BNE R3, R4, #8  # Branch if R3 != R4 (depends on R3, result of ADD)
44:        ORI R5, R5, 0xFF   # Dummy instruction (should not execute if branch is taken)
48: B3:  XORI R6, R6, 0x0F  # Branch target
52:        LW R1, 0(R2)       # Load value from memory address in R2 into R1
56:        LW R3, 4(R2)       # Load another value from memory address in R2+4 into R3
60:        BNE R1, R3, #8  # Branch if R1 != R3 (both depend on load instructions)
64:        ADDI R4, R4, 1     # Dummy instruction (should not execute if branch is taken)
68: B4:  SUBI R5, R5, 1     # Branch target
72: HALT

/*
00000000010000011010000010000011 - 0x0041a083
00000000001000001001010001100011 - 0x00209463
00000000000100100000001000010011 - 0x00120213
00000000001000101000001010010011 - 0x00228293
11111111111111111111111111111111 - 0xFFFFFFFF
*/