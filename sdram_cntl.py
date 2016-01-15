from math import ceil
from sd_intf import *
from host_intf import *


def sdram_cntl(clk_i, host_intf, sd_intf):

    # commands to SDRAM    ce ras cas we dqml dqmh
    nop_cmd_c = int(sd_intf.SDRAM_NOP_CMD_C)        # intbv("011100")[6:]  #0,1,1,1,0,0
    active_cmd_c = int(sd_intf.SDRAM_ACTIVE_CMD_C)  # intbv("001100")[6:]  #0,0,1,1,0,0
    read_cmd_c = int(sd_intf.SDRAM_READ_CMD_C)      # intbv("010100")[6:]  # 0,1,0,1,0,0
    write_cmd_c = int(sd_intf.SDRAM_WRITE_CMD_C)    # intbv("010000")[6:]  # 0,1,0,0,0,0
    pchg_cmd_c = int(sd_intf.SDRAM_PCHG_CMD_C)      # intbv("001000")[6:]  # 0,0,1,0,0,0
    mode_cmd_c = int(sd_intf.SDRAM_MODE_CMD_C)      # intbv("000000")[6:]  # 0,0,0,0,0,0
    rfsh_cmd_c = int(sd_intf.SDRAM_RFSH_CMD_C)      # intbv("000100")[6:]  # 0,0,0,1,0,0
    mode_c = int(sd_intf.SDRAM_MODE_C)              # intbv("00_0_00_011_0_000")[12:] mode command for set_mode command

    # generic parameters
    freq_ghz_g = sd_intf.SDRAM_FREQ_C / 1000
    # ENABLE_REFRESH_G = True
    nrows_g = sd_intf.SDRAM_NROWS_C
    t_ref_g = sd_intf.SDRAM_T_REF_C
    t_init_g = sd_intf.SDRAM_T_INIT_C   # min initialization interval (ns).
    t_ras_g = sd_intf.SDRAM_T_RAS_C     # min interval between active to precharge commands (ns).
    t_rcd_g = sd_intf.SDRAM_T_RCD_C     # min interval between active and R/W commands (ns).
    t_ref_g = sd_intf.SDRAM_T_REF_C     # maximum refresh interval (ns).
    t_rfc_g = sd_intf.SDRAM_T_RFC_C     # duration of refresh operation (ns).
    t_rp_g = sd_intf.SDRAM_T_RP_C       # min precharge command duration (ns).
    t_xsr_g = sd_intf.SDRAM_T_XSR_C     # exit self-refresh time (ns).

    # delay constants
    init_cycles_c = int(ceil(t_init_g * freq_ghz_g))
    rp_cycles_c = int(ceil(t_rp_g * freq_ghz_g))
    rfc_cycles_c = int(ceil(t_rfc_g * freq_ghz_g))
    ref_cycles_c = int(ceil(t_ref_g * freq_ghz_g / nrows_g))
    rcd_cycles_c = int(ceil(t_rcd_g * freq_ghz_g))
    ras_cycles_c = int(ceil(t_ras_g * freq_ghz_g))
    mode_cycles_c = 2
    cas_cycles_c = 3
    wr_cycles_c = 2
    rfsh_ops_c = 8                            # number of refresh operations needed to init SDRAM.

    # constant values
    all_banks_c = int(sd_intf.SDRAM_ALL_BANKS_C)       # value of CMDBIT to select all banks
    one_bank_c = int(sd_intf.SDRAM_ONE_BANK_C)
    input_c = bool(0)                                # sDataDir_r bit 0 for INPUT
    output_c = bool(1)                                # sDataDir_r bit 1 for OUTPUT
    nop_c = bool(0)
    read_c = bool(1)
    write_c = bool(1)
    ba_len_c = 2
    col_len_c = int(log(sd_intf.SDRAM_NCOLS_C, 2))
    row_len_c = int(log(sd_intf.SDRAM_NROWS_C, 2))

    # states of the SDRAM controller state machine
    cntlstatetype = enum(
        'INITWAIT',         # initialization - waiting for power-on initialization to complete.
        'INITPCHG',         # initialization - initial precharge of SDRAM banks.
        'INITSETMODE',      # initialization - set SDRAM mode.
        'INITRFSH',         # initialization - do initial refreshes.
        'RW',               # read/write/refresh the SDRAM.
        'ACTIVATE',         # open a row of the SDRAM for reading/writing.
        'REFRESHROW',       # refresh a row of the SDRAM.
        'SELFREFRESH'       # keep SDRAM in self-refresh mode with CKE low.
        )

    # state register and next state
    state_r = Signal(cntlstatetype.INITWAIT)
    state_x = Signal(cntlstatetype.INITWAIT)

    # timer registers
    timer_r = Signal(intbv(0, min=0, max=init_cycles_c+1))                          # current sdram opt time
    timer_x = Signal(intbv(0, min=0, max=init_cycles_c+1))

    reftimer_r = Signal(intbv(ref_cycles_c, min=0, max=ref_cycles_c+1))    # time between row refreshes
    reftimer_x = Signal(intbv(ref_cycles_c, min=0, max=ref_cycles_c+1))

    rastimer_r = Signal(intbv(0, min=0, max=ras_cycles_c+1))    # active to precharge time
    rastimer_x = Signal(intbv(0, min=0, max=ras_cycles_c+1))

    wrtimer_r = Signal(intbv(0, min=0, max=wr_cycles_c+1))     # write to precharge time
    wrtimer_x = Signal(intbv(0, min=0, max=wr_cycles_c+1))

    rfshcntr_r = Signal(intbv(0, min=0, max=nrows_g+1))         # count refreshes that are needed
    rfshcntr_x = Signal(intbv(0, min=0, max=nrows_g+1))

    # status signals
    activate_in_progress_s = Signal(bool(0))
    rd_in_progress_s = Signal(bool(0))
    wr_in_progress_s = Signal(bool(0))

    # command assignment
    cmd_r = Signal(intbv(nop_cmd_c)[3:0])   # this should be [6:] last two digits and first digit removed because zero
    cmd_x = Signal(intbv(nop_cmd_c)[3:0])

    saddr_r = Signal(intbv(0)[row_len_c:])  # ideally this should be sd_intf.addr_width but we dont use upper two bits
    saddr_x = Signal(intbv(0)[row_len_c:])

    sdata_r = Signal(intbv(0)[sd_intf.data_width:])
    sdata_x = Signal(intbv(0)[sd_intf.data_width:])

    sdriver = sd_intf.dq.driver()

    sdramdata_r = Signal(intbv(0)[sd_intf.data_width:])
    sdramdata_x = Signal(intbv(0)[sd_intf.data_width:])

    sdatadir_r = Signal(input_c)
    sdatadir_x = Signal(input_c)

    activerow_r = [Signal(intbv(0)[row_len_c:]) for _ in range(2**ba_len_c)]   # each bank will have a active row
    activerow_x = [Signal(intbv(0)[row_len_c:]) for _ in range(2**ba_len_c)]
    activeflag_r = [Signal(bool(0)) for _ in range(2**ba_len_c)]
    activeflag_x = [Signal(bool(0)) for _ in range(2**ba_len_c)]
    activebank_r = Signal(intbv(0)[2:])
    activebank_x = Signal(intbv(0)[2:])  # banks with active rows
    doactivate_s = Signal(bool(0))       # request row activation if a new row is needed to activate

    rdpipeline_r = Signal(intbv(0)[cas_cycles_c+2:])
    rdpipeline_x = Signal(intbv(0)[cas_cycles_c+2:])

    wrpipeline_r = Signal(intbv(0)[cas_cycles_c+2:])
    wrpipeline_x = Signal(intbv(0)[cas_cycles_c+2:])

    ba_r = Signal(intbv(0)[ba_len_c:])
    ba_x = Signal(intbv(0)[ba_len_c:])

    bank_s = Signal(intbv(0)[ba_len_c:])
    row_s = Signal(intbv(0)[row_len_c:])
    col_s = Signal(intbv(0)[col_len_c:])

    # pin assignment for SDRAM
    @always_comb
    def sdram_pin_map():
        sd_intf.cke.next = 1
        sd_intf.cs.next = 0  # cmd_r[3]
        sd_intf.ras.next = cmd_r[2]
        sd_intf.cas.next = cmd_r[1]
        sd_intf.we.next = cmd_r[0]
        sd_intf.bs.next = bank_s
        sd_intf.addr.next = saddr_r
        # sd_intf.driver.next = sData_r if sDataDir_r == OUTPUT_C else None
        if sdatadir_r == output_c:
            sdriver.next = sdata_r
        else:
            sdriver.next = None
        sd_intf.dqml.next = 0
        sd_intf.dqmh.next = 0

    # pin assignment for HOST SIDE
    @always_comb
    def host_pin_map():
        host_intf.done_o.next = rdpipeline_r[0] or wrpipeline_r[0]
        host_intf.data_o.next = sdramdata_r
        host_intf.rdPending_o.next = rd_in_progress_s
        sdata_x.next = host_intf.data_i

    # extract bank, row and column from controller address
    @always_comb
    def extract_addr():
        # extract bank
        # Multiple active rows logic has been removed for now
        bank_s.next = host_intf.addr_i[ba_len_c+row_len_c+col_len_c:row_len_c+col_len_c]
        ba_x.next = host_intf.addr_i[ba_len_c+row_len_c+col_len_c:row_len_c+col_len_c]

        # extract row
        row_s.next = host_intf.addr_i[row_len_c+col_len_c:col_len_c]
        # extract column
        col_s.next = host_intf.addr_i[col_len_c:]

    @always_comb
    def do_active():
        if bank_s != activebank_r or row_s != activerow_r[bank_s.val] or not activeflag_r[bank_s.val]:
            doactivate_s.next = True
        else:
            doactivate_s.next = False

        if rdpipeline_r[1] == read_c:
            sdramdata_x.next = sd_intf.dq
        else:
            sdramdata_x.next = sdramdata_r

        # update status signals
        # activateInProgress_s.next = True    if rasTimer_r != 0 else False
        if rastimer_r != 0:
            activate_in_progress_s.next = True
        else:
            activate_in_progress_s.next = False

        # writeInProgress_s.next    = True    if wrTimer_r  != 0 else False
        if wrtimer_r != 0:
            wr_in_progress_s.next = True
        else:
            wr_in_progress_s.next = False

        # rdInProgress_s.next       = True    if rdPipeline_r[CAS_CYCLES_C+2:1] != 0 else False
        if rdpipeline_r[cas_cycles_c+2:1] != 0:
            rd_in_progress_s.next = True
        else:
            rd_in_progress_s.next = False

    @always_comb
    def comb_func():

        rdpipeline_x.next = concat(nop_c, rdpipeline_r[cas_cycles_c+2:1])
        wrpipeline_x.next = intbv(nop_c)[cas_cycles_c+2:]

        # #################### Update the timers ###########################

        # row activation timer
        # rasTimer_x.next = rasTimer_r - 1 if rasTimer_r != 0 else rasTimer_r
        if rastimer_r != 0:
            rastimer_x.next = rastimer_r - 1
        else:
            rastimer_x.next = rastimer_r

        # write operation timer
        # wrTimer_x.next  = wrTimer_r - 1  if wrTimer_r != 0 else wrTimer_r
        if wrtimer_r != 0:
            wrtimer_x.next = wrtimer_r - 1
        else:
            wrtimer_x.next = wrtimer_r

        # refresh timer
        # refTimer_x.next = refTimer_r - 1 if refTimer_r != 0 else REF_CYCLES_C
        if reftimer_r != 0:
            reftimer_x.next = reftimer_r - 1
            rfshcntr_x.next = rfshcntr_r
        else:
            reftimer_x.next = ref_cycles_c
        # if refTimer_r == 0:
            # on timeout, reload the timer with the interval between row refreshes
            # and increment the counter for the number of row refreshes that are needed
            # rfshCntr_x.next = rfshCntr_r + 1 if ENABLE_REFRESH_G else 0
            rfshcntr_x.next = rfshcntr_r + 1

        ######################################################################

        # ################## code to remove latches ###########################
        cmd_x.next = cmd_r
        state_x.next = state_r
        saddr_x.next = saddr_r
        activebank_x.next = activebank_r
        sdatadir_x.next = sdatadir_r
        for index in range(2**ba_len_c):
            activeflag_x[index].next = activeflag_r[index]
            activerow_x[index].next = activerow_r[index]
        ######################################################################

        if timer_r != 0:
            timer_x.next = timer_r - 1
            cmd_x.next = nop_cmd_c
        else:
            timer_x.next = timer_r

            if state_r == cntlstatetype.INITWAIT:
                # wait for SDRAM power-on initialization once the clock is stable
                timer_x.next = init_cycles_c  # set timer for initialization duration
                state_x.next = cntlstatetype.INITPCHG

            elif state_r == cntlstatetype.INITPCHG:
                # all banks should be precharged after initialization
                cmd_x.next = pchg_cmd_c
                timer_x.next = rp_cycles_c  # set timer for precharge operation duration
                state_x.next = cntlstatetype.INITRFSH
                saddr_x.next = all_banks_c  # select all banks precharge
                rfshcntr_x.next = rfsh_ops_c
                # ## tempory line should be change #####
                # state_x.next = CntlStateType.RW
                # ######################################

            elif state_r == cntlstatetype.INITRFSH:
                # refreshing state
                cmd_x.next = rfsh_cmd_c
                timer_x.next = rfc_cycles_c
                rfshcntr_x.next = rfshcntr_r - 1
                if rfshcntr_r == 1:
                    state_x.next = cntlstatetype.INITSETMODE

            elif state_r == cntlstatetype.INITSETMODE:
                cmd_x.next = mode_cmd_c
                timer_x.next = mode_cycles_c
                state_x.next = cntlstatetype.RW
                saddr_x.next = mode_c

            elif state_r == cntlstatetype.RW:

                if rfshcntr_r != 0:
                    # wait for any activation, read or write before precharge
                    if not activate_in_progress_s and not wr_in_progress_s and not rd_in_progress_s:
                        cmd_x.next = pchg_cmd_c
                        timer_x.next = rp_cycles_c
                        state_x.next = cntlstatetype.REFRESHROW
                        saddr_x.next = all_banks_c
                        for index in range(2**ba_len_c):
                            activeflag_x[index].next = False

                # for now leave row refresh need.. IT SHOULD COME HERE
                elif host_intf.rd_i:
                    if ba_x == ba_r:
                        if doactivate_s:   # A new row need to be activated. PRECHARGE The bank
                            # activate new row only if all previous activations, writes, reads are done
                            if not activate_in_progress_s and not wr_in_progress_s and not rd_in_progress_s:
                                cmd_x.next = pchg_cmd_c
                                timer_x.next = rp_cycles_c
                                state_x.next = cntlstatetype.ACTIVATE
                                saddr_x.next = one_bank_c
                                activeflag_x[bank_s].next = False
                        elif not rd_in_progress_s:
                            cmd_x.next = read_cmd_c
                            sdatadir_x.next = input_c
                            saddr_x.next = col_s
                            rdpipeline_x.next = concat(read_c, rdpipeline_r[cas_cycles_c+2:1])

                elif host_intf.wr_i:
                    if ba_x == ba_r:
                        if doactivate_s:
                            # activate new row only if all previous activations, writes, reads are done
                            if not activate_in_progress_s and not wr_in_progress_s and not rd_in_progress_s:
                                cmd_x.next = pchg_cmd_c
                                timer_x.next = rp_cycles_c
                                state_x.next = cntlstatetype.ACTIVATE
                                saddr_x.next = one_bank_c
                                activeflag_x[bank_s].next = False

                        elif not rd_in_progress_s:
                            cmd_x.next = write_cmd_c
                            sdatadir_x.next = output_c
                            saddr_x.next = col_s
                            wrpipeline_x.next = intbv(1)[cas_cycles_c+2:]
                            wrtimer_x.next = wr_cycles_c

                else:
                    cmd_x.next = nop_cmd_c
                    state_x.next = cntlstatetype.RW

            elif state_r == cntlstatetype.ACTIVATE:
                cmd_x.next = active_cmd_c
                timer_x.next = rcd_cycles_c
                state_x.next = cntlstatetype.RW
                rastimer_x.next = ras_cycles_c
                saddr_x.next = row_s
                activebank_x.next = bank_s
                activerow_x[bank_s].next = row_s
                activeflag_x[bank_s].next = True

            elif state_r == cntlstatetype.REFRESHROW:
                cmd_x.next = rfsh_cmd_c
                timer_x.next = rfc_cycles_c
                state_x.next = cntlstatetype.RW
                rfshcntr_x.next = rfshcntr_r - 1

            else:
                state_x.next = cntlstatetype.INITWAIT

    @always_seq(clk_i.posedge, host_intf.rst_i)
    def seq_func():

        state_r.next = state_x
        cmd_r.next = cmd_x

        saddr_r.next = saddr_x
        sdata_r.next = sdata_x
        sdatadir_r.next = sdatadir_x
        activebank_r.next = activebank_x
        sdramdata_r.next = sdramdata_x
        wrpipeline_r.next = wrpipeline_x
        rdpipeline_r.next = rdpipeline_x
        ba_r.next = ba_x
        # timers
        timer_r.next = timer_x
        rastimer_r.next = rastimer_x
        reftimer_r.next = reftimer_x
        wrtimer_r.next = wrtimer_x
        rfshcntr_r.next = rfshcntr_x
        for index in range(2**ba_len_c):
            activerow_r[index].next = activerow_x[index]
            activeflag_r[index].next = activeflag_x[index]

    return comb_func, seq_func, sdram_pin_map, host_pin_map, extract_addr, do_active
