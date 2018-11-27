import enum

class Message(enum.Enum):
	interest = 1
	not_interest = 2
	unchoke = 3
	choke = 4
	request = 5
	annouce = 6
	payload = 7
	cancel = 8

