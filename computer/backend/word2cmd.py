
def load_cmds(filename):
    cmd_dict = {}
    file = open(filename, 'r', encoding = 'utf-8')
    lines = file.readlines()
    file.close()
    for line in lines:
        line = line.strip('\n')
        line = line.split(';')
        cmd_dict[line[0]] = line[1]
    return cmd_dict

'''def find_cmd(trans, cmd_dict):
    for word in trans.split():
        if cmd_dict.get(word):
            print ('key: ' + word +'\nvalue: ' + cmd_dict[word])'''


def find_cmd(trans, cmd_dict):
    line = trans.split()
    for i in range(len(line)):
        if cmd_dict.get(line[i]):
            print('key: ' + line[i] + '\nvalue: ' + cmd_dict[line[i]])
            if i<len(line) and (cmd_dict[line[i]] == 'multi'): # if it is a a cmd that requires multiple words the first word has been designated the value multi to check for a second
                if cmd_dict.get(line[i]+line[i+1]):
                    print('cmd word' + line[i] +' ' + line[i+1] + 'cmd: ' + cmd_dict[line[i]+line[i+1]] )


def main():
    cmd_format = load_cmds ('cmds_formatting.txt')
    print (cmd_format)
    test_string = input('Enter test string:')
    find_cmd(test_string, cmd_format)

main()