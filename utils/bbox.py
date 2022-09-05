import json
import math

import numpy as np
import matplotlib.pyplot as plt

from generatePC import *

scan_id = '4fbad329-465b-2a5d-8401-a3f550ef3de5'

point_cloud = get_pc(scan_id)
seg2pc = get_seg2pc(scan_id, point_cloud)
obj2pc = get_obj2pc(scan_id, seg2pc)
obj2global = get_obj2global(scan_id)
obj2hex = get_obj2hex(scan_id)


fig, ax = plt.subplots()
pcs = obj2pc[23]
center = (np.max(pcs, axis=0) + np.min(pcs, axis=0))/2



# min_area = np.inf

# for i in range(1,91):
#     degree = i
#     radian = math.radians(degree)
#     T = np.array([[1, 0, -center[0]], [0, 1, -center[1]], [0, 0, 1]])
#     R = np.array([[math.cos(radian), -math.sin(radian)], [math.sin(radian), math.cos(radian)]])
#     homo_pcs = pcs.copy()
#     homo_pcs[:, -1] = 1
#     pcs_r = R @ pcs[:,:-1].T
#     wh = np.max(pcs_r, axis=1) - np.min(pcs_r, axis=1)
#     area = wh[0] * wh[1]
#     if area < min_area:
#         min_area = area
#         w = wh[0]
#         h = wh[1]
#         rotation = degree

# print(w, h, min_area, rotation)

# visualize
degree = 30
radian = math.radians(degree)

T = np.array([[1, 0, -center[0]], [0, 1, -center[1]], [0, 0, 1]])
R = np.array([[math.cos(radian), -math.sin(radian), 0], [math.sin(radian), math.cos(radian), 0],  [0, 0, 1]])
homo_pcs = pcs.copy()
homo_pcs[:, -1] = 1
#pcs_t = T @ homo_pcs.T
pcs_r = R @ (T @ homo_pcs.T)
# print(pcs_r.shape)
# print(np.max(pcs_r, axis=1), np.min(pcs_r, axis=1))
# wh = np.max(pcs_r, axis=1) - np.min(pcs_r, axis=1)
# area = wh[0] * wh[1]

plt.scatter(pcs[:,0], pcs[:,1], 5, 'b')
#plt.scatter(pcs_t[0,:], pcs_t[1,:], 5, 'b')
plt.scatter(pcs_r[0,:], pcs_r[1,:], 5, 'g')
# # for pc in pcs:
# #     plt.scatter(pc[0], pc[1], 5, 'b')
plt.scatter(center[0], center[1], 10, 'r')
plt.show()
