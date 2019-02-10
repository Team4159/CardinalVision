# CardinalVision
This is Team 4159's image recognition code running on the Nvidia Jetson TX1. We use an IR sensitive camera with an IR filter and an IR LED ring around it to detect the retroreflective tape.

## How to install and run on your computer:
1. Install python
2. Clone this directory
3. `cd` into directory
4. Uncomment OpenCV in `requirements.txt`
5. `pip3 install -r requirements.txt`
6. `python3 Vision.py`

## Links for Getting it to run on the Jetson TX1

[Installing OpenCV on the Jetson](https://github.com/jetsonhacks/buildOpenCVTX1/). You can change the versions inside the script to get a different version of OpenCV. This script will also install Python 2.7 and 3.5.

[Installing the Driver for the Playstation 3 Eye Camera](https://github.com/jetsonhacks/installPlayStationEyeTX1). Make sure that the Jetson is running [Linux For Tegra R24.2.1](https://developer.nvidia.com/embedded/linux-tegra-r2421), the driver won't work for any other versions.
