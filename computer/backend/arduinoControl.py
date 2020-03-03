import serial
import serial.tools.list_ports
import mouse
from threading import Thread, Lock
from math import floor
from time import time, time_ns

class ArduinoController:

    def __init__(self):
# serial set up
        port = ""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if 'Arduino' in p[1]:
                port = p[0]

        if port != "":
            self.ser = serial.Serial(port, 19200)
        else:
            self.ser = None

# settings
        self.puff_threshold = 600
        self.sip_threshold = 300
        self.short_puff_time = 0.15
        self.long_puff_time = 0.4
        self.short_sip_time = 0.2
        self.long_sip_time = 0.4

# variables
        self.above_threshold = False
        self.below_threshold = False
        self.drag = False
        self.sip = False
        self.puff = False
        self.double = False

        self.mouse_calibrate = True

# settings
        self.mouse_dead_zone = 5
        self.mouse_scaling_threshold = 300
        self.mouse_lower_scaling = 1
        self.mouse_higher_scaling = 0.5
        self.mouse_movement_duration = 0.06


        self.mutex = Lock()
        self.mouse_controller = MouseController()

# data loop

    def start(self):
        if self.ser is None:
            return
        self.mouse_controller.start()
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
                    self.mouse_controller.set_direction(LR/scaling, UD/UD_scaling)
                else:
                    self.mouse_controller.set_direction(0, 0)

                # snp
                if self.puff:
                    if snp_data > self.puff_threshold and not self.above_threshold:
                        self.above_threshold = True
                        start_time = time()
                        elapsed1 = time() - stop_time
                        if elapsed1 < 0.4:
                            print("double puff")
                            self.double = True
                    elif self.double:
                        self.double = False
                    else:
                        print("single puff")
                    self.puff = False
                elif self.sip:
                    if snp_data < self.sip_threshold and not self.below_threshold:
                        self.below_threshold = True
                        start_time = time()
                        elapsed1 = time() - start_time
                        if elapsed1 < 0.5:
                            print("double sip")
                            self.double = True
                    elif self.double:
                        self.double = False
                    else:
                        print("single sip")
                    self.sip = False
                elif snp_data > self.puff_threshold and not self.above_threshold:
                    self.above_threshold = True
                    start_time = time()
                elif snp_data < self.sip_threshold and not self.below_threshold:
                    self.below_threshold = True
                    start_time = time()
                elif snp_data < self.puff_threshold and self.above_threshold:
                    stop_time = time()
                    elapsed = stop_time - start_time
                    if elapsed > self.long_puff_time:
                        print("Long puff")
                    elif elapsed > self.short_puff_time:
                        self.puff = True
                    self.above_threshold = False
                elif snp_data > self.sip_threshold and self.below_threshold:
                    stop_time = time()
                    elapsed = stop_time - start_time
                    if elapsed > self.long_sip_time:
                        if not self.drag:
                            print("Long sip activate")
                            self.drag = True
                            self.below_threshold = False
                        elif self.drag and self.below_threshold:
                            print("Long sip deactivate")
                            self.drag = False
                            self.below_threshold = False
                    elif elapsed > self.short_sip_time:
                        self.sip = True
                        self.below_threshold = False

    def set_bounds(self, w, h):
        self.mutex.acquire()
        try:
            self.mouse_controller.set_bounds(w, h)
        finally:
            self.mutex.release()

class MouseController:

    def __init__(self):
        self.x = mouse.get_position()[0]
        self.y = mouse.get_position()[1]
        self.dx = 0
        self.dy = 0
        self.width = self.x
        self.height = self.y
        self.running = True
        self.mutex = Lock()
        self.delay = 0.01

    def set_bounds(self, w, h):
        self.width = w
        self.height = h

    def start(self):
        t = Thread(target=self.loop, args=(self,))
        t.start()

    def set_direction(self, dx, dy):
        self.mutex.acquire()
        try:
            self.dx = dx
            self.dy = dy
        finally:
            self.mutex.release()

    def loop(self, _):
        last_time = time_ns()
        while self.running:
            cur_time = time_ns()
            dt = (cur_time - last_time) / 1000000000
            if dt > self.delay:
                last_time = cur_time
                if self.dx != 0 or self.dy != 0:
                    self.x = self.x + self.dx * dt
                    self.y = self.y + self.dy * dt
                    if self.x < 0:
                        self.x = 0
                    if self.x >= self.width:
                        self.x = self.width
                    if self.y < 0:
                        self.y = 0
                    if self.y > self.height:
                        self.y = self.height
                    mouse.move(self.x, self.y)


if __name__ == "__main__":
    a = ArduinoController()
    a.mouse_calibrate = True
    a.data_loop("")