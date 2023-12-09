

import os
import mysql.connector as database


username = os.environ.get("username")
password = os.environ.get("password")

#Connect to mariadb
connection = database.connect(user='default', password='password',
 host="localhost", database="final_project")

#Cursor to move through rows of 'users' table
cursor = connection.cursor()

def get_data1(rfid):
   # try:
      statement = "SELECT first_name, rfid FROM users WHERE rfid=%s"
      data = (rfid,)
      cursor.execute(statement, data)
      username = cursor.fetchone()[0]
      print(username)
      if (cursor.fetchone()):
       return username
      #for (first_name, rfid) in cursor:
      #  print(f"Successfully retrieved {first_name}, {rfid}")
       # return first_name
      
    #except:
    #  print("error")
    #     statement1 = "SELECT COUNT(*) FROM users"
    #     cursor.execute(statement1)
    #     result = cursor.fetchone() + 1
    #     print("Result is")
    #     print(result)
    #     name ="User%i"%result
    #     statement = "INSERT INTO users (name,rfid) VALUES (%s, %s)"
    # #   statement = "SELECT first_name, rfid FROM users WHERE rfid=%s"
    #     data = (name,rfid)
    #     cursor.execute(statement, data)
    #     connection.commit()
    #     print("Successfully added user to database")
    #     return name

def add_data(first_name, rfid):
    try:
        user_exists = get_data(rfid)
        if (user_exists):
          print("User already exists")
        
        else:
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
    print("Error entering database information: {e}")
    
def remove_data(first_name):
  try:

    statement = "DELETE FROM users WHERE first_name= %s"

    data = (first_name,)
    cursor.execute(statement, data)
    connection.commit()
    print("Successfully deleted user %s" % first_name)

  except database.Error as e:
    print("Error entering database information: {e}")



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

def modify_ws_occupancy(WS_occupancy_type):
  try:
    statement = "UPDATE users SET WS_occupancy = %s"

    data = (WS_occupancy_type,)
    cursor.execute(statement, data)
    connection.commit()
    print("Successfully modified WS occupancy to %d" % WS_occupancy_type)

  except database.Error as e:
    print("Error entering database information: {e}")

def update_ws_table(ws, status_, remaining_time):
  try:
    statement = "UPDATE ws_occupancy SET status_ = %s, remaining_time = %s WHERE workstation = %s"

    data = (status_, remaining_time, ws)
    cursor.execute(statement, data)
    connection.commit()
    print("Successfully modified WS occupancy to")

  except database.Error as e:
    print("Error entering database information: {e}")



def return_count():
  try:
    statement = "SELECT COUNT(*) FROM users"

    data = ()
    cursor.execute(statement)
    # connection.commit()
    
    print("The returned count is %d" % cursor.fetchone()[0])

  except database.Error as e:
    print("Error entering database information: {e}")

# modify_session_time("254,103,7,144", 1, 0)
# modify_ws_occupancy(0)

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

   


# print(int((check_num()[0])))
# rfid="17496"
# if (check_name(rfid)):
#     print("name present in database")
# else:
#     name = "User" + str(check_num()[0]+1)
#     add(name,rfid)

modify_session_time("Devin", 1,30)
   
# update_ws_table(1, "Devin", 50)
# name = get_data1("174,96,0,144")
# print(name)
#add_data("Adi", "254,103,7,144")
#get_data("12345")
#increment_data ("Devin", 1)

#user_exists = get_data("56779")

#if (user_exists):
#   print("The user %s exists" %)

#else:
#   print("USER does not exist")

# add_data("Devin", "12345")

connection.close()
