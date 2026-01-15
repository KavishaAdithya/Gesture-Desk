import pygetwindow as gw
import time
import HandtrackingModule as htm
import cv2 as cv
import numpy as np
import threading
import queue
import time
import pyautogui



machine_state = 0 
status_msg = "ROOT: [Index]LeftMon [Peace]RightMon [Spidey]Focus"
last_executed_gesture = [] 


gesture_queue = queue.Queue()


def get_Active_Window():

    try:
        active_Win = gw.getActiveWindow()

    except Exception as e:
        print(f'Error {e}')
    
    return active_Win

def state_machine(confirmed_fingers):

    global machine_state, status_msg, last_executed_gesture
    active_win=get_Active_Window()


    if confirmed_fingers == [0,0,0,0,0,0]:

        if machine_state != 0:
            machine_state = 0
            last_executed_gesture = confirmed_fingers
            status_msg = 'Reset to root'

    elif confirmed_fingers != last_executed_gesture:
        if machine_state == 0:

            if confirmed_fingers == [1, 0, 1, 0, 0, 0]:
                pyautogui.hotkey('win','shift','left')
                status_msg = 'Moved to L Monitor'
                machine_state = 1

            elif confirmed_fingers == [1,0,1,1,0,0]:
                pyautogui.hotkey('win','shift','right')
                status_msg = 'Moved to R Monitor'
                machine_state = 1

            elif confirmed_fingers == [1,1,1,0,0,1]:
                status_msg = 'Focus on current window'
                machine_state = 1

            elif confirmed_fingers == [1,0,0,0,0,0]:
                status_msg = 'Minimize'
                active_win.minimize()
                machine_state = 0

            pyautogui.hotkey('esc')
            time.sleep(1)

        elif machine_state == 1:

            if confirmed_fingers == [1, 0, 1, 0, 0, 0]:
                if active_win.isMaximized:
                    active_win.restore()
                pyautogui.hotkey('win', 'left')
                status_msg = 'LEFT HALF -> [Index]Top [Peace]Bottom'
                machine_state = 2

            elif confirmed_fingers == [1, 0, 1, 1, 0, 0]:
                if active_win.isMaximized:
                    active_win.restore()
                pyautogui.hotkey('win', 'right')
                status_msg = "RIGHT HALF -> [Index]Top [Peace]Bottom"
                machine_state = 2

            elif confirmed_fingers == [1,1,1,1,1,1]:
                active_win.maximize()
                status_msg = "Mxm"
                machine_state = 0 

                
            pyautogui.hotkey('esc')
            time.sleep(1)


        elif machine_state == 2:
             

            if confirmed_fingers == [1, 0, 1, 0, 0, 0]:
                pyautogui.hotkey('win', 'up')
                status_msg = "Snapped Top. Done."
                machine_state = 0 


            elif confirmed_fingers == [1, 0, 1, 1, 0, 0]:
                pyautogui.hotkey('win', 'down')
                status_msg = "Snapped Bottom. Done."
                machine_state = 0 

            pyautogui.press('esc')
            time.sleep(1)
            
        last_executed_gesture = confirmed_fingers
        print(f"Action: {status_msg}")

def gesture_worker():

    while True:
        
        fingers = gesture_queue.get()
        
        if fingers is None:
            break
        
        state_machine(fingers)
        gesture_queue.task_done()

def main():


    pTime = 0
    cTime = 0

    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Error")
        return
    
    detector = htm.handDetector()

    t = threading.Thread(target=gesture_worker)
    t.daemon = True
    t.start()

    print("System Ready. Thread Started.")


    while True:
        success,frame = capture.read()
        

        if not success:
            print("failed to grab frame")
            break

        frame = cv.flip(frame,1)

        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame)

        if lmList != 0:

            confirmed_fingers = detector.getConfirmFL(lmList)

            if confirmed_fingers is not None:

                gesture_queue.put(confirmed_fingers)
                cv.putText(frame, str(confirmed_fingers), (50, 50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

            else:
                cv.putText(frame, "Stabilizing...", (50, 50), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv.putText(frame,str(int(fps)),(10,70),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),3)   
        
        cv.imshow('Video',frame)

        if cv.waitKey(20)&0xFF==ord('d'):
            break



    gesture_queue.put(None)
    t.join()
    capture.release()
    cv.destroyAllWindows()

if  __name__ == "__main__":
    main()
   
           
   
        
      
      