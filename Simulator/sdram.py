from myhdl import intbv,always,Signal,TristateSignal

def sdram(sd_intf):

    regFile  = {}     # register file is essentially a map
    dqDriver = sd_intf.dq.driver()    

    @always(sd_intf.clk.posedge)
    def function():
        if(sd_intf.cke == 1):
            if(sd_intf.we == 1):    # memory write operaton
                dqDriver.next = None
                regFile[str(sd_intf.addr.val)] = sd_intf.dq
                #print "i ",(regFile[sd_intf.addr.val])
                print "add: ",str(sd_intf.addr.val)," val: ",str(sd_intf.dq)
            else:
                print str(regFile.get(str(sd_intf.addr.val),0))
                dqDriver.next = regFile.get(str(sd_intf.addr.val),0)

       # print "address:",sd_intf.addr," value : ",regFile[str(sd_intf.addr.val)]
                
    return function
