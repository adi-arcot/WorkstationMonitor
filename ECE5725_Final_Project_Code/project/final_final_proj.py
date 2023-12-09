import RPi.GPIO as GPIO
import subprocess
import serial
import time
import os
import sys
import pygame
from pygame.locals import *
from time import sleep
import pigpio
import cv2 
#import digitalio 
from adafruit_pn532.uart import PN532_UART
#from  database_test import get_data
import os
import mysql.connector as database
# from threading import Thread
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

# def get_data(rfid):
#     try:
#       statement = "SELECT first_name, rfid FROM users WHERE rfid=%s"
#       data = (rfid,)
#       cursor.execute(statement, data)
#       for (first_name, rfid) in cursor:
#         print(f"Successfully retrieved {first_name}, {rfid}")
#         return first_name
      
#     except database.Error as e:
#         statement1 = "SELECT COUNT(*) FROM users"
#         cursor.execute(statement1)
#         result = cursor.fetchone()[0] + 1
#         print("Result is")
#         print(result)
#         name ="User%i"%result
#         statement = "INSERT INTO users (name,rfid) VALUES (%s, %s)"
#     #   statement = "SELECT first_name, rfid FROM users WHERE rfid=%s"
#         data = (name,rfid)
#         cursor.execute(statement, data)
#         connection.commit()
#         print("Successfully added user to database")

#         return name
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

#Camera Call function
def check_camera(person_present, code_run):
    GPIO.add_event_detect(SW1, GPIO.FALLING, callback=quit_callback, bouncetime=300)

    # global person_present
    while(code_run.value==1):
        print("Checking camera")
        os.system('raspistill -w 640 -h 480 -t 2000 -n -o  /home/pi/Desktop/image.jpg')
        img = cv2.imread("/home/pi/Desktop/image.jpg")
        #Below is the never ending loop that determines what will happen when an object is identified.    
        #success, img = cap.read()
        #Below provides a huge amount of controll. the 0.45 number is the threshold number, the 0.2 number is the nms number)
        result, objectInfo = getObjects(img,0.60,1, objects = ['person'])
        #print(objectInfo)
        print("Result is")
        print(objectInfo)
        if (not objectInfo):
            person_present.value = 0
        else:
            person_present.value = 1
        #cv2.imshow("Output",img)
        cv2.waitKey(1)
       

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

def rfid_read():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        return None
    else:
        #print("UID number is: ",[int(i) for i in uid])
        # if(workstation_user[1]==1):
            #l = [int(i) for i in uid]
        la = [str(i) for i in uid]
        tag = ','.join(la)
        return tag
        
pi_hw = pigpio.pi()
#Declare Camera thread

#Main while
username1 = None
def main_program(person_present, code_run):
    GPIO.add_event_detect(SW1, GPIO.FALLING, callback=quit_callback, bouncetime=300)

    global check1
    st1 = True
    st2 = True
    timeout1 = False
    timeout2 = False
    last_time1=0
    last_time2=0
    check1_f = float(60.1)
    check1_int = 0
    check1 = 0
    check1_time = 0
    check2_f = float(60.1)
    check2_int = 0
    check2 = 0
    check2_time = 0
    username1 = None
    username2 = None
    
    checkCam1 = 0
    checkCam2 = 0
        
    pi_hw.hardware_PWM(12, 50, 45000)
    #sleep(1)
    pos = 0 #position of camera
    while(code_run.value == 1):

    # while (code_run):
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
                        workstation_time[1] = 90
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
                        workstation_time[2] = 90


        
        now = time.time()
        elapsed_time = now-start_time
        if(workstation_user[1] and workstation_user[2]):
            workstation_status = {(160, 100): '%s' % (rfid_tags[1]), (160, 140): '%s' % (rfid_tags[1])}
            update_ws_table(1, "Available", workstation_time[1])
            update_ws_table(2, "Available", workstation_time[2])

            
        elif(workstation_user[1] and not (workstation_user[2])):
            workstation_status = {(160, 100): '%s'%(rfid_tags[1]), (160, 140): '%s'%(username2)}
            update_ws_table(1, "Available", workstation_time[1])
            update_ws_table(2, username2, workstation_time[2])

        elif(not workstation_user[1] and (workstation_user[2])):
            workstation_status = {(160, 100): '%s'%(username1), (160, 140): '%s'%(rfid_tags[1])}
            update_ws_table(1, username1, workstation_time[1])
            update_ws_table(2, "Available", workstation_time[2])

            

        else:
            workstation_status = {(160, 100): '%s'%(username1), (160, 140): '%s'%(username2)}
            update_ws_table(1, username1, workstation_time[1])
            update_ws_table(2, username2, workstation_time[2])
                          
        my_times = { (240, 100):'%d'%(workstation_time[1]), (240, 140):'%d'%(workstation_time[2])}
        
        # if((workstation_time[1]>0 or workstation_time[2]>0) and ( or (time.time()-last_time2>1))):
            
            #Update database for WS1
        if(workstation_time[1]>0 and (time.time()-last_time1>1)):
                if (workstation_time[1] == 86):
                    increment_access_count(username1, 1)

                workstation_time[1] = workstation_time[1] - 1

                last_time1 = time.time()
                
                check1_f = int(time.time() + 15) / 30.0 # float devision
                print(check1_f)
                check1_int = int(check1_f)
                #print(check1_f)
                #print(check1_int)
                #if(not workstation_user[2]): #if the other user is not logged in, rotate camera immediately
                 #   if(pos == 1):
                  #      pos = rotate_cam(pos)
                check1_time = check1_time + check1
                print("check1 time")
                print(check1_time)
                print(check1)
                #if(not workstation_user[2]):
                #    if(pos == 1):
                #        pos = rotate_cam(pos)
                if(check1_f == check1_int):
                    check1 = 1
                    #check1_time = check1_int
                    if(pos == 1):
                        pos = rotate_cam(pos)
                        
                    print("CHECK1")
                    # result = check_camera()
                    #print(result[0][0] or result[1][0] or result[2][0] )
                    # print(result[0][0])
                    print(person_present.value)

                if(pos == 0 and check1_time > 10):
                    #if(person_present.value):
                    #    timeout1 = False
                    if (not person_present.value):
                            
                        # if (0<result[0][0]<150):
                        workstation_user[1] = 1
                        check1 = 0
                        check1_time = 0
                        check2_time = 0
                        modify_session_time(username1,1,90-workstation_time[1])
                        username1 = None
                        workstation_time[1] = 0
                        GPIO.output(LED,GPIO.LOW)
                        timeout1 =False
                                
                        #elif(not person_present.value and not timeout1):
                        #        timeout1 =True
                    #print("position of the camera is:")
                    #print(pos)
               

                if(workstation_time[1]==1 and st1):
                    modify_session_time(username1,1,90)
                    username1 = None
                    st1 = False
                        
                if(workstation_time[1]==0):
                    workstation_user[1] = 1
                    st1 = True

        if(workstation_time[2]>0 and (time.time()-last_time2>1)):
                #if(not workstation_user[1]):
                #    if(pos == 0):
                #        pos = rotate_cam(pos)
                if (workstation_time[2] == 86):
                    increment_access_count(username2, 2)

                workstation_time[2] = workstation_time[2] - 1

                last_time2 = time.time()
                check2_f = int(time.time()) / 30.0 # float devision
                check2_int = int(check2_f)
                #print(check1_f)
                #print(check1_int)
                #if(not workstation_user[1]): #if the other user is not logged in, rotate camera immediately
                 #   if(pos == 0):
                  #      pos = rotate_cam(pos)
                check2_time = check2_time + check2
                print("chech2 time")
                print(check2_time)
                if(check2_f == check2_int):
                    check2 = 1
                    if(pos == 0):
                        pos = rotate_cam(pos)
                    print("CHECK2")
                    # result = check_camera()
                    #print(result[0][0] or result[1][0] or result[2][0] )
                    # print(result[0][0])
                    print(person_present.value)

                if(pos==1 and check2_time > 10):
                    #if(person_present.value):
                    #    timeout2 =False
                    if (not person_present.value):
                            
                        # if (0<result[0][0]<150):
                        workstation_user[2] = 1
                        check2 = 0
                        check2_time = 0
                        check1_time = 0
                        modify_session_time(username2,2,90-workstation_time[2])
                        username2 = None
                        workstation_time[2] = 0
                        GPIO.output(LED,GPIO.LOW)
                        timeout2 =False
                                
                        #elif(not person_present.value and not timeout2):
                        #        timeout2 =True
                    #print("position of the camera is:")
                    #print(pos)
                    
                    
              

                if(workstation_time[2]==1 and st2):
                    modify_session_time(username2,2,90)
                    username2 = None
                    st2 = False
                        
                if(workstation_time[2]==0):
                    workstation_user[2] = 1
                    st2 = True




            
            
        # if(workstation_time[2]>0 and time.time()-last_time2>1):
        #     #Update database for WS2
        #     if (workstation_time[2] == 26):
        #         increment_access_count(username2, 2)
        #     workstation_time[2] = workstation_time[2] - 1
        #     last_time2 = time.time()
            
        # if(workstation_time[2]==1 and st2):
        #     modify_session_time(username2,2,30)
        #     st2 = False
                
        # if(workstation_time[2]==0):
        #     workstation_user[2] = 1
        #     st2 = True
            # increment_access_count(username2, 2)

        
        # if(not GPIO.input(SW2)):
            
        #     workstation_user[1] = "1"
        #     workstation_time[1] = 30
            
            
        #     time.sleep(1)
            
        # if(not GPIO.input(SW3)):
            
        #     workstation_user[2] = "2"
        #     workstation_time[2] = 30
            
        #     time.sleep(1)
            
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
        

        # if (elapsed_time > time_limit):
        #     code_run = False
            
            
        screen.fill(BLACK)
        time.sleep(1/60)
 
if __name__ == "__main__":

    code_run = multiprocessing.Value('i', 1)
    person_present = multiprocessing.Value('i', 0)
    process = multiprocessing.Process(target = check_camera, args=(person_present, code_run,))
    process1 = multiprocessing.Process(target = main_program, args=(person_present,code_run, ))

    process.start()
    process1.start()

    process.join()
    process1.join()


    
