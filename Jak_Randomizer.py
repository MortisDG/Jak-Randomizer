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


# Randomizer made by Mortis
# Help from: barg & zed
# Created: 10/08/2023 
# Used repo for effects: https://github.com/Zedb0T/Opengoal-Twitch-CrowdControl/blob/main/resources/twitchcommands.py

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
    
#paths
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
  
lang_list = ["english","french","german","spanish","italian","japanese","uk-english"]
input_list = ["square","circle","x","triangle","up","down","left","right"]
cam_list = ["endlessfall","eye","standoff","bike","stick"]

# Defined list of effects
command_names = [
    "protect","rjto","superjump","superboosted","noboosteds","nojumps","fastjak","slowjak","pacifist","trip",
    "shortfall","ghostjak","flutspeed","sucksuck","noeco","die","ouch",
    "burn","hp","melt","drown","endlessfall","iframes","invertcam","cam","stickycam","deload",
    "quickcam","dark","nodax","lowpoly",
    "resetactors","repl","debug","save","resetcooldowns","cd","dur","enable","disable",
    "widejak","flatjak","smalljak","bigjak","color","scale","slippery","rocketman","actorson",
    "actorsoff","unzoom","bighead","smallhead","bigfist","bigheadnpc","hugehead","mirror","notex","press",
    "lang", "color", "scale", "bonk"]

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
        return True
    elif COOLDOWN_MSG == "t":
        # sendMessage(irc, "/me @"+user+" Command '"+command_names[command_names.index(cmd)]+"' is on cooldown ("+str(int(last_used[command_names.index(cmd)]-(time.time()-cooldowns[command_names.index(cmd)])))+"s left).")
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
        # sendMessage(irc, "/me @"+user+" Command '"+command_names[command_names.index(cmd)]+"' is disabled.")
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

# Split GK commands into args for gk.exe
GKCOMMANDLINElist = PATHTOGK.split()

# Defined dictionary map from name effects to numbers
effect_mapping = {
    1: "rjto",
    2: "superjump",
    3: "superboosted",
    4: "noboosteds",
    5: "nojumps",
    6: "fastjak",
    7: "slowjak",
    8: "pacifist",
    9: "trip",
    10: "shortfall",
    11: "ghostjak",
    11: "flutspeed",
    12: "sucksuck",
    13: "noeco",
    14: "die",
    15: "ouch",
    16: "burn",
    17: "hp",
    18: "melt",
    19: "endlessfall",
    20: "iframes",
    21: "invertcam",
    22: "cam",
    23: "stickycam",
    24: "deload",
    25: "quickcam",
    26: "dark",
    27: "nodax",
    28: "lowpoly",
    29: "resetactors",
    30: "widejak",
    31: "flatjak",
    32: "smalljak",
    33: "bigjak",
    34: "color",
    35: "scale",
    36: "slippery",
    37: "rocketman",
    38: "unzoom",
    39: "bighead",
    40: "smallhead",
    41: "bigfist",
    42: "bigheadnpc",
    43: "hugehead",
    44: "mirror",
    45: "notex",
    46: "press",
    47: "lang",
    48: "bonk",
    49: "drown",

}

# Number of effects to apply
num_effects_to_apply = 3

start_time = time.time()
interval = 1 * 60 

while True:
    args = message.split(" ")
def apply_effects(effects):
    random_effect = random.sample(range(1, 49), effects)

    # Apply selected effects
    for effect_num in random_effects:
        effect_name = effect_mapping.get(effect_num)
        if effect_name:
            execute_effect(effect_name)

def execute_effect(effect_name):
    global message

    if effect_name == "rjto" and on_check("rjto") and cd_check("rjto"):
        activate("rjto")
        sendForm("(set! (-> *TARGET-bank* wheel-flip-dist) (meters " + str(args[1]) + "))")
        message = ""

    if effect_name == "superjump" and on_check("superjump") and cd_check("superjump"):
        "(set! (-> *TARGET-bank* jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* jump-height-min)(meters 5.0))(set! (-> *TARGET-bank* double-jump-height-max)(meters 15.0))(set! (-> *TARGET-bank* double-jump-height-min)(meters 5.0))",
        # "(set! (-> *TARGET-bank* jump-height-max)(meters 3.5))(set! (-> *TARGET-bank* jump-height-min)(meters 1.01))(set! (-> *TARGET-bank* double-jump-height-max)(meters 2.5))(set! (-> *TARGET-bank* double-jump-height-min)(meters 1))"
        message = ""

    if effect_name == "superboosted" and on_check("superboosted") and cd_check("superboosted"):
        "(set! (-> *edge-surface* fric) 1.0)",
        # "(set! (-> *edge-surface* fric) 30720.0)"
        message = ""

    if effect_name == "noboosteds" and on_check("noboosteds") and cd_check("noboosteds"):
        "(set! (-> *edge-surface* fric) 1530000.0)",
        # "(set! (-> *edge-surface* fric) 30720.0)"
        message = ""

    if effect_name == "fastjak" and on_check("fastjak") and cd_check("fastjak"):
        "(set! (-> *walk-mods* target-speed) 77777.0)(set! (-> *double-jump-mods* target-speed) 77777.0)(set! (-> *jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *attack-mods* target-speed) 77777.0)(set! (-> *forward-high-jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *stone-surface* target-speed) 1.25)",
        # "(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *stone-surface* target-speed) 1.0)"
        message == ""

    if effect_name == "slowjak" and on_check("slowjak") and cd_check("slowjak"):
        "(send-event *target* 'reset-pickup 'eco)(set! (-> *walk-mods* target-speed) 20000.0)(set! (-> *double-jump-mods* target-speed) 20000.0)(set! (-> *jump-mods* target-speed) 20000.0)(set! (-> *jump-attack-mods* target-speed) 20000.0)(set! (-> *attack-mods* target-speed) 20000.0)(set! (-> *stone-surface* target-speed) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 0))",
        "(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))(send-event *target* 'get-pickup (pickup-type eco-blue) 0.1)"
        message == ""

    if effect_name == "trip" and on_check("trip") and cd_check("trip"):
        sendForm("(send-event *target* 'loading)")
        message == ""
    
    if effect_name == "bonk" and on_check("bonk") and cd_check("bonk"):
        sendForm("(dummy-10 (-> *target* skel effect) 'group-smack-surface (the-as float 0.0) 5)(send-event *target* 'shove)(sound-play \"smack-surface\")")
        message == ""

    if effect_name == "shortfall" and on_check("shortfall") and cd_check("shortfall"):
        "(set! (-> *TARGET-bank* fall-far) (meters 2.5))(set! (-> *TARGET-bank* fall-far-inc) (meters 3.5))",
        # "(set! (-> *TARGET-bank* fall-far) (meters 30))(set! (-> *TARGET-bank* fall-far-inc) (meters 20))"
        message == ""

    if effect_name == "ghostjak" and on_check("ghostjak") and cd_check("ghostjak"):
        "(set! (-> *TARGET-bank* body-radius) (meters -1.0))",
        # "(set! (-> *TARGET-bank* body-radius) (meters 0.7))"
        message == ""

    if effect_name == "unzoom" and on_check("unzoom") and cd_check("unzoom"):
        sendForm("(send-event *target* 'no-look-around (seconds 0.1))")
        message == ""

    if effect_name == "flutspeed" and on_check("flutspeed") and cd_check("flutspeed"):
        sendForm("(set! (-> *flut-walk-mods* target-speed)(meters " + str(args[1]) + "))")
        message == ""

    if effect_name == "sucksuck" and on_check("sucksuck") and cd_check("sucksuck"):
        sendForm("(set! (-> *FACT-bank* suck-suck-dist) (meters " + str(args[1]) + "))(set! (-> *FACT-bank* suck-bounce-dist) (meters " + str(args[1]) + "))")
        message == ""

    if effect_name == "noeco" and on_check("noeco") and cd_check("noeco"):
        "(send-event *target* 'reset-pickup 'eco)(set! (-> *FACT-bank* eco-full-timeout) (seconds 0.0))",
        # "(set! (-> *FACT-bank* eco-full-timeout) (seconds 20.0))"
        message == ""

    if effect_name == "die" and on_check("die") and cd_check("die"):
        sendForm("(when (not (movie?))(initialize! *game-info* 'die (the-as game-save #f) (the-as string #f)))")
        message == ""

    if effect_name == "ouch" and on_check("ouch") and cd_check("ouch"):
        sendForm("(if (not (= *target* #f))(send-event *target* 'attack #t (new 'static 'attack-info)))")
        message == ""

    if effect_name == "burn" and on_check("burn") and cd_check("burn"):
        sendForm("(if (not (= *target* #f))(target-attack-up *target* 'attack 'burnup))")
        message == ""

    if effect_name == "hp" and on_check("hp") and cd_check("hp"):
        sendForm("(set! (-> (the-as fact-info-target (-> *target* fact))health) (+ 0.0 " + str(args[1]) + "))")
        message == ""

    if effect_name == "melt" and on_check("melt") and cd_check("melt"):
        sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'melt))")
        message == ""

    if effect_name == "endlessfall" and on_check("endlessfall") and cd_check("endlessfall"):
        sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'endlessfall))")
        message == ""

    if effect_name == "iframes" and on_check("iframes") and cd_check("iframes"):
        sendForm("(set! (-> *TARGET-bank* hit-invulnerable-timeout) (seconds " + str(args[1]) + "))")
        message == ""
    
    if effect_name == "invertcam" and on_check("invertcam") and cd_check("invertcam"):
        sendForm("(set! (-> *pc-settings* " + str(args[1]) + "-camera-" + str(args[2]) + "-inverted?) (not (-> *pc-settings* " + str(args[1]) + "-camera-" + str(args[2]) + "-inverted?)))")
        message == ""

    if effect_name == "cam" and on_check("cam") and cd_check("cam"):
        sendForm("(send-event *camera* 'change-state cam-" + str(args[1]) + " 0)(send-event *target* 'no-look-around (seconds " + str(durations[command_names.index("cam")]) + "))")
        message == ""

    if effect_name == "stickycam" and on_check("stickycam") and cd_check("stickycam"):
        "(send-event *target* 'no-look-around (seconds " + str(durations[command_names.index("stickycam")]) + "))(send-event *camera* 'change-state cam-circular 0)",
        # "(send-event *target* 'no-look-around (seconds 0))(send-event *camera* 'change-state cam-string 0)"
        message == ""

    if effect_name == "deload" and on_check("deload") and cd_check("deload"):
        sendForm("(when (not (movie?))(set! (-> *load-state* want 0 display?) #f))")
        message == ""

    if effect_name == "quickcam" and on_check("quickcam") and cd_check("quickcam"):
        sendForm("(stop 'debug)(start 'play (get-or-create-continue! *game-info*))")
        time.sleep(0.1)
        sendForm("(set! (-> *game-info* current-continue) (get-continue-by-name *game-info* \"training-start\"))")
        message == ""

    if effect_name == "dark" and on_check("dark") and cd_check("dark"):
        "(set! (-> (level-get-target-inside *level*) mood-func)update-mood-finalboss)",
        "(set! (-> (level-get-target-inside *level*) mood-func)update-mood-darkcave)"
        message == ""

    if effect_name == "nodax" and on_check("nodax") and cd_check("nodax"):
        "(send-event *target* 'sidekick #f)",
        # "(send-event *target* 'sidekick #t)"
        message == ""

    if effect_name == "lowpoly" and on_check("lowpoly") and cd_check("lowpoly"):
        "(set! (-> *pc-settings* lod-force-tfrag) 2)(set! (-> *pc-settings* lod-force-tie) 3)(set! (-> *pc-settings* lod-force-ocean) 2)(set! (-> *pc-settings* lod-force-actor) 3)",
        # "(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)"
        message == ""

    if effect_name == "resetactors" and on_check("resetactors") and cd_check("resetactors"):
        sendForm("(reset-actors 'debug)")
        message == ""

    if effect_name == "widejak" and on_check("widejak") and cd_check("widejak"):
        deactivate("bigjak")
        deactivate("smalljak")
        deactivate("scale")
        deactivate("flatjak")
        "(set! (-> (-> (the-as target *target* )root)scale x) 4.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)",
        "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)"
        message == ""

    if effect_name == "flatjak" and on_check("flatjak") and cd_check("flatjak"):
        deactivate("bigjak")
        deactivate("smalljak")
        deactivate("widejak")
        deactivate("scale")
        "(set! (-> (-> (the-as target *target* )root)scale x) 1.3)(set! (-> (-> (the-as target *target* )root)scale y) 0.2)(set! (-> (-> (the-as target *target* )root)scale z) 1.3)",
        "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)"
        message == ""

    if effect_name == "smalljak" and on_check("smalljak") and cd_check("smalljak"):
        deactivate("bigjak")
        deactivate("scale")
        deactivate("widejak")
        deactivate("flatjak") 
        "(set! (-> (-> (the-as target *target* )root)scale x) 0.4)(set! (-> (-> (the-as target *target* )root)scale y) 0.4)(set! (-> (-> (the-as target *target* )root)scale z) 0.4)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 43.25))",
        "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))"
        message = ""

    if effect_name == "bigjak" and on_check("bigjak") and cd_check("bigjak"):
        deactivate("scale")
        deactivate("smalljak")
        deactivate("widejak")
        deactivate("flatjak")
        "(set! (-> (-> (the-as target *target* )root)scale x) 2.7)(set! (-> (-> (the-as target *target* )root)scale y) 2.7)(set! (-> (-> (the-as target *target* )root)scale z) 2.7)",
        "(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)"
        message = ""

    if effect_name == "color" and on_check("color") and cd_check("color"):
        sendForm("(set! (-> *target* draw color-mult x) (+ 0.0 " + str(args[1]) + "))(set! (-> *target* draw color-mult y) (+ 0.0 " + str(args[2]) + "))(set! (-> *target* draw color-mult z) (+ 0.0 " + str(args[3]) + "))")
        message == ""

    if effect_name == "scale" and on_check("scale") and cd_check("scale"):
        deactivate("bigjak")
        deactivate("smalljak")
        deactivate("widejak")
        deactivate("flatjak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) (+ 0.0 " + str(args[1]) + "))(set! (-> (-> (the-as target *target* )root)scale y) (+ 0.0 " + str(args[2]) + "))(set! (-> (-> (the-as target *target* )root)scale z) (+ 0.0 " + str(args[3]) + "))")
        message = ""

    if effect_name == "slippery" and on_check("slippery") and cd_check("slippery"):
        "(set! (-> *stone-surface* slope-slip-angle) 16384.0)(set! (-> *stone-surface* slip-factor) 0.7)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* turnv) 0.5)(set! (-> *stone-surface* nonlin-fric-dist) 4091904.0)(set! (-> *stone-surface* fric) 23756.8)",
        "(set! (-> *stone-surface* slope-slip-angle) 8192.0)(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)"
        message == ""

    if effect_name == "rocketman" and on_check("rocketman") and cd_check("rocketman"):
        "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters -60.0))(start 'play (get-or-create-continue! *game-info*))",
        "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters 60.0))(start 'play (get-or-create-continue! *game-info*))"
        message = ""

    if effect_name == "bighead" and on_check("bighead") and cd_check("bighead"):
        deactivate("smallhead")
        deactivate("hugehead")
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head))"
        message = ""

    if effect_name == "smallhead" and on_check("smallhead") and cd_check("smallhead"):
        deactivate("bighead")
        deactivate("hugehead")
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats small-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats small-head)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats small-head))"
        message = ""

    if effect_name == "hugehead" and on_check("hugehead") and cd_check("hugehead"):
        deactivate("bighead")
        deactivate("smallhead")
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats huge-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats huge-head)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats huge-head))"
        message = ""

    if effect_name == "bigfist" and on_check("bigfist") and cd_check("bigfist"):
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-fist)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-fist)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats big-fist))"
        message = ""

    if effect_name == "bigheadnpc" and on_check("bigheadnpc") and cd_check("bigheadnpc"): 
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head-npc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head-npc)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))"
        message = ""

    if effect_name == "mirror" and on_check("mirror") and cd_check("mirror"): 
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats mirror)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats mirror)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))"
        message = ""

    if effect_name == "notex" and on_check("notex") and cd_check("notex"):    
        "(begin (logior! (-> *pc-settings* cheats) (pc-cheats no-tex)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats no-tex)))",
        "(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))"
        message = ""

    if effect_name == "press" and on_check("press") and cd_check("press"):
        sendForm("(logior! (cpad-pressed 0) (pad-buttons " + str(args[1]) + "))")
        message == ""

    if effect_name == "press" and on_check("press") and cd_check("press"):
        sendForm("(set! (-> *setting-control* default language) (language-enum " + str(args[1]).lower() + "))")
        message = ""



    if current_effect:
        deactivate(current_effect)

    # Activate new effect
        activate(random_effect)

    # Store current active effect
    current_effect = random_effect

    pass
while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= interval:
        # Apply new effect and turn off previous
        selected_effects = 3
        apply_effects(selected_effects)
       
        # Update the start time to the current time
        start_time = current_time
    
# Avoid constant checking
time.sleep(1)


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