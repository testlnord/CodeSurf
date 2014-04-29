__author__ = 'icemore'

import random
import hashlib

def getColor(st):
    h = int(hashlib.sha1(st).hexdigest(), 16)
    #print st+"  "+str(h)
    #r = random.random()
    #g = random.random()
    #b = random.random()
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF

    return (r/255.0, g/255.0, b/255.0)
    #return (r, g, b)