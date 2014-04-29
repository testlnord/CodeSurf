
from panda3d.core import *

def makeCircle(xc, yc, zc, xn, yn, zn):
    m = loader.loadModel("models/circle.egg")
    m.setScale(0.01)
    m.setPos(xc, yc, zc)
    m.lookAt(xn, yn, zn)
    return m
