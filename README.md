
>*Note: Project still in development, code-base is not yet complete*

# e3SpaceProgram
## Hermes III - Polaroids in Space


## Intro

This script uses a Raspberry Pi and a SenseHAT break-out board to actuate a 1980's Polaroid camera.

The camera is included in the payload of a High Altitude Balloon; the purpose of the script is to actuate the camera at altitude so that the camera takes photos of the Earth from space.

A full description of the project will be made available soon. It will include images of the payload and its construction, as well as a bill of materials. 

You can also follow the project on social media via twitter.com/e3spaceprogram

## License

The script is available under the GPL license. 

## Code Overview

The script is started using the joystick control on the SenseHAT.

Once started, the script measures the atmospheric pressure as a proxy for the altitude of the payload. Once it's sufficiently low (or, as a back-up, sufficient time has passed) the RPi triggers the Polaroid camera 8 times (with a user-defined gap in between each photo). 

Prior to taking each photo, the accelerometer measures the position and speed of the camera to try and ensure the camera is as stable and level as possible to help ensure the photo is as good as possible.

## Camera

The script uses the GPIO pins on the Pi to short-circuit the manual switch on the camera itself. This involves taking the facia off the camera and soldering some wires in place and so comes with a certain amount of risk of breaking the camera. Detailed instructions for this will be made available in the coming weeks.

## Power

The Polaroid camera itself is powered by a small battery in the film catridge. Unfortunately, this battery will freeze and die at altitude and your camera won't work (as happened with [Hermes II] (https://twitter.com/e3SpaceProgram/status/729339846649597952). 

To avoid this problem, solder energizer lithium batteries in parallel with the inbuilt battery in the camera (be careful not to break anything). 

## Film

The film used for Hermes III is made by the [Impossible Project](https://uk.impossible-project.com/) who make instant film for Polaroid cameras (Polaroid stopped making the film back in 2008).

The film itself is a series of chemical layers that would freeze in the low temperatures of the edges of the atmosphere.

To mitigate this risk, the photos are ejected into a heated bath of glycerine that helps maintain the temperature of the film as it develops (development takes ~45 mins). 
