import trimesh
import plyfile
import time
import json
import os

import numpy as np
from plyfile import PlyData, PlyElement
from utils import generatePC
from utils import genCam
from utils import Object # class
from utils import BirdEyeView # class

import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

def extract_ddb(scan_id, overwrite=True, viz=False, rand_seed=None):
    #============================================================
    # Extract the objects' distance, direction and splitted bins (ddb)
    # Get scene mesh and scene graph data and creates new_objects.json file (graph data)
    # Args:
    #     scan_id : list of scans
    #     overwrite : if there already exists any configuration(ddb)
    #         , overwrite(true) or skip(false) for the given scan id
    #     viz : visualize(true) or not(false)
    #     rand_seed : random seed for generating camera
    #============================================================
    start = time.time()
    print("============================================================================")
    
    #============================================================
    # Load the scene graph data
    #============================================================
    # scene mesh
    filename = '/root/dev/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)
    mesh = trimesh.load_mesh(filename)
    
    with open('/root/dev/3DSSG/new_objects.json', 'r') as ro:
        data_obj = json.load(ro)
    
    # objects
    for scan in data_obj['scans']:
        if scan_id == scan['scan']:
            objects = scan['objects']
    
    #============================================================
    # Variables
    #============================================================
    # semantic informations
    plydata = PlyData.read(filename)
    
    # Region to sample a random camera pos
    point_cloud = generatePC.get_pc(scan_id)
    seg2pc = generatePC.get_seg2pc(scan_id, point_cloud)
    obj2pc = generatePC.get_obj2pc(scan_id, seg2pc)
    
    #=========================================================================
    # get the camera position and objects' positions
    #=========================================================================
    cam = Object.Obj(genCam.rand_cam(filename, point_cloud, obj2pc, rand_seed))
    print('Position of camera: ', cam.getCart())
    obj_poses = generatePC.obj_pos(obj2pc)
    objs = {}

    for key in obj2pc.keys():
        objs.update({int(key) : Object.Obj(obj_poses[key])})
        print('Position of {}th object: {}'.format(key, objs[key].getCart()))
    
    #=========================================================================
    # with BEV class
    #=========================================================================
    bev = BirdEyeView.BEV(cam.getCart(), obj_poses)
    
    # get the distances and directions
    distances = bev.Distance()
    directions = bev.Direction()
    print('Disatnces of each objects: {}'.format(distances))
    print('Directions of each objects: {}'.format(directions))
    print()
    
    # visualization
    if viz:
        visualize(obj2pc, cam, objs)
    
    #=========================================================================
    # new json file with distances and directions
    #=========================================================================
    print("new objects.json file for scan id {}...".format(scan_id))
    new_obj = data_obj.copy() # shallow copy
    
    for i in range(len(new_obj["scans"])):
        if new_obj["scans"][i]["scan"] == scan_id:
            if "camera" in new_obj["scans"][i]:
                print("The ddb information already exists!")
                if overwrite:
                    print("overwriting...")
                    for j in range(len(new_obj["scans"][i]["objects"])): # for the graph data
                        for k in bev.objects.keys(): # for each object id in the scene
                            if int(new_obj["scans"][i]["objects"][j]["id"]) == k:
                                new_obj["scans"][i]["objects"][j]["attributes"].update({"distance" : bev.Distance()[k]})
                                new_obj["scans"][i]["objects"][j]["attributes"].update({"direction" : bev.Direction()[k]})
                                new_obj["scans"][i].update({"camera" : {"location" : cam.getCart()}})
                else:
                    print("didn't create any new configurations because overwrite == False")
            else:
                print("adding configurations...")
                for j in range(len(new_obj["scans"][i]["objects"])): # for the graph data
                    for k in bev.objects.keys(): # for each object id in the scene
                        if int(new_obj["scans"][i]["objects"][j]["id"]) == k:
                            new_obj["scans"][i]["objects"][j]["attributes"].update({"distance" : bev.Distance()[k]})
                            new_obj["scans"][i]["objects"][j]["attributes"].update({"direction" : bev.Direction()[k]})
                            new_obj["scans"][i].update({"camera" : {"location" : cam.getCart()}})

    # save new json file (object)
    save_path = '/root/dev/3DSSG/new_objects.json'
    with open(save_path, "w") as f:
        json.dump(new_obj, f, indent=4)
    print('new configurations added for scan id "{}" for {} sec'.format(scan_id, time.time() - start))
    print("============================================================================")