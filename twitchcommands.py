import socket
import threading
import os
import struct
import subprocess
import time
import sys
import random
from dotenv import load_dotenv
from os.path import exists
import shutil

"""
Created on Fri Apr 29 16:20:54 2022
@author: Yop Mike Zed
"""
#Set the working directory
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    application_path = os.path.dirname(__file__)


if (exists(".env.txt")):
    if(exists(".env")):
        shutil.remove(".env")
    os.replace(".env.txt", ".env")

if(exists("env")):
    os.replace("env",".env")

#env values
load_dotenv()
OAUTH = str(os.getenv("OAUTH"))
CONNECT_MSG = str(os.getenv("CONNECT_MSG"))
COOLDOWN_MSG = str(os.getenv("COOLDOWN_MSG"))
DISABLED_MSG = str(os.getenv("DISABLED_MSG"))
ACTIVATE_MSG = str(os.getenv("ACTIVATE_MSG"))
PROTECT_SACRIFICE = str(os.getenv("PROTECT_SACRIFICE"))
SACRIFICE_DURATION = str(os.getenv("SACRIFICE_DURATION"))
PREFIX = str(os.getenv("PREFIX"))

#bool that checks if its the launcher version
launcher_version = exists(application_path+"\OpenGOAL-Launcher.exe")

#checks

if (not exists(".env")):
    print("ERROR: .env file not found -- please check if it is in the same folder as gk.exe and JakCrowdControl.exe")
    time.sleep(936814)

if ((len(OAUTH) != 36) or (OAUTH[0:6] != "oauth:")):
    print("ERROR: Invalid ouath -- please get new oauth from: https://twitchapps.com/tmi/")
    time.sleep(936814)
    
#paths
PATHTOGOALC = application_path + "\goalc.exe"
PATHTOGK = application_path +"\gk.exe -boot -fakeiso -debug -v"

#If its the launcher version update the paths!
if launcher_version:
    print("launcher version detected")
    shutil.copyfile(application_path+"/goalc.exe", os.getenv('APPDATA') +"\OpenGOAL-Launcher\\goalc.exe")
    time.sleep(1)
    PATHTOGOALC=os.getenv('APPDATA') +"\OpenGOAL-Launcher\\goalc.exe"
    extraGKCommand = "-proj-path "+os.getenv('APPDATA') +"\OpenGOAL-Launcher\\data "
    PATHTOGK = application_path +"\gk.exe "+extraGKCommand+"-boot -fakeiso -debug -v"

#
#Function definitions
#
def sendForm(form):
    header = struct.pack('<II', len(form), 10)
    clientSocket.sendall(header + form.encode())
    print("Sent: " + form)
    return

def cd_check(cmd):
    global message
    if (time.time() - last_used[command_names.index(cmd)]) > cooldowns[command_names.index(cmd)]:
        last_used[command_names.index(cmd)] = time.time()
        return True
    elif COOLDOWN_MSG == "t":
        sendMessage(irc, "/me @"+user+" Command '"+command_names[command_names.index(cmd)]+"' is on cooldown ("+str(int(last_used[command_names.index(cmd)]-(time.time()-cooldowns[command_names.index(cmd)])))+"s left).")
        message = ""
        return False
    else:
        message = ""
        return False

def on_check(cmd):
    global message
    if on_off[command_names.index(cmd)] != "f" and not active[command_names.index("protect")]:
        return True 
    elif DISABLED_MSG == "t":
        sendMessage(irc, "/me @"+user+" Command '"+command_names[command_names.index(cmd)]+"' is disabled.")
        message = ""
        return False
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
    if ACTIVATE_MSG != "f":
        sendMessage(irc, "/me > '"+command_names[command_names.index(cmd)]+"' activated!")
        activated[command_names.index(cmd)] = time.time()
        active[command_names.index(cmd)] = True

def deactivate(cmd):
    if active[command_names.index(cmd)]:
         if ACTIVATE_MSG != "f":
            sendMessage(irc, "/me > '"+command_names[command_names.index(cmd)]+"' deactivated!")
         active[command_names.index(cmd)] = False

def max_val(val, min, max):
    global message
    try:
        float(val)
        if float(val) <= max and float(val) >= min:
           return True
        else:
            sendMessage(irc, "/me @"+user+" Use values between " + str(min) + " and " + str(max) + ".")
            message = ""
            return False
    except ValueError:
        return False

#
#Launch REPL, connect bot, and mi

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

#add all commands into an array so we can reference via index
command_names = ["protect","rjto","superjump","superboosted","noboosteds","nojumps","fastjak","slowjak","pacifist","trip",
                 "shortfall","ghostjak","getoff","flutspeed","freecam","enemyspeed","give","collected",
                 "eco","sucksuck","noeco","die","topoint","randompoint","setpoint","tp","shift","movetojak","ouch",
                 "burn","hp","melt","drown","endlessfall","iframes","invertcam","cam","stickycam","deload",
                 "quickcam","dark","nodax","smallnet","widefish","lowpoly","moveplantboss","moveplantboss2",
                 "basincell","resetactors","repl","debug","save","resetcooldowns","cd","dur","enable","disable",
                 "widejak","flatjak","smalljak","bigjak","color","scale","slippery","rocketman","actorson",
                 "actorsoff","unzoom","bighead","smallhead","bigfist","bigheadnpc","hugehead","mirror","notex","press",
                 "lang","fixoldsave"]

#array of valid checkpoints so user cant send garbage data
point_list = ["training-start","game-start","village1-hut","village1-warp","beach-start",
              "jungle-start","jungle-tower","misty-start","misty-silo","misty-bike",
              "misty-backside","misty-silo2","firecanyon-start","firecanyon-end",
              "village2-start","village2-warp","village2-dock","rolling-start",
              "sunken-start","sunken1","sunken2","sunken-tube1","sunkenb-start",
              "sunkenb-helix","swamp-start","swamp-dock1","swamp-cave1","swamp-dock2",
              "swamp-cave2","swamp-game","swamp-cave3","ogre-start","ogre-race","ogre-end",
              "village3-start","village3-warp","village3-farside","maincave-start",
              "maincave-to-darkcave","maincave-to-robocave","darkcave-start","robocave-start",
              "robocave-bottom","snow-start","snow-fort","snow-flut-flut","snow-pass-to-fort",
              "snow-by-ice-lake","snow-by-ice-lake-alt","snow-outside-fort","snow-outside-cave",
              "snow-across-from-flut","lavatube-start","lavatube-middle","lavatube-after-ribbon",
              "lavatube-end","citadel-start","citadel-entrance","citadel-warp","citadel-launch-start",
              "citadel-launch-end","citadel-generator-start","citadel-generator-end","citadel-plat-start",
              "citadel-plat-end","citadel-elevator","finalboss-start","finalboss-fight"]

lang_list = ["english","french","german","spanish","italian","japanese","uk-english"]
input_list = ["square","circle","x","triangle","up","down","left","right"]
cam_list = ["endlessfall","eye","standoff","bike","stick"]

#intialize arrays same length as command_names
on_off = ["t"] * len(command_names)
cooldowns = [0.0] * len(command_names)
last_used = [0.0] * len(command_names)
activated = [0.0] * len(command_names)
durations = [0.0] * len(command_names)
active = [False] * len(command_names)

#pull cooldowns set in env file and add to array
for x in range(len(command_names)):
    cooldowns[x]=float(os.getenv(command_names[x]+"_cd"))
    on_off[x]=(os.getenv(command_names[x]))
#pull durations set in env file and add to array
for x in range(len(command_names)):
    durations[x]=float(os.getenv(command_names[x]+"_dur"))
    
#twitch irc stuff
SERVER = "irc.twitch.tv"
PORT = 6667

#Get Your OAUTH Code Here! https://twitchapps.com/tmi/

#What you'd like to name your bot
BOT = "jakopengoalbot"
#The channel you want to monitor
CHANNEL = str(os.getenv("TARGET_CHANNEL")).lower()

#COMMAND_MODS, these users can use the REPL command to create custom commands!
COMMAND_MODS = ["zed_b0t", "mikegamepro", "water112", "barg034", CHANNEL]

#initialize empty strings to store user and message
message = ""
user = ""

irc = socket.socket()
irc.connect((SERVER, PORT))
irc.send((    "PASS " + OAUTH + "\n" +
            "NICK " + BOT + "\n" +
            "JOIN #" + CHANNEL + "\n").encode())

#sends a message to the irc channel.
def sendMessage(irc, message):
    messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
    irc.send((messageTemp + "\n").encode())

def gamecontrol():
    
    global message

    while True:
        #split a whole message into args so we can evaluate it one by one
        args = message.split(" ")
        
        if PREFIX + "protect" == str(args[0]).lower() and on_check("protect") and cd_check("protect"):
            activate("protect")
            if PROTECT_SACRIFICE == "t":
                sendMessage(irc, "/timeout "+user+" "+str(SACRIFICE_DURATION))
                sendMessage(irc, "/me "+user+" sacrificed themselves to protect "+CHANNEL+" for "+str(int(durations[command_names.index("protect")]))+"s!")
            message = ""

        if (PREFIX + "rjto" == str(args[0]).lower() or PREFIX + "rj" == str(args[0]).lower()) and len(args) >= 2 and max_val(args[1], -200, 200) and on_check("rjto") and cd_check("rjto"):
            activate("rjto")
            sendForm("(set! (-> *TARGET-bank* wheel-flip-dist) (meters " + str(args[1]) + "))")
            message = ""

        if PREFIX + "superjump" == str(args[0]).lower() and on_check("superjump") and cd_check("superjump"):
            active_check("superjump", 
            "(set! (-> *TARGET-bank* jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* jump-height-min)(meters 5.0))(set! (-> *TARGET-bank* double-jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* double-jump-height-min)(meters 5.0))",
            "(set! (-> *TARGET-bank* jump-height-max)(meters 3.5))(set! (-> *TARGET-bank* jump-height-min)(meters 1.01))(set! (-> *TARGET-bank* double-jump-height-max)(meters 2.5))(set! (-> *TARGET-bank* double-jump-height-min)(meters 1))")
            message = ""

        if (PREFIX + "superboosted" == str(args[0]).lower() or PREFIX + "superboosteds" == str(args[0]).lower()) and on_check("superboosted") and cd_check("superboosted"):
            active_check("superboosted", 
            "(set! (-> *edge-surface* fric) 1.0)",
            "(set! (-> *edge-surface* fric) 30720.0)")
            message = ""

        if (PREFIX + "noboosteds" == str(args[0]).lower() or PREFIX + "noboosted" == str(args[0]).lower()) and on_check("noboosteds") and cd_check("noboosteds"):
            active_check("noboosteds", 
            "(set! (-> *edge-surface* fric) 1530000.0)",
            "(set! (-> *edge-surface* fric) 30720.0)")
            message = ""
        
        if (PREFIX + "nojumps" == str(args[0]).lower() or PREFIX + "nojumping" == str(args[0]).lower() or PREFIX + "nojump" == str(args[0]).lower()) and on_check("nojumps") and cd_check("nojumps"):
            active_check("nojumps", 
            "(logior! (-> *target* state-flags) (state-flags prevent-jump))",
            "(logclear! (-> *target* state-flags) (state-flags prevent-jump))")
            message = ""

        if PREFIX + "fastjak" == str(args[0]).lower() and on_check("fastjak") and cd_check("fastjak"):
            if active[command_names.index("slowjak")]:
                sendForm("(pc-cheat-toggle-and-tune *pc-settings* eco-yellow)(send-event *target* 'reset-pickup 'eco)")
                deactivate("slowjak")
            if not active[command_names.index("smalljak")]:
                sendForm("(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
            active_check("fastjak", 
            "(set! (-> *walk-mods* target-speed) 77777.0)(set! (-> *double-jump-mods* target-speed) 77777.0)(set! (-> *jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *attack-mods* target-speed) 77777.0)(set! (-> *forward-high-jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *stone-surface* target-speed) 1.25)",
            "(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *stone-surface* target-speed) 1.0)")
            message = ""

        if PREFIX + "slowjak" == str(args[0]).lower() and on_check("slowjak") and cd_check("slowjak"):
            deactivate("fastjak")
            deactivate("noeco")
            sendForm("(set! (-> *FACT-bank* eco-full-timeout) (seconds 20.0))(pc-cheat-toggle-and-tune *pc-settings* eco-yellow)")
            active_check("slowjak",
            "(send-event *target* 'reset-pickup 'eco)(set! (-> *walk-mods* target-speed) 20000.0)(set! (-> *double-jump-mods* target-speed) 20000.0)(set! (-> *jump-mods* target-speed) 20000.0)(set! (-> *jump-attack-mods* target-speed) 20000.0)(set! (-> *attack-mods* target-speed) 20000.0)(set! (-> *stone-surface* target-speed) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 0))",
            "(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))(send-event *target* 'get-pickup (pickup-type eco-blue) 0.1)")
            message = ""

        if PREFIX + "pacifist" == str(args[0]).lower() and on_check("pacifist") and cd_check("pacifist"):
            active_check("pacifist", 
            "(set! (-> *TARGET-bank* punch-radius) (meters -1.0))(set! (-> *TARGET-bank* spin-radius) (meters -1.0))(set! (-> *TARGET-bank* flop-radius) (meters -1.0))(set! (-> *TARGET-bank* uppercut-radius) (meters -1.0))",
            "(set! (-> *TARGET-bank* punch-radius) (meters 1.3))(set! (-> *TARGET-bank* spin-radius) (meters 2.2))(set! (-> *TARGET-bank* flop-radius) (meters 1.4))(set! (-> *TARGET-bank* uppercut-radius) (meters 1))")
            message = ""

        if PREFIX + "trip" == str(args[0]).lower() and on_check("trip") and cd_check("trip"):
            sendForm("(send-event *target* 'loading)")
            message = ""
            
        #if PREFIX + "bonk" == str(args[0]).lower() and on_check("bonk") and cd_check("bonk"):
        #    sendForm("(dummy-10 (-> *target* skel effect) 'group-smack-surface (the-as float 0.0) 5)(send-event *target* 'shove)(sound-play \"smack-surface\")")
        #    message = ""

        if PREFIX + "shortfall" == str(args[0]).lower() and on_check("shortfall") and cd_check("shortfall"):
            active_check("shortfall", 
            "(set! (-> *TARGET-bank* fall-far) (meters 2.5))(set! (-> *TARGET-bank* fall-far-inc) (meters 3.5))",
            "(set! (-> *TARGET-bank* fall-far) (meters 30))(set! (-> *TARGET-bank* fall-far-inc) (meters 20))")
            message = ""

        if PREFIX + "ghostjak" == str(args[0]).lower() and on_check("ghostjak") and cd_check("deload"):
            active_check("ghostjak", 
            "(set! (-> *TARGET-bank* body-radius) (meters -1.0))",
            "(set! (-> *TARGET-bank* body-radius) (meters 0.7))")
            message = ""
            
        if PREFIX + "getoff" == str(args[0]).lower() and on_check("getoff") and cd_check("getoff"):
            sendForm("(when (not (movie?))(send-event *target* 'end-mode))")
            message = ""
            
        if PREFIX + "unzoom" == str(args[0]).lower() and on_check("unzoom") and cd_check("unzoom"):
            sendForm("(send-event *target* 'no-look-around (seconds 0.1))")
            message = ""

        if (PREFIX + "flutspeed" == str(args[0]).lower() or PREFIX + "setflutflut" == str(args[0]).lower()) and len(args) >= 2 and max_val(args[1], -200, 200) and on_check("flutspeed") and cd_check("flutspeed"):
            sendForm("(set! (-> *flut-walk-mods* target-speed)(meters " + str(args[1]) + "))")
            message = ""

        if PREFIX + "freecam" == str(args[0]).lower() and on_check("freecam") and cd_check("freecam"):
            active_check("freecam", 
            "(stop 'debug)",
            "(start 'play (get-or-create-continue! *game-info*))")
            message = ""

        if PREFIX + "enemyspeed" == str(args[0]).lower() and len(args) >= 3 and max_val(args[1], -200, 200) and on_check("enemyspeed") and cd_check("enemyspeed"):
            sendForm("(set! (-> *" + str(args[1]) + "-nav-enemy-info* run-travel-speed) (meters " + str(args[2]) + "))")
            message = ""

        if PREFIX + "give" == str(args[0]).lower() and len(args) >= 3 and on_check("give") and cd_check("give"):
            sendForm("(set! (-> *game-info* " + str(args[1]) + ") (+ (-> *game-info* " + str(args[1]) + ") " + str(args[2]) + "))")
            message = ""

        if (PREFIX + "collected" == str(args[0]).lower() or PREFIX + "setcollected" == str(args[0]).lower()) and len(args) >= 3 and on_check("collected") and cd_check("give"):
            sendForm("(set! (-> *game-info* " + str(args[1]) + ") (+ 0.0 " + str(args[2]) + "))")
            message = ""

        if PREFIX + "eco" == str(args[0]).lower() and len(args) >= 2 and on_check("eco") and cd_check("eco"):
            sendForm("(send-event *target* 'get-pickup (pickup-type eco-" + str(args[1]) + ") 5.0)")
            message = ""

        if (PREFIX + "sucksuck" == str(args[0]).lower() or PREFIX + "setsucksuck" == str(args[0]).lower()) and len(args) >= 2 and max_val(args[1], -200, 200) and on_check("sucksuck") and cd_check("sucksuck"):
            sendForm("(set! (-> *FACT-bank* suck-suck-dist) (meters " + str(args[1]) + "))(set! (-> *FACT-bank* suck-bounce-dist) (meters " + str(args[1]) + "))")
            message = ""

        if PREFIX + "noeco" == str(args[0]).lower() and not active[command_names.index("slowjak")] and on_check("noeco") and cd_check("noeco"):
            active_check("noeco", 
            "(send-event *target* 'reset-pickup 'eco)(set! (-> *FACT-bank* eco-full-timeout) (seconds 0.0))",
            "(set! (-> *FACT-bank* eco-full-timeout) (seconds 20.0))")
            message = ""

        if PREFIX + "die" == str(args[0]).lower() and on_check("die") and cd_check("die"):
            sendForm("(when (not (movie?))(initialize! *game-info* 'die (the-as game-save #f) (the-as string #f)))")
            message = ""

        if (PREFIX + "topoint" == str(args[0]).lower() or PREFIX + "gotopoint" == str(args[0]).lower() or PREFIX + "gotolevel" == str(args[0]).lower()) and len(args) >= 2 and point_list.count(str(args[1]).lower()) == 1 and on_check("topoint") and cd_check("topoint"):
            sendForm("(start 'play (get-continue-by-name *game-info* \"" + str(args[1]) + "\"))(auto-save-command 'auto-save 0 0 *default-pool*)")
            message = ""

        if (PREFIX + "randompoint" == str(args[0]).lower() or PREFIX + "randomcheckpoint" == str(args[0]).lower()) and on_check("randompoint") and cd_check("topoint"):
            sendForm("(start 'play (get-continue-by-name *game-info* \"" + point_list[random.choice(range(0,52))] + "\"))(auto-save-command 'auto-save 0 0 *default-pool*)")
            message = ""
			
        #if (PREFIX + "setpoint" == str(args[0]).lower() or PREFIX + "setcheckpoint" == str(args[0]).lower()) and on_check("setpoint") and cd_check("setpoint"):
        #    sendForm("(vector-copy! (-> (-> *game-info* current-continue) trans) (new 'static 'vector :x (-> (target-pos 0) x) :y (-> (target-pos 0) y) :z (-> (target-pos 0) z) :w 1.0))")
        #    message = ""

        if PREFIX + "tp" == str(args[0]).lower() and len(args) >= 4 and on_check("tp") and cd_check("tp"):
            sendForm("(when (not (movie?))(set! (-> (target-pos 0) x) (meters " + str(args[1]) + "))  (set! (-> (target-pos 0) y) (meters " + str(args[2]) + ")) (set! (-> (target-pos 0) z) (meters " + str(args[3]) + ")))")
            message = ""

        if PREFIX + "shift" == str(args[0]).lower() and len(args) >= 4 and on_check("shift") and cd_check("tp"):
            sendForm("(when (not (movie?))(set! (-> (target-pos 0) x) (+ (-> (target-pos 0) x)(meters " + str(args[1]) + ")))  (set! (-> (target-pos 0) y) (+ (-> (target-pos 0) y)(meters " + str(args[2]) + "))) (set! (-> (target-pos 0) z) (+ (-> (target-pos 0) z)(meters " + str(args[3]) + "))))")
            message = ""

        if PREFIX + "rocketman" == str(args[0]).lower() and on_check("rocketman") and cd_check("rocketman"):
            active_check("rocketman", 
            "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters -60.0))(start 'play (get-or-create-continue! *game-info*))",
            "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters 60.0))(start 'play (get-or-create-continue! *game-info*))")
            message = ""

        if PREFIX + "movetojak" == str(args[0]).lower() and len(args) >= 2 and on_check("movetojak") and cd_check("movetojak"):
            sendForm("(when (process-by-ename \"" + str(args[1]) + "\")(set-vector!  (-> (-> (the process-drawable (process-by-ename \"" + str(args[1]) + "\"))root)trans) (-> (target-pos 0) x) (-> (target-pos 0) y) (-> (target-pos 0) z) 1.0))")
            message = ""

        if PREFIX + "ouch" == str(args[0]).lower() and on_check("ouch") and cd_check("ouch"):
            sendForm("(if (not (= *target* #f))(send-event *target* 'attack #t (new 'static 'attack-info)))")
            message = ""

        if PREFIX + "burn" == str(args[0]).lower() and on_check("burn") and cd_check("ouch"):
            sendForm("(if (not (= *target* #f))(target-attack-up *target* 'attack 'burnup))")
            message = ""

        if PREFIX + "hp" == str(args[0]).lower() and len(args) >= 2 and on_check("hp") and cd_check("hp"):
            sendForm("(set! (-> (the-as fact-info-target (-> *target* fact))health) (+ 0.0 " + str(args[1]) + "))")
            message = ""

        if PREFIX + "melt" == str(args[0]).lower() and on_check("melt") and cd_check("die"):
            sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'melt))")
            message = ""

        if PREFIX + "endlessfall" == str(args[0]).lower() and on_check("endlessfall") and cd_check("die"):
            sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'endlessfall))")
            message = ""
			
        if PREFIX + "drown" == str(args[0]).lower() and on_check("drown") and cd_check("die"):
            sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'drown-death))")
            message = ""

        if PREFIX + "iframes" == str(args[0]).lower() and len(args) >= 2 and on_check("iframes") and cd_check("iframes"):
            activate("iframes")
            sendForm("(set! (-> *TARGET-bank* hit-invulnerable-timeout) (seconds " + str(args[1]) + "))")
            message = ""

        if PREFIX + "invertcam" == str(args[0]).lower() and len(args) >= 3 and on_check("invertcam") and cd_check("invertcam"):
            activate("invertcam")
            sendForm("(set! (-> *pc-settings* " + str(args[1]) + "-camera-" + str(args[2]) + "-inverted?) (not (-> *pc-settings* " + str(args[1]) + "-camera-" + str(args[2]) + "-inverted?)))")
            message = ""

       # if PREFIX + "normalcam" == str(args[0]).lower() and on_check("normalcam") and cd_check("normalcam"):
       #     deactivate("invertcam")
       #     sendForm("(set! (-> *pc-settings* third-camera-h-inverted?) #t)(set! (-> *pc-settings* third-camera-v-inverted?) #t)(set! (-> *pc-settings* first-camera-v-inverted?) #t)(set! (-> *pc-settings* first-camera-h-inverted?) #f)")
       #     message = ""

        if PREFIX + "cam" == str(args[0]).lower() and len(args) >= 2 and cam_list.count(str(args[1]).lower()) == 1 and on_check("cam") and cd_check("cam"):
            deactivate("stickycam")
            activate("cam")
            sendForm("(send-event *camera* 'change-state cam-" + str(args[1]) + " 0)(send-event *target* 'no-look-around (seconds " + str(durations[command_names.index("cam")]) + "))")
            message = ""

        if PREFIX + "stickycam" == str(args[0]).lower() and on_check("stickycam") and cd_check("stickycam"):
            deactivate("cam")
            active_check("stickycam",
            "(send-event *target* 'no-look-around (seconds " + str(durations[command_names.index("stickycam")]) + "))(send-event *camera* 'change-state cam-circular 0)",
            "(send-event *target* 'no-look-around (seconds 0))(send-event *camera* 'change-state cam-string 0)")
            message = ""

        if PREFIX + "deload" == str(args[0]).lower() and on_check("deload") and cd_check("deload"):
            sendForm("(when (not (movie?))(set! (-> *load-state* want 0 display?) #f))")
            message = ""

        if (PREFIX + "quickcam" == str(args[0]).lower() or PREFIX + "frickstorage" == str(args[0]).lower()) and on_check("quickcam") and cd_check("quickcam"):
            sendForm("(stop 'debug)(start 'play (get-or-create-continue! *game-info*))")
            time.sleep(0.1)
            sendForm("(set! (-> *game-info* current-continue) (get-continue-by-name *game-info* \"training-start\"))")
            message = ""

        if PREFIX + "dark" == str(args[0]).lower() and on_check("dark") and cd_check("dark"):
            active_check("dark", 
            "(set! (-> (level-get-target-inside *level*) mood-func)update-mood-finalboss)",
            "(set! (-> (level-get-target-inside *level*) mood-func)update-mood-darkcave)")
            message = ""

        if (PREFIX + "nodax" == str(args[0]).lower() or PREFIX + "nodaxter" == str(args[0]).lower()) and on_check("nodax") and cd_check("nodax"):
            active_check("nodax", 
            "(send-event *target* 'sidekick #f)",
            "(send-event *target* 'sidekick #t)")
            message = ""

        if PREFIX + "smallnet" == str(args[0]).lower() and on_check("smallnet") and cd_check("smallnet"):
            active_check("smallnet", 
            "(when (process-by-ename \"fisher-1\")(set!(-> *FISHER-bank* net-radius)(meters 0.0)))",
            "(when (process-by-ename \"fisher-1\")(set! (-> *FISHER-bank* net-radius)(meters 0.7)))")
            message = ""

        if PREFIX + "widefish" == str(args[0]).lower() and on_check("widefish") and cd_check("widefish"):
            active_check("widefish", 
            "(when (process-by-ename \"fisher-1\")(set! (-> *FISHER-bank* width)(meters 10.0)))",
            "(when (process-by-ename \"fisher-1\")(set! (-> *FISHER-bank* width)(meters 3.3)))")
            message = ""

        if (PREFIX + "lowpoly" == str(args[0]).lower() or PREFIX + "lod" == str(args[0]).lower()) and on_check("lowpoly") and cd_check("lowpoly"):
            active_check("lowpoly", 
            "(set! (-> *pc-settings* lod-force-tfrag) 2)(set! (-> *pc-settings* lod-force-tie) 3)(set! (-> *pc-settings* lod-force-ocean) 2)(set! (-> *pc-settings* lod-force-actor) 3)",
            "(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)")
            message = ""

        if PREFIX + "moveplantboss" == str(args[0]).lower() and on_check("moveplantboss") and cd_check("moveplantboss"):
            sendForm("(set! (-> *pc-settings* force-actors?) #t)")
            time.sleep(0.050)
            sendForm("(when (process-by-ename \"plant-boss-3\")(set-vector!  (-> (-> (the process-drawable (process-by-ename \"plant-boss-3\"))root)trans) (meters 436.97) (meters -43.99) (meters -347.09) 1.0))")
            sendForm("(set! (-> (the-as fact-info-target (-> *target* fact))health) 1.0)")
            time.sleep(2)
            sendForm("(set! (-> (target-pos 0) x) (meters 431.47))  (set! (-> (target-pos 0) y) (meters -44.00)) (set! (-> (target-pos 0) z) (meters -334.09)) (set! (-> *pc-settings* force-actors?) #f)")
            message = ""

        if PREFIX + "moveplantboss2" == str(args[0]).lower() and on_check("moveplantboss2") and cd_check("moveplantboss2"):
            sendForm("(set! (-> *pc-settings* force-actors?) #t)")
            time.sleep(0.050)
            sendForm("(when (process-by-ename \"plant-boss-3\")(set-vector!  (-> (-> (the process-drawable (process-by-ename \"plant-boss-3\"))root)trans) (meters 436.97) (meters -43.99) (meters -347.09) 1.0))")
            time.sleep(0.050)
            sendForm("(set! (-> *pc-settings* force-actors?) #f)")
            message = ""

        if PREFIX + "basincell" == str(args[0]).lower() and on_check("basincell") and cd_check("basincell"):
            sendForm("(if (when (process-by-ename \"fuel-cell-45\") (= (-> (->(the process-drawable (process-by-ename \"fuel-cell-45\"))root)trans x)  (meters -266.54)))(when (process-by-ename \"fuel-cell-45\")(set-vector!  (-> (-> (the process-drawable (process-by-ename \"fuel-cell-45\"))root)trans) (meters -248.92) (meters 52.11) (meters -1515.66) 1.0))(when (process-by-ename \"fuel-cell-45\")(set-vector!  (-> (-> (the process-drawable (process-by-ename \"fuel-cell-45\"))root)trans) (meters -266.54) (meters 52.11) (meters -1508.48) 1.0)))")
            message = ""

        if PREFIX + "resetactors" == str(args[0]).lower() and on_check("resetactors") and cd_check("resetactors"):
            sendForm("(reset-actors 'debug)")
            message = ""

        #if PREFIX + "nopunching" == str(args[0]).lower():
        #    sendForm("(set! (-> *FACT-bank* eco-full-timeout) (seconds 20 ))(pc-cheat-toggle-and-tune *pc-settings* eco-yellow)")
        #    message = ""

        if PREFIX + "actorson" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
            sendForm("(set! (-> *pc-settings* force-actors?) #t)")
            message = ""

        if PREFIX + "actorsoff" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
            sendForm("(set! (-> *pc-settings* force-actors?) #f)")
            message = ""

        if PREFIX + "debug" == str(args[0]).lower() and on_check("debug") and COMMAND_MODS.count(user) > 0:
            sendForm("(set! *debug-segment* (not *debug-segment*))(set! *cheat-mode* (not *cheat-mode*))")
            message = ""
			
        if PREFIX + "fixoldsave" == str(args[0]).lower() and on_check("fixoldsave") and COMMAND_MODS.count(user) > 0:
            sendForm("(set! (-> *game-info* current-continue) (get-continue-by-name *game-info* \"training-start\"))(auto-save-command 'auto-save 0 0 *default-pool*)")
            message = ""

        if PREFIX + "save" == str(args[0]).lower() and on_check("save") and COMMAND_MODS.count(user) > 0:            
            sendForm("(auto-save-command 'auto-save 0 0 *default-pool*)")
            message = ""
			   
        if (PREFIX + "resetcooldowns" == str(args[0]).lower() or PREFIX + "resetcds" == str(args[0]).lower()) and COMMAND_MODS.count(user) > 0:           
            for x in range(len(command_names)):
                last_used[x]=0.0
                message = ""
            sendMessage(irc, "/me ~ All cooldowns reset.")
			   
        if (PREFIX + "cd" == str(args[0]).lower() or PREFIX + "cooldown" == str(args[0]).lower()) and len(args) >= 3 and command_names.count(str(args[1]).lower()) == 1 and COMMAND_MODS.count(user) > 0:          
            cooldowns[command_names.index(str(args[1]))]=float(args[2])
            sendMessage(irc, "/me ~ '" + str(args[1]) + "' cooldown set to " + str(args[2]) + "s.")
            message = ""
			   
        if (PREFIX + "dur" == str(args[0]).lower() or PREFIX + "duration" == str(args[0]).lower()) and len(args) >= 3 and command_names.count(str(args[1]).lower()) == 1 and COMMAND_MODS.count(user) > 0:          
            durations[command_names.index(str(args[1]))]=float(args[2])
            sendMessage(irc, "/me ~ '" + str(args[1]) + "' duration set to " + str(args[2]) + "s.")
            message = ""
   
        if PREFIX + "enable" == str(args[0]).lower() and len(args) >= 2 and command_names.count(str(args[1]).lower()) == 1 and COMMAND_MODS.count(user) > 0:          
            on_off[command_names.index(str(args[1]))]="t"
            sendMessage(irc, "/me ~ '" + str(args[1]) + "' enabled.")
            message = ""
			   
        if PREFIX + "disable" == str(args[0]).lower() and len(args) >= 2 and command_names.count(str(args[1]).lower()) == 1 and COMMAND_MODS.count(user) > 0:          
            on_off[command_names.index(str(args[1]))]="f"
            sendMessage(irc, "/me ~ '" + str(args[1]) + "' disabled.")
            message = ""
			   
        if PREFIX + "widejak" == str(args[0]).lower() and on_check("widejak") and cd_check("scale"):
            deactivate("bigjak")
            deactivate("smalljak")
            deactivate("scale")
            deactivate("flatjak")
            active_check("widejak", 
            "(set! (-> (-> (the-as target *target* )root)scale x) 4.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)",
            "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
            message = ""
            
        if PREFIX + "flatjak" == str(args[0]).lower() and on_check("flatjak") and cd_check("scale"):
            deactivate("bigjak")
            deactivate("smalljak")
            deactivate("widejak")
            deactivate("scale")
            active_check("flatjak", 
            "(set! (-> (-> (the-as target *target* )root)scale x) 1.3)(set! (-> (-> (the-as target *target* )root)scale y) 0.2)(set! (-> (-> (the-as target *target* )root)scale z) 1.3)",
            "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
            message = ""    

        if PREFIX + "smalljak" == str(args[0]).lower() and on_check("smalljak") and cd_check("scale"):
            deactivate("bigjak")
            deactivate("scale")
            deactivate("widejak")
            deactivate("flatjak")
            active_check("smalljak", 
            "(set! (-> (-> (the-as target *target* )root)scale x) 0.4)(set! (-> (-> (the-as target *target* )root)scale y) 0.4)(set! (-> (-> (the-as target *target* )root)scale z) 0.4)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 43.25))",
            "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
            message = ""
            
        if PREFIX + "bigjak" == str(args[0]).lower() and on_check("bigjak") and cd_check("scale"):
            deactivate("scale")
            deactivate("smalljak")
            deactivate("widejak")
            deactivate("flatjak")
            active_check("bigjak", 
            "(set! (-> (-> (the-as target *target* )root)scale x) 2.7)(set! (-> (-> (the-as target *target* )root)scale y) 2.7)(set! (-> (-> (the-as target *target* )root)scale z) 2.7)",
            "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
            message = ""
			
        if (PREFIX + "color" == str(args[0]).lower() or PREFIX + "colour" == str(args[0]).lower()) and len(args) >= 4 and on_check("color") and cd_check("color"):
            activate("color")
            sendForm("(set! (-> *target* draw color-mult x) (+ 0.0 " + str(args[1]) + "))(set! (-> *target* draw color-mult y) (+ 0.0 " + str(args[2]) + "))(set! (-> *target* draw color-mult z) (+ 0.0 " + str(args[3]) + "))")
            message = ""
			
        if PREFIX + "scale" == str(args[0]).lower() and len(args) >= 4 and max_val(str(args[1]), -15, 15) and max_val(str(args[2]), -15, 15) and max_val(str(args[3]), -15, 15) and on_check("scale") and cd_check("scale"):
            deactivate("bigjak")
            deactivate("smalljak")
            deactivate("widejak")
            deactivate("flatjak")
            activate("scale")
            sendForm("(set! (-> (-> (the-as target *target* )root)scale x) (+ 0.0 " + str(args[1]) + "))(set! (-> (-> (the-as target *target* )root)scale y) (+ 0.0 " + str(args[2]) + "))(set! (-> (-> (the-as target *target* )root)scale z) (+ 0.0 " + str(args[3]) + "))")
            message = ""
            
        if PREFIX + "slippery" == str(args[0]).lower() and on_check("slippery") and cd_check("slippery"):
            active_check("slippery", 
            "(set! (-> *stone-surface* slope-slip-angle) 16384.0)(set! (-> *stone-surface* slip-factor) 0.7)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* turnv) 0.5)(set! (-> *stone-surface* nonlin-fric-dist) 4091904.0)(set! (-> *stone-surface* fric) 23756.8)",
            "(set! (-> *stone-surface* slope-slip-angle) 8192.0)(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)")
            message = ""

        #if PREFIX + "heatmax" == str(args[0]).lower() and len(args) >= 2:
        #    sendForm("(set! (-> *RACER-bank* heat-max) " + str(args[1]) + ")")
        #    message = ""
            
        #if PREFIX + "loadlevel" == str(args[0]).lower() and len(args) >= 2:
        #    sendForm("(set! (-> *load-state* want 1 name) '" + str(args[1]) + ")(set! (-> *load-state* want 1 display?) 'display)")
        #    message = ""
            
        #if (PREFIX + "setecotime" == str(args[0]).lower() or PREFIX + "ecotime" == str(args[0]).lower()) and len(args) >= 2:
        #    sendForm("(set! (-> *FACT-bank* eco-full-timeout) (seconds " + str(args[1]) + "))")
        #    message = ""

        if PREFIX + "bighead" == str(args[0]).lower() and on_check("bighead") and cd_check("bighead"):
            deactivate("smallhead")
            deactivate("hugehead")
            active_check("bighead",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head))")
            message = ""

        if PREFIX + "smallhead" == str(args[0]).lower() and on_check("smallhead") and cd_check("smallhead"):
            deactivate("bighead")
            deactivate("hugehead")
            active_check("smallhead",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats small-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats small-head)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats small-head))")
            message = ""

        if PREFIX + "bigfist" == str(args[0]).lower() and on_check("bigfist") and cd_check("bigfist"):
            active_check("bigfist",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-fist)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-fist)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats big-fist))")
            message = ""

        if PREFIX + "bigheadnpc" == str(args[0]).lower() and on_check("bigheadnpc") and cd_check("bigheadnpc"):
            active_check("bigheadnpc",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head-npc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head-npc)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))")
            message = ""

        if PREFIX + "hugehead" == str(args[0]).lower() and on_check("hugehead") and cd_check("hugehead"):
            deactivate("bighead")
            deactivate("smallhead")
            active_check("hugehead",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats huge-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats huge-head)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats huge-head))")
            message = ""

        if PREFIX + "mirror" == str(args[0]).lower() and on_check("mirror") and cd_check("mirror"):
            active_check("mirror",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats mirror)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats mirror)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))")
            message = ""

        if (PREFIX + "notex" == str(args[0]).lower() or PREFIX + "notextures" == str(args[0]).lower()) and on_check("notex") and cd_check("notex"):
            active_check("notex",
            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats no-tex)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats no-tex)))",
            "(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))")
            message = ""

        if PREFIX + "press" == str(args[0]).lower() and len(args) >= 2 and input_list.count(str(args[1]).lower()) == 1 and on_check("press") and cd_check("press"):
            sendForm("(logior! (cpad-pressed 0) (pad-buttons " + str(args[1]) + "))")
            message = ""

        if (PREFIX + "lang" == str(args[0]).lower() or PREFIX + "language" == str(args[0]).lower()) and len(args) >= 2 and lang_list.count(str(args[1]).lower()) == 1 and on_check("lang") and cd_check("lang"):
            sendForm("(set! (-> *setting-control* default language) (language-enum " + str(args[1]).lower() + "))")
            message = ""
            
        if PREFIX + "turn-left" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(quaternion-rotate-local-y! (-> *target* root dir-targ) (-> *target* root dir-targ) (/ DEGREES_PER_ROT 8.0))")
          message = ""
        if PREFIX + "turn-right" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(quaternion-rotate-local-y! (-> *target* root dir-targ) (-> *target* root dir-targ) (/ DEGREES_PER_ROT -8.0))")
          message = ""
        if PREFIX + "turn-180" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(quaternion-rotate-local-y! (-> *target* root dir-targ) (-> *target* root dir-targ) (/ DEGREES_PER_ROT 2.0))")
          message = ""
        if PREFIX + "cam-right" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(set! (-> *cpad-list* cpads 0 rightx) (the-as uint 0))")
          message = ""
        if PREFIX + "cam-left" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(set! (-> *cpad-list* cpads 0 rightx) (the-as uint 255))")
          message = ""
        if PREFIX + "cam-in" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(set! (-> *cpad-list* cpads 0 righty) (the-as uint 0))")
          message = ""
        if PREFIX + "cam-out" == str(args[0]).lower() and COMMAND_MODS.count(user) > 0:
          sendForm("(set! (-> *cpad-list* cpads 0 righty) (the-as uint 255))")
          message = ""
            
        if str(args[0]) == PREFIX + "repl" and len(args) >= 2 and on_check("repl") and cd_check("repl"):
            if COMMAND_MODS.count(user) > 0:
                args = message.split(" ", 1)
                sendForm(str(args[1]))
                message = ""
            else:
                sendMessage(irc, "/me @"+user+" Sorry, 'repl' is currently only accessable to the devs.")
                message = ""

        #check which commands have reached their duration, then deactivate
        active_sweep("rjto","(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
        active_sweep("superjump","(set! (-> *TARGET-bank* jump-height-max)(meters 3.5))(set! (-> *TARGET-bank* jump-height-min)(meters 1.01))(set! (-> *TARGET-bank* double-jump-height-max)(meters 2.5))(set! (-> *TARGET-bank* double-jump-height-min)(meters 1))")
        active_sweep("superboosted","(set! (-> *edge-surface* fric) 30720.0)")
        active_sweep("noboosteds","(set! (-> *edge-surface* fric) 30720.0)")
        active_sweep("nojumps","(logclear! (-> *target* state-flags) (state-flags prevent-jump))")
        active_sweep("fastjak","(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *stone-surface* target-speed) 1.0)")
        active_sweep("slowjak", "(pc-cheat-toggle-and-tune *pc-settings* eco-yellow)(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))(send-event *target* 'reset-pickup 'eco)")
        active_sweep("pacifist", "(set! (-> *TARGET-bank* punch-radius) (meters 1.3))(set! (-> *TARGET-bank* spin-radius) (meters 2.2))(set! (-> *TARGET-bank* flop-radius) (meters 1.4))(set! (-> *TARGET-bank* uppercut-radius) (meters 1))")
        active_sweep("shortfall", "(set! (-> *TARGET-bank* fall-far) (meters 30))(set! (-> *TARGET-bank* fall-far-inc) (meters 20))")
        active_sweep("ghostjak", "(set! (-> *TARGET-bank* body-radius) (meters 0.7))")
        active_sweep("freecam", "(start 'play (get-or-create-continue! *game-info*))")
        active_sweep("noeco", "(set! (-> *FACT-bank* eco-full-timeout) (seconds 20.0))")
        active_sweep("invertcam", "(set! (-> *pc-settings* third-camera-h-inverted?) #t)(set! (-> *pc-settings* third-camera-v-inverted?) #t)(set! (-> *pc-settings* first-camera-v-inverted?) #t)(set! (-> *pc-settings* first-camera-h-inverted?) #f)")
        active_sweep("stickycam", "(send-event *target* 'no-look-around (seconds 0))(send-event *camera* 'change-state cam-string 0)")
        active_sweep("cam", "(send-event *camera* 'change-state cam-string 0)")
        active_sweep("dark", "(set! (-> (level-get-target-inside *level*) mood-func)update-mood-darkcave)")
        active_sweep("nodax", "(send-event *target* 'sidekick #t)")
        active_sweep("smallnet", "(when (process-by-ename \"fisher-1\")(set! (-> *FISHER-bank* net-radius)(meters 0.7)))")
        active_sweep("widefish", "(when (process-by-ename \"fisher-1\")(set! (-> *FISHER-bank* width)(meters 3.3)))")
        active_sweep("lowpoly", "(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)")
        active_sweep("widejak", "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        active_sweep("flatjak", "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        active_sweep("smalljak", "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
        active_sweep("bigjak", "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        active_sweep("color", "(set! (-> *target* draw color-mult x) 1.0)(set! (-> *target* draw color-mult y) 1.0)(set! (-> *target* draw color-mult z) 1.0)")
        active_sweep("scale", "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        active_sweep("slippery", "(set! (-> *stone-surface* slope-slip-angle) 8192.0)(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)")
        active_sweep("protect", "")
        active_sweep("iframes","(set! (-> *TARGET-bank* hit-invulnerable-timeout) (seconds 3))")
        active_sweep("rocketman", "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters 60.0))(start 'play (get-or-create-continue! *game-info*))")
        active_sweep("bighead", "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head))")
        active_sweep("smallhead", "(logclear! (-> *pc-settings* cheats) (pc-cheats small-head))")
        active_sweep("bigfist", "(logclear! (-> *pc-settings* cheats) (pc-cheats big-fist))")
        active_sweep("bigheadnpc", "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))")
        active_sweep("hugehead", "(logclear! (-> *pc-settings* cheats) (pc-cheats huge-head))")
        active_sweep("mirror", "(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))")
        active_sweep("notex", "(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))")
        
        #if GK_WIN.poll() is not None:
        #     code that closes goalc
            
            
#Dont touch
def twitch():

    global user
    global message

    def joinchat():
        Loading = True
        while Loading:
            readbuffer_join = irc.recv(1024)
            readbuffer_join = readbuffer_join.decode()
            print(readbuffer_join)
            for line in readbuffer_join.split("\n")[0:-1]:
                print(line)
                Loading = loadingComplete(line)

    def loadingComplete(line):
        if("End of /NAMES list" in line):
            print("TwitchBot has joined " + CHANNEL + "'s Channel!")
            sendMessage(irc, "/me "+CONNECT_MSG)
            return False
        else:
            return True


    def getUser(line):
        #global user
        colons = line.count(":")
        colonless = colons-1
        separate = line.split(":", colons)
        user = separate[colonless].split("!", 1)[0]
        return user

    def getMessage(line):
        #global message
        print(line)
        try:
            colons = line.count(":")
            message = (line.split(":", colons))[colons]
        except:
            message = ""
        return message

    def console(line):
        if "PRIVMSG" in line:
            return False
        else:
            return True

    joinchat()
    irc.send("CAP REQ :twitch.tv/tags\r\n".encode())
    while True:
        try:
            readbuffer = irc.recv(1024).decode()
        except:
            readbuffer = ""
        for line in readbuffer.split("\r\n"):
            if line == "":
                continue
            if "PING :tmi.twitch.tv" in line:
                print(line)
                msgg = "PONG :tmi.twitch.tv\r\n".encode()
                irc.send(msgg)
                print(msgg)
                continue
            else:
                try:
                    user = getUser(line)
                    message = getMessage(line)
                    print("message is " + message)
                except Exception:
                    pass

def main():
    if __name__ =='__main__':
        t1 = threading.Thread(target = twitch)
        t1.start()
        t2 = threading.Thread(target = gamecontrol)
        t2. start()
main()