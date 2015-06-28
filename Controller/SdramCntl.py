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
    RCD_CYCLES_C  = 3
    CAS_CYCLES_C  = 3
    
    # constant values
    ALL_BANKS_C   = intbv("001000000000")[12:]       # value of CMDBIT to select all banks
    ONE_BANK_C    = intbv("000000000000")[12:]
    INPUT_C       = bool(0)                                # sDataDir_r bit 0 for INPUT
    OUTPUT_C      = bool(1)                                # sDataDir_r bit 1 for OUTPUT
    NOP_C         = bool(0)
    READ_C        = bool(1)
    WRITE_C       = bool(1)
    BA_LEN_C      = 2
    COL_LEN_C     = 10
    ROW_LEN_C     = 10
    
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
    
    sAddr_r = Signal(intbv(0)[sd_intf.addr_width:])
    sAddr_x = Signal(intbv(0)[sd_intf.addr_width:])
    
    sData_r = Signal(intbv(0)[sd_intf.data_width:])
    sData_x = Signal(intbv(0)[sd_intf.data_width:])
    
    sdramData_r  = Signal(intbv(0)[sd_intf.data_width:])
    sdramData_x  = Signal(intbv(0)[sd_intf.data_width:])
    
    sDataDir_r   = Signal(INPUT_C)
    sDataDir_x   = Signal(INPUT_C)
    
    activeRow_r  = [ Signal(intbv(0)[sd_intf.addr_width:]) ] * (2**BA_LEN_C) # each bank will have a active row
    activeRow_x  = [ Signal(intbv(0)[sd_intf.addr_width:]) ] * (2**BA_LEN_C) 
    activeFlag_r = [ Signal(bool(0)) ] * (2**BA_LEN_C)
    activeFlag_x = [ Signal(bool(0)) ] * (2**BA_LEN_C)
    activeBank_r = Signal(intbv(0)[4:]) 
    activeBank_x = Signal(intbv(0)[4:]) # banks with active rows
    doActivate_s = Signal(bool(0))      # request row activation if a new row is needed to activate
    
    rdPipeline_r = Signal(intbv(0)[CAS_CYCLES_C+2:])
    rdPipeline_x = Signal(intbv(0)[CAS_CYCLES_C+2:])
    
    wrPipeline_r = Signal(intbv(0)[CAS_CYCLES_C+2:])
    wrPipeline_x = Signal(intbv(0)[CAS_CYCLES_C+2:])
    
    bank_s = Signal(intbv(0)[BA_LEN_C:])
    row_s  = Signal(intbv(0)[ROW_LEN_C:])
    col_s  = Signal(intbv(0)[COL_LEN_C:])
    
    # pin assignment for SDRAM
    @always_comb
    def sdram_pin_map():
        sd_intf.cke.next    = 1
        sd_intf.cs.next     = cmd_r[5]
        sd_intf.ras.next    = cmd_r[4]
        sd_intf.cas.next    = cmd_r[3]
        sd_intf.we.next     = cmd_r[2]
        sd_intf.bs.next     = bank_s.val
        sd_intf.addr.next   = sAddr_r.val
        if sDataDir_r == OUTPUT_C :
            sd_intf.driver.next = sData_r.val
        else :
            sd_intf.driver.next = None
        sd_intf.dqml.next   = 0
        sd_intf.dqmh.next   = 0
        
    # pin assignment for HOST SIDE
    @always_comb
    def host_pin_map():
        host_intf.done_o.next = rdPipeline_r.val[0] or wrPipeline_r.val[0]
        host_intf.data_o.next = sdramData_r.val
        sData_x.next          = host_intf.data_i.val

    # extract bank, row and column from controller address
    @always_comb
    def extract_addr():
        # extract bank
        bank_s.next = host_intf.addr_i.val[BA_LEN_C+ROW_LEN_C+COL_LEN_C:ROW_LEN_C+COL_LEN_C]
        # extract row
        row_s.next  = host_intf.addr_i.val[ROW_LEN_C+COL_LEN_C:COL_LEN_C]
        # extract column
        col_s.next  = host_intf.addr_i.val[COL_LEN_C:]
        
        
        
    @always_comb
    def do_active():
        if bank_s.val != activeBank_r.val or row_s.val != activeRow_r[bank_s.val].val or activeFlag_r[bank_s.val].val == False :
            doActivate_s.next = True
        else :
            doActivate_s.next = False
            
        rdPipeline_x.next = concat(NOP_C,rdPipeline_r.val[CAS_CYCLES_C+2:1])
        wrPipeline_x.next = intbv(NOP_C)[len(wrPipeline_x):]
        
        if rdPipeline_r.val[1] == READ_C :
            sdramData_x.next = sd_intf.dq.val
        else :
            sdramData_x.next = sdramData_r.val
    
    @always_comb
    def comb_func():
        
        if timer_r.val != 0 :
            timer_x.next = timer_r.val - 1
            cmd_x.next   = NOP_CMD_C
        else :
            timer_x.next = timer_r.val
            
            if   state_r.val == CntlStateType.INITWAIT :
                # wait for SDRAM power-on initialization once the clock is stable
                timer_x.next = INIT_CYCLES_C  # set timer for initialization duration
                state_x.next = CntlStateType.INITPCHG
                
            elif state_r.val == CntlStateType.INITPCHG :
                # all banks should be precharged after initialization
                cmd_x.next   = PCHG_CMD_C
                timer_x.next = RP_CYCLES_C  # set timer for precharge operation duration
              #  state_x.next        = CntlStateType.INITRFSH
              
              ### tempory line should be change #####
                state_x.next = CntlStateType.RW
              #######################################
                sAddr_x.next = ALL_BANKS_C  # select all banks precharge   
            
            elif state_r.val == CntlStateType.INITRFSH :
                # refreshing state
                cmd_x.next   = RFSH_CMD_C
                timer_x.next = RFC_CYCLES_C
                state_x.next = CntlStateType.INITSETMODE
                
            elif state_r.val == CntlStateType.INITSETMODE :
                cmd_x.next   = MODE_CMD_C
                timer_x.next = MODE_CYCLES_C
                state_x.next = CntlStateType.RW
                sAddr_x.next = MODE_C
                
            elif state_r.val == CntlStateType.RW :
                
                # for now leave row refresh need.. IT SHOULD COME HERE
                if host_intf.rd_i.val == True :
                    
                    if doActivate_s.val == True :   # A new row need to be activated. PRECHARGE The bank
                        print "new row should be activated before read"
                    else :
                        cmd_x.next        = READ_CMD_C
                        sDataDir_x.next   = INPUT_C
                        sAddr_x.next      = col_s.val
                        rdPipeline_x.next = concat(READ_C,rdPipeline_r.val[CAS_CYCLES_C+2:1])
                        
                elif host_intf.wr_i.val == True :
                
                    if doActivate_s.val == True :
                        cmd_x.next                    = PCHG_CMD_C
                        timer_x.next                  = RP_CYCLES_C
                        state_x.next                  = CntlStateType.ACTIVATE
                        sAddr_x.next                  = ONE_BANK_C
                        activeFlag_x[bank_s.val].next = False
                        
                    else :
                        cmd_x.next        = WRITE_CMD_C
                        sDataDir_x.next   = OUTPUT_C
                        sAddr_x.next      = col_s.val
                        wrPipeline_x.next = intbv(1)[len(wrPipeline_x):]
                
                else :
                    cmd_x.next = NOP_CMD_C
                        
                        
                    
            elif state_r.val == CntlStateType.ACTIVATE :
                cmd_x.next                    = ACTIVE_CMD_C
                timer_x.next                  = RCD_CYCLES_C
                state_x.next                  = CntlStateType.RW    
                sAddr_x.next                  = row_s.val
                activeBank_x.next             = bank_s.val
                activeRow_x[bank_s.val].next  = row_s.val
                activeFlag_x[bank_s.val].next = True
              
            else :
                state_x.next    = CntlStateType.INITWAIT

    @always_seq(sd_intf.clk.posedge, rst_i)
    def seq_func():

        state_r.next      = state_x.val
        cmd_r.next        = cmd_x.val
        timer_r.next      = timer_x.val
        sAddr_r.next      = sAddr_x.val
        sData_r.next      = sData_x.val
        sDataDir_r.next   = sDataDir_x.val
        activeBank_r.next = activeBank_x.val
        sdramData_r.next  = sdramData_x.val
        wrPipeline_r.next = wrPipeline_x.val
        rdPipeline_r.next = rdPipeline_x.val
        for index in range(2**BA_LEN_C) :
            activeRow_r[index].next  = activeRow_x[index].val
            activeFlag_r[index].next = activeFlag_x[index].val
        

    return comb_func, seq_func, sdram_pin_map, host_pin_map, extract_addr, do_active
