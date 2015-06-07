from myhdl import *


commands = enum("COM_INHIBIT","NOP","ACTIVE","READ","WRITE","BURST_TERM", \
                    "PRECHARGE","AUTO_REFRESH","LOAD_MODE","OUTPUT_EN","OUTPUT_Z","INVALID")

def sdram(sd_intf):

    regFile  = {}                       # register file for holding the values
    data = sd_intf.dq.driver()          # driver for bidirectional DQ port

    curr_command = Signal(commands.INVALID)
    control_logic_inst = Control_Logic(curr_command,sd_intf)

    active_row = [None,None,None,None]  # Active row of each bank

    @always(sd_intf.clk.posedge)
    def function():
        if(sd_intf.cke == 1):
            print " SDRAM : [COMMAND] ", curr_command
            if(curr_command == commands.INVALID):
                print " SDRAM : [ERROR] Invalid command is given" 
            elif(curr_command == commands.ACTIVE):
                activate(sd_intf.bs,sd_intf.addr)
            elif(curr_command == commands.READ):
                read(sd_intf.bs,sd_intf.addr)
            elif(curr_command == commands.WRITE):
                write(sd_intf.bs,sd_intf.addr)
            elif(curr_command == commands.PRECHARGE):
                precharge(sd_intf.bs,sd_intf.addr)

   
    def activate(bs,addr):
        if(active_row[bs.val] != None):
            print " SDRAM : [ERROR] A row is already activated. Bank should be precharged first"
        active_row[bs.val] = addr.val

    def read(bs,addr):
        if(active_row[bs.val] == None):
            print " SDRAM : [ERROR] A row should be activated before trying to read"

    def write(bs,addr):
        if(active_row[bs.val] == None):
            print " SDRAM : [ERROR] A row should be activated before trying to write"

    def precharge(bs,addr):
        if(addr.val[10] == 1):           # Precharge all banks command
            for row in active_row :
                row = None
        else:                            # Precharge selected bank
            active_row[bs.val] = None

    return instances()

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

