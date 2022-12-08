import utils.DDB as ddb

if __name__=='__main__':
    # for all scan_id
    # dataset = '/root/dev/3RScan'
    # scan_id_list = os.listdir(dataset)
    # for scan_id in scan_id_list:
    #     if scan_id = '09582223-e2c2-2de1-94b6-750684b4f80a': # only visualize this scan
    #         ddb.extract_ddb(scan_id, overwrite=True, viz=True)
    #     else:
    #         ddb.extract_ddb(scan_id, overwrite=True, viz=False)
    
    # for a scan_id
    scan_id = '09582223-e2c2-2de1-94b6-750684b4f80a'
    ddb.extract_ddb(scan_id, overwrite=True, viz=False, rand_seed=None)