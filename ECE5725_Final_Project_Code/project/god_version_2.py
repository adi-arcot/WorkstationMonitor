import RPi.GPIO as GPIO

import serial
import time
import os

import pygame
from pygame.locals import *
from time import sleep
import pigpio
import cv2 

from adafruit_pn532.uart import PN532_UART

import os
import mysql.connector as database

import multiprocessing

username = os.environ.get("username")
password = os.environ.get("password")

#Connect to mariadb
connection = database.connect(user='default', password='password',
 host="localhost", database="final_project")

#Cursor to move through rows of 'users' table
cursor = connection.cursor()
def update_ws_table(ws, status_, remaining_time):
  try:
    statement = "UPDATE ws_occupancy SET status_ = %s, remaining_time = %s WHERE workstation = %s"

    data = (status_, remaining_time, ws)
    cursor.execute(statement, data)
    connection.commit()
    #print("Successfully modified WS occupancy to")

  except database.Error as e:
    print("Error entering database information from update_ws_table: {e}")

def increment_access_count(first_name, WS):
  try:

    if (WS == 1):
      statement = "UPDATE users SET WS1_noof_access = WS1_noof_access  + 1 WHERE first_name = %s"
    elif(WS == 2):
      statement = "UPDATE users SET WS2_noof_access = WS2_noof_access  + 1 WHERE first_name = %s"

    data = (first_name,)
    cursor.execute(statement, data)
    connection.commit()
    print("Successfully incremented Workstation %s access count" % WS)

  except database.Error as e:
    print("Error entering database information from increment access count: {e}")


def check_name(rfid):
    try:
        query = "SELECT COUNT(*) FROM users WHERE rfid = %s"
        cursor.execute(query, (rfid,))
        result = cursor.fetchone()
        if result[0] == 0:
           return False
        else:
            return True
    except Exception as e:
        print(f"Error: {e}")


def check_num():
    try:
        statement = "SELECT COUNT(*) FROM users"
        cursor.execute(statement)
        result = cursor.fetchone()

        return result
    except Exception as e:
        print(f"Error: {e}")

def add(first_name,rfid):
    try:  
        statement = "INSERT INTO users (first_name,rfid) VALUES (%s, %s)"
        data = (first_name, rfid)
        cursor.execute(statement, data)
        connection.commit()
        print("Successfully added user to database")
    except database.Error as e:
        print("Error entering database information: %s" % e)

def get_data(rfid):
    try:
      statement = "SELECT first_name, rfid FROM users WHERE rfid=%s"
      data = (rfid,)
      cursor.execute(statement, data)
      for (first_name, rfid) in cursor:
        print(f"Successfully retrieved {first_name}, {rfid}")
        return first_name
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")
      return False

def modify_session_time(first_name, WS, session_time):
  try:
    if (WS == 1):
      statement = "UPDATE users SET WS1_total_time = WS1_total_time + %s WHERE first_name = %s"
    elif(WS == 2):
      statement = "UPDATE users SET WS2_total_time =  WS2_total_time + %s WHERE first_name = %s"


    data = (session_time, first_name)
    cursor.execute(statement, data)
    connection.commit()
    print("Successfully updated WS %d time" % WS)

  except database.Error as e:
    print("Error entering database information: {e}")

os.putenv('SDL_VIDEODRIVER','fbcon') #Display on piTFT
os.putenv('SDL_FBDEV','/dev/fb0')
os.putenv('SDL_MOUSEDRV','TSLIB') #Track mouse clicks on PiTFT
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

pygame.init()

pygame.mouse.set_visible(False)
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
workstation_user = { 1:1, 2:1}
user_id = {0: "Available", 1: "Devin", 2:"Yi", 3: "Adi"}

#rfid_tags = {[174,96,0,144] : 1, [254,103,7,144] : 2, [244,247,167,34] : 3}
# rfid_tags = { "174,96,0,144":"Devin" , "254,103,7,144":"Yi" ,'244,247,167,34':"Adi","0":"Available"}
rfid_tags = { 1:"Available", 0:"-"}

#def return_name(tag):
    


my_font = pygame.font.Font(None, 25)
#my_buttons = {'button1':(80, 180), 'button2':(240, 180)}
my_buttons = {(160, 40):'Workstation Activity', (60, 100):'Station 1:', (60, 140):'Station 2'}
workstation_status = {(160, 100): '%s'%(rfid_tags[workstation_user[1]]), (160, 140): '%s'%(rfid_tags[workstation_user[2]])}
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
#servo_pin = 12
#SW6 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SW1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW3, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SW4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26,GPIO.OUT)
#GPIO.setup(servo_pin, GPIO.OUT)

def quit_callback(channel):
    GPIO.output(LED,GPIO.LOW)
    global code_run
    print("*************************Code exiting************")

    # code_run=False
    code_run.value= 0

    # code_run = False  
   
time_limit = 300 
start_time = time.time()
code_run = True

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
                    pass
    
    return img,objectInfo

def rotate_cam(pos):
    if(pos == 0):
        print("camera turn right")
        pi_hw.hardware_PWM(12, 50, 90000)
        #sleep(5)
        return 1
    elif(pos == 1):
        print("camera turn left")
        pi_hw.hardware_PWM(12, 50, 45000)
        #sleep(5)
        return 0

#Camera Call function
def check_camera(person_present1, person_present2, check, code_run):
    GPIO.add_event_detect(SW1, GPIO.FALLING, callback=quit_callback, bouncetime=300)
    

    pi_hw.hardware_PWM(12, 50, 45000)
    timeout1=0
    timeout2=0
    #sleep(1)
    pos = 0 #position of camera
    print("process started")
    # global person_present
    print(code_run.value)
    while(code_run.value==1):
        print("running"+ str(check.value))
        #Below is the never ending loop that determines what will happen when an object is identified.    
        #success, img = cap.read()
        #Below provides a huge amount of controll. the 0.45 number is the threshold number, the 0.2 number is the nms number)
        
        #print(objectInfo)
        
        if(check.value == 0):
            if(pos == 1):
                pos = rotate_cam(pos)
                time.sleep(5)
                # time.sleep(2)
            print("Checking camera 1")
            os.system('raspistill -w 640 -h 480 -t 2000 -n -o  /home/pi/Desktop/image.jpg')
            img = cv2.imread("/home/pi/Desktop/image.jpg")
            result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
            print("Result is")
            print(objectInfo)
            if (not objectInfo):
                if(timeout1==1):
                    person_present1.value = 0
                    timeout1 = 0
                    time.sleep(3)
                else: 
                    person_present1.value = 1
                    timeout1 = 1
                    time.sleep(3)
                    print("time")
            else:
                person_present1.value = 1
                timeout1 = 0

        if(check.value == 1):
            if(pos == 0):
                pos = rotate_cam(pos)
                time.sleep(5)
                #time.sleep(5)
            print("Checking camera 2")
            os.system('raspistill -w 640 -h 480 -t 2000 -n -o  /home/pi/Desktop/image.jpg')
            img = cv2.imread("/home/pi/Desktop/image.jpg")
            result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
            print("Result is")
            print(objectInfo)
            if (not objectInfo):
                if(timeout2==1):
                    person_present2.value = 0
                    timeout2 = 0
                    time.sleep(3)
                else: 
                    person_present2.value = 1
                    timeout2 = 1
                    time.sleep(3)
            else:
                person_present2.value = 1
                timeout2 = 0
                
            
        if(check.value == 2):
            if(pos == 1):
                pos = rotate_cam(pos)
                time.sleep(5)
            print("Checking camera 1")
            os.system('raspistill -w 640 -h 480 -t 2000 -n -o  /home/pi/Desktop/image.jpg')
            img = cv2.imread("/home/pi/Desktop/image.jpg")
            result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
            print("Result is")
            print(objectInfo)
            if (not objectInfo):
                if(timeout1==1):
                    person_present1.value = 0
                    timeout1 = 0
                    time.sleep(3)
                else: 
                    person_present1.value = 1
                    timeout1 = 1
                    time.sleep(3)
                    print("timeout1")
            else:
                person_present1.value = 1
                timeout1 = 0
            
            if(pos == 0):
                pos = rotate_cam(pos)
                time.sleep(5)
            print("Checking camera 2")
            os.system('raspistill -w 640 -h 480 -t 2000 -n -o  /home/pi/Desktop/image.jpg')
            img = cv2.imread("/home/pi/Desktop/image.jpg")
            result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
            print("Result is")
            print(objectInfo)
            if (not objectInfo):
                if(timeout2==1):
                    person_present2.value = 0
                    timeout2 = 0
                    time.sleep(5)
                else: 
                    person_present2.value = 1
                    timeout2 = 1
                    time.sleep(5)
                    print("timeout2")
            else:
                person_present2.value = 1
                timeout2 = 0
        
        cv2.waitKey(1)
       



def rfid_read():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        return None
    else:
        la = [str(i) for i in uid]
        tag = ','.join(la)
        return tag
        
pi_hw = pigpio.pi()
#Declare Camera thread

#Main while
username1 = None
def main_program(person_present1, person_present2,  check,code_run):
    GPIO.add_event_detect(SW1, GPIO.FALLING, callback=quit_callback, bouncetime=300)

  
    st1 = True
    st2 = True
    
    

   
    username1 = None
    username2 = None
    
    
    time1 = 0
    time2 = 0
        
    pi_hw.hardware_PWM(12, 50, 45000)
    #sleep(1)
    
    while(code_run.value == 1):

        if(workstation_user[1]==1 or workstation_user[2]==1):
            temp = rfid_read()
            if(temp != None):
                tag = temp
                print(tag)
                if(workstation_user[1]==1):
                    print(check_name(tag))
                    if(check_name(tag)):
                        print(get_data(tag))
                        username1temp = get_data(tag)
                    else:
                        name = "User" + str(check_num()[0]+1)
                        add(name,tag)
                        username1temp = name
                    print(username2)
                    if(username2 != username1temp):
                        username1 = username1temp
                        workstation_user[1] = 0
                        workstation_time[1] = 120
                elif(workstation_user[2]==1):
                    if(check_name(tag)):
                        username2temp = get_data(tag)
                    else:
                        name = "User" + str(check_num()[0]+1)
                        add(name,tag)
                        username2temp = name
                    if(username1 != username2temp):
                        username2 = username2temp
                        workstation_user[2] = 0
                        workstation_time[2] = 120


        
       
       
        if(workstation_user[1] and workstation_user[2]):
            workstation_status = {(160, 100): '%s' % (rfid_tags[1]), (160, 140): '%s' % (rfid_tags[1])}
            update_ws_table(1, "Available", workstation_time[1])
            update_ws_table(2, "Available", workstation_time[2])
            check.value = 0

            
        elif(workstation_user[1] and not (workstation_user[2])):
            workstation_status = {(160, 100): '%s'%(rfid_tags[1]), (160, 140): '%s'%(username2)}
            update_ws_table(1, "Available", workstation_time[1])
            update_ws_table(2, username2, workstation_time[2])
            check.value = 1

        elif(not workstation_user[1] and (workstation_user[2])):
            workstation_status = {(160, 100): '%s'%(username1), (160, 140): '%s'%(rfid_tags[1])}
            update_ws_table(1, username1, workstation_time[1])
            update_ws_table(2, "Available", workstation_time[2])
            check.value = 0

            

        else:
            workstation_status = {(160, 100): '%s'%(username1), (160, 140): '%s'%(username2)}
            update_ws_table(1, username1, workstation_time[1])
            update_ws_table(2, username2, workstation_time[2])
            check.value = 2
                          
        my_times = { (240, 100):'%d'%(workstation_time[1]), (240, 140):'%d'%(workstation_time[2])}
        
      
        
        
        if(workstation_time[1]>0 ):
            if(time.time()-time1>1):
                workstation_time[1] = workstation_time[1] - 1

                time1 = time.time()
            
                if (workstation_time[1] == 116):
                    increment_access_count(username1, 1)
                
                if(workstation_time[1]<100):
                    if(person_present1.value == 0):
                        workstation_user[1] = 1
                        
                        modify_session_time(username1,1,120-workstation_time[1])
                        username1 = None
                        workstation_time[1] = 0
                if(workstation_time[1]==1 and st1):
                    modify_session_time(username1,1,120)
                    st1 = False
                        
                if(workstation_time[1]==0):
                    workstation_user[1] = 1
                    username1 = None
                    st1 = True
                    
        if(workstation_time[2]>0 ):
            if(time.time()-time2>1):
                workstation_time[2] = workstation_time[2] - 1
                time2 = time.time()
                if (workstation_time[2] == 116):
                    increment_access_count(username2, 2)
                
                if(workstation_time[2]<100):
                    if(person_present2.value == 0):
                        workstation_user[2] = 1
                        
                        modify_session_time(username2,2,120-workstation_time[2])
                        username2 = None
                        workstation_time[2] = 0
                
                if(workstation_time[2]==1 and st2):
                    modify_session_time(username2,2,120)
                    st2 = False
                        
                if(workstation_time[2]==0):
                    workstation_user[2] = 1
                    st2 = True
                    username2 = None


                


            
    
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
        

   
            
        screen.fill(BLACK)
        time.sleep(1/60)
 
if __name__ == "__main__":

    code_run = multiprocessing.Value('i', 1)
    person_present1 = multiprocessing.Value('i', 1)
    person_present2 = multiprocessing.Value('i', 1)
    check = multiprocessing.Value('i', 0)
    process = multiprocessing.Process(target = check_camera, args=(person_present1, person_present2, check, code_run,  ))
    process1 = multiprocessing.Process(target = main_program, args=(person_present1, person_present2, check, code_run,  ))

    process.start()
    process1.start()

    process.join()
    process1.join()


    
