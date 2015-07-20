from myhdl import *

class sd_intf(object):

    addr_width = 12
    data_width = 16
    # constant for sdram
    SDRAM_NROWS_C                = 8192       # Number of rows in SDRAM array.
    SDRAM_NCOLS_C                = 512        # Number of columns in SDRAM array.
    SDRAM_DATA_WIDTH_C           = 16         # Host & SDRAM data width.
    SDRAM_HADDR_WIDTH_C          = 24         # Host-side address width.
    SDRAM_SADDR_WIDTH_C          = 13         # SDRAM-side address width.
    SDRAM_T_INIT_C               = 200.0#200000.0   # Min initialization interval (ns).
    SDRAM_T_RAS_C                = 45.0       # Min interval between active to precharge commands (ns).
    SDRAM_T_RCD_C                = 20.0       # Min interval between active and R/W commands (ns).
    SDRAM_T_REF_C                = 640#64000000.0 # Maximum refresh interval (ns).
    SDRAM_T_RFC_C                = 65.0       # Duration of refresh operation (ns).
    SDRAM_T_RP_C                 = 20.0       # Min precharge command duration (ns).
    SDRAM_T_XSR_C                = 75.0       # Exit self-refresh time (ns).

    SDRAM_FREQ_C                 = 1.0#100.0      # Operating frequency in MHz.
    SDRAM_IN_PHASE_C             = True       # SDRAM and controller XESS on same or opposite clock edge.
    SDRAM_PIPE_EN_C              = False      # If true, enable pipelined read operations.
    SDRAM_ENABLE_REFRESH_C       = True       # If true, row refreshes are automatically inserted.
    SDRAM_MULTIPLE_ACTIVE_ROWS_C = False      # If true, allow an active row in each bank.
    SDRAM_MAX_NOP_C              = 10000      # Number of NOPs before entering self-refresh.
    SDRAM_BEG_ADDR_C             = 16         #00_0000#;  -- Beginning SDRAM address.
    SDRAM_END_ADDR_C             = 16         #FF_FFFF#;  -- Ending SDRAM address.

    timing = { # timing details refer data sheet
        'init' : 100,       # min init interval
        'ras'  : 10,        # min interval between active prechargs
        'rcd'  : 10,        # min interval between active R/W
        'cas'  : 20,
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
