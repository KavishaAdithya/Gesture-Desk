import pygetwindow as gw
import time
import sys
import ctypes
from ctypes import windll
import HandtrackingModule as htm
import cv2 as cv


SM_CMONITORS = 80
MONITOR_DEFAULTTONEAREST = 0x00000002
Def_RES = [1920,1080]


class RECT(ctypes.Structure):
    _fields_ = [
        ('left',ctypes.c_long),
        ('top',ctypes.c_long),
        ('right',ctypes.c_long),
        ('bottom',ctypes.c_long),
    ]

class MONITORINFO(ctypes.Structure):
    _fields_=[
        ('cbSize',ctypes.c_ulong),
        ('rcMonitor',RECT),
        ('rcWork',RECT),
        ('dwFlags',ctypes.c_ulong)

    ]

def get_Active_Window():

    try:
        active_Win = gw.getActiveWindow()
        # print(f'activeWin type : {type(active_Win)}')
        if active_Win:
            print(f'active window : {active_Win.width} X{active_Win.height}')
            print(f'center: {active_Win.centerx} X {active_Win.centery} ')

        else:
            print("failed to get active Win")

    except Exception as e:
        print(f'Error {e}')

def get_monitor_info():
    num_Monitors = windll.user32.GetSystemMetrics(SM_CMONITORS)    
    print(f"Monitors : {num_Monitors}")
    

    monitors = []
    


    def callback(monitor,dc,rect,data):
        info = MONITORINFO()

        info.cbSize = ctypes.sizeof(MONITORINFO)



        if windll.user32.GetMonitorInfoA(monitor,ctypes.byref(info)):

            monitor_Info = {
                'handle' : monitor,
                'left' : info.rcMonitor.left,
                'top':info.rcMonitor.top,
                'width': info.rcMonitor.right - info.rcMonitor.left,
                'height': info.rcMonitor.bottom - info.rcMonitor.top,
                'work_left': info.rcWork.left,
                'work_top': info.rcWork.top,
                'work_width': info.rcWork.right - info.rcWork.left,
                'work_height': info.rcWork.bottom - info.rcWork.top
                
            }
            monitors.append(monitor_Info)
            
        return True

    MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_ulong,ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_long)

    windll.user32.EnumDisplayMonitors(None,None, MONITORENUMPROC(callback),0)

    monitors.sort(key = lambda m:m['left'])

    
    for i,m in enumerate(monitors):

        print(print(f"Monitor {i+1}: {m['width']}x{m['height']} at position ({m['left']}, {m['top']})"))

    return monitors

def get_Get_ScaleFactors():

    scale_Factors = []

    monitors = get_monitor_info()

    for id,mon in enumerate(monitors):
        scale_Factors.append(Def_RES[1]/mon['height'])
    print (scale_Factors)

    return scale_Factors

def move_Active_Win(mon_Num,byTwo=0,Full=0,byThree=0,move =False):
    active_Win = gw.getActiveWindow()

    if not active_Win:
        return False

    monitors = get_monitor_info()
    scale = get_Get_ScaleFactors()

    if len(monitors)<2:
        print("only 1 monitor detected")
        return False

    x_cent,y_cent = active_Win.center
    x,y= active_Win.topleft
    

    print(x_cent,y_cent)
    print(x,y)
    

    active_monitor = 0

    for id,m in enumerate(monitors):
        if (m['left']<= x_cent < m['left']+ m['width'])&(m['top']<= y_cent < m['top']+m['height']):
            active_monitor = id+1
            break


    print(f'active Monitor : {active_monitor}')

    if byTwo:
        active_Win.restore()
        active_Win.resizeTo(int((monitors[active_monitor-1]['width']//2)),int(monitors[active_monitor-1]['height']))
        active_Win.moveTo(int(monitors[active_monitor-1]['left']),int(monitors[active_monitor-1]['top']))
        

    if byThree:
        active_Win.restore()
        active_Win.resizeTo(int(monitors[active_monitor-1]['width']//2),int(monitors[active_monitor-1]['height']))
        active_Win.moveTo(int(monitors[active_monitor-1]['left']+monitors[active_monitor-1]['width']//2),int(monitors[active_monitor-1]['top']))

    if move:
        active_Win.restore()
        
        active_Win.resizeTo(int(monitors[mon_Num]['width']//((scale[mon_Num]))),int(monitors[mon_Num]['height']//(scale[mon_Num])))
        
        active_Win.moveTo(monitors[mon_Num]['left'],monitors[mon_Num]['top'])

        print(f'active mon num :{mon_Num}')

    if Full:
        active_Win.maximize()

    get_Active_Window()
    get_Get_ScaleFactors()
    
def main():
    pTime = 0
    cTime = 0
    capture = cv.VideoCapture(0)
    if capture.isOpened():
        print("Error")
    detector = htm.handDetector()
    
    while True:
        success,frame = capture.read()

        if not success:
            print("failed to grab frame")
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame)
        fingerList = detector.fingerCount(lmList)

        # print(fingerList)
        

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv.putText(frame,str(int(fps)),(10,70),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),3)   

        cv.imshow('Video',frame)
        

        if cv.waitKey(20)&0xFF==ord('d'):
            break


        if fingerList == [0,1,0,0,0]:
            get_monitor_info()
            get_Active_Window()
            get_Get_ScaleFactors()
            move_Active_Win(mon_Num=0,move=True)

        elif fingerList == [0,1,1,0,0]:
            get_monitor_info()
            get_Active_Window()
            get_Get_ScaleFactors()
            move_Active_Win(mon_Num=1,move=True)

        elif fingerList == [1,1,0,0,0]:
            get_monitor_info()
            get_Active_Window()
            get_Get_ScaleFactors()
            move_Active_Win(mon_Num=1,byTwo=1)
        
        elif fingerList == [1,0,0,0,1]:
            get_monitor_info()
            get_Active_Window()
            get_Get_ScaleFactors()
            move_Active_Win(mon_Num=1,Full=1)

        elif fingerList == [1,1,1,0,0]:
            get_monitor_info()
            get_Active_Window()
            get_Get_ScaleFactors()
            move_Active_Win(mon_Num=1,byThree=1)
        
        elif fingerList == [1,0,0,0,0]:

            windows_obj = gw.getAllWindows()
        
            for window in windows_obj:  
                if not window.isMinimized:
                
                    try:
                        window.minimize()

                    except Exception as e:
                        print(f"Error minimizing{e}")

        elif fingerList == [0,0,0,0,1]:
            windows_obj = gw.getAllWindows()
        
            for window in windows_obj:  
                if window.isMinimized:
                
                    try:
                        window.restore()

                    except Exception as e:
                        print(f"Error minimizing{e}")



    capture.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
    
   
           
   
        
      
      