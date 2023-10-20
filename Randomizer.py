import socket
import subprocess
import time
import sys
import random
import struct
import os
import shutil
from dotenv import load_dotenv

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
    "protect", "rjto", "superjump", "superboosted", "noboosteds","nojumps",
    "fastjak","pacifist","trip",
    "shortfall","ghostjak","sucksuck","noeco","die","ouch",
    "burn","drown","endlessfall","iframes","quickcam","dark","nodax","lowpoly",
    "resetactors", "widejak","flatjak","smalljak","bigjak",
    "slippery","rocketman","unzoom","bighead","smallhead","bigfist",
    "bigheadnpc","hugehead","mirror","notex", "flutspeed", "nuka",
    "highgrav", "lang", "invertcam", "mirror2", "fakecrash", "deload"
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
start_time = time.time()
sendForm("(mi)")
while time.time() - start_time < 40:
    time.sleep(1)
sendForm("(send-event *target* 'get-pickup (pickup-type eco-red) 5.0)")
sendForm("(dotimes (i 1) (sound-play-by-name (static-sound-name \"cell-prize\") (new-sound-id) 1024 0 0 (sound-group sfx) #t))")
sendForm("(set! *cheat-mode* #f)")
sendForm("(set! *debug-segment* #f)")
sendForm("(initialize! *game-info* 'game (the-as game-save #f) \"game-start\")")
sendForm("(set! (-> *setting-control* default play-hints) #f)")
sendForm("(set! (-> *pc-settings* speedrunner-mode?) #f)")
# End Int block

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
    # 7: "slowjak",
    7: "pacifist",
    8: "trip",
    9: "shortfall",
    10: "ghostjak",
    11: "flutspeed",
    12: "sucksuck",
    13: "noeco",
    14: "die",
    15: "ouch",
    16: "burn",
    17: "endlessfall",
    18: "iframes",
    19: "deload",
    20: "quickcam",
    21: "dark",
    22: "nodax",
    23: "lowpoly",
    24: "resetactors",
    25: "widejak",
    26: "flatjak",
    27: "smalljak",
    28: "bigjak",
    29: "slippery",
    30: "rocketman",
    31: "unzoom",
    32: "bighead",
    33: "smallhead",
    34: "bigfist",
    35: "bigheadnpc",
    36: "hugehead",
    37: "mirror",
    38: "notex",
    39: "drown",
    40: "nuka",
    41: "highgrav",
    42: "lang",
    43: "invertcam",
    44: "mirror2",
    45: "fakecrash"
}

# Define a list of available languages
available_languages = ["french", "german", "spanish", "italian", "japanese", "korean"]

def randomize_language():
    selected_language = random.choice(available_languages)
    return selected_language

load_dotenv()

# Number of effects to apply
num_effects_to_apply = int(os.getenv("num_effects_to_apply"))

total_duration = int(os.getenv("total_duration"))
start_time = time.time()
interval = int(os.getenv("interval"))

def apply_effect(effects):
    random_effect = random.sample(range(1, len(effect_mapping) + 1), effects)

    # Deactivate any active effects
    for effect_num in range(1, len(effect_mapping) + 1):
        effect_name = effect_mapping.get(effect_num)
        if effect_name and active[command_names.index(effect_name)]:
            print("Deactivating:", effect_name)
            # Deactivate previous effect(s)
            execute_deactivation(effect_name)

    # Apply selected effects
    for effect_num in random_effect:
        effect_name = effect_mapping.get(effect_num)
        if effect_name:
            print("Applying:", effect_name)
            # Write new effects in "effect.txt" and replace the old ones
            with open("effect.txt", "r") as file:
                lines = file.readlines()
                lines.append("current effect: " + effect_name + "\n")
            if len(lines) > num_effects_to_apply:
                lines = lines[-num_effects_to_apply:]
            with open("effect.txt", "w") as file:
                file.writelines(lines)
            # Activate new effect(s)
            execute_activation(effect_name)

def value_changer(cstring):
    #Call this function with a string to tell it which effect to change
    #some crowd control commands send multiple lines of code
    #having an elif chunk for each lets us pick the rng range for each
    #this requires calling value_changer once per line of goal we send
    if cstring == "rjto":
        # Generate a random value between 1 - 100
        random_value = random.randint(1, 200)
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
    elif cstring == "flutspeed":
        random_value = random.randint(1, 20)
        command =   "(set! (logtest? (-> *target* control root-prim prim-core action) (collide-action flut))(set! (-> *flut-walk-mods* target-speed) (meters {})))".format(random_value)
    elif cstring == "sucksuck1":
        random_value = random.randint(1, 50)
        command = "(set! (-> *FACT-bank* suck-suck-dist) (meters {}))".format(random_value)
    elif cstring == "sucksuck2":
        random_value = random.randint(1, 50)
        command = "(set! (-> *FACT-bank* suck-bounce-dist) (meters {}))".format(random_value)
    elif cstring == "iframes":
        random_value = random.randint(1, 60)
        command = "(set! (-> *TARGET-bank* hit-invulnerable-timeout) (seconds {}))".format(random_value)
    elif cstring == "unzoom":
        random_value = random.randint(1, 120)
        command = "(send-event *target* 'no-look-around (seconds {}))".format(random_value)
    elif cstring == "highgrav":
        random_value = random.randint(100, 500)
        command = "(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters {}))(start 'play (get-or-create-continue! *game-info*))".format(random_value)
    elif cstring == "fakecrash":
        random_value = random.randint(10, 30)
        command = "(set-blackout-frames (seconds {}))".format(random_value)
    print(command)
    return command


def execute_activation(effect_name):
    global message

    if effect_name == "rjto" and on_check("rjto"):
        activate("rjto")
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
        activate("noboosteds")
        sendForm("(set! (-> *edge-surface* fric) 1530000.0)")
        message = ""
    elif effect_name == "nojumps" and on_check("nojumps"):
        activate("nojumps")
        sendForm("(logior! (-> *target* state-flags) (state-flags prevent-jump))",)
        message = ""
    elif effect_name == "fastjak" and on_check("fastjak"):
        activate("fastjak")
        sendForm("(set! (-> *walk-mods* target-speed) 77777.0)(set! (-> *double-jump-mods* target-speed) 77777.0)(set! (-> *jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *attack-mods* target-speed) 77777.0)(set! (-> *forward-high-jump-mods* target-speed) 77777.0)(set! (-> *jump-attack-mods* target-speed) 77777.0)(set! (-> *stone-surface* target-speed) 1.25)")
        message = ""
    elif effect_name == "pacifist" and on_check("pacifist"):
        activate("pacifist")
        sendForm("(set! (-> *TARGET-bank* punch-radius) (meters -1.0))(set! (-> *TARGET-bank* spin-radius) (meters -1.0))(set! (-> *TARGET-bank* flop-radius) (meters -1.0))(set! (-> *TARGET-bank* uppercut-radius) (meters -1.0))")
        message = ""
    elif effect_name == "trip" and on_check("trip"):
        activate("trip")
        sendForm("(send-event *target* 'loading)")
        message = ""
    elif effect_name == "shortfall" and on_check("shortfall"):
        activate("shortfall")
        sendForm("(set! (-> *TARGET-bank* fall-far) (meters 2.5))(set! (-> *TARGET-bank* fall-far-inc) (meters 3.5))")
        message = ""
    elif effect_name == "ghostjak" and on_check("ghostjak"):
        activate("ghostjak")
        sendForm("(set! (-> *TARGET-bank* body-radius) (meters -1.0))")
        message = ""
    elif effect_name == "flutspeed" and on_check("flutspeed"):
        activate("flutspeed")
        sendForm(value_changer("flutspeed"))
        message = ""
    elif effect_name == "sucksuck" and on_check("sucksuck"):
        activate("sucksuck")
        sendForm(value_changer("sucksuck1"))
        sendForm(value_changer("sucksuck2"))
        message = ""
    elif effect_name == "noeco" and on_check("noeco"):
        activate("noeco")
        sendForm("(send-event *target* 'reset-pickup 'eco)(set! (-> *FACT-bank* eco-full-timeout) (seconds 0.0))")
        message = ""
    elif effect_name == "die" and on_check("die"):
        activate("die")
        sendForm("(when (not (movie?))(initialize! *game-info* 'die (the-as game-save #f) (the-as string #f)))")
        message = ""
    elif effect_name == "ouch" and on_check("ouch"):
        activate("ouch")
        sendForm("(if (not (= *target* #f))(send-event *target* 'attack #t (new 'static 'attack-info)))")
        message = ""
    elif effect_name == "burn" and on_check("burn"):
        activate("burn")
        sendForm("(if (not (= *target* #f))(target-attack-up *target* 'attack 'burnup))")
        message = ""
    elif effect_name == "endlessfall" and on_check("endlessfall"):
        activate("endlessfall")
        sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'endlessfall))")
        message = ""
    elif effect_name == "iframes" and on_check("iframes"):
        activate("iframes")
        sendForm(value_changer("iframes"))
        message = ""
    elif effect_name == "deload" and on_check("deload"):
        activate("deload")
        sendForm("(when (not (movie?))(set! (-> *load-state* want 0 display?) #f))")
        time.sleep(3)
        sendForm("(when (not (movie?))(initialize! *game-info* 'die (the-as game-save #f) (the-as string #f)))")
        message = ""
    elif effect_name == "quickcam" and on_check("quickcam"):
        activate("quickcam")
        sendForm("(stop 'debug)(start 'play (get-or-create-continue! *game-info*))")
        time.sleep(0.1)
        sendForm("(set! (-> *game-info* current-continue) (get-continue-by-name *game-info* \"training-start\"))")
        message = ""
    elif effect_name == "dark" and on_check("dark"):
        activate("dark")
        sendForm("(set! (-> (level-get-target-inside *level*) mood-func)update-mood-finalboss)")
        message = ""
    elif effect_name == "nodax" and on_check("nodax"):
        activate("nodax")
        sendForm("(send-event *target* 'sidekick #f)")
        message = ""
    elif effect_name == "lowpoly" and on_check("lowpoly"):
        activate("lowpoly")
        sendForm("(set! (-> *pc-settings* lod-force-tfrag) 2)(set! (-> *pc-settings* lod-force-tie) 3)(set! (-> *pc-settings* lod-force-ocean) 2)(set! (-> *pc-settings* lod-force-actor) 3)")
        message = ""
    elif effect_name == "resetactors" and on_check("resetactors"):
        activate("resetactors")
        sendForm("(reset-actors 'debug)")
        message = ""
    elif effect_name == "widejak" and on_check("widejak"):
        activate("widejak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 4.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        message = ""
    elif effect_name == "flatjak" and on_check("flatjak"):
        activate("flatjak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 1.3)(set! (-> (-> (the-as target *target* )root)scale y) 0.2)(set! (-> (-> (the-as target *target* )root)scale z) 1.3)")
        message = ""
    elif effect_name == "smalljak" and on_check("smalljak"):
        activate("smalljak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 0.4)(set! (-> (-> (the-as target *target* )root)scale y) 0.4)(set! (-> (-> (the-as target *target* )root)scale z) 0.4)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 43.25))")
        message = ""
    elif effect_name == "bigjak" and on_check("bigjak"):
        activate("bigjak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 2.7)(set! (-> (-> (the-as target *target* )root)scale y) 2.7)(set! (-> (-> (the-as target *target* )root)scale z) 2.7)")
        message = ""
    elif effect_name == "slippery" and on_check("slippery"):
        activate("slippery")
        sendForm("(set! (-> *stone-surface* slope-slip-angle) 16384.0)(set! (-> *stone-surface* slip-factor) 0.7)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* turnv) 0.5)(set! (-> *stone-surface* nonlin-fric-dist) 4091904.0)(set! (-> *stone-surface* fric) 23756.8)")
        message = ""
    elif effect_name == "rocketman" and on_check("rocketman"):
        activate("rocketman")
        sendForm("(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters -5.0))(start 'play (get-or-create-continue! *game-info*))")
        message = ""
    elif effect_name == "unzoom" and on_check("unzoom"):
        activate("unzoom")
        sendForm(value_changer("unzoom"))
        message = ""
    elif effect_name == "bighead" and on_check("bighead"):
        activate("bighead")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats big-head))")
        message = ""
    elif effect_name == "smallhead" and on_check("smallhead"):
        activate("smallhead")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats small-head))")
        message = ""
    elif effect_name == "bigfist" and on_check("bigfist"):
        activate("bigfist")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats big-fist))")
        message = ""
    elif effect_name == "bigheadnpc" and on_check("bigheadnpc"):
        activate("bigheadnpc")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats big-head-npc))")
        message = ""
    elif effect_name == "hugehead" and on_check("hugehead"):
        activate("hugehead")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats huge-head))")
        message = ""
    elif effect_name == "mirror" and on_check("mirror"):
        activate("mirror")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats mirror))")
        message = ""
    elif effect_name == "notex" and on_check("notex"):
        activate("notex")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats no-tex))")
        message = ""
    elif effect_name == "drown" and on_check("drown"):
        activate("drown")
        sendForm("(when (not (movie?))(target-attack-up *target* 'attack 'drown-death))")
        message = ""
    elif effect_name == "nuka" and on_check("nuka"):
        activate("nuka")
        sendForm("(logior! (-> *target* state-flags) (state-flags dying))")
        message = ""
    elif effect_name == "highgrav" and on_check("highgrav"):
        activate("highgrav")
        sendForm(value_changer("highgrav"))
        message = ""
    elif effect_name == "invertcam" and on_check("invertcam"):
        activate("invertcam")
        sendForm("(not! (-> *pc-settings* third-camera-h-inverted?))")
        message = ""
    elif effect_name == "lang" and on_check("lang"):
        activate("lang")
        selected_language = randomize_language()
        sendForm(f"(set! (-> *pc-settings* text-language) (pc-language {selected_language}))")
        sendForm(f"(set! (-> *setting-control* default language) (language-enum {selected_language}))")
        message = ""
    elif effect_name == "mirror2" and on_check("mirror2"):
        activate("mirror2")
        sendForm("(logior! (-> *pc-settings* cheats) (pc-cheats mirror-v))")
        message = ""
    elif effect_name ==  "fakecrash" and on_check("fakecrash"):
        activate("fakecrash")
        sendForm(value_changer("fakecrash"))
        message = ""


# Deactivate the previous effects
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
        deactivate("noboosteds")
        sendForm("(set! (-> *edge-surface* fric) 30720.0)")
        message = ""
    elif effect_name == "nojumps" and on_check("nojumps"):
        deactivate("nojumps")
        sendForm("(logclear! (-> *target* state-flags) (state-flags prevent-jump))")
        message = ""
    elif effect_name == "fastjak" and on_check("fastjak"):
        deactivate("fastjak")
        sendForm("(set! (-> *walk-mods* target-speed) 40960.0)(set! (-> *double-jump-mods* target-speed) 32768.0)(set! (-> *jump-mods* target-speed) 40960.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *attack-mods* target-speed) 40960.0)(set! (-> *forward-high-jump-mods* target-speed) 45056.0)(set! (-> *jump-attack-mods* target-speed) 24576.0)(set! (-> *stone-surface* target-speed) 1.0)")
        message = ""
    elif effect_name == "pacifist" and on_check("pacifist"):
        deactivate("pacifist")
        sendForm("(set! (-> *TARGET-bank* punch-radius) (meters 1.3))(set! (-> *TARGET-bank* spin-radius) (meters 2.2))(set! (-> *TARGET-bank* flop-radius) (meters 1.4))(set! (-> *TARGET-bank* uppercut-radius) (meters 1))")
        message = ""
    elif effect_name == "trip" and on_check("trip"):
        deactivate("trip")
        sendForm("(send-event *target* 'loading)")
        message = ""
    elif effect_name == "shortfall" and on_check("shortfall"):
        deactivate("shortfall")
        sendForm("(set! (-> *TARGET-bank* fall-far) (meters 30))(set! (-> *TARGET-bank* fall-far-inc) (meters 20))")
        message = ""
    elif effect_name == "ghostjak" and on_check("ghostjak"):
        deactivate("ghostjak")
        sendForm("(set! (-> *TARGET-bank* body-radius) (meters 0.7))")
        message = ""
    elif effect_name == "flutspeed" and on_check("flutspeed"):
        deactivate("flutspeed")
        sendForm("(set! (logtest? (-> *target* control root-prim prim-core action) (collide-action flut))(set! (-> *flut-walk-mods* target-speed) (meters 20.0))")
        message = ""
    elif effect_name == "sucksuck" and on_check("sucksuck"):
        deactivate("sucksuck")
        sendForm("(set! (-> *FACT-bank* suck-suck-dist) (meters 7.5)")
        sendForm("(set! (-> *FACT-bank* suck-bounce-dist) (meters 18.0)")
        message = ""
    elif effect_name == "noeco" and on_check("noeco"):
        deactivate("noeco")
        sendForm("(set! (-> *FACT-bank* eco-full-timeout) (seconds 20.0))")
        message = ""
    elif effect_name == "iframes" and on_check("iframes"):
        deactivate("iframes")
        sendForm("(set! (-> *TARGET-bank* hit-invulnerable-timeout) (seconds 3))")
        message = ""
    elif effect_name == "quickcam" and on_check("quickcam"):
        deactivate("quickcam")
        sendForm("(stop 'debug)(start 'play (get-or-create-continue! *game-info*))")
        time.sleep(0.1)
        sendForm("(set! (-> *game-info* current-continue) (get-continue-by-name *game-info* \"training-start\"))")
        message = ""
    elif effect_name == "dark" and on_check("dark"):
        deactivate("dark")
        sendForm("(set! (-> (level-get-target-inside *level*) mood-func)update-mood-darkcave)")
        message = ""
    elif effect_name == "nodax" and on_check("nodax"):
        deactivate("nodax")
        sendForm("(send-event *target* 'sidekick #f)")
        message = ""
    elif effect_name == "lowpoly" and on_check("lowpoly"):
        deactivate("lowpoly")
        sendForm("(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)")
        message = ""
    elif effect_name == "resetactors" and on_check("resetactors"):
        deactivate("resetactors")
        sendForm("(reset-actors 'debug)")
        message = ""
    elif effect_name == "widejak" and on_check("widejak"):
        deactivate("widejak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        message = ""
    elif effect_name == "flatjak" and on_check("flatjak"):
        deactivate("flatjak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        message = ""
    elif effect_name == "smalljak" and on_check("smalljak"):
        deactivate("smalljak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)(set! (-> *TARGET-bank* wheel-flip-dist) (meters 17.3))")
        message = ""
    elif effect_name == "bigjak" and on_check("bigjak"):
        deactivate("bigjak")
        sendForm("(set! (-> (-> (the-as target *target* )root)scale x) 1.0)(set! (-> (-> (the-as target *target* )root)scale y) 1.0)(set! (-> (-> (the-as target *target* )root)scale z) 1.0)")
        message = ""
    elif effect_name == "slippery" and on_check("slippery"):
        deactivate("slippery")
        sendForm("(set! (-> *stone-surface* slope-slip-angle) 8192.0)(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)")
        message = ""
    elif effect_name == "rocketman" and on_check("rocketman"):
        deactivate("rocketman")
        sendForm("(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters 60.0))(start 'play (get-or-create-continue! *game-info*))")
        message = ""
    elif effect_name == "unzoom" and on_check("unzoom"):
        deactivate("unzoom")
        sendForm("(send-event *target* 'no-look-around (seconds 0.1))")
        message = ""
    elif effect_name == "bighead" and on_check("bighead"):
        deactivate("bighead")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats big-head))")
        message = ""
    elif effect_name == "smallhead" and on_check("smallhead"):
        deactivate("smallhead")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats small-head))")
        message = ""
    elif effect_name == "bigfist" and on_check("bigfist"):
        deactivate("bigfist")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats big-fist))")
        message = ""
    elif effect_name == "bigheadnpc" and on_check("bigheadnpc"):
        deactivate("bigheadnpc")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))")
        message = ""
    elif effect_name == "hugehead" and on_check("hugehead"):
        deactivate("hugehead")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats huge-head))")
        message = ""
    elif effect_name == "mirror" and on_check("mirror"):
        deactivate("mirror")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))")
        message = ""
    elif effect_name == "notex" and on_check("notex"):
        deactivate("notex")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))")
        message = ""
    elif effect_name == "nuka" and on_check("nuka"):
        deactivate("nuka")
        sendForm("(logclear! (-> *target* state-flags) (state-flags dying)))")
        message = ""
    elif effect_name == "highgrav" and on_check("highgrav"):
        deactivate("highgrav")
        sendForm("(stop 'debug)(set! (-> *standard-dynamics* gravity-length) (meters 60.0))(start 'play (get-or-create-continue! *game-info*))")
        message = ""
    elif effect_name == "lang" and on_check("lang"):
        deactivate("lang")
        sendForm("(set! (-> *pc-settings* text-language) (pc-language english))")
        sendForm("(set! (-> *setting-control* default language) (language-enum english))")
        message = ""
    elif effect_name == "invertcam" and on_check("invertcam"):
        deactivate("invertcam")
        sendForm("(not! (-> *pc-settings* third-camera-h-inverted?))")
        message = ""
    elif effect_name == "mirror2" and on_check("mirror2"):
        deactivate("mirror2")
        sendForm("(logclear! (-> *pc-settings* cheats) (pc-cheats mirror-v))")
        message = ""


while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    # Calculate the remaining time (assuming you have a total_duration)
    remaining_time = total_duration - elapsed_time

    with open("timer.txt", "w") as file:
        file.write("seconds remaining: " + str(round(remaining_time, 0)))

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