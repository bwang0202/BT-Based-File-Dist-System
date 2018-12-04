# util.py
# A small collection of useful functions
import threading
import os, binascii
import colors

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

def print_red(s):
	print(colors.red(s)) # send piece payload

def print_green(s):
	print(colors.green(s)) # recieved piece

def print_blue(s):
	print(colors.blue(s)) # subpieces stuff

def print_yellow(s):
	print(colors.yellow(s))  # Signals like choke, unchoke, interested, request

# FOR DEBUGGING purpose
DEBUG_PIECE_SUBPIECES = 8
DEBUG_SUBPIECE_PAYLOAD = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09'

LENLEN = 4
MAGIC = b"BITTORRENT"
ENDIAN = 'big'
INTEREST = 1
UNINTEREST = 2
UNCHOKE = 3
CHOKE = 4
REQUEST = 5
ANNOUNCE = 6
PAYLOAD = 7
CANCEL = 8