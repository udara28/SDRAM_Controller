from myhdl import *
from Simulator import *

def SdramCntl(
    # Host side
        clk_i,
        rst_i,
        rd_i,
        wr_i,
        addr_i,
        data_i,
        data_o,
        done_o,
        status_o,
        opBegun_o,
    # SDRAM side
        sdCke_o,
        sdCe_bo,
        sdRas_bo,
        sdCas_bo,
        sdWe_bo,
        sdBs_o,
        sdAddr_o,
        sdData_io,
        sdDqmh_o,
        sdDqml_o,
        sd_intf,
    ):
    
    # commands to SDRAM    ce ras cas we dqml dqmh
    NOP_CMD_C     = intbv("01_1100")[6:]  #0,1,1,1,0,0 
    ACTIVE_CMD_C  = intbv("00_1100")[6:]  #0,0,1,1,0,0
    READ_CMD_C    = intbv("01_0100")[6:]  # 0,1,0,1,0,0
    WRITE_CMD_C   = intbv("01_0000")[6:]  # 0,1,0,0,0,0
    PCHG_CMD_C    = intbv("00_1000")[6:]  # 0,0,1,0,0,0
    MODE_CMD_C    = intbv("00_0000")[6:]  # 0,0,0,0,0,0
    RFSH_CMD_C    = intbv("00_0100")[6:]  # 0,0,0,1,0,0
    

    # delay constants
    INIT_CYCLES_C = 4
    RP_CYCLES_C   = 3
    
    # states of the SDRAM controller state machine
    CntlStateType = enum( 
            'INITWAIT',  # initialization - waiting for power-on initialization to complete.
            'INITPCHG',  # initialization - initial precharge of SDRAM banks.
            'INITSETMODE',                        # initialization - set SDRAM mode.
            'INITRFSH',  # initialization - do initial refreshes.
            'RW',                                 # read/write/refresh the SDRAM.
            'ACTIVATE',  # open a row of the SDRAM for reading/writing.
            'REFRESHROW',                         # refresh a row of the SDRAM.
            'SELFREFRESH'   # keep SDRAM in self-refresh mode with CKE low.
        );
    
    # state register and next state
    state_r = Signal(CntlStateType.INITWAIT)
    state_x = Signal(CntlStateType.INITWAIT)
    
    timer_r , timer_x = 0, 0
    
    # command assignment
    cmd_r   = Signal(NOP_CMD_C)
    cmd_x   = Signal(NOP_CMD_C)
    
    # pin assignment for SDRAM
    @always_comb
    def sdram_pin_map():
        sd_intf.clk.next    = clk_i
        sd_intf.cke.next    = 1
        sd_intf.cs.next     = cmd_r[5]
        sd_intf.cas.next    = cmd_r[4]
        sd_intf.ras.next    = cmd_r[3]
        sd_intf.we.next     = cmd_r[2]
        sd_intf.bs.next     = cmd_r[1]
        sd_intf.addr.next   = 0
        sd_intf.dqml.next   = 0
        sd_intf.dqmh.next   = 0
        sd_intf.driver.next = 0
    

    @always_comb
    def comb_func():
        
        
        if timer_r != 0 :
            timer_x = timer_r - 1
        else :
            timer_x = timer_r
            
            if   state_r.val == CntlStateType.INITWAIT :
                # wait for SDRAM power-on initialization once the clock is stable
                timer_x = INIT_CYCLES_C;  # set timer for initialization duration
                state_x.next = CntlStateType.INITPCHG;
                
            elif state_r.val == CntlStateType.INITPCHG :
                # all banks should be precharged after initialization
                cmd_x.next                 = PCHG_CMD_C;
                timer_x               = RP_CYCLES_C;  # set timer for precharge operation duration
              
              
    @always_seq(clk_i.posedge, rst_i)
    def seq_func():

        state_r.next = state_x.val
        cmd_r.next   = cmd_x.val
        timer_r = timer_x
        

    return comb_func, seq_func, sdram_pin_map
