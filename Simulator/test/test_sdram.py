from myhdl import *
from Simulator import *

def test_readWrite(sd_intf):
    
    @instance
    def test():
        yield delay(120)
        sd_intf.cke.next = 1
        yield sd_intf.nop()
        yield sd_intf.activate(17)
        yield sd_intf.nop()
        yield delay(30)
        yield sd_intf.write(20,31)
        yield sd_intf.nop()
        yield delay(30)
        yield sd_intf.read(20)
        yield sd_intf.nop()
        yield delay(20)
        for i in range(20):
            print sd_intf.dq.val
            yield delay(10)
        print "hello world"
        
    return test

clk = Signal(bool(0))

clkDriver_Inst      = clkDriver(clk)
sd_intf_Inst        = sd_intf(clk)
sdram_Inst          = sdram(sd_intf_Inst)
test_readWrite_Inst = test_readWrite(sd_intf_Inst)

sim = Simulation(clkDriver_Inst,sdram_Inst,test_readWrite_Inst)
sim.run(250)
