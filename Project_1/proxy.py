#! /usr/bin/env python
import os, sys, thread, socket, ssl, requests

# CONSTANTS
BACKLOG = 50 			# How many pending connection will the queue hold?	
MAX_DATA_RECV = 4096	# Max number of bytes to receive at once?
DEBUG = True			# Set true if you want to see debug messages. 

# MAIN PROGRAM
def main():
	# Check for relevant arguments..
	try:
		listening_port = int(raw_input("[*] Enter Listening Port Number: "))
	except KeyboardInterrupt:
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
			thread.start_new_thread(proxy_thread, (conn, data, client_addr))	# Start a thread
		except KeyboardInterrupt:
			s.close()
			print("[*] Proxy server shutting down...")
			sys.exit(1)
	s.close()




def proxy_thread(conn, data, client_addr):
	print("[*] Starting new thread...")
	try:
		first_line = data.split('\n')[0]
		url = first_line.split(' ')[1]
		method = first_line.split(' ')[0]
		print("[*] Connecting to url " + url)
		print("[*] Method: " + method)

		if (DEBUG):
			print(first_line)
			print("")
			print("URL: " + url)
			print("")

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
		
		proxy_server(webserver, port, conn, client_addr, data, method)
	except Exception, e:
		pass
	

def proxy_server(webserver, port, conn, client_addr, data, method):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if method == "CONNECT":
		try:
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
	else:
		try:
			s.connect((webserver, port))
			s.send(data)

			while True:
				reply = s.recv(MAX_DATA_RECV)
				if (len(reply) > 0):
					conn.send(reply)		# Send reply back to client
				else:
					break
			s.close()			# Close server socket
			conn.close()		# Close client socket
		except Exception, e:
			s.close()
			conn.close()
			print("Runtime Error: " + e)	
			sys.exit(1)


if __name__ == '__main__':
	main()
