import serial
import sys
import serial.tools.list_ports
import mouse
import time
from math import floor

# serial set up

port = ""
ports = serial.tools.list_ports.comports()
for p in ports:
    if 'Arduino' in p[1]:
        port = p[0]

if port == "":
    sys.exit("Error: Arduino not found!")

ser = serial.Serial(port, 9600)

# control parameters

puff_threshold = 600
sip_threshold = 200
short_puff_time = 0.15
long_puff_time = 0.4
short_sip_time = 0.2
long_sip_time = 0.4
above_threshold = False
below_threshold = False
drag = False
is_holding = False

mouse_calibrate = False
mouse_dead_zone = 5
mouse_scaling_threshold = 200
mouse_lower_scaling = 10
mouse_higher_scaling = 4
mouse_movement_duration = 0.075

# data loop

while True:
    payload = ser.read(5) # reading 5 bytes of data
    size = len(payload)
    if size == 5: # check if 5 bytes actually received
        payload0 = int(payload[0])
        payload1 = int(payload[1])
        payload2 = int(payload[2])
        payload3 = int(payload[3])
        payload4 = int(payload[4])
        snp_L = payload1 # low byte of pressure
        snp_H = payload0 & 0x3 # high byte of pressure
        snp_data = (snp_H << 8) + snp_L # sip-and-puff data
        LR1 = payload2 & 0xF # high byte of Left-Right data
        LR0 = payload3 & 0xFC # low byte of Left-Right data
        LR0 = LR0 >> 2
        UD1 = payload3 & 0x3 # high byte of Up-Down data
        UD0 = payload4 # low byte of Up-Down data
        LR = floor(((LR1 << 8) + LR0)/4) # Left-Right joystick data
        UD = (UD1 << 8) + UD0 # Up-Down joystick data
        UD_mid = UD
        LR_mid = LR

        # joystick

        if mouse_calibrate: # mouse midpoint calibration
            UD_mid = UD
            LR_mid = LR
            mouse_calibrate = False
        LR = LR - LR_mid
        UD = UD_mid - UD
        if abs(UD) > mouse_scaling_threshold or abs(LR) > mouse_scaling_threshold: # scaling decider
            scaling = mouse_higher_scaling
        else:
            scaling = mouse_lower_scaling
        UD_scaling = scaling / 2
        if abs(UD) > mouse_dead_zone or abs(LR) > mouse_dead_zone:
            mouse.move(LR/scaling, UD/UD_scaling, absolute=False, duration=mouse_movement_duration)

        # snp

        if snp_data > puff_threshold and not above_threshold:
            above_threshold = True
            start_time = time.time()
        elif snp_data < sip_threshold and not below_threshold:
            below_threshold = True
            start_time = time.time()
        elif snp_data < puff_threshold and above_threshold:
            stop_time = time.time()
            elapsed = stop_time - start_time
            if elapsed > long_puff_time:
                print("Double click")
                mouse.double_click()
            elif elapsed > short_puff_time:
                print("Left click")
                mouse.click()
            above_threshold = False
        elif snp_data > sip_threshold and below_threshold:
            stop_time = time.time()
            elapsed = stop_time - start_time
            if elapsed > long_sip_time:
                if not drag:
                    print("Start dragging")
                    mouse.press()
                    drag = True
                    below_threshold = False
                elif drag and below_threshold:
                    print("Stop dragging")
                    mouse.release()
                    drag = False
                    below_threshold = False
            elif elapsed > short_sip_time:
                print("Right click")
                mouse.right_click()
                below_threshold = False
