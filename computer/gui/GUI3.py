import tkinter as tk
import tkinter.messagebox
import datetime

class App:
    """ sets up the main window and all the graphics """
    def __init__(self, modes):
    # set up root window
        self.root = tk.Tk()
        self.root.title('App Name Menu')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+%d' %(self.width,0.1*self.height,self.height-0.2*self.height)) # note: 0,0 cooordiantes is top left corner
        self.root.attributes('-topmost', True)


        #frame
           # self.panel_frame = Frame(self.root, )
        self.root.grid_columnconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=24)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    #Buttons
        #Menu buttons

        self.btn_exit = tk.Button(self.root, text = 'Exit')
        self.btn_exit['command'] = lambda: self.root.destroy() # note: when we turn this to an app change to root.quit
        self.btn_exit.grid(row = 0, column = 0, sticky = 'nsew')

        self.btn_move = tk.Button(self.root, text = 'Minimize')
        self.btn_move['command'] = lambda: self.move()
        self.btn_move.grid(row = 0, column = 3, sticky = 'nsew')

        self.btn_hide = tk.Button(self.root, text='Hide')
        self.btn_hide['command'] = lambda: self.hide()
        self.btn_hide.grid(row=0, column=4,sticky = 'nsew')

        self.btn_settings = tk.Button(self.root, text='Settings')
        self.btn_settings['command'] = lambda: self.settings()
        self.btn_settings.grid(row=0, column=5, sticky = 'nsew')
    # Transcription setup as a label
        self.transcription = tk.Label(self.root, text = 'Transcript runs here', bg = 'black', fg='white', anchor = 'nw'
                                   , height = 2)
        #self.transcription.config(wraplength = ) potentially needs to be set to ensure
        self.transcription.grid(row = 0, column = 2, sticky = 'nsew')


    # mode menu
        self.current_mode = tk.StringVar()
        self.current_mode.set(modes[0])
        self.m_mode = tk.OptionMenu(self.root, self.current_mode, *modes, command = self.change_mode)
        self.m_mode.grid(row = 0, column =1, sticky='nsew')

        self.root.mainloop()


    def settings(self):
        self.settings_w = tk.Toplevel()
        self.settings_w.title('Settings')
        self.page = tk.Frame(self.settings_w)


        self.page.columnconfigure(0, weight = 1)
        self.page.rowconfigure(0, weight = 1)
        self.page.grid(row=0, column=0, sticky='nsew')

        self.frames = {}
        self.pages = {}
        self.pages[SettingsMenu] = SettingsMenu(self.page, self)
        self.show_page(SettingsMenu)

    def show_page(self, selected):
        page = self.pages[selected]
        page.lift(self.settings_w)

    def move(self):
        #trun of topmost
        self.root.attributes('-topmost', False)
        #set up grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)
        self.root.grid_columnconfigure(5, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        #resize and move window
        self.root.geometry('%dx%d+0+0' % (0.1*self.width, 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
        #reorganize the buttons
        self.btn_exit.grid(row = 0, column = 0, sticky = 'news')
        self.btn_settings.grid(row=5, column=0, sticky='news')
        self.m_mode.grid(row=1, column=0, sticky='news')
        self.btn_move.grid(row=2, column=0, sticky='news')
        self.btn_move.config(text = 'Panel View', command = lambda: self.panel_view())
        self.btn_hide.grid(row=3, column=0, sticky='news')

        #hide the trascription
        self.transcription.grid_forget()

    def panel_view(self):
        #resize and move window
        self.root.geometry('%dx%d+0+%d' % (self.width, 0.1 * self.height, self.height - 0.2 * self.height))
        #Turn on Foremost
        self.root.attributes('-topmost', True)
        #frame
           # self.panel_frame = Frame(self.root, )
        self.root.grid_columnconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=24)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        #reroganize the buttons
        self.btn_exit.grid(row=0, column=0, sticky='nsew')
        self.m_mode.grid(row=0, column=1, sticky='nsew')
        self.btn_move.grid(row = 0, column = 3, sticky = 'nsew')
        self.btn_move.config(text='Minimize', command=lambda: self.move())
        self.btn_hide.grid(row=0, column=4, sticky='nsew')
        self.btn_settings.grid(row=0, column=5, sticky='nsew')
        self.transcription.grid(row=0, column=2, sticky='nsew')


    def hide(self):
        #hide window so that just the icon on the taskbar is left
        self.root.iconify()

    def change_mode(self, select):
        print ('Updtate mode to %s' %select)





class SettingsMenu(tk.Frame):
    def __init__(self, parent,control):
        tk.Frame.__init__(self, parent)
        self.controller = control
        self.btn_js = tk.Button(self, text = 'Joy Stick')
        self.btn_js.grid(row = 0, column = 0)

        self.btn_snp = tk.Button(self, text='Sip & Puff')
        self.btn_snp.grid(row=0, column=1)

        self.btn_stt = tk.Button(self, text='Speach to Text')
        self.btn_stt.grid(row=1, column=0)

        self.btn_def = tk.Button(self, text='Window Options')
        self.btn_def.grid(row=1, column=1)



class Mode():
    #class that creates mode objects
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
            self.dictionary[name]=(Mode(name, transcript, track_file))

    def get_keys(self):
        return list(self.dictionary.keys())

class settings():
    """class that contains all the settings"""
pass


def main():
    modes = Mode_list('GUISetUp.txt')
    app = App(modes.get_keys())

main()