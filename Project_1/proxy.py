#! /usr/bin/env python
import os, sys, thread, socket
import Tkinter as tk
from Tkinter import *

# CONSTANTS
BACKLOG = 50 			# How many pending connection will the queue hold?	
MAX_DATA_RECV = 4096	# Max number of bytes to receive at once?
DEBUG = True			# Set true if you want to see debug messages. 
blocked = {}			# Dict to store the blocked URLs
cache = {}				# Dict to act as a cache, stores responses.

# Tkinter function.. Used to dynamicall block URLs.
# Also used to display the current blocked URLs and the cache.
def tkinter():
	# Create block and unblock entries.. 
	console = tk.Tk()
	block = Entry(console)
	block.grid(row=0,column=0)
	unblock = Entry(console)
	unblock.grid(row=1, column=0)

	# Function for blocking urls.. basically take whats in the entry cell and put it into 
	# the dict..
	def block_url():
		ret = block.get()
		temp = blocked.get(ret)
		if temp is None:
			blocked[ret] = 1	
			print("[*] Successfully blocked: " + ret)
		else:
			print("[*] This website is already blocked..")
	# Creating a button to call the block_url function..
	block_button = Button(console, text="Block URL", command=block_url)
	block_button.grid(row=0, column=1)

	# Function for unblocking urls.. basically tkaes whats in the entry cell and removes it
	# from the blocked dict if it exists..
	def unblock_url():
		ret = unblock.get()
		temp = blocked.get(ret)
		if temp is None:
			print("[*] Url is not blocked: " + ret)
		else:
			blocked.pop(ret)
			print("[*] Successfully unblocked: " + ret)
	# Creating a button to call the unblock_url function..
	unblock_button = Button(console, text="Unlock URL", command=unblock_url)
	unblock_button.grid(row=1, column=1)
	
	# Function to print all currently blocked urls..
	def print_blocked():
		print(blocked)
	print_blocked = Button(console, text="Print Blocked URLs", command=print_blocked)
	print_blocked.grid(row=3, column=0)

	# Function to print all currently cached pages..
	def print_cache():
		for key, value in cache.iteritems():
			print key
	print_blocked = Button(console, text="Print Cache", command=print_cache)
	print_blocked.grid(row=3, column=1)

	# Could add other functionality here :D	

	mainloop()
	
# MAIN PROGRAM
def main():
	# Run a thread of our tkinter function..
	thread.start_new_thread(tkinter,())

	try:
		# Ask user what port they'd like to run the proxy on..
		listening_port = int(raw_input("[*] Enter Listening Port Number: "))
	except KeyboardInterrupt:
		# Handling keyboard interrupt.. looks nicer..
		print("\n[*] User Requested An Interrupt")
		print("[*] Application Exiting...")
		sys.exit()
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# Ininitiate socket
		s.bind(('', listening_port))							# Bind socket for listen
		s.listen(BACKLOG)						# Start listening for incoming connections
		print("[*] Initializing sockets... done")
		print("[*] Sockets binded successfully...")
		print("[*] Server started successfully [ %d ]\n" % (listening_port))		
	except Exception, e:
		print("[*] Unable to initalize socket...")
		sys.exit(2)

	while True:
		try:
			conn, client_addr = s.accept()		# Accept connection from client browser
			data = conn.recv(MAX_DATA_RECV)		# Receive client data
			thread.start_new_thread(proxy_thread, (conn, data, client_addr)) # Start a thread
		except KeyboardInterrupt:
			s.close()
			print("[*] Proxy server shutting down...")
			sys.exit(1)
	s.close()



def proxy_thread(conn, data, client_addr):
	print("")
	print("[*] Starting new thread...")
	try:
		# Parsing the request..
		first_line = data.split('\n')[0]
		url = first_line.split(' ')[1]
		method = first_line.split(' ')[0]
		print("[*] Connecting to url " + url)
		print("[*] Method: " + method)
		if (DEBUG):
			print("[*] URL: " + url)

		http_pos = url.find("://")		# Find pos of ://
		if (http_pos == -1):
			temp = url
		else:
			temp = url[(http_pos+3):]	# Rest of url..
		port_pos = temp.find(":")		# Finding port position if there is one..

		webserver_pos = temp.find("/") 	# Find end of web server
		if webserver_pos == -1:
			webserver_pos = len(temp)

		webserver = ""
		port = -1
		if (port_pos == -1 or webserver_pos < port_pos):	# Default port..
			port = 80
			webserver = temp[:webserver_pos]
		else:												# Specific port..
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]

		# Checking if we already have the response in our cache..
		x = cache.get(webserver)
		if x is not None:
			# If we do, don't bother with proxy_server function and send the response on..
			print("[*] Found in Cache!")
			print("[*] Sending cached result to user..")
			conn.sendall(x)
		else:
			# If we don't, continue..
			proxy_server(webserver, port, conn, client_addr, data, method)
	except Exception, e:
		pass
	

def proxy_server(webserver, port, conn, client_addr, data, method):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Initiating socket..
	
	# Checking our blocked dict to check if the URL the user is trying to connect to 
	# is blocked..
	for key, value in blocked.iteritems():
		if key in webserver and value is 1:
			print("That url is blocked!")
			conn.close()
			return

	# If the method is CONNECT, we know this is HTTPS.
	if method == "CONNECT":
		try:
			# Connect to the webserver..
			s.connect((webserver, port))
			reply = "HTTP/1.0 200 Connection established\r\n"
			reply += "Proxy-agent: Pyx\r\n"
			reply += "\r\n"
			conn.sendall(reply.encode())
		except socket.error as err:
			print(err)
			return
		conn.setblocking(0)
		s.setblocking(0)
		# Bidirectional messages here.. (Websocket connection)
		while True:
			try:
				request = conn.recv(MAX_DATA_RECV)
				s.sendall(request)
			except socket.error as err:
				pass
			try:
				reply = s.recv(MAX_DATA_RECV)
				conn.sendall(reply)
			except socket.error as err:
				pass

	# Else we know this is HTTP.
	else:
		# String builder to build response for our cache.
		string_builder = bytearray("", 'utf-8')
		s.connect((webserver, port))
		s.send(data)
		s.settimeout(2)
		try:
			while True:
				reply = s.recv(MAX_DATA_RECV)
				if (len(reply) > 0):
					conn.send(reply)		# Send reply back to client
					string_builder.extend(reply)
				else:
					break
		except socket.error:
			pass
		# After response is complete, we can store this in cache. 
		cache[webserver] = string_builder
		print("[*] Added to cache: " + webserver + "\n" + cache[webserver])
		s.close()			# Close server socket
		conn.close()		# Close client socket


if __name__ == '__main__':
	main()
