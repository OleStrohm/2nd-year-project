import keyboard as kb
import mouse


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


def move(angle, speed):
    for i in range(10):
        mouse.move(1, 1, absolute=False, duration=(1 / speed))


if __name__ == "__main__":
    cmd = Macro("test", [Left(5), Text("teext")])
    cmd.execute()
# ---------------------------------S------------------------------------
