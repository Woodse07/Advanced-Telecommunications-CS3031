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
import requests
import base64
import os

from flask import Flask
from flask import request
app = Flask(__name__)

# Create route for get_key function
@app.route('/get_key', methods=['GET'])
def index():
	# Grab username and public_key for that user.
	username = request.args.get('username')
	pub_key = request.args.get('pub_key').encode('ascii')
	public_key = serialization.load_pem_public_key(pub_key,backend=default_backend())

	# Grab the unencrypted symmetric key..
	key = open("keys/symmetric_key.txt", "r")
	key = key.read()

	# Encrypt the symmetric key..
	encrypted = public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    	)
	)	

	# Return the symmetric key specifically encrypted for that user...
	encrypted = base64.b64encode(encrypted)

	print("encrypted symmetric key.. sending to client..")
	return encrypted

if __name__ == '__main__':
   app.run(debug = True)
