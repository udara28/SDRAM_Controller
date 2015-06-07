from myhdl import *


commands = enum("COM_INHIBIT","NOP","ACTIVE","READ","WRITE","BURST_TERM", \
                    "PRECHARGE","AUTO_REFRESH","LOAD_MODE","OUTPUT_EN","OUTPUT_Z","INVALID")

def sdram(sd_intf):

    regFile  = {}                     # register file for holding the values
    data = sd_intf.dq.driver()        # driver for bidirectional DQ port

    curr_command = Signal(commands.INVALID)

    control_logic_inst = Control_Logic(curr_command,sd_intf)

    @always(sd_intf.clk.posedge)
    def function():
        if(sd_intf.cke == 1):

            if(curr_command != commands.INVALID):
                print " SDRAM : [COMMAND] " , curr_command.val   
            if(curr_command.val == commands.WRITE):    # memory write operaton
                data.next = None
                regFile[str(sd_intf.addr.val)] = sd_intf.dq
                #print "i ",(regFile[sd_intf.addr.val])
                #print "add: ",str(sd_intf.addr.val)," val: ",str(sd_intf.dq)
            else:
                #print str(regFile.get(str(sd_intf.addr.val),0))
                data.next = regFile.get(str(sd_intf.addr.val),0)

       # print "address:",sd_intf.addr," value : ",regFile[str(sd_intf.addr.val)]
                
    return control_logic_inst,function

def Control_Logic(curr_command,sd_intf):

    @always(sd_intf.clk.posedge)
    def decode():
        # detect the registered command
        if(sd_intf.cs == 1):
            # cs ras cas we dqm : H X X X X
            curr_command.next = commands.COM_INHIBIT
        else:
            if(sd_intf.ras == 1):
                if(sd_intf.cas == 1):
                    if(sd_intf.we == 1):
                        # cs ras cas we dqm : L H H H X
                        curr_command.next = commands.NOP
                    else:
                        # cs ras cas we dqm : L H H L X
                        curr_command.next = commands.BURST_TERM
                else:
                    if(sd_intf.we == 1):
                        # cs ras cas we dqm : L H L H X
                        curr_command.next = commands.READ
                    else:
                        # cs ras cas we dqm : L H L L X
                        curr_command.next = commands.WRITE
            else:
                if(sd_intf.cas == 1):
                    if(sd_intf.we == 1):
                        # cs ras cas we dqm : L L H H X
                        curr_command.next = commands.ACTIVE
                    else:
                        # cs ras cas we dqm : L L H L X
                        curr_command.next = commands.PRECHARGE
                else:
                    if(sd_intf.we == 1):
                        # cs ras cas we dqm : L L L H X
                        curr_command.next = commands.AUTO_REFRESH
                    else:
                        # cs ras cas we dqm : L L L L X
                        curr_command.next = commands.LOAD_MODE
    
    return decode

