#!/usr/bin/python

from struct import unpack
from subprocess import Popen, PIPE
from threading import Thread
from multiprocessing import Queue, Process
from time import sleep, time

PROC_NAME = 'Cip'
ADDRESS = '0x5A3E32'  # Must be a hex string
OFFSETS = {
    'name': (0x30, 0x38, 'string'),
    'x': (0x40, 0x44, '<I'),
    'y': (0x44, 0x48, '<I'),
    'z': (0x48, 0x4C, '<I'),
    'id': (0x20, 0x24, '<I'),
    'direction': (0x74, 0x75, '<B'),
    'targetable': (0x76, 0x77, '<B'),
    'xRayAvaible': (0x110, 0x111, '<B'),
    'hp': (0xc8, 0xc9, '<B')
}

class Player():
    def __init__(self, addr):
        self.addr = addr
        self.update()
        
    def update(self):
        self.buffer = mRead(self.addr, 0x120)
        for attr in OFFSETS:
            c = OFFSETS[attr]
            if c[2] == 'string':
                c = readString(unpack('<Q', self.buffer[c[0]:c[1]])[0])
            else:
                c = unpack(c[2], self.buffer[c[0]:c[1]])[0]
            setattr(self, attr, c)

class TraceBreakpoint(gdb.Breakpoint):
    def __init__(self, addr, queue):
        gdb.Breakpoint.__init__(self, '*{}'.format(addr), type=gdb.BP_BREAKPOINT, internal=True)
        self.queue = queue

    def stop(self):
        self.queue.put(int(gdb.selected_frame().read_register('rbx')))

def getProcessId(uniqueKeyword):
    return Popen(['pgrep', '-f', uniqueKeyword], stdout=PIPE).communicate()[0].strip().split('\n')[0]

def readString(addr):
    try:
        length = unpack('<I', mRead(addr + 4, 4))[0]
        b = mRead(addr + 0x18, length * 2)
        return ''.join([chr(unpack('<B', b[i])[0]) for i in range(0, length * 2, 2)])
    except:
        print('Cannot read player name.')
        return False

def runGdb(queue):
    TraceBreakpoint(ADDRESS, queue)
    gdb.execute('set pagination off\nset print thread-events off\nattach {}\ncontinue'.format(getProcessId(PROC_NAME)))

def mRead(addr, size):
    try:
        f.seek(addr)
        return f.read(size)
    except:
        print('Something went wrong while reading memory')

    return False

def main(queue):
    while True:
        while not queue.empty():
            addr = queue.get()
            players[addr] = Player(addr)
        sleep(0.001)

def init():
    q = Queue()
    p = Process(target=runGdb, args=(q,))
    p.start()
    t = Thread(target=main, args=(q,))
    t.start()

f = open('/proc/{}/mem'.format(getProcessId(PROC_NAME)), 'rb')
players = {}
init()

while True:
    for player in list(players):
        p = players[player]
        p.update()
        if p.xRayAvaible == 0:
            del players[player]
            continue
        
        # Write your code here
        print(p.xRayAvaible, p.name, p.x, p.y, p.z)
    
    # Write your code here
    sleep(1)
