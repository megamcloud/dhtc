import shelve
from random import choice

from .DBEntry import DBEntry


class Database(object):
    def __init__(self, path="dht.db"):
        self.db = shelve.open(path)

    def has_key(self, key):
        return key in self.db.keys()

    def get(self, key, addr=None, peer_addr=None) -> DBEntry:
        return self.db.get(key, DBEntry(key, addr, peer_addr))

    def get_random_title(self):
        k = list(self.db.keys())
        if len(k) > 0:
            i = self.get(choice(k))
            if len(i.meta_infos) > 0:
                return choice(i.meta_infos)["title"]
        return "no entries yet"

    def get_count(self):
        return len(self.db.keys())

    def save(self, e: DBEntry):
        self.db[e.info_hash] = e
        self.db.sync()

    def close(self):
        self.db.close()
