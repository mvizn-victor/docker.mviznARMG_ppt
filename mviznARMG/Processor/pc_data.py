import psutil, GPUtil, random

def coretemp():
	try:
		temps = psutil.sensors_temperatures()['coretemp']
	except KeyError:
		temps = psutil.sensors_temperatures()['k10temp']
	except AttributeError:
		return random.randint(0,100)
	else:
		avg_temp = 0.0
		for entry in temps:
			if entry.label[0:-2] == 'Core':
				avg_temp += entry.current/4.0
			elif entry.label == 'Tdie':
				avg_temp = entry.current
		return avg_temp


def gputemp():
	if len(GPUtil.getGPUs()) == 2:
		gpu_list = []		
		for gpu in GPUtil.getGPUs():
			gpu_list += [gpu.temperature]
		return gpu_list
	elif len(GPUtil.getGPUs()) == 1:
		return [GPUtil.getGPUs()[0].temperature, random.randint(0,100)]
	else:
		return [random.randint(0,100), random.randint(0,100)]
