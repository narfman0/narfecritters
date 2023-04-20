smb3-video-autosplitter
==============

.. image:: https://badge.fury.io/py/smb3-video-autosplitter.png
    :target: https://badge.fury.io/py/smb3-video-autosplitter

.. image:: https://ci.appveyor.com/api/projects/status/github/narfman0/smb3-video-autosplitter?branch=main
    :target: https://ci.appveyor.com/project/narfman0/smb3-video-autosplitter

Ingest video data from a capture card to autosplit in livesplit

Installation
------------

Navigate to the most recent versioned release here:

https://github.com/narfman0/smb3-video-autosplitter/releases

Download the zip and extract to your favorite directory.

We need to update the trigger frame and region. First set show_capture_video=true,
then run the tool. Take a screen cap of princess peach's letter or similar, then
crop her face and take note of coordinates and width/height. Replace trigger.png
in the `data/` directory, and set the `autosplitter_region` equal to the x,y,width,height
of the cropped image relative to the original image.

License
-------

Copyright (c) 2023 Jon Robison

See LICENSE for details
