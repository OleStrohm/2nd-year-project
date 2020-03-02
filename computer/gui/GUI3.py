import tkinter as tk
import tkinter.messagebox

from threading import Thread


class GUI:
    """ sets up the main window and all the graphics """

    def __init__(self, modes, settings, mode_file, arduino):
        self.modes = modes
        self.settings = settings
        self.arduino = arduino

        self.root = None
        self.width = None
        self.height = None
        self.changes = False
        self.transcription = modes[list(self.modes.keys())[0]].trans
        self.current_mode = list(self.modes.keys())[0]
        self.t = Thread(target=self.main_loop, args=(self,))
        self.t.start()

    def main_loop(self, _):
        # set up root window
        self.root = tk.Tk()
        self.root.title('App Name Menu')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.arduino.set_bounds(self.width, self.height)
        self.root.geometry('%dx%d+%d+%d' % (
            self.width, 0.1 * self.height, 0,
            self.height - 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
        self.root.attributes('-topmost', True)

        # frame
        # self.panel_frame = Frame(self.root, )
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=24)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        # Buttons
        # Menu buttons
        self.btn_exit = tk.Button(self.root, text='Exit')
        self.btn_exit['command'] = lambda: self.close_program()  # note: when we turn this to an app change to root.quit
        self.btn_exit.grid(row=0, column=0, sticky='nsew')

        self.btn_move = tk.Button(self.root, text='Minimize')
        self.btn_move['command'] = lambda: self.move()
        self.btn_move.grid(row=0, column=3, sticky='nsew')

        self.btn_hide = tk.Button(self.root, text='Hide')
        self.btn_hide['command'] = lambda: self.hide()
        self.btn_hide.grid(row=0, column=4, sticky='nsew')

        self.btn_settings = tk.Button(self.root, text='Settings')
        self.btn_settings['command'] = lambda: self.settings_start()
        self.btn_settings.grid(row=0, column=5, sticky='nsew')
        # Transcription setup as a label
        self.l_transcription = tk.Label(self.root, text='Transcript runs here', bg='black', fg='white', anchor='nw',
                                        height=2)
        # self.transcription.config(wraplength = ) potentially needs to be set to ensure
        self.l_transcription.grid(row=0, column=2, sticky='nsew')

        # mode menu
        self.m_current_mode = tk.StringVar()
        self.m_current_mode.set(self.current_mode)
        self.m_mode = tk.OptionMenu(self.root, self.m_current_mode, *list(self.modes.keys()), command=self.change_mode)
        self.m_mode.grid(row=0, column=1, sticky='nsew')

        self.root.protocol('WM_DELETE_WINDOW', self.close_program)

        self.root.mainloop()

    def close_program(self):
        print('Program should do complete exit')
        mode_dict_update()
        self.root.destroy()

    def settings_start(self):
        self.main_menu = tk.Toplevel(bg='white')
        self.main_menu.title('Settings')
        self.main_menu.geometry(
            '%dx%d+%d+%d' % (0.6 * self.width, 0.4 * self.height, 0.2 * self.width, 0.1 * self.height))

        # self.main_menu.grid(row=0, column=0, sticky = 'news')
        self.main_menu.grid_rowconfigure(0, weight=1)
        self.main_menu.grid_columnconfigure(0, weight=1)
        self.main_menu.grid_rowconfigure(1, weight=2)
        self.main_menu.grid_columnconfigure(1, weight=2)
        self.main_menu.grid_rowconfigure(2, weight=2)
        self.main_menu.grid_columnconfigure(2, weight=2)
        self.main_menu.grid_rowconfigure(3, weight=1)
        self.main_menu.grid_columnconfigure(3, weight=1)

        btn_js = tk.Button(self.main_menu, text='Joy Stick', command=lambda: self.settings_joy())
        btn_js.grid(row=1, column=1, sticky='news')

        btn_snp = tk.Button(self.main_menu, text='Sip & Puff', command=lambda: self.settings_sip())
        btn_snp.grid(row=1, column=2, sticky='news')

        btn_stt = tk.Button(self.main_menu, text='Speach to Text', command=lambda: self.settings_speech2text())
        btn_stt.grid(row=2, column=1, sticky='news')

        btn_def = tk.Button(self.main_menu, text='Window Options', command=lambda: self.settings_gui())
        btn_def.grid(row=2, column=2, sticky='news')

        btn_factory = tk.Button(self.main_menu, text='Factory Settings', command=lambda: self.factory_settings())
        btn_factory.grid(row=3, column=4, columnspan=1, sticky='es')

        btn_save_default = tk.Button(self.main_menu, text='Save updated settings to Default',
                                     command=lambda: self.save('SettingsGUI.txt', self.settings))
        btn_save_default.grid(row=3, column=1, columnspan=2, sticky='ns')

        btn_close = tk.Button(self.main_menu, text='Close settings', command=lambda: self.close_settings())
        btn_close.grid(row=4, column=1, columnspan=2, sticky='s')

        self.main_menu.protocol('WM_DELETE_WINDOW', self.close_settings)

    def close_settings(self):
        if (self.changes):
            default_msg = tk.messagebox.askokcancel(title='Update settings',
                                                    message='Do you wish to make the settings changes to your default settings?')
            if default_msg:
                self.save('SettingsGUI.txt', self.settings)
        self.main_menu.destroy()

    def save(self, filename, dict):
        save_changed_settings(filename, dict)
        self.changes = False;

    def settings_joy(self):
        joy_page = tk.Toplevel(self.main_menu)
        joy_page.title('Settings Joystick')
        # set the speed of the cursor
        l_speed = tk.Label(master=joy_page, text='Cursor speed')
        l_speed.grid(row=0, column=0, columnspan=2, sticky='news')
        l_smin = tk.Label(master=joy_page, text='Min Range 0').grid(row=1, column=0, sticky='nes')
        l_smax = tk.Label(master=joy_page, text='100 Max Range').grid(row=1, column=2, sticky='nws')
        slider_speed = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal')
        slider_speed.set(self.settings['Cursor_speed'])  # update with settings value
        slider_speed.grid(row=1, column=1, columnspan=1, sticky='news')
        slider_speed.bind("<ButtonRelease>", lambda event: self.settings_update(slider_speed.get(), 'Cursor_speed'))

        # Set Up Range Sensetivity
        l_X = tk.Label(master=joy_page, text='X Range')
        l_X.grid(row=2, column=0, columnspan=3, sticky='ews')
        l_Xmin = tk.Label(master=joy_page, text='Min Range 0').grid(row=3, column=0, sticky='nes')
        l_Xmix = tk.Label(master=joy_page, text='100 Max Range').grid(row=3, column=2, sticky='nws')
        slider_X = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal', )
        slider_X.set(self.settings['X_range'])  # update with settings value
        slider_X.grid(row=3, column=1, sticky='news')
        slider_X.bind("<ButtonRelease>", lambda event: self.settings_update(slider_X.get(), 'X_range'))

        # Set Up Range Sensetivity
        l_Y = tk.Label(master=joy_page, text='Y Range')
        l_Y.grid(row=4, column=0, columnspan=3, sticky='ews')
        l_Ymin = tk.Label(master=joy_page, text='Min Range 0').grid(row=5, column=0, sticky='nes')
        l_Ymix = tk.Label(master=joy_page, text='100 Max Range').grid(row=5, column=2, sticky='nws')
        slider_Y = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal', )
        slider_Y.set(self.settings['Y_range'])  # update with settings value
        slider_Y.grid(row=5, column=1, sticky='news')
        slider_Y.bind("<ButtonRelease>", lambda event: self.settings_update(slider_Y.get(), 'Y_range'))

        # set size of dead zone
        l_speed = tk.Label(master=joy_page, text='Dead zone size')
        l_speed.grid(row=6, column=0, columnspan=2, sticky='news')
        l_smin = tk.Label(master=joy_page, text='Min size 0').grid(row=7, column=0, sticky='nes')
        l_smax = tk.Label(master=joy_page, text='100 Max size').grid(row=7, column=2, sticky='nws')
        slider_speed = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal')
        slider_speed.set(self.settings['dead_zone'])  # update with settings value
        slider_speed.grid(row=7, column=1, columnspan=1, sticky='news')
        slider_speed.bind("<ButtonRelease>", lambda event: self.settings_update(slider_speed.get(), 'dead_zone'))

        # Close Button
        btn_close_js = tk.Button(master=joy_page, text='Close Joystick Settings', command=lambda: joy_page.destroy())
        btn_close_js.grid(row=8, column=1, sticky='news')

    def settings_sip(self):
        page = tk.Toplevel(self.main_menu)
        page.title('Settings Sip & Puff')
        # set up pressure sensetivity
        l_pressure = tk.Label(master=page, text='Pressure Threshold')
        l_pressure.grid(row=0, column=0, columnspan=3, sticky='news')
        l_pmin = tk.Label(master=page, text='Min Range 0').grid(row=1, column=0, sticky='nes')
        l_pmax = tk.Label(master=page, text='100 Max Range').grid(row=1, column=3, sticky='nws')
        slider_pressure = tk.Scale(master=page, from_=0, to=100, orient='horizontal')
        slider_pressure.set(self.settings['Min_sens'])  # update with settings value
        slider_pressure.grid(row=1, column=1, columnspan=2, sticky='news')
        slider_pressure.bind("<ButtonRelease>",
                             lambda event: self.settings_update(slider_pressure.get(), 'Min_sens'))

        # Set left click
        l_left = tk.Label(master=page, text='Left click functionality', wraplength=50)
        l_left.grid(row=2, column=0, columnspan=1, sticky='ews')
        current_type_pre = tk.StringVar()
        current_type_pre.set(self.settings['leftC_pre'])
        l_left_menu_pre = tk.OptionMenu(page, current_type_pre, *self.settings['pressure_type'],
                                        command=lambda select: self.settings_update(select, 'pressure_type'))
        l_left_menu_pre.grid(row=2, column=1, columnspan=1, sticky='ew')
        current_type_time = tk.StringVar()
        current_type_time.set(self.settings['leftC_len'])
        l_left_menu_time = tk.OptionMenu(page, current_type_time, *self.settings['length'],
                                         command=lambda select: self.settings_update(select, 'length'))
        l_left_menu_time.grid(row=2, column=2, columnspan=1, sticky='ew')

        # Set up right click
        l_left = tk.Label(master=page, text='Right click functionality', wraplength=50)
        l_left.grid(row=3, column=0, columnspan=1, sticky='ews')
        current_type_r_pre = tk.StringVar()
        current_type_r_pre.set(self.settings['rightC_pre'])
        l_left_menu_r_pre = tk.OptionMenu(page, current_type_r_pre, *self.settings['pressure_type'],
                                          command=lambda select: self.settings_update(select, 'rightC_pre'))
        l_left_menu_r_pre.grid(row=3, column=1, columnspan=1, sticky='ew')

        current_type_r_time = tk.StringVar()
        current_type_r_time.set(self.settings['rightC_len'])
        l_left_menu_r_time = tk.OptionMenu(page, current_type_r_time, *self.settings['length'],
                                           command=lambda select: self.settings_update(select, 'rightC_len'))
        l_left_menu_r_time.grid(row=3, column=2, columnspan=1, sticky='ew')
        # Length of long
        l_long_time = tk.Label(master=page, text='Length of Long pressure')
        l_long_time.grid(row=4, column=0, columnspan=4, sticky='news')
        l_tl_min = tk.Label(master=page, text='Min Range 0').grid(row=5, column=0, sticky='nes')
        l_tl_max = tk.Label(master=page, text='100 Max Range').grid(row=5, column=3, sticky='nws')
        slider_long_time = tk.Scale(master=page, from_=0, to=100, orient='horizontal')
        slider_long_time.set(self.settings['length_long'])  # update with settings value
        slider_long_time.grid(row=5, column=1, columnspan=2, sticky='news')
        slider_long_time.bind("<ButtonRelease>",
                              lambda event: self.settings_update(slider_pressure.get(), 'length_long'))

        # Length of short
        l_long_time = tk.Label(master=page, text='Length of Short pressure')
        l_long_time.grid(row=6, column=0, columnspan=4, sticky='news')
        l_tl_min = tk.Label(master=page, text='Min Range 0').grid(row=7, column=0, sticky='nes')
        l_tl_max = tk.Label(master=page, text='100 Max Range').grid(row=7, column=3, sticky='nws')
        slider_long_time = tk.Scale(master=page, from_=0, to=100, orient='horizontal')
        slider_long_time.set(self.settings['length_short'])  # update with settings value
        slider_long_time.grid(row=7, column=1, columnspan=2, sticky='news')
        slider_long_time.bind("<ButtonRelease>",
                              lambda event: self.settings_update(slider_pressure.get(), 'length_short'))
        # Close Button
        btn_close_js = tk.Button(master=page, text='Close Sip & Puff Settings', command=lambda: page.destroy())
        btn_close_js.grid(row=8, column=0, columnspan=4, sticky='news')

    def settings_speech2text(self):
        page = tk.Toplevel(self.main_menu)
        page.title('Settings Speech to text')
        # Chose mode to start program with
        l_startm = tk.Label(master=page, text="Set defulat mode at start up: ")
        l_startm.grid(row=0, column=0, columnspan=2)

        start_mode = tk.StringVar()
        start_mode.set(list(self.modes.keys())[0])
        m_select_start = tk.OptionMenu(page, start_mode, *list(self.modes.keys()))
        m_select_start.grid(row=1, column=0, columnspan=2)

        btn_set_start = tk.Button(master=page, text='Make defualt on Start up',
                                  command=lambda: self.set_start(start_mode.get()))
        btn_set_start.grid(row=2, column=0, columnspan=2)

        # Turn off and on trascription
        l_onoff = tk.Label(master=page, text="Transcription on/off")
        l_onoff.grid(row=3, column=0, columnspan=2)

        btn_on = tk.Button(master=page, text="ON", command=lambda: self.off_transcript(btn_on))
        btn_on.grid(row=4, column=0, columnspan=2)

        # Create New Node
        l_cmd_add_mode = tk.Label(master=page, text='Name of mode:')
        l_cmd_add_mode.grid(row=5, column=0)

        txt_box_mode = tk.Entry(master=page)
        txt_box_mode.grid(row=5, column=1)

        btn_create_mode = tk.Button(master=page, text='Add new mode',
                                    command=lambda: self.create_mode(txt_box_mode.get()))
        btn_create_mode.grid(row=6, column=0, columnspan=2)

        # Add new command to mode
        l_cmd_mode = tk.Label(master=page, text='Add cmd to mode:')
        l_cmd_mode.grid(row=7, column=0, columnspan=2)

        current_modes = tk.StringVar()
        current_modes.set(self.current_mode.get())
        m_select_modeadd = tk.OptionMenu(page, current_modes, *list(self.modes.keys()))
        m_select_modeadd.grid(row=8, column=0, columnspan=2)

        l_cmd_key_word = tk.Label(master=page, text='Key word to cmd:')
        l_cmd_key_word.grid(row=9, column=0)

        txt_key_word = tk.Entry(master=page)
        txt_key_word.grid(row=9, column=1)

        l_cmd = tk.Label(master=page, text='Desired cmd:')
        l_cmd.grid(row=10, column=0)

        txt_cmd = tk.Entry(master=page)
        txt_cmd.grid(row=10, column=1)

        btn_addmode = tk.Button(master=page, text='Add command',
                                command=lambda: self.add_cmd(current_modes.get(), txt_key_word.get(), txt_cmd.get()))
        btn_addmode.grid(row=11, column=0, columnspan=2)

        # Close Button
        btn_close_stt = tk.Button(master=page, text='Close Speech to Text Settings', command=lambda: page.destroy())
        btn_close_stt.grid(row=13, column=0, columnspan=4, sticky='news')

    def settings_gui(self):
        gui_page = tk.messagebox.showinfo(title='Window options', message='Window options are still under development')

    def settings_update(self, value, name):
        self.settings[name] = value
        self.changes = True

    def move(self):
        # set up grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)
        self.root.grid_columnconfigure(5, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        # resize and move window
        self.root.geometry(
            '%dx%d+0+0' % (0.1 * self.width, 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
        # reorganize the buttons
        self.btn_exit.grid(row=0, column=0, sticky='news')
        self.btn_settings.grid(row=5, column=0, sticky='news')
        self.m_mode.grid(row=1, column=0, sticky='news')
        self.btn_move.grid(row=2, column=0, sticky='news')
        self.btn_move.config(text='Panel View', command=lambda: self.panel_view())
        self.btn_hide.grid(row=3, column=0, sticky='news')

        # hide the trascription
        self.l_transcription.grid_forget()

    def add_cmd(self, mode, key, cmd):
        filename = self.modes[mode].file_name
        keys = key.split()
        if len(keys)>1:
            print(str(mode) + str(keys[0]) + 'multi')
            save_add_cmd(filename, key[0], cmd)
            print(str(mode) + str(keys[0]) + str(keys[1]) + str(cmd))
            save_add_cmd(filename, keys[0]+keys[1], cmd)
        else:
            print(str(mode) + str(keys[0]) + str(cmd))
            save_add_cmd(filename, keys[0], cmd)
    def create_mode(self, name):
        file = open('cmd_' + str(name) + '.txt', 'w+', encoding='utf-8')
        file.close()
        self.modes[name] = Mode(name, True, 'cmd_' + str(name) + '.txt')

    def set_start(self, mode):
        print('Make default')

    def panel_view(self):
        # resize and move window
        self.root.geometry('%dx%d+0+%d' % (self.width, 0.1 * self.height, (1 - 0.2) * self.height))

        # frame
        # self.panel_frame = Frame(self.root, )
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=24)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        # reroganize the buttons
        self.btn_exit.grid(row=0, column=0, sticky='nsew')
        self.m_mode.grid(row=0, column=1, sticky='nsew')
        self.btn_move.grid(row=0, column=3, sticky='nsew')
        self.btn_move.config(text='Minimize', command=lambda: self.move())
        self.btn_hide.grid(row=0, column=4, sticky='nsew')
        self.btn_settings.grid(row=0, column=5, sticky='nsew')
        self.l_transcription.grid(row=0, column=2, sticky='nsew')

    def hide(self):
        # hide window so that just the icon on the taskbar is left
        self.root.iconify()

    def change_mode(self, select):
        self.current_mode = select
        self.transcription = self.modes[select].trans
        print(self.transcription)
        if not self.transcription:
            self.l_transcription.config(text='Transcription is off')

        print('Update mode to %s' % select)

    def uppdate_transcript(self, line):
        if self.transcription:
            self.l_transcription.config(text=line)
        else:
            self.l_transcription.config(text='Transcription is off')

    def off_transcript(self, btn):
        self.l_transcription.config(text='Transcription is off')
        self.transcription = False
        btn.config(text='OFF', command=lambda: self.on_transcript(btn))

    def on_transcript(self, btn):
        self.transcription = True
        self.l_transcription.config(text='Transcription is on')
        btn.config(text='ON', command=lambda: self.off_transcript(btn))

    def factory_settings(self):
        factory_msg = tk.messagebox.askokcancel(title='Reset to factory settings',
                                                message='Do you wish to reset the app to factory settings?\n All your personalised settings will be lost.')
        if factory_msg:
            self.settings = setting_config('DefaultSettingsGUI.txt')
            save_changed_settings('settingsGUI.txt', self.settings)


def save_changed_settings(filename, dict):
    print('save changes runs')
    file = open(filename, 'w', encoding='utf-8')
    li = dict.items()
    for pair in li:
        if not (isinstance(pair[1], list)):
            file.write(str(pair[0]) + ';' + str(pair[1]) + '\n')
        else:
            file.write(str(pair[0]))
            for el in pair[1]:
                file.write(';' + str(el))
            file.write('\n')
    file.close()


def save_add_cmd(filename_mode, key, value):
    file = open(filename_mode, 'a', encoding='utf-8')
    file.write(key + ',' + str(value) + '\n')
    file.close()


class Mode():
    # class that creates mode objects
    def __init__(self, name, transcription, file, echo):
        self.name = name
        self.trans = int(transcription)
        self.file_name = file
        self.echo = int(echo)


def mode_dict_set_up(filename):
    mode_dict = {}
    file = open(filename, 'r', encoding='utf-8')
    line = file.readlines()
    for mode in line:
        name, transcript, track_file, echo = mode.split(';')
        track_file = track_file.strip('\n')
        mode_dict[name] = (Mode(name, transcript, track_file,echo))
    file.close()

    return mode_dict


def mode_dict_update():
    pass


def setting_config(filename):
    """sets up a dict contains all the settings"""
    settings_current = {}
    file = open(filename, 'r', encoding='utf-8')
    lines = file.readlines()
    file.close()
    for line in lines:
        l = line.strip('\n')
        l = l.split(';')
        if len(l) == 2:
            settings_current[l[0]] = l[1]
        else:
            tmp_l = []
            for i in range(1, len(l)):
                tmp_l.append(l[i])
            settings_current[l[0]] = tmp_l

    return settings_current


if __name__ == "__main__":
    modes = mode_dict_set_up('GUISetUp.txt')
    print(modes['typing'].file_name)
    settings = setting_config('SettingsGUI.txt')
    app = GUI(modes, settings, 'GUISetUp.txt')
