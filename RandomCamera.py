import json
from generatePC import *
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from plyfile import PlyData, PlyElement
import random

scan_id = '4fbad329-465b-2a5d-8401-a3f550ef3de5'
num = 7
random_camera_name = "random_camera{}.ply".format(num)

point_cloud = get_pc(scan_id)
seg2pc = get_seg2pc(scan_id, point_cloud)
obj2pc = get_obj2pc(scan_id, seg2pc)
obj2global = get_obj2global(scan_id)
obj2hex = get_obj2hex(scan_id)

min_point = np.min(point_cloud, axis=0)+1
max_point = np.max(point_cloud, axis=0)-1


# random camera coordinate
cam_x = random.uniform(min_point[0], max_point[0])
cam_y = random.uniform(min_point[1], max_point[1])
cam_z = (min_point[2]+max_point[2])/2

# random rotation
degree = random.randint(0,360)
radian = np.radians(degree)

RT = np.array([[np.cos(radian), -np.sin(radian), 0, -cam_x], [np.sin(radian), np.cos(radian), 0, -cam_y], [0, 0, 1, -cam_z]])

vertex = []
for obj_id, pcs in obj2pc.items():
    for pc in pcs:
        # Set camera coordinate as starting point
        trans_coor = RT @ np.array([pc[0], pc[1], pc[2], 1]).T
        x = trans_coor[0]
        y = trans_coor[1]
        z = trans_coor[2]

        global_id = int(obj2global[str(int(obj_id))])
        r, g, b = hex2rgb(obj2hex[str(int(obj_id))])

        if len(vertex) == 0:
            vertex = [(x, y, z, r, g, b, obj_id, global_id, 0, 0, 0)]

        else:
            vertex.append((x, y, z, r, g, b, obj_id, global_id, 0, 0, 0))

    
vertex = np.array(vertex, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'),
                    ('object_id', 'ushort'), ('global_id', 'ushort'), ('NYU40', 'u1'), ('Eigen13', 'u1'), ('RIO27', 'u1')])
face = PlyData.read(os.path.join(scan_id, "labels.instances.annotated.v2.ply")).elements[1].data


v = PlyElement.describe(vertex, 'vertex')
f = PlyElement.describe(face, 'face')
PlyData([v, f], text=True).write(os.path.join(scan_id, 'RandomCamera', random_camera_name))

