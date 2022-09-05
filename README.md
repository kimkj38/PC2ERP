# PointCloud to ERP images
This repository provides projection function which convert point cloud into multi-view 360-degree images in equirectangular projection (ERP) format.

## Requirements
- numpy
- matplotlib
- plyfile
- cv2

## TODO
22-09-04 
- 카메라가 object 바로 옆에 배치돼서 ERP의 많은 영역이 해당 object로 가려지는 현상 해결
- 육안으로는 object가 몇 개 없어보이는데 많이 잡히는 원인 분석 및 해결
- multiprocessing으로 전처리 속도 향상(현재 512x256 기준 한 장당 8분 정도)
