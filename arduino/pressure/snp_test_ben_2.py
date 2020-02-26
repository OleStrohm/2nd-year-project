import serial
import mouse

ser = serial.Serial('COM5', 9600)
input =
#active range is <1 or >4
is_holding = False
while True: #need data to give me long, short, right or left. if data comes in every 150ms
    #identify the command. right or left click (left for sip, right for puff)
    if input > 4:
        click_type = "left"
    elif input < 1:
        click_type = "right"
    elif input >= 4 or input <= 1:
        continue #if not in active range, keep running while loop
    # INSERT CODE HERE to identify the length of the command
    if click_length == "long":
        if is_holding == False and click_type == "left":
            is_holding = True
            mouse.press()
        elif is_holding == True and click_type == "left":
            is_holding == False
            mouse.release()
        elif click_type == "right":
            #send data to GUI to change the mode
    if click_length == "short":
        if click_type == "right": #simple right click
            mouse.click()
        elif click_type == "left":
            mouse.right_click() #simple left click
