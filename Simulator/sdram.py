from myhdl import *

commands = enum("COM_INHIBIT","NOP","ACTIVE","READ","WRITE","BURST_TERM", \
                    "PRECHARGE","AUTO_REFRESH","LOAD_MODE","OUTPUT_EN","OUTPUT_Z","INVALID")

states   = enum("Uninitialized","Initialized","Idle","Activating","Active","Read","Reading","Read_rdy","Write","Writing")

regFile  = {}

def sdram(sd_intf):

    regFile  = {}                       # register file for holding the values
    data = sd_intf.dq.driver()          # driver for bidirectional DQ port

    curr_command = Signal(commands.INVALID)
    control_logic_inst = Control_Logic(curr_command,sd_intf)

    curr_state = [ State(0,sd_intf), State(1,sd_intf), State(2,sd_intf), State(3,sd_intf) ] # Represents the state of eah bank

    @always(sd_intf.clk.posedge)
    def function():
        if(sd_intf.cke == 1):
            print " SDRAM : [COMMAND] ", curr_command

            for bank_state in curr_state :
                bank_state.nextState(curr_command)

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
        if(curr_state[bs.val].active_row != None):
            print " SDRAM : [ERROR] A row is already activated. Bank should be precharged first"
            return None
        if(curr_state[bs.val].getState() == states.Uninitialized):
            print " SDRAM : [ERROR] Bank is not in a good state. Too bad for you"
            return None
        curr_state[bs.val].active_row = addr.val

    def read(bs,addr):
        if(curr_state[bs.val].active_row == None):
            print " SDRAM : [ERROR] A row should be activated before trying to read"
        else:
            print " okay"        

    def write(bs,addr):
        if(curr_state[bs.val].active_row == None):
            print " SDRAM : [ERROR] A row should be activated before trying to write"

    def precharge(bs,addr):
        if(addr.val[10] == 1):           # Precharge all banks command
            for bank in curr_state :
                bank.active_row = None
        else:                            # Precharge selected bank
            curr_state[bs.val].active_row  = None

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

class State:

    def __init__(self,bank_id,sd_intf,regFile={}):
        self.state      = states.Uninitialized
        self.init_time  = now()
        self.wait       = 0
        self.bank_id    = bank_id
        self.memory     = regFile
        self.sd_intf    = sd_intf
        self.driver     = sd_intf.dq.driver()
        self.active_row = None
        self.addr       = None
        self.data       = None

    def nextState(self,curr_command):
        self.wait = now() - self.init_time
    
        if(self.state == states.Uninitialized):
            if(self.wait >= self.sd_intf.timing['init']):
                print " BANK",self.bank_id,"STATE : [CHANGE] Uninitialized -> Initialized @ ", now()
                self.state     = states.Initialized
                self.init_time = now()
                self.wait      = 0

        # Reading states
        if(self.state == states.Idle):
            if(curr_command ==  commands.READ):
                self.state     = states.Reading
                self.init_time = now()
                if(sd_intf != None):
                    self.addr  = self.sd_intf.addr

        if(self.state == states.Reading):
            if(self.wait >= sd_intf.timing['rcd']):
                self.state     = states.Read_rdy
                self.init_time = now()
                self.driver.next = self.memory[self.active_row + self.addr]

        if(self.state == states.Read_rdy):
                self.state = states.Idle
                self.init_time = now()
                self.driver.next = None 

        # Writing states
        if(self.state == states.Idle):
            if(curr_command == commands.WRITE):
                self.state     = states.Writing
                self.init_time = now()
                if(sd_intf != None):
                    self.addr  = self.sd_intf.addr
                    self.data  = self.sd_intf.data

        if(self.state == states.Writing):
            if(self.wait >= self.sd_intf.timing['rcd']):
                self.state     = states.Idle
                self.init_time = now()
                self.memory[self.active_row + self.addr] = self.data

    def getState(self):
        return self.state

    def getData(self):
        return self.data
