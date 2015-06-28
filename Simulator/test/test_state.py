from myhdl import Signal,always,delay,now,Simulation,intbv,instance
from sd_intf import sd_intf
from sdram import sdram

def clkDrive(clk):

    halfPeriod = delay(5)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk

def stateTest(sd):
    # [ACTIVE] cs ras cas we : L L H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,1
    sd.cke.next = 1
    yield delay(10)
    # [PRECHARGE] cs ras cas we : L L H L
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,0
    yield delay(10)
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
    yield delay(20)
    # [ACTIVE] cs ras cas we : L L H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,1
    yield delay(10)
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1
    yield delay(90)
    # [ACTIVATE] cs ras cas we : L L H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,1
    yield delay(10)  # activating row without precharging should result in an error
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1

clk = Signal(bool(0))
# module instances
clkDriver_inst = clkDrive(clk)
sdram_intf     = sd_intf(clk)
sdram_inst     = sdram(sdram_intf)
stateTest_inst = stateTest(sdram_intf)

sim = Simulation(clkDriver_inst, sdram_inst, stateTest_inst)
sim.run(200)
