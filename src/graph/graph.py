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
import sys, os


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

    res.look_at(xn,yn,zn)
    res.set_pos(xc,yc,zc)
    return res


def drawLines(list1):
    title = OnscreenText(text="Code visualisation",
                         style=1, fg=(1, 1, 1, 1),
                         pos=(-0.2, 0.9), scale=.07)

    base.disableMouse()
    base.camera.setPos(0, -50, 0)
    base.oobe()

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
        render.attachNewNode(makeArc(x1,y1,z1,x2,y2,z2).node())
    run()


if __name__ == '__main__':
    points = [(0, 0, 10), (10, 10, 10), (-10, 10, -10), (14, -10, -5)]
    lines = []

    for i in range(len(points) - 1):
        lines.append((points[i], points[i + 1]))

    drawLines(lines)