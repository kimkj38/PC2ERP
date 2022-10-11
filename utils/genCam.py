import trimesh
import numpy as np
import random

from plyfile import PlyData, PlyElement

def rand_cam(ply_file, point_cloud, object_to_pc):
    #=========================================================================
    # Get random camera position until it is on the floor
    # Args:
    #     ply_file : path of the ply file
    #     point_cloud : point cloud data
    #     object_to_pc : points of objects
    #=========================================================================
    mesh = trimesh.load_mesh(ply_file)
    plydata = PlyData.read(ply_file)
    
    floor = object_to_pc[1] # object id of floor : 1
    
    faces = plydata['face'].data['vertex_indices']
    vertices = plydata['vertex'].data
    
    min_point = np.min(point_cloud, axis=0)
    max_point = np.max(point_cloud, axis=0)
    
    floor_global_id = 0
    while floor_global_id != 188: # floor global id == 188
        random_idx = random.randint(0, len(floor)-1)
        cam_x = floor[random_idx][0]
        cam_y = floor[random_idx][1]
        cam_z = (min_point[2]+max_point[2])/2

        camray_direction = np.array([[0,0,-1]]) # downward direction

        # get global id of face which intersets first from camera with downward direction ray
        floor_id = mesh.ray.intersects_first(np.array([[cam_x, cam_y, cam_z]]), camray_direction) 
        floor_vertex3 = faces[floor_id]
        floor_vertex = vertices[floor_vertex3[0][0]]

        floor_global_id = floor_vertex[7]
    
    # print("randomly generated camera's coordinate", (cam_x, cam_y, cam_z))
    
    return (cam_x, cam_y, cam_z)