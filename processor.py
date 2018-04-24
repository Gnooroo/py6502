#!/usr/bin/python3

import sys
from common import *
from cpu import *
from ram import *

"""
memory map:
    0000 - 07FF: RAM
    2000 - 2007: CPU to PPU writes
    2008 - 3FFF: mirrors of the addr range
    4000 - 401F: IO ports and Sound
    4020 - 4FFF: rarely used, by some cartridges
    5000 - 5FFF: rarely used, by some cartridges
    6000 - 7FFF: cartridge WRAM
    8000 - FFFF: main area cartridge ROM is mapped to

FFFC - reset vector
"""

class Processor():

    def __init__(self, verbose=False):
        self.opcodes = OPCODES_6502
        self.clk = Clock(0)
        self.ram = RAM()
        self.cpu = CPU(self.clk, self.ram, self.opcodes, self.clk)
        self.cpu.config(pc=0, status=0x20, a=0, x=0, y=0, sp=0xFF, verbose=verbose)
        self.verbose = verbose

    def set_verbose(self, verbose):
        self.verbose = verbose
        self.cpu.config(verbose=verbose)
        
    def disassemble(self, size=None):
        if size is None:
            end = self.ram.size
        else:
            end = self.cpu.pc + size

        if self.verbose:
            print('Address  Hexdump    Disassembly')
            print('-------------------------------')
            
        while self.cpu.pc < end:
            print(self.cpu.decode_next())

    def execute(self):
        while (self.cpu.execute() != Op.BRK):
            continue
        
def main():
    verbose = False
    if '-v' in sys.argv:
        verbose = True
        sys.argv.remove('-v')
        
    proc = Processor(verbose=verbose)
    proc.ram.load_str('65 20')
    proc.ram.load_str('ff', 0x20)
    #print(proc.ram.to_str(0x0, 0x40))
    #print(proc.cpu.reg_to_str())
    proc.execute()

if __name__ == '__main__':
    main()
        
