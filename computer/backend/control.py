import keyboard as kb
import mouse
import math


class Command:
    name = ""

    def __init__(self, name):
        self.name = name

    def execute(self):
        pass


class Macro(Command):
    steps = []

    def __init__(self, name, steps):
        super().__init__(name)
        self.steps = steps

    def execute(self):
        for step in self.steps:
            if isinstance(step, Command):
                step.execute()
            else:
                kb.press_and_release(step)


class Left(Command):
    n = 0

    def __init__(self, n):
        super().__init__("Left")
        self.n = n

    def execute(self):
        for i in range(self.n):
            kb.press_and_release("left_arrow")


class Right(Command):
    n = 0

    def __init__(self, n):
        super().__init__("Left")
        self.n = n

    def execute(self):
        for i in range(self.n):
            kb.press_and_release("right_arrow")


class Text(Command):
    text = ""

    def __init__(self, text):
        super().__init__("Left")
        self.text = text

    def execute(self):
        kb.write(self.text)

mx = mouse.get_position()[0]
my = mouse.get_position()[1]

def move(angle, speed):
    global mx, my
    mx += math.cos(angle / 180.0 * math.pi) * speed
    my += math.sin(angle / 180.0 * math.pi) * speed
    mouse.move(mx, my, duration=0.05)


def on_press(event):
    keys = [72, 75, 77, 80]
    if event.scan_code in keys:
        print(event.scan_code)
        return True

if __name__ == "__main__":
    # move (90.0, 100)
    # cmd = Macro("test", [Left(5), Text("teext"), Right(2), Text("more")])
    kb.on_press(on_press)
    kb.wait("escape")
    #cmd.execute()
# ---------------------------------S------------------------------------
