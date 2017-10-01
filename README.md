

The Minstrel music software wraps around the mpg123 music player.  It
allows said player be controlled by hardware buttons wired to the GPIO
pins of a Raspberry Pi (tested with version model B revision 1.1).  It
provides minimal status information via a miniture OLED display wired
to those same pins.

Installing
==========

*Disclaimer* I have only tested this code on one hardware
 configuration.  Use at your own risk.

First, install dependencies on the Raspberry Pi:
- sudo apt-get install build-essential python-dev python-pip python-imaging python-smbus git
- sudo pip install RPi.GPIO
- git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
- cd Adafruit_Python_SSD1306
- sudo python setup.py install
- cd ..

Second, configure hardware.  You might find this guide useful:
https://learn.adafruit.com/adafruit-pioled-128x32-mini-oled-for-raspberry-pi/usage

Third, install minstrel:
- git clone https://github.com/woza/minstrel.git
- cd minstrel
- sudo python setup.py install
- cd ..

Configuration
=============
Minstrel expects your music to be stored under the directory /opt/music.

Minstrel can persist volume settings between runs.  This information
is stored in /var/minstrel/state/.  Minstrel will not automatically
create this directory (because it will probably lack the permissions
to do so), so you will need to create that directory by hand and
adjust permissions so that minstrel can write files to it.

Design
======

The software has a modular design, which allows the core logic to be
driven by normal keyboard inputs and output to a normal laptop screen
- this allows for the core logic to be tested without having to worry
about hardware interface issues or debugging on the target platform.

The following types of module are defined:
   - Model: implements a state machine that reacts to button presses - see src/state_machine.py
   - View: Retrieves information from the model and system and draws it into a Python Image Library (PIL) image  - see src/minstrel.py
   - Renderer: Places a PIL image on a physical screen - see src/oled.py and test/tk_display.py
   - Control loop: runs the main loop detecting input, dispatching it to the model and then updating the display - see src/main.py and test/tk_player.py

Other source code files:
=================
*File* | *Purpose* | *Alternative stubs*
src/buttons.py | Wraps GPIO interface logic | None
src/minstrel_enum.py | Defines enumerated types with useful methods | None
src/misc.py | Utility routines | None
src/system.py | Abstracts calls to backend system | test/stub_system.py
src/thermometer.py | Measures system temperature (automatically adjusts between Ubuntu & Raspbian) | None

Available tests
================

- Running the file test/tk_player.py will bring up a fully functional
  version of the music player on an Ubuntu system.  Output is to a
  small screen of the same dimensions as the physical screen on the
  Pi.

- test/test_button_wiring.py can be run on the Raspberry Pi to confirm
  that buttons are connected to the correct pins.  Run it, press
  buttons and your presses will be reported to stdout.

- test/state_script.py exercises the state machine - it ensures that
  the state transitions are as expected.

- test/plot_button.py can be used to check for transient button state
  readings that would require debouncing.  Run it and it will log
  (timestamp, state) pairs for the button wired to the 'play' GPIO
  pin.  The state is an integer (1 = pressed, 0 == not pressed) for
  ease of plotting in GNUplot.  *Be aware this code runs with no
  sleep() call and will take readings as quickly as it can - you can
  get a large file very quickly.* I have seen files grow at 36,000
  lines per second.