from tkinter import *
import tkinter.font
from tkinter import messagebox
import RPi.GPIO as GPIO
from time import strftime
import time
from threading import Thread
import random
import requests

##GUI DEFINITIONS
win = Tk()
win.title("Productivity Buddy")
win.geometry("500x440")

##variables for timer
hour=StringVar()
minute=StringVar()
second=StringVar()
##default settings for timer
hour.set("00")
minute.set("00")
second.set("00")

##set font
myFont = tkinter.font.Font(family='Helvetica', size=20)

##setting pins and setup
pressure = 4
led = 23
buzzer = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(pressure,GPIO.IN)
GPIO.setup(led,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)

##functions
##to make led blink
def blinking_LED():
    GPIO.output(led, GPIO.HIGH)
    time.sleep(0.02)
    GPIO.output(led, GPIO.LOW)
    time.sleep(0.02)
        
##to make buzzer noise 
def buzzering():
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(0.02)
    GPIO.output(buzzer, GPIO.LOW)
    time.sleep(0.02)


##reminder to have a break, hardware -- 5 beeps/flash
def break_reminder():
    for i in range(5):
        #led
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.2)
        ##buzzer
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.02)
        
        
##reminder to get back to work, hardware -- 3 beeps/flash
def back_to_work_reminder():
    for i in range(3):
        #led
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.2)
        ##buzzer
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(0.02)

##timer function
def timer():
    try:
        ##the input provided by the user is stored in here :t
        t = int(hour.get())*3600 + int(minute.get())*60 + int(second.get())
    except:
        print("Please input the right value")
    while t >-1:
        mins, secs = divmod(t, 60)
        hours=0
        
        if mins > 60:
            hours, mins = divmod(mins, 60)
            
        hour.set("{0:2d}".format(hours))
        minute.set("{0:2d}".format(mins))
        second.set("{0:2d}".format(secs))
        
        win.update()
        time.sleep(1)
        t -= 1
                
        if (t == 0):
            Thread(target = program).start()
            Thread(target = displaybox).start()

##display the current time
def time_display():
    string = strftime('%H:%M:%S %p')
    time_display_lbl.config(text = string)
    time_display_lbl.after(1000, time_display)
    
##quotes list to randomly pick from
quotes = ['“The Best Way To Get Started Is To Quit Talking And Begin Doing.” – Walt Disney',
          '“The Pessimist Sees Difficulty In Every Opportunity. The Optimist Sees Opportunity In Every Difficulty.” – Winston Churchill',
          '“Don’t Let Yesterday Take Up Too Much Of Today.” – Will Rogers',
          '“You Learn More From Failure Than From Success. Don’t Let It Stop You. Failure Builds Character.” – Unknown',
          '“It’s Not Whether You Get Knocked Down, It’s Whether You Get Up.” – Inspirational Quote By Vince Lombardi',
          '“If You Are Working On Something That You Really Care About, You Don’t Have To Be Pushed. The Vision Pulls You.” – Steve Jobs',
          '“People Who Are Crazy Enough To Think They Can Change The World, Are The Ones Who Do.” – Rob Siltanen',
          '“Failure Will Never Overtake You If Your Determination To Succeed Is Strong Enough.” – Og Mandino',
          '“We May Encounter Many Defeats But We Must Not Be Defeated.” – Maya Angelou',
          '“Knowing Is Not Enough; We Must Apply. Wishing Is Not Enough; We Must Do.” – Johann Wolfgang Von Goethe',
          '“Imagine Your Life Is Perfect In Every Respect; What Would It Look Like?” – Brian Tracy']

##display box to start work
def displaybox():
    messagebox.showinfo("TIMES UP!!!", "Time's up !\nIt's time to work!\n" + random.choice(quotes))
    
##quotes to publish when going back to work
def get_to_work_displaybox():
    quote1 = random.choice(quotes)
    email_reminder(quote1)
    messagebox.showinfo("TIMES UP!!!", "Time's up !\nIt's time to get back to work!\n" + quote1)    
##quotes to publish when break
def break_time_quotes():
    TAB_quotes=['“Let’s loosen up some time and take a break to re-calibrate. Let’s just connect the dots, set the scene, and steam ahead.”',
                '“In this game, everyone needs a break to refuel, recharge, and jump back in full throttle.”',
                '“Sometimes doing nothing makes way for everything.”']
    break_time_quotes = random.choice(TAB_quotes)
    email_break_reminder(break_time_quotes)
    messagebox.showinfo("Take a break", "Hey!\nIt's time to take a break!\n" + break_time_quotes)
    
##trigger process to take a break
def break_time_reminder():
    ##25minutes
    time.sleep(1500)
    Thread(target = break_reminder).start()
    Thread(target = break_time_quotes).start()

##trigger process to go back to work
def back_to_work():
    ##5minutes
    time.sleep(300)
    Thread(target = get_to_work_displaybox).start()
    Thread(target = back_to_work_reminder).start()
    
##email reminder to work
def email_reminder(message):
    report={}
    report["value1"] = message
    requests.post("https://maker.ifttt.com/trigger/time_up/with/key/b-pIrJWlidwvzHrDm6Zjym", data=report)

##email reminder to have a break 
def email_break_reminder(break_message):
    report={}
    report["value1"] = break_message
    requests.post("https://maker.ifttt.com/trigger/rest/with/key/b-pIrJWlidwvzHrDm6Zjym", data=report)

##main program
def program():
    try:
        while True:
        #initialise a previous input variable to 0 (Assume no pressure applied) == no one is seated so no pressure
            prev_input = 0
            message = random.choice(quotes)
        #program start
            input = GPIO.input(pressure) ##user seated
            if ((prev_input == 0) and not input):
                ##if user not seated, buzzer and ligthing will not stop
                print("Waiting User to be Seated")
                blinking_LED()
                buzzering()
                email_reminder(message)
            elif((not prev_input) and input):
                ##if user seated, buzzer and ligthing will stop
                print("User Seated")
                GPIO.output(led, GPIO.LOW)
                GPIO.output(buzzer, GPIO.LOW)
                ##a cycle of pomodoro
                for i in range(4):
                    break_time_reminder()
                    back_to_work()
                break
            
                    
    except KeyboardInterrupt:
        GPIO.cleanup()
            
##close function
def close():
    GPIO.cleanup()
    win.destroy()
    
##GUI Settings
##header
header1 = Label(win, text="Input your timer, then grab a coffee.", font=("Cambria",12,""))
header1.place(x=0,y=0)
header2 = Label(win, text="When timer is up, Start Working! Let's go!!", font=("Cambria",12,""))
header2.place(x=0,y=25)
##setting timer
##hours
hourEntry= Entry(win, width=3, font=("Arial",18,""),textvariable=hour)
hourEntry.place(x=100,y=60)
hourlabel = Label(win,text='HOURS')
hourlabel.place(x=145,y=70)
##minutes
minuteEntry= Entry(win, width=3, font=("Arial",18,""),textvariable=minute)
minuteEntry.place(x=200,y=60)
hourlabel = Label(win,text='MINUTES')
hourlabel.place(x=245,y=70)
##seconds
secondEntry= Entry(win, width=3, font=("Arial",18,""),textvariable=second)
secondEntry.place(x=315,y=60)
hourlabel = Label(win,text='SECONDS')
hourlabel.place(x=360,y=70)
##button to confirm
btn = Button(win, text='Set Time Countdown', bd='5',command=timer,bg='green',foreground = 'white')
btn.place(x = 170,y = 120)

##exit button to quit
exitButton = Button(win, text='EXIT', font=myFont, command=close, bg='bisque2', height=1, width = 15)
exitButton.place(x=120, y=350)

##time display
timelbl = Label(win,text='Current Time', font=('calibri', 15), bg='thistle1')
timelbl.place(x=180, y=220)
time_display_lbl = Label(win, font = ('calibri', 40, 'bold'),bg = 'purple', foreground = 'white')
time_display_lbl.place(x=70, y=250)
time_display()

win.protocol("WM_DELETE_WINDOW", close) #exit cleanly (using 'x' button)

##information
info1 = Label(win, text="**After time's up, a cycle of pomodoro will begin.**", font=("Arial",10,""))
info1.place(x=0,y=400)
info2 = Label(win, text="**A cycle of pomodoro => 4sets of [25minutes(work-time)/5minutes(rest-time)]**", font=("Arial",10,""))
info2.place(x=0,y=420)

win.mainloop() #loop forever