#!/bin/bash
set -e
# Create user
useradd -m -g wheel -s /bin/sh tester
echo "tester ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
chown -R tester:wheel /opt/pkgdir
# Install makepkg deps with full upgrade, e.g. no plain pacman -Sy
# See: https://wiki.archlinux.org/index.php/System_maintenance#Avoid_certain_pacman_commands
pacman -Suy sudo base-devel --noconfirm --needed
# Build and install the package as the `tester' user with recommended flags:
# See: https://wiki.archlinux.org/index.php/Arch_User_Repository#Installing_and_upgrading_packages
su - tester /opt/scripts/build-and-install.sh
