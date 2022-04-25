# -*- coding: utf-8 -*-
"""
    Animated 3D sinc function
"""

import os
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import struct

NEXT_FRAME = struct.pack('1B', 0xFF)
NEXT_SLICE = struct.pack('1B', 0xFE)
FRAMERATE = 15000
NUM_SLICES = 360

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
        self.width  = 48
        # self.height = 10
        # self.width  = 16
        
        self.image_index = 0
        self.image_max = 65

        self.dpu = 1
        self.rpu = self.dpu * np.pi / 180
        self.r = np.arange(-self.width/2, self.width/2) + 0.5
        print(self.r)
        self.t = np.arange(-np.pi, np.pi, self.rpu)
        # self.t = np.arange(0, self.rpu, self.rpu)
        self.z = np.arange(self.height)

        # create the background grids
        # gx = gl.GLGridItem()
        # gx.setSize(x=self.width/2)
        # gx.rotate(90, 0, 1, 0)
        # gx.translate(-self.width/2, 0, 0)
        # self.w.addItem(gx)
        # gy.setSize(y=self.width/2)
        # gy = gl.GLGridItem()
        # gy.rotate(90, 1, 0, 0)
        # gy.translate(0, -self.width/2, 0)
        # self.w.addItem(gy)
        # gz.setSize()
        # gz = gl.GLGridItem()
        # gz.translate(0, 0, -self.height)
        # self.w.addItem(gz)
        gx = gl.GLGridItem()
        gx.setSize(x=self.width, y=self.width, z=0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.setSize(x=self.height, y=self.width, z=0)
        gy.rotate(90, 0, 1, 0)
        gy.rotate(90, 0, 0, 1)
        gy.translate(0, 0, self.height/2)
        self.w.addItem(gy)

        self.u = 0
        self.d = 0.05

        i = 0
        for t in self.t:
            x = self.r * np.cos(t)
            y = self.r * np.sin(t)
            for z in self.z:
                points = np.vstack((x, y, z*np.ones_like(x)))
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
        
        self.prev_closest_zind_arr = np.zeros_like(self.r)

        os.system("rm *-cylinder.png")
        self.savepng()
        self.file = open("cylinder.bin", "wb")
        self.file.write(struct.pack('H', int(NUM_SLICES)))
        self.file.write(struct.pack('H', int(FRAMERATE)))
        self.file.write(NEXT_FRAME)
        for slice in range(NUM_SLICES) :
            self.file.write(NEXT_SLICE)
            for r_res in self.r :
                for z_res in self.z :
                    self.file.write(struct.pack('1B', int(self.height - z_res - 1)))
                    self.file.write(struct.pack('1B', int(r_res + 23.5)))
                    self.file.write(struct.pack('1B', int(0x00)))
                    self.file.write(struct.pack('1B', int(0x00)))
                    self.file.write(struct.pack('1B', int(0x00)))

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color):
        self.traces[name].setData(pos=points, color=color)

    def savepng(self):
        self.w.grabFramebuffer().save('out/%05d-cylinder.png' % self.image_index)
        self.image_index += 1
        if self.image_index > self.image_max :
            print('hi')
            self.timer.stop()
            self.file.close()
            os.system("ffmpeg -f image2 -r 15 -i out/%05d-cylinder.png -vcodec mpeg4 -y cylinder.mp4")

    def update(self):
        self.u += self.d
        # if self.u > 10 :
        #     self.d *= -1
        #     self.u = 10
        # elif self.u < 0 :
        #     self.d *= -1
        #     self.u = 0

        s = 2

        sinc = np.zeros((self.z.shape[0], self.r.shape[0]))
        zval = 0.5 * s * self.height * \
                ((np.cos(10*np.abs(2*self.r/self.width) - 2*np.pi*self.u))*np.exp(-self.u) \
                / (10*np.abs(2*self.r/self.width) + s) + 1/s)
        # zval = 0.5 * self.height * \
        #         ((np.sin(10*np.pi*np.abs(self.r / self.width) - 2*np.pi*self.u)) \
        #         / (10*np.abs(self.r / self.width) + self.height/10) + 1)
        print(zval)

        self.file.write(NEXT_FRAME)
        closest_zind_arr = np.empty_like(self.r)
        for rind in range(len(self.r)) :
            closest_zind = np.argmin(np.abs(self.z - zval[rind]))
            closest_zind_arr[rind] = closest_zind
            sinc[closest_zind, rind] = 1
        for slice in range(NUM_SLICES) :
            self.file.write(NEXT_SLICE)
            for rind in range(len(self.r)) :
                self.file.write(struct.pack('1B', int(self.height - self.prev_closest_zind_arr[rind] - 1)))
                self.file.write(struct.pack('1B', int(self.r[rind] + 23.5)))
                self.file.write(struct.pack('1B', int(0x00)))
                self.file.write(struct.pack('1B', int(0x00)))
                self.file.write(struct.pack('1B', int(0x00)))

                self.file.write(struct.pack('1B', int(self.height - closest_zind_arr[rind] - 1)))
                self.file.write(struct.pack('1B', int(self.r[rind] + 23.5)))
                self.file.write(struct.pack('1B', int(0xFF)))
                self.file.write(struct.pack('1B', int(0xFF)))
                self.file.write(struct.pack('1B', int(0xFF)))
        
        self.prev_closest_zind_arr = closest_zind_arr

        i = 0
        for t in self.t:
            x = self.r * np.cos(t)
            y = self.r * np.sin(t)
            for index, z in enumerate(self.z):
                points = np.vstack((x, y, z*np.ones_like(x)))
                # color = np.abs(self.r) / np.max(np.abs(self.r))
                # color /= self.u
                color = sinc[index, :]
                colors = np.vstack((color, color, color, np.ones_like(color)))
                self.traces[i].setData(pos=points.T, color=colors.T)
                i += 1
        self.savepng()
        print("update %d" % self.image_index)


    def animation(self):
        self.timer.start(15)
        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer()
    v.animation()
