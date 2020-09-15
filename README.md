# Scale2

Overview:
Scale for EDGE, including basic and takeaway scale versions

Features:
Basic scale mode as well as takeaway scale mode that has pretop for cheese and pepperoni (auto tare when within tolerance of desired weight)

Setup & Installation:
1. Install Raspbian to Raspberry Pi (any version)
2. Run the following commands to install the Luma LED Matrix library
  $ sudo raspi-config and enable P4 SPI
  $ sudo usermod -a -G spi,gpio pi
  $ sudo apt install build-essential python3-dev python3-pip libfreetype6-dev libjpeg-dev libopenjp2-7 libtiff5
  $ sudo -H pip3 install --upgrade --ignore-installed pip setuptools
  $ sudo -H pip3 install --upgrade luma.led_matrix
3. Run the following commands to set up firebase and pyfireconnect (which makes firebase python3 compatible)
  $ sudo pip3 install python-firebase
  $ sudo pip3 install pyfireconnect
4. Clone this repository onto the Pi
  $  git clone https://github.com/corinnedixon/Scale2
5. To allow the code to run on boot, type sudo nano /etc/rc.local and paste this into the file before exit 0: 
  python 3/home/pi/Scale2/takeawayscale.py &

Usage & Details:
Code runs with proper scale load cell.  For pretop features, also need 3 position switch, two position switch, and 4 buttons.
These ports can be changed in the file being run (takeawayscale.py)

Credits:
Code for reading and writing to scale written by David Vincent
