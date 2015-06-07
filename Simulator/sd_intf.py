from myhdl import *

class sd_intf(object):

    addr_width = 12
    data_width = 16

    def __init__(self,clk):

        self.clk = clk
        self.cke = Signal(bool(0))
        self.cs  = Signal(bool(0))
        self.cas = Signal(bool(0))
        self.ras = Signal(bool(0))
        self.we  = Signal(bool(0))
        self.bs  = Signal(intbv(0)[2:])
        self.addr= Signal(intbv(0)[self.addr_width:])
        self.dqml= Signal(bool(0))
        self.dqmh= Signal(bool(0))
        self.dq  = TristateSignal(intbv(0)[self.data_width:]) 
