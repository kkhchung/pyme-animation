# pyme-animation
More fleshed out version of the animations tools in PYME.
Should be able to generate movies good enough for publishing without coding.
Can save/load animation script or generate actual image series or movie.

Require scipy > 1.2 (for rotations) and opencv (for saving to movie).

Allows saving / loading of these parameters as a snapshot
* target position / rotation
* scale
* clipping position / rotation
* Showing or hiding the LUT / scale bar, and axes
* Background color
* Layer 0 alpha and point size

Allows animated movement between 2 snapshots with control for
* duration
* transition style: linear, smooth (ease in/out), etc

GUI controls for:
* Specifying output image/video dimension
* Basic zoom/rotation/move buttons with fixed step size (hold down 'Shift' or 'Ctrl' for other size)
* All the snapshot settings are exposed in a list control for editing

## Instructions:
* Should be pretty standard for animation software
* Add snapshot / key frames
* Should automatically generate transition animation
* Click 'Make' to generate images/movie
* Any changes made on the canvas while having a snaphot selected should be automatically saved
* For generating 360 degree rotation, add sequential frames at 45 degree (e.g. with the rotate buttons) and set transition mode to LINEAR


## Todo's
* Code needs refactoring and cleanup
* Need code comments
* Add way to specify output format.
* Need to expose FPS setting

## Bugs:
* Changes are not propagated to the 'Layers' and 'View Clipping' panel