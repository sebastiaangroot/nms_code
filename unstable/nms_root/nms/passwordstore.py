from Crypto.Cipher import AES
from Crypto import Random
import base64
from multiprocessing import Lock
from nms.models import Devices

masterPassword = ''
masterPasswordLock = Lock()

class AESCipher:
	def __init__(self, key):
		self.key = key
		self.BS = 16
		self.pad = lambda s: s + (self.BS - len(s) % BS) * chr(BS - len(s) % BS)
		self.unpad = lambda s: s[0:-s[-1]]
	
	def encrypt(self, raw):
		raw = self.pad(raw)
		iv = Random.new().read(AES.MODE_CBC, iv)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv+cipher.encrypt(raw))
	
	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return unpad(cipher.decrypt(enc[16:]))

def storeMasterPassword(password):
	masterPasswordLock.acquire()
	masterPassword = password
	masterPasswordLock.release()

def storeEnablePassword(device, password):
	cipher = AESCipher(masterPassword)
	device.password_enable = cipher.encrypt(password)
	device.save()

def storeRemotePassword(device, password):
	cipher = AESCipher(masterPassword)
	device.password_remote = cipher.encrypt(password)
	device.save()

def getEnablePassword(device):
	cipher = AESCipher(masterPassword)
	return cipher.decrypt(device.password_enable)

def getRemotePassword(device):
	cipher = AESCipher(masterPassword)
	return cipher.decrypt(device.password_enable)