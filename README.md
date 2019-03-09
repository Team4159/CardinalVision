# CardinalVision
This is Team 4159's image recognition code running on the Nvidia Jetson TX1. We use the Playstation Eye camera with an infrared polyester filter and a 850nm IR LED ring around it to detect the retroreflective tape.

## How to Setup / Develop

Prerequisites:

`python3`

Clone this repository:

`git clone https://github.com/Team4159/CardinalVision.git`

Install CardinalVision and dependencies:

`python3 setup.py develop`

Run Debugging Configuration:

`python3 -m CardinalVision.vision.debug_vision`

You can include extra options if needed:

`--category [category]` - The folder within `CardinalVision/test` where the debugging video is.
`--name [name]` - The name of the file within the folder.
`--fps [fps]` - The fps of the debugging video


## Help for Setting Up the Jetson TX1

_Building OpenCV on the Jetson:_
1) Clone [opencv_contrib](https://github.com/opencv/opencv_contrib) (for CUDA support).
2) Download [this script](https://github.com/jetsonhacks/buildOpenCVTX1), it's usable but you need to make some changes.
3) Change the OpenCV version in the script to the latest, and add some stuff to the `cmake` options:
    1) `-D OPENCV_EXTRA_MODULES=../opencv_contrib/modules` to build with extras.
    2) If low on space, exclude modules that you don't need from the build: http://answers.opencv.org/question/56049/exclude-modules-while-building-opencv/

_Swtiching Between Internet and Static IP for the Radio:_
1) Open `/etc/network/interfaces.d/eth0` with an editor (`gedit`, `vim`, etc.)
2) Uncomment the commented lines and comment to uncommented ones.
3) Restart the network service: `sudo /etc/init.d/networking restart`

_Installing Playstation 3 Eye Camera Driver:_
1) Use [this script](https://github.com/jetsonhacks/installPlayStationEyeTX1). Make sure that the Jetson is running [Linux For Tegra R24.2.1](https://developer.nvidia.com/embedded/linux-tegra-r2421), the driver won't work for any other versions.
