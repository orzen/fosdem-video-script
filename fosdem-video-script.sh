#!/bin/sh

docker run -it -v $(pwd):/home/fosdem orzen/fosdem-video $@
