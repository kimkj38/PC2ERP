import numpy as np

#=========================================================================
# class Obj
# Obj can be any object such as camera, chair, floor, wall etc.
# Args:
#     pos : object's center position (Cartesian Coordinate)
#=========================================================================
class Obj:
    def __init__(self, pos):
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.z_pos = pos[2]

    def getCart(self):
        return (self.x_pos, self.y_pos, self.z_pos)
    
    def getSphere(self):
        return cart2sph(self.x_pos, self.y_pos, self.z_pos)
    
    def getDist(self):
        return self.distance
    
    def getAng(self):
        return self.angle
    
    def setCart(self, x, y, z):
        self.x_pos = x
        self.y_pos = y
        self.z_pos = z
    
    def setDist(self, distance):
        self.distance = distance
    
    def setAng(self, angle):
        self.angle = angle
    
    def setBin(self, bev_bin):
        self.bev_bin = bev_bin
    
    #=========================================================================
    # cart2sph -> cartesian coordinates to sphere coordinates
    # sph2cart -> sphere coordinates to cartesian coordinates
    #=========================================================================
    def cart2sph(self, x, y, z):
        azimuth = np.arctan2(y, x) # theta
        elevation = np.arctan2(z, np.sqrt(x**2 + y**2)) # phi
        r = np.sqrt(x**2 + y**2 + z**2)
        return (r, azimuth, elevation)
    
    def sph2cart(self, r, azimuth, elevation): # r, theta, phi
        x = r * np.cos(elevation) * np.cos(azimuth)
        y = r * np.cos(elevation) * np.sin(azimuth)
        z = r * np.sin(elevation)
        return (x, y, z)