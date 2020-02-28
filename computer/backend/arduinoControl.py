import serial
import sys
import serial.tools.list_ports
import mouse
import time
from threading import Thread
from math import floor
import keyboard as kb

class ArduinoController:

    def __init__(self):
# serial set up
        port = ""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if 'Arduino' in p[1]:
                port = p[0]

        if port == "":
            sys.exit("Error: Arduino not found!")

        self.ser = serial.Serial(port, 19200)

# variables set up
        self.puff_threshold = 600
        self.sip_threshold = 300
        self.short_puff_time = 0.15
        self.long_puff_time = 0.4
        self.short_sip_time = 0.2
        self.long_sip_time = 0.4
        self.above_threshold = False
        self.below_threshold = False
        self.drag = False
        self.is_holding = False

        self.mouse_calibrate = True
        self.mouse_dead_zone = 5
        self.mouse_scaling_threshold = 300
        self.mouse_lower_scaling = 10
        self.mouse_higher_scaling = 4
        self.mouse_movement_duration = 0.06

# data loop

    def start(self):
        t = Thread(target=self.data_loop, args=(self,))
        t.start()

    def data_loop(self, _):
        start_time = 0
        print("began")
        while True:
            payload = self.ser.read(5)  # reading 5 bytes of data
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

                # joystick

                if self.mouse_calibrate: # mouse midpoint calibration
                    UD_mid = UD
                    LR_mid = LR
                    self.mouse_calibrate = False
                LR = LR_mid - LR
                UD = UD - UD_mid
                if abs(UD) > self.mouse_scaling_threshold or abs(LR) > self.mouse_scaling_threshold:  # scaling decider
                    scaling = self.mouse_higher_scaling
                else:
                    scaling = self.mouse_lower_scaling
                UD_scaling = scaling / 2
                if abs(UD) > self.mouse_dead_zone or abs(LR) > self.mouse_dead_zone:
                    mouse.move(LR/scaling, UD/UD_scaling, absolute=False, duration=self.mouse_movement_duration)

                # snp

                if snp_data > self.puff_threshold and not self.above_threshold:
                    self.above_threshold = True
                    start_time = time.time()
                elif snp_data < self.sip_threshold and not self.below_threshold:
                    self.below_threshold = True
                    start_time = time.time()
                elif snp_data < self.puff_threshold and self.above_threshold:
                    stop_time = time.time()
                    elapsed = stop_time - start_time
                    if elapsed > self.long_puff_time:
                        print("Double click")
                        mouse.double_click()
                    elif elapsed > self.short_puff_time:
                        print("Left click")
                        mouse.click()
                    self.above_threshold = False
                elif snp_data > self.sip_threshold and self.below_threshold:
                    stop_time = time.time()
                    elapsed = stop_time - start_time
                    if elapsed > self.long_sip_time:
                        if not self.drag:
                            print("Start dragging")
                            mouse.press()
                            self.drag = True
                            self.below_threshold = False
                        elif self.drag and self.below_threshold:
                            print("Stop dragging")
                            mouse.release()
                            self.drag = False
                            self.below_threshold = False
                    elif elapsed > self.short_sip_time:
                        print("Right click")
                        mouse.right_click()
                        self.below_threshold = False

if __name__ == "__main__":
    a = ArduinoController()
    a.mouse_calibrate = True
    a.data_loop("")
    kb.wait("esc")