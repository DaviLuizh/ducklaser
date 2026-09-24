import cv2
import numpy as np
import pyautogui

    # which camera to choose, what resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # if no camera, warns that theres no camera
if not cap.isOpened():
    print("no camera!!!")
    exit()

    # things that make work
pyautogui.PAUSE = 0.001
laser_is_on_screen = False

print("everything red with a white center it aims. q to exit")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue
        
    # anti earthquake feature
    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    
    # light=laser so yes
    # converts to HSV
    hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
    
    # uhh idk light channel
    v = hsv[:, :, 2]
    
    # high threshold, gets everything that has anything above 220 (0 a 255)
    # ts will separate the laser from your room (it still going to detect
    # reflections as the laser so point to a reflectionless black surface)
    _, mask = cv2.threshold(v, 220, 255, cv2.THRESH_BINARY)
    
    # think that makes sure it'll make it detect laser
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # im tired of writing code. this does somethign that im too tired to explain
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    laser_visivel = False

    if contours:
        c = max(contours, key=cv2.contourArea)
        # the laser is tiny, but bright, so 5 is enough
        if cv2.contourArea(c) > 5: 
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # draws a green circle to see whats it detecting as the laser
                cv2.circle(frame, (cX, cY), 20, (0, 255, 0), 2)

                h, w, _ = frame.shape
                if w > 0 and h > 0:
                    screen_w, screen_h = pyautogui.size()
                    mapped_x = int((cX / w) * screen_w)
                    mapped_y = int((cY / h) * screen_h)

                    pyautogui.moveTo(mapped_x, mapped_y)
                    laser_visivel = True

    if laser_estava_na_tela and not laser_visivel:
        pyautogui.click()

    laser_estava_na_tela = laser_visivel

    # shows the webcam and mask (for debug)
    cv2.imshow("duck hunt - sniper", frame)
    cv2.imshow("mask - brightness", mask)

    # if q is pressed, kills everything
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
