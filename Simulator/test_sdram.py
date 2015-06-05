from myhdl import Signal,always,delay,now,Simulation,intbv,instance
from sdram import sdram

def clkDrive(clk):

    halfPeriod = delay(5)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk

def writeData(addr,dq,we):

    yield delay(10)
    addr.next = 2
    dq.next = 123
    we.next = 1
    yield delay(10)
    we.next = 0
    dq.next = 0
    
    yield delay(20)
    addr.next = 1
    yield delay(20)
    addr.next = 2
    yield delay(20)
    addr.next = 3


clk = Signal(0)
cke = Signal(1)
cs  = Signal(1)
we  = Signal(0)
cas = Signal(0)
ras = Signal(0)
addr= Signal(intbv(2,min=0,max=5))
ba  = Signal(intbv(0,min=0,max=4))
dqml= Signal(0)
dqmh= Signal(0)
dq  = Signal(intbv(0,min=0,max=255))

# module instances
clkDriver_inst = clkDrive(clk)
sdram_inst     = sdram(cke,clk,cs,we,cas,ras,addr,ba,dqml,dqmh,dq)
writeData_inst = writeData(addr,dq,we)

sim = Simulation(clkDriver_inst, sdram_inst, writeData_inst)
sim.run(100)
