import json
from generatePC import *
import matplotlib.pyplot as plt
import numpy as np
import math


#-180 ~ 180
min_degree = 0
max_degree = 90
min_theta = np.radians(min_degree)
max_theta = np.radians(max_degree)

# file name
scan_id = '4fbad329-465b-2a5d-8401-a3f550ef3de5'
partial_name = 'partial_{}{}.ply'.format(min_degree, max_degree)

point_cloud = get_pc(scan_id)
seg2pc = get_seg2pc(scan_id, point_cloud)
obj2pc = get_obj2pc(scan_id, seg2pc)
obj2global = get_obj2global(scan_id)
obj2hex = get_obj2hex(scan_id)

# key: theta, value: [x,y,z,obj_id]
def get_theta2objpc(obj2pc):
    theta2objpc = {}
    for obj, pcs in obj2pc.items():
        for pc in pcs:
            theta = np.arctan2(pc[1],pc[0])
            objpc = np.append(pc, obj)
            theta2objpc[theta] = objpc
            
    return theta2objpc


# make ply file within assigned range of theta
theta2objpc = get_theta2objpc(obj2pc)
vertex = []
for theta, objpc in theta2objpc.items():
    if min_theta <= theta <= max_theta:
        x = objpc[0]
        y = objpc[1]
        z = objpc[2]
        obj_id = objpc[3]
        global_id = int(obj2global[str(int(obj_id))])
        r, g, b = hex2rgb(obj2hex[str(int(obj_id))])

        if len(vertex) == 0:
            vertex = [(x, y, z, r, g, b, obj_id, global_id)]
    
        else:
            vertex.append((x, y, z, r, g, b, obj_id, global_id))
    
vertex = np.array(vertex, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'),
                    ('object_id', 'ushort'), ('global_id', 'ushort')])

el = PlyElement.describe(vertex, 'vertex')
PlyData([el], text=True).write(os.path.join(scan_id, partial_name))