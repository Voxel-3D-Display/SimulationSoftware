import numpy as np
from PIL import Image
import os
import pygame


def voxel_frames_to_hdmi_frame(v_frames):
    """
    Converts a series of voxel frames (48x30 pixels) to an HDMI frame (1920x1080). By nature, there is a maximum
    of 1080 voxel frames that can fit in a single HDMI frame. THe HDMI frames are structured as below:

    [ # # # # # # # # # # # # # # # # . . . # # # # 0 0 0 . . . 0 0 0 0 0 0 ]
    [ # # # # # # # # # # # # # # # # . . . # # # # 0 0 0 . . . 0 0 0 0 0 0 ]
    [ # # # # # # # # # # # # # # # # . . . # # # # 0 0 0 . . . 0 0 0 0 0 0 ]
    [ . . .               . . .                                       . . . ]
    [ . . .                   . . .                                   . . . ]
    [ . . .                       . . .                               . . . ]
    [ # # # # # # # # # # # # # # # # . . . # # # # 0 0 0 . . . 0 0 0 0 0 0 ]
    [ # # # # # # # # # # # # # # # # . . . # # # # 0 0 0 . . . 0 0 0 0 0 0 ]
    [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
    [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
    [ . . .                                       . . .               . . . ]
    [ . . .                                           . . .           . . . ]
    [ . . .                                               . . .       . . . ]
    [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]
    [ 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]

    It is a 1920x1280x3 numpy array where the # represents the pixels and the 0 represent blank values.
    THe size of the data within the frame will be 1440 x n where n is the number of voxel frames per revolution.
    There actual matrix sizes need an additional dimension of 3 to store RGB values.

    :param v_frames: a numpy array of shape (n, 30, 48, 3) where n is the number of voxel frames per revolution.
    :return: A numpy array of shape (1920, 1080, 3) that represents an HDMI frame
    """

    # Check if size of input array is correct
    try:
        assert v_frames.shape[0] <= 1080 and v_frames.shape[1] == 30 and v_frames.shape[2] == 48 and v_frames.shape[3] == 3
    except (IndexError, AssertionError):
        print(bcolors.WARNING + "Voxel frames matrix was incorrect size. Got {} but expected (n, 30, 48, 3) with n <= 1080".format(
                v_frames.shape) + bcolors.ENDC)
        raise AssertionError

    # Resize array to HDMI frame
    h_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    h_frame[0:v_frames.shape[0], 0:1440, :] = v_frames.reshape(v_frames.shape[0], 1440, 3)

    return h_frame.transpose((1, 0, 2))


def save_hdmi_frame_to_bitmap(hdmi_frame, directory, bitmap_num):
    """
    Saves an hdmi frame to a bitmap image with a name of "0000000n.bmp" (each name is 8 digits long and n is the
    bitmap_num.

    :param hdmi_frame: The HDMI frame to convert to a bitmap image
    :param directory: The directory to save the file to
    :param bitmap_num: The image number that will be used for the file name
    """

    im = Image.fromarray(hdmi_frame)
    filepath = os.path.join(directory, str(bitmap_num).zfill(8) + '.bmp')
    im.save(filepath)


def display_image_from_bitmap(display_frame, directory, bitmap_num):
    """
    Uses pygame to display an image to the raspberry pi HDMI output, still need to use pygame.display.update() after

    :param display_frame: The pygame display object
    :param directory: The directory where the bitmap images are stored
    :param bitmap_num: The number for the image to display
    """

    img = pygame.image.load(os.path.join(directory, str(bitmap_num).zfill(8) + '.bmp'))
    display_frame.blit(img, (0, 0))


# For printing colored fonts to terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Code to test some of the functions
if __name__ == "__main__":

    voxel_frames = np.zeros((360, 30, 48, 3), dtype=np.int64)
    num = 0
    for i in range(360):
        for j in range(30):
            for k in range(48):
                for l in range(3):
                    num = i * (10 ** 4) + j * (10 ** 2) + k
                    voxel_frames[i, j, k, l] = num

    hdmi_frame = voxel_frames_to_hdmi_frame(voxel_frames)

    print(hdmi_frame.T.T.shape)



