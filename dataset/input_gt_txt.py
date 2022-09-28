import os
import json

root = '/root/dataset/mini_SGE'

train_txt = open('input_train_path.txt', 'w')
test_txt = open('input_test_path.txt', 'w')

scan_list = os.listdir(root)
train_num = int(len(scan_list)*0.8)

for (i, scan) in enumerate(scan_list):
    scan_path = os.path.join(root,scan) # /root/dataset/mini_SGE/scan_id
    ERP_list = os.listdir(scan_path)
    for ERP in ERP_list:
        ERP_path = os.path.join(scan_path, ERP) # /root/dataset/mini_SGE/scan_id/ERP0
        complete_img_path = os.path.join(ERP_path, 'complete_ERP.jpg') # /root/dataset/mini_SGE/scan_id/ERP0/complete_ERP.jpg
        mask_list = os.listdir(ERP_path)
        if 'complete_ERP.jpg' in mask_list:
            mask_list.remove('complete_ERP.jpg') # remove complete ERP from mask list
        
        # even index is partial image, odd index is partial scene graph 
        for index, mask_file in enumerate(mask_list): 
            if index % 2 == 0:
                partial_image_path = os.path.join(ERP_path, mask_file)
            else:
                partial_graph_path = os.path.join(ERP_path, mask_file)
                lines = complete_img_path + " " + partial_image_path + " " + partial_graph_path + "\n"
                if i <= train_num:
                    train_txt.write(lines)
                else:
                    test_txt.write(lines)


