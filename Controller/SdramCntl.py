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
        done_o
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

    # states of the SDRAM controller state machine
    CntlStateType = (
            INITWAIT,  # initialization - waiting for power-on initialization to complete.
            INITPCHG,  # initialization - initial precharge of SDRAM banks.
            INITSETMODE,                        # initialization - set SDRAM mode.
            INITRFSH,  # initialization - do initial refreshes.
            RW,                                 -- read/write/refresh the SDRAM.
            ACTIVATE,  # open a row of the SDRAM for reading/writing.
            REFRESHROW,                         -- refresh a row of the SDRAM.
            SELFREFRESH   # keep SDRAM in self-refresh mode with CKE low.
        );
    
    state_r , state_x = None,None # state register and next state
    
    

    @always_comb
    def test():
        clk_i = a & b

    return test

a  = Signal(bool(0))
b  = Signal(bool(0))

c  = Signal(bool(0))

sdram_Inst = SdramCntl(c,a,b)

sim = Simulation(sdram_Inst)
sim.run(20)
