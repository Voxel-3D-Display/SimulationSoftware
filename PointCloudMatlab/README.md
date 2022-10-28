# PointCloudMatlab

This method uses the Computer Vision Toolbox.

## Generating .ply files

Meshlab is used to generate .ply files from any standard mesh format. Import the mesh file. Select Filters > Sampling > Poisson-disk sampling. Increase the number of samples to 100000. This will generate a new layer with a random point cloud on the surface of the mesh file. Making sure this layer is selected, go to File > Export Mesh As... . Make sure Stanford Polygon File Format is selected as the filetype, with an extension of .ply. Save the file somewhere.

## Using the new point cloud files

Open CylinderSample.m. Change the file to the desired mesh file, and click run. The file uses MATLAB's point cloud object to resample the object at VOXEL's cylindrical locations.

After the progress bar completes, the original .ply file should pop up in Figure 1, and the new point cloud sampled at the correct locations should pop up in Figure 2.
