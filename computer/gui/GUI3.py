import tkinter as tk
import tkinter.messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
from ttkwidgets import TickScale
from word2cmd import CommandController

from threading import Thread
from arduinoControl import ArduinoController
from threading import Lock
import keyboard as kb


class GUI:
	# sets up the main window and all the graphics

	def __init__(self, path, modes_file, settings_file, arduino, commands, speech_to_text):
		self.commands = commands
		self.arduino = arduino
		self.arduino.set_gui_callback(self.sip_transcription)
		self.speech_to_text = speech_to_text
		self.path = path
		self.modes_file = path + modes_file
		self.settings_file = path + settings_file

		self.modes = mode_dict_set_up(self.modes_file)
		self.settings = setting_config(self.settings_file)


		for key in self.modes:
			self.commands.load_cmds(key, path + self.modes[key].file_name)

		self.update_sip_cmds(self.settings['s_sip'], self.settings['s_puff'], self.settings['l_sip'], self.settings['l_puff'], self.settings['d_sip'], self.settings['d_puff'], True)

		self.root = None
		self.width = None
		self.height = None
		self.changes = False
		self.transcription = self.modes[self.settings['start_mode']].trans
		print(self.settings['start_mode'])
		self.current_mode = self.settings['start_mode']
		print(self.current_mode)


		# set up root window
		# self.root = tk.Tk()
		self.root = ThemedTk(theme="arc", themebg=True)

		print(self.root.get_themes())

		self.root.title('App Name Menu')
		self.width = self.root.winfo_screenwidth()
		self.height = self.root.winfo_screenheight()
		self.arduino.set_bounds(self.width, self.height)
		self.root.geometry('%dx%d+%d+%d' % (
			self.width, 0.1 * self.height, 0,
			self.height - 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
		self.root.attributes('-topmost', True)

		# frame
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		self.root.grid_columnconfigure(3, weight=12)
		self.root.grid_columnconfigure(4, weight=1)
		self.root.grid_columnconfigure(5, weight=1)
		self.root.grid_columnconfigure(6, weight=1)
		self.root.grid_columnconfigure(7, weight=1)
		self.root.grid_rowconfigure(0, weight=1)
		# Buttons
		# Menu buttons
		self.btn_exit = ttk.Button(self.root, text='Exit')
		self.btn_exit['command'] = lambda: self.close_program()  # note: when we turn this to an app change to root.quit
		self.btn_exit.grid(row=0, column=0, sticky='nsew')

		self.btn_move = ttk.Button(self.root, text='Minimize')
		self.btn_move['command'] = lambda: self.move()
		self.btn_move.grid(row=0, column=5, sticky='nsew')

		self.btn_transcription = ttk.Button(self.root, text='something')
		self.btn_transcription.grid(row=0, column=2, sticky='news')

		self.btn_hide = ttk.Button(self.root, text='Hide')
		self.btn_hide['command'] = lambda: self.hide()
		self.btn_hide.grid(row=0, column=6, sticky='nsew')

		self.btn_settings = ttk.Button(self.root, text='Settings')
		self.btn_settings['command'] = lambda: self.settings_start()
		self.btn_settings.grid(row=0, column=7, sticky='nsew')
		# Transcription setup as a label
		self.l_transcription = ttk.Label(self.root, text='Transcript runs here', anchor='nw', background='black',
										 foreground='white',
										 width=80, wraplength=0.6 * self.width)
		self.l_transcription.grid(row=0, column=3, sticky='nsew')

		# puff transcription
		self.l_sips = ttk.Label (self.root, text='Short sip', foreground = 'purple', anchor = 'center')
		self.l_sips.grid(row = 0, column = 4, sticky = 'nesw')

		# mode menu
		self.m_current_mode = tk.StringVar()
		self.m_current_mode.set(self.current_mode)
		self.m_mode = ttk.OptionMenu(self.root, self.m_current_mode, self.current_mode, *list(self.modes.keys()),
									 command=self.change_mode)
		self.m_mode.grid(row=0, column=1, sticky='nsew')

		if self.transcription:
			self.on_transcript()
		else:
			self.off_transcript()
		self.root.protocol('WM_DELETE_WINDOW', self.close_program)


	def start(self):
		self.root.mainloop()
		print("closed gui")

	def close_program(self):
		print('Program should do complete exit')
		if self.arduino != None:
			self.arduino.stop()
		if self.speech_to_text != None:
			self.speech_to_text.stop()
		self.root.destroy()

	def settings_start(self):
		self.main_menu = tk.Toplevel()
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

		btn_js = ttk.Button(self.main_menu, text='Joy Stick', command=lambda: self.settings_joy())
		btn_js.grid(row=1, column=1, sticky='news')

		btn_snp = ttk.Button(self.main_menu, text='Sip & Puff', command=lambda: self.settings_sip())
		btn_snp.grid(row=1, column=2, sticky='news')

		btn_stt = ttk.Button(self.main_menu, text='Speech to Text', command=lambda: self.settings_speech2text())
		btn_stt.grid(row=2, column=1, sticky='news')

		btn_def = ttk.Button(self.main_menu, text='Window Options', command=lambda: self.settings_gui())
		btn_def.grid(row=2, column=2, sticky='news')

		btn_factory = ttk.Button(self.main_menu, text='Factory Settings', command=lambda: self.factory_settings())
		btn_factory.grid(row=3, column=4, columnspan=1, sticky='es')

		btn_close = ttk.Button(self.main_menu, text='Close settings', command=self.main_menu.destroy)
		btn_close.grid(row=4, column=1, columnspan=2, sticky='s')

		# self.main_menu.protocol('WM_DELETE_WINDOW', lambda: self.close_settings('all', self.main_menu))

	def close_settings(self, name, window):
		if (self.changes):
			default_msg = tk.messagebox.askyesno(title='Update %s settings ' % name,
												 message='You have unsaved changes. Do you wish to make the settings changes to your default settings?')
			if default_msg:
				self.save(self.settings_file, self.settings)
		window.destroy()

	def sip_changes(self, _):
		self.changes = True

	def sip_close(self, s_sip, s_puff, l_sip, l_puff, d_sip, d_puff, window):
		if self.changes:
			default_msg = tk.messagebox.askyesno(title='Update sip settings',
												 message='You have unsaved changes. Do you wish to save these changes?')
			if default_msg:
				self.update_sip_cmds(s_sip, s_puff, l_sip, l_puff, d_sip, d_puff)
		window.destroy()

	def save(self, filename, dict_set):
		save_changed_settings(filename, dict_set)
		self.changes = False

	def settings_joy(self):
		joy_page = tk.Toplevel(self.main_menu)
		joy_page.title('Settings Joystick')
		# set size of dead zone
		l_speed = ttk.Label(master=joy_page, text='Dead zone size')
		l_speed.grid(row=6, column=0, columnspan=2, sticky='news')
		l_smin = ttk.Label(master=joy_page, text='Min size 0').grid(row=7, column=0, sticky='nes')
		l_smax = ttk.Label(master=joy_page, text='100 Max size').grid(row=7, column=2, sticky='nws')
		dead_zone = TickScale(master=joy_page, from_=0, to=20, orient='horizontal', digits = 0, command=lambda e: self.settings_update(e, 'dead_zone', self.arduino.set_mouse_dead_zone))
		dead_zone = TickScale(master=joy_page, from_=0, to=20, orient='horizontal', digits=0)
		dead_zone.set(self.settings['dead_zone'])  # update with settings value
		dead_zone.grid(row=7, column=1, columnspan=1, sticky='news')


		# set the speed of the cursor
		l_speed = ttk.Label(master=joy_page, text='Cursor speed')
		l_speed.grid(row=0, column=0, columnspan=2, sticky='news')
		l_smin = ttk.Label(master=joy_page, text='Min 0').grid(row=1, column=0, sticky='nes')
		l_smax = ttk.Label(master=joy_page, text='100 Max').grid(row=1, column=2, sticky='nws')
		slider_speed = ttk.Scale(master=joy_page, from_=0.1, to=10, orient='horizontal')
		slider_speed.set(self.settings['Cursor_speed'])  # update with settings value
		slider_speed.grid(row=1, column=1, columnspan=1, sticky='news')
		slider_speed.bind("<ButtonRelease>", lambda event: self.settings_update(slider_speed.get(), 'Cursor_speed',
																				self.arduino.set_mouse_speed))

		# Set Up High Spped Theshold
		l_high_speed = ttk.Label(master=joy_page, text='High Speed Threshold')
		l_high_speed.grid(row=4, column=0, columnspan=3, sticky='ews')
		l_min = ttk.Label(master=joy_page, text='Min 0').grid(row=5, column=0, sticky='nes')
		l_mix = ttk.Label(master=joy_page, text='512 Max ').grid(row=5, column=2, sticky='nws')
		slider_high_speed = ttk.Scale(master=joy_page, from_=0, to=512, orient='horizontal', )
		slider_high_speed.set(self.settings['high_speed'])  # update with settings value
		slider_high_speed.grid(row=5, column=1, sticky='news')
		slider_high_speed.bind("<ButtonRelease>",
							   lambda event: self.settings_update(slider_high_speed.get(), 'high_speed',
																  self.arduino.set_mouse_scaling_threshold))
		# Save Button
		btn_save_js = ttk.Button(master=joy_page, text='Save Settings as Default',
								 command=lambda: self.save(self.settings_file, self.settings))
		btn_save_js.grid(row=8, column=0, columnspan=3)
		# Close Button
		btn_close_js = ttk.Button(master=joy_page, text='Close Joystick Settings',
								  command=lambda: self.close_settings('Joystick', joy_page))
		btn_close_js.grid(row=9, column=0, columnspan=3, sticky='news')
		joy_page.protocol('WM_DELETE_WINDOW', lambda: self.close_settings('Joystick', joy_page))

	def settings_sip(self):
		page = tk.Toplevel(self.main_menu)
		page.title(' Advanced Settings Sip & Puff')

		btn_advanced = ttk.Button(master=page, text='Advanced Sip & Puff settings', command=self.advanced_settings_sip)
		btn_advanced.grid(row=5, column=1, columnspan=2)

		# Set commands to sip and puffs
		# cmd_list = self.settings['sip_cmds']
		cmd_list = self.arduino.functions.keys()
		print(cmd_list)
		l_sip_set = ttk.Label(master=page, text='Set up the sip and puff commands to desired action')
		l_sip_set.grid(row=0, column=0, columnspan=2)

		l_s_sip = ttk.Label(master=page, text='Single Sip')
		l_s_sip.grid(row=1, column=0, columnspan=1)

		s_sip_var = tk.StringVar()
		s_sip_var.set(self.settings['s_sip'])
		menu_s_sip = ttk.OptionMenu(page, s_sip_var, self.settings['s_sip'], *cmd_list, command=self.sip_changes)
		menu_s_sip.grid(row=1, column=1)

		l_s_puff = ttk.Label(master=page, text='Single Puff')
		l_s_puff.grid(row=1, column=2, columnspan=1)

		s_puff_var = tk.StringVar()
		s_puff_var.set(self.settings['s_puff'])
		menu_s_puff = ttk.OptionMenu(page, s_puff_var, self.settings['s_puff'], *cmd_list, command=self.sip_changes)
		menu_s_puff.grid(row=1, column=3, columnspan=1)

		l_d_sip = ttk.Label(master=page, text='Double Sip')
		l_d_sip.grid(row=2, column=0, columnspan=1)

		d_sip_var = tk.StringVar()
		d_sip_var.set(self.settings['d_sip'])
		menu_d_sip = ttk.OptionMenu(page, d_sip_var, self.settings['d_sip'], *cmd_list, command=self.sip_changes)
		menu_d_sip.grid(row=2, column=1, columnspan=1)

		l_d_puff = ttk.Label(master=page, text='Double Puff')
		l_d_puff.grid(row=2, column=2, columnspan=1)

		d_puff_var = tk.StringVar()
		d_puff_var.set(self.settings['d_puff'])
		menu_d_puff = ttk.OptionMenu(page, d_puff_var, self.settings['d_puff'], *cmd_list, command=self.sip_changes)
		menu_d_puff.grid(row=2, column=3, columnspan=1)

		l_l_sip = ttk.Label(master=page, text='Long Sip')
		l_l_sip.grid(row=3, column=0, columnspan=1)

		l_sip_var = tk.StringVar()
		l_sip_var.set(self.settings['l_sip'])
		menu_l_sip = ttk.OptionMenu(page, l_sip_var, self.settings['l_sip'], *cmd_list, command=self.sip_changes)
		menu_l_sip.grid(row=3, column=1, columnspan=1)

		l_l_puff = ttk.Label(master=page, text='Long Puff')
		l_l_puff.grid(row=3, column=2, columnspan=1)

		l_puff_var = tk.StringVar()
		l_puff_var.set(self.settings['l_puff'])
		menu_l_puff = ttk.OptionMenu(page, l_puff_var, self.settings['l_puff'], *cmd_list, command=self.sip_changes)
		menu_l_puff.grid(row=3, column=3, columnspan=1)

		# Save Button
		btn_save_sp = ttk.Button(master=page, text='Save Settings',
								 command=lambda: self.update_sip_cmds(s_sip_var.get(), s_puff_var.get(),
																	  l_sip_var.get(), l_puff_var.get(),
																	  d_sip_var.get(), d_puff_var.get()))
		btn_save_sp.grid(row=4, column=1, columnspan=2)

		# Close Button
		btn_close_sp = ttk.Button(master=page, text='Close Sip & Puff Settings',
								  command=lambda: self.sip_close(s_sip_var.get(), s_puff_var.get(), l_sip_var.get(),
																 l_puff_var.get(), d_sip_var.get(), d_puff_var.get(),
																 page))
		btn_close_sp.grid(row=6, column=0, columnspan=4, sticky='news')
		page.protocol('WM_DELETE_WINDOW',
					  lambda: self.sip_close(s_sip_var.get(), s_puff_var.get(), l_sip_var.get(), l_puff_var.get(),
											 d_sip_var.get(), d_puff_var.get(), page))

	def advanced_settings_sip(self):
		page = tk.Toplevel(self.main_menu)
		page.title(' Advanced Settings Sip & Puff')
		# Sip
		l_sip = ttk.Label(master=page, text='Sip Settings')
		l_sip.grid(row=0, column=0, columnspan=4)

		# set up pressure sensetivity
		sip_l_pressure = ttk.Label(master=page, text='Pressure Threshold')
		sip_l_pressure.grid(row=1, column=0, columnspan=3, sticky='w')
		sip_l_pmin = ttk.Label(master=page, text='Min 0').grid(row=2, column=0, sticky='nes')
		sip_l_pmax = ttk.Label(master=page, text='100 Max').grid(row=2, column=3, sticky='nws')
		sip_slider_pressure = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		sip_slider_pressure.set(self.settings['sip_pressure_threshold'])  # update with settings value
		sip_slider_pressure.grid(row=2, column=1, columnspan=2, sticky='news')
		sip_slider_pressure.bind("<ButtonRelease>",
								 lambda event: self.settings_update(sip_slider_pressure.get(), 'sip_pressure_threshold',
																	self.arduino.set_puff_threshold))

		# Length of long
		sip_l_long_time = ttk.Label(master=page, text='Length of Long pressure')
		sip_l_long_time.grid(row=3, column=0, columnspan=4, sticky='w')
		sip_l_tl_min = ttk.Label(master=page, text='Min 0').grid(row=4, column=0, sticky='nes')
		sip_l_tl_max = ttk.Label(master=page, text='100 Max').grid(row=4, column=3, sticky='nws')
		sip_slider_long_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		sip_slider_long_time.set(self.settings['sip_long_time'])  # update with settings value
		sip_slider_long_time.grid(row=4, column=1, columnspan=2, sticky='news')
		sip_slider_long_time.bind("<ButtonRelease>",
								  lambda event: self.settings_update(sip_slider_long_time.get(), 'sip_long_time',
																	 self.arduino.set_long_sip_time))

		# Length of short
		sip_l_short_time = ttk.Label(master=page, text='Length of Short pressure')
		sip_l_short_time.grid(row=5, column=0, columnspan=4, sticky='w')
		sip_l_tl_min = ttk.Label(master=page, text='Min 0').grid(row=6, column=0, sticky='nes')
		sip_l_tl_max = ttk.Label(master=page, text='100 Max').grid(row=6, column=3, sticky='nws')
		sip_slider_short_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		sip_slider_short_time.set(self.settings['sip_short_time'])  # update with settings value
		sip_slider_short_time.grid(row=6, column=1, columnspan=2, sticky='news')
		sip_slider_short_time.bind("<ButtonRelease>",
								   lambda event: self.settings_update(sip_slider_short_time.get(), 'sip_short_time',
																	  self.arduino.set_short_sip_time))

		# Double time
		sip_l_d_time = ttk.Label(master=page, text='Double Time')
		sip_l_d_time.grid(row=7, column=0, columnspan=3, sticky='w')
		sip_l_dmin = ttk.Label(master=page, text='Min 0').grid(row=8, column=0, sticky='nes')
		sip_l_dmax = ttk.Label(master=page, text='100 Max').grid(row=8, column=3, sticky='nws')
		slider_sip_d_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		slider_sip_d_time.set(self.settings['sip_double_time'])  # update with settings value
		slider_sip_d_time.grid(row=8, column=1, columnspan=2, sticky='news')
		slider_sip_d_time.bind("<ButtonRelease>",
							   lambda event: self.settings_update(slider_sip_d_time.get(), 'sip_double_time',
																  self.arduino.set_puff_threshold))

		# Puff
		l_puff = ttk.Label(master=page, text='Puff Settings')
		l_puff.grid(row=0, column=4, columnspan=4)

		# set up pressure sensetivity
		puff_l_pressure = ttk.Label(master=page, text='Pressure Threshold')
		puff_l_pressure.grid(row=1, column=4, columnspan=3, sticky='news')
		puff_l_pmin = ttk.Label(master=page, text='Min 0').grid(row=2, column=4, sticky='nes')
		puff_l_pmax = ttk.Label(master=page, text='100 Max').grid(row=2, column=7, sticky='nws')
		puff_slider_pressure = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		puff_slider_pressure.set(self.settings['puff_pressure_threshold'])  # update with settings value
		puff_slider_pressure.grid(row=2, column=5, columnspan=2, sticky='news')
		puff_slider_pressure.bind("<ButtonRelease>",
								  lambda event: self.settings_update(sip_slider_pressure.get(),
																	 'sip_pressure_threshold',
																	 self.arduino.set_puff_threshold))

		# Length of long
		puff_l_long_time = ttk.Label(master=page, text='Length of Long pressure')
		puff_l_long_time.grid(row=3, column=4, columnspan=4, sticky='news')
		puff_l_tl_min = ttk.Label(master=page, text='Min 0').grid(row=4, column=4, sticky='nes')
		puff_l_tl_max = ttk.Label(master=page, text='100 Max').grid(row=4, column=7, sticky='nws')
		puff_slider_long_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		puff_slider_long_time.set(self.settings['puff_long_time'])  # update with settings value
		puff_slider_long_time.grid(row=4, column=5, columnspan=2, sticky='news')
		puff_slider_long_time.bind("<ButtonRelease>",
								   lambda event: self.settings_update(puff_slider_long_time.get(), 'puff_long_time',
																	  self.arduino.set_long_puff_time))

		# Length of short
		puff_l_short_time = ttk.Label(master=page, text='Length of Short pressure')
		puff_l_short_time.grid(row=5, column=4, columnspan=4, sticky='news')
		puff_l_tl_min = ttk.Label(master=page, text='Min 0').grid(row=6, column=4, sticky='nes')
		puff_l_tl_max = ttk.Label(master=page, text='100 Max').grid(row=6, column=7, sticky='nws')
		puff_slider_short_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		puff_slider_short_time.set(self.settings['puff_short_time'])  # update with settings value
		puff_slider_short_time.grid(row=6, column=5, columnspan=2, sticky='news')
		puff_slider_short_time.bind("<ButtonRelease>",
									lambda event: self.settings_update(puff_slider_short_time.get(), 'puff_short_time',
																	   self.arduino.set_short_puff_time))

		# Double time
		puff_l_d_time = ttk.Label(master=page, text='Double Time')
		puff_l_d_time.grid(row=7, column=4, columnspan=3, sticky='news')
		puff_l_dmin = ttk.Label(master=page, text='Min 0').grid(row=8, column=4, sticky='nes')
		puff_l_dmax = ttk.Label(master=page, text='100 Max').grid(row=8, column=7, sticky='nws')
		slider_puff_d_time = ttk.Scale(master=page, from_=0, to=100, orient='horizontal')
		slider_puff_d_time.set(self.settings['puff_double_time'])  # update with settings value
		slider_puff_d_time.grid(row=8, column=5, columnspan=2, sticky='news')
		slider_puff_d_time.bind("<ButtonRelease>",
								lambda event: self.settings_update(slider_puff_d_time.get(), 'puff_double_time',
																   self.arduino.set_puff_threshold))

		# Save Button
		btn_save_sp = ttk.Button(master=page, text='Save Advanced Settings as Default',
								 command=lambda: self.save(self.settings_file, self.settings))
		btn_save_sp.grid(row=9, column=3, columnspan=2)

		# Close Button
		btn_close_sp = ttk.Button(master=page, text='Close Advanced Sip & Puff Settings',
								  command=lambda: self.close_settings('Sip & Puff', page))
		btn_close_sp.grid(row=10, column=3, columnspan=2, sticky='news')
		page.protocol('WM_DELETE_WINDOW', lambda: self.close_settings('Sip & Puff', page))

	def settings_speech2text(self):
		page = tk.Toplevel(self.main_menu)
		page.title('Settings Speech to text')
		# Chose mode to start program with
		l_startm = ttk.Label(master=page, text="Set default mode at start up: ")
		l_startm.grid(row=0, column=0, columnspan=2)

		start_mode = tk.StringVar()
		start_mode.set(self.settings['start_mode'])
		m_select_start = ttk.OptionMenu(page, start_mode, self.settings['start_mode'], *list(self.modes.keys()),
										command=lambda select: self.settings_update(select, 'start_mode'))
		m_select_start.grid(row=1, column=0, columnspan=2)

		btn_set_start = ttk.Button(master=page, text='Make default on Start up',
								   command=lambda: self.save(self.settings_file, self.settings))
		btn_set_start.grid(row=2, column=0, columnspan=2)

		# Selection to trun on/off
		l_trans_onoff = ttk.Label(master=page, text='Set transcription on/off')
		l_trans_onoff.grid(row=3, column=1, columnspan=2)

		# make check box selection
		check_boxes = ttk.Frame(page)
		check_boxes.grid(row=4, column=0, columnspan=2, sticky='news')
		modes_list = list(self.modes.keys())
		index = list(range(len(modes_list)))
		for i in range(0, len(self.modes.keys())):
			index[i] = tk.IntVar()
			print(self.modes[modes_list[i]].trans)
			index[i].set(self.modes[modes_list[i]].trans)
			ttk.Checkbutton(master=check_boxes, text=modes_list[i], var=index[i],
							command=lambda: self.update_trans(modes_list, index)).grid(row=i, column=0)

		btn_update_trans_set = ttk.Button(master=page, text='Update transcription default', command=self.save_trans)
		btn_update_trans_set.grid(row=5, column=0, columnspan=2)

		# Advanced mode settings
		btn_mode_adv = ttk.Button(master=page, text='Advance Mode Settings', command=self.additional_mode)
		btn_mode_adv.grid(row=6, column=0, columnspan=2)
		# Close Button
		btn_close_stt = ttk.Button(master=page, text='Close Speech to Text Settings',
								   command=lambda: self.save_sip(page))
		btn_close_stt.grid(row=7, column=0, columnspan=2, sticky='news')

		page.protocol('WM_DELETE_WINDOW', lambda: self.save_sip(page))

	def additional_mode(self):
		page = tk.Toplevel()
		page.title('Advanced mode Settings')

		# Create New Mode
		l_cmd_add_mode = ttk.Label(master=page, text='Name of mode:')
		l_cmd_add_mode.grid(row=5, column=0)

		txt_box_mode = ttk.Entry(master=page)
		txt_box_mode.grid(row=5, column=1)

		new_echo = tk.IntVar
		check_echo = ttk.Checkbutton(master=page, text='Transcription', var=new_echo)
		check_echo.grid(row=6, column=0, columnspan=2, sticky='w')

		btn_create_mode = ttk.Button(master=page, text='Add new mode',
									 command=lambda: self.create_mode(txt_box_mode.get(), new_echo, txt_box_mode))
		btn_create_mode.grid(row=7, column=0, columnspan=2)

		# Add new command to mode
		l_cmd_mode = ttk.Label(master=page, text='Add cmd to mode:')
		l_cmd_mode.grid(row=11, column=0, columnspan=2)

		current_modes = tk.StringVar()
		current_modes.set(self.current_mode)
		m_select_modeadd = ttk.OptionMenu(page, current_modes, self.current_mode, *list(self.modes.keys()))
		m_select_modeadd.grid(row=12, column=0, columnspan=2)

		l_cmd_key_word = ttk.Label(master=page, text='Key word to cmd:')
		l_cmd_key_word.grid(row=13, column=0)

		txt_key_word = ttk.Entry(master=page)
		txt_key_word.grid(row=13, column=1)

		l_cmd = ttk.Label(master=page, text='Desired cmd:')
		l_cmd.grid(row=14, column=0)

		txt_cmd = ttk.Entry(master=page)
		txt_cmd.grid(row=14, column=1)

		btn_addmode = ttk.Button(master=page, text='Add command',
								 command=lambda: self.add_cmd(current_modes.get(), txt_key_word.get(), txt_cmd.get(),
															  txt_key_word, txt_cmd))
		btn_addmode.grid(row=15, column=0, columnspan=2)

	def save_sip(self, window):
		if self.changes:
			msg = tk.messagebox.askyesno(title='Unsaved Changes',
										 message='There are unsaved settings changes. Do you wish to save these to default settings?')
			if msg:
				self.changes = False
				save_changed_settings(self.settings_file, self.settings)
				save_mode_settings(self.modes_file, self.modes)
		window.destroy()

	def save_trans(self):
		save_mode_settings(self.modes_file, self.modes)
		self.changes = False

	def settings_gui(self):
		gui_page = tk.messagebox.showinfo(title='Window options', message='Window options are still under development')

	def settings_update(self, value, name, callback):
		callback(value)
		self.settings[name] = value
		self.changes = True

	def update_sip_cmds(self, s_sip, s_puff, l_sip, l_puff, d_sip, d_puff, override=False):
		cmd_list = [s_sip, s_puff, l_sip, l_puff, d_sip, d_puff]
		if 'left' not in cmd_list:
			msg_left = tk.messagebox.showerror('No left click',
											   message='You have not set up a command for left click. This is not valid. Please set a command for left click.')
		else:
			self.settings_update(s_sip, 's_sip', lambda v: self.arduino.set_callback("short_sip", v))
			self.settings_update(s_puff, 's_puff', lambda v: self.arduino.set_callback("short_puff", v))
			self.settings_update(l_sip, 'l_sip', lambda v: self.arduino.set_callback("long_sip", v))
			self.settings_update(l_puff, 'l_puff', lambda v: self.arduino.set_callback("long_puff", v))
			self.settings_update(d_sip, 'd_sip', lambda v: self.arduino.set_callback("double_sip", v))
			self.settings_update(d_puff, 'd_puff', lambda v: self.arduino.set_callback("double_puff", v))
			if not override:
				default_msg = tk.messagebox.askyesno(title='Update Sip & Puff settings ',
													 message='You have upadated your sip & puff settings. Do you wish to make the settings changes to your default settings?')
				if default_msg:
					self.save(self.settings_file, self.settings)
				else:
					self.changes = False
	def move(self):
		# set up grid
		self.root.grid_columnconfigure(0, weight=2)
		self.root.grid_columnconfigure(1, weight=0)
		self.root.grid_columnconfigure(2, weight=0)
		self.root.grid_columnconfigure(3, weight=0)
		self.root.grid_columnconfigure(4, weight=0)
		self.root.grid_columnconfigure(5, weight=0)
		self.root.grid_columnconfigure(6, weight=0)
		self.root.grid_columnconfigure(7, weight=0)
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
		self.btn_transcription.grid_forget()
		self.l_sips.grid_forget()

	def add_cmd(self, mode, keys, cmd, entry_1, entry_2):
		keys = keys.split()
		if len(keys) > 2 and cmd > '':
			msg_len = tk.messagebox.showinfo('Keyword is too long',
											 'The key word combination you have entered contains more than two words '
											 + 'Please enter a key word combination with no more than two words')
		elif len(keys) > 1 and cmd > '':
			if (keys[0] + keys[1]) in self.commands.modes[mode]:
				msg_key_2 = tk.messagebox.askyesno('Key word exisit',
												   'The key word combination you have entered already exists. '
												   + 'Would you like to replace the functionality of the key word', )
				if msg_key_2:
					self.save_cmd(mode, keys[0], 'multi')
					self.save_cmd(mode, keys[0] + keys[1], cmd)
					entry_1.delete(0, 'end')
					entry_2.delete(0, 'end')
			else:
				self.save_cmd(mode, keys[0], 'multi')
				self.save_cmd(mode, keys[0] + keys[1], cmd)
				entry_1.delete(0, 'end')
				entry_2.delete(0, 'end')

		elif len(keys) > 0 and cmd > '':
			if keys[0] in self.commands.modes[mode]:
				msg_key = tk.messagebox.askyesno('Key word exisit',
												 'The key word you have entered already exists. Would you like to replace the functionality of the key word', )
				if msg_key:
					self.save_cmd(mode, keys[0], cmd)
					entry_1.delete(0, 'end')
					entry_2.delete(0, 'end')

			else:
				self.save_cmd(mode, keys[0], cmd)
				entry_1.delete(0, 'end')
				entry_2.delete(0, 'end')
		else:
			if len(keys) == 0 and cmd == '':
				msg_both = tk.messagebox.showinfo('Too few characters',
												  'The key you have entred has too few characters. Please enter a cmd and a key that has length greater than 1 character')
			elif len(keys) == 0:
				msg_key = tk.messagebox.showinfo('Too few characters in key',
												 'The key you have entred has too few characters. Please enter a cmd that has length greater than 1 character')
			else:
				msg_cmd = tk.messagebox.showinfo('Too few characters in cmd',
												 'The cmd you have entred has too few characters. Please enter a cmd that')

	def save_cmd(self, mode, key, cmd):
		filename = self.path + self.modes[mode].file_name
		self.commands.modes[mode][key] = cmd
		print(str(mode) + str(key) + str(cmd))
		save_add_cmd(filename, key, cmd)

	def create_mode(self, name, echo, entry):
		if name > '' and not self.modes.get(name):
			entry.delete(0, 'end')
			new_filename = self.path + 'settings/cmd_' + str(name) + '.txt'
			# create a new text file to store all cmds in
			file = open(new_filename, 'w+', encoding='utf-8')
			file.close()
			# add to dict and file of modes
			self.modes[name] = Mode(name, 1, new_filename, bool(echo.get))
		elif self.modes.get(name):
			msg_name = tk.messagebox.showinfo('Mode already exsist',
											  'The mode name you have entered already exsists as a mode.'
											  + ' Please enter another mode name')
		else:
			msg_too_few = tk.messagebox.showinfo('Too few characters',
												 'The mode name you have entred has too few characters. ' +
												 'Please give it the name of minimum one character in lenght')

	def panel_view(self):
		# resize and move window
		self.root.geometry('%dx%d+0+%d' % (self.width, 0.1 * self.height, (1 - 0.2) * self.height))

		# frame
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		self.root.grid_columnconfigure(3, weight=12)
		self.root.grid_columnconfigure(4, weight=1)
		self.root.grid_columnconfigure(5, weight=1)
		self.root.grid_columnconfigure(6, weight=1)
		self.root.grid_columnconfigure(7, weight=1)
		self.root.grid_rowconfigure(0, weight=1)
		# reroganize the buttons
		self.btn_exit.grid(row=0, column=0, sticky='nsew')
		self.btn_transcription.grid(row=0, column=2, sticky='nsew')
		self.m_mode.grid(row=0, column=1, sticky='nsew')
		self.btn_move.grid(row=0, column=5, sticky='nsew')
		self.btn_move.config(text='Minimize', command=lambda: self.move())
		self.btn_hide.grid(row=0, column=6, sticky='nsew')
		self.btn_settings.grid(row=0, column=7, sticky='nsew')
		self.l_transcription.grid(row=0, column=3, sticky='nsew')
		self.l_sips.grid(row = 0, column = 4, sticky = 'news')

	def hide(self):
		# hide window so that just the icon on the taskbar is left
		self.root.iconify()

	def change_mode(self, select):
		self.current_mode = select
		self.transcription = self.modes[select].trans
		if not self.transcription:
			self.l_transcription.config(text='Transcription is off')
			self.off_transcript()
		else:
			self.on_transcript()

		print('Update mode to %s' % select)

	def update_transcript(self, line):
		if self.transcription:
			self.l_transcription.config(text=line)
		else:
			self.l_transcription.config(text='Transcription is off')

	def sip_transcription (self, trans):
		self.l_sips.config(text = trans)

	def off_transcript(self):
		self.l_transcription.config(text='Transcription is off')
		self.transcription = False
		self.btn_transcription.config(text='ON', command=self.on_transcript)

	def on_transcript(self):
		self.transcription = True
		self.l_transcription.config(text='Transcription is on')
		self.btn_transcription.config(text='OFF', command=self.off_transcript)

	def update_trans(self, mode_list, index):
		self.changes = True
		for i in range(len(index)):
			self.modes[mode_list[i]].trans = index[i].get()
			print(str(mode_list[i]) + ';' + str(index[i].get()))

	def factory_settings(self):
		factory_msg = tk.messagebox.askyesno(title='Reset to factory settings',
											 message='Do you wish to reset the app to factory settings?\n All your personalised settings will be lost.')
		if factory_msg:
			self.settings = setting_config(self.path + 'DefaultSettingsGUI.txt')
			save_changed_settings(self.settings_file, self.settings)


def save_changed_settings(filename, dict_set):
	print('save changes runs')
	file = open(filename, 'w', encoding='utf-8')
	li = dict_set.items()
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
	file.write(key + ' ' + str(value) + '\n')
	file.close()


class Mode:
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
		mode_dict[name] = (Mode(name, transcript, track_file, echo))
	file.close()

	return mode_dict


def save_mode_settings(filename, modes_dict):
	file = open(filename, 'w', encoding='utf-8')
	for key in modes_dict:
		mode = modes_dict[key]
		file.write(mode.name + ';' + str(mode.trans) + ';' + mode.file_name + ';' + str(mode.echo) + '\n')
	file.close()


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
	print(settings_current)
	return settings_current


if __name__ == "__main__":
	stt = None #SpeechToTextController(None, lambda t, f: print(t))
	arduino = ArduinoController()
	# arduino = None
	commands = CommandController()
	app = GUI("", 'settings/GUISetUp.txt', 'settings/settingsGUI.txt', arduino, commands, stt)
	app.start()
