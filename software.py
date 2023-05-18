import cv2
import numpy as np

def preprocessing(frame):
    # Apply the preprocessing steps to a single frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    #background subtraction method 
    fgmask = backSub.apply(blur)
    #apply morphological operations
    eroded_mask = cv2.erode(fgmask, kernel, iterations=2)
    dilated_mask = cv2.dilate(eroded_mask, kernel, iterations=1)
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
        
def meteor_detection(new_, processed_frame, counter):
    # Apply Canny edge detection
    edges = cv2.Canny(new_,10 , 20)

    # Apply probabilistic Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=10, minLineLength=30, maxLineGap=50)

    # Check if any lines are detected
    if lines is not None:
        print("Lines detected!")  #when there are lines on the frame
        # Process the detected lines further if needed
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(processed_frame, (x1, y1), (x2, y2), (255, 255, 255), 1)  # Example: draw the lines on the image
    else:
        print("No lines detected.")
       
# Create background subtractor and kernel
backSub = cv2.createBackgroundSubtractorMOG2(history=15, varThreshold=15)
kernel_size = 3
kernel = np.ones((kernel_size, kernel_size), np.uint8)

# Open video capture (change 0 to the appropriate video source or file path)
video_path = '/home/reema/Desktop/videos/3_5:58.webm'
i = 0
count = 0
cap = cv2.VideoCapture(video_path)
new_ = np.zeros((1080, 1920), dtype=np.uint8)

while True:
    
    # Read a frame from the video stream
    ret, frame = cap.read()
    
    
    if not ret:
        break

    # Preprocess the frame
    processed_frame = preprocessing(frame)
    #add frames
    new_, i = add(new_, processed_frame, i)
    #after each 20 frames, check on the combined frames, if there is any line, 
    if(i == 20):
        meteor_detection(new_, processed_frame, count)
        output = 0

    # Display the processed frame
    cv2.namedWindow("output", cv2.WINDOW_NORMAL)  
    resized_image = cv2.resize(processed_frame, (600, 600))
    cv2.putText(resized_image, str(count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Processed Frame', resized_image)
    count += 1
    # Break the loop if 'q' is pressed
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()

