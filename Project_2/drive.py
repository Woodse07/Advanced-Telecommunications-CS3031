from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet
from encrypt import encrypt
from decrypt import decrypt
import os
import shutil

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def main():
	print("[*] Running program..")
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
	while not finished:
		print("[*]")
		option = input("[*] Enter 1 to encrypt files.\n[*] Enter 2 to decrypt files.\n[*] Enter 3 to add a user.\n[*] Enter 4 to remove a user.\n[*] Enter 5 to list files.\n[*] Enter 6 to quit.\n[*] ")
		if option is 1:
			encrypt(f, f_list)

		elif option is 2:
			decrypt(f,f_list)

		elif option is 3:
			username = raw_input("[*] Enter username: ")
			if os.path.exists("group/" + str(username)):
				print("[*] Username taken.")
			else:
				print("[*] Adding user " + str(username) + "..")
				# Creating dir for user..
				os.mkdir("group/" + str(username))
				
				print("[*] Generating keys for user..")
				# Generating private + public keys..
				private_key = rsa.generate_private_key(
    			public_exponent=65537,
    			key_size=2048,
    			backend=default_backend())
				public_key = private_key.public_key()

				# Serialising keys for storing..
				private_serialized = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.NoEncryption())
				public_serialized = public_key.public_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PublicFormat.SubjectPublicKeyInfo)
			
				# Storing private key..
				file = open("group/" + str(username) + "/private_key.txt", "w")
				file.write(private_serialized)
				file = open("group/" + str(username) + "/private_key.txt", "w")
				file.write(public_serialized)
				print("[*] Added user " + str(username) + "!")

		elif option is 4:
			username = raw_input("[*] Enter username: ")
			if os.path.exists("group/" + str(username)):
				print("[*] Removing user..")
				shutil.rmtree("group/" + str(username))
				print("[*] Generating new symmetric key and re-encrypting all files..")
				key = Fernet.generate_key()
				f = open('keys/symmetric_key.txt', 'w')
				f.write(key)
				print("[*] New symmetric key: " + key)
			else:
				print("[*] Username does not exist..")

		elif option is 5:
			for file in f_list:
				print(file['title'])

		elif option is 6: 
			print("[*] Thanks for using the program!")
			finished = True
		





if __name__ == "__main__":
	main()
