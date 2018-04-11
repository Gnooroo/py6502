from common import *

class RAM():
    def __init__(self, size=2*1024, addr_size=4):
        self.size = size
        self.addr_size = addr_size
        self.data = bytearray(size)

    # sould be in caller
    def load_str(self, input_str, offset=0):
        blob = bytearray()
        
        string = input_str.replace(' ', '')
        for s in range(0, len(string), 2):
            i = int('0x' + string[s:s+2], 16)
            blob.append(i)
        
        self.load(blob, offset)
    
    def load(self, blob, offset):
        self.data[offset:len(blob)] = blob

    def __getitem__(self, pos):
        return self.data[pos]

    def __setitem__(self, pos, value):
        self.data[pos] = value
        
    def to_str(self, offset=0, size=0x20, line_size=16, formatted=True):
        out = ''

        if formatted:   
            offset = int(offset / 16) * 16
            out += self.header(line_size) + '\n'
            
        addr = offset
        for a in range(addr, offset+size, line_size):
            if a + line_size > offset + size:
                data_len = line_size - (a + line_size - offset - size)
            else:
                data_len = line_size
                
            out += (self.get_line_str(a, self.data[a:a+data_len], formatted))
            
            if formatted:
                out += '\n'

        return out
            
    def get_addr_str(self, addr):
        return hexStr(addr, self.addr_size) + ':'

    def get_line_str(self, addr, line, show_addr=True):
        line_str = ' '.join(hexStr(x) for x in line)

        if show_addr:           
            return '%s %s' % (self.get_addr_str(addr), line_str)
        else:
            return line_str
    
    def header(self, line_size, show_addr=True):
        line_str = ' '.join(hexStr(i) for i in range(0, line_size))
        
        if show_addr:
            return '%s %s' % (' ' * len(self.get_addr_str(self.size)), line_str)
        else:
            return line_str
