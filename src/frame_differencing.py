import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import matplotlib.patches as patches
import glob
import os
%matplotlib qt

video_path = ...

video_name = video_path.split('\\')[-1].split('.')[0]
output_folder = ....
images = []
counter = 0
idx = 0

x1, y1, x2, y2 = (0,0,0,0)
cap = cv2.VideoCapture(video_path)
# prev = None
m = 10
timer = 0

while True:   
    ret, frame = cap.read()
    if not ret:
        break
    # Apply background subtraction
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian filtering to reduce thermal noise
    filtered_image = cv2.GaussianBlur(gray, (3, 3), 0)
    
    images.append(filtered_image)
    if(timer >= m):
        #save frames
        final, trigger = sumofimages(images)
        if(trigger == True):
            p = m
            for img in images:                
                print("Saving...")
                output_path = os.path.join(output_folder, f"{video_name}+{counter - p }.jpg")
                cv2.imwrite(output_path, img)
                p -= 1
            print("Saving completed!")
        else:
            print("No Detection Found. Buffer cleared.")
        images = []
        timer = 0
    # Display the resulting image
    cv2.namedWindow("output")  
    resized_image = cv2.resize(filtered_image, (600, 600))
    cv2.imshow('output', resized_image)
    
    print(counter)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# 
    counter += 1  
    timer += 1
cap.release()
cv2.destroyAllWindows()


# Define the folder path containing the images
folder_path = output_folder

# Get a list of image file paths in the folder
image_files = glob.glob(folder_path + '/*.jpg')
# Iterate over pairs of consecutive images
count = 0
prev = None
idx = 0
j = 0
prev_x1, prev_x2, prev_y1, prev_y2 = (0,0,0,0)
while j < len(image_files)-10:
#     print("idx", idx, "j:", j, "counter:", count, "prev", prev)
    j, idx, prev,prev_x1, prev_y1, prev_x2, prev_y2 = autocorr(j, idx, prev,prev_x1, prev_y1, prev_x2, prev_y2)
    
    count += 1


