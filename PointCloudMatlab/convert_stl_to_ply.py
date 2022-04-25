import os
import pymeshlab
import shutil

folder_name = "hand"
# os.chdir(os.path.join(os.getcwd()))
folder_level = os.getcwd()
path = os.path.join(os.getcwd(), "stls/" + folder_name)

new_folder = os.path.join(folder_level, "plys/" + folder_name)
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

for file_name in os.listdir(path):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(os.path.join(path, file_name))
    ms.generate_sampling_poisson_disk(samplenum=100000)
    ms.save_current_mesh(os.path.join(new_folder, file_name[:-4] + ".ply"))

# shutil.make_archive(folder_name + "_PLY_Files", 'zip', new_folder)
