from math import pi, sin, cos

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *
from numpy import deg2rad

from hashing import *
import math

import time
import sys, os
from src.graph import primitives

cameraSpeed = 0.05
cameraRotationSpeed = 3
cameraRotationSpeedEpsilon = 2


def makeTorus(xc, yc, zc, xn, yn, zn):
    m = loader.loadModel("models/Torus.egg")
    m.set_pos(xc, yc, zc)

    m.look_at(xn, yn, zn)
    m.setHpr(m, Vec3(90, 0, 90))

    return m


def makeTeleport(xc, yc, zc, xn, yn, zn):
    m = makeTorus(xc, yc, zc, xn, yn, zn)
    m.setColor(0, 1,0 ,1)
    c = loader.loadModel("models/circle.egg")
    c.setTransparency(TransparencyAttrib.M_alpha)

    c.set_pos(xc, yc, zc)
    c.look_at(xn, yn, zn)
    c.setHpr(c, Vec3(90, 0, 90))
    c.setColor(0.5,0,0,0.5)
    c.setScale(m, 0.35)
    return m,c


def makeArc(xc, yc, zc, xn, yn, zn, angleDegrees=360, numSteps=16):
    ls = LineSegs()

    angleRadians = deg2rad(angleDegrees)

    for i in range(numSteps + 1):
        a = angleRadians * i / numSteps

        y = math.sin(a)
        x = math.cos(a)

        ls.drawTo(x, 0, y)

    node = ls.create()
    res = NodePath(node)

    res.set_pos(xc, yc, zc)
    res.look_at(xn, yn, zn)
    return res


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.trajectory = []
        self.currentTarget = 0

        self.setBackgroundColor(0, 0, 0.1)
        self.render.setAntialias(AntialiasAttrib.MPolygon)

        self.cameraSpeed = cameraSpeed
        self.cameraRotationSpeed = cameraRotationSpeed
        self.cameraRotationSpeedEpsilon = cameraRotationSpeedEpsilon

        self.camLens.setNear(0.01)

        self.disableMouse()
        self.taskMgr.add(self.moveCameraTask, "MoveCameraTask")

        title = OnscreenText(text="Code visualisation",
                     style=1, fg=(1, 1, 1, 1),
                     pos=(-0.2, 0.9), scale=.07)


    def addLines(self, lines, teleports):
        for line in lines:
            linesegs = LineSegs("lines")
            linesegs.setColor(1, 0.5, 1, 1)
            ((x1, y1, z1), (x2, y2, z2)) = line
            linesegs.drawTo(x1, y1, z1)
            linesegs.drawTo(x2, y2, z2)
            node = linesegs.create(False)
            nodePath = self.render.attachNewNode(node)
            self.render.attachNewNode(primitives.makeCircle(x1,y1,z1,x2,y2,z2).node())
        for teleport in teleports:
            (x1,y1,z1) = teleport.pos
            (x2,y2,z2) = teleport.orient
            m,c = makeTeleport(x1, y1, z1, x2, y2, z2)
            m.reparentTo(self.render)
            c.reparentTo(self.render)
        mysh = loader.loadShader("src/shaders/inkGen.sha")
        #self.render.setShader(mysh)
        #self.render.setShaderInput("separation", Vec4(0.001, 0, 0.001,0))
        #self.render.setShaderInput("cutoff", Vec4(0.3, 0.3,0.3,0.3))

    def setTrajectory(self, trajectory):
        self.trajectory = trajectory
        for obj in trajectory:
            (x,y,z) = obj.coord
            obj.coord = (x,y,z+0.05)
        self.currentTarget = 0

    def aimToNextTarget(self):
        self.currentTarget += 1
        if self.currentTarget == len(self.trajectory):
            self.currentTarget = 0
            print "END OF PROGRAM, START AGAIN"

    def teleportToNext(self):
        print "Teleport to next"
        (x,y,z) = self.trajectory[self.currentTarget].coord
        self.camera.setPos(x, y, z)
        self.aimToNextTarget()

        (x,y,z) = self.trajectory[self.currentTarget].coord
        self.camera.lookAt(x, y, z)

        (r, g, b) = getColor(self.trajectory[self.currentTarget].name)
        self.setBackgroundColor(r*0.2, g*0.2, b*0.2 )


    def moveCameraTask(self, task):
        if self.trajectory[self.currentTarget].t == True:
            self.teleportToNext()
            return Task.cont

        #MOVE
        self.cameraSpeed = cameraSpeed

        (x,y,z) = self.trajectory[self.currentTarget].coord
        currentPosition = VBase3(self.camera.getPos())
        desiredPosition = VBase3(x, y, z)
        dv = desiredPosition - currentPosition

        while dv.length() < self.cameraSpeed:
            self.cameraSpeed -= dv.length()
            self.camera.setPos(desiredPosition)
            self.aimToNextTarget()
            if self.trajectory[self.currentTarget].t == True:
                self.teleportToNext()
                return Task.cont
            (x,y,z) = self.trajectory[self.currentTarget].coord
            currentPosition = VBase3(self.camera.getPos())
            desiredPosition = VBase3(x, y, z)
            dv = desiredPosition - currentPosition

        dv.normalize()
        currentPosition += dv * self.cameraSpeed
        self.camera.setPos(currentPosition)

        #ROTATE
        (x, y, z) = self.trajectory[self.currentTarget].coord
        (x2, y2, z2) = (x, y, z)

        #if (self.currentTarget + 1 < len(self.trajectory)) and (self.trajectory[self.currentTarget+1].t == False):
        #    (x2, y2, z2) = self.trajectory[self.currentTarget + 1].coord

        currentRotation = VBase3(self.camera.getHpr())
        self.camera.lookAt(x, y, z)
        #self.camera.lookAt((x+x2)*0.5, (y+y2)*0.5, (z+z2)*0.5)
        desiredRotation = VBase3(self.camera.getHpr())
        dv = desiredRotation - currentRotation

        if dv.length() > self.cameraRotationSpeedEpsilon:
            if dv.length() > self.cameraRotationSpeed:
                dv.normalize()
                currentRotation = currentRotation + dv * self.cameraRotationSpeed
            else:
                pass

        self.camera.setHpr(currentRotation)

        return Task.cont


class Data:
    pass

if __name__ == '__main__':
    points = [(0, 0, 0), (70, 70, 5), (-70, 70, -10), (90, -70, 0), (-20, 80, 10), (0, -100, 0)]
    lines = []
    traj = []

    for i in range(len(points) - 1):
        lines.append((points[i], points[i + 1]))

    for point in points:
        obj = Data()
        obj.coord = (point[0], point[1], point[2] + 1)
        obj.t = False
        obj.v = False
        obj.vrs = None
        if(point[1] == -100):
            obj.t = True
        traj.append(obj)

    app = App()
    app.addLines(lines)
    app.setTrajectory(traj)
    app.run()