import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode as KeycodeUS
from keyboard_layout_win_fr import KeyboardLayout as KeyboardLayoutFR
from keycode_win_fr import Keycode as KeycodeFR
import rotaryio
from fakeButton import *
import adafruit_matrixkeypad
import os

import busio
import terminalio
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_button import Button
import gc

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
from adafruit_st7789 import ST7789

version = '1.0'

tabLang = [['FR','US'],
            [KeyboardLayoutFR, KeyboardLayoutUS],
            [KeycodeFR, KeycodeUS]
]

langCount = len(tabLang[0])
langIndex = 0
language = ''
layerList = []
layerCount = 0
layerIndex = 0
layer = ''

labels = []

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutFR(keyboard)
Keycode = KeycodeFR

cols = [digitalio.DigitalInOut(x) for x in (board.GP10, board.GP11, board.GP12, board.GP13)]
rows = [digitalio.DigitalInOut(x) for x in (board.GP2, board.GP3, board.GP4)]
keys = (
    (0, 1,  2,  3), 
    (4, 5,  6,  7), 
    (8, 9, 10, 11)
    )

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

nb_keys = len(keys) * len(keys[0])

encoder_A = board.GP7
encoder_B = board.GP8
encoder_PUSH = board.GP9
delayLongPush = 1000000000

coder_cw = nb_keys
coder_ccw = coder_cw + 1
nb_keys += 2

time_debounce = 25

dico_flags = {}
in_if = False
in_else = False
wait_else_or_endif = False
wait_endif = False

BUTTON_WIDTH = 64
BUTTON_HEIGHT = 60
BUTTON_MARGIN = 4
STATUS_HEIGHT = 20
BLACK = 0x0
ORANGE = 0xFF8800
WHITE = 0xFFFFFF
GRAY = 0x888888
GREEN = 0x00FF44


def button_grid(row, col):
    return(BUTTON_MARGIN * (row + 1) + BUTTON_WIDTH * row,
        BUTTON_MARGIN * (col + 1) + BUTTON_HEIGHT * col)

def add_button(col, row, label, width=1, color=WHITE, text_color=BLACK):
    pos = button_grid(row, col)
    new_button = Button(x = pos[0], y = pos[1],
                    width=BUTTON_WIDTH * width + BUTTON_MARGIN * (width - 1),
                    height = BUTTON_HEIGHT, label=label, label_font=font,
                    label_color=text_color, fill_color=color,
style=Button.ROUNDRECT)
    buttons.append(new_button)
    return new_button
    
def find_button(label):
    result = None
    for _, btn in enumerate(buttons):
        if btn.label == label:
            result = btn
    return result


def convertLine(line):
    newline = []
    for key in filter(None, line.split(" ")):
        key = key.upper()
        if hasattr(Keycode, key):
            newline.append(getattr(Keycode, key))
        else:
            pass
    return newline

def runScriptLine(line):
    for k in line:
        keyboard.press(k)
    keyboard.release_all()

def sendString(line):
    layout.write(line)

def switchKey(keynum, state):   
    buttons[keynum].selected = True if state == 'KEY_SEL' else False

def parseLine(filename, line):
    global defaultDelay
    global dico_flags
    global in_if
    global in_else
    global wait_else_or_endif
    global wait_endif
    
    if line[0:5] == "LABEL":
        pass
    elif(line[0:3] == "#"):
        pass
    elif(line[0:6] == "IF_NOT"):
        flag = line[7:]
        state = dico_flags.get(flag,False)
        if(not state):
            in_if = True
        else:
            wait_else_or_endif = True
    elif(line[0:2] == "IF"):
        flag = line[3:]
        state = dico_flags.get(flag,False)
        if(state):
            in_if = True
        else:
            wait_else_or_endif = True
    elif(line[0:4] == "ELSE"):
        if( in_if):
            in_if = False
            wait_endif = True
        else:
            if(wait_else_or_endif):
                wait_else_or_endif = False
                in_else = True
    elif(line[0:5] == "ENDIF"):
        if(in_if or in_else or wait_endif or wait_else_or_endif):
            in_if = False
            in_else = False
            wait_else_or_endif = False
            wait_endif = False
    elif(not wait_else_or_endif and not wait_endif):
        if(line[0:5] == "DELAY"):
            time.sleep(float(line[6:])/1000)
        elif(line[0:6] == "STRING"):
            sendString(line[7:])
        elif(line[0:13] == "DEFAULT_DELAY"):
            defaultDelay = int(line[14:]) * 10
        elif(line[0:12] == "DEFAULTDELAY"):
            defaultDelay = int(line[13:]) * 10
        elif(line[0:7] == "KEY_SEL"):
            switchKey(int(filename), "KEY_SEL")
        elif(line[0:9] == "KEY_UNSEL"):
            switchKey(int(filename), "KEY_UNSEL")
        elif(line[0:8] == "SET_FLAG"):
            arg = line[9:]
            dico_flags[arg]=True
        elif(line[0:10] == "RESET_FLAG"):
            arg = line[11:]
            dico_flags[arg]=False
        else:
            newScriptLine = convertLine(line)
            runScriptLine(newScriptLine)

def runScript(filename):
    global in_if
    global in_else
    global wait_else_or_endif
    global wait_endif
    global language
    
    in_if = False
    in_else = False
    wait_else_or_endif = False
    wait_endif = False

    
    f = open(scriptsLib+'/'+filename,"r",encoding='utf-8')
    previousLine = ""
    script = f.readlines()
    for line in script:
        line = line.rstrip()
        if(line[0:6] == "REPEAT"):
            for i in range(int(line[7:])):
                parseLine(filename, previousLine)
        else:
            parseLine(filename, line)
            previousLine = line

def listLang(langDir):
    global langList
    global langCount

    langList = os.listdir(langDir)
    langList.sort()
    langCount = len(langList)

def listLayer(dir):
    global layerList
    global layerCount
    
    layerList = os.listdir(dir)
    layerList.sort()
    layerCount = len(layerList)

def make_labels(path):
    global labels
    global nb_keys
    
    labels.clear()
    for i in range(nb_keys):
        labels.append(str(i))
    for filename in os.listdir(path):
        file = open(path + '/' + filename, 'r')
        line = file.readline()
        if line[0:5] == 'LABEL':
            label = line[6:].rstrip()
            labels[int(filename)] = label
        file.close()

def update_labels():
    for i, but in enumerate(buttons):
        but.label = labels[i]
        
    but_ccw.label = labels[nb_keys-1]
    but_cw.label = labels[nb_keys-2]
    
    stat_lang.label = language
    stat_mode.label = layer

def changeLayer(inc):
    global layerIndex
    global layerCount
    global layer
    global scriptsLib
    
    layerIndex = (layerIndex + inc) % layerCount
    layer = layerList[layerIndex]
    scriptsLib = '/scripts/'+layer
    
    make_labels(scriptsLib)
    update_labels()


def changeLanguage():
    global langList
    global langCount
    global langIndex
    global language
    global layout
    global Keycode
    global layerIndex
    global layer
    
    langIndex = (langIndex + 1) % langCount

    language = tabLang[0][langIndex]
    KeyboardLayout = tabLang[1][langIndex]
    Keycode = tabLang[2][langIndex]
        
    layout = KeyboardLayout(keyboard)
    listLayer('/scripts/')
    layerIndex = 0
    changeLayer(0)

def managePush():
    timePushed = time.monotonic_ns()
    elapsedTime = 0
    time.sleep(0.05)
    while not encoderPush.value and (elapsedTime < delayLongPush): # wait for button released or timeout
        elapsedTime = time.monotonic_ns() - timePushed
        time.sleep(0.01)
    if (elapsedTime > delayLongPush): # if timeout
        changeLanguage()
        while not encoderPush.value:
            time.sleep(0.01)
    else:
        changeLayer(1)   

def getDefault():
    global language
    global langIndex
    global layer
    global layerIndex
    
    listLang('/scripts')
    language = os.getenv('lang',None)
    if (language == None) or (not (language in tabLang[0])):
        language = tabLang[0][0]
    langIndex = tabLang[0].index(language)
    listLayer('/scripts/')
    layer = os.getenv('layer',None)
    if (layer == None) or (not (layer in layerList)):
        layer = layerList[0]
    layerIndex = layerList.index(layer)
    changeLayer(0)


       
enc = rotaryio.IncrementalEncoder(encoder_A, encoder_B)
cw = fakeButton(enc, fakeButton.CW, fakeButton.ACTIVE_LOW )
ccw = fakeButton(enc, fakeButton.CCW, fakeButton.ACTIVE_LOW)

encoderPush = digitalio.DigitalInOut(encoder_PUSH)
encoderPush.direction = digitalio.Direction.INPUT
encoderPush.pull = digitalio.Pull.UP

last_pressed = [0 for _ in range(nb_keys)]
pressed = []

displayio.release_displays()

spi_clk = board.GP18
spi_mosi = board.GP19
tft_cs = board.GP21
tft_dc = board.GP17
tft_res= board.GP16
tft_blk = board.GP22
blk = digitalio.DigitalInOut(tft_blk)
blk.direction = digitalio.Direction.OUTPUT
blk.value=1

spi = busio.SPI(spi_clk, spi_mosi)

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_res, baudrate=64000000)

display = ST7789(display_bus, width=280, height=240, rowstart=20, rotation=90)


root = displayio.Group()
display.root_group = root

color_bitmap = displayio.Bitmap(280, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = GRAY
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
root.append(bg_sprite)

font = bitmap_font.load_font('/fonts/orbitron_black14.pcf')
buttons = []

add_button(0, 0, '0')
add_button(0, 1, '1')
add_button(0, 2, '2')
add_button(0, 3, '3')
add_button(1, 0, '4')
add_button(1, 1, '5')
add_button(1, 2, '6')
add_button(1, 3, '7')
add_button(2, 0, '8')
add_button(2, 1, '9')
add_button(2, 2, '10')
add_button(2, 3, '11')

for b in buttons:
    root.append(b)

ystatus = 4 * BUTTON_MARGIN + 3 * BUTTON_HEIGHT

stat_lang = Button(x = BUTTON_MARGIN, y = ystatus,
                    width = BUTTON_WIDTH,
                    height = STATUS_HEIGHT, label="FR", label_font=font,
                    label_color=BLACK, fill_color=WHITE,
style=Button.ROUNDRECT)
root.append(stat_lang)

stat_mode = Button(x = 2 * BUTTON_MARGIN + BUTTON_WIDTH, y = ystatus,
                    width =  2 * BUTTON_MARGIN + 3 * BUTTON_WIDTH,
                    height = STATUS_HEIGHT, label="Editor", label_font=font,
                    label_color=BLACK, fill_color=WHITE,
style=Button.ROUNDRECT)
root.append(stat_mode)

ystatus += STATUS_HEIGHT + BUTTON_MARGIN

but_ccw = Button(x = BUTTON_MARGIN, y = ystatus,
                    width = BUTTON_MARGIN + 2 * BUTTON_WIDTH,
                    height = STATUS_HEIGHT, label="<-- prev", label_font=font,
                    label_color=BLACK, fill_color=WHITE,
style=Button.ROUNDRECT)
root.append(but_ccw)

but_cw = Button(x =  3 * BUTTON_MARGIN + 2 * BUTTON_WIDTH, y = ystatus,
                    width = BUTTON_MARGIN + 2 * BUTTON_WIDTH,
                    height = STATUS_HEIGHT, label="next -->", label_font=font,
                    label_color=BLACK, fill_color=WHITE,
style=Button.ROUNDRECT)
root.append(but_cw)

getDefault()

gc.collect()

while True:
    pressedKey = keypad.pressed_keys
    
    if not cw.value:
        pressedKey.append(coder_cw)
    if not ccw.value:
        pressedKey.append(coder_ccw)
    if not encoderPush.value:
        time.sleep(0.01)
        managePush()
        
    for ix in range(nb_keys):
        if ix in pressedKey:
            last_pressed[ix] = time_debounce if last_pressed[ix] <= 1 else last_pressed[ix]
    
    for ix, lp in enumerate(last_pressed):
        if lp == time_debounce:
            if ix not in pressed:
                pressed.append(ix)
                runScript(str(ix))

    for ix, lp in enumerate(last_pressed):
        if lp == 1 and ix in pressed:
                pressed.remove(ix)

    last_pressed = [max(0, lp - 1) for lp in last_pressed]

    time.sleep(0.01)

