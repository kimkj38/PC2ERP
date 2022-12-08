import trimesh
import rtree
import shapely
import numpy as np
import random
from generatePC import *
import cv2
from plyfile import PlyData, PlyElement
import time
import multiprocessing
import os
from multiprocessing.pool import Pool

lock = multiprocessing.Lock()

def raycasting(scan_id):
    print(scan_id)
    start = time.time()
    
    # scene mesh
    filename = '/root/dataset/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)
    mesh = trimesh.load_mesh(filename)

    # scene graph
    with open('/root/dataset/3DSSG_subset/subset_relationships.json') as f:
        relationships = json.load(f)['scans']

    for scan in relationships:
        if scan['scan'] == scan_id:
            split = scan['split']
            sub_objs = list(scan['objects'].keys())
            sub_objs = list(map(int, sub_objs))            

            # Output ERP size
            width = 1024//2
            height = 512//2

            # extract semantic information
            plydata = PlyData.read(filename)
            faces = plydata['face'].data['vertex_indices']
            vertexes = plydata['vertex'].data    

            # Region to sample a random camera position
            point_cloud = get_pc(scan_id)
            seg2pc = get_seg2pc(scan_id, point_cloud)
            obj2pc = get_obj2pc(scan_id, seg2pc)

            # floor coordinates
            min_point = np.min(point_cloud, axis=0)+1
            max_point = np.max(point_cloud, axis=0)-1
            
            # floor vertexes coordinates
            objs = scan['objects']
            for obj_id, name in objs.items():
                if name == "floor":
                    floor_id = obj_id

            floor = obj2pc[int(floor_id)] 

            # scene folder    
            save_path = "/root/dataset/3DSSG_subset_ERP/{}".format(scan_id)
            if not os.path.exists(save_path):
                os.mkdir(save_path)



            # Get random camera position until it is on the floor
            floor_global_id = 0
            while floor_global_id != 188: # floor global id == 188
                print("xxxxxxx", scan_id)
                random_idx = random.randint(0, len(floor)-1)
                cam_x = floor[random_idx][0]
                cam_y = floor[random_idx][1]
                cam_z = (min_point[2]+max_point[2])/2

                camray_direction = np.array([[0,0,-1]]) # downward direction

                # get global id of face which intersets first from camera with downward direction ray
                floor_id = mesh.ray.intersects_first(np.array([[cam_x, cam_y, cam_z]]), camray_direction) 
                floor_vertex3 = faces[floor_id]
                floor_vertex = vertexes[floor_vertex3[0][0]]

                floor_global_id = floor_vertex[7] 


            print(cam_x, cam_y, cam_z)

            # random degree for rotation variation
            random_degree = random.uniform(0,360)
            print("random degree는", random_degree)

            # image
            img = np.zeros((height, width, 3), dtype=np.uint8)

            # get all the rays from sphere
            for x in range(width):
                for y in range(height):
                    # sphere coordinate
                    phi = -(y+1-height/2)*np.pi/height
                    theta = (x+1-width/2)*2*np.pi/width

                    # z-axis rotation for augmentation
                    rotated_theta = theta + np.radians(random_degree)
                    if rotated_theta > np.radians(180):
                        rotated_theta -= np.radians(360)
                    #print("x는 ",x, "y는 ", y, "theta는 ", np.degrees(theta), "phi는 ", np.degrees(phi))
                    
                    # sphere to cartesian
                    ray_x = np.sin(rotated_theta) * np.cos(phi)
                    ray_y = np.cos(phi) * np.cos(rotated_theta)
                    ray_z = np.sin(phi)
                    
                    # theta degree
                    theta_degree = np.degrees(rotated_theta)

                    # face that ray intersects first
                    face_id = mesh.ray.intersects_first(np.array([[cam_x, cam_y, cam_z]]), np.array([[ray_x, ray_y, ray_z]]))   

                    # if intersection exists, extract face color
                    if face_id != -1:
                        vertex3 = faces[face_id]
                        vertex = vertexes[vertex3[0][0]]
                        object_id = vertex[6]

                        if object_id in sub_objs:
                            img[y, x, 0] = vertex[5]
                            img[y, x, 1] = vertex[4]
                            img[y, x, 2] = vertex[3]

            # save ERP image
            cv2.imwrite(os.path.join(save_path,"subset{}.jpg".format(split)), img)

# # records scan id if there's no floor id
#     else:
#         print("floor 없음", scan_id)
#         filename = "/root/dataset/3RScan_ERP/no_floor.txt"
#         if not os.path.exists(filename):
#             f = open(filename, 'w')
#             data = "{} \n".format(scan_id)
#             f.write(data)
#         else:
#             f = open(filename, 'a')
#             data = "{} \n".format(scan_id)
#             f.write(data)

    print("연산시간: ", time.time()-start)



if __name__=='__main__':
    dataset = '/root/dataset/3RScan'
    scan_id_list = os.listdir(dataset)

    pool = multiprocessing.Pool(50)

    pool.map(raycasting, scan_id_list)
    pool.close()
    pool.join()

