from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec4, Vec3
from panda3d.core import *
from direct.interval.LerpInterval import *
from direct.showbase import DirectObject
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from AccelerometerReadingAsAClass import SerialData
import math

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.serialPort = SerialData()
        self.cube = loader.loadModel("panda")
        self.cube.reparentTo(self.render)
        self.cube.setPos(0.8, 0.0, 0.5)
        self.cube.setScale(0.35)
        self.handle = NodePath("temp")
        self.handle.reparentTo(self.render)
        self.handle.setPos(0.8, -15.0, 3.0)
        self.camera.reparentTo(self.handle)
        self.camera.setPos(0.0, -20.0, 10.0)
        self.camera.lookAt(0.0, 0.0, -20.0)
        self.spinUp = True
        self.updateTask = taskMgr.add(self.update, "update")
        self.text = TextNode('node name')
        self.textNodePath = aspect2d.attachNewNode(self.text)
        self.textNodePath.setScale(0.07)
        self.textNodePath.setPos(-0.175, 0.0, 0.75)
        self.text.font = loader.loadFont('THB_____.ttf')
        taskMgr.doMethodLater(0.4, self.updateText, 'Updating Text')
        self.angularSpeed = 6
        self.cube.setHpr(0,180,0)

    def det_direction_of_rotation(self, angle):
        if angle % 360 > 180:
            return 1
        else:
            return -1

    def updateText(self, task):
        self.serialPort.ser.open()
        self.serialPort.getSensorData()
        self.serialPort.ser.close()
        self.text.setText("%s"%self.serialPort.output)
        return Task.again

    def update(self, task):
        keypress = base.mouseWatcherNode.is_button_down
        angularSpeed = 6
        turn = 0
        if self.serialPort.z > 8.0:
            if self.cube.getP() % 360 != 0:
                if self.cube.getP() < 0:
                    self.cube.setHpr(0, self.cube.getP() + self.angularSpeed, 0)
                else:
                    self.cube.setHpr(0, self.cube.getP() - self.angularSpeed, 0)
            if self.cube.getR() != 0:
                if self.cube.getR() > 0:
                    self.cube.setR(self.cube.getR() - self.angularSpeed)
                else:
                    self.cube.setR(self.cube.getR() + self.angularSpeed)
        elif self.serialPort.z < -8.0 :
            if self.cube.getP() != 180:
                self.cube.setHpr(0, self.cube.getP() + self.angularSpeed, 0)
        elif self.serialPort.x > 6.0:
            if self.cube.getR() % 360 != 270:
                self.cube.setHpr(0, 0, self.cube.getR() - self.angularSpeed)
        elif self.serialPort.x < -6.0:
            if self.cube.getR() % 360 != 90:
                self.cube.setHpr(0, 0, self.cube.getR() + self.angularSpeed)
        elif self.serialPort.y > 6.0:
            if self.cube.getP() != -90:
                self.cube.setHpr(0, self.cube.getP() - self.angularSpeed, 0)
        elif self.serialPort.y < -6.0:
            if self.cube.getP() % 360 != 90:
                self.cube.setHpr(0, self.cube.getP() + self.angularSpeed, 0)

        return task.cont


game = Game()
game.run()
