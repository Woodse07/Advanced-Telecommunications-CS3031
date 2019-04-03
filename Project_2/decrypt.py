from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet

def decrypt(f, file_list):
	for file in file_list:
		encoded = file.GetContentString()
		print("[*] Decrypting file: " + file['title'] + "...")
		decoded = f.decrypt(encoded.encode())
		file.SetContentString(decoded.decode())
		file.Upload()
