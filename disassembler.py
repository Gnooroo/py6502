#!/usr/bin/python3

import sys
from common import *
from processor import *

def disassemble(start_pc, hex_str, verbose):
    proc = Processor(verbose=verbose)
    proc.cpu.config(pc=start_pc)
    proc.ram.load_str(hex_str, start_pc)
    proc.disassemble(len(hex_str.replace(' ', '')) / 2)
    
def usage():
    out = 'python3 %s [Starting Hex Addr] [Byte String]\n' % sys.argv[0]
    out += 'Example: \n'
    out += 'python3 %s 0x600 "20 09 06 20 0c 06 20 12 06 a2 00 60 e8 e0 05 d0 fb 60 00"' % sys.argv[0]
    return out

def main(argv):
    if len(argv) < 3 or argv[1] == '-h':
        print(usage())
        return   

    verbose = False
    if '-v' in argv:
        verbose = True
        argv.remove('-v')
        
    start_pc = int(argv[1], 16)
    hex_str = argv[2]

    disassemble(start_pc, hex_str, verbose)

if __name__ == '__main__':
    main(sys.argv)
