#!/usr/bin/env python3
import requests
import hashlib
import subprocess
import logging
import operator
from string import Template
from pathlib import Path
from functools import reduce
from packaging import version, Version, LegacyVersion
from collections import namedtuple
from typing import Any, Optional

# Logging format and logger
FORMAT = "[%(asctime)s][%(process)d %(processName)s][%(levelname)-4s] (L:%(lineno)s) %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

# Packages to update and other needed files
Package = namedtuple("Package", ["name", "info_url", "version_path", "latest_package"])
packages = [
    Package(
        "expo-cli",
        "https://registry.npmjs.org/expo-cli",
        ["dist-tags", "latest"],
        lambda version: f"https://registry.npmjs.org/expo-cli/-/expo-cli-{version}.tgz",
    )
]

templates_folder = Path(".") / "PKGBUILD_templates/"


def recursively_get_value(data: Any, path: list[str]) -> str:
    """Walk given path on data, return value."""
    return str(reduce(operator.getitem, path, data))


def get_current_version(package: Package) -> Optional[LegacyVersion | Version]:
    """Get current package version from PKGBUILD file."""
    current_pkgbuild = Path(".") / package.name / "PKGBUILD"
    with current_pkgbuild.open() as file:
        try:
            return version.parse(
                next(
                    line for line in file.readlines() if line.startswith("pkgver")
                ).split("=")[1]
            )
        except StopIteration:
            LOG.error("PKGBUILD was broken, no line with pkgver found!")


def get_latest_version(package: Package) -> Optional[LegacyVersion | Version]:
    """Get latest package version from upstream."""
    package_info = requests.get(package.info_url).json()
    return version.parse(recursively_get_value(package_info, package.version_path))

def get_shasum_for_latest_package(package: Package) -> None:



def main() -> None:
    LOG.info("Starting auto updater")
    for package in packages:
        LOG.info(f"Checking updates for {package.name}")

        current_version = get_current_version(package)
        latest_version = get_latest_version(package)

        if latest_version == current_version:
            LOG.info("No updates")
            continue

        template = templates_folder / "expo-cli"

        # Calculate sha512sum for package
        package = requests.get(package.latest_package(latest_version))
        message = hashlib.sha512()
        for data in package.iter_content(8192):  # iter by chunks of 8kB
            message.update(data)

        # Replace variables in template
        replacements = {
            "latest_pkgver": latest_version,
            "latest_shasum": message.hexdigest(),
        }
        with template.open() as file:
            src = Template(file.read())
            result = src.substitute(replacements)

        print(result)
        # Write new PKGBUILD file
        # pkgbuild_file = submodule_folder / "PKGBUILD"
        # pkgbuild_file.write_text(result)

        # Run tests in docker
        # try:
        #     subprocess.run(
        #         "./aur-pkgbuild-tester.sh expo-cli", shell=True, check=True
        #     )
        # except subprocess.CalledProcessError as error:
        #     logging.error(
        #         "Wasn't able to build expo-cli with newest PKGBUILD, "
        #         f"more details: {error}"
        #     )
        #     return

        # # Git add, commit, cleanup and push submodule
        # try:
        #     subprocess.run(
        #         (
        #             "git add . && "
        #             f'git commit -m "Bump version to {latest_version}" && '
        #             "git clean -xfd && "
        #             "git push origin master"
        #         ),
        #         shell=True,
        #         check=True,
        #         cwd=submodule_folder,
        #     )
        # except subprocess.CalledProcessError as error:
        #     logging.error(
        #         "Wasn't able to run git commands for expo-cli submodule, "
        #         f"more details: {error}"
        #     )
        #     return

        # # Git add, commit and push main repo
        # try:
        #     subprocess.run(
        #         (
        #             "git add expo-cli && "
        #             f'git commit -m "Bump expo-cli version to {latest_version}" && '
        #             "git push origin master"
        #         ),
        #         shell=True,
        #         check=True,
        #         cwd=Path("."),
        #     )
        # except subprocess.CalledProcessError as error:
        #     logging.error(
        #         "Wasn't able to run git commands for main repo, "
        #         f"more details: {error}"
        #     )
        #         return


if __name__ == "__main__":
    main()
