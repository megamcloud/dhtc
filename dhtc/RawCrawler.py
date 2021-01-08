from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP
from os import urandom
from collections import deque
import bencoder
from loguru import logger as log
from multiprocessing import Process
from threading import Thread
from time import sleep
from struct import unpack
from socket import inet_ntoa
import codecs
import dataset

SLEEP_TIME = 1e-5
PER_NID_LEN = 20
PER_SEC_BS_TIMER = 8
MAX_PROCESSES = 1
MAX_NODE_QSIZE = 10000
NEIGHBOR_END = 14
UDP_RECV_BUFFSIZE = 65535
PER_NODE_LEN = 26
PER_NID_NIP_LEN = 24
MAGNET_PER = "magnet:?xt=urn:btih:{}"


def get_random_id():
    return urandom(PER_NID_LEN)


def get_neighbor(addr):
    return addr[:NEIGHBOR_END] + get_random_id()[NEIGHBOR_END:]


def get_nodes_info(nodes):
    l = len(nodes)
    if (l % PER_NODE_LEN) != 0:
        return []
    for i in range(0, l, PER_NODE_LEN):
        nid = nodes[i: i + PER_NID_LEN]
        ip = inet_ntoa(nodes[i + PER_NID_LEN: i + PER_NID_NIP_LEN])
        port = unpack("!H", nodes[i + PER_NID_NIP_LEN: i + PER_NODE_LEN])[0]
        yield nid, ip, port


class HNode(object):
    def __init__(self, nid, ip=None, port=None):
        self.nid = nid
        self.ip = ip
        self.port = port


class DHTServer(object):
    s = None
    bind_addr = None
    bootstrap_nodes = []

    def __init__(self, db, bind_addr, process_id, bootstrap_nodes):
        self.db = db
        self.bind_addr = bind_addr
        self.process_id = process_id
        self.nid = get_random_id()
        self.nodes = deque(maxlen=MAX_NODE_QSIZE)
        if isinstance(bootstrap_nodes, list):
            self.bootstrap_nodes = bootstrap_nodes
        self.s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.s.bind(self.bind_addr)

    def send_krpc(self, addr, msg):
        try:
            self.s.sendto(bencoder.bencode(msg), addr)
        except Exception as e:
            pass

    def send_find_node(self, addr, nid=None):
        nid = get_neighbor(nid) if nid else self.nid
        tid = get_random_id()
        msg = {
            "t": tid,
            "y": "q",
            "q": "find_node",
            "a": {
                "id": nid,
                "target": get_random_id()
            }
        }
        self.send_krpc(addr, msg)

    def bootstrap(self):
        for addr in self.bootstrap_nodes:
            self.send_find_node(addr)

    def send_find_node_forever(self):
        while True:
            try:
                n = self.nodes.popleft()
                self.send_find_node((n.ip, n.port), n.nid)
                sleep(SLEEP_TIME)
            except IndexError:
                self.bootstrap()

    def on_find_node_response(self, msg):
        for n in get_nodes_info(msg[b"r"][b"nodes"]):
            nid, ip, port = n
            if len(nid) != PER_NID_LEN or ip == self.bind_addr[0]:
                continue
            self.nodes.append(HNode(nid, ip, port))

    def save_magnet(self, info_hash):
        hih = codecs.getencoder("hex")(info_hash)[0].decode()
        magnet = MAGNET_PER.format(hih)
        self.db["magnets"].upsert({"info_hash": hih, "magnet": magnet}, ["info_hash"])
        log.info("pid_{0} - {1}".format(self.process_id, magnet))

    def send_error(self, addr, tid):
        msg = {
            "t": tid,
            "y": "e",
            "e": [202, "Server Error"]
        }
        self.send_krpc(addr, msg)

    def on_request(self, addr, msg):
        tid = msg[b"t"]
        try:
            self.save_magnet(msg[b"a"][b"info_hash"])
        except KeyError:
            self.send_error(addr, tid)

    def on_message(self, addr, msg):
        try:
            if msg[b"y"] == b"r":
                if msg[b"r"].get(b"nodes", None):
                    self.on_find_node_response(msg)
            elif msg[b"y"] == b"q":
                if msg[b"q"] == b"get_peers":
                    self.on_request(addr, msg)
                elif msg[b"q"] == b"announce_peer":
                    self.on_request(addr, msg)
        except KeyError:
            pass

    def receive_response_forever(self):
        self.bootstrap()
        while True:
            try:
                d, a = self.s.recvfrom(UDP_RECV_BUFFSIZE)
                msg = bencoder.bdecode(d)
                self.on_message(a, msg)
                sleep(SLEEP_TIME)
            except Exception as e:
                pass

    def bs_timer(self):
        t = 1
        while True:
            if t % PER_SEC_BS_TIMER == 0:
                t = 1
                self.bootstrap()
            t += 1
            sleep(1)


def _start_thread(db, host, port, offset, bootstrap_nodes):
    dht = DHTServer(db, (host, port + offset), offset, bootstrap_nodes)
    threads = [
        Thread(target=dht.send_find_node_forever),
        Thread(target=dht.receive_response_forever),
        Thread(target=dht.bs_timer),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def start_server(db, host, port, bootstrap_nodes):
    processes = []
    for i in range(MAX_PROCESSES):
        processes.append(Process(target=_start_thread, args=(db, host, port, i, bootstrap_nodes,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    start_server(dataset.connect("sqlite:///raw.db"), "0.0.0.0", 9090, [
        "udp://tracker.open-internet.nl:6969/announce",
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://exodus.desync.com:6969/announce",
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://tracker.internetwarriors.net:1337/announce",
        "udp://9.rarbg.to:2710/announce",
        "udp://public.popcorn-tracker.org:6969/announce",
        "udp://tracker.vanitycore.co:6969/announce",
        "https://1.track.ga:443/announce",
        "udp://tracker.tiny-vps.com:6969/announce",
        "udp://tracker.cypherpunks.ru:6969/announce",
        "udp://thetracker.org:80/announce",
        "udp://tracker.torrent.eu.org:451/announce",
        "udp://retracker.lanta-net.ru:2710/announce",
        "udp://bt.xxx-tracker.com:2710/announce",
        "http://retracker.telecom.by:80/announce",
        "http://retracker.mgts.by:80/announce",
        "http://0d.kebhana.mx:443/announce",
        "udp://torr.ws:2710/announce",
        "udp://open.stealth.si:80/announce",
        ("router.bittorrent.com", 6881),
        ("dht.transmissionbt.com", 6881),
        ("router.utorrent.com", 6881),
    ])
