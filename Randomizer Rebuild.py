from email import message
import socket
import threading
import os
import struct
import subprocess
import time
import sys
import random
import shutil
from dotenv import load_dotenv
from os.path import exists

# Working directory
if getattr(sys, 'forzen', False):
    application_path = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    application_path = os.path.dirname(__file__)
    
if (exists(".env.txt")):
    if(exists(".env")):
        shutil.remove(".env")
    os.replace(".env.txt", ".env")

launcher_version = exists(application_path+"\OpenGOAL-Launcher.exe")

# Paths
PATHTOGOALC = application_path + "\goalc.exe"
PATHTOGK = application_path +"\gk.exe -v -- -boot -fakeiso -debug"

# Launcher -> Update path
if launcher_version:
   print("launcher version detected")
   shutil.copyfile(application_path+"/goalc.exe", os.getenv('APPDATA') +"\OpenGOAL-Launcher\\goalc.exe")
   time.sleep(1)
   PATHTOGOAL=os.getnev('APPDATA') +"\OpenGOAL-Launcher\\goalc.exe"
   extraGKCommand = "-proj-path "+os.getenv('APPDATA') +"\OpenGOAL-Launcher\\data "
   PATHTOGK = application_path +"\gk.exe"+extraGKCommand+"-boot -fakeiso -debug -v"

   # Defined list of effects
command_names = [
    "protect","rjto","superjump"]

# Initialize the current_effect variable
current_effect = None

# intialize arrays same length as command_names
on_off = ["t"] * len(command_names)
cooldowns = [0.0] * len(command_names)
last_used = [0.0] * len(command_names)
activated = [0.0] * len(command_names)
durations = [0.0] * len(command_names)
active = [False] * len(command_names)

# Function Definitions
def sendForm(form):
    header = struct.pack('<II', len(form), 10)
    clientSocket.sendall(header + form.encode())
    print("Sent: " + form)
    return

def cd_check(cmd):
    global message
    if (time.time() - last_used[command_names.index(cmd)]) > cooldowns[command_names.index(cmd)]:
        last_used[command_names.index(cmd)] = time.time()
        message == ""
        return
    else:
        message = ""
        return False

def on_check(cmd):
    global message
    if on_off[command_names.index(cmd)] != "f" and not active[command_names.index("protect")]:
        message == ""
        return True 
    else:
        message = ""
        return False

def active_check(cmd, line1, line2):
    if not active[command_names.index(cmd)]:
        sendForm(line1)
        activate(cmd)
    else:
        sendForm(line2)
        deactivate(cmd)
        
def active_sweep(cmd, line):
    if active[command_names.index(cmd)] and (time.time() - activated[command_names.index(cmd)]) >= durations[command_names.index(cmd)]:
        deactivate(cmd)
        sendForm(line)

def activate(cmd):
    activated[command_names.index(cmd)] = time.time()
    active[command_names.index(cmd)] = True

def deactivate(cmd):
    if active[command_names.index(cmd)]:
         #if ACTIVATE_MSG != "f":
            #sendMessage(irc, "/me > '"+command_names[command_names.index(cmd)]+"' deactivated!")
         active[command_names.index(cmd)] = False

def max_val(val, min, max):
    global message
    try:
        float(val)
        if float(val) <= max and float(val) >= min:
           return True
        else:
            #sendMessage(irc, "/me @"+user+" Use values between " + str(min) + " and " + str(max) + ".")
            message = ""
            return False
    except ValueError:
        return False
    
#This splits the Gk commands into args for gk.exe
GKCOMMANDLINElist = PATHTOGK.split()

#Close Gk and goalc if they were open.
print("If it errors below that is O.K.")
subprocess.Popen("""taskkill /F /IM gk.exe""",shell=True)
subprocess.Popen("""taskkill /F /IM goalc.exe""",shell=True)
time.sleep(3)

#Open a fresh GK and goalc then wait a bit before trying to connect via socket
print("opening " + PATHTOGK)
print("opening " + PATHTOGOALC)
GK_WIN = subprocess.Popen(GKCOMMANDLINElist)
GOALC_WIN = subprocess.Popen([PATHTOGOALC])
time.sleep(3)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
clientSocket.connect(("127.0.0.1", 8181))
time.sleep(1)
data = clientSocket.recv(1024)
print(data.decode())

#Int block these comamnds are sent on startup
sendForm("(lt)")
sendForm("(mi)")
sendForm("(send-event *target* 'get-pickup (pickup-type eco-red) 5.0)")
sendForm("(dotimes (i 1) (sound-play-by-name (static-sound-name \"cell-prize\") (new-sound-id) 1024 0 0 (sound-group sfx) #t))")
sendForm("(set! *cheat-mode* #f)")
sendForm("(set! *debug-segment* #f)")
#End Int block

# Split GK commands into args for gk.exe
GKCOMMANDLINElist = PATHTOGK.split()

# Defined dictionary map from name effects to numbers
effect_mapping = {
    1: "rjto",
    2: "superjump",
    3: "superboosted",
}

# Number of effects to apply
num_effects_to_apply = 1

start_time = time.time()
interval = 1 * 60 

def apply_effect(effects):
    random_effect = random.sample(range(1, 3), effects)

    # Apply selected effects
    for effect_num in random_effect:
        effect_name = effect_mapping.get(effect_num)
        if effect_name:
            execute_effect(effect_name)


def execute_effect(effect_name):
    global message

    print("Epic Rolljump frfr")
    if effect_name == "rjto" and on_check("rjto") and cd_check("rjto"):
        apply_effect("rjto")
        sendForm("(set! (-> *TARGET-bank* wheel-flip-dist) (meters 15.0)")
        message = ""

    print("Epic Highjump frfr")
    if effect_name == "superjump" and on_check("superjump") and cd_check("superjump"):
        apply_effect("superjump")
        sendForm("(set! (-> *TARGET-bank* jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* jump-height-min)(meters 5.0))(set! (-> *TARGET-bank* double-jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* double-jump-height-min)(meters 5.0))"),
        message = ""

    print("Epic Boosted frfr")
    if effect_name == "superboosted" and on_check("superboosted") and cd_check("superboosted"):
        sendForm("(set! (-> *edge-surface* fric) 1.0)"),
        message = ""


    pass
while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= interval:
        # Apply new effect and turn off previous
        selected_effects = 2
        apply_effect(selected_effects)
       
        # Update the start time to the current time
        start_time = current_time
    
# Avoid constant checking
time.sleep(1)