## Description

This repo contains all the PKGBUILDS for [aur packages I maintain](https://aur.archlinux.org/packages/?SeB=m&K=otahontas).

## Updating testing

Github actions workflow runs updater twice a week for packages that are not based on git. Updater checks for new program versions and, if there's  a newer version available, writes new PKGBUILD file.

This is still WIP, todo:
- test new pgkbuild after it has been built
- if all ok, commit pkgbuild
- then push to aur

Also todo:
- remove package testing after they've been updated in AUR
- separate updater workflow to parallel jobs: one job per package. Atm everything is ran in one workflow.

## Tests in github

Repo is also used to test if packages are being built correctly after I've updated them in AUR. Thanks to [Build AUR Package](https://github.com/marketplace/actions/build-aur-package) Github action for making this easy!

### Statuses:

![edgedb-cli](https://github.com/otahontas/aur-packages/workflows/edgedb-cli/badge.svg)

![expo-cli](https://github.com/otahontas/aur-packages/workflows/expo-cli/badge.svg)

![kanttiinit-git](https://github.com/otahontas/aur-packages/workflows/kanttiinit-git/badge.svg)

![routahe](https://github.com/otahontas/aur-packages/workflows/routahe/badge.svg)
