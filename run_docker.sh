#!/bin/bash
mkdir -p sync
docker run -d -p 5000:5000 -v $PWD:/dropnot --restart=always --name dropnot-server dropnot-server
