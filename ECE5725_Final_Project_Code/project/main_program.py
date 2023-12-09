import RPi.GPIO as GPIO
import subprocess
import serial
import time
import os
import sys
import pygame
from pygame.locals import *
import cv2 
#import digitalio 
from adafruit_pn532.uart import PN532_UART


#os.putenv('SDL_VIDEODRIVER','fbcon') #Display on piTFT
#os.putenv('SDL_FBDEV','/dev/fb1')
#os.putenv('SDL_MOUSEDRV','TSLIB') #Track mouse clicks on PiTFT
#os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

pygame.init()

#pygame.mouse.set_visible(False)
WHITE = 255, 255, 255
BLACK = 0,0,0
GREEN = 0, 255, 0
RED = 255, 0, 0
screen=pygame.display.set_mode((320, 240))


#uart setup
uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
pn532 = PN532_UART(uart, debug=False)
ic, ver, rev, support = pn532.firmware_version
#Configure PN532
pn532.SAM_configuration()

#Wrokstation user   workstation : user_id
workstation_user = {1:0, 2:0}
user_id = {0: "Available", 1: "Devin", 2:"Yi", 3: "Adi"}

#rfid_tags = {[174,96,0,144] : 1, [254,103,7,144] : 2, [244,247,167,34] : 3}
rfid_tags = {174 : 1, 254 : 2, 244 : 3}

my_font = pygame.font.Font(None, 25)
#my_buttons = {'button1':(80, 180), 'button2':(240, 180)}
my_buttons = {(160, 40):'Workstation Activity', (60, 100):'Station 1:', (60, 140):'Station 2'}
workstation_status = {(160, 100): '%s'%(user_id[workstation_user[1]]), (160, 140): '%s'%(user_id[workstation_user[2]])}
workstation_time = {1:0, 2:0} 
my_times = { (240, 100):'%d'%(workstation_time[1]), (240, 140):'%d'%(workstation_time[2])}



screen.fill(BLACK)

my_buttons_rect= {}

for text_pos, my_text in my_buttons.items():
    text_surface = my_font.render(my_text, True, WHITE)
    rect = text_surface.get_rect(center = text_pos)
    screen.blit(text_surface, rect)
    my_buttons_rect[my_text] = rect

    #position_text = 'touch at {}, {}'
    #position_text_surface = my_font.render(position_text, True, WHITE)
    #position_text_rect = position_text_surface.get_rect(center = (160, 120))
    #screen.blit(position_text_surface,position_text_rect)

for text_pos, my_text in workstation_status.items():
    if (my_text == "Available"):
        text_surface = my_font.render(my_text, True, GREEN)
    else:
        text_surface = my_font.render(my_text, True, RED)
    rect = text_surface.get_rect(center = text_pos)
    screen.blit(text_surface, rect)
    #my_buttons_rect[my_text] = rect

pygame.display.flip()


#define switches to be used
SW1 = 17
SW2 = 22
SW3 = 23
SW4 = 27
LED = 26
#SW6 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SW1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(SW5, GPIO.IN)
#GPIO.setup(SW6, GPIO.IN)
#GPIO.setwarning(False)
GPIO.setup(26,GPIO.OUT)

def quit_callback(channel):
    GPIO.output(LED,GPIO.LOW)
    GPIO.cleanup()
    global code_run
    code_run = False  
   
GPIO.add_event_detect(SW1, GPIO.FALLING, callback=quit_callback, bouncetime=300)

time_limit = 300 
start_time = time.time()
code_run = True

last_time1=0
last_time2=0

check1_f = float(30.1)
check1_int = 0

check1 = 0
check1_time = 0
GPIO.output(LED,GPIO.LOW)







#Open CV Functions
#This is to pull the information about what each object is called
classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

#This is to pull the information about what each object should look like
configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

#This is some set up values to get good results
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)







#This is to set up what the drawn box size/colour is and the font/size/colour of the name tag and confidence label   
def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
#Below has been commented out, if you want to print each sighting of an object to the console you can uncomment below     
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects: 
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    #print(box)
                    #print(className)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    
    return img,objectInfo



#Camera Call function

def check_camera():
    print("Checking camera")
    os.system('raspistill -w 640 -h 480 -o Desktop/image.jpg')
    img = cv2.imread("Desktop/image.jpg")
    #Below is the never ending loop that determines what will happen when an object is identified.    
    #success, img = cap.read()
    #Below provides a huge amount of controll. the 0.45 number is the threshold number, the 0.2 number is the nms number)
    result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
    #print(objectInfo)
    #cv2.imshow("Output",img)
    cv2.waitKey(1)
    return objectInfo



def rfid_read():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None or (workstation_user[1]!=0 and workstation_user[2]!=0) :
        pass
    else:
        #print("UID number is: ",[int(i) for i in uid])
        if(workstation_user[1]==0):
            l = [int(i) for i in uid]
            workstation_user[1] = rfid_tags[l[0]]
            workstation_time[1] = 30
        elif(workstation_user[2]==0):
            l = [int(i) for i in uid]
            workstation_user[2] = rfid_tags[l[0]]
            workstation_time[2] = 30
        
    #if uid is (not None):
    #    pass
    #else:
    #    print("No UID found")

#Main while
while (code_run):
    rfid_read()
    now = time.time()
    elapsed_time = now-start_time
    workstation_status = {(160, 100): '%s'%(user_id[workstation_user[1]]), (160, 140): '%s'%(user_id[workstation_user[2]])}
    my_times = { (240, 100):'%d'%(workstation_time[1]), (240, 140):'%d'%(workstation_time[2])}
    
    if(workstation_time[1]>0 and time.time()-last_time1>1):
        workstation_time[1] = workstation_time[1] - 1
        last_time1 = time.time();
        check1_f = workstation_time[1] / 5.0 # float devision
        check1_int = int(check1_f)
        print(check1_f)
        print(check1_int)
        if(check1_f == check1_int):
            print("CHECK")
            result = check_camera()
            print(result)
            if (not result):
                workstation_user[1] = 0
                check1 = 0
                workstation_time[1] = 0
                GPIO.output(LED,GPIO.LOW)
                
                #check1 = 1
                #check1_time = workstation_time[1]
                #GPIO.output(LED,GPIO.HIGH)

                
    if(check1 and (check1_time - workstation_time[1] < 3)):
        if(not GPIO.input(SW4)):
            check1 = 0
            GPIO.output(LED,GPIO.LOW)
    elif(check1 and (check1_time - workstation_time[1] >= 3)):
        workstation_user[1] = 0
        check1 = 0
        workstation_time[1] = 0
        GPIO.output(LED,GPIO.LOW)
            
        
        
    if(workstation_time[1]==0):
         workstation_user[1] = 0
         
    
         
         
    if(workstation_time[2]>0 and time.time()-last_time2>1):
        workstation_time[2] = workstation_time[2] - 1
        last_time2 = time.time();
        
    if(workstation_time[2]==0):
         workstation_user[2] = 0
    

        
        
        
    if(not GPIO.input(SW2)):
        
        workstation_user[1] = 1
        workstation_time[1] = 30
        
         
        time.sleep(1)
        
    if(not GPIO.input(SW3)):
        
        workstation_user[2] = 2
        workstation_time[2] = 30
        
         
        time.sleep(1)
        
    #else if (not GPIO.input(SW3))
    for text_pos, my_text in my_buttons.items():
        text_surface = my_font.render(my_text, True, WHITE)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        my_buttons_rect[my_text] = rect


    for text_pos, my_text in workstation_status.items():
        if (my_text == "Available"):
            text_surface = my_font.render(my_text, True, GREEN)
        else:
            text_surface = my_font.render(my_text, True, RED)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        #my_buttons_rect[my_text] = rect
        
    for text_pos, my_text in my_times.items():
        if(my_text != "0"):
            text_surface = my_font.render(my_text, True, RED)
            rect = text_surface.get_rect(center = text_pos)
            screen.blit(text_surface, rect)
            my_buttons_rect[my_text] = rect


    pygame.display.flip()
    pygame.image.save(screen,"screen.jpg")
    
    if (elapsed_time > time_limit):
        code_run = False
        
        
    screen.fill(BLACK)
    time.sleep(1/60)
 


