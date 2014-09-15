#!/usr/bin/python
# 32x32 RGB led lamp controlled via TouchOSC
# (c) 2014 Sergio Tanzilli - sergio@tanzilli.com 

from OSC import OSCServer,OSCClient, OSCMessage
import sys
from time import sleep
import types
import StringIO
import Image, ImageDraw, ImageFont
from PIL import ImageEnhance
import PIL.ImageOps    

size = 32, 32

server = OSCServer( ("0.0.0.0", 8000) )
client = OSCClient()
#client.connect( ("192.168.1.2", 9000) )
client.connect( ("0.0.0.0", 9000) )

#Create a 32x32 black image  
im=Image.new("RGB",size,(1<<5,0,0))


#Create a draw object to draw primitives on the new image 
draw = ImageDraw.Draw(im)

def handle_timeout(self):
	print ("Timeout")

server.handle_timeout = types.MethodType(handle_timeout, server)

def rele_callback(path, tags, args, source):
	if args[0]:
		print "rele.on()"
	else:
		print "rele.off()"

red=0
green=0
blue=0
def fader_rgb_callback(path, tags, args, source):
	global red,green,blue
	
	if (path[3:]=="red"):
		red=int(args[0])	
		
	if (path[3:]=="green"):
		green=int(args[0])	

	if (path[3:]=="blue"):
		blue=int(args[0])	

	if (path[3:]=="off"):
		red=0	
		green=0	
		blue=0	

	#Draw counter text on the panel 
	draw.rectangle((0, 0, 31, 31), outline=0, fill=(red<<5,green<<5,blue<<5))
	

	#Generate a PPM image (a format very similar to byte array RGB we need)
	output = StringIO.StringIO()
	im.save(output, format='PPM')
	buf=output.getvalue()

	#Discard the first 13 bytes of header and save the rest (the
	#RGB array) on the ledpanel driver output buffer
	out_file = open("/sys/class/ledpanel/rgb_buffer","w")
	out_file.write(buf[13:])
	out_file.close()

	#msg=OSCMessage("/1/rotary1")
	#msg.append(args);
	#client.send(msg)


server.addMsgHandler( "/1/red",fader_rgb_callback)
server.addMsgHandler( "/1/green",fader_rgb_callback)
server.addMsgHandler( "/1/blue",fader_rgb_callback)
server.addMsgHandler( "/1/off",fader_rgb_callback)

while True:
	server.handle_request()

server.close()


