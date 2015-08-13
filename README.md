# SDRAM_Controller

This repository is created to host the work I done for Google Summer of Code 2015. It contains a Sdram controller and a modal that can be used to test the modal.
All the designs are written in MyHDL which is a HDL written in Python. Details and manual to use MyHDL can be found on http://myhdl.org/

## Prerequistes ##

* Python 2
* MyHDL

## Instructions ##

To run the tests myhdl and SDRAM_Controller should be included in the PYTHONPATH
```bash
export PYTHONPATH = $PYTHONPATH:<path to myhdl>:<path to SDRAM_Controller>

python <path to SDRAM_Controller>/Simulator/test/test_sdram.py

python <path to SDRAM_Controller>/Controller/TestBench.py
```
## Simulator ##

This folder contains a sdram modal. It has a similar interface to real sdram which is defined in the file sd_intf.py
The modal is closely simulating the sdram behaviour with the timing delays so that an sdram controller can be tested for functionality.

### Simulator Output ###

This simulator prints several types of messages to the console.

| Output                                         | Description                                                                             |
|------------------------------------------------|-----------------------------------------------------------------------------------------|
|SDRAM : [COMMAND]  command-name                 | In every possitive edge of the clock cycle sdram will print the current command issued. (This would appear only if show_command is set to True. Default is False) |
|STATE : [CHANGE] old-state -> new-state @  time | Each bank can be in different state. This would print the state transition and the time |
|DATA : [WRITE] Addr: addr  Data: value          | This print happens at the moment when data is written to the memory. There is a few cycle delay between the time write command appear in the pins and the time when actual data is written to the memory |
|STATE : [READ] Data Ready @  time               | This is a very important print. It appears when sdram start driving the data bus with the read value. Since the sdram will only drive the bus for a limited time the controller should extract the data right after this time |
|SDRAM : [ERROR] error-message                   | There are several self tests in the sdram. If this type of message appear in the output, controller is not functioning properly. error-message will give more information about the error. |

## Controller ##

The controller is written reffering the VHDL designed by xesscorp which can be found on https://github.com/xesscorp/VHDL_Lib/blob/master/SdramCntl.vhd

Sdram controller make it easy to access the sdram. The host logic can use the sdram more likely an sram because of the controller.
Host side interface of the controller is present on the file host_intf.py

### Instructions ###

* WRITE : To perform write operation write the address to addr and the data to data_i and drive write_i high. Hold the values until done_o goes high.
* READ  : To perform read operation write the read address to addr and wait until don_o goes high. Read the value of data_o as soon as done_o goes high. 

* MyHDL allows to write transactors in the host_intf.py file where the host side interface is defined. Transactors furthur simplifies usage of the controller. With transactors read and write looks like follows

```python
        yield host_intf.write(120,23)
        yield host_intf.done_o.posedge

        yield host_intf.read(120)
        yield host_intf.done_o.posedge
        print "Data Value : ",host_intf.data_o
```

### Limitations ###

Sdram can be programmed to used in several different modes. However this controller does not allow to set up the sdram user mode. Instead it uses a fixed mode where burst length is one.
