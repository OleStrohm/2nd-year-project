import tkinter as tk
import tkinter.messagebox
import datetime


class App:
    """ sets up the main window and all the graphics """

    def __init__(self, modes, settings):
        # set up root window
        self.root = tk.Tk()
        self.root.title('App Name Menu')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+%d' % (
        self.width, 0.1 * self.height, self.height - 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
        self.root.attributes('-topmost', True)
        self.settings = settings

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
        self.btn_exit['command'] = lambda: self.root.destroy()  # note: when we turn this to an app change to root.quit
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
        self.transcription = tk.Label(self.root, text='Transcript runs here', bg='black', fg='white', anchor='nw',
                                      height=2)
        # self.transcription.config(wraplength = ) potentially needs to be set to ensure
        self.transcription.grid(row=0, column=2, sticky='nsew')

        # mode menu
        self.current_mode = tk.StringVar()
        self.current_mode.set(modes[0])
        self.m_mode = tk.OptionMenu(self.root, self.current_mode, *modes, command=self.change_mode)
        self.m_mode.grid(row=0, column=1, sticky='nsew')

        self.root.mainloop()

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

        btn_stt = tk.Button(self.main_menu, text='Speach to Text')
        btn_stt.grid(row=2, column=1, sticky='news')

        btn_def = tk.Button(self.main_menu, text='Window Options')
        btn_def.grid(row=2, column=2, sticky='news')

    def settings_joy(self):
        joy_page = tk.Toplevel(self.main_menu)
        joy_page.title('Settings Joystick')
        # set the speed of the cursor
        l_speed = tk.Label(master=joy_page, text='Cursor speed')
        l_speed.grid(row=0, column=0, columnspan=2, sticky='news')
        l_smin = tk.Label(master=joy_page, text='Min Range 0').grid(row=1, column=0, sticky='nes')
        l_smax = tk.Label(master=joy_page, text='100 Max Range').grid(row=1, column=2, sticky='nws')
        slider_speed = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal')
        slider_speed.set(self.settings.cursor_speed)  # update with settings value
        slider_speed.grid(row=1, column=1, columnspan=2, sticky='news')
        slider_speed.bind("<ButtonRelease>", lambda event: self.settings_update(slider_speed.get(), 'js_speed'))

        # Set Up Range Sensetivity
        l_X = tk.Label(master=joy_page, text='X Range')
        l_X.grid(row=2, column=0, columnspan=3, sticky='ews')
        l_Xmin = tk.Label(master=joy_page, text='Min Range 0').grid(row=3, column=0, sticky='nes')
        l_Xmix = tk.Label(master=joy_page, text='100 Max Range').grid(row=3, column=2, sticky='nws')
        slider_X = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal', )
        slider_X.set(self.settings.Xrange)  # update with settings value
        slider_X.grid(row=3, column=1, sticky='news')
        slider_X.bind("<ButtonRelease>", lambda event: self.settings_update(slider_X.get(), 'X_range'))

        # Set Up Range Sensetivity
        l_Y = tk.Label(master=joy_page, text='Y Range')
        l_Y.grid(row=4, column=0, columnspan=3, sticky='ews')
        l_Ymin = tk.Label(master=joy_page, text='Min Range 0').grid(row=5, column=0, sticky='nes')
        l_Ymix = tk.Label(master=joy_page, text='100 Max Range').grid(row=5, column=2, sticky='nws')
        slider_Y = tk.Scale(master=joy_page, from_=0, to=100, orient='horizontal', )
        slider_Y.set(self.settings.Yrange)  # update with settings value
        slider_Y.grid(row=5, column=1, sticky='news')
        slider_Y.bind("<ButtonRelease>", lambda event: self.settings_update(slider_Y.get(), 'Y_range'))

        # Close Button
        btn_close_js = tk.Button(master=joy_page, text='Close Joystick Settings', command=lambda: joy_page.destroy())
        btn_close_js.grid(row=6, column=1, sticky='news')

    def settings_sip(self):
        page = tk.Toplevel(self.main_menu)
        page.title('Settings Sip & Puff')
        # set up pressure sensetivity
        l_pressure = tk.Label(master=page, text='Pressure Threshold')
        l_pressure.grid(row=0, column=0, columnspan=3, sticky='news')
        l_pmin = tk.Label(master=page, text='Min Range 0').grid(row=1, column=0, sticky='nes')
        l_pmax = tk.Label(master=page, text='100 Max Range').grid(row=1, column=2, sticky='nws')
        slider_pressure = tk.Scale(master=page, from_=0, to=100, orient='horizontal')
        slider_pressure.set(self.settings.sens)  # update with settings value
        slider_pressure.grid(row=1, column=1, columnspan=2, sticky='news')
        slider_pressure.bind("<ButtonRelease>",
                             lambda event: self.settings_update(slider_pressure.get(), self.settings.sens))

        # Set type of 'left click puff
        l_left = tk.Label(master=page, text='Left click functionality')
        l_left.grid(row=3, column=0, columnspan=3, sticky='ews')
        current_type_pre = tk.StringVar()
        current_type_pre.set(self.settings.left_C[0])
        l_left_menu_pre = tk.OptionMenu(page, current_type_pre, *self.settings.select_type_pressure, )
        l_left_menu_pre.grid(row=4, column=1, columnspan=2)
        current_type_time = tk.StringVar()
        current_type_time.set(self.settings.left_C[1])
        l_left_menu_time = tk.OptionMenu(page, current_type_time, *self.settings.select_type_time)
        l_left_menu_time.grid(row=4, column=2, columnspan=2)

        # Set Length of 'left click puff
        l_left = tk.Label(master=page, text='Right click functionality')
        l_left.grid(row=5, column=0, columnspan=3, sticky='ews')
        current_type_r_pre = tk.StringVar()
        current_type_r_pre.set(self.settings.right_C[0])
        l_left_menu_r_pre = tk.OptionMenu(page, current_type_r_pre, *self.settings.select_type_pressure, )
        l_left_menu_r_pre.grid(row=6, column=1, columnspan=2)
        current_type_r_time = tk.StringVar()
        current_type_r_time.set(self.settings.right_C[1])
        l_left_menu_r_time = tk.OptionMenu(page, current_type_r_time, *self.settings.select_type_time)
        l_left_menu_r_time.grid(row=6, column=2, columnspan=2)

        # Close Button
        btn_close_js = tk.Button(master=page, text='Close Sip & Puff Settings', command=lambda: page.destroy())
        btn_close_js.grid(row=7, column=1, sticky='news')

    def settings_update(self, value, name):
        print('Paramter: %s \n Value: %d' % (name, value))

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
        self.transcription.grid_forget()

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
        self.transcription.grid(row=0, column=2, sticky='nsew')

    def hide(self):
        # hide window so that just the icon on the taskbar is left
        self.root.iconify()

    def change_mode(self, select):
        print('Updtate mode to %s' % select)

    def uppdate_transcript(self, line):
        self.transcription.config(text=line)


class Mode():
    # class that creates mode objects
    def __init__(self, name, transcription, menu_pos):
        self.name = name
        self.transcription = transcription
        self.menu_pos = menu_pos


class Mode_list():
    def __init__(self, filename):
        self.setup_file = filename
        self.dictionary = {}
        self.setup()

    def setup(self):
        file = open(self.setup_file, 'r', encoding='utf-8')
        line = file.readlines()
        for mode in line:
            name, transcript, track_file = mode.split(';')
            self.dictionary[name] = (Mode(name, transcript, track_file))
        file.close()

    def get_keys(self):
        return list(self.dictionary.keys())


class Setting():
    """class that contains all the settings"""

    def __init__(self, filename):
        self.settings = self.setup(filename)
        # joy stick settings
        self.deadzone = self.settings[0][1]
        self.Xrange = self.settings[0][3]
        self.Yrange = self.settings[0][5]
        self.cursor_speed = self.settings[0][7]

        # sip and puff settings
        self.left_C = [self.settings[1][1], self.settings[1][2]]
        self.right_C = [self.settings[1][4], self.settings[1][5]]
        self.sens = self.settings[1][7]
        self.select_type_time = [self.settings[2][3], self.settings[2][4]]
        self.select_type_pressure = [self.settings[2][1], self.settings[2][2]]

    def setup(self, setup_file):
        file = open(setup_file, 'r', encoding='utf-8')
        line = file.readlines()
        settings_current = []
        for set in line:
            type = set.split(';')
            settings_current.append(type)
        file.close()
        return settings_current


if __name__ == "__main__":
    modes = Mode_list('GUISetUp.txt')
    settings = Setting('SettingsGUI.txt')
    app = App(modes.get_keys(), settings)
