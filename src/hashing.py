__author__ = 'icemore'

def getColor(str):
    h = hash(str)
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF

    return (r/255.0, g/255.0, b/255.0)