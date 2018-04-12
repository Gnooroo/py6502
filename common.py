from enum import Enum

def hexStr(num, size=2, prefix=''):
    return prefix + format(num, '0%dx' % size)

def binStr(num, size=8, prefix=''):
    #return bin(num)[2:] if prefix is None else bin(num)
    return prefix + format(num, '0%db' % size)

def testBit(num, offset):
    mask = 1 << offset
    return (num & mask)

def setBit(num, offset):
    mask = 1 << offset
    return (num | mask)

def clearBit(num, offset):
    mask = ~(1 << offset)
    return (num & mask)

def toggleBit(num, offset):
    mask = 1 << offset
    return (num ^ mask)

def toSigned(byte):
    if byte > 127:
        return byte - 256
    else:
        return byte
    
class NoValue(Enum):
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class Register():
    def __init__(self, value):
        self.value = value

    def __getitem__(self, pos):
        return (self.value & (1 << pos)) > 0

    def __setitem__(self, pos, value):
        if value is None or value == 0:
            self.value = clearBit(self.value, pos)
        else:
            self.value = setBit(self.value, pos)
        
    def __repr__(self):
        return bin(self.value)[2:]

class Clock():
    def __init__(self, counter):
        self.counter = counter

    def tick(self, ticks=1):
        self.counter += ticks

class Op(NoValue):
    ADC = 'Add Memory to Accumulator with Carry'
    AND = '"AND" Memory with Accumulator'
    ASL = 'Shift Left One Bit (Memory or Accumulator)'
    BCC = 'Branch on Carry Clear'
    BCS = 'Branch on Carry Set'
    BEQ = 'Branch on Result Zero'
    BIT = 'Test Bits in Memory with Accumulator'
    BMI = 'Branch on Result Minus'
    BNE = 'Branch on Result not Zero'
    BPL = 'Branch on Result Plus'
    BRK = 'Force Break'
    BVC = 'Branch on OVerflow Clear'
    BVS = 'Branch on Overflow Set'
    CLC = 'Clear Carry Flag'
    CLD = 'Clear Decimal Mode'
    CLI = 'Clear interrupt Disable Bit'
    CLV = 'Clear Overflow Flag'
    CMP = 'Compare Memory and Accumulator'
    CPX = 'Compare Memory and Index X'
    CPY = 'Compare Memory and Index Y'
    DEC = 'Decrement Memory by One'
    DEX = 'Decrement Index X by One'
    DEY = 'Decrement Index Y by One'
    EOR = '"Exclusive-Or" Memory with Accumulator'
    INC = 'Increment Memory by One'
    INX = 'Increment Index X by One'
    INY = 'Increment Index Y by One'
    JMP = 'Jump to New Location'
    JSR = 'Jump to New Location Saving Return Address'
    LDA = 'Load Accumulator with Memory'
    LDX = 'Load Index X with Memory'
    LDY = 'Load Index Y with Memory'
    LSR = 'Shift Right One Bit (Memory or Accumulator)'
    NOP = 'No Operation'
    ORA = '"OR" Memory with Accumulator'
    PHA = 'Push Accumulator on Stack'
    PHP = 'Push Processor Status on Stack'
    PLA = 'Pull Accumulator from Stack'
    PLP = 'Pull Processor Status from Stack'
    ROL = 'Rotate One Bit Left (Memory or Accumulator)'
    ROR = 'Rotate One Bit Right (Memory or Accumulator)'
    RTI = 'Return from Interrupt'
    RTS = 'Return from Subroutine'
    SBC = 'Substract Memory from Accumulator with Borrow'
    SEC = 'Set Carry Flag'
    SED = 'Set Decimal Mode'
    SEI = 'Set Interrupt Disable Status'
    STA = 'Store Accumulator in Memory'
    STX = 'Store Index X in Memory'
    STY = 'Store Index Y in Memory'
    TAX = 'Transfer Accumulator to Index X'
    TAY = 'Transfer Accumulator to Index Y'
    TSX = 'Transfer Stack Pointer to Index X'
    TXA = 'Transfer Index X to Accumulator'
    TXS = 'Transfer Index X to Stack Pointer'
    TYA = 'Transfer Index Y to Accumulator'
    
class AddrMode(NoValue):
    A = 'Accumulator'
    IMM = 'Immediate'
    REL = 'Relative'
    ZP = 'Zero Page'
    ZPX = 'Zero Page,X'
    ZPY = 'Zero Page,Y'
    ABS = 'Absolute'
    ABSX = 'Absolute,X'
    ABSY = 'Absolute,Y'
    IND = '(Indrect)'
    INDX = '(Indirect,X)'
    INDY = '(Indirect),Y'

class OpCode:
    def __init__(self, binary, op_code, op_mode=None, op_size=None, op_cycles=None):
        self.binary = binary
        self.code = op_code
        self.mode = op_mode
        self.size = OpCode.get_size(self.mode)
        self.cycles = op_cycles
        self.name = str(op_mode)

    def __str__(self):
        return self.__repr__();
    
    def __repr__(self):
        output = '%s - %s' % (hexStr(self.binary), self.code)
        if self.mode:
            output += ' - %s' % self.mode.value

        if self.size:
            output += ' - %d' % self.size

        return output

    @staticmethod
    def get_size(mode):
        if mode in (AddrMode.IMM, AddrMode.REL, AddrMode.ZP, AddrMode.ZPX, AddrMode.ZPY, AddrMode.INDX, AddrMode.INDY):
            size = 2
        elif mode in (AddrMode.ABS, AddrMode.ABSX, AddrMode.ABSY, AddrMode.IND):
            size = 3
        else:
            size = 1

        return size

    def get_mem(self):
        pass

    def print_oper(self, oper):
        return {
                AddrMode.A: 'A',
                AddrMode.IMM: '#$%s' % hexStr(oper),
                AddrMode.REL: '$%s' % hexStr(oper, size=4),
                AddrMode.ZP: '$%s' % hexStr(oper),
                AddrMode.ZPX: '$%s,X' % hexStr(oper),
                AddrMode.ZPY: '$%s,Y' % hexStr(oper),
                AddrMode.ABS: hexStr(oper, size=4, prefix='$'),
                AddrMode.ABSX: '$%s,X' % hexStr(oper, size=4),
                AddrMode.ABSY:'$%s,Y' % hexStr(oper, size=4),
                AddrMode.IND: '($%s)' % hexStr(oper, size=4),
                AddrMode.INDX:'($%s,X)' % hexStr(oper),
                AddrMode.INDY:'($%s),Y' % hexStr(oper),
                AddrMode.REL:'($%s)' % hexStr(oper),
                }.get(self.mode, None)


class Instruction():
    def __init__(self, opcode, ram, addr):
        self.opcode = opcode
        self.bytes = ram[addr:addr+opcode.size]


OPCODES_6502 = [OpCode(0x00, Op.BRK), OpCode(0x01, Op.ORA, AddrMode.INDX), \
                OpCode(0x02, None), OpCode(0x03, None), \
                OpCode(0x04, None), OpCode(0x05, Op.ORA, AddrMode.ZP), \
                OpCode(0x06, Op.ASL, AddrMode.ZP), OpCode(0x07, None), \
                OpCode(0x08, Op.PHP), OpCode(0x09, Op.ORA, AddrMode.IMM), \
                OpCode(0x0A, Op.ASL, AddrMode.A, 1), OpCode(0x0B, None), \
                OpCode(0x0C, None), OpCode(0x0D, Op.ORA, AddrMode.ABS), \
                OpCode(0x0E, Op.ASL, AddrMode.ABS, 3), OpCode(0x0F, None), \
                OpCode(0x10, Op.BPL, AddrMode.REL), OpCode(0x11, Op.ORA, AddrMode.INDY), \
                OpCode(0x12, None), OpCode(0x13, None), \
                OpCode(0x14, None), OpCode(0x15, Op.ORA, AddrMode.ZPX), \
                OpCode(0x16, Op.ASL, AddrMode.ZPX, 2), OpCode(0x17, None), \
                OpCode(0x18, Op.CLC), OpCode(0x19, Op.ORA, AddrMode.ABSY), \
                OpCode(0x1A, None), OpCode(0x1B, None), \
                OpCode(0x1C, None), OpCode(0x1D, Op.ASL, AddrMode.ABSX), \
                OpCode(0x1E, Op.ASL, AddrMode.ABSX, 3), OpCode(0x1F, None), \
                OpCode(0x20, Op.JSR, AddrMode.ABS), OpCode(0x21, Op.AND, AddrMode.INDX), \
                OpCode(0x22, None), OpCode(0x23, None), \
                OpCode(0x24, Op.BIT, AddrMode.ZP), OpCode(0x25, Op.AND, AddrMode.ZP), \
                OpCode(0x26, Op.ROL, AddrMode.ZP), OpCode(0x27, None), \
                OpCode(0x28, Op.PLP), OpCode(0x29, Op.AND, AddrMode.IMM), \
                OpCode(0x2A, Op.ROL, AddrMode.A), OpCode(0x2B, None), \
                OpCode(0x2C, Op.BIT, AddrMode.ABS), OpCode(0x2D, Op.AND, AddrMode.ABS), \
                OpCode(0x2E, Op.ROL, AddrMode.ABS), OpCode(0x2F, None), \
                OpCode(0x30, Op.BMI, AddrMode.REL), OpCode(0x31, Op.AND, AddrMode.INDY), \
                OpCode(0x32, None), OpCode(0x33, None), \
                OpCode(0x34, None), OpCode(0x35, Op.AND, AddrMode.ZPX), \
                OpCode(0x36, Op.ROL, AddrMode.ZPX), OpCode(0x37, None), \
                OpCode(0x38, Op.SEC), OpCode(0x39, Op.AND, AddrMode.ABSY), \
                OpCode(0x3A, None), OpCode(0x3B, None), \
                OpCode(0x3C, None), OpCode(0x3D, Op.AND, AddrMode.ABSX), \
                OpCode(0x3E, Op.ROL, AddrMode.ABSX), OpCode(0x3F, None), \
                OpCode(0x40, Op.RTI), OpCode(0x41, Op.EOR, AddrMode.INDX), \
                OpCode(0x42, None), OpCode(0x43, None), \
                OpCode(0x44, None), OpCode(0x45, Op.EOR, AddrMode.ZP), \
                OpCode(0x46, Op.LSR, AddrMode.ZP), OpCode(0x47, None), \
                OpCode(0x48, Op.PHA), OpCode(0x49, Op.EOR, AddrMode.IMM), \
                OpCode(0x4A, Op.LSR, AddrMode.A), OpCode(0x4B, None), \
                OpCode(0x4C, Op.JMP, AddrMode.ABS), OpCode(0x4D, Op.EOR, AddrMode.ABS), \
                OpCode(0x4E, Op.LSR, AddrMode.ABS), OpCode(0x4F, None), \
                OpCode(0x50, Op.BVC, AddrMode.REL), OpCode(0x51, Op.EOR, AddrMode.INDY), \
                OpCode(0x52, None), OpCode(0x53, None), \
                OpCode(0x54, None), OpCode(0x55, Op.EOR, AddrMode.ZPX), \
                OpCode(0x56, Op.LSR, AddrMode.ZPX), OpCode(0x57, None), \
                OpCode(0x58, Op.CLI), OpCode(0x59, Op.EOR, AddrMode.ABSY), \
                OpCode(0x5A, None), OpCode(0x5B, None), \
                OpCode(0x5C, None), OpCode(0x5D, Op.EOR, AddrMode.ABSX), \
                OpCode(0x5E, Op.LSR, AddrMode.ABSX), OpCode(0x5F, None), \
                OpCode(0x60, Op.RTS), OpCode(0x61, Op.ADC, AddrMode.INDX), \
                OpCode(0x62, None), OpCode(0x63, None), \
                OpCode(0x64, None), OpCode(0x65, Op.ADC, AddrMode.ZP), \
                OpCode(0x66, Op.ROR, AddrMode.ZP), OpCode(0x67, None), \
                OpCode(0x68, Op.PLA), OpCode(0x69, Op.ADC, AddrMode.IMM), \
                OpCode(0x6A, Op.ROR, AddrMode.A), OpCode(0x6B, None), \
                OpCode(0x6C, Op.JMP, AddrMode.IND), OpCode(0x6D, Op.ADC, AddrMode.ABS), \
                OpCode(0x6E, Op.ROR, AddrMode.ABS), OpCode(0x6F, None), \
                OpCode(0x70, Op.BVS, AddrMode.REL), OpCode(0x71, Op.ADC, AddrMode.INDY), \
                OpCode(0x72, None), OpCode(0x73, None), \
                OpCode(0x74, None), OpCode(0x75, Op.ADC, AddrMode.ZPX), \
                OpCode(0x76, Op.ROR, AddrMode.ZPX), OpCode(0x77, None), \
                OpCode(0x78, Op.SEI), OpCode(0x79, Op.ADC, AddrMode.ABSY), \
                OpCode(0x7A, None), OpCode(0x7B, None), \
                OpCode(0x7C, None), OpCode(0x7D, Op.ADC, AddrMode.ABSX), \
                OpCode(0x7E, Op.ROR, AddrMode.ABSX), OpCode(0x7F, None), \
                OpCode(0x80, None), OpCode(0x81, Op.STA, AddrMode.INDX), \
                OpCode(0x82, None), OpCode(0x83, None), \
                OpCode(0x84, Op.STY, AddrMode.ZP), OpCode(0x85, Op.STA, AddrMode.ZP), \
                OpCode(0x86, Op.STX, AddrMode.ZP), OpCode(0x87, None), \
                OpCode(0x88, Op.DEY), OpCode(0x89, None), \
                OpCode(0x8A, Op.TXA), OpCode(0x8B, None), \
                OpCode(0x8C, Op.STY, AddrMode.ABS), OpCode(0x8D, Op.STA, AddrMode.ABS), \
                OpCode(0x8E, Op.STX, AddrMode.ABS), OpCode(0x8F, None), \
                OpCode(0x90, Op.BCC, AddrMode.REL), OpCode(0x91, Op.STA, AddrMode.INDY), \
                OpCode(0x92, None), OpCode(0x93, None), \
                OpCode(0x94, Op.STY, AddrMode.ZPX), OpCode(0x95, Op.STA, AddrMode.ZPX), \
                OpCode(0x96, Op.STX, AddrMode.ZPY), OpCode(0x97, None), \
                OpCode(0x98, Op.TYA), OpCode(0x99, Op.STA, AddrMode.ABSY), \
                OpCode(0x9A, Op.TXS), OpCode(0x9B, None), \
                OpCode(0x9C, None), OpCode(0x9D, Op.STA, AddrMode.ABSX), \
                OpCode(0x9E, None), OpCode(0x9F, None), \
                OpCode(0xA0, Op.LDY, AddrMode.IMM), OpCode(0xA1, Op.LDA, AddrMode.INDX), \
                OpCode(0xA2, Op.LDX, AddrMode.IMM), OpCode(0xA3, None), \
                OpCode(0xA4, Op.LDY, AddrMode.ZP), OpCode(0xA5, Op.LDA, AddrMode.ZP), \
                OpCode(0xA6, Op.LDX, AddrMode.ZP), OpCode(0xA7, None), \
                OpCode(0xA8, Op.TAY), OpCode(0xA9, Op.LDA, AddrMode.IMM), \
                OpCode(0xAA, Op.TAX), OpCode(0xAB, None), \
                OpCode(0xAC, Op.LDY, AddrMode.ABS), OpCode(0xAD, Op.LDA, AddrMode.ABS), \
                OpCode(0xAE, Op.LDX, AddrMode.ABS), OpCode(0xAF, None), \
                OpCode(0xB0, Op.BCS, AddrMode.REL), OpCode(0xB1, Op.LDA, AddrMode.INDY), \
                OpCode(0xB2, None), OpCode(0xB3, None), \
                OpCode(0xB4, Op.LDY, AddrMode.ZPX), OpCode(0xB5, Op.LDA, AddrMode.ZPX), \
                OpCode(0xB6, Op.LDX, AddrMode.ZPY), OpCode(0xB7, None), \
                OpCode(0xB8, Op.CLV), OpCode(0xB9, Op.LDA, AddrMode.ABSY), \
                OpCode(0xBA, Op.TSX), OpCode(0xBB, None), \
                OpCode(0xBC, Op.LDY, AddrMode.ABSX), OpCode(0xBD, Op.LDA, AddrMode.ABSX), \
                OpCode(0xBE, Op.LDX, AddrMode.ABSY), OpCode(0xBF, None), \
                OpCode(0xC0, Op.CPY, AddrMode.IMM), OpCode(0xC1, Op.CMP, AddrMode.INDX), \
                OpCode(0xC2, None), OpCode(0xC3, None), \
                OpCode(0xC4, Op.CPY, AddrMode.ZP), OpCode(0xC5, Op.CMP, AddrMode.ZP), \
                OpCode(0xC6, Op.DEC, AddrMode.ZP), OpCode(0xC7, None), \
                OpCode(0xC8, Op.INY), OpCode(0xC9, Op.CMP, AddrMode.IMM), \
                OpCode(0xCA, Op.DEX, AddrMode.IMM), OpCode(0xCB, None), \
                OpCode(0xCC, Op.CPY, AddrMode.ABS), OpCode(0xCD, Op.CMP, AddrMode.ABS), \
                OpCode(0xCE, Op.DEC, AddrMode.ABS), OpCode(0xCF, None), \
                OpCode(0xD0, Op.BNE, AddrMode.REL), OpCode(0xD1, Op.CMP, AddrMode.INDY), \
                OpCode(0xD2, None), OpCode(0xD3, None), \
                OpCode(0xD4, None), OpCode(0xD5, Op.CMP, AddrMode.ZPX), \
                OpCode(0xD6, Op.DEC, AddrMode.ZPX), OpCode(0xD7, None), \
                OpCode(0xD8, Op.CLD), OpCode(0xD9, Op.CMP, AddrMode.ABSY), \
                OpCode(0xDA, None), OpCode(0xDB, None), \
                OpCode(0xDC, None), OpCode(0xDD, Op.CMP, AddrMode.ABSX), \
                OpCode(0xDE, Op.DEC, AddrMode.ABSX), OpCode(0xDF, None), \
                OpCode(0xE0, Op.CPX, AddrMode.IMM), OpCode(0xE1, Op.SBC, AddrMode.INDX), \
                OpCode(0xE2, None), OpCode(0xE3, None), \
                OpCode(0xE4, Op.CPX, AddrMode.ZP), OpCode(0xE5, Op.SBC, AddrMode.ZP), \
                OpCode(0xE6, Op.INC, AddrMode.ZP), OpCode(0xE7, None), \
                OpCode(0xE8, Op.INX), OpCode(0xE9, Op.SBC, AddrMode.IMM), \
                OpCode(0xEA, Op.NOP), OpCode(0xEB, None), \
                OpCode(0xEC, Op.CPX, AddrMode.ABS), OpCode(0xED, Op.SBC, AddrMode.ABS), \
                OpCode(0xEE, Op.INC, AddrMode.ABS), OpCode(0xEF, None), \
                OpCode(0xF0, Op.BEQ, AddrMode.REL), OpCode(0xF1, Op.SBC, AddrMode.INDY), \
                OpCode(0xF2, None), OpCode(0xF3, None), \
                OpCode(0xF4, None), OpCode(0xF5, Op.SBC, AddrMode.ZPX), \
                OpCode(0xF6, Op.INC, AddrMode.ZPX), OpCode(0xF7, None), \
                OpCode(0xF8, Op.SED), OpCode(0xF9, Op.SBC, AddrMode.ABSY), \
                OpCode(0xFA, None), OpCode(0xFB, None), \
                OpCode(0xFC, None), OpCode(0xFD, Op.SBC, AddrMode.ABSX), \
                OpCode(0xFE, Op.INC, AddrMode.ABSX), OpCode(0xFF, None)]

