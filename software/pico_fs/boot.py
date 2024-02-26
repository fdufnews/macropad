from board import *
import digitalio
import storage
import time
import board

noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(board.GP9)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = not noStoragePin.value
time.sleep(1)

if(noStorageStatus == False):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")

