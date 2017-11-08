#!/bin/sh
curl -k -O -G https://mds.swamid.se/md/swamid-2.0.xml
mdexport.py -t local -o swamid2.md swamid-2.0.xml