THANKS FOR CHECKING MY CODE OUT!!!

So UD and LR are the displacement from the midpoints (i.e. the position of the joystick when the code is first run)

For UD: 

UP --> positive, max = 513
DOWN --> negative, max = -497

For LR:

RIGHT --> positive, max = 513
LEFT --> negative, max = -507

Natural stick drift seems to be  |x|, |y| < 3 i.e. define a dead zone between 3 and -3
tbh not seen anything greater than 2 but choose 3 to be on a safer side

---------------Encode---------------

a 3 byte array called payload is used here
payload[2] = first 8 bits of UD
payload[1] = first 6 bits of LR + last 2 bits of UD
payload[0] = identifier 0xA + last 4 bits of LR

---------------Decode---------------

UD = payload[2] + ((payload[1] & 0x3) << 8)
LR = (payload[1] & 0xFC) + ((payload[0] & 0xF) << 8)
Identifier = ((payload[0] >> 4) & 0xA)) this should give you 0xA

I guess we can implement some sort of error mechanism here if we really wanted.