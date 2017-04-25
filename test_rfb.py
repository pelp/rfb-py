import sys, random
from rfb_class import RFB

def c(c):
    print("Client with address {} connected!".format(r.get_address(c)))
    
def d(c):
    print("Client with address {} disconnected!".format(r.get_address(c)))

def k(c, pressed, key):
    if (pressed):
        if (key < 0xFF):
            r.fill(random.randint(0, 255))
            r.rect(int(r.width / 2) - int(r.height / 4), int(r.height / 4), int(r.height / 2), int(r.height / 2), c)
        else:
            print("Special key: {}".format(str(key)))
def m(c, pressed, xy, change):
    if(pressed):
        if (pressed and change):
            print("Pressed mouse!")
            r.send_bell(c)
        
r = RFB(640, 480, 3332)
r.disconnect_event = d
r.connect_event = c
r.onKey_event = k
r.onMouse_event = m
while(True):
    r.handle()
