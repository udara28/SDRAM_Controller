from myhdl import *
from Simulator import *
from SdramCntl import *

# Host side signals
clk_i     = Signal(bool(0))
rst_i     = ResetSignal(0, active=0, async=True)
rd_i      = Signal(bool(0))
wr_i      = Signal(bool(0))
addr_i    = Signal(bool(0))
data_i    = Signal(bool(0))
data_o    = Signal(bool(0))
done_o    = Signal(bool(0))
status_o  = Signal(bool(0))
opBegun_o = Signal(bool(0))

clkDriver_Inst      = clkDriver(clk_i)
sd_intf_Inst        = sd_intf(clk_i)

# SDRAM side
sdCke_o   = sd_intf_Inst.cke 
sdCe_bo   = sd_intf_Inst.cs
sdRas_bo  = sd_intf_Inst.ras 
sdCas_bo  = sd_intf_Inst.cas
sdWe_bo   = sd_intf_Inst.we
sdBs_o    = sd_intf_Inst.bs
sdAddr_o  = sd_intf_Inst.addr
sdData_io = sd_intf_Inst.dq
sdDqmh_o  = sd_intf_Inst.dqmh
sdDqml_o  = sd_intf_Inst.dqml

sdram_Inst = sdram(sd_intf_Inst)
sdramCntl_Inst = SdramCntl(clk_i,rst_i,rd_i,wr_i,addr_i,data_i,data_o,done_o,status_o,opBegun_o,
                        sdCke_o,sdCe_bo,sdRas_bo,sdCas_bo,sdWe_bo,sdBs_o,sdAddr_o,sdData_io,sdDqmh_o,sdDqml_o,sd_intf_Inst)

sim = Simulation(clkDriver_Inst,sdram_Inst,sdramCntl_Inst)
sim.run(250)
