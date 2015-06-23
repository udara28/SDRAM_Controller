from myhdl import *


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
    ):
    
    # commands to SDRAM    ce ras cas we dqml dqmh
    NOP_CMD_C     = 0,1,1,1,0,0 
    ACTIVE_CMD_C  = 0,0,1,1,0,0
    READ_CMD_C    = 0,1,0,1,0,0
    WRITE_CMD_C   = 0,1,0,0,0,0
    PCHG_CMD_C    = 0,0,1,0,0,0
    MODE_CMD_C    = 0,0,0,0,0,0
    RFSH_CMD_C    = 0,0,0,1,0,0
    

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
    
    state_r , state_x = None,None # state register and next state
    
    timer_r , timer_x = 0, 0

    @always_comb
    def comb_func():
        
        # Applying commands
        sdCe_bo, sdRas_bo, sdCas_bo, sdWe_bo, sdDqmh_o, sdDqml_o, = cmd_r
        
        
        if timer_r != 0 :
            timer_x = timer_r - 1
        else :
            timer_x = timer_r
            
            if   state_r == CntlStateType.INITWAIT :
                # wait for SDRAM power-on initialization once the clock is stable
                timer_x = INIT_CYCLES_C;  # set timer for initialization duration
                state_x = INITPCHG;
                
            elif state_r == CntlStateType.INITPCHG :
                # all banks should be precharged after initialization
                cmd_x                 = PCHG_CMD_C;
                timer_x               = RP_CYCLES_C;  # set timer for precharge operation duration
              
              
    @always_seq(clk_i.posedge, rst_i)
    def seq_func():
        if rst_i == 1 :
            state_r = CntlStateType.INITWAIT;
            timer_r = 0
            cmd_r   = NOP_CMD_C
            
        elif clk_i.posedge == 1 :
            state_r = state_x
            cmd_r   = cmd_x
            timer_r = timer_x
        

    return comb_func, seq_func
