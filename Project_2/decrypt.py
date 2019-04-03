from cryptography.fernet import Fernet
import os

file = open("keys/symmetric_key.txt", "r")
key = file.read()
f = Fernet(key)

for filename in os.listdir("secret_files"):
	file = open("secret_files/" + filename, "r")
	data = file.read()
	encrypted = f.decrypt(data)	
	file2 = open("secret_files/" + filename, "w")
	file2.write(encrypted)
