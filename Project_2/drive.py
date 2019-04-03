from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from cryptography.fernet import Fernet
from encrypt import encrypt
from decrypt import decrypt

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

	f_list = drive.ListFile({'q':"'1l53l9SNSC2qwj6wfDCMFQvXMOhX1BI0f' in parents and trashed=false"}).GetList()
	
	f = Fernet(key)
	encrypt(f, f_list)
	decrypt(f, f_list)
		





if __name__ == "__main__":
	main()
