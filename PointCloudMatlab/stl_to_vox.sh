#!/bin/bash

python convert_stl_to_ply.py $1 $2
#matlab -nodisplay -nosplash -nodesktop -r "CylinderSampleScript('$1'); exit"
matlab -r "CylinderSampleScript('$1'); exit"
cp still_bins/$1.vox ../../pi_fs/VOXEL/bins
