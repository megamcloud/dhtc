import dataset
import libtorrent as lt
from time import sleep

import dhtc


class RawDBReader(object):
    hashes = []

    def __init__(self, db, routers):
        self.db = db
        self.s = lt.session()
        self.s.listen_on(6891, 6891)
        for r in routers:
            self.s.add_dht_router(r[0], r[1])
        self.s.start_dht()

    def run(self):
        for m in self.db["magnets"]:
            self.hashes.append(lt.add_magnet_uri(self.s, m["magnet"], {
                "save_path": "./data",
                'storage_mode': lt.storage_mode_t(2)
            }))

        while len(self.hashes) > 0:
            for h in self.hashes:
                if h.has_metadata():
                    print(h.get_torrent_info())
            sleep(2)


if __name__ == '__main__':
    r = RawDBReader(dataset.connect("sqlite:///raw.db"), list(dhtc.BOOTSTRAP_NODES))
    r.run()
