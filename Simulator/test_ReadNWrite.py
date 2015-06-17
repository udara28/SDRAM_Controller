from myhdl import *
from Clk import clkDriver



def test_ReadNWrite(sd):
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
    # [WRITE] # cs ras cas we dqm : L H L L X
    sd.cs.next,sd.ras.next,sd.cas.next,sd.we.next = 0,1,0,0
    sd.dq.
    
    yield delay(20)


clk = Signal(bool(0))

clkDriver_Inst = clkDriver(clk)

sim = Simulation(clkDriver_Inst)
sim.run(100)
