0:         lw R1, #4(R3)       # Load value from memory address in R3 into R1
4:         BNE R1, R2, #8  # Branch if R1 != R2 (depends on R1, loaded by LW)
8:         ADDI R4, R4, 1     # Dummy instruction (should not execute if branch is taken)
12: B1:  ADDI R5, R5, 2     # Branch target
16: HALT

/*
00000000010000011010000010000011 - 0x0041a083
00000000001000001001010001100011 - 0x00209463
00000000000100100000001000010011 - 0x00120213
00000000001000101000001010010011 - 0x00228293
11111111111111111111111111111111 - 0xFFFFFFFF
*/