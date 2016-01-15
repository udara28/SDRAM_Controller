from clk_driver import clk_driver
from sdram_cntl import *

clk_i = Signal(bool(0))
rst_i = ResetSignal(0, active=1, async=True)

clkDriver_Inst = clk_driver(clk_i)
sd_intf_Inst = SdramIntf()
host_intf_Inst = HostIntf()

sdramCntl_Inst = sdram_cntl(clk_i, host_intf_Inst, sd_intf_Inst)

toVerilog(sdram_cntl, clk_i, host_intf_Inst, sd_intf_Inst)
toVHDL(sdram_cntl, clk_i, host_intf_Inst, sd_intf_Inst)
