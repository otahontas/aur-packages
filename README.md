## Description

This repo contains all the PKGBUILDS for [aur packages I maintain](https://aur.archlinux.org/packages/?SeB=m&K=otahontas).

## Tests in github

Repo is also used to test if packages are being built correctly after I've updated them in AUR. Thanks to [Build AUR Package](https://github.com/marketplace/actions/build-aur-package) Github action for making this easy!

### Statuses:

![edgedb-cli](https://github.com/otahontas/aur-packages/workflows/edgedb-cli/badge.svg)

![expo-cli](https://github.com/otahontas/aur-packages/workflows/expo-cli/badge.svg)

![kanttiinit-git](https://github.com/otahontas/aur-packages/workflows/kanttiinit-git/badge.svg)

![routahe](https://github.com/otahontas/aur-packages/workflows/routahe/badge.svg)

## Autoupdating and testing

`auto_updater.py` (currently handling only expo-cli updates) checks for new program versions. If there's  a newer version available, it writes new PKGBUILD file, builds new version inside Docker and finally pushes PKGBUILD to aur repo and this github repo.

Script runs as cron job on my personal server. For building and testing PKGBUILD inside docker, I'm using [aur-pkgbuild-tester](https://github.com/Stunkymonkey/aur-pkgbuild-tester). 

## TODO
- Move auto_updater to github actions, so everything is in the same place
