from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet
from encrypt import encrypt
from decrypt import decrypt
import os

# getkey() function is temprorary.. will replace with some web framework?
def getKey(username):
	with open("group/" + str(username) + "/private_key.txt", "rb") as key_file:
		private_key = key_file.read()
	private_key = load_pem_private_key(private_key, None, default_backend())

	public_key = private_key.public_key()
	print(public_key)

	key = open("keys/symmetric_key.txt", "r")
	key = key.read()

	encrypted = public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    	)
	)	
	print("[*] Received encrypted symmetric key..")
	
	symmetric_key = private_key.decrypt(
    encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    	)
	)
	print("[*] Decrypted symmetric key!")
	
	return symmetric_key




def main():
	print("[*] Welcome to secure cloud storage application!")
	username = raw_input("[*] Please enter your username: ")
	if os.path.exists("group/" + str(username)):
		print("[*] Welcome " + str(username) + "!")
		auth = GoogleAuth()
		auth.LocalWebserverAuth()
		drive = GoogleDrive(auth)
		key = getKey(username)	
		f = Fernet(key)
		f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()

		finished = False
		while not finished:
			print("[*]")
			option = input("[*] Enter 1 to view all files.\n[*] Enter 2 to open a file.\n[*] Enter 3 to quit.\n[*] ")
			if option is 1:
				for file in f_list:
					print(file['title'])

			elif option is 2:
				file_name = raw_input("[*] Enter name of file: ")
				for file in f_list:
					if file["title"] == file_name:
						encoded = file.GetContentString()
						decoded = f.decrypt(encoded.encode())
						print(decoded)
	
			elif option is 3:
				print("todo")


		
		


	else:
		print("[*] You are not part of the admin's group.. please contact admin for an invite.")















if __name__ == "__main__":
	main()
