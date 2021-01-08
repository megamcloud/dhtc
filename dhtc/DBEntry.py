from time import time


class DBEntry(object):
    info_hash = ""
    addr = None
    peer_addr = None
    prev_addrs = []
    prev_peer_addrs = []
    seen = 0
    first_seen = None
    last_seen = None
    last_seen_list = []
    meta_infos = []

    def __init__(self, info_hash, addr, peer_addr):
        self.info_hash = info_hash
        self.addr = addr
        self.peer_addr = peer_addr
        self.last_seen = time()
        self.first_seen = self.last_seen
