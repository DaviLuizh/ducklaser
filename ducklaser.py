import cv2
import numpy as np
import pyautogui

    # qual camera escolher, resoluçao
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # se nao detectar camera, dizer que nao ta
if not cap.isOpened():
    print("a camera usb nao ta aqui")
    exit()

    # coisas
pyautogui.PAUSE = 0.001
laser_estava_na_tela = False

print("tudo vermelho ele mira. aponta o laser pra uma superficie preta. q pra sair.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue
        
    # desfoque pra nao tremer muito
    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    
    # brilho=laser entao vai
    # converte para HSV
    hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
    
    # separa apenas o canal de Value (brilho)
    v = hsv[:, :, 2]
    
    # threshold alto, pega tudo que tem brilho acima de 220 (0 a 255)
    # isso vai isolar o laser e ignorar o resto da sala
    _, mask = cv2.threshold(v, 220, 255, cv2.THRESH_BINARY)
    
    # dilata um pouco a mascara para garantir que pega o laser todo
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # encontra os contornos baseados SOMENTE no brilho
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    laser_visivel = False

    if contours:
        c = max(contours, key=cv2.contourArea)
        # o laser é pequeno, mas muito brilhante, entao um tamanho minimo de 5 eh suficiente
        if cv2.contourArea(c) > 5: 
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # desenha o circulo verde no frame original
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

    # mostra o frame original e a mascara de brilho (pra debug)
    cv2.imshow("duck hunt - sniper", frame)
    cv2.imshow("mascara - brilho", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
