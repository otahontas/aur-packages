#!/bin/bash
set -e
DATADIR=$(readlink -f $1)
if [ ! -d "$DATADIR" ]; then
    echo "First argument must be a directory containing PKGBUILD"
    exit 1
fi
docker run --rm -it \
    -v "$DATADIR/:/opt/pkgdir" \
    -v "$(pwd)/scripts:/opt/scripts" \
    archlinux/base \
    /opt/scripts/entrypoint.sh
