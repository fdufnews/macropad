# MacroPad

## How it started from
As a left-hander, using keyboard shortcuts is usually problematic. Many of them have to use the left hand so I have to let go of the mouse, type the key combination, pick up the mouse again, or twist my fingers to type the key combination with the right hand.  
After some research on the Internet I found the [DuckyMacroPad](https://github.com/aarnas/pico-circuit-python/tree/main/Projects/DuckyMacroPad) of a simple combination of hardware and software. 

I quickly tested it and found some limitations to what I wanted. So I forked the repository and started my own version of Macropad. Added support for a matrix keyboard and some keywords to make the scripts more versatile.

## Description of what I wanted
- a macropad with between 9 and 12 keys (not too much keys as I wanted the keypad to stay atop my keyboard)
- progammed in Python
- no daemon on the computer
- support of different keymaps (I have a desktop with a french keyboard and a laptop with a US keyboard).
- programmable macros with support for some software and easy modification of them without a specific tool.

## What I ended with
 A macropad with:
 
- Raspberry Pi Pico, running CircuitPython (as CircuitPython supports USB HID and make the Pico be viewed as an externel disk)
- 12 buttons, 9 seems a bit limited
- 1 rotary encoder, this adds some pleasant tricks like undo/redo at the turn of a button
- a 280 x 240 TFT color display, to show key affectation

## Pin allocation on the Raspberry Pi Pico
```
|        |       |    |     ┏━━━━━┓     |    |          |          |
|        |       |    |┏━━━━┫     ┣━━━━┓|    |          |          |
|        | GP0   | 1  |┃◎   ┗━━━━━┛   ◎┃| 40 |VBUS      |          |
|        | GP1   | 2  |┃◎ ▩           ◎┃| 39 |VSYS      |          |
|        | Ground| 3  |┃▣ └─GP25      ▣┃| 38 |Ground    |          |
| L1     | GP2   | 4  |┃◎  ▒▒▒        ◎┃| 37 |3v3 En    |          |
| L2     | GP3   | 5  |┃◎  ▒▒▒        ◎┃| 36 |3v3 Out   |          |
| L3     | GP4   | 6  |┃◎             ◎┃| 35 |ADC VRef  |          |
| R1     | GP5   | 7  |┃◎             ◎┃| 34 |GP28 / A2 |          |
|        | Ground| 8  |┃▣             ▣┃| 33 |ADC Ground|          |
|        | GP6   | 9  |┃◎   ▓▓▓▓▓▓▓   ◎┃| 32 |GP27 / A1 |          |
| ROT1A  | GP7   | 10 |┃◎   ▓▓▓▓▓▓▓   ◎┃| 31 |GP26 / A0 |          |
| ROT1B  | GP8   | 11 |┃◎   ▓▓▓▓▓▓▓   ◎┃| 30 |run       |          |
| ROT1S  | GP9   | 12 |┃◎   ▓▓▓▓▓▓▓   ◎┃| 29 |GP22      | TFT_BLK  |
|        | Ground| 13 |┃▣             ▣┃| 28 |Ground    |          |
| C1     | GP10  | 14 |┃◎             ◎┃| 27 |GP21      | TFT_CS   |
| C2     | GP11  | 15 |┃◎             ◎┃| 26 |GP20      | TFT_MISO |
| C3     | GP12  | 16 |┃◎             ◎┃| 25 |GP19      | NU       |
| C4     | GP13  | 17 |┃◎             ◎┃| 24 |GP18      | TFT_SCK  |
|        | Ground| 18 |┃▣             ▣┃| 23 |Ground    |          |
| R2     | GP14  | 19 |┃◎             ◎┃| 22 |GP17      | TFT_CD   |
| R3     | GP15  | 20 |┃◎    ◎ ▣ ◎    ◎┃| 21 |GP16      | TFT_RS   |
|        |       |    |┗━━━━━━━━━━━━━━━┛|    |          |          |
```
R1-3 are reserved for future use. They are parts of the 2 connectors that are connecting the keyboard to the main board

The full [schematic is here](hardware/MacroPad.pdf)

## View of the Macropad
![](doc/IMG_20240226_132405_small.jpg)

## How it works
The Macropad embeds its own documentation.
If plugged with the rotary encoder pushed, the Macropad also shows itself as an external thumb drive where a readme.md with the documentation can be found.
It is [here too](software/pico_fs/readme.md)

## Software
The full source code with comments is [here](software/code_full.py)
The [pico_fs](pico_fs) directory contains all the necessary files to make a functionnal Macropad: a stripped code, the drivers, the fonts, some scripts.  
Once the Pico is programmed with CircuitPython, all files in pico_fs shall be copyed on the CIRCUITPY drive.

## Todo list
### Easy
[x] Add management of key colors in the settings.toml file  
[x] add a keyword for the script to switch the layer. Example, selecting Gedit in the *applications* layer launches Gedit and switches to *Edition* layer  
### Difficult
[] Look if it is possible to use either of icons or text in the keys without exploding memory and making software slower (Difficult as it can be very memory hungry).  
[] Search a way to place multi lines of text in the keys. It is very boring to be limited to 5 or 6 caracters (difficult as it all depends on the buttons library).  
