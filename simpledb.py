"""python 2.7"""
from bsddb import hashopen
from pickle import dumps, loads

class Database():
	""" A wrapper around a bsddb database, acting as a dictionary.
	Can accept all Python datatypes as keys, and values. """

	def __init__(self, dbname, flag="c"):
		""" Read the database given by dbname. """

		self.data = hashopen(dbname, flag)

	def __contains__(self, key):
		""" Return true if the database contains the key. """

		key = dumps(key)
		boolean = self.data.has_key(key)	# Returns 1 or 0.
		return bool(boolean)

	def __getitem__(self, key):
		""" Return the value held by the key. """

		key = dumps(key)
		value = self.data[key]
		return loads(value)

	has_key = __contains__
	get 	= __getitem__

	def __setitem__(self, key, value):
		""" Set the value of key to the value given. """

		key = dumps(key)
		value = dumps(value)
		self.data[key] = value

	def __repr__(self):
		""" Represent the database. """

		keys = self.data.keys()
		items = [(loads(key), loads(self.data[key])) for key in keys]
		return str(dict(items))

	def clear(self):
		""" Remove all data in the database. """

		self.data.clear()

	def items(self):
		""" Return a list of tuples of the keys and values. """

		keys = self.data.keys()
		items = [(loads(key), loads(self.data[key])) for key in keys]
		return items

	def keys(self):
		""" Return a list of keys. """

		keys = [loads(key) for key in self.data.keys()]
		return keys

	def values(self):
		""" Return a list of values. """

		values = [loads(value) for value in self.data.values()]
		return values

	def pop(self, key):
		""" Return the value given by key, and remove it. """

		key = dumps(key)
		value = self.data[key]
		del self.data[key]
		return loads(value)

	def setdefault(self, key, default):
		""" Return the value held by key, or default if it isn't in
		the database. """

		key = dumps(key)
		try:
			value = self.data[key]
		except KeyError:
			return default
		return loads(value)

	def __del__(self):
		""" Synchronize the database on disk"""

		self.data.sync()