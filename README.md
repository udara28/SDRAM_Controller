# SDRAM_Controller

This repository is created to host the work I done for Google Summer of Code 2015. It contains a Sdram controller and a modal that can be used to test the modal.
All the designs are written in MyHDL which is a HDL written in Python. Details and manual to use MyHDL can be found on http://myhdl.org/

## Prerequistes ##

* Python 2
* MyHDL

## Instructions ##

To run the tests myhdl and SDRA_Controller should be included in the PYTHONPATH
```bash
export PYTHONPATH = $PYTHONPATH:<path to myhdl>:<path to SDRAM_Controller>
```
## Simulator ##

This folder contains a sdram modal. It has a similar interface to real sdram which is in the file sd_intf.py
The modal is closely simulating the sdram behaviour with the timing delays so that an sdram controller can be tested for functionality.

### Simulator Output ###

This simulator prints several types of messages to the console.

| Output                                                    | Description                                                                             |
|-----------------------------------------------------------|-----------------------------------------------------------------------------------------|
|SDRAM : [COMMAND]  command-name                            | In every possitive edge of the clock cycle sdram will print the current command issued. |
|BANK ba-id STATE : [CHANGE] old-state -> new-state @  time | Each bank can be in different state. This would print the state transition and the time |
|DATA : [WRITE] Addr: addr  Data: value                     | This print happens at the moment when data is written to the memory. There is a few cycle delay between the time write command appear in the pins and the time when actual data is written to the memory |
|STATE : [READ] Data Ready @  time                          | This is a very important print. It appears when sdram start driving the data bus with the read value. Since the sdram will only drive the bus for a limited time the controller should extract the data right after this time |
|SDRAM : [ERROR] error-message                              | There are several self tests in the sdram. If this type of message appear in the output controller is not functioning properly. error-message will give more information about the error. |


TODO : In the future additional parameters will be introduced to control which type of messages are printed to the console. So that only important messages are shown.

## Controller ##

The controller is written reffering the VHDL designed by xesscorp which can be found on https://github.com/xesscorp/VHDL_Lib/blob/master/SdramCntl.vhd

Sdram controller make it easy to access the sdram. The host logic can use the sdram more likely an sram because of the controller.
Host side interface of the controller is present on the file host_intf.py

### How to Use ###

TODO:
