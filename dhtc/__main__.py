from loguru import logger as log
from argparse import ArgumentParser
import asyncio

import dhtc


def main():
    ap = ArgumentParser()
    ap.add_argument("-ld", "--log-dir", default="log", help="where to log to")
    ap.add_argument("-db", "--database", default="dht", help="the database path")
    ap.add_argument("-w", "--web-interface", action="store_true", help="Spin up the web interface")
    ap.add_argument("-wh", "--web-interface-host", default="127.0.0.1", help="Public or not")
    ap.add_argument("-wp", "--web-interface-port", default=4200, help="The port on which the webinterface runs")
    ap.add_argument("-bn", "--bootstrap-node", nargs='+', action="append", help="format: 'ip:port'", default=[[]])
    a = ap.parse_args()

    if not a.log_dir.endswith("/"):
        a.log_dir += "/"

    log.add("%s{time}.log" % a.log_dir, rotation="100 MB")
    log.info("Using {} bootstrap nodes.", len(dhtc.BOOTSTRAP_NODES))
    log.info("Using database '{}'.", a.database)
    log.info("Logging to {}.", a.log_dir)

    nodes = list(dhtc.BOOTSTRAP_NODES)

    if len(a.bootstrap_node[0]) > 0:
        for node in a.bootstrap_node[0]:
            n = node.split(":")
            nodes.append((n[0], int(n[1])))

    dhtc.BOOTSTRAP_NODES = tuple(nodes)

    db = dhtc.Database(a.database)

    try:
        c = dhtc.Crawler(db, dhtc.BOOTSTRAP_NODES)
        if a.web_interface:
            log.info("Running Website on '{}:{}'.", a.web_interface_host, a.web_interface_port)
            asyncio.get_event_loop() \
                .run_until_complete(dhtc.create_webserver(db, a.web_interface_host, a.web_interface_port))
        log.info("Running crawler.")
        c.run(0)
    except Exception as e:
        log.exception(e)
        db.close()


if __name__ == '__main__':
    main()
