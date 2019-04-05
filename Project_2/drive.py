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

def show_users():
	subs = os.listdir('group/')
	print("[*] -------------------- Users --------------------")
	print("[*]")
	for sub in subs:
		print("[*] " + sub)
	print("[*]")
	print("[*] -------------------- Users --------------------")	
	print("[*]")

def show_files(f_list):
	print("[*] -------------------- Files --------------------")
	print("[*]")
	for file in f_list:
		print("[*] " + file['title'])
	print("[*]")
	print("[*] -------------------- Files --------------------")
	print("[*]")

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
	auth = GoogleAuth()
	auth.LocalWebserverAuth()
	drive = GoogleDrive(auth) 

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
	f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()

	finished = False
	logo()
	print("[*]")
	while not finished:
		option = input("[*] Enter 1 to encrypt files.\n[*] Enter 2 to decrypt files.\n[*] Enter 3 to add a user.\n[*] Enter 4 to remove a user.\n[*] Enter 5 to list files.\n[*] Enter 6 to list users.\n[*] Enter 7 to quit.\n[*] ")
		logo()
		print("[*]")
		if option is 1:
			encrypt(f, f_list)

		elif option is 2:
			decrypt(f,f_list)

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

		elif option is 5:
			show_files(f_list)

		elif option is 6:
			show_users()

		elif option is 7: 
			print("[*] Thanks for using the program!")
			finished = True
		
		else:
			print("[*] Please pick one of the options listed below..")
			print("[*]")

if __name__ == "__main__":
	main()
