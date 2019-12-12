import distorm3

FILE_NAME = '/path/filename'
START_OFFSET = 0x1000
END_OFFSET = 0x2000
VA = 0x8048000
MODE = distorm3.Decode32Bits
MAX_CHUNK_SIZE = 20

def printGadget(asm):
    print('\naddress: {}'.format(hex(asm[0][0])[:-1]))
    for line in asm:
        print('{}     {}'.format(hex(line[0])[:-1], line[2].lower()))

def checkGadget(g):
    for j, instruction in enumerate(g):
        if 'DB' in instruction[2]:
            break

        if 'RET' in instruction[2] and j > 0:
            printGadget(g[:j + 1])
            break

with open(FILE_NAME, 'rb') as f:
    d = f.read()
    for i in range(START_OFFSET, END_OFFSET - MAX_CHUNK_SIZE):
        checkGadget(distorm3.Decode(VA + i, d[i:i + MAX_CHUNK_SIZE], MODE))