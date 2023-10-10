import socket
import subprocess
import time
import sys
import random
import struct
import os
import shutil

# Randomizer made by Mortis
# Help from: barg, zed & yopie
# Created: 10/08/2023 
# Used repo for effects: https://github.com/Zedb0T/Opengoal-Twitch-CrowdControl/blob/main/resources/twitchcommands.py

# Working directory
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    application_path = os.path.dirname(__file__)

if os.path.exists(".env.txt"):
    if os.path.exists(".env"):
        os.remove(".env")
    os.replace(".env.txt", ".env")

launcher_version = os.path.exists(application_path + "\OpenGOAL-Launcher.exe")

# Paths
PATHTOGOALC = application_path + "\goalc.exe"
PATHTOGK = application_path + "\gk.exe -v -- -boot -fakeiso -debug"

# Launcher -> Update path
if launcher_version:
    print("launcher version detected")
    shutil.copyfile(application_path + "/goalc.exe", os.getenv('APPDATA') + "\OpenGOAL-Launcher\\goalc.exe")
    time.sleep(1)
    PATHTOGOAL = os.getenv('APPDATA') + "\OpenGOAL-Launcher\\goalc.exe"
    extraGKCommand = "-proj-path " + os.getenv('APPDATA') + "\OpenGOAL-Launcher\\data "
    PATHTOGK = application_path + "\gk.exe" + extraGKCommand + "-boot -fakeiso -debug -v"

# Defined list of effects
command_names = [
    "protect", "rjto", "superjump", "superboosted", "noboosteds"
]

# Initialize the current_effect variable
current_effect = None

# Initialize arrays same length as command_names
on_off = ["t"] * len(command_names)
cooldowns = [0.0] * len(command_names)
last_used = [0.0] * len(command_names)
activated = [0.0] * len(command_names)
durations = [0.0] * len(command_names)
active = [False] * len(command_names)

#this global decides if the timer in our while loop should count or not
timer_on = False

# Function Definitions
def sendForm(form):
    header = struct.pack('<II', len(form), 10)
    clientSocket.sendall(header + form.encode())
    print("Sent: " + form)

def cd_check(cmd):
    global message
    if (time.time() - last_used[command_names.index(cmd)]) > cooldowns[command_names.index(cmd)]:
        last_used[command_names.index(cmd)] = time.time()
        return True
    else:
        message = ""
        return False

def on_check(cmd):
    global message
    if on_off[command_names.index(cmd)] != "f" and not active[command_names.index("protect")]:
        message = ""
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

def activate(cmd):
    activated[command_names.index(cmd)] = time.time()
    active[command_names.index(cmd)] = True

def deactivate(cmd):
    if active[command_names.index(cmd)]:
        active[command_names.index(cmd)] = False

def max_val(val, min, max):
    global message
    try:
        float(val)
        if float(val) <= max and float(val) >= min:
            return True
        else:
            message = ""
            return False
    except ValueError:
        return False

# This splits the Gk commands into args for gk.exe
GKCOMMANDLINElist = PATHTOGK.split()

# Close Gk and goalc if they were open.
print("If it errors below that is O.K.")
subprocess.Popen("""taskkill /F /IM gk.exe""", shell=True)
subprocess.Popen("""taskkill /F /IM goalc.exe""", shell=True)
time.sleep(3)

# Open a fresh GK and goalc then wait a bit before trying to connect via socket
print("opening " + PATHTOGK)
print("opening " + PATHTOGOALC)
GK_WIN = subprocess.Popen(GKCOMMANDLINElist)
GOALC_WIN = subprocess.Popen([PATHTOGOALC])
time.sleep(3)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(("127.0.0.1", 8181))
time.sleep(1)
data = clientSocket.recv(1024)
print(data.decode())

# Int block these commands are sent on startup
sendForm("(lt)")
sendForm("(mi)")
sendForm("(send-event *target* 'get-pickup (pickup-type eco-red) 5.0)")
sendForm("(dotimes (i 1) (sound-play-by-name (static-sound-name \"cell-prize\") (new-sound-id) 1024 0 0 (sound-group sfx) #t))")
sendForm("(set! *cheat-mode* #f)")
sendForm("(set! *debug-segment* #f)")
#putting an on/off variable here for the while loop didn't work :(

# End Int block

# Split GK commands into args for gk.exe
GKCOMMANDLINElist = PATHTOGK.split()

# Defined dictionary map from name effects to numbers
effect_mapping = {
    1: "rjto",
    2: "superjump",
    3: "superboosted",
    4: "noboosteds",
}

# Number of effects to apply
num_effects_to_apply = 1

start_time = time.time()
interval = 1 * 40  # 5 minutes 
#elapsed_time = time.time() - start_time
#with open("timer.txt", "w") as file:
#        file.write(str(round(elapsed_time, 2)))
#        time.sleep(1)

def apply_effect(effects):
    random_effect = random.sample(range(1, len(effect_mapping) + 1), effects)

    # Deactivate any active effects
    for effect_num in range(1, len(effect_mapping) + 1):
        effect_name = effect_mapping.get(effect_num)
        if effect_name and active[command_names.index(effect_name)]:
            print("Deactivating:", effect_name)
            execute_deactivation(effect_name)

    # Apply selected effects
    for effect_num in random_effect:
        effect_name = effect_mapping.get(effect_num)
        if effect_name:
            print("Applying:", effect_name)
            with open("effect.txt", "w") as file:
                file.write("current effect:" + effect_name)
            execute_activation(effect_name)

def value_changer(cstring):
    #Call this function with a string to tell it which effect to change
    #some crowd control commands send multiple lines of code
    #having an elif chunk for each lets us pick the rng range for each
    #this requires calling value_changer once per line of goal we send
    if cstring == "rjto":
        # Generate a random value between 1 - 100
        random_value = random.randint(1, 100)
        # Create new command with random value
        command = "(set! (-> *TARGET-bank* wheel-flip-dist) (meters {}))".format(random_value)
    elif cstring == "jump1":
        random_value = random.randint(1, 50)
        command = "(set! (-> *TARGET-bank* jump-height-max) (meters {}))".format(random_value)
    elif cstring == "jump2":
        random_value = random.randint(1, 20)
        command = "(set! (-> *TARGET-bank* jump-height-min) (meters {}))".format(random_value)
    elif cstring == "jump3":
        random_value = random.randint(1, 50)
        command = "(set! (-> *TARGET-bank* double-jump-height-max) (meters {}))".format(random_value)
    elif cstring == "jump4":
        random_value = random.randint(1, 20)
        command = "(set! (-> *TARGET-bank* double-jump-height-min) (meters {}))".format(random_value)
    print(command)
    return command


def execute_activation(effect_name):
    global message

    if effect_name == "rjto" and on_check("rjto"):
        activate("rjto")
        #sendform the new string
        sendForm(value_changer("rjto"))
        message = ""
    elif effect_name == "superjump" and on_check("superjump"):
        activate("superjump")
        sendForm(value_changer("jump1"))
        sendForm(value_changer("jump2"))
        sendForm(value_changer("jump3"))
        sendForm(value_changer("jump4"))        
        message = ""
    elif effect_name == "superboosted" and on_check("superboosted"):
        activate("superboosted")
        sendForm("(set! (-> *edge-surface* fric) 1.0)")
        message = ""
    elif effect_name == "noboosteds" and on_check("noboosteds"):
        sendForm("(set! (-> *edge-surface* fric) 1530000.0)")

def execute_deactivation(effect_name):
    global message
    
    if effect_name == "rjto" and on_check("rjto"):
        deactivate("rjto")
        sendForm("(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
        message = ""
    elif effect_name == "superjump" and on_check("superjump"):
        deactivate("superjump")
        sendForm("(set! (-> *TARGET-bank* jump-height-max) (meters 3.5))")
        sendForm("(set! (-> *TARGET-bank* jump-height-min) (meters 1.10))")
        sendForm("(set! (-> *TARGET-bank* double-jump-height-max) (meters 2.5))")
        sendForm("(set! (-> *TARGET-bank* double-jump-height-min) (meters 1.0))")        
        message = ""
    elif effect_name == "superboosted" and on_check("superboosted"):
        deactivate("superboosted")
        sendForm("(set! (-> *edge-surface* fric) 30720.0)")
        message = ""
    elif effect_name == "noboosteds" and on_check("noboosteds"):
        sendForm("(set! (-> *edge-surface* fric) 30720.0)")

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    with open("timer.txt", "w") as file:
        file.write("seconds passed: " + str(round(elapsed_time, 0)))

    if elapsed_time >= interval:
        print("amongus")
        # Apply new effect and turn off previous
        selected_effects = num_effects_to_apply
        apply_effect(selected_effects)

        # Update the start time to the current time
        start_time = current_time
    else:
        print(elapsed_time)
    # Sleep to avoid constant checking
        time.sleep(1)




#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⣤⣤⣤⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠙⠛⠛⠛⠛⠻⢿⣿⣷⣤⡀⠀⠀⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠈⢻⣿⣿⡄⠀⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⣸⣿⡏⠀⠀⠀⣠⣶⣾⣿⣿⣿⠿⠿⠿⢿⣿⣿⣿⣄⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⢰⣿⣿⣯⠁⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀ 
#⠀⠀⣀⣤⣴⣶⣶⣿⡟⠀⠀⠀⢸⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⠀ 
#⠀⢰⣿⡟⠋⠉⣹⣿⡇⠀⠀⠀⠘⣿⣿⣿⣿⣷⣦⣤⣤⣤⣶⣶⣶⣶⣿⣿⣿⠀ 
#⠀⢸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀ 
#⠀⣸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠉⠻⠿⣿⣿⣿⣿⡿⠿⠿⠛⢻⣿⡇⠀⠀ 
#⠀⣿⣿⠁⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⠀⠀ 
#⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
#⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
#⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀ 
#⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀ 
#⠀⠀⠛⢿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⣰⣿⣿⣷⣶⣶⣶⣶⠶⢠⣿⣿⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿⡏⠁⠀⠀⢸⣿⡇⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿⠁⠀⠈⠻⣿⣿⣿⣿⡿⠏⠀⠀⠀⠀ 
#⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀
#  sus⠀⠀⠀⠀⠀⠀