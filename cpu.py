from common import *

"""
    C = 0 #Carry flag
    Z = 1 #Zero flag
    I = 2 #Interrupt enable/disable flag
    D = 3 #decimal mode status flag
    B = 4 #software interrupt flag
    U = 5 #unused. logical 1 at all times
    V = 6 #overflow flag
    S = 7 #sign flag
"""
class StatusRegister(Register):
    bitmap = {'C':0, 'Z':1, 'I':2, 'D':3, 'B':4, 'U':5, 'V':6, 'S':7}
    
    def __init__(self, value):
        Register.__init__(StatusRegister, value)        

    def __getattr__(self, attrName):
        return self[StatusRegister.bitmap[attrName]]
        
    def __setattr__(self, attrName, val):
        if attrName in StatusRegister.bitmap.keys():
            self[StatusRegister.bitmap[attrName]] = val
        else:
            super().__setattr__(attrName, val)

    def __repr__(self):
        return 'S V - B D I Z C\n%d %d %d %d %d %d %d %d' % \
               (self.S, self.V, self.U, self.B, self.D, self.I, self.Z, self.C)

class CPU:              
    def __init__(self, clk, ram, opcodes, pc=0, status=0x20, a=0, x=0, y=0, sp=0xFF, verbose=False):
        self.ram = ram
        self.opcodes = opcodes
        self.pc = pc
        self.status = StatusRegister(status)
        self.y = Register(y)
        self.x = Register(x)
        self.a = Register(a)
        self.sp = Register(sp)
        self.clk = clk
        self.verbose = verbose

    def config(self, pc=None, status=None, a=None, x=None, y=None, sp=None, clk_cnt=None, verbose=None):
        if pc is not None:
            self.pc = pc

        if status is not None:
            self.status = StatusRegister(status)

        if y is not None:
            self.y = Register(y)

        if x is not None:
            self.x = Register(x)

        if a is not None:
            self.a = Register(a)

        if sp is not None:
            self.sp = Register(sp)

        if clk_cnt is not None:
            self.clk.counter = clk_cnt

        if verbose is not None:
            self.verbose = verbose

    def print_opcodes(self):
        for c in range(0, len(self.opcodes), 2):
            print('%-30s %s' % (self.opcodes[c], self.opcodes[c+1]))

    def print_context(self, addr=0, size=0x20):
        print(self.reg_to_str())
        print(self.ram.to_str(addr, size))

    def reg_to_str(self):
        return 'A:%s X:%s Y:%s PC:%s SP:%s SV-BDIZC:%s Clk:%d' % \
               (hexStr(self.a.value), hexStr(self.x.value), hexStr(self.y.value), \
                hexStr(self.pc), hexStr(self.sp.value), binStr(self.status.value), \
                self.clk.counter)

    def read_oper(self, op, oper=None):
        oper_size = op.size - 1
        if oper_size == 0:
            return None

        if oper is None:
            oper = self.read_next(oper_size)
        
        if op.mode == AddrMode.REL:
            oper = toSigned(oper) + self.pc

        return oper

    def fetch_src(self, op):
        src = None
        oper = self.read_oper(op)

        if op.mode in (AddrMode.ZP, AddrMode.ABS):
           pass 
        elif op.mode == AddrMode.ZPX:
            oper += self.x.value
        elif op.mode == AddrMode.ZPY:
            oper += self.y.value
        elif op.mode == AddrMode.ABSX:
            oper += self.x.value
        elif op.mode == AddrMode.ABSY:
            oper += self.y.value
        elif op.mode == AddrMode.IND:
            ind_addr = oper
            oper = cpu.read(ind_addr, 2)
        elif self.mode == AddrMode.INDX:
            ind_addr = (oper + self.x.value) & 0x00ff
            oper = self.read(ind_addr, 2)
        elif self.mode == AddrMode.INDY:
            ind_addr = oper
            oper = self.read(ind_addr, 2) + self.y.value
            
        if oper is not None:
            src = self.read(oper)
            
        return src, oper

    def store_src(self, op, src, addr):
        if op.mode is None:
            return
       
        dest = None
        if op.mode in (AddrMode.A, AddrMode.IMM):
            self.a = src
            dest = 'A'
        elif op.mode in (AddrMode.ZP, AddrMode.ABS):
            self.ram[addr] = src
            dest = hexStr(addr, size=4, prefix='$')

        if dest is not None:
            self.clk.tick()

        if self.verbose and dest is not None:
            print('%s -> %s' % (hexStr(src, prefix='$'), dest))

    def do_BRK(self, op):
        self.clk.tick(7)
        pass

    def do_ADC(self, op):
        src, addr = self.fetch_src(op)

        temp = src + self.a.value + self.status.C
        self.set_zero(temp & 0xff)

        #decimal mode not supported
        self.set_sign(temp)

        #Calc overflow
        self.set_overflow(temp)
        self.set_carry(temp > 0xff)

        self.store_src(op, temp & 0xff, addr)
        self.clk.tick()

    def do_ASL(self, op):
        src, addr = self.fetch_src(op)
        
        self.set_carry(src & 0x80)
        src = src << 1
        src = src & 0xff
        self.set_sign(src)
        self.set_zero(src)

        self.store_src(op, src, addr)

        self.clk.tick()

    def execute_op(self, op): 
        getattr(self, 'do_' + str(op.code))(op)

    def execute(self):
        if self.verbose:
            self.print_op_bytes()

        opcode = self.opcodes[self.read_next()]
        self.execute_op(opcode)

        if self.verbose:
            print(self.reg_to_str())

        return opcode.code

    def get_op_bytes(self, addr):
        opcode = self.opcodes[self.ram[addr]]
        return self.ram[addr:addr+opcode.size]

    def print_op_bytes(self):
        print('Execute: ' + self.decode_op_bytes(self.get_op_bytes(self.pc)))

    def decode_op_bytes(self, op_bytes):
        oper_bytes = None
        opcode = self.opcodes[op_bytes[0]]
        if len(op_bytes) > 1:
            oper_bytes = int.from_bytes(op_bytes[1:], 'little')

        oper = self.read_oper(opcode, oper_bytes)
        if oper is not None:
            return '%s %s' % (str(opcode.code), str(opcode.mode.print_oper(oper)))

        return str(opcode.code)

    def decode_next(self):
        op_bytes = self.get_op_bytes(self.pc)
        decoded = self.decode_op_bytes(op_bytes)
        addr = self.pc
        op_size = len(op_bytes)

        self.pc += op_size

        if self.verbose:
            addr_str = hexStr(addr, size=4, prefix='$')
            hex_str = self.ram.to_str(addr, op_size, formatted=False)

            return '%-8s %-10s %-12s' % (addr_str, hex_str, decoded)
        
        return decoded

    def set_sign(self, src):
        self.status.S = testBit(src, 7)

    def set_zero(self, src):
        self.status.Z = src == 0

    def set_carry(self, src):
        self.status.C = src & 0x80

    # TODO: fix this
    def set_overflow(self, overflow):
        self.status.V = overflow

    def read_next(self, size=1):
        data = self.read(self.pc, size)

        self.pc += size

        return data
    
    def read(self, addr, size=1):
        self.clk.tick()
        
        raw_bytes = self.ram[addr:addr+size]

        result = int.from_bytes(raw_bytes, 'little')
        if self.verbose:
            print ('%s <- %s' % \
                    (hexStr(result, size=2, prefix='$'), hexStr(addr, size=4, prefix='$')))

        return result

