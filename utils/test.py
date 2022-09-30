import trimesh
import rtree
import shapely
import random
import time
import os
import multiprocessing
import json

import numpy as np
import cv2
from plyfile import PlyData, PlyElement
import generatePC

def bin_ordering(scan_id):
    #============================================================
    # Ordering by splitting with bins
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
    # Load the data
    #============================================================
    
    # scene mesh
    filename = '/root/dev/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)
    # filename = '/root/dev/3RScan/09582223-e2c2-2de1-94b6-750684b4f80a/labels_instances_annotated_v2.ply' # 파일명에 . 들어가면 안됨...
    mesh = trimesh.load_mesh(filename)
    
    with open('/root/dev/3DSSG/objects.json', 'r') as ro:
        data_obj = json.load(ro)
    with open('/root/dev/3DSSG/relationships.json', 'r') as rr:
        data_rel = json.load(rr)
    
    for scan in data_obj['scans']:
        if scan_id == scan['scan']:
            objects = scan['objects']
    
    for scan in data_rel['scans']:
        if scan_id == scan['scan']:
            relationships = scan['relationships']
    
    #============================================================
    # Variables
    #============================================================
    # output ERP size
    width = 1024//2
    height = 512//2
    
    # semantic informations
    plydata = PlyData.read(filename)
    faces = plydata['face'].data['vertex_indices']
    vertices = plydata['vertex'].data
    
    # Region to sample a random camera pos
    point_cloud = generatePC.get_pc(scan_id)
    seg2pc = generatePC.get_seg2pc(scan_id, point_cloud)
    obj2pc = generatePC.get_obj2pc(scan_id, seg2pc)
    
    min_point = np.min(point_cloud, axis=0)
    max_point = np.max(point_cloud, axis=0)
    
    # floor vertices (object id of floor: 1)
    floor = obj2pc[1]
    
    # directory to save
    save_path = '/root/dev/3DSSG/new_objects.json'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    #============================================================
    # ray casting (cam pos 랜덤 생성하는 부분만 가져옴 -> 나중에 삭제)
    #============================================================
    # get random cam pos until it is on the floor
    floor_global_id = 0
    while floor_global_id != 188: # floor's global_id == 188
        print("==============================================")
        random_idx = random.randint(0, len(floor) - 1)
        cam_x = floor[random_idx][0]
        cam_y = floor[random_idx][1]
        cam_z = (min_point[2] + max_point[2]) / 2
        
        camray_direction = np.array([[0, 0, -1]]) # downward dir
        
        # get global id of the face which intersects first from camera with downward direction ray
        floor_id = mesh.ray.intersects_first(np.array([[cam_x, cam_y, cam_z]]), camray_direction)
        floor_vertex3 = faces[floor_id]
        floor_vertex = vertices[floor_vertex3[0][0]]
        
        floor_global_id = floor_vertex[7]
    
    print('Cam Pos: ({}, {}, {})'.format(cam_x, cam_y, cam_z))

if __name__=='__main__':
    scan_id = '09582223-e2c2-2de1-94b6-750684b4f80a'
    bin_ordering(scan_id)