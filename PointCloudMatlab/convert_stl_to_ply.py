import os
import sys
import pymeshlab
import shutil

file_name = sys.argv[1]
# os.chdir(os.path.join(os.getcwd()))
folder_level = os.getcwd()
path = os.path.join(folder_level, "stls/" + file_name + sys.argv[2])

ms = pymeshlab.MeshSet()
ms.load_new_mesh(path)
ms.generate_sampling_poisson_disk(samplenum=100000)
ms.save_current_mesh(os.path.join(folder_level, "plys/", file_name + ".ply"))

# shutil.make_archive(folder_name + "_PLY_Files", 'zip', new_folder)
