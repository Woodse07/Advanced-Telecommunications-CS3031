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
import base64
import requests
import os

# Takes in a username and returns the encrypted version of the symmetric key specifically 
# for that user.
def getKey(username):
	# Grabbing private key..
	with open("group/" + str(username) + "/private_key.txt", "rb") as key_file:
		private_key = key_file.read()
	private_key = load_pem_private_key(private_key, None, default_backend())
	
	# Generating public key..
	public_key = private_key.public_key()
	public_key = public_key.public_bytes(
            	 	encoding=serialization.Encoding.PEM,
            	  	format=serialization.PublicFormat.SubjectPublicKeyInfo)

	# Sending request to flask server..
	print("[*] Requesting symmetric key from server..")
	URL = "http://127.0.0.1:5000/get_key"
	PARAMS = {'username' : username, 'pub_key': public_key}
	r = requests.get(url=URL, params=PARAMS)
	encrypted = r.text
	print("[*] Received encrypted symmetric key from server..")

	# Decrypting response from flask server..
	encrypted = base64.b64decode(encrypted)
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

# Shows all files in the folder of the drive..
def show_files(f_list):
	print("[*] -------------------- Files --------------------")
	print("[*]")
	for file in f_list:
		print("[*] " + file['title'])
	print("[*]")
	print("[*] -------------------- Files --------------------")
	print("[*]")

# Clears terminal and prints logo
def logo(username):
	os.system('cls' if os.name == 'nt' else 'clear')
	print("   _____        _____        _____                 ")
	print("  / ____|      / ____|      / ____|         /\     ")
	print(" | (___       | |          | (___          /  \    ")
	print("  \___ \      | |           \___ \        / /\ \   ")
	print("  ____) |  _  | |____   _   ____) |  _   / ____ \  ")
	print(" |_____/  (_)  \_____| (_) |_____/  (_) /_/    \_\ ")
	print("[*] Welcome to secure cloud storage application "+username+"!(Client side)")



def main():
	logo("")
	# Prompts client for username and checks if they're a valid user..
	username = raw_input("[*] Please enter your username: ")
	if os.path.exists("group/" + str(username)):
		print("[*] Welcome " + str(username) + "!")
		auth = GoogleAuth()
		auth.LocalWebserverAuth()
		drive = GoogleDrive(auth)

		# Get symmetric key..
		key = getKey(username)	
		print("[*] '" + key + "'")
		f = Fernet(key)
		f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()

		finished = False
		logo(username)
		while not finished:
			print("[*]")
			# Present user with options...
			option = input("[*] Enter 1 to view all files.\n[*] Enter 2 to open a file.\n[*] Enter 3 to upload a file.\n[*] Enter 4 to delete a file.\n[*] Enter 5 to quit.\n[*] ")
			logo(username)
			print("[*]")
			
			# Shows all files in the folder of the drive..
			if option is 1:
				show_files(f_list)

			# Opens the contents of a file.. basically grabs contents of the file in the
			# drive and drcrypts it using the symmetric key.
			elif option is 2:
				found = 0
				show_files(f_list)
				file_name = raw_input("[*] Enter name of file: ")
				logo(username)
				for file in f_list:
					if file["title"] == file_name:
						found = 1
						encoded = file.GetContentString()
						print("[*] Decrypting contents of file...")
						decoded = f.decrypt(encoded.encode())
						print("[*] Decrypted!")
						print("[*]")
						print("[*] --------------------File Contents--------------------")
						print("")
						print(decoded.decode())
						print("[*] --------------------File Contents--------------------")
						print("[*]")
				if found is 0:
					print("[*] No such file name in drive.. enter '1' to see list of files.")
					print("[*]")	

			# Uploads a file.. just takes in the name of a file form secret_files/ and 
			# encrypts it before uploading..
			elif option is 3:
				file_name = raw_input("[*] Enter name of file to upload: ")
				file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f"}],'title':file_name})
				source_file = open("secret_files/" + file_name, "r")
				print("[*] Encrypting file and uploading...")
				data = source_file.read()
				encrypted_data = f.encrypt(data)
				file.SetContentString(encrypted_data.decode())
				file.Upload()
				print("[*] Uploaded!")
				f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()
				print("[*]")
			
			# Removes a file.. self explanatory. 
			elif option is 4:
				found = 0
				show_files(f_list)
				file_name = raw_input("[*] Enter name of file: ")
				logo(username)
				for file in f_list:
					if file["title"] == file_name:	
						found = 1
						file.Delete()
						print("[*] Deleted " + file_name + "!")
						print("[*]")
				if found is 0:
					print("[*] No such file name in drive.. enter '1' to see list of files.")
					print("[*]")

			# Exit.
			elif option is 5:
				print("[*] Thanks for using the program!")
				print("[*]")
				finished = True

			else:
				print("[*] Please pick one of the options listed below..")
				print("[*]")


		
		

	# If user is not a valid user, print this.
	else:
		print("[*] You are not part of the admin's group.. please contact admin for an invite.")

if __name__ == "__main__":
	main()
