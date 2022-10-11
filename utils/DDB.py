import trimesh
import plyfile
import time
import json
import os

import numpy as np
from plyfile import PlyData, PlyElement
from utils import generatePC
from utils import genCam

import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
        self.cam = Obj(camPos) # 'camera' Obj class
        self.objects = [] # list of 'object' Obj classes
        
        for key in objPoses.keys():
            self.objects.append(Obj(objPoses[key]))

        cam_x, cam_y, cam_z = self.cam.getCart()
        
        # Set object's distance and angle
        for i in range(len(objPoses.keys())):
            obj_x, obj_y, obj_z = self.objects[i].getCart()
            self.objects[i].setDist(np.sqrt((obj_x - cam_x) ** 2 + (obj_y - cam_y) ** 2))
            self.objects[i].setAng(np.arctan2(obj_y - cam_y, obj_x - cam_x))
    
    def Distance(self, obj_index=None):
        #============================================================
        # Get distance (list) of object(s) from camera
        # obj_index : 1, 2, 3, ...
        # if obj_index is None, then the dictionary of distances will be returned.
        #============================================================
        if obj_index == None:
            distances = {}
            for i in range(len(self.objects)):
                distances.update({int(i) : self.objects[i].getDist()})
            return distances
        else:
            index = obj_index - 1
            return self.objects[index].getDist()
    
    def Direction(self, obj_index=None):
        #============================================================
        # Get direction (list) of object(s) from camera
        # obj_index : 1, 2, 3, ...
        # if obj_index is None, then the dictionary of directions will be returned.
        #============================================================
        if obj_index == None:
            angles = {}
            for i in range(len(self.objects)):
                angles.update({int(i) : self.objects[i].getAng()})
            return angles
        else:
            index = obj_index - 1
            return self.objects[index].getAng()
    
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

#=========================================================================
# visualization
#=========================================================================
def visualize(obj_to_pc, cameraObj, objectObjs):
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(projection='3d')
    
    # point cloud (obj2pc)
    pc_x = []
    pc_y = []
    pc_z = []
    for key in obj_to_pc.keys():
        pc_x.extend(obj_to_pc[key][:,0])
        pc_y.extend(obj_to_pc[key][:,1])
        pc_z.extend(obj_to_pc[key][:,2])
    ax.scatter(pc_x, pc_y, pc_z, c='r', marker='o', s=1)
    
    # camera (an instance)
    cam_x, cam_y, cam_z = cameraObj.getCart()
    ax.scatter(cam_x, cam_y, cam_z, c='y', marker='s', s=100)
    
    # objects (dictionary including all object instances)
    obj_x = []
    obj_y = []
    obj_z = []
    
    for key in objectObjs.keys():
        obj_x.extend([objectObjs[key].getCart()[0]])
        obj_y.extend([objectObjs[key].getCart()[1]])
        obj_z.extend([objectObjs[key].getCart()[2]])
        ax.scatter(objectObjs[key].getCart()[0], objectObjs[key].getCart()[1],
                   objectObjs[key].getCart()[2], c='b', marker='o', s=50)
        ax.text(objectObjs[key].getCart()[0], objectObjs[key].getCart()[1],
                   objectObjs[key].getCart()[2], "object{}".format(key), color='k')
    
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    
    plt.savefig("/root/PC2ERP/pointcloud_visualization/pcViz.png")

    # Rotate the axes and save figs
    azimuth = 0
    for i in range(8):
        angle = 45 * (i - 4) # -180 ~ 180
        ax.view_init(45, angle)
        
        save_path = "/root/PC2ERP/pointcloud_visualization/pcViz{}.png".format(angle)
        plt.savefig(save_path)

def extract_ddb(scan_id, viz=False):
    #============================================================
    # Extract the objects' distance, direction and splitted bins
    # Get scene mesh and scene graph data and gives some ERP
    # You should import 'trimesh', 'plyfile'
    # Args:
    #     scan_id : index of scans (default: all scans → 추후에 추가)
    #     data_path : root directory path of mesh data (.ply) and graph data (.json)
    #     iterations
    #     cam_pos : coordinate of camera
    #     ray_comps : components of ray
    # You should import 'trimesh'
    #============================================================
    start = time.time()
    
    #============================================================
    # Load the scene graph data
    #============================================================
    
    # scene mesh
    filename = '/root/dev/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)
    mesh = trimesh.load_mesh(filename)
    
    with open('/root/dev/3DSSG/objects.json', 'r') as ro:
        data_obj = json.load(ro)
    # with open('/root/dev/3DSSG/relationships.json', 'r') as rr:
    #     data_rel = json.load(rr)
    
    # objects
    for scan in data_obj['scans']:
        if scan_id == scan['scan']:
            objects = scan['objects']
    
    # relationships
    # for scan in data_rel['scans']:
    #     if scan_id == scan['scan']:
    #         relationships = scan['relationships']
    
    # print('==============================================')
    # print('Data paths')
    # print('Object data path: {}'.format('arg로 추가'))
    # print('Relationship data path: {}'.format('arg로 추가'))
    
    #============================================================
    # Variables
    #============================================================
    # output ERP size
    # width = 1024//2
    # height = 512//2
    
    # semantic informations
    plydata = PlyData.read(filename)
    
    # Region to sample a random camera pos
    point_cloud = generatePC.get_pc(scan_id)
    seg2pc = generatePC.get_seg2pc(scan_id, point_cloud)
    obj2pc = generatePC.get_obj2pc(scan_id, seg2pc)
    
    # directory to save
    save_path = '/root/dev/3DSSG/new_objects.json'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    #=========================================================================
    # get the camera position and objects' positions
    #=========================================================================
    cam = Obj(genCam.rand_cam(filename, point_cloud, obj2pc))
    print('Position of camera: ', cam.getCart())
    obj_poses = generatePC.obj_pos(obj2pc)
    objs = {}

    for key in obj2pc.keys():
        objs.update({int(key) : Obj(obj_poses[key])})
        print('Position of {}th object: {}'.format(key, objs[key].getCart()))
    
    #=========================================================================
    # with BEV class
    #=========================================================================
    bev = BEV(cam.getCart(), obj_poses)
    
    # get the distances and directions
    distances = bev.Distance()
    print('Disatnces of each objects: {}'.format(distances))
    directions = bev.Direction()
    print('Directions of each objects: {}'.format(directions))
    
    #=========================================================================
    # visualization
    #=========================================================================
    # fig = plt.figure(figsize=(12, 12))
    # ax = fig.add_subplot(projection='3d')
    
    # # point cloud (obj2pc)
    # pc_x = []
    # pc_y = []
    # pc_z = []
    # for key in obj2pc.keys():
    #     pc_x.extend(obj2pc[key][:,0])
    #     pc_y.extend(obj2pc[key][:,1])
    #     pc_z.extend(obj2pc[key][:,2])
    # ax.scatter(pc_x, pc_y, pc_z, c='r', marker='o', s=1)
    
    # # camera
    # cam_x, cam_y, cam_z = cam.getCart()
    # ax.scatter(cam_x, cam_y, cam_z, c='y', marker='s', s=100)
    
    # # objects
    # obj_x = []
    # obj_y = []
    # obj_z = []
    
    # for key in objs.keys():
    #     obj_x.extend([objs[key].getCart()[0]])
    #     obj_y.extend([objs[key].getCart()[1]])
    #     obj_z.extend([objs[key].getCart()[2]])
    # ax.scatter(obj_x, obj_y, obj_z, c='b', marker='o', s=50)
        
    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')

    # plt.show()
    if viz:
        visualize(obj2pc, cam, objs)
    
    