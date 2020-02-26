import serial
import mouse
import time
from math import floor

ser = serial.Serial('COM5', 9600)

#active range is <1 or >4
is_holding = False
puff_threshold = 600
sip_threshold = 200
calibrate = True
dead_zone = 5
joystick_scaling_threshold = 200
mouse_movement_duration = 0.075
above_threshold = False
below_threshold = False
drag = False
while True: #need data to give me long, short, right or left. if data comes in every 150ms
    #identify the command. right or left click (left for sip, right for puff)
    payload = ser.read(5)
    size = len(payload)
    if size == 5:
        payload0 = int(payload[0])
        payload1 = int(payload[1])
        payload2 = int(payload[2])
        payload3 = int(payload[3])
        payload4 = int(payload[4])
        inputL = payload1
        inputH = payload0 & 0x3
        data = (inputH << 8) + inputL
        LR1 = payload2 & 0xF
        LR0 = payload3 & 0xFC
        LR0 = LR0 >> 2                  # DECODE
        UD1 = payload3 & 0x3
        UD0 = payload4
        LR = floor(((LR1 << 8) + LR0)/4)
        UD = (UD1 << 8) + UD0
        if calibrate: # 'first time' set up
            UDmid = UD
            LRmid = LR
            calibrate = False
        LR = LR - LRmid
        UD = UDmid - UD
        if abs(UD) > joystick_scaling_threshold or abs(LR) > joystick_scaling_threshold: # scaling decider
            scaling = 4
            UD_scaling = scaling / 2
        else:
            scaling = 10
            UD_scaling = scaling / 2
        if abs(UD) > dead_zone or abs(LR) > dead_zone:
            mouse.move(LR/scaling, UD/UD_scaling, absolute=False, duration=mouse_movement_duration)
        if data > puff_threshold and above_threshold != True:
            above_threshold = True
            start_time = time.time()
        elif data < sip_threshold and below_threshold != True:
            below_threshold = True
            start_time = time.time()
        elif data < puff_threshold and above_threshold == True:
            stop_time = time.time()
            if stop_time - start_time > 0.4:
                print("Long click")
                mouse.double_click()
            elif stop_time - start_time > 0.15:
                print("Left click")
                mouse.click()
            above_threshold = False
        elif data > sip_threshold and below_threshold == True:
            stop_time = time.time()
            if stop_time - start_time > 0.4:
                print("Long sip")
                if drag == False:
                    print("Start dragging")
                    mouse.press()
                    drag = True
                    below_threshold = False
                elif drag == True and below_threshold == True:
                    print("Stop dragging")
                    mouse.release()
                    drag = False
                    below_threshold = False
            elif stop_time - start_time > 0.2:
                print("Right click")
                mouse.right_click()
                below_threshold = False
