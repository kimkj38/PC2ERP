from plyfile import PlyData, PlyElement
import numpy as np
import cv2

# ERP size
w = 1024
h = 512

# image
img = np.zeros((512,1024,3), np.uint8)

# ply mesh data
sample_num = 2
plydata = PlyData.read('{}/labels.instances.annotated.v2.ply'.format(sample_num))

vertexes = plydata.elements[0].data
faces = plydata.elements[1].data

# save color and projected ERP coordinate of vertexes
vertex_dict = dict()

for (id, vertex) in enumerate(vertexes):
    x =vertex[0]
    y = vertex[1]
    z = vertex[2]

    color = (int(vertex[5]), int(vertex[4]), int(vertex[3]))

    #rho = np.sqrt(x**2+y**2+z**2)
    
    theta = np.arctan2(y,x)
    phi = np.arctan2(z, (np.sqrt(x**2 + y**2)))

    pano_x = int(w*theta/(2*np.pi)+(w/2-1))
    pano_y = int((h/2-1) - h*phi/np.pi)

    vertex_dict[id] = (pano_x, pano_y, color)

    #img = cv2.circle(img, (pano_x, pano_y), 2, tuple(color), -1)

# use face information to fill the region with color
face_points = []
for face_id, face in enumerate(faces):
    color = vertex_dict[face[0][0]][2]
    color_match = True

    for i, vertex_id in enumerate(face[0]):
        color2 = vertex_dict[vertex_id][2]
        pano_x = vertex_dict[vertex_id][0]
        pano_y = vertex_dict[vertex_id][1]
        face_points.append((pano_x, pano_y))
        
        if color != color2:
            color_match = False

    print(face_id)
    if color_match == True:
        cv2.drawContours(img, [np.array(face_points)], 0, tuple(color), -1)

cv2.imwrite("{}/face_erp2.jpg".format(sample_num), img)

        # if i != 0:
        #     if main_c != color:
        #         print("face_id=", face_id)
        #         print(main_c)
        #         print(color)
        #         print("______________")
        # main_c = color
        # if face_id == 2727:
        #     print(color)    



# cv2.imshow('erp', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
