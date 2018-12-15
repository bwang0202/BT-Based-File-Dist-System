# util.py
# A small collection of useful functions
import threading
import os, binascii
import colors
import calendar, time

############## UTILITIES Functions ##################################################
def epoch_microsec():
    return int(round(time.time() * 1000000))

def append_dict_list(d, k, v):
    tmp = d.get(k, [])
    tmp.append(v)
    d[k] = tmp

def append_dict_dict(d, k, v, vv):
    tmp = d.get(k, {})
    tmp[v] = vv
    d[k] = tmp


############## DEBUG Printing Functions ############################################

DEBUG = True
VERBOSE = False
VERBOSE_VERBOSE = False

def myprint(s):
    if DEBUG and VERBOSE and VERBOSE_VERBOSE:
        print(s)

def print_red(s):
    # send piece payload
    if VERBOSE:
        print(colors.red(s))

def print_green(s):
    # recieved piece
    print(colors.green(s))

def print_blue(s):
    # subpieces stuff
    if VERBOSE:
        print(colors.blue(s))

def print_yellow(s):
    # Signals like choke, unchoke, interested, request
    print(colors.yellow(s))

def complete_download(peer_id, result_file):
    with open(result_file, 'a') as f:
        f.write("%s Done at %d\n" % (str(peer_id), epoch_microsec()))
def start_download(peer_id, result_file):
    with open(result_file, 'a') as f:
        f.write("%s Start at %d\n" % (str(peer_id), epoch_microsec()))



################ UNCHOKE algorithms ###############################################
SPEED_UNCHOKE = False
UNCHOKE_PEERS = 4
RANDOM_UNCHOKE = False

################ Simulating Network Delays ########################################
SIMULATE_DELAYS = True
WASTE_RESOURCES = 128
DELAY_EVERY_BYTES = 64*64

def needs_delay(peer_id1, peer_id2):
    return peer_id1 % 2 != peer_id2 % 2

def slowdown_uploads():
    i = 0
    while True:
        i = i + 1
        if i > WASTE_RESOURCES:
            return


############### PREDEFINED PARAMETERS for BitTorrent Protocol #####################
CONCURRENT_PIECES = 5
PIPELINED_REQUEST = 5
DEBUG_PIECE_SUBPIECES = 20
# 256KB, for performance measurement purposes, no need to use actual file content
DEBUG_SUBPIECE_PAYLOAD = b'\x01\x02\x03\x04\x05\x06\x07\x08' * 16384 * 2


############### PROTOCOL USED COMMON CONSTANTS ####################################
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