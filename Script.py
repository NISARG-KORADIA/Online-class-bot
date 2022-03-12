# python packages
import time
from datetime import datetime, timedelta
# custome intallation
from win10toast import ToastNotifier
# selenium packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
# import other files
import login_cred

email_id = login_cred.email_id  
password = login_cred.password
prefs = { 
    "profile.default_content_setting_values.media_stream_mic": 2, 
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.geolocation": 2, 
    "profile.default_content_setting_values.notifications": 2,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False 
  }
lec_sched = {}
toaster = ToastNotifier()

options = Options()
# options.headless = True
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-insecure-localhost")
options.add_argument("--disable-application-cache")
options.add_argument("--disable-session-crashed-bubble")
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

def time_now():
  return datetime.now().strftime("%H:%M")

def time_diff(time_1, time_2):
  if datetime.strptime(time_1, "%H:%M") < datetime.strptime(time_2, "%H:%M"):
    return -1

  difference = (datetime.strptime(time_1, "%H:%M") - datetime.strptime(time_2, "%H:%M")).seconds
  return difference

def get_class(lectures):
  date = datetime.now().strftime("%B %#d")
  print("getting list of today's lectures...")
  for lecture in lectures:
    lec_aria_label = lecture.get_attribute('aria-label')
    lec_title = lecture.get_attribute('title')
    if lec_aria_label.find(date)!=-1 and lec_aria_label.find('Canceled')==-1:
      lecture = lec_title[:lec_title.find("from")-1]
      start_time = (datetime.strptime(lec_title[lec_title.find(date)+len(date)+1:lec_title.find("to")-1], "%I:%M %p") + timedelta(minutes=5)).strftime("%H:%M")
      end_time = (datetime.strptime(lec_title[lec_title.find("to")+3:], "%I:%M %p") - timedelta(minutes=5)).strftime("%H:%M")
      lec_sched[lecture] = {
          "xpath" : ".//div[@title='"+lec_title+"']",
          "start_time" : start_time,
          "end_time" : end_time
      }
  
  print(lec_sched)
  print("Got all today's lectures.")

def wait_for_ele(by, arg, func_to_restart):
  try:
    if by == "class":
      WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, arg)))
    if by == "xpath":
      WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, arg)))
    if by == "id":
      WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, arg)))
  except:
    print("element:" + arg + "is not loaded. Trying again!")
    driver.refresh()
    func_to_restart()

def go_back_to_calender():
  calender = 'app-bar-ef56c0de-36fc-4ef8-b417-3d82ba9d073c'
  card_class = "node_modules--msteams-bridges-components-calendar-event-card-dist-es-src-renderers-event-card-renderer-event-card-renderer__eventCard--h5y4X"
  
  wait_for_ele('id', calender, go_back_to_calender)
  cal_btn = driver.find_element(By.ID, calender)
  cal_btn.click()

  wait_for_ele('class', card_class, start)

def dismiss_notification():
  try:
    noti_card = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-tid='incoming-notification']")))
    driver.find_element(By.XPATH, "//button[@ng-click='action.action(); $event.stopPropagation();']").click()
  except:
    print("Notification permission card haven't been found")

def leave_class():
  dismiss_xpath = "//button[@ng-click='postCallingScreen.dismiss()']"

  # hanging up class
  screen = driver.find_element(By.CLASS_NAME, 'ts-calling-screen')
  action.move_to_element(screen).click(screen).perform()
  disconnect_btn = driver.find_element(By.ID, 'hangup-button')
  driver.execute_script("$(arguments[0]).click();", disconnect_btn)

  # dismissing review
  wait_for_ele('xpath', dismiss_xpath, start)
  dismiss_btn = driver.find_element(By.XPATH, dismiss_xpath)
  dismiss_btn.click() 

  print("Class left successfully.")

  go_back_to_calender()

def class_waiting_time(end_time):
  wait_for_ele('id', 'hangup-button', start)
  wait_time = time_diff(end_time, time_now())
  print("This class will run for "+ str(wait_time/60) + " minutes.")
  time.sleep(wait_time)

def join_meeting(class_xpath):
  continue_btn_xpath = "//button[@ng-click='getUserMedia.passWithoutMedia()']"
  mic_icon_xpath = 'icons-call-microphone-off'
  join_xpath = "//button[@data-tid='calv2-peek-join-button']"

  # clicking meeting card
  try:
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, class_xpath)))
    wait_for_ele('xpath', class_xpath, start)
    meeting_card = driver.find_element(By.XPATH, class_xpath)
    meeting_card.click()

    # clicking join button in pop-up
    wait_for_ele('xpath', join_xpath, start)
    join_btn = driver.find_element(By.XPATH, join_xpath)
    join_btn.click()

    # clicking continue without media button
    wait_for_ele('xpath', continue_btn_xpath, start)
    media_btn = driver.find_element(By.XPATH, continue_btn_xpath)
    media_btn.click()
    
    # finally clicking join button to enter the meeting
    wait_for_ele('class', mic_icon_xpath, start)
    join_class_btn = driver.find_element(By.CLASS_NAME, 'join-btn')
    join_class_btn.click()

    wait_for_ele('id', 'hangup-button', start)
    print("Class joined successfully.")
  
  except:
    print("Class not found")

def join_today_class(current_time, day, class_name):
  if time_diff(current_time, lec_sched[class_name]["start_time"])<0:
    diff = time_diff(lec_sched[class_name]["start_time"], current_time)
    print("Next class is "+class_name+", joining in " + str(diff/60) + " minutes.")
    time.sleep(diff)
    join_today_class(time_now(), day, class_name)
  elif time_diff(current_time, lec_sched[class_name]["start_time"])>=0 and time_diff(lec_sched[class_name]["end_time"], current_time)>0:
    print("Joining class of "+class_name+"...")
    join_meeting(lec_sched[class_name]["xpath"])
    toaster.show_toast("Class butler", "Joining "+ class_name + " lecture", duration=5, threaded=True)

    class_waiting_time(lec_sched[class_name]["end_time"])
    
    toaster.show_toast("Class butler", "Left "+ class_name +" Class.", duration=5, threaded=True)
    print("Leaving class of "+class_name+"...")
    leave_class()

def start():
  day = datetime.now().strftime("%a")

  go_back_to_calender()

  dismiss_notification()

  lectures = driver.find_elements(By.CLASS_NAME, "node_modules--msteams-bridges-components-calendar-event-card-dist-es-src-renderers-event-card-renderer-event-card-renderer__eventCard--h5y4X")

  get_class(lectures)

  print("Joinig classes")

  if len(lec_sched) != 0:
    for index, lecture in enumerate(lec_sched):
      join_today_class(time_now(), day, lecture)
    print("All classes complete.")
    toaster.show_toast("Class butler", "Shutting Down, class complete.", duration=5, threaded=True)

  else:
    print("No classes today")

def login():
  login_input_id = "i0116"
  sub_btn_id = "idSIButton9"
  pass_input_id = "i0118"
  chk_box_id = "KmsiCheckboxField"

  print("Loggin in...")

  wait_for_ele("id", login_input_id, login)
  login_field = driver.find_element(By.ID, login_input_id)
  login_field.click()
  login_field.send_keys(email_id) 
  next_btn = driver.find_element(By.ID, sub_btn_id)
  next_btn.click()

  wait_for_ele("id", "idA_PWD_ForgotPassword", login)
  pass_field = driver.find_element(By.ID, pass_input_id)
  pass_field.click()
  pass_field.send_keys(password)
  sub_btn = driver.find_element(By.ID, sub_btn_id)
  sub_btn.click()

  wait_for_ele("id", chk_box_id, open_chrome)
  yes_btn = driver.find_element(By.ID, sub_btn_id)
  yes_btn.click()

  print("Logged In.")
  start()

def open_chrome():
  driver.get('https://teams.microsoft.com/')
  global action
  action = ActionChains(driver)
  login()

# date = datetime.strptime("3:00 PM", "%I:%M %p").strftime("%H:%M")
# print(date)

open_chrome()

# driver.save_screenshot("screenshot.png")
driver.close()
driver.quit()