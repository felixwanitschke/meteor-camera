import cv2
import numpy as np

def preprocessing(frame):
    # Apply the preprocessing steps to a single frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    #background subtraction method 
    fgmask = backSub.apply(blur)
    #apply morphological operations
    eroded_mask = cv2.erode(fgmask, kernel, iterations=2)
    dilated_mask = cv2.dilate(eroded_mask, kernel, iterations=5)
    return dilated_mask

def add(new_, frame_, i):
    #add 20 frames and return the combined image
    if(i<=20):
        new_ += frame_
        i += 1
    else:
        i = 0
        new_ = np.zeros_like(frame_)
    return new_, i
        
def meteor_detection(new_, count):
    imgLines= cv2.HoughLinesP(new_,15,np.pi/180,10, minLineLength = 400, maxLineGap = 50)
    if(imgLines is not None):
        for i in range(len(imgLines)):
            for x1,y1,x2,y2 in imgLines[i]:
                dist = ((x2-x1)**2 + (y2 - y1)**2)**(1/2)
                if(dist < 1000):
                    print(dist, count)
#                     cv2.line(new_,(x1,y1),(x2,y2),(255,255,255),2)
    return count
       
# Create background subtractor and kernel
backSub = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=10)
kernel_size = 3
kernel = np.ones((kernel_size, kernel_size), np.uint8)

# Open video capture (change 0 to the appropriate video source or file path)
video_path = r'C:\Users\ERSA\Desktop\3_5_25.webm'
i = 0 #counter for images to be combined
count = 0  #a general counter for frames
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
new_ = np.zeros_like(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
while True:
    
    # Read a frame from the video stream
    ret, frame = cap.read()
    
    
    if not ret:
        break

    # Preprocess the frame
    processed_frame = preprocessing(frame)
    #add frames
    new_, i = add(new_, processed_frame, i)
    #after each 20 frames, check on the combined frames to see if there is any line, 
    if(i == 20):
        count = meteor_detection(new_, count)

    # Display the processed frame
    cv2.namedWindow("output")  
    resized_image = cv2.resize(new_, (600, 600))
    cv2.putText(resized_image, str(count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('output', resized_image)
    count += 1
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()
