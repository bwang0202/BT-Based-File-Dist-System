# util.py
# A small collection of useful functions
import threading
import os, binascii
import colors
import calendar, time

def epoch_microsec():
    return int(round(time.time() * 1000000))

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

    try:    # Add on any stragglers
        if string[(i-n)] != "":
            temp.append(string[(i-n):])
    except IndexError:
        pass

    return temp

def append_dict_list(d, k, v):
    tmp = d.get(k, [])
    tmp.append(v)
    d[k] = tmp

def append_dict_dict(d, k, v, vv):
    tmp = d.get(k, {})
    tmp[v] = vv
    d[k] = tmp

DEBUG = True
VERBOSE = False

def myprint(s):
    if DEBUG:
        print(s)

def print_red(s):
    if VERBOSE:
        myprint(colors.red(s)) # send piece payload

def print_green(s):
    myprint(colors.green(s)) # recieved piece

def print_blue(s):
    if VERBOSE:
        myprint(colors.blue(s)) # subpieces stuff

def print_yellow(s):
    myprint(colors.yellow(s))  # Signals like choke, unchoke, interested, request

def complete_download(result_file):
    with open(result_file, 'a') as f:
        f.write("Done %d\n" % epoch_microsec())


# FOR DEBUGGING purpose
CONCURRENT_PIECES = 4
PIPELINED_REQUEST = 5

SPEED_UNCHOKE = False
UNCHOKE_PEERS = 5

DEBUG_PIECE_SUBPIECES = 20
# 128KB
DEBUG_SUBPIECE_PAYLOAD = b'\x01\x02\x03\x04\x05\x06\x07\x08' * 16384 * 2

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
PEERID = 9