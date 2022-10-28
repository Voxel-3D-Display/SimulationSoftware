import matlab.engine    # install instructions located at https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html
import glob
import os
import shutil

from numpy import True_

# model_name = 'lava_lamp'
model_names = [
# "minecraft_steve_running",
# "mommy_walking",
# "dino_running",
# "chicken_looking",
# "rubiks",
# "kitten_playing",
# "water_waves", 
# "drone_flying"
"spiderman_swinging"
]

render_type = 'animation'
resample_plys_flag = True
colored_flag = True

cloud_compare_dir = 'F:\CloudCompare'
resampling_mesh_points = 100000
parent_dir = os.path.dirname(os.path.abspath(__file__))

def create_folders():
    if not os.path.exists(os.path.join(parent_dir,'plys')):
        os.mkdir(os.path.join(parent_dir,'plys'))
    if not os.path.exists(os.path.join(parent_dir,'plys_sparse')):
        os.mkdir(os.path.join(parent_dir,'plys_sparse'))
    if not os.path.exists(os.path.join(parent_dir,'still_bins')):
        os.mkdir(os.path.join(parent_dir,'still_bins'))
    if not os.path.exists(os.path.join(parent_dir,'video_bins')):
        os.mkdir(os.path.join(parent_dir,'video_bins'))
    if not os.path.exists(os.path.join(parent_dir,'out')):
        os.mkdir(os.path.join(parent_dir,'out'))

def clean_resampled_plys():
    # for file in glob.glob(os.path.join(parent_dir,'*_SAMPLED_POINTS.*'), recursive=True):
    for file in glob.glob(os.path.join(parent_dir,'**','*_SAMPLED_POINTS.*'), recursive=True):
        if "_SAMPLED_POINTS." in file:
            os.remove(file)

def resample_plys(model_name, file_extension = '.ply'):
    if (render_type == 'still'):
        plys_sparse_dir = os.path.join(parent_dir,'plys_sparse')
        plys_dir = os.path.join(parent_dir,'plys')
        os.chdir(cloud_compare_dir)
        os.system("CloudCompare -SILENT -AUTO_SAVE OFF -C_EXPORT_FMT PLY -O {ply_path} -SAMPLE_MESH POINTS {mesh_points} -NO_TIMESTAMP -SAVE_CLOUDS".format(ply_path = os.path.join(plys_sparse_dir,model_name+file_extension), mesh_points = resampling_mesh_points))
        shutil.move(os.path.join(plys_sparse_dir,model_name+'_SAMPLED_POINTS.ply'), os.path.join(plys_dir,model_name+'.ply'))
    elif (render_type == 'animation'):
        plys_sparse_dir = os.path.join(parent_dir,'plys_sparse',model_name)
        plys_dir = os.path.join(parent_dir,'plys',model_name)
        file_index = 1
        if not os.path.exists(plys_dir):
            os.mkdir(plys_dir)
        for file in os.listdir(os.path.join(plys_sparse_dir)):
            os.chdir(cloud_compare_dir)
            os.system("CloudCompare -SILENT -AUTO_SAVE OFF -C_EXPORT_FMT PLY -O {ply_path} -SAMPLE_MESH POINTS {mesh_points} -NO_TIMESTAMP -SAVE_CLOUDS".format(ply_path = os.path.join(plys_sparse_dir,file), mesh_points = resampling_mesh_points))
            # print(os.path.splitext(file)[0])
            # shutil.move(os.path.join(plys_sparse_dir,os.path.splitext(file)[0]+'_SAMPLED_POINTS.ply'), os.path.join(plys_dir,os.path.splitext(file)[0]+'.ply'))
            shutil.move(os.path.join(plys_sparse_dir,os.path.splitext(file)[0]+'_SAMPLED_POINTS.ply'), os.path.join(plys_dir, str(file_index).zfill(5) +'.ply'))
            file_index += 1
    else:
        print("RenderTypeError: Incorrect render type entered.")
    os.chdir(parent_dir)


def exec_matlab(model_name):
    os.chdir(parent_dir)
    eng = matlab.engine.start_matlab()
    eng.addpath(eng.genpath(parent_dir), nargout=0)     # add parent folder to matlab path to allow matlab to search for files in the parent folder

    if (render_type == 'still'):
        eng.workspace['filename'] = model_name
        eng.CylinderSampleStill(nargout=0)
    elif (render_type == 'animation'):
        eng.workspace['folder'] = model_name
        eng.workspace['colored'] = colored_flag
        eng.CylinderSampleVidFrames(nargout=0)
    else:
        print("RenderTypeError: Incorrect render type entered.")
    eng.quit()

def transfer_vox_to_rpi():
    pass


# exports plys from blender -> resample plys to increase point cloud density -> create a .vox/.mp4 file using plys in matlab -> send over to rpi
def generate_dot_vox(model_name):
    if (resample_plys_flag):
        resample_plys(model_name)
    # if (render_type == 'still'):
    exec_matlab(model_name)
    # transfer_vox_to_rpi()


def run_plys_to_vox_script(model_name):
    create_folders()
    clean_resampled_plys()
    generate_dot_vox(model_name)

if __name__ == "__main__":
    for model in model_names: 
        run_plys_to_vox_script(model)