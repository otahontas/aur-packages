## Description

This repo contains all the PKGBUILDS for [aur packages I maintain](https://aur.archlinux.org/packages/?SeB=m&K=otahontas).

## Tests

Repo is also used to test if packages are being built correctly after I've updated them in AUR. Thanks to [Build AUR Package](https://github.com/marketplace/actions/build-aur-package) Github action for making this easy!

### Statuses:

![edgedb-cli](https://github.com/otahontas/aur-packages/workflows/edgedb-cli/badge.svg)

![expo-cli](https://github.com/otahontas/aur-packages/workflows/expo-cli/badge.svg)

![kanttiinit-git](https://github.com/otahontas/aur-packages/workflows/kanttiinit-git/badge.svg)

![routahe](https://github.com/otahontas/aur-packages/workflows/routahe/badge.svg)

## TODO / Notes

Repo currently tests package building after they've been published to AUR. This of course should be other way around. Two thing should done:
- add webhook checks for new releases for different packages
- add action (triggered by webook) that gets new release, builds new pkgbuild, tests it and if everything goes well, pushes new version to aur
