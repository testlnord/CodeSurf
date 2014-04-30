from IPython.lib import backgroundjobs
from math import pi, sin, cos

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup
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
cameraRotationChangeRatio = 0.75
cameraRotationChangeEpsilon = 1

def makeTorus(xc, yc, zc, xn, yn, zn):
    m = loader.loadModel("models/Torus.egg")
    m.set_pos(xc, yc, zc)

    m.look_at(xn, yn, zn)
    m.setHpr(m, Vec3(90, 0, 90))

    return m


def skyBox(camera):
    background = loader.loadModel("models/Square.egg")
    background.setPos(0,0,0)
    background.setHpr(0, 90, 0)
    background.setScale(3.0)
    mysh = Shader.load(Shader.SLGLSL, "src/shaders/def_sl_vertex.glsl","src/shaders/piu.glsl",
                       "src/shaders/def_sl_geom.glsl")
    background.setShader(mysh)
    background.setShaderInput("time", 0.00)
    background.setShaderInput("resolution", Vec2(800,800))
    background.setShaderInput("r",0.7)
    background.setShaderInput("g",0.7)
    background.setShaderInput("b",0.7)
    #background.setColor(1.0,0.0,0,1.0)
    background.setBin("background", 0)
    background.setDepthWrite(False)
    #background.setCompass()

    background.reparentTo(camera)
    return background

def makeTeleport(xc, yc, zc, xn, yn, zn, r, g, b):
    m = makeTorus(xc, yc, zc, xn, yn, zn)
    m.setColor(r*0.8, g*0.8,b*0.8 ,1)
    c = loader.loadModel("models/circle.egg")
    c.setTransparency(TransparencyAttrib.M_dual)


    mysh = Shader.load(Shader.SLGLSL, "src/shaders/def_sl_vertex.glsl","src/shaders/burl.glsl",
                       "src/shaders/def_sl_geom.glsl")
    c.setShader(mysh)
    time = random.random()*100
    c.setShaderInput("time", time)
    c.set_pos(xc, yc, zc)
    c.look_at(xn, yn, zn)
    c.setHpr(c, Vec3(90, 0, 90))

    c.setScale(m, 0.35)
    return m,c, time


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
        self.render.setAntialias(AntialiasAttrib.MPolygon)

        self.cameraSpeed = cameraSpeed
        self.cameraRotationSpeed = cameraRotationSpeed
        self.cameraRotationSpeedEpsilon = cameraRotationSpeedEpsilon
        self.cameraRotationChange = VBase3(0, 0, 0)
        self.cameraRotationChangeRatio = cameraRotationChangeRatio
        self.cameraRotationChangeEpsilon = cameraRotationChangeEpsilon

        self.camLens.setNear(0.01)

        self.disableMouse()
        self.taskMgr.add(self.updateObjects, "Update")

        self.setupLights()

        self.addParticles()

        self.title = OnscreenText(text="Code visualisation",
                     style=1, fg=(1, 1, 1, 1),
                     pos=(-0.2, 0.9), scale=.07)

        self.captionFunctionName = OnscreenText(text="Caption",
                     style=1, fg=(1, 1, 1, 1),
                     pos=(-1, 0.8), scale=.07, mayChange=True, align = TextNode.ALeft)

        self.captionVars = OnscreenText(text="local scope",
                     style=1, fg=(1, 1, 1, 1),
                     pos=(-1, 0.7), scale=.07, mayChange=True, align = TextNode.ALeft)

        self.taskMgr.add(self.moveCameraTask, "MoveCameraTask")
        #sky box
        self.skybox = skyBox(self.particleNodePath)



    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        #ambientLight.setColor(Vec4(.4, .4, .35, 1))
        ambientLight.setColor(Vec4(1, 1, 1, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))

        #dirty hack stuff
        self.teleports = []
        self.time = 0

    def addParticles(self):
        base.enableParticles()
        self.particles = ParticleEffect()
        self.particles.loadConfig(Filename('particles/one_zero.ptf'))

        self.particleNodePath = NodePath('gridnode')
        self.particleNodePath.reparentTo(self.camera)
        self.particleNodePath.setPos(0, 10, 0)
        self.particleNodePath.setHpr(0, 90, 0)

        self.particles.setPos(0, 0, 0)
        self.particles.setDepthTest(False)
        self.particles.start(self.particleNodePath)

    def updateParticles(self):
        pass

    def makeBillboard(self, coords, text):

        billboardNode = NodePath('billboardnode')
        billboardNode.reparentTo(self.render)
        (x,y,z) = coords
        billboardNode.setPos(x, y, z + 0.1)

        textNode = TextNode('node name')
        textNode.setText(text)
        textNode.setTextColor(1, 1, 1, 1)
        textNode.setCardColor(0, 0, 0, 0.3)
        textNode.setCardAsMargin(0.4, 0.4, 0.4, 0.4)
        textNode.setCardDecal(True)
        textNode.setWordwrap(15.0)
        textNode.setTabWidth(0.05)
        textNode.setAlign(TextNode.ACenter)
        textNode.setShadow(0.05, 0.05)
        textNode.setShadowColor(0, 0, 0, 1)

        cardMaker = CardMaker('cardmaker')
        card = NodePath(cardMaker.generate())
        tnp = card.attachNewNode(textNode)
        card.setEffect(DecalEffect.make())
        tnp.reparentTo(billboardNode)
        tnp.setPos(-0.004*textNode.getWidth(), 0, 0)
        tnp.setScale(0.05)
        billboardNode.setBillboardPointEye()

    def addLines(self, lines, teleports, instructions):
        for line in lines:
            linesegs = LineSegs("lines")
            linesegs.setColor(1, 0.5, 1, 1)
            ((x1, y1, z1), (x2, y2, z2)) = line
            linesegs.drawTo(x1, y1, z1)
            linesegs.drawTo(x2, y2, z2)
            node = linesegs.create(False)
            #nodePath = self.render.attachNewNode(node)
            self.render.attachNewNode(primitives.makeCircle(x1,y1,z1,x2,y2,z2).node())

        for teleport in teleports:
            (x1,y1,z1) = teleport.pos
            (x2,y2,z2) = teleport.orient
            (r, g, b) = getColor(teleport.to_fun)

            m,c,t = makeTeleport(x1, y1, z1, x2, y2, z2, r, g, b)
            m.reparentTo(self.render)
            self.teleports.append((c,t))
            c.reparentTo(self.render)

        for instruction in instructions:
            self.makeBillboard((instruction.x, instruction.y, instruction.z), instruction.text)

    def setTrajectory(self, trajectory):
        self.trajectory = trajectory
        for obj in trajectory:
            (x,y,z) = obj.coord
            obj.coord = (x,y,z+0.05)
        self.currentTarget = 0

    def updateCaptionFunctionName(self, text):
        self.captionFunctionName.setText("current function name: " + text)

    def updateCaptionVars(self, text):
        self.captionVars.setText("local Scope: " + text)

    def updateCaptions(self):
        self.updateCaptionFunctionName(self.trajectory[self.currentTarget].name)
        if self.trajectory[self.currentTarget].vrs is not None:
            self.updateCaptionVars(str(self.trajectory[self.currentTarget].vrs))

    def aimToNextTarget(self):
        self.updateCaptions()
        self.currentTarget += 1
        if self.currentTarget == len(self.trajectory):
            self.currentTarget = 0
            sys.exit(0)

    def updateObjects(self, task):
        for tel,t in self.teleports:

            tel.setShaderInput("time", t+self.time)
        self.skybox.setShaderInput("time", self.time)
        self.time+=0.1

        return task.again

    def teleportToNext(self):
        print "Teleport to next"
        (x,y,z) = self.trajectory[self.currentTarget].coord
        self.camera.setPos(x, y, z)
        self.aimToNextTarget()

        (x,y,z) = self.trajectory[self.currentTarget].coord
        self.camera.lookAt(x, y, z)

        (r, g, b) = getColor(self.trajectory[self.currentTarget].name)
        self.skybox.setShaderInput("r",r*0.7)
        self.skybox.setShaderInput("g",g*0.7)
        self.skybox.setShaderInput("b",b*0.7)


    def moveCameraTask(self, task):
        if self.currentTarget == 0:
            self.teleportToNext()
            return Task.cont

        self.updateCaptions()

        self.updateParticles()

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
                self.cameraSpeed = 0
                currentPosition = VBase3(self.camera.getPos())
                break
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

        if (self.currentTarget + 1 < len(self.trajectory)) and (self.trajectory[self.currentTarget+1].t == False):
            (x2, y2, z2) = self.trajectory[self.currentTarget + 1].coord

        oldRotation = VBase3(self.camera.getHpr())
        currentRotation = applyToVector(oldRotation, toPositiveAngle)
        oldRotation = currentRotation
        self.camera.lookAt(x, y, z)

        self.camera.lookAt((x+x2)*0.5, (y+y2)*0.5, (z+z2)*0.5)

        desiredRotation = applyToVector(VBase3(self.camera.getHpr()), toPositiveAngle)
        dv = desiredRotation - currentRotation
        delta = VBase3(0, 0, 0)

        if dv.length() > self.cameraRotationSpeedEpsilon:
            if dv.length() > self.cameraRotationSpeed:
                dv = applyToVector(dv, toSharpAngle)
                dv.normalize()
                #currentRotation = currentRotation + dv * self.cameraRotationSpeed
                delta = dv * self.cameraRotationSpeed
            else:
                pass

        self.cameraRotationChange = (self.cameraRotationChange + delta) * self.cameraRotationChangeRatio

        if self.cameraRotationChange.length() > self.cameraRotationChangeEpsilon:
            self.camera.setHpr(oldRotation + self.cameraRotationChange)

        return Task.cont

def applyToVector(vec, fun):
    return VBase3(fun(vec[0]), fun(vec[1]), fun(vec[2]))

def toPositiveAngle(angle):
    return (angle + 360.0001) % 360

def toSharpAngle(angle):
    if angle < 0:
        return angle if angle >= -180 else 360 + angle
    else:
        return angle if angle <= 180 else -360 + angle

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