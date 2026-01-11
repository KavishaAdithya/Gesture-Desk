import cv2 as cv
import mediapipe as mp
import time
from collections import deque

class handDetector():

    def __init__(self,mode=False,maxHands=2,model_complexity=1,detectionCon=0.5,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.model_complexity = model_complexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,min_detection_confidence=self.detectionCon,min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None 
        self.stability_frames = 7
        self.history = deque(maxlen=self.stability_frames)
        self.current_ConfirmedFL = [0,0,0,0,0,0]
        self.last_state = []
        self.action_text = "Waiting.."


    def findHands(self,frame,draw = True):
        imgRGB = cv.cvtColor(frame,cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(frame,handLms,self.mpHands.HAND_CONNECTIONS)
        return frame


    def findPosition(self,frame,handNo = 0,draw = True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id,lm in enumerate(myHand.landmark):
                h,w,c = frame.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv.circle(frame,(cx,cy),7,(255,0,255),cv.FILLED)
      
        return lmList
    

    def fingerCount(self,lmList):

            tipId = [4,8,12,16,20]

            hand = 0

            fingerList = []
            if len(lmList) != 0:

                fingerList.append(1)

                if lmList[0][1] - lmList[1][1]<0:
                    hand = 2

                else:
                    hand = 1

                if lmList[tipId[0]][1] < lmList[tipId[0] - 2][1] and hand == 1:
                    fingerList.append(1)


                elif lmList[tipId[0]][1] > lmList[tipId[0] - 2][1] and hand == 2:
                    fingerList.append(1)

                else:
                    fingerList.append(0)


                for Id in range(1,5):
                    if lmList[tipId[Id]][2] < lmList[tipId[Id] - 2][2]:
                        fingerList.append(1)
                    else:
                        fingerList.append(0)

                # fingerList.append(hand)

            else:
                fingerList = [0,0,0,0,0,0]

            return fingerList


    def getConfirmFL(self,lmList):

        current_fingers = self.fingerCount(lmList)

        if len(self.history) == 0:
            self.history.append(current_fingers)
            return None 

        
        last_fingers = self.history[-1]

        if current_fingers == last_fingers:
            
            self.history.append(current_fingers)
            
            
            if len(self.history) == self.stability_frames:
                return current_fingers 
            else:
                return None 
        else:
            
            self.history.clear()
            
            self.history.append(current_fingers)
            return None 
        
                  
def main():
    
    pTime = 0
    cTime = 0
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Error")
        return
    
    detector = handDetector()

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
                
                cv.putText(frame, str(confirmed_fingers), (50, 50), cv.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            else:
                
                cv.putText(frame, "Stabilizing...", (50, 50), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            gesture = detector.StateMachine(confirmed_fingers)

            cv.putText(frame, gesture, (100, 50), cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv.putText(frame,str(int(fps)),(10,70),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),3)   
        
        cv.imshow('Video',frame)

        if cv.waitKey(20)&0xFF==ord('d'):
            break

    capture.release()
    cv.destroyAllWindows()

if  __name__ == "__main__":
    main()