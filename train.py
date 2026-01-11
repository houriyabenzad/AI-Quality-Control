from ultralytics import YOLO
model = YOLO("Yolo11x-obb.pt")
model.train(data="/Users/rpc/Desktop/PythonProject1/PythonProject/detect_train/dataset/yaml.yaml",epochs=16,imgsz=1280)
