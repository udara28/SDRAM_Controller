from myhdl import *

class sd_intf(object):

    addr_width = 12
    data_width = 16

    timing = { # timing details refer data sheet
        'init' : 100000,    # min init interval
        'ras'  : 45,        # min interval between active prechargs
        'rcd'  : 20,        # min interval between active R/W
        'ref'  : 64000000,  # max refresh interval
        'rfc'  : 65,        # refresh opertaion
        'rp'   : 20,        # min precharge
        'xsr'  : 75,        # exit self-refresh time
        'wr'   : 55,        # @todo ...
    }

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
