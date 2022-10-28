#!/bin/bash 

ffmpeg -f image2 -r 15 -i out/%05d-cylinder.png -vcodec mpeg4 -y cylinder.mp4
ffmpeg -f image2 -r 15 -i out/%05d-cylindersim.png -vcodec mpeg4 -y cylindersim.mp4
