# Face Animation in Real Time
One-shot face animation using webcam, capable of running in real time.
## **Examples Results**
(Driving video | Result video)
- Original Result without Face Restoration

https://github.com/sky24h/Face_Mapping_Real_Time/assets/26270672/231778e3-0f37-42c3-8cb0-cf849b22c8a8

- With Face Restoration

https://github.com/sky24h/Face_Mapping_Real_Time/assets/26270672/323fb958-77b4-444d-9a21-4d0245fb108c

# How to Use
### 0. Dependencies
```
pip install -r requirements.txt
```
### **1. For local webcam**
Tested on RTX 3090, got 17 FPS without face restoration, and 10 FPS with face restoration.
```
python camera_local.py --source_image ./assets/source.jpg --restore_face False
```
The model output only supports size of 256, but you can change the output size to 512x512 or larger to get a resized output.

### **2. For input driving video**
```
python camera_local.py --source_image ./assets/source.jpg --restore_face False --driving_video ./assets/driving.mp4 --result_video ./result_video.mp4 --output_size 512
```
The driving video does not require any preprocessing, it is valid to use as long as every frame contains a face.

### **3. For remote access (Not recommended)**
First you need to bind the port between server and client, for example, using vscode remote ssh like [this](https://code.visualstudio.com/docs/editor/port-forwarding).
Then run the server side on the remote server, and run the client side on the local machine.

Notably, due to the network latency, the FPS is low (only 1~2 FPS).

Server Side:
```
python remote_server.py --source_image ./assets/source.jpg --restore_face False
```

Client Side (Copy only this file to local machine):
```
python remote_client.py
```
---
### Pre-trained Models
All necessary pre-trained models should be downloaded automatically when running the demo.
If you somehow need to download them manually, please refer to the following links:

[Motion Transfer Model](https://drive.google.com/file/d/11ZgyjKI5OcB7klcsIdPpCCX38AIX8Soc/view?usp=drive_link)

[GPEN (Face Restoration Model](https://drive.google.com/drive/folders/1epln5c8HW1QXfVz6444Fe0hG-vRNavi6?usp=drive_link)


# Acknowlegement: 
Motion transfer is modified from [zhanglonghao1992](https://github.com/zhanglonghao1992/One-Shot_Free-View_Neural_Talking_Head_Synthesis).
Face restoration is modified from [GPEN](https://github.com/yangxy/GPEN).

Thanks to the authors for their great work!
