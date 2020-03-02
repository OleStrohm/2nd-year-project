
from threading import Lock
import keyboard as kb

class CommandController:

    def __init__(self):
        self.modes = {}

    def load_cmds(self, name, filename):
        cmd_dict = {}
        file = open(filename, 'r', encoding = 'utf-8')
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.strip('\n')
            line = line.split(' ')
            cmd_dict[line[0]] = line[1]

        self.modes[name] = cmd_dict

    def find_cmd(self, name, trans):
        # if not self.modes.get(name):
        #     return "empty", trans

        if trans == "":
            return "empty", ""

        line = trans.split()
        cmd_dict = self.modes[name]
        cmd = 'empty'
        left_string = line
        for i in range(len(line)):
            if cmd_dict.get(line[i]):
                if i<len(line) and (cmd_dict[line[i]] == 'multi'): # if it is a a cmd that requires multiple words the first word has been designated the value multi to check for a second
                    if len(line) == i+1:
                        unprocessed_string = " ".join(left_string[i:])
                        return cmd, unprocessed_string
                    elif cmd_dict.get(line[i]+line[i+1]):
                        print('cmd word' + line[i] +' ' + line[i+1] + 'cmd: ' + cmd_dict[line[i]+line[i+1]])
                        cmd = cmd_dict[line[i]+line[i+1]]
                        unprocessed_string = " ".join(left_string[i + 2:])
                        return cmd, unprocessed_string
                else:
                    print('key: ' + line[i] + '\nvalue: ' + cmd_dict[line[i]])
                    cmd = cmd_dict[line[i]]
                    unprocessed_string = " ".join(left_string[i + 1:])
                    return cmd, unprocessed_string

        return cmd, ""

# please _copy_ this, _select all_, then _paste_

# pleas eofnreinubreigbier select ->
# all and then do more stuff

if __name__ == "__main__":
    controller = CommandController()
    controller.load_cmds("test_mode", 'cmds_format.txt')
    print (controller.modes)
    test_string = input('Enter test string:')
    hotkey, unprocessed = controller.find_cmd("test_mode", test_string)
    mutex = Lock()
    mutex.acquire()
    kb.send(hotkey)
    mutex.release()
    kb.wait("esc")