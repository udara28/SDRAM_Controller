from myhdl import *

class host_intf(object):
    
    def __init__(self,clk):
        # Host side signals
        self.clk_i     = clk
        self.rst_i     = ResetSignal(0, active=0, async=True)
        self.rd_i      = Signal(bool(0))
        self.wr_i      = Signal(bool(0))
        self.addr_i    = Signal(intbv(0)[12:])
        self.data_i    = Signal(intbv(0)[16:])
        self.data_o    = Signal(intbv(0)[16:])
        self.done_o    = Signal(bool(0))
        self.status_o  = Signal(bool(0))
        
    def read(self,addr):
        self.addr_i.next = addr
        self.rd_i.next   = 1
        yield delay(10)
        self.rd_i.next   = 0
        
    def write(self,addr,data):
        self.addr_i.next = addr
        self.data_i.next = data
        yield delay(5)
        self.wr_i.next   = 1
        
    def nop(self):
        self.rd_i.next = 0
        self.wr_i.next = 0
