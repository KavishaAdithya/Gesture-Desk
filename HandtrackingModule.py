import cv2 as cv
import mediapipe as mp
import time


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
        fingerList = []
        if len(lmList) != 0:
            if lmList[tipId[0]][1] < lmList[tipId[0] - 2][1]:
                fingerList.append(1)
            else:
                fingerList.append(0)


            for Id in range(1,5):
                if lmList[tipId[Id]][2] < lmList[tipId[Id] - 2][2]:
                    fingerList.append(1)
                else:
                    fingerList.append(0)

        else:
            fingerList = [0,0,0,0,0]

        return fingerList
        
def main():
    
    pTime = 0
    cTime = 0
    capture = cv.VideoCapture(0)
    if capture.isOpened():
        print("Error")
    detector = handDetector()
    
    while True:
        success,frame = capture.read()

        if not success:
            print("failed to grab frame")
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame)
        fingerList = detector.fingerCount(lmList)

        print(fingerList)
        

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