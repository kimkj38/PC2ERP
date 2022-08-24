import trimesh
import rtree
import shapely
import numpy as np
import random
from generatePC import *

scan_id = "4fbad329-465b-2a5d-8401-a3f550ef3de5"
filename = "{}/labels.instances.annotated.v2.ply".format(scan_id)

# scene mesh
mesh = trimesh.load_mesh(filename)

# Output ERP size
width = 1024
height = 512

# Region to sample a random camera position
point_cloud = get_pc(scan_id)
# seg2pc = get_seg2pc(scan_id, point_cloud)
# obj2pc = get_obj2pc(scan_id, seg2pc)
# obj2global = get_obj2global(scan_id)
# obj2hex = get_obj2hex(scan_id)

min_point = np.min(point_cloud, axis=0)+1
max_point = np.max(point_cloud, axis=0)-1

# random camera coordinate
cam_x = random.uniform(min_point[0], max_point[0])
cam_y = random.uniform(min_point[1], max_point[1])
cam_z = (min_point[2]+max_point[2])/2

# ray origin and directions
ray_origins = np.repeat(np.array([[cam_x, cam_y, cam_z]]), width * height, axis=0)
ray_directions = []

random_degree = random.uniform(0,360)

# get all the rays from sphere
count = 0
for x in range(width):
    for y in range(height):
        # sphere coordinate
        theta = -(x+1-width/2)*2*np.pi/width
        phi = -(y+1-height/2)*np.pi/height

        # z-axis rotation for augmentation
        rotated_theta = theta + np.radians(random_degree)
        if rotated_theta > np.radians(180):
            rotated_theta -= np.radians(360)
        
        ray_x = np.sin(phi) * np.cos(rotated_theta)
        ray_y = np.sin(phi) * np.sin(rotated_theta)
        ray_z = np.cos(phi)
        ray_directions.append([ray_x, ray_y, ray_z])
        count += 1
    if count > 10000:
        break
ray_origins = np.repeat(np.array([[cam_x, cam_y, cam_z]]), len(ray_directions), axis=0)
print(len(ray_directions))
# first hit face ids
face_ids = mesh.ray.intersects_first(ray_origins, np.array(ray_directions))

print(face_ids)
print(len(face_ids))

