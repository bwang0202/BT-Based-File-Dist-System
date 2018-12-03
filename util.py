# util.py
# A small collection of useful functions
import threading
import os, binascii

def collapse(data):
	""" Given an homogenous list, returns the items of that list
	concatenated together. """

	return reduce(lambda x, y: x + y, data)

def slice(string, n):
	""" Given a string and a number n, cuts the string up, returns a
	list of strings, all size n. """

	temp = []
	i = n
	while i <= len(string):
		temp.append(string[(i-n):i])
		i += n

	try:	# Add on any stragglers
		if string[(i-n)] != "":
			temp.append(string[(i-n):])
	except IndexError:
		pass

	return temp

def random_thread_id():
	return binascii.b2a_hex(os.urandom(15))

class myThread(threading.Thread):
   def __init__(self, threadID, name, f, *args, **kwargs):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.f = f
      self.args = args
      self.kwargs = kwargs
   def run(self):
      print ("Starting " + self.name)
      self.f(*self.args, **self.kwargs)
      print ("Exiting " + self.name)

# FOR DEBUGGING purpose
DEBUG_PIECE_SUBPIECES = 8
DEBUG_SUBPIECE_PAYLOAD = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09'