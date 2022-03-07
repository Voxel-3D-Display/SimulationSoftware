import numpy as np
from PIL import Image
import os
import sys
import pygame
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl


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

    It is a 1080x1920x3 numpy array where the # represents the pixels and the 0 represent blank values.
    THe size of the data within the frame will be 1440 x n where n is the number of voxel frames per revolution.
    There actual matrix sizes need an additional dimension of 3 to store RGB values.

    :param v_frames: a numpy array of shape (n, 30, 48, 3) where n is the number of voxel frames per revolution.
    :return: A numpy array of shape (1080, 1920, 3) that represents an HDMI frame
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

    return h_frame


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


def simulate_3d_image_from_voxel_frames(v_frames):
    v = Visualizer()
    v.animation()


def generate_static_test_image():
    """
    This will generate a static test image that can be used for initial tests. The first voxel frame will be a
    image that transitions in color and the rest of the voxel frames will be black.

    :return: voxel frames
    """
    v_frames = np.zeros((720, 30, 48, 3), dtype=np.uint8)
    first_voxel_frame = np.zeros((30, 48, 3), dtype=np.uint8)
    for i in range(30):
        for j in range(48):
            first_voxel_frame[i, j, 0] = i*8  # Set red gradient that increases going down
            first_voxel_frame[i, j, 1] = j*5  # Set green gradient that increases going right

    v_frames[0] = first_voxel_frame
    return v_frames



class Visualizer(object):
    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 80
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1080, 1080)
        self.w.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        self.height = 30
        self.width = 48

        self.image_index = 0
        self.image_max = 30

        self.dpu = 2
        self.rpu = self.dpu * np.pi / 180
        self.r = np.arange(-self.width / 2, self.width / 2)  # radius
        self.t = np.arange(-np.pi, np.pi, self.rpu)  # theta
        self.z = np.arange(self.height)  # z

        # Initialize the 3D grid
        gx = gl.GLGridItem()
        gx.setSize(x=self.width, y=self.width, z=0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.setSize(x=self.height, y=self.width, z=0)
        gy.rotate(90, 0, 1, 0)
        gy.rotate(90, 0, 0, 1)
        gy.translate(0, 0, self.height / 2)
        self.w.addItem(gy)

        # Initialize the object to store the color data of all of the 3D Voxels
        i = 0
        for t in self.t:
            x = self.r * np.cos(t)
            y = self.r * np.sin(t)
            for z in self.z:
                points = np.vstack((x, y, z * np.ones_like(x)))
                color = np.abs(self.r) / np.max(np.abs(self.r))
                color /= 4
                colors = np.vstack((color, color, color, np.ones_like(color)))
                self.traces[i] = gl.GLScatterPlotItem(
                    pos=points.T,
                    color=colors.T,
                    size=4
                )
                self.w.addItem(self.traces[i])
                i += 1

        # os.system("rm *-cylinder.png")
        # self.savepng()

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color):
        self.traces[name].setData(pos=points, color=color)

    def savepng(self):
        self.w.grabFramebuffer().save('out/%05d-cylinder.png' % self.image_index)
        self.image_index += 1
        if self.image_index > self.image_max:
            print('hi')
            self.timer.stop()
            os.system("ffmpeg -f image2 -r 15 -i out/%05d-cylinder.png -vcodec mpeg4 -y cylinder.mp4")

    def update(self):

        sinc = np.zeros((self.z.shape[0], self.r.shape[0]))
        zval = 100 * np.sin(0.01 * np.pi * self.r) / self.r
        print(zval)
        for rind in range(len(self.r)):
            closest_zind = np.argmin(np.abs(self.z - zval[rind]))
            sinc[closest_zind, rind] = 1

        i = 0
        for t in self.t:
            x = self.r * np.cos(t)
            y = self.r * np.sin(t)
            for index, z in enumerate(self.z):
                points = np.vstack((x, y, z * np.ones_like(x)))
                color = sinc[index, :]
                colors = np.vstack((color, color, color, np.ones_like(color)))
                self.traces[i].setData(pos=points.T, color=colors.T)
                i += 1
        print("update")
        # self.savepng()

    def animation(self):
        self.timer.start(20)
        self.start()


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

    # simulate_3d_image_from_voxel_frames(voxel_frames)
    voxel_frames = generate_static_test_image()
    hdmi_frame = voxel_frames_to_hdmi_frame(voxel_frames)
    save_hdmi_frame_to_bitmap(hdmi_frame, os.getcwd(), 1)




