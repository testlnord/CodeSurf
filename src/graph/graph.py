from direct.directbase import DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from numpy import deg2rad
import math
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import LineSegs, NodePath
import time
import sys, os


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

    res.look_at(xn, yn, zn)
    res.set_pos(xc, yc, zc)
    return res


class GTriangle:
    def __init__(self, x, y, z):
        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('stuff', format, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        vertex.addData3f(x - 1, y + 1, z - 1)
        vertex.addData3f(x + 1, y - 1, z - 1)
        vertex.addData3f(x, y, z + 1)
        color.addData4f(1.0, 0.0, 0.0, 1.0)
        color.addData4f(0.0, 1.0, 0.0, 1.0)
        color.addData4f(0.0, 0.0, 1.0, 1.0)
        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        tri1 = GeomTriangles(Geom.UHDynamic)
        tri1.addVertex(0)
        tri1.addVertex(1)
        tri1.addVertex(2)
        tri1.closePrimitive()
        self.geom = Geom(vdata)
        self.geom.addPrimitive(tri1)

        snode = GeomNode('node1')
        snode.addGeom(self.geom)
        result = render.attachNewNode(snode)
        result.setTwoSided(True)


def drawLines(list1):
    title = OnscreenText(text="Code visualisation",
                         style=1, fg=(1, 1, 1, 1),
                         pos=(-0.2, 0.9), scale=.07)

    rk = ReadKeys(0, -10, 0)

    slight = Spotlight('slight')
    slight.setColor(Vec4(1, 1, 1, 1))
    lens = PerspectiveLens()
    slight.setLens(lens)
    slnp = render.attachNewNode(slight)

    for line in list1:
        linesegs = LineSegs("lines")
        linesegs.setColor(1, 0.5, 1, 1)
        ((x1, y1, z1), (x2, y2, z2)) = line
        linesegs.drawTo(x1, y1, z1)
        linesegs.drawTo(x2, y2, z2)
        node = linesegs.create(False)
        nodePath = render.attachNewNode(node)

        p1 = GTriangle(x1, y1, z1);
        p2 = GTriangle(x2, y2, z2);

    run()

#sys.exit()


class ReadKeys(DirectObject):
    def __init__(self, x, y, z):
        DirectObject.__init__(self);

        base.disableMouse();

        self.v = 5;
        self.x = x
        self.y = y
        self.z = z

        self.moveCamera(0, 0, 0)

        self.accept('w', self.keyForwardDown)
        self.accept('w-up', self.keyForwardUp)

        self.accept('s', self.keyBackwardDown)
        self.accept('s-up', self.keyBackwardUp)

        self.accept('a', self.keyLeftDown)
        self.accept('a-up', self.keyLeftUp)

        self.accept('d', self.keyRightDown)
        self.accept('d-up', self.keyRightUp)

        self.accept('e', self.keyUpDown)
        self.accept('e-up', self.keyUpUp)

        self.accept('q', self.keyDownDown)
        self.accept('q-up', self.keyDownUp)

    def keyForwardDown(self):
        self.moveCamera(0, self.v, 0)

    def keyForwardUp(self):
        self.moveCamera(0, 0, 0)

    def keyBackwardDown(self):
        self.moveCamera(0, -self.v, 0)

    def keyBackwardUp(self):
        self.moveCamera(0, 0, 0)

    def keyUpDown(self):
        self.moveCamera(0, 0, self.v)

    def keyUpUp(self):
        self.moveCamera(0, 0, 0)

    def keyDownDown(self):
        self.moveCamera(0, 0, -self.v)

    def keyDownUp(self):
        self.moveCamera(0, 0, 0)

    def keyLeftDown(self):
        self.moveCamera(-self.v, 0, 0)

    def keyLeftUp(self):
        self.moveCamera(0, 0, 0)

    def keyRightDown(self):
        self.moveCamera(self.v, 0, 0)

    def keyRightUp(self):
        self.moveCamera(0, 0, 0)

    def moveCamera(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        camera.setPos(self.x, self.y, self.z)


if __name__ == '__main__':
    points = [(0, 0, 10), (10, 10, 10), (-10, 10, -10), (14, -10, -5)]
    lines = []

    for i in range(len(points) - 1):
        lines.append((points[i], points[i + 1]))

    drawLines(lines)
