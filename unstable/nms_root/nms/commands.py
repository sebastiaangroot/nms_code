import nms.sshconnection as sshconnection
import nms.xmlparser as xmlparser
import nms.passwordstore as passwordstore
from multiprocessing import Lock

interfaces = {}
interfacesLock = Lock()

sshconnections = {}
sshconnectionsLock = Lock()

def removeInterfaces(device):
	global interfacesLock
	global interfaces
	
	interfacesLock.acquire()
	if device in interfaces.keys():
		del interfaces[device]
	interfacesLock.release()

def getInterfaces(command, parser, device):
	global interfacesLock
	global interfaces
	interfacesLock.acquire()
	try:
		if not device in interfaces.keys():
			s = sshconnection.SSHConnection(device.ip, device.login_name, passwordstore.getRemotePassword(device), device.port)
			if s.connect() == -1:
				return -1
			ret = b''
			for i, arg in enumerate(command):
				if i+1 == len(command):
					ret += s.send_and_receive(arg, delay=0.5)
				else:
					ret += s.send_and_receive(arg)
			s.close()
			interfaces[device] = parser.parse(ret)
	except:
		raise
	finally:
		interfacesLock.release()
	return interfaces[device]

def executeTask(taskpath, device, uargs):
	xmlroot = xmlparser.get_xml_struct(device.gen_dev_id.file_location_id.location)
	taskpath = taskpath.split('|')
	commands = xmlparser.getAvailableTasks(xmlroot)
	for key in taskpath:
		if not key in commands.keys():
			return ['Invalid command']
		commands = commands[key]
	uarg_names, args, parser = commands
	
	for uarg_name in uarg_names:
		if not uarg_name in uargs.keys():
			return 'User arguments not supplied'
	for i in range(len(args)):
		for uarg_key in uargs.keys():
			if type(args[i]) == type(str()):
				args[i] = args[i].replace('%arg:' + uarg_key + '%', uargs[uarg_key])

	s = sshconnection.SSHConnection(device.ip, device.login_name, passwordstore.getRemotePassword(device), device.port)
	if s.connect() == -1:
		return -1
	ret = b''
	for i, arg in enumerate(args):
		if i+1 == len(args):
			ret += s.send_and_receive(arg, delay=0.5)
		else:
			ret += s.send_and_receive(arg)
	s.close()
	return parser.parse(ret)

def __createSSHConnection__(device):
	connection = sshconnection.SSHConnection(device.ip, device.login_name, passwordstore.getRemotePassword(device), device.port)
	connection.connect()
	connection.chan.setblocking(0)
	return connection

def getSSHConnection(user, device):
	#sshconnectionsLock.acquire()
	#try:
	if not user in sshconnections.keys():
		sshconnections[user] = {}
	if not device in sshconnections[user].keys():
		sshconnections[user][device] = __createSSHConnection__(device)
	return sshconnections[user][device]
	#except:
	#	raise
	#finally:
	#	sshconnectionsLock.release()
		
def removeSSHConnection(user, device):
	#sshconnectionsLock.acquire()
	#try:
	if not user in sshconnections.keys():
		return
	if not device in sshconnections[user].keys():
		return
	connection = sshconnections[user][device]
	connection.close()
	del sshconnections[user][device]
	#except:
	#	raise
	#finally:
	#	sshconnectionsLock.release()