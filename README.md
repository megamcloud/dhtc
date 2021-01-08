# dhtc
## tl;dr
it's just another dht crawler <br>
## features
- [X] dht crawling
  - [ ] multiprocess
    - [ ] multi threaded
- [X] web ui
    - [X] dashboard
    - [X] search
- [X] containerized
    
## install
```shell
pip3 install git+https://github.com/nbdy/dhtc
```

## usage
```shell
dhtc --help

usage: dhtc [-h] [-ld LOG_DIR] [-db DATABASE] [-w] [-wh WEB_INTERFACE_HOST] [-wp WEB_INTERFACE_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -ld LOG_DIR, --log-dir LOG_DIR
                        where to log to
  -db DATABASE, --database DATABASE
                        the database path
  -w, --web-interface   Spin up the web interface
  -wh WEB_INTERFACE_HOST, --web-interface-host WEB_INTERFACE_HOST
                        Public or not
  -wp WEB_INTERFACE_PORT, --web-interface-port WEB_INTERFACE_PORT
                        The port on which the webinterface runs
```