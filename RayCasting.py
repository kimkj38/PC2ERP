# import trimesh
# import rtree
# import shapely
# import numpy as np
# import random
# from generatePC import *
# import cv2

# scan_id = "4fbad329-465b-2a5d-8401-a3f550ef3de5"
# filename = "{}/labels.instances.annotated.v2.ply".format(scan_id)

# # scene mesh
# mesh = trimesh.load_mesh(filename)

# # Output ERP size
# width = 1024
# height = 512

# # Region to sample a random camera position
# point_cloud = get_pc(scan_id)
# # seg2pc = get_seg2pc(scan_id, point_cloud)
# # obj2pc = get_obj2pc(scan_id, seg2pc)
# # obj2global = get_obj2global(scan_id)
# # obj2hex = get_obj2hex(scan_id)

# min_point = np.min(point_cloud, axis=0)+1
# max_point = np.max(point_cloud, axis=0)-1
# print(min_point,max_point)

# # random camera coordinate
# cam_x = random.uniform(min_point[0], max_point[0])
# cam_y = random.uniform(min_point[1], max_point[1])
# cam_z = (min_point[2]+max_point[2])/2

# # ray origin and directions
# ray_origins = np.repeat(np.array([[cam_x, cam_y, cam_z]]), width * height, axis=0)
# ray_directions = []

# random_degree = random.uniform(0,360)

# # get all the rays from sphere
# count = 0
# for x in range(width):
#     for y in range(height):
#         # sphere coordinate
#         theta = -(x+1-width/2)*2*np.pi/width
#         phi = -(y+1-height/2)*np.pi/height

#         # z-axis rotation for augmentation
#         rotated_theta = theta + np.radians(random_degree)
#         if rotated_theta > np.radians(180):
#             rotated_theta -= np.radians(360)
        
#         ray_x = np.sin(phi) * np.cos(rotated_theta)
#         ray_y = np.sin(phi) * np.sin(rotated_theta)
#         ray_z = np.cos(phi)
#         ray_directions.append([ray_x, ray_y, ray_z])
#         count += 1
#     if count > 100000:
#         break
# ray_origins = np.repeat(np.array([[cam_x, cam_y, cam_z]]), len(ray_directions), axis=0)
# print(len(ray_directions))
# # first hit face ids
# face_ids = mesh.ray.intersects_first(ray_origins, np.array(ray_directions))

# # image
# img = np.zeros((height, width, 3), dtype=np.uint8)
# print(len(face_ids))

# # extract semantic color
# plydata = PlyData.read(filename)
# faces = plydata['face'].data['vertex_indices']
# vertexes = plydata['vertex'].data


# face_count = 0

# for x in range(width):
#     for y in range(height):
#         if face_count <100000:
#             face_id = face_ids[face_count]
#             if face_id != -1:
#                 vertex3 = faces[face_id]
#                 vertex = vertexes[vertex3[0]]
#                 img[y, x, 0] = vertex[3]
#                 img[y, x, 1] = vertex[4]
#                 img[y, x, 2] = vertex[5]
#             face_count += 1


# # cv2.imshow("image", img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()

    

import trimesh
import rtree
import shapely
import numpy as np
import random
#from generatePC import *
import cv2
from plyfile import PlyData, PlyElement

scan_id = "4a9a43e6-7736-2874-8723-08ae98eccd16"
filename = 'dataset/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)

# scene mesh
mesh = trimesh.load_mesh(filename)

# Output ERP size
width = 1024//4
height = 512//4

# Region to sample a random camera position
#point_cloud = get_pc(scan_id)
# seg2pc = get_seg2pc(scan_id, point_cloud)
# obj2pc = get_obj2pc(scan_id, seg2pc)
# obj2global = get_obj2global(scan_id)
# obj2hex = get_obj2hex(scan_id)

# min_point = np.min(point_cloud, axis=0)+1
# max_point = np.max(point_cloud, axis=0)-1
# print(min_point,max_point)
# min_point = [-1.86972+2, -2.13141+2, -2.18311] 
# max_point = [6.48426-2, 4.54175-2, 0.85609]
min_point = [-4.8831+3, -3.61415+2, -2.95241] 
max_point = [2.13-2, 3.58402-2, 2.12298]

# random camera coordinate
cam_x = random.uniform(min_point[0], max_point[0])
cam_y = random.uniform(min_point[1], max_point[1])
cam_z = (min_point[2]+max_point[2])/2
print(cam_x, cam_y, cam_z)

# ray origin and directions

ray_directions = []

random_degree = random.uniform(0,360)

# get all the rays from sphere
for x in range(width):
    for y in range(height):
        # sphere coordinate
        phi = -(y+1-height/2)*np.pi/height
        theta = (x+1-width/2)*2*np.pi/width

        # if phi > 0:
        #     theta = (x+1-width/2)*2*np.pi/width
        # else:
        #     theta = -(x+1-width/2)*2*np.pi/width

        # theta_map[y,x] = theta
        # phi_map[y,x] = phi

        # z-axis rotation for augmentation
        rotated_theta = theta + np.radians(random_degree)
        if rotated_theta > np.radians(180):
            rotated_theta -= np.radians(360)
        #print("x는 ",x, "y는 ", y, "theta는 ", np.degrees(theta), "phi는 ", np.degrees(phi))

        if -180 <= np.degrees(rotated_theta) < 90:
            ray_x = np.sin(rotated_theta) * np.cos(phi)
            ray_y = np.cos(phi) * np.cos(rotated_theta)
            # ray_x = np.sin(theta) * np.cos(phi)
            # ray_y = np.cos(phi) * np.cos(theta)
            ray_z = np.sin(phi)

            ray_directions.append([ray_x, ray_y, ray_z])

print(len(ray_directions))
ray_origins = np.repeat(np.array([[0,0,0]]), len(ray_directions), axis=0)
ray_directions = np.array(ray_directions)

# first hit face ids
face_ids = mesh.ray.intersects_first(ray_origins, ray_directions)

# image
img = np.zeros((height, width, 3), dtype=np.uint8)
print(len(face_ids))

# extract semantic color
plydata = PlyData.read(filename)
faces = plydata['face'].data['vertex_indices']
vertexes = plydata['vertex'].data


ray_count = 0

for x in range(width):
    for y in range(height):
        # if ray_count <100000:
        theta = (x+1-width/2)*2*np.pi/width
        rotated_theta = theta + np.radians(random_degree)
        if rotated_theta > np.radians(180):
            rotated_theta -= np.radians(360)

        if -180 <= np.degrees(rotated_theta) < 90:
            face_id = face_ids[ray_count]
            if face_id != -1:
                vertex3 = faces[face_id]
                vertex = vertexes[vertex3[0]]
                img[y, x, 0] = vertex[5]
                img[y, x, 1] = vertex[4]
                img[y, x, 2] = vertex[3]
            ray_count += 1
cv2.imwrite("meshrender.jpg", img)

# cv2.imshow("image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()