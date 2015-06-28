from myhdl import Signal,always,delay,now,Simulation,intbv,instance
from sd_intf import sd_intf
from sdram import sdram

def clkDrive(clk):

    halfPeriod = delay(5)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk

def activateTest(sd):
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
    yield delay(10)
    # [ACTIVATE] cs ras cas we : L L H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,0,1,1
    yield delay(10)  # activating row without precharging should result in an error
    # [NOP] cs ras cas we : L H H H
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,1,1

def writeData(sd_intf):

    dqDriver = sd_intf.dq.driver()
    dqDriver.next = None

    # Activate command : cs ras cas we : L L H H
    sd_intf.cs.next,sd_intf.ras.next,sd_intf.cas.next,sd_intf.we.next = 0,0,1,1
    sd_intf.cke.next = 1
    yield delay(10)

    sd_intf.addr.next = 2
    sd_intf.we.next = 1
    yield delay(5)
    dqDriver.next = 123
    yield delay(10)
    sd_intf.we.next = 0
    dqDriver.next = None
    
    yield delay(20)
    sd_intf.addr.next = 1
    yield delay(20)
    sd_intf.addr.next = 2
    yield delay(20)
    sd_intf.addr.next = 3

clk = Signal(bool(0))
# module instances
clkDriver_inst = clkDrive(clk)
sdram_intf     = sd_intf(clk)
sdram_inst     = sdram(sdram_intf)
writeData_inst = writeData(sdram_intf)
activateTest_inst = activateTest(sdram_intf)

sim = Simulation(clkDriver_inst, sdram_inst, activateTest_inst)
sim.run(100)
