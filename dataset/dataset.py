from torch.utils.data import Dataset, DataLoader
import json 

class SGDataset(Dataset):
    def __init__(self, input_list_path):
        sg = '/root/dataset/3DSSG/new_relationships.json'
        with open(input_list_path, 'r') as f:
            self.input_list = f.readlines()
        with open(sg, 'r') as f:
            self.complete_graph = json.load(f)

    def __getitem__(self, idx):
        sample_path = self.input_list[idx]
        complete_ERP_path = sample_path.split()[0]
        partial_ERP_path = sample_path.split()[1]
        partial_graph_path = sample_path.split()[2]

        scan_id = partial_graph_path.split("/")[-3]
        
        complete_graph = sg[scan_id]
        with open(partial_graph_path, 'r') as f:
            partial_graph = list(json.load(f).values())
        complete_ERP = Image.open(complete_image_path)
        partial_ERP = Image.open(partial_ERP)

        return complete_ERP, partial_ERP, complete_graph, partial_graph
    
    def __len__(self):
        return len(self.input_list)
        