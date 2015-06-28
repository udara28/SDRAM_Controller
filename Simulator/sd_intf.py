from myhdl import *

class sd_intf(object):

    addr_width = 12
    data_width = 16

    timing = { # timing details refer data sheet
        'init' : 100,    # min init interval
        'ras'  : 10,        # min interval between active prechargs
        'rcd'  : 10,        # min interval between active R/W
        'ref'  : 64000000,  # max refresh interval
        'rfc'  : 65,        # refresh opertaion
        'rp'   : 20,        # min precharge
        'xsr'  : 75,        # exit self-refresh time
        'wr'   : 55,        # @todo ...
    }

    def __init__(self,clk):

        self.clk    = clk
        self.cke    = Signal(bool(0))
        self.cs     = Signal(bool(0))
        self.cas    = Signal(bool(0))
        self.ras    = Signal(bool(0))
        self.we     = Signal(bool(0))
        self.bs     = Signal(intbv(0)[2:])
        self.addr   = Signal(intbv(0)[self.addr_width:])
        self.dqml   = Signal(bool(0))
        self.dqmh   = Signal(bool(0))
        self.dq     = TristateSignal(intbv(0)[self.data_width:])
        self.driver = self.dq.driver()
        
    # Written below are transactors for passing commands to sdram
    
    def nop(self):
        # [NOP] cs ras cas we : L H H H
        self.cs.next,self.ras.next,self.cas.next,self.we.next = 0,1,1,1
        yield self.clk.posedge
        
    def activate(self,row_addr,bank_id=0):
        self.bs.next   = bank_id
        self.addr.next = row_addr
        # [ACTIVE] cs ras cas we : L L H H
        self.cs.next,self.ras.next,self.cas.next,self.we.next = 0,0,1,1
        yield self.clk.posedge
        
    def precharge(self,bank_id=None):
        if(bank_id == None):    # precharge all banks
            self.addr.next = 2**10  # A10 is high
        else:
            self.addr.next = 0
            self.bs.next   = bank_id
        # [PRECHARGE] cs ras cas we : L L H L
        self.cs.next,self.ras.next,self.cas.next,self.we.next = 0,0,1,0
        yield self.clk.posedge
        
    def read(self,addr,bank_id=0):
        self.bs.next   = bank_id
        self.addr.next = addr
        # [READ] # cs ras cas we dqm : L H L H X
        self.cs.next,self.ras.next,self.cas.next,self.we.next = 0,1,0,1
        yield self.clk.posedge
        
    def write(self,addr,value,bank_id=0):
        self.bs.next     = bank_id
        self.addr.next   = addr
        self.driver.next = value 
        # [WRITE] # cs ras cas we dqm : L H L L X
        self.cs.next,self.ras.next,self.cas.next,self.we.next = 0,1,0,0
        yield self.clk.posedge
        yield self.clk.posedge
        self.driver.next = None
