from myhdl import intbv,always,Signal

def sdram(cke,clk,cs,we,cas,ras,addr,ba,dqml,dqmh,dq):

    regFile = [intbv(15,min=0,max=255)] * 5

    @always(clk.posedge)
    def function():
        if(cke == 1):
            if(we == 1):    # memory write operaton
                regFile[addr.val] = dq.val
                print "i : %d" %(regFile[addr.val])
            else:
                dq.next = regFile[addr.val]

        print "address: %d value: %d" % (addr,regFile[addr.val])
                
    return function
