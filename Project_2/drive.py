from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet
from encrypt import encrypt
from decrypt import decrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import shutil

# Shows all the users that are part of the admin's group
def show_users():
	subs = os.listdir('group/')
	print("[*] -------------------- Users --------------------")
	print("[*]")
	for sub in subs:
		print("[*] " + sub)
	print("[*]")
	print("[*] -------------------- Users --------------------")	
	print("[*]")

# Shows all the files in the folder of the drive
def show_files(f_list):
	print("[*] -------------------- Files --------------------")
	print("[*]")
	for file in f_list:
		print("[*] " + file['title'])
	print("[*]")
	print("[*] -------------------- Files --------------------")
	print("[*]")

# Clears terminal and prints logo
def logo():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("   _____        _____        _____                 ")
	print("  / ____|      / ____|      / ____|         /\     ")
	print(" | (___       | |          | (___          /  \    ")
	print("  \___ \      | |           \___ \        / /\ \   ")
	print("  ____) |  _  | |____   _   ____) |  _   / ____ \  ")
	print(" |_____/  (_)  \_____| (_) |_____/  (_) /_/    \_\ ")
	print("[*] Welcome to secure cloud storage application!(Server side)")


def main():
	logo()

	# Google Authentication
	auth = GoogleAuth()
	auth.LocalWebserverAuth()
	drive = GoogleDrive(auth) 

	# Grab the symmetric key.. if it doesn't exist, generate a new one
	try:
		f = open('keys/symmetric_key.txt', 'r')
		key = f.read()
		print("[*] Your symmetric key: '" + key + "'")
	except:
		key = Fernet.generate_key()
		f = open('keys/symmetric_key.txt', 'w')
		f.write(key)
		print("[*] Your symmetric key: '" + key + "'")
	f = Fernet(key)
	
	# Grabbing list of files in folder of drive.. change the id here to change folder.
	f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()

	# Guts of the program..
	finished = False
	logo()
	print("[*]")
	# Present admin with list of options..
	while not finished:
		option = input("[*] Enter 1 to encrypt files.\n[*] Enter 2 to decrypt files.\n[*] Enter 3 to add a user.\n[*] Enter 4 to remove a user.\n[*] Enter 5 to list files.\n[*] Enter 6 to list users.\n[*] Enter 7 to quit.\n[*] ")
		logo()
		print("[*]")
		# Encrypts all files in the folder of the drive..
		if option is 1:
			encrypt(f, f_list)

		# Decrypts all files in the folder of the drive..
		elif option is 2:
			decrypt(f,f_list)

		# Adds a user to the group.. basically just creates a new folder whose name is the 
		# name of the user, and generates an rsa key and stores it in that folder. 
		elif option is 3:
			username = raw_input("[*] Enter username: ")
			if os.path.exists("group/" + str(username)):
				print("[*] Username taken.")
				print("[*]")
			else:
				print("[*] Adding user " + str(username) + "..")
				# Creating dir for user..
				os.mkdir("group/" + str(username))
				
				print("[*] Generating keys for user..")
				# Generating private key..
				private_key = rsa.generate_private_key(
    			public_exponent=65537,
    			key_size=2048,
    			backend=default_backend())

				# Serialising keys for storing..
				private_serialized = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.NoEncryption())
			
				# Storing private key..
				file = open("group/" + str(username) + "/private_key.txt", "w")
				file.write(private_serialized)
				file.close()
				print("[*] Added user " + str(username) + "!")
				print("[*]")

		# Removes a user.. basically deletes the folder whose name is the same as the users, 
		# decrypts all the files in the folder of the drive, generates a new symmetrics key,
		# and re-encrypts all the files in folder of the drive.
		elif option is 4:
			show_users()
			username = raw_input("[*] Enter username: ")
			logo()
			if os.path.exists("group/" + str(username)):
				print("[*] Removing user..")
				shutil.rmtree("group/" + str(username))
				print("[*] Generating new symmetric key and re-encrypting all files..")
				decrypt(f, f_list)
				key = Fernet.generate_key()
				file = open('keys/symmetric_key.txt', 'w')
				file.write(key)
				file.close()
				f = Fernet(key)
				print("[*] New symmetric key: " + key)
				encrypt(f, f_list)
				print("[*]")
				logo()
				print("[*]\n[*] Deleted user " + username + "!\n[*]")
			else:
				print("[*] Username does not exist.. enter '6' to see list of users.")
				print("[*]")

		# Shows all files in the folder of the drive..
		elif option is 5:
			show_files(f_list)

		# Shows all users in the admin's group..
		elif option is 6:
			show_users()

		# Exit()
		elif option is 7: 
			print("[*] Thanks for using the program!")
			finished = True
		
		else:
			print("[*] Please pick one of the options listed below..")
			print("[*]")

if __name__ == "__main__":
	main()
