from myhdl import *
from Simulator import *
from SdramCntl import *
from host_intf import host_intf

clk_i = Signal(bool(0))
rst_i = ResetSignal(0,active=1,async=True)

clkDriver_Inst      = clkDriver(clk_i)
sd_intf_Inst        = sd_intf()
host_intf_Inst      = host_intf()

sdramCntl_Inst = SdramCntl(clk_i,host_intf_Inst,sd_intf_Inst)

toVerilog(SdramCntl,clk_i,host_intf_Inst,sd_intf_Inst)
toVHDL(SdramCntl,clk_i,host_intf_Inst,sd_intf_Inst)
