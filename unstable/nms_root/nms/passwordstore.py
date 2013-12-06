from Crypto.Cipher import AES
from Crypto import Random
import base64
from multiprocessing import Lock

masterPassword = bytes()
masterPasswordLock = Lock()

class AESCipher:
	def __init__(self, key):
		self.key = key
		self.BS = 16
		self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
		self.unpad = lambda s: s[0:-s[-1]]

	def encrypt(self, raw):
		raw = self.pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv+cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self.unpad(cipher.decrypt(enc[16:]))

def storeMasterPassword(password):
	global masterPasswordLock
	global masterPassword
	if len(password) != 16:
		return -1
	masterPasswordLock.acquire()
	masterPassword = password
	masterPasswordLock.release()
	return 0

def hasMasterPassword():
	masterPasswordLock.acquire()
	try:
		if not (len(masterPassword) == 16 or len(masterPassword) == 24 or len(masterPassword) == 32):
			return False
		return True
	except:
		return False
	finally:
		masterPasswordLock.release()

def storeEnablePassword(device, password):
	salt = base64.b64encode(Random.new().read(16))[:16].decode()
	cipher = AESCipher(masterPassword + salt)
	device.password_enable = salt + '$' + cipher.encrypt(password).decode()
	device.save()

def storeRemotePassword(device, password):
    salt = base64.b64encode(Random.new().read(16))[:16].decode()
	cipher = AESCipher(masterPassword)
	device.password_remote = salt + '$' + cipher.encrypt(password).decode()
	device.save()

def getEnablePassword(device):
	try:
		cipher = AESCipher(masterPassword + device.password_enable[:device.password_enable.find('$')])
		return cipher.decrypt(device.password_enable[device.password_enable.find('$')+1:])
	except:
		return b''
		

def getRemotePassword(device):
	try:
		cipher = AESCipher(masterPassword + device.password_remote[:device.password_remote.find('$')])
		return cipher.decrypt(device.password_remote[device.password_remote.find('$')+1:])
	except:
		return b''