#!/usr/bin/env sh

# Fail on error
set -e

# Read srcdir argument
SRCDIR="$(readlink -f "$1")"

# Create user
useradd -m -g wheel -s /bin/sh tester
echo "tester ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
chown -R tester:wheel "/github/workspace/$SRCDIR"

# Run makepkg
cd /github/workspace/expo-cli
makepkg -srci
