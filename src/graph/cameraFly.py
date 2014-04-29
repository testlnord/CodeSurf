from math import pi, sin, cos

from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from panda3d.core import Vec3, Vec4, Point3, VBase3
from panda3d.core import LineSegs
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens

class GTriangle:
    def __init__(self, render, x, y, z):
        format=GeomVertexFormat.getV3n3cpt2()
        vdata=GeomVertexData('stuff', format, Geom.UHDynamic)
        vertex=GeomVertexWriter(vdata, 'vertex')
        normal=GeomVertexWriter(vdata, 'normal')
        color=GeomVertexWriter(vdata, 'color')
        texcoord=GeomVertexWriter(vdata, 'texcoord')
        vertex.addData3f(x-1, y+1, z-1)
        vertex.addData3f(x+1, y-1, z-1)
        vertex.addData3f(x, y, z+1)
        color.addData4f(1.0,0.0,0.0,1.0)
        color.addData4f(0.0,1.0,0.0,1.0)
        color.addData4f(0.0,0.0,1.0,1.0)
        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        tri1 = GeomTriangles(Geom.UHDynamic)
        tri1.addVertex(0)
        tri1.addVertex(1)
        tri1.addVertex(2)
        tri1.closePrimitive()
        geom = Geom(vdata)
        geom.addPrimitive(tri1)

        snode = GeomNode('node1')
        snode.addGeom(geom)
        result = render.attachNewNode(snode)
        result.setTwoSided(True)


class MyApp(ShowBase):
    def __init__(self, lines):
        ShowBase.__init__(self)
        
        self.trajectory = []
        self.currentTarget = 0

        self.cameraSpeed = 1
        self.cameraRotationSpeed = 5

        self.trajectory.append(Vec3(0, -120, 0));
        gt = GTriangle(self.render, 0, -120, 0)

        for line in lines:
            linesegs = LineSegs("lines")
            linesegs.setColor(1, 0.5, 1, 1)
            ((x1, y1, z1), (x2, y2, z2)) = line
            gt = GTriangle(self.render, x1, y1, z1)
            self.trajectory.append(Vec3(x1, y1, z1 + 1));

            linesegs.drawTo(x1, y1, z1)
            linesegs.drawTo(x2, y2, z2)
            node = linesegs.create(False)
            nodePath = render.attachNewNode(node)

        ((x1, y1, z1), (x2, y2, z2)) = lines[len(lines) - 1]
        gt = GTriangle(self.render, x2, y2, z2)
        self.trajectory.append(Vec3(x2, y2, z2 + 1));

        # Disable the camera trackball controls.
        self.disableMouse()
        self.taskMgr.add(self.moveCameraTask, "MoveCameraTask")

    # Define a procedure to move the camera.
    def moveCameraTask(self, task):
        (x,y,z) = (self.trajectory[self.currentTarget].getX(), self.trajectory[self.currentTarget].getY(), self.trajectory[self.currentTarget].getZ())
        
        currentRotation = VBase3(self.camera.getHpr())
        #self.camera.lookAt(x, y, z)
        self.camera.headsUp(x, y, z);
        desiredRotation = VBase3(self.camera.getHpr())
        dv = desiredRotation - currentRotation

        if dv.length() > self.cameraRotationSpeed:
            dv.normalize()
            currentRotation = currentRotation + dv * self.cameraRotationSpeed
        else:
            currentRotation = desiredRotation
        self.camera.setHpr(currentRotation)

        currentPosition = VBase3(self.camera.getPos())
        desiredPosition = VBase3(self.trajectory[self.currentTarget])
        dv = desiredPosition - currentPosition

        if dv.length() < self.cameraSpeed:
            currentPosition = desiredPosition
            self.currentTarget += 1
            if(self.currentTarget == len(self.trajectory)):
                self.currentTarget = 0
        else:
            dv.normalize()
            currentPosition = currentPosition + dv * self.cameraSpeed

        self.camera.setPos(currentPosition)
        return Task.cont

def drawLines(lines):
    app = MyApp(lines)
    app.run()

if __name__ == '__main__':
    points = [(0, 0, 0), (70, 70, 5), (-70, 70, -10), (90, -70, 0), (-20, 80, 10)]
    lines = []

    for i in range(len(points) - 1):
        lines.append((points[i], points[i+1]))

    drawLines(lines)