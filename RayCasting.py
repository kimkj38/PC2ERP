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


def raycasting(scan_id, iterations):


    start = time.time()
    
    # scene mesh
    filename = '/root/dataset/3RScan/{}/labels.instances.annotated.v2.ply'.format(scan_id)
    mesh = trimesh.load_mesh(filename)

    # scene graph
    with open('/root/dataset/3RScan_ERP/new_relationships.json') as f:
        relationships = json.load(f)[scan_id]

    # Output ERP size
    width = 1024//2
    height = 512//2

    # data to extract semantic information
    plydata = PlyData.read(filename)
    faces = plydata['face'].data['vertex_indices']
    vertexes = plydata['vertex'].data    

    # Region to sample a random camera position
    point_cloud = get_pc(scan_id)
    seg2pc = get_seg2pc(scan_id, point_cloud)
    obj2pc = get_obj2pc(scan_id, seg2pc)

    # min & max point coordinate
    min_point = np.min(point_cloud, axis=0)
    max_point = np.max(point_cloud, axis=0)
    
    # floor vertexes coordinates
    floor = obj2pc[1] # floor object id == 1

    # make scene folder    
    save_path = "/root/dataset/3RScan_ERP/{}".format(scan_id)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # ray casting
    for it in range(iterations):
        # make ERP folder in scene folder
        ERP_folder = os.path.join(save_path, 'ERP{}'.format(it))
        if not os.path.exists(ERP_folder):
            os.mkdir(ERP_folder)

        # Get random camera position until it is on the floor
        floor_global_id = 0
        while floor_global_id != 188: # floor global id == 188
            print("xxxxxxx")
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

        # object ids list per section
        mask1 = []
        mask2 = []
        mask3 = []
        mask4 = []

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

                # face id that ray intersects first
                face_id = mesh.ray.intersects_first(np.array([[cam_x, cam_y, cam_z]]), np.array([[ray_x, ray_y, ray_z]]))   

                # if intersection exists, extract face color
                if face_id != -1: # -1 means there's no intersection
                    vertex3 = faces[face_id]
                    vertex = vertexes[vertex3[0][0]]
                    img[y, x, 0] = vertex[5]
                    img[y, x, 1] = vertex[4]
                    img[y, x, 2] = vertex[3]

                    # records object id for masking and making partial scene graph
                    if -180 <= theta_degree < -90:
                        mask1.append(vertex[6])
                    elif -90 <= theta_degree < 0:
                        mask2.append(vertex[6])
                    elif 0 <= theta_degree < 90:
                        mask3.append(vertex[6])
                    elif 90 <= theta_degree <= 180:
                        mask4.append(vertex[6])


        # save ERP image
        cv2.imwrite(os.path.join(ERP_folder,"complete_ERP.jpg"), img)

        # make partial image and partial scene graph
        # make mask.jpg when there are 5~10 objects in masking area
        if 5 <= len(set(mask1)) < 10:
            mask1_img = img.copy()
            mask1_img[:, :width//4, :] = 0
            cv2.imwrite(os.path.join(ERP_folder, "mask1.jpg"), mask1_img)
            partial_relation = {}
            
            obj_ids = mask2 + mask3 + mask4

            # bring triplet from original relationsips.json only when both subject and object are included in non-masking area
            i  = 0
            for obj in relationships:
                if (obj[0] in obj_ids) and (obj[1] in obj_ids):
                    partial_relation[i] = obj
                    i += 1

            with open(os.path.join(ERP_folder, "mask1.json"), "w") as f:
                json.dump(partial_relation, f)

        if 5 <= len(set(mask2)) < 10:
            mask2_img = img.copy()
            mask2_img[:, width//4:width//2, :] = 0
            cv2.imwrite(os.path.join(ERP_folder, "mask2.jpg"), mask2_img)
            partial_relation = {}
            
            obj_ids = mask1 + mask3 + mask4

            i  = 0
            for obj in relationships:
                if (obj[0] in obj_ids) and (obj[1] in obj_ids):
                    partial_relation[i] = obj
                    i += 1


            with open(os.path.join(ERP_folder, "mask2.json"), "w") as f:
                json.dump(partial_relation, f)

        if 5 <= len(set(mask3)) < 10:
            mask3_img = img.copy()
            mask3_img[:, width//2:width*3//4, :] = 0
            cv2.imwrite(os.path.join(ERP_folder, "mask3.jpg"), mask3_img)
            partial_relation = {}
            
            obj_ids = mask2 + mask2 + mask4

            i  = 0
            for obj in relationships:
                if (obj[0] in obj_ids) and (obj[1] in obj_ids):
                    partial_relation[i] = obj
                    i += 1

            with open(os.path.join(ERP_folder, "mask3.json"), "w") as f:
                json.dump(partial_relation, f)

        if 5 <= len(set(mask4)) < 10:
            mask4_img = img.copy()
            mask4_img[:, width*3//4:, :] = 0
            cv2.imwrite(os.path.join(ERP_folder, "mask4.jpg"), mask4_img)
            partial_relation = {}
            
            obj_ids = mask1 + mask2 + mask3

            i  = 0
            for obj in relationships:
                if (obj[0] in obj_ids) and (obj[1] in obj_ids):
                    partial_relation[i] = obj
                    i += 1

            with open(os.path.join(ERP_folder, "mask4.json"), "w") as f:
                json.dump(partial_relation, f)

        print(set(mask1), len(set(mask1)))
        print(set(mask2), len(set(mask2)))
        print(set(mask3), len(set(mask3)))
        print(set(mask4), len(set(mask4)))

        print("연산시간: ", time.time()-start)

if __name__=='__main__':
    dataset = '/root/dataset/3RScan'
    scan_id_list = os.listdir(dataset)
    # scan_id = "4fbad329-465b-2a5d-8401-a3f550ef3de5"
    iterations = 5
    for scan_id in scan_id_list:
        raycasting(scan_id, iterations)
