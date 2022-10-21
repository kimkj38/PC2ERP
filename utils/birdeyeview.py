import numpy as np
from utils import Object

#=========================================================================
# class BEV
# bird-eye-view version of the scene (with the class 'Obj')
#  Args:
#     camPos : (x_coordinate, y_coordinate, z_coordinate) of Camera
#     objPoses : dictionary datatype
#         key : object id
#         value : list of coordinates of the object's center
#=========================================================================
class BEV:
    def __init__(self, camPos, objPoses):
        self.cam = Object.Obj(camPos) # 'camera' Obj class
        self.objects = {} # dictionary of 'object' Obj classes
        
        for key in objPoses.keys():
            self.objects.update({key : Object.Obj(objPoses[key])})

        cam_x, cam_y, cam_z = self.cam.getCart()
        
        # Set object's distance and angle
        for key in self.objects.keys():
            obj_x, obj_y, obj_z = self.objects[key].getCart()
            self.objects[key].setDist(np.sqrt((obj_x - cam_x) ** 2 + (obj_y - cam_y) ** 2))
            self.objects[key].setAng(np.arctan2(obj_y - cam_y, obj_x - cam_x))
    
    def Distance(self, obj_index=None):
        #============================================================
        # Get distance (list) of object(s) from camera
        # obj_index : 1, 2, 3, ...
        # if obj_index is None, then the dictionary of distances will be returned.
        #============================================================
        if obj_index == None:
            distances = {}
            for key in self.objects.keys():
                distances.update({key : self.objects[key].getDist()})
            return distances
        else:
            return self.objects[obj_index].getDist()
    
    def Direction(self, obj_index=None):
        #============================================================
        # Get direction (list) of object(s) from camera
        # obj_index : 1, 2, 3, ...
        # if obj_index is None, then the dictionary of directions will be returned.
        #============================================================
        if obj_index == None:
            angles = {}
            for key in self.objects.keys():
                angles.update({key : self.objects[key].getAng()})
            return angles
        else:
            return self.objects[obj_index].getAng()
    
    #=========================================================================
    # multi cylindrical image
    # split the distance along the bins in bird eye view
    #=========================================================================
#     def split(self, height, width, obj_distances, num_bin, dstep):
#         print('splitting by distances from the camera...')
#         x = self.obj_x - self.cam_x
#         y = self.obj_y - self.cam_y

#         mci = np.zeros(height, width, num_bin + 1) # 3rd index : bins (0th bin : camera itself)
#         for i in range(len(obj_distances)):
#             if num_bin * dstep < obj_distances[i]: # if the distance value is greater than last bin, project it to the last bin
#                mci[x, y, ] = num_bin * dstep
            
#             else:
#                 diff = obj_distances[i] % dstep
#                 if diff == 0:
#                     splitted_dist[i] = obj_distances[i]
#                 elif diff > dstep / 2:
#                     p = 