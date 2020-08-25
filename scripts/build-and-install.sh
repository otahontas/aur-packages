#!/bin/bash
set -e
cd /opt/pkgdir
makepkg -si --noconfirm
