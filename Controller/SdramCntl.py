from myhdl import *
from Simulator import *

def SdramCntl(host_intf, sd_intf, rst_i):
    
    # commands to SDRAM    ce ras cas we dqml dqmh
    NOP_CMD_C     = intbv("011100")[6:]  #0,1,1,1,0,0 
    ACTIVE_CMD_C  = intbv("001100")[6:]  #0,0,1,1,0,0
    READ_CMD_C    = intbv("010100")[6:]  # 0,1,0,1,0,0
    WRITE_CMD_C   = intbv("010000")[6:]  # 0,1,0,0,0,0
    PCHG_CMD_C    = intbv("001000")[6:]  # 0,0,1,0,0,0
    MODE_CMD_C    = intbv("000000")[6:]  # 0,0,0,0,0,0
    RFSH_CMD_C    = intbv("000100")[6:]  # 0,0,0,1,0,0
    
    # mode command for set_mode command
    MODE_C        = intbv("00_0_00_011_0_000")[12:]

    # delay constants
    INIT_CYCLES_C = 10
    RP_CYCLES_C   = 3
    RFC_CYCLES_C  = 3
    MODE_CYCLES_C = 3
    ALL_BANKS_C   = intbv("001000000000")[12:]       # value of CMDBIT to select all banks
    
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
    
    timer_r = Signal(intbv(0)[8:])
    timer_x = Signal(intbv(0)[8:])
    
    # command assignment
    cmd_r   = Signal(NOP_CMD_C)
    cmd_x   = Signal(NOP_CMD_C)
    
    activeRow_r  = Signal(intbv(0)[sd_intf.addr_width:])
    activeRow_x  = Signal(intbv(0)[sd_intf.addr_width:])
    activeBank_r = Signal(intbv(0)[4:]) 
    activeBank_x = Signal(intbv(0)[4:]) # banks with active rows
    doActivate_s = Signal(bool(0))      # request row activation if the read row is not activated
    
    # pin assignment for SDRAM
    @always_comb
    def sdram_pin_map():
        sd_intf.cke.next    = 1
        sd_intf.cs.next     = cmd_r[5]
        sd_intf.ras.next    = cmd_r[4]
        sd_intf.cas.next    = cmd_r[3]
        sd_intf.we.next     = cmd_r[2]
        sd_intf.bs.next     = 0
        sd_intf.dqml.next   = 0
        sd_intf.dqmh.next   = 0
        sd_intf.driver.next = 0
    

    @always_comb
    def comb_func():
        
        
        if timer_r.val != 0 :
            timer_x.next = timer_r.val - 1
        else :
            timer_x.next = timer_r.val
            
            if   state_r.val == CntlStateType.INITWAIT :
                # wait for SDRAM power-on initialization once the clock is stable
                timer_x.next = INIT_CYCLES_C  # set timer for initialization duration
                state_x.next = CntlStateType.INITPCHG
                
            elif state_r.val == CntlStateType.INITPCHG :
                # all banks should be precharged after initialization
                cmd_x.next          = PCHG_CMD_C
                timer_x.next        = RP_CYCLES_C  # set timer for precharge operation duration
                state_x.next        = CntlStateType.INITRFSH
                sd_intf.addr.next   = ALL_BANKS_C  # select all banks precharge   
            
            elif state_r.val == CntlStateType.INITRFSH :
                # refreshing state
                cmd_x.next          = RFSH_CMD_C
                timer_x.next        = RFC_CYCLES_C
                state_x.next        = CntlStateType.INITSETMODE
                
            elif state_r.val == CntlStateType.INITSETMODE
                cmd_x.next          = MODE_CMD_C
                timer_x.next        = MODE_CYCLES_C
                state_x.next        = CntlStateType.RW
                sd_intf.addr.next   = MODE_C
                
            elif state_r.val == CntlStateType.RW
                
                # for now leave row refresh need.. IT SHOULD COME HERE
                if host_intf.rd_i.val == True :
                    
                
              
    @always_seq(sd_intf.clk.posedge, rst_i)
    def seq_func():

        state_r.next = state_x.val
        cmd_r.next   = cmd_x.val
        timer_r.next = timer_x.val
        

    return comb_func, seq_func, sdram_pin_map
