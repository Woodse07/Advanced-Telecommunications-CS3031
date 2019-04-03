from cryptography.fernet import Fernet
import os

key = Fernet.generate_key()
file = open("keys/symmetric_key.txt", "w")
file.write(key)
print("My symmetric key: " + key)
f = Fernet(key)

for filename in os.listdir("secret_files"):
	file = open("secret_files/" + filename, "r")
	data = file.read()
	encrypted = f.encrypt(data)	
	file2 = open("secret_files/" + filename, "w")
	file2.write(encrypted)

