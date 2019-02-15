# CardinalVision
This is Team 4159's image recognition code running on the Nvidia Jetson TX1. We use the Playstation Eye camera with an infrared polyester filter and a 850nm IR LED ring around it to detect the retroreflective tape.

## Links for Getting it to run on the Jetson TX1

[Installing OpenCV on the Jetson](https://github.com/jetsonhacks/buildOpenCVTX1/). You can change the versions inside the script to get a different version of OpenCV. This script will also install Python 2.7 and 3.5.

_Tips for building OpenCV on the Jetson:_

1) Build with all 4 cores by using `-j4` flag
2) Exclude modules that you don't need from the build: http://answers.opencv.org/question/56049/exclude-modules-while-building-opencv/

[Installing the Driver for the Playstation 3 Eye Camera](https://github.com/jetsonhacks/installPlayStationEyeTX1). Make sure that the Jetson is running [Linux For Tegra R24.2.1](https://developer.nvidia.com/embedded/linux-tegra-r2421), the driver won't work for any other versions.
