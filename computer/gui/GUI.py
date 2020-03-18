import tkinter as tk
import tkinter.messagebox
from time import sleep

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
		self.arduino.set_gui_change_mode(lambda: self.sip_change_mode(self.previous_mode))
		self.speech_to_text = speech_to_text
		self.path = path
		self.modes_file = path + modes_file
		self.settings_file = path + settings_file

		self.modes = mode_dict_set_up(self.modes_file)
		self.settings = setting_config(self.settings_file)

		self.sip_transcription_thread_id = 0

		for key in self.modes:
			self.commands.load_cmds(key, path + self.modes[key].file_name)

		self.update_sip_cmds(self.settings['s_sip'], self.settings['s_puff'], self.settings['l_sip'],
							 self.settings['l_puff'], self.settings['d_sip'], self.settings['d_puff'], True)

		self.root = None
		self.width = None
		self.height = None
		self.changes = False
		self.transcription = self.modes[self.settings['start_mode']].trans
		self.echo = self.modes[self.settings['start_mode']].echo
		self.current_mode = self.settings['start_mode']
		self.previous_mode = self.settings['start_mode']

		# set up root window
		# self.root = tk.Tk()
		self.root = ThemedTk(theme="arc", themebg=True)

		self.root.title('Monica')
		self.width = self.root.winfo_screenwidth()
		self.height = self.root.winfo_screenheight()
		self.arduino.set_bounds(self.width, self.height)
		self.root.geometry('%dx%d+%d+%d' % (
			self.width, 0.1 * self.height, 0,
			self.height - 0.2 * self.height))  # note: 0,0 cooordiantes is top left corner
		self.root.attributes('-topmost', True)

		# Set up all button and labels (doesn't actually grid them - that is done as panel method)
		# Menu buttons
		self.btn_exit = ttk.Button(self.root, text='Exit', width=8)
		self.btn_exit['command'] = lambda: self.close_program()  # note: when we turn this to an app change to root.quit

		self.btn_move = ttk.Button(self.root, text='Minimize', width=8)
		self.btn_move['command'] = lambda: self.move()

		self.btn_transcription = ttk.Button(self.root, text='something', command = self.trans_toggle, width=8)


		self.btn_hide = ttk.Button(self.root, text='Hide', width=8)
		self.btn_hide['command'] = lambda: self.hide()

		self.btn_settings = ttk.Button(self.root, text='Settings', width=8)
		self.btn_settings['command'] = lambda: self.settings_start()

		self.btn_echo = ttk.Button(self.root, width = 8, command = self.echo_toggle)
		if self.echo:
			self.btn_echo.config(text  = ' Echo:\nON')
		else:
			self.btn_echo.config(text=' Echo:\nOFF')


		# tracription labels
		self.l_sips = ttk.Label(self.root, text='Sip & Puff', foreground='purple', anchor='center', width=12)

		self.l_transcription = ttk.Label(self.root, text='Transcript runs here', anchor='nw', background='black',
										 foreground='white', width=80, wraplength=0.6 * self.width)

		# Set up trascription button label
		if self.transcription:
			self.btn_transcription.config(text = 'Panel trans:\nON')
			self.l_transcription.config(text = 'Transcription is on')
		else:
			self.btn_transcription.config(text='Panel trans:\nOFF')
			self.l_transcription.config(text='Transcription is OFF')

		# mode menu
		max_len = len(max(list(self.modes.keys()), key=len))
		self.m_current_mode = tk.StringVar()
		self.m_current_mode.set(self.current_mode)
		self.m_mode = ttk.OptionMenu(self.root, self.m_current_mode, self.current_mode, *list(self.modes.keys()),
									 command=self.change_mode)
		self.m_mode.config(width=max_len)
		# Call panel view method to place all widgets in the window
		self.panel_view()


		self.root.protocol('WM_DELETE_WINDOW', self.close_program)

	def panel_view(self):
		# resize and move window
		self.root.geometry('%dx%d+0+%d' % (self.width, 0.1 * self.height, (1 - 0.2) * self.height))

		# frame
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		self.root.grid_columnconfigure(3, weight=1)
		self.root.grid_columnconfigure(4, weight=10)
		self.root.grid_columnconfigure(5, weight=2)
		self.root.grid_columnconfigure(6, weight=1)
		self.root.grid_columnconfigure(7, weight=1)
		self.root.grid_columnconfigure(8, weight=1)
		self.root.grid_rowconfigure(0, weight=1)

		# reroganize the buttons
		self.btn_exit.grid(row=0, column=0, sticky='nsew')
		self.m_mode.grid(row=0, column=1, sticky='nsew')
		self.btn_echo.grid(row = 0, column = 2, sticky = 'nsew')
		self.btn_transcription.grid(row=0, column=3, sticky='nsew')
		self.l_transcription.grid(row=0, column=4, sticky='nsew')
		self.l_sips.grid(row=0, column=5, sticky='news')
		self.btn_move.grid(row=0, column=6, sticky='nsew')
		self.btn_move.config(text='Minimize', command=lambda: self.move())
		self.btn_hide.grid(row=0, column=7, sticky='nsew')
		self.btn_settings.grid(row=0, column=8, sticky='nsew')


	def move(self):
		# set up grid
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(1, weight=0)
		self.root.grid_columnconfigure(2, weight=0)
		self.root.grid_columnconfigure(3, weight=0)
		self.root.grid_columnconfigure(4, weight=0)
		self.root.grid_columnconfigure(5, weight=0)
		self.root.grid_columnconfigure(6, weight=0)
		self.root.grid_columnconfigure(7, weight=0)
		self.root.grid_columnconfigure(8, weight=0)
		self.root.grid_rowconfigure(0, weight=1)

		# resize and move window
		self.root.geometry(
			'%dx%d+0+0' % (0.1 * self.width, 0.3 * self.height))  # note: 0,0 cooordiantes is top left corner
		# reorganize the buttons
		self.btn_exit.grid(row=0, column=0, sticky='news')
		self.m_mode.grid(row=1, column=0, sticky='news')
		self.btn_echo.grid(row = 2, column = 0, sticky ='news')
		self.btn_move.grid(row=3, column=0, sticky='news')
		self.btn_move.config(text='Panel View', command=lambda: self.panel_view())
		self.btn_settings.grid(row=5, column=0, sticky='news')
		self.btn_hide.grid(row=4, column=0, sticky='news')

		# hide the trascription
		self.l_transcription.grid_forget()
		self.btn_transcription.grid_forget()
		self.l_sips.grid_forget()

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

	def settings_joy(self):
		joy_page = tk.Toplevel(self.main_menu)
		joy_page.title('Settings Joystick')

		joy_page.columnconfigure(0, weight=1)
		joy_page.rowconfigure(0, weight=1)

		frame = tk.Frame(master=joy_page)
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.grid(row=0, column=0, sticky='news')

		# set size of dead zone
		l_speed = ttk.Label(master=frame, text='Dead zone size')
		l_speed.grid(row=6, column=0, columnspan=2, sticky='news')
		l_smin = ttk.Label(master=frame, text='1').grid(row=7, column=0, sticky='nes')
		l_smax = ttk.Label(master=frame, text='20').grid(row=7, column=2, sticky='nws')
		dead_zone = ttk.Scale(master=frame, from_=1, to=20, orient='horizontal')
		dead_zone.set(self.settings['dead_zone'])  # update with settings value
		dead_zone.bind("<ButtonRelease>",
					   lambda e: self.settings_update(dead_zone.get(), 'dead_zone', self.arduino.set_mouse_dead_zone))
		dead_zone.grid(row=7, column=1, columnspan=1, sticky='news')

		# set the speed of the cursor
		l_speed = ttk.Label(master=frame, text='Cursor speed')
		l_speed.grid(row=0, column=0, columnspan=2, sticky='news')
		l_smin = ttk.Label(master=frame, text='1').grid(row=1, column=0, sticky='nes')
		l_smax = ttk.Label(master=frame, text='150').grid(row=1, column=2, sticky='nws')
		slider_speed = ttk.Scale(master=frame, from_=1, to=150, orient='horizontal')
		slider_speed.set(self.settings['Cursor_speed'])  # update with settings value
		slider_speed.grid(row=1, column=1, columnspan=1, sticky='news')
		slider_speed.bind("<ButtonRelease>", lambda event: self.settings_update(slider_speed.get(), 'Cursor_speed',
																				self.arduino.set_mouse_speed))

		# Set Up High Speed Threshold
		l_high_speed = ttk.Label(master=frame, text='High Speed Threshold')
		l_high_speed.grid(row=4, column=0, columnspan=3, sticky='ews')
		l_min = ttk.Label(master=frame, text='0').grid(row=5, column=0, sticky='nes')
		l_mix = ttk.Label(master=frame, text='512').grid(row=5, column=2, sticky='nws')
		slider_high_speed = ttk.Scale(master=frame, from_=0, to=512, orient='horizontal', )
		slider_high_speed.set(self.settings['high_speed'])  # update with settings value
		slider_high_speed.grid(row=5, column=1, sticky='news')
		slider_high_speed.bind("<ButtonRelease>",
							   lambda event: self.settings_update(slider_high_speed.get(), 'high_speed',
																  self.arduino.set_mouse_scaling_threshold))
		# Save Button
		btn_save_js = ttk.Button(master=frame, text='Save Settings as Default',
								 command=lambda: self.save(self.settings_file, self.settings))
		btn_save_js.grid(row=8, column=0, columnspan=3)
		# Close Button
		btn_close_js = ttk.Button(master=frame, text='Close Joystick Settings',
								  command=lambda: self.close_settings('Joystick', joy_page))
		btn_close_js.grid(row=9, column=0, columnspan=3, sticky='news')
		joy_page.protocol('WM_DELETE_WINDOW', lambda: self.close_settings('Joystick', joy_page))

	def settings_sip(self):
		page = tk.Toplevel(self.main_menu)
		page.title(' Advanced Settings Sip & Puff')

		page.columnconfigure(0, weight=1)
		page.rowconfigure(0, weight=1)

		frame = tk.Frame(master=page)
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.grid(row=0, column=0, sticky='news')

		btn_advanced = ttk.Button(master=frame, text='Advanced Sip & Puff settings', command=self.advanced_settings_sip)
		btn_advanced.grid(row=5, column=1, columnspan=2)

		# Set commands to sip and puffs
		cmd_list = self.arduino.functions.keys()
		print(cmd_list)
		l_sip_set = ttk.Label(master=frame, text='Set up the sip and puff commands to desired action')
		l_sip_set.grid(row=0, column=0, columnspan=2)
		# Short Sip
		l_s_sip = ttk.Label(master=frame, text='Single Sip')
		l_s_sip.grid(row=1, column=0, columnspan=1)

		s_sip_var = tk.StringVar()
		s_sip_var.set(self.settings['s_sip'])
		menu_s_sip = ttk.OptionMenu(frame, s_sip_var, self.settings['s_sip'], *cmd_list, command=self.sip_changes)
		menu_s_sip.grid(row=1, column=1)

		# Short puff
		l_s_puff = ttk.Label(master=frame, text='Single Puff')
		l_s_puff.grid(row=1, column=2, columnspan=1)

		s_puff_var = tk.StringVar()
		s_puff_var.set(self.settings['s_puff'])
		menu_s_puff = ttk.OptionMenu(frame, s_puff_var, self.settings['s_puff'], *cmd_list, command=self.sip_changes)
		menu_s_puff.grid(row=1, column=3, columnspan=1)

		# Double Sip
		l_d_sip = ttk.Label(master=frame, text='Double Sip')
		l_d_sip.grid(row=2, column=0, columnspan=1)

		d_sip_var = tk.StringVar()
		d_sip_var.set(self.settings['d_sip'])
		menu_d_sip = ttk.OptionMenu(frame, d_sip_var, self.settings['d_sip'], *cmd_list, command=self.sip_changes)
		menu_d_sip.grid(row=2, column=1, columnspan=1)

		# Double Puff
		l_d_puff = ttk.Label(master=frame, text='Double Puff')
		l_d_puff.grid(row=2, column=2, columnspan=1)

		d_puff_var = tk.StringVar()
		d_puff_var.set(self.settings['d_puff'])
		menu_d_puff = ttk.OptionMenu(frame, d_puff_var, self.settings['d_puff'], *cmd_list, command=self.sip_changes)
		menu_d_puff.grid(row=2, column=3, columnspan=1)

		# Long Sip
		l_l_sip = ttk.Label(master=frame, text='Long Sip')
		l_l_sip.grid(row=3, column=0, columnspan=1)

		l_sip_var = tk.StringVar()
		l_sip_var.set(self.settings['l_sip'])
		menu_l_sip = ttk.OptionMenu(frame, l_sip_var, self.settings['l_sip'], *cmd_list, command=self.sip_changes)
		menu_l_sip.grid(row=3, column=1, columnspan=1)

		l_l_puff = ttk.Label(master=frame, text='Long Puff')
		l_l_puff.grid(row=3, column=2, columnspan=1)

		l_puff_var = tk.StringVar()
		l_puff_var.set(self.settings['l_puff'])
		menu_l_puff = ttk.OptionMenu(frame, l_puff_var, self.settings['l_puff'], *cmd_list, command=self.sip_changes)
		menu_l_puff.grid(row=3, column=3, columnspan=1)

		# Save Button
		btn_save_sp = ttk.Button(master=frame, text='Save Settings',
								 command=lambda: self.update_sip_cmds(s_sip_var.get(), s_puff_var.get(),
																	  l_sip_var.get(), l_puff_var.get(),
																	  d_sip_var.get(), d_puff_var.get()))
		btn_save_sp.grid(row=4, column=1, columnspan=2)

		# Close Button
		btn_close_sp = ttk.Button(master=frame, text='Close Sip & Puff Settings',
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
		page.columnconfigure(0, weight=1)
		page.rowconfigure(0, weight=1)

		frame = tk.Frame(master=page)
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.grid(row=0, column=0, sticky='news')

		# Sip
		l_sip = ttk.Label(master=frame, text='Sip Settings')
		l_sip.grid(row=0, column=0, columnspan=4)

		# set up pressure sensetivity
		sip_l_pressure = ttk.Label(master=frame, text='Pressure Threshold')
		sip_l_pressure.grid(row=1, column=0, columnspan=3, sticky='w')

		sip_l_pmin = ttk.Label(master=frame, text='10').grid(row=2, column=0, sticky='nes')
		sip_l_pmax = ttk.Label(master=frame, text='400').grid(row=2, column=3, sticky='nws')

		sip_slider_pressure = ttk.Scale(master=frame, from_=10, to=400, orient='horizontal')
		sip_slider_pressure.set(self.settings['sip_pressure_threshold'])  # update with settings value
		sip_slider_pressure.grid(row=2, column=1, columnspan=2, sticky='news')
		sip_slider_pressure.bind("<ButtonRelease>",
								 lambda event: self.settings_update(sip_slider_pressure.get(), 'sip_pressure_threshold',
																	self.arduino.set_puff_threshold))

		# Length of long
		sip_l_long_time = ttk.Label(master=frame, text='Length of Long pressure')
		sip_l_long_time.grid(row=3, column=0, columnspan=4, sticky='w')
		sip_l_tl_min = ttk.Label(master=frame, text='0.1').grid(row=4, column=0, sticky='nes')
		sip_l_tl_max = ttk.Label(master=frame, text='2').grid(row=4, column=3, sticky='nws')
		sip_slider_long_time = ttk.Scale(master=frame, from_=0.1, to=2, orient='horizontal')
		sip_slider_long_time.set(self.settings['sip_long_time'])  # update with settings value
		sip_slider_long_time.grid(row=4, column=1, columnspan=2, sticky='news')
		sip_slider_long_time.bind("<ButtonRelease>",
								  lambda event: self.settings_update(sip_slider_long_time.get(), 'sip_long_time',
																	 self.arduino.set_long_sip_time))

		# Length of short
		sip_l_short_time = ttk.Label(master=frame, text='Length of Short pressure')
		sip_l_short_time.grid(row=5, column=0, columnspan=4, sticky='w')
		sip_l_tl_min = ttk.Label(master=frame, text='0.1').grid(row=6, column=0, sticky='nes')
		sip_l_tl_max = ttk.Label(master=frame, text='1').grid(row=6, column=3, sticky='nws')
		sip_slider_short_time = ttk.Scale(master=frame, from_=0.1, to=1, orient='horizontal')
		sip_slider_short_time.set(self.settings['sip_short_time'])  # update with settings value
		sip_slider_short_time.grid(row=6, column=1, columnspan=2, sticky='news')
		sip_slider_short_time.bind("<ButtonRelease>",
								   lambda event: self.settings_update(sip_slider_short_time.get(), 'sip_short_time',
																	  self.arduino.set_short_sip_time))

		# Double time
		sip_l_d_time = ttk.Label(master=frame, text='Double Time')
		sip_l_d_time.grid(row=7, column=0, columnspan=3, sticky='w')
		sip_l_dmin = ttk.Label(master=frame, text='0.1').grid(row=8, column=0, sticky='nes')
		sip_l_dmax = ttk.Label(master=frame, text='1').grid(row=8, column=3, sticky='nws')
		slider_sip_d_time = ttk.Scale(master=frame, from_=0.1, to=1, orient='horizontal')
		slider_sip_d_time.set(self.settings['sip_double_time'])  # update with settings value
		slider_sip_d_time.grid(row=8, column=1, columnspan=2, sticky='news')
		slider_sip_d_time.bind("<ButtonRelease>",
							   lambda event: self.settings_update(slider_sip_d_time.get(), 'sip_double_time',
																  self.arduino.set_puff_threshold))

		# Puff
		l_puff = ttk.Label(master=frame, text='Puff Settings')
		l_puff.grid(row=0, column=4, columnspan=4)

		# set up pressure sensetivity
		puff_l_pressure = ttk.Label(master=frame, text='Pressure Threshold')
		puff_l_pressure.grid(row=1, column=4, columnspan=3, sticky='news')
		puff_l_pmin = ttk.Label(master=frame, text='10').grid(row=2, column=4, sticky='nes')
		puff_l_pmax = ttk.Label(master=frame, text='400').grid(row=2, column=7, sticky='nws')
		puff_slider_pressure = ttk.Scale(master=frame, from_=10, to=400, orient='horizontal')
		puff_slider_pressure.set(self.settings['puff_pressure_threshold'])  # update with settings value
		puff_slider_pressure.grid(row=2, column=5, columnspan=2, sticky='news')
		puff_slider_pressure.bind("<ButtonRelease>",
								  lambda event: self.settings_update(sip_slider_pressure.get(),
																	 'sip_pressure_threshold',
																	 self.arduino.set_puff_threshold))

		# Length of long
		puff_l_long_time = ttk.Label(master=frame, text='Length of Long pressure')
		puff_l_long_time.grid(row=3, column=4, columnspan=4, sticky='news')
		puff_l_tl_min = ttk.Label(master=frame, text='0.1').grid(row=4, column=4, sticky='nes')
		puff_l_tl_max = ttk.Label(master=frame, text='2').grid(row=4, column=7, sticky='nws')
		puff_slider_long_time = ttk.Scale(master=frame, from_=0.1, to=2, orient='horizontal')
		puff_slider_long_time.set(self.settings['puff_long_time'])  # update with settings value
		puff_slider_long_time.grid(row=4, column=5, columnspan=2, sticky='news')
		puff_slider_long_time.bind("<ButtonRelease>",
								   lambda event: self.settings_update(puff_slider_long_time.get(), 'puff_long_time',
																	  self.arduino.set_long_puff_time))

		# Length of short
		puff_l_short_time = ttk.Label(master=frame, text='Length of Short pressure')
		puff_l_short_time.grid(row=5, column=4, columnspan=4, sticky='news')
		puff_l_tl_min = ttk.Label(master=frame, text='0.1').grid(row=6, column=4, sticky='nes')
		puff_l_tl_max = ttk.Label(master=frame, text='1').grid(row=6, column=7, sticky='nws')
		puff_slider_short_time = ttk.Scale(master=frame, from_=0.1, to=1, orient='horizontal')
		puff_slider_short_time.set(self.settings['puff_short_time'])  # update with settings value
		puff_slider_short_time.grid(row=6, column=5, columnspan=2, sticky='news')
		puff_slider_short_time.bind("<ButtonRelease>",
									lambda event: self.settings_update(puff_slider_short_time.get(), 'puff_short_time',
																	   self.arduino.set_short_puff_time))

		# Double time
		puff_l_d_time = ttk.Label(master=frame, text='Double Time')
		puff_l_d_time.grid(row=7, column=4, columnspan=3, sticky='news')
		puff_l_dmin = ttk.Label(master=frame, text='0.1').grid(row=8, column=4, sticky='nes')
		puff_l_dmax = ttk.Label(master=frame, text='1').grid(row=8, column=7, sticky='nws')
		slider_puff_d_time = ttk.Scale(master=frame, from_=0.1, to=1, orient='horizontal')
		slider_puff_d_time.set(self.settings['puff_double_time'])  # update with settings value
		slider_puff_d_time.grid(row=8, column=5, columnspan=2, sticky='news')
		slider_puff_d_time.bind("<ButtonRelease>",
								lambda event: self.settings_update(slider_puff_d_time.get(), 'puff_double_time',
																   self.arduino.set_puff_threshold))

		# Save Button
		btn_save_sp = ttk.Button(master=frame, text='Save Advanced Settings as Default',
								 command=lambda: self.save(self.settings_file, self.settings))
		btn_save_sp.grid(row=9, column=3, columnspan=2)

		# Close Button
		btn_close_sp = ttk.Button(master=frame, text='Close Advanced Sip & Puff Settings',
								  command=lambda: self.close_settings('Sip & Puff', page))
		btn_close_sp.grid(row=10, column=3, columnspan=2, sticky='news')
		page.protocol('WM_DELETE_WINDOW', lambda: self.close_settings('Sip & Puff', page))

	def settings_speech2text(self):
		page = tk.Toplevel(self.main_menu)
		page.title('Settings Speech to text')

		page.columnconfigure(0, weight=1)
		page.rowconfigure(0, weight=1)

		frame = tk.Frame(master=page)
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.grid(row=0, column=0, sticky='news')
		# Chose mode to start program with
		l_startm = ttk.Label(master=frame, text="Set default mode at start up: ")
		l_startm.grid(row=0, column=0, columnspan=2)

		start_mode = tk.StringVar()
		start_mode.set(self.settings['start_mode'])
		m_select_start = ttk.OptionMenu(frame, start_mode, self.settings['start_mode'], *list(self.modes.keys()),
										command=lambda select: self.settings_update(select, 'start_mode'))
		m_select_start.grid(row=1, column=0, columnspan=2)

		btn_set_start = ttk.Button(master=frame, text='Make default on Start up',
								   command=lambda: self.save(self.settings_file, self.settings))
		btn_set_start.grid(row=2, column=0, columnspan=2)

		# Selection to trun transcription on/off
		l_trans_onoff = ttk.Label(master=frame, text='transcription on/off')
		l_trans_onoff.grid(row=3, column=0, columnspan=1)

		modes_list = list(self.modes.keys())

		# make check box selection trans
		check_boxes = ttk.Frame(frame)
		check_boxes.grid(row=4, column=0, columnspan=1, sticky='news')
		index_t = list(range(len(modes_list)))
		for i in range(0, len(self.modes.keys())):
			index_t[i] = tk.IntVar()
			print(self.modes[modes_list[i]].trans)
			index_t[i].set(self.modes[modes_list[i]].trans)
			ttk.Checkbutton(master=check_boxes, text=modes_list[i], var=index_t[i],
							command= self.update_trans).grid(row=i, column=0, sticky = 'w')

		# Selection to trun echo on/off
		l_trans_onoff = ttk.Label(master=frame, text='Echo on/off')
		l_trans_onoff.grid(row=3, column=1, columnspan=1)

		# make check box selection echo
		check_boxes = ttk.Frame(frame)
		check_boxes.grid(row=4, column=1, columnspan=1, sticky='news')
		modes_list = list(self.modes.keys())
		index_e = list(range(len(modes_list)))
		for i in range(0, len(self.modes.keys())):
			index_e[i] = tk.IntVar()
			print(self.modes[modes_list[i]].echo)
			index_e[i].set(self.modes[modes_list[i]].echo)
			ttk.Checkbutton(master=check_boxes, text=modes_list[i], var=index_e[i],
							command= self.update_trans).grid(row=i, column=0, sticky='w')

		btn_update_trans_set = ttk.Button(master=frame, text='Update transcription details to default', command=lambda: self.save_trans(modes_list, index_e, index_t))
		btn_update_trans_set.grid(row=5, column=0, columnspan=2)

		# Advanced mode settings
		btn_mode_adv = ttk.Button(master=frame, text='Advance Mode Settings', command=self.additional_mode)
		btn_mode_adv.grid(row=6, column=0, columnspan=2)
		# Close Button
		btn_close_stt = ttk.Button(master=frame, text='Close Speech to Text Settings',
								   command=lambda: self.save_sip(page, modes_list, index_e, index_t))
		btn_close_stt.grid(row=7, column=0, columnspan=2, sticky='news')

		page.protocol('WM_DELETE_WINDOW', lambda: self.save_sip(page, modes_list, index_e, index_t))

	def additional_mode(self):
		page = tk.Toplevel()
		page.title('Advanced mode Settings')

		page.columnconfigure(0, weight=1)
		page.rowconfigure(0, weight=1)
		page.rowconfigure(1, weight=1)

		frame = tk.Frame(master=page)
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.grid(row=0, column=0, sticky='news')

		# Create New Mode
		l_new_mode = ttk.Label(master = frame, text = 'Add new mode')
		l_new_mode.grid(row = 0, column = 0, columnspan = 2)
		l_cmd_add_mode = ttk.Label(master=frame, text='Name of mode:')
		l_cmd_add_mode.grid(row=1, column=0)

		txt_box_mode = ttk.Entry(master=frame)
		txt_box_mode.grid(row=1, column=1)

		new_echo = tk.IntVar
		check_echo = ttk.Checkbutton(master=frame, text='Echo', var=new_echo)
		check_echo.grid(row=2, column=0, columnspan=1, sticky='w')

		new_trans = tk.IntVar
		check_trans = ttk.Checkbutton(master=frame, text='Transcription', var=new_trans)
		check_trans.grid(row=2, column=1, columnspan=1, sticky='w')



		btn_create_mode = ttk.Button(master=frame, text='Add new mode',
									 command=lambda: self.create_mode(txt_box_mode.get(), new_echo, new_trans, txt_box_mode))
		btn_create_mode.grid(row=3, column=0, columnspan=2)

		# Add new command to mode
		l_cmd_mode = ttk.Label(master=frame, text='Add cmd to mode:')
		l_cmd_mode.grid(row = 4, column=0, columnspan=2)

		current_modes = tk.StringVar()
		current_modes.set(self.current_mode)
		m_select_modeadd = ttk.OptionMenu(frame, current_modes, self.current_mode, *list(self.modes.keys()))
		m_select_modeadd.grid(row=5, column=0, columnspan=2)

		l_cmd_key_word = ttk.Label(master=frame, text='Key word to cmd:')
		l_cmd_key_word.grid(row=6, column=0)

		txt_key_word = ttk.Entry(master=frame)
		txt_key_word.grid(row=6, column=1)

		l_cmd = ttk.Label(master=frame, text='Desired cmd:')
		l_cmd.grid(row=7, column=0)

		txt_cmd = ttk.Entry(master=frame)
		txt_cmd.grid(row=7, column=1)

		btn_addmode = ttk.Button(master=frame, text='Add command',
								 command=lambda: self.add_cmd(current_modes.get(), txt_key_word.get(), txt_cmd.get(),
															  txt_key_word, txt_cmd))
		btn_addmode.grid(row=8, column=0, columnspan=2)

		#Show all cmds currently in each mode

		l_cmd_list = ttk.Label(master = frame, text = 'Edit current list of cmds')
		l_cmd_list.grid(row = 9, column = 0, columnspan = 2)
		# Select mode to look at
		show_modes = tk.StringVar()
		show_modes.set(self.current_mode)
		m_select_modeadd = ttk.OptionMenu(frame, show_modes, self.current_mode, *list(self.modes.keys()), command = lambda mode: self.update_list_cmds(mode, cmd_list))
		m_select_modeadd.grid(row=10, column=0, columnspan=2)

		#Set up listbox
		frame1 = tk.Frame(master=frame)
		frame1.columnconfigure(0, weight=1)
		frame1.rowconfigure(0, weight=1)
		frame1.grid(row=11, column=0, columnspan = 2,sticky='news')

		cmd_list = tk.Listbox(master = frame1)
		cmd_list.grid(row = 0, column = 0, sticky = 'news')
		self.update_list_cmds(self.current_mode, cmd_list)

		cmd_list_scroll = ttk.Scrollbar(master=frame1)
		cmd_list_scroll.grid(row=0, column=1, sticky = 'nws')

		cmd_list.config(yscrollcommand = cmd_list_scroll.set)
		cmd_list_scroll.config(command = cmd_list.yview)

		# delete button
		cmd_list_delete = ttk.Button(master = frame, text = 'Delete cmd', command = lambda: self.delete_cmd(cmd_list.curselection(), show_modes.get(), cmd_list))
		cmd_list_delete.grid(row = 12, column = 0, columnspan = 2)

		#close button


	def delete_cmd(self, index, mode, cmd_list):
		index = index[0]
		key = list(self.commands.modes[mode])[index]
		msg = tk.messagebox.askokcancel('Delete cmd', 'You are about to delete the cmd for: %s. '%(str(key)))
		if msg:
			cmd_list.delete(index)
			del self.commands.modes[mode][key]
			filename = self.path + self.modes[mode].file_name
			save_cmd_dicts(filename, self.commands.modes[mode])

	def update_list_cmds(self,mode, cmd_list):
		cmd_list.delete(0, 'end')
		cmd_dict = self.commands.modes[mode]
		for key in cmd_dict:
			cmd_list.insert('end', key + ' : ' + cmd_dict[key])

	def start(self):
		# used to start the program from the main filed
		self.root.mainloop()
		print("closed gui")

	def close_program(self):
		# used to close all different threads
		print('Program should do complete exit')
		if self.arduino != None:
			self.arduino.stop()
		if self.speech_to_text != None:
			self.speech_to_text.stop()
		self.root.destroy()

	def close_settings(self, name, window):
		if (self.changes):
			default_msg = tk.messagebox.askyesno(title='Update %s settings ' % name,
												 message='You have unsaved changes. Do you wish to make the settings changes to your default settings?')
			if default_msg:
				self.save(self.settings_file, self.settings)
		window.destroy()

	def save_sip(self, window, mode_list, index_e, index_t):
		if self.changes:
			msg = tk.messagebox.askyesno(title='Unsaved Changes',
										 message='There are unsaved settings changes. Do you wish to save these to default settings?')
			if msg:
				self.changes = False
				save_changed_settings(self.settings_file, self.settings)
				self.save_trans(mode_list, index_e, index_t)
		window.destroy()

	def save_trans(self, mode_list, index_e, index_t):
		for i in range(len(index_t)):
			self.modes[mode_list[i]].trans = index_t[i].get()
			print('trans: '+str(mode_list[i]) + ';' + str(index_t[i].get()))
			self.modes[mode_list[i]].echo = index_e[i].get()
			print('echo: ' + str(mode_list[i]) + ';' + str(index_e[i].get()))

		save_mode_settings(self.modes_file, self.modes)
		select = self.current_mode
		self.current_mode = self.previous_mode
		self.change_mode(select)
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

	def add_cmd(self, mode, keys, cmd, entry_1, entry_2):
		keys = keys.split()
		if len(keys) > 2 and cmd > '':
			msg_len = tk.messagebox.showinfo('Keyword is too long',
											 'The key word combination you have entered contains more than two words '
											 + 'Please enter a key word combination with no more than two words')
		elif len(keys) > 1 and cmd > '':
			if (keys[0] + keys[1]) in self.commands.modes[mode]:
				msg_key_2 = tk.messagebox.askyesno('Key word exist',
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

	def create_mode(self, name, echo, trans,entry):
		if name > '' and not self.modes.get(name):
			entry.delete(0, 'end')
			new_filename = self.path + 'settings/cmd_' + str(name) + '.txt'
			# create a new text file to store all cmds in
			file = open(new_filename, 'w+', encoding='utf-8')
			file.close()
			# add to dict and file of modes
			self.modes[name] = Mode(name, bool(echo.get), new_filename, bool(trans.get))
		elif self.modes.get(name):
			msg_name = tk.messagebox.showinfo('Mode already exsist',
											  'The mode name you have entered already exsists as a mode.'
											  + ' Please enter another mode name')
		else:
			msg_too_few = tk.messagebox.showinfo('Too few characters',
												 'The mode name you have entred has too few characters. ' +
												 'Please give it the name of minimum one character in lenght')

	def sip_changes(self, _):
		self.changes = True

	def hide(self):
		# hide window so that just the icon on the taskbar is left
		self.root.iconify()

	def change_mode(self, select):
		self.previous_mode = self.current_mode
		self.current_mode = select
		self.transcription = self.modes[select].trans
		self.echo = self.modes[select].echo
		if not self.transcription:
			self.l_transcription.config(text='Transcription is off')
			self.btn_transcription.config(text = 'Panel Trans:\nOFF')
		else:
			self.btn_transcription.config(text='Panel Trans:\nON')
		if self.echo:
			self.btn_echo.config (text = 'Echo:\nON')
		else:
			self.btn_echo.config(text='Echo:\nOFF')

		print('Update mode to %s' % select)

	def sip_change_mode(self, mode):
		self.change_mode(mode)
		self.m_current_mode.set(mode)

	def update_transcript(self, line):
		if self.transcription:
			self.l_transcription.config(text=line)
		else:
			self.l_transcription.config(text='Transcription is off')

	def sip_transcription(self, trans):
		self.l_sips.config(text=trans)
		self.sip_transcription_thread_id = self.sip_transcription_thread_id + 1
		Thread(target=self.sip_transcription_timeout, args=(self.sip_transcription_thread_id,)).start()

	def sip_transcription_timeout(self, id):
		sleep(2)
		if self.sip_transcription_thread_id == id:
			self.l_sips.config(text="-")


	def trans_toggle(self):
		if self.transcription:
			self.btn_transcription.config(text='Panel trans:\nOFF')
			self.l_transcription.config(text = 'Transcription is off')
			self.transcription = False
		else:
			self.btn_transcription.config(text='Panel trans:\nON')
			self.l_transcription.config(text = 'Transcription is on')
			self.transcription = True

	def echo_toggle(self):
		if self.echo:
			self.btn_echo.config(text = 'Echo:\nOFF')
			self.echo = False
		else:
			self.btn_echo.config(text='Echo:\nON')
			self.echo = True
		print('Echo: ' + str(self.echo))

	def update_trans(self):
		self.changes = True


	def factory_settings(self):
		factory_msg = tk.messagebox.askyesno(title='Reset to factory settings',
											 message='Do you wish to reset the app to factory settings?\n All your personalised settings will be lost.')
		if factory_msg:
			self.settings = setting_config(self.path + 'DefaultSettingsGUI.txt')
			save_changed_settings(self.settings_file, self.settings)

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

def save_cmd_dicts(filename_mode, dict):
	file = open(filename_mode, 'w', encoding='utf-8')
	for key in dict:
		file.write(key + ' ' + dict[key] + '\n')
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
	stt = None  # SpeechToTextController(None, lambda t, f: print(t))
	arduino = ArduinoController()
	# arduino = None
	commands = CommandController()
	app = GUI("", 'settings/GUISetUp.txt', 'settings/settingsGUI.txt', arduino, commands, stt)
	app.start()
