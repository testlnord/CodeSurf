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

cameraSpeed = 0.05
cameraRotationSpeed = 2
cameraRotationSpeedEpsilon = 4


def makeTorus(xc, yc, zc, xn, yn, zn):
    m = loader.loadModel("models/Torus.egg")
    m.set_pos(xc, yc, zc)

    m.look_at(xn, yn, zn)
    m.setHpr(m, Vec3(90, 0, 90))
    m.setColor(0, 1,0 ,1)
    return m


def makeTeleport(xc, yc, zc, xn, yn, zn):
    m = makeTorus(xc, yc, zc, xn, yn, zn)
    c = loader.loadModel("models/circle.egg")
    c.set_pos(xc, yc, zc)
    c.look_at(xn, yn, zn)
    c.setHpr(c, Vec3(90, 0, 90))
    c.setColor(0.5,0,0,0.001)
    c.setScale(m, 0.01)
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


class MockObject:
    def __init__(self):
        self.pos = (0, 0, 0)
        self.hpr = (0, 0, 0)

    def getPos(self):
        return self.pos

    def getHpr(self):
        return self.hpr

    def setPos(self, pos1):
        self.pos = pos1

    def setHpr(self, hpr1):
        self.hpr = hpr1


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.trajectory = []
        self.currentTarget = 0

        self.followObject1 = MockObject()
        #self.followObject1.setPos()
        #myFog = Fog("Fog")
        #myFog.setColor(0,0.05,0.05)
        #myFog.setExpDensity(0.5)
        #self.render.setFog(myFog)

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

        #b=OnscreenImage(parent=self.render, image="stuff.jpg")
        #self.camera.node().getDisplayRegion(0).setSort(20)


    def addLines(self, lines, teleports):
        for line in lines:
            linesegs = LineSegs("lines")
            linesegs.setColor(1, 0.5, 1, 1)
            ((x1, y1, z1), (x2, y2, z2)) = line
            linesegs.drawTo(x1, y1, z1)
            linesegs.drawTo(x2, y2, z2)
            node = linesegs.create(False)
            nodePath = self.render.attachNewNode(node)
            self.render.attachNewNode(makeArc(x1,y1,z1,x2,y2,z2).node())
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
            #obj.coord[2] += 1
            (x,y,z) = obj.coord
            obj.coord = (x,y,z+0.05)
        self.currentTarget = 0

    def moveToNextTarget(self):
        self.currentTarget += 1
        if(self.currentTarget == len(self.trajectory)):
            self.currentTarget = 0
            print "END OF PROGRAM, START AGAIN"

    def updateObjects(self):
        pass

    def teleportToNext(self):
        self.moveToNextTarget()

        (x,y,z) = (self.trajectory[self.currentTarget].coord[0], self.trajectory[self.currentTarget].coord[1], self.trajectory[self.currentTarget].coord[2])
        print "Teleport to next"
        self.camera.setPos(VBase3(x, y, z))

        self.moveToNextTarget()

        (r, g, b) = getColor(self.trajectory[self.currentTarget].name)
        self.setBackgroundColor(r*0.2, g*0.2, b*0.2 )

        (x,y,z) = (self.trajectory[self.currentTarget].coord[0], self.trajectory[self.currentTarget].coord[1], self.trajectory[self.currentTarget].coord[2])
        self.camera.lookAt(x, y, z)


    def moveCameraTask(self, task):
        (x,y,z) = (self.trajectory[self.currentTarget].coord[0], self.trajectory[self.currentTarget].coord[1], self.trajectory[self.currentTarget].coord[2])
        (x2, y2, z2) = (x, y, z)

        if(self.currentTarget + 1 < len(self.trajectory)):
            (x2, y2, z2) = (self.trajectory[self.currentTarget+1].coord[0], self.trajectory[self.currentTarget+1].coord[1], self.trajectory[self.currentTarget+1].coord[2])

        if self.trajectory[self.currentTarget].t == True:
            #print "TELEPORT!!!"
            self.teleportToNext()
            return Task.cont

        currentRotation = VBase3(self.camera.getHpr())
        self.camera.lookAt((x+x2)*0.5, (y+y2)*0.5, (z+z2)*0.5 )
        #self.camera.lookAt((x+x2)*0.5, (y+y2)*0.5, (z+z2)*0.5 )
        #self.camera.headsUp(x, y, z)
        desiredRotation = VBase3(self.camera.getHpr())
        dv = desiredRotation - currentRotation

        if dv.length() > self.cameraRotationSpeed:
            dv.normalize()
            currentRotation = currentRotation + dv * self.cameraRotationSpeed
            #currentRotation = currentRotation + dv*self.cameraRotationSpeed
        else:
            pass
            #currentRotation = desiredRotation
        self.camera.setHpr(currentRotation)


        self.cameraSpeed = cameraSpeed

        currentPosition = VBase3(self.camera.getPos())
        desiredPosition = VBase3(x, y, z)
        dv = desiredPosition - currentPosition

        teleported = False
        while dv.length() < self.cameraSpeed:
            currentPosition = desiredPosition
            self.moveToNextTarget()
            if self.trajectory[self.currentTarget].t == True:
                self.teleportToNext()
                self.cameraSpeed = 0
                teleported = True
            else:
                self.cameraSpeed -= dv.length()

        if not teleported:
            pass
            dv.normalize()
            currentPosition = currentPosition + dv * self.cameraSpeed
            self.camera.setPos(currentPosition)

        """
        if dv.length() < self.cameraSpeed:
            currentPosition = desiredPosition
            self.moveToNextTarget()
        else:
            dv.normalize()
            currentPosition = currentPosition + dv * self.cameraSpeed
        """

        #self.camera.setPos(currentPosition)
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