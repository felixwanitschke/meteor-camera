import cv2
import numpy as np
from scipy import ndimage
def preprocessing(final, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
#     blur = ndimage.median_filter(blur, size=2)
    final += blur
    
    return final

def frame_diff(current, prev):
    frame_diff = cv2.absdiff(current, prev)
    kernel_size = 3
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded_mask = cv2.erode(frame_diff, kernel, iterations=1
                           )
    dilated_mask = cv2.dilate(eroded_mask, kernel, iterations=3)
    return dilated_mask
 
def bgsub(frame):
    fgmask = backSub.apply(frame)
    return fgmask
    
video_path = r'C:\Users\ERSA\Desktop\3_5_58.webm'
cap = cv2.VideoCapture(video_path)
i = 0
count = 0
ret, frame = cap.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
final = np.zeros_like(frame)
diff = np.zeros_like(frame)
output = np.zeros_like(frame)
backSub = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=15)
fgmask = None
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if(i<3):
        final = preprocessing(final, frame)
    else:
        i = 0
        prev = final
        current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = frame_diff(current, prev)
        final = 0
        current = 0
    i += 1
    # Display the processed frame
    cv2.namedWindow("output")  
    resized_image = cv2.resize(diff, (600, 600))
    cv2.putText(resized_image, str(i)+'-'+str(count), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('output', resized_image)
    count += 1
    # Break the loop if 'q' is pressed
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()

    
    
