from myhdl import Signal,always,delay,now,Simulation,intbv,instance
from sd_intf import sd_intf
from sdram import sdram

def clkDrive(clk):

    halfPeriod = delay(5)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk

def writeData(sd_intf):

    dqDriver = sd_intf.dq.driver()
    dqDriver.next = None
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

sim = Simulation(clkDriver_inst, sdram_inst, writeData_inst)
sim.run(100)
