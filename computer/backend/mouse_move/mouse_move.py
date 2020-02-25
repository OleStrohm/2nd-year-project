from math import floor
import mouse
import serial

# control parameters
calibrate = True
dead_zone = 5
scaling_threshold = 200
mouse_movement_duration = 0.075

# serial connection
ser = serial.Serial('COM5', 9600)
while True:
    payload = ser.read(3)  # detect 3 bytes of data
    size = len(payload)
    if size == 3: # if all 3 bytes are there
        payload0 = int(payload[0])
        payload1 = int(payload[1])
        payload2 = int(payload[2])
        LR1 = payload0 & 0xF
        LR0 = payload1 & 0xFC
        LR0 = LR0 >> 2                  # DECODE
        UD1 = payload1 & 0x3
        UD0 = payload2
        LR = floor(((LR1 << 8) + LR0)/4)
        UD = (UD1 << 8) + UD0
        if calibrate: # 'first time' set up
            UDmid = UD
            LRmid = LR
            calibrate = False
        LR = LR - LRmid
        UD = UDmid - UD
        if abs(UD) > scaling_threshold or abs(LR) > scaling_threshold: # scaling decider
            scaling = 4
            UD_scaling = scaling / 2
        else:
            scaling = 10
            UD_scaling = scaling / 2
        if abs(UD) > dead_zone or abs(LR) > dead_zone:
            mouse.move(LR/scaling, UD/UD_scaling, absolute=False, duration=mouse_movement_duration)