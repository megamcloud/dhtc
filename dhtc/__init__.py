from .Crawler import Crawler
from .Database import Database
from .WebServer import create_webserver


BOOTSTRAP_NODES = (
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881),
    ("tracker.opentrackr.org", 1337),
    ("9.rarbg.to", 2710),
    ("tracker.internetwarriors.net", 1337),
    ("tracker.cyberia.is", 6969),
    ("exodus.desync.com", 6969),
    ("3rt.tace.ru", 60889),
    ("explodie.org", 6969),
    ("p4p.arenabg.ch", 1337),
    ("tracker.tiny-vps.com", 6969),
    ("open.stealth.si", 80),
    ("www.torrent.eu.org", 451),
    ("tracker.zerobytes.xyz", 1337),
    ("tracker.torrent.eu.org", 451),
    ("tracker.ds.is", 6969),
    ("retracker.lanta-net.ru", 2710),
    ("open.demonii.si", 1337),
    ("tracker4.itzmx.com", 2710),
    ("tracker.moeking.me", 6969),
    ("tracker.open-internet.nl", 6969),
    ("tracker.coppersurfer.tk", 6969),
    ("9.rarbg.to", 2710),
    ("public.popcorn-tracker.org", 6969),
    ("tracker.vanitycore.co", 6969),
    ("tracker.cypherpunks.ru", 6969),
    ("thetracker.org", 6969),
    ("bt.xxx-tracker.com", 2710),
    ("retracker.telecom.by", 80),
    ("retracker.mgts.by", 80),
    ("torr.ws", 2710)
)

__all__ = ["Crawler", "Database", "BOOTSTRAP_NODES", "create_webserver"]
