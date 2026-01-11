import os
import cv2
import tkinter as tk
from tkinter import Canvas, Label
from PIL import Image, ImageTk
import numpy as np

def load_image(images):
    image = cv2.imread(images)
    if image is None:
        raise FileNotFoundError(f"Failed to load image: {images}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def load_annotations(labels):
    annotations = []
    with open(labels, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) == 9:
                class_id = int(parts[0])
                points = list(map(float, parts[1:]))
                annotations.append((class_id, points))
    return annotations


COLOR_MAP = {
    0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255),
    3: (255, 255, 0), 4: (255, 0, 255), 5: (0, 255, 255),
    6: (128, 0, 0), 7: (0, 128, 0), 8: (0, 0, 128),
    9: (128, 128, 0), 10: (128, 0, 128), 11: (0, 128, 128),
    12: (192, 192, 192), 13: (255, 165, 0), 14: (75, 0, 130),
}

class_map = {
   .....
}


def draw_annotations(image, annotations):
    placed_labels = []

    for class_id, points in annotations:
        pts = np.array(points).reshape(4, 2) * [image.shape[1], image.shape[0]]
        pts = pts.astype(int)

        color = COLOR_MAP.get(class_id, (255, 255, 255))
        cv2.polylines(image, [pts], isClosed=True, color=color, thickness=16)

        class_desc = class_map.get(class_id, str(class_id))
        x, y = pts[0]

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 5
        thickness = 10
        text_size, _ = cv2.getTextSize(class_desc, font, font_scale, thickness)
        text_width, text_height = text_size

        label_x, label_y = x, y - 10

        move_step = 10
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            rect_x1 = label_x
            rect_y1 = label_y - text_height
            rect_x2 = label_x + text_width
            rect_y2 = label_y

            overlap_found = False
            for (ox1, oy1, ox2, oy2) in placed_labels:
                if not (rect_x2 < ox1 or rect_x1 > ox2 or rect_y2 < oy1 or rect_y1 > oy2):
                    overlap_found = True
                    break

            if not overlap_found:
                break
            else:
                label_x += move_step
                label_y += move_step
                attempts += 1

        placed_labels.append((rect_x1, rect_y1, rect_x2, rect_y2))

        cv2.putText(image, class_desc, (label_x, label_y), font, font_scale, color, thickness, cv2.LINE_AA)

    return image


def resize_image(image, max_width, max_height):
    h, w = image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def update_image():
    global img_tk
    if images:
        image_path = images[current_index]
        label_path = os.path.join(labels_dir, os.path.basename(image_path).replace('.jpg', '.txt'))
        image = load_image(image_path)
        if os.path.exists(label_path):
            annotations = load_annotations(label_path)
            image = draw_annotations(image, annotations)

        filename = os.path.basename(image_path)
        filename_label.config(text=filename)

        total_images = len(images)
        passed = current_index + 1
        remaining = total_images - passed
        count_label.config(text=f"Image {passed}/{total_images}  -  Restantes: {remaining}")

        image = resize_image(image, 740, 550)
        image = Image.fromarray(image)
        img_tk = ImageTk.PhotoImage(image)
        canvas.config(width=img_tk.width(), height=img_tk.height())
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)


def next_image():
    global current_index
    current_index = (current_index + 1) % len(images)
    update_image()


def prev_image():
    global current_index
    current_index = (current_index - 1) % len(images)
    update_image()



images_dir = "/Users/rpc/Downloads/...../images"
labels_dir = "/Users/rpc/Downloads/...../labels"
images = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith('.jpg')]
current_index = 0

# Création de l'interface
root = tk.Tk()
root.title("YOLO OBB Viewer")

canvas = Canvas(root, width=1000, height=600)
canvas.pack()


filename_label = Label(root, text="", font=("Arial", 12))
filename_label.pack()

count_label = Label(root, text="", font=("Arial", 12))
count_label.pack()

tk.Button(root, text="Previous", command=prev_image).pack(side=tk.LEFT)
tk.Button(root, text="Next", command=next_image).pack(side=tk.RIGHT)

update_image()
root.mainloop()
