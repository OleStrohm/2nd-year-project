import serial
import serial.tools.list_ports
import mouse
import keyboard
from threading import Thread, Lock
from math import floor
from time import time, time_ns, sleep



class ArduinoController:
    def __init__(self):
        # serial set up¬
        port = ""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if 'Arduino' in p[1]:
                port = p[0]

        if port != "":
            self.ser = serial.Serial(port, 19200)
        else:
            self.ser = None

        self.functions = {
            "left": self.handle_click,
            "middle": self.handle_middle_click,
            "right": self.handle_right_click,
            "double": self.handle_double_click,
            "drag": self.handle_drag,
            "enter": self.handle_enter,
            "prev mode": self.handle_change_mode,
            "nothing": self.handle_nothing
        }

        self.callbacks = {
            "short_sip": "left",
            "double_sip": "left",
            "long_sip": "left",
            "short_puff": "left",
            "double_puff": "left",
            "long_puff": "left"
        }

        self.puff_threshold = 600
        self.short_puff_time = 0.15
        self.long_puff_time = 0.4
        self.double_puff_time = 0.4
        self.sip_threshold = 300
        self.short_sip_time = 0.2
        self.long_sip_time = 0.4
        self.double_sip_time = 0.5
        self.start_snp_data = 0

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
        self.mouse_higher_scaling = 2
        self.mouse_movement_duration = 0.06

        self.gui_callback = None
        self.gui_change_mode = None

        self.running = False

        self.mouse_controller = MouseController()

    # data loop

    def start(self):
        if self.ser is None:
            return
        self.mouse_controller.start()
        self.running = True
        print("started arduino")
        t = Thread(target=self.data_loop, args=(self,))
        t.start()

    def data_loop(self, _):
        start_time = 0
        print("began")
        while self.running:
            payload = self.ser.read(5)  # reading 5 bytes of data
            size = len(payload)

            if size == 5:  # check if 5 bytes actually received
                payload0 = int(payload[0])
                payload1 = int(payload[1])
                payload2 = int(payload[2])
                payload3 = int(payload[3])
                payload4 = int(payload[4])
                snp_L = payload1  # low byte of pressure
                snp_H = payload0 & 0x3  # high byte of pressure
                snp_data = (snp_H << 8) + snp_L  # sip-and-puff data
                LR1 = payload2 & 0xF  # high byte of Left-Right data
                LR0 = payload3 & 0xFC  # low byte of Left-Right data
                LR0 = LR0 >> 2
                UD1 = payload3 & 0x3  # high byte of Up-Down data
                UD0 = payload4  # low byte of Up-Down data
                LR = floor(((LR1 << 8) + LR0) / 4)  # Left-Right joystick data
                UD = (UD1 << 8) + UD0  # Up-Down joystick data

                # joystick

                if self.mouse_calibrate:  # mouse midpoint calibration
                    UD_mid = UD
                    LR_mid = LR
                    self.start_snp_data = snp_data
                    self.mouse_calibrate = False
                LR = LR_mid - LR
                UD = UD - UD_mid
                if abs(UD) > self.mouse_scaling_threshold or abs(LR) > self.mouse_scaling_threshold:  # scaling decider
                    scaling = self.mouse_higher_scaling
                else:
                    scaling = self.mouse_lower_scaling
                UD_scaling = scaling * 3
                if abs(UD) > self.mouse_dead_zone or abs(LR) > self.mouse_dead_zone:
                    self.mouse_controller.set_direction(LR * scaling, UD * UD_scaling)
                else:
                    self.mouse_controller.set_direction(0, 0)

                # snp

                if self.puff:
                    if snp_data > self.puff_threshold and not self.above_threshold:
                        self.above_threshold = True
                        start_time = time()
                        elapsed1 = time() - stop_time
                        if elapsed1 < self.double_puff_time:
                            print("double puff")
                            self.handle_callback("double_puff")
                            self.double = True
                    elif self.double:
                        self.double = False
                    else:
                        print("single puff")
                        self.handle_callback("short_puff")
                    self.puff = False
                elif self.sip:
                    if snp_data < self.sip_threshold and not self.below_threshold:
                        self.below_threshold = True
                        start_time = time()
                        elapsed1 = time() - start_time
                        if elapsed1 < self.double_sip_time:
                            print("double sip")
                            self.handle_callback("double_sip")
                            self.double = True
                    elif self.double:
                        self.double = False
                    else:
                        print("single sip")
                        self.handle_callback("short_sip")
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
                        self.handle_callback("long_puff")
                    elif elapsed > self.short_puff_time:
                        self.puff = True
                    self.above_threshold = False
                elif snp_data > self.sip_threshold and self.below_threshold:
                    stop_time = time()
                    elapsed = stop_time - start_time
                    if elapsed > self.long_sip_time:
                        print("Long sip")
                        self.handle_callback("long_sip")
                    elif elapsed > self.short_sip_time:
                        self.sip = True
                    self.below_threshold = False
        print("stopped arduino")

    def stop(self):
        self.mouse_controller.stop()
        self.running = False

    def handle_change_mode(self):
        self.gui_change_mode()

    def set_gui_change_mode(self, callback):
        self.gui_change_mode = callback

    def set_callback(self, command, function):
        self.callbacks[command] = function

    def handle_callback(self, command):
        self.functions[self.callbacks[command]]()
        command = command.replace('_', ' ')
        command = command.title()
        self.gui_callback(command)

    def handle_nothing(self):
        pass

    def handle_drag(self):
        self.drag = not self.drag
        if self.drag:
            print("drag activate")
            mouse.press()
        else:
            print("drag deactivate")
            mouse.release()

    def handle_click(self):
        mouse.click()
        self.drag = False

    def handle_double_click(self):
        if not self.drag:
            mouse.double_click()

    def handle_right_click(self):
        if not self.drag:
            mouse.right_click()

    def handle_middle_click(self):
        if not self.drag:
            mouse.click("middle")

    def handle_enter(self):
        if not self.drag:
            keyboard.press_and_release("enter")

    def set_bounds(self, w, h):
        self.mouse_controller.set_bounds(w, h)

    def set_puff_threshold(self, puff_threshold):
        self.puff_threshold = self.start_snp_data + puff_threshold

    def set_sip_threshold(self, sip_threshold):
        self.sip_threshold = self.start_snp_data - sip_threshold

    def set_short_puff_time(self, short_puff_time):
        self.short_puff_time = short_puff_time

    def set_long_puff_time(self, long_puff_time):
        self.long_puff_time = long_puff_time

    def set_short_sip_time(self, short_sip_time):
        self.short_sip_time = short_sip_time

    def set_long_sip_time(self, long_sip_time):
        self.long_sip_time = long_sip_time

    def set_mouse_dead_zone(self, mouse_dead_zone):
        self.mouse_dead_zone = int(mouse_dead_zone)
        print(self.mouse_dead_zone)

    def set_mouse_scaling_threshold(self, mouse_scaling_threshold):
        self.mouse_scaling_threshold = int(mouse_scaling_threshold)

    def set_mouse_speed(self, mouse_speed):
        self.mouse_lower_scaling = mouse_speed
        self.mouse_higher_scaling = mouse_speed/2

    def set_gui_callback(self, callback):
        self.gui_callback = callback


class MouseController:

    def __init__(self):
        self.x = mouse.get_position()[0]
        self.y = mouse.get_position()[1]
        self.dx = 0
        self.dy = 0
        self.width = self.x
        self.height = self.y
        self.running = True
        self.delay = 0.01

    def set_bounds(self, w, h):
        self.width = w
        self.height = h

    def start(self):
        t = Thread(target=self.loop, args=(self,))
        t.start()

    def stop(self):
        self.running = False

    def set_direction(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def loop(self, _):
        last_time = time_ns()
        while self.running:
            sleep(0.001)
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
        print("stopped mouse controller")


if __name__ == "__main__":
    a = ArduinoController()
    a.mouse_calibrate = True
    a.data_loop("")
