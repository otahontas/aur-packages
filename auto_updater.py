#!/usr/bin/env python3
import hashlib
import logging
import subprocess
from collections import namedtuple
from functools import reduce
from operator import getitem
from pathlib import Path
from string import Template
from typing import Any, Optional, Union

import requests
from packaging import version
from packaging.version import LegacyVersion, Version

FORMAT = "[%(asctime)s][%(process)d %(processName)s][%(levelname)-4s] (L:%(lineno)s) %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

Vers = Union[LegacyVersion, Version]


Package = namedtuple("Package", ["name", "info_url", "version_path", "latest_package"])


def recursively_get_value(data: Any, path: list[str]) -> str:
    """Walk given path on data, return value."""
    return str(reduce(getitem, path, data))


def get_current_version(package: Package) -> Optional[Vers]:
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


def get_latest_version(package: Package) -> Optional[Vers]:
    """Get latest package version from upstream."""
    package_info = requests.get(package.info_url).json()
    return version.parse(recursively_get_value(package_info, package.version_path))


def get_shasum_for_latest_package(package: Package, latest_version: Vers) -> str:
    """Download newest package and calculate its checksum."""
    file = requests.get(package.latest_package(latest_version))
    message = hashlib.sha512()
    for data in file.iter_content(8192):  # iter by chunks of 8kB
        message.update(data)
    return message.hexdigest()


def create_new_pkgbuild(package: Package, latest_version: Vers) -> None:
    """Create new PKGBUILD by substituting stuff in template, then write it to file."""
    LOG.info(f"Creating pkgbuild")
    template = Path(".") / "PKGBUILD_templates" / package.name
    replacements = {
        "latest_pkgver": latest_version,
        "latest_shasum": get_shasum_for_latest_package(package, latest_version),
    }
    with template.open() as file:
        pkgbuild = Template(file.read()).substitute(replacements)

    path = Path(".") / package.name / "PKGBUILD"
    path.write_text(pkgbuild)


def run_docker_tests(package: Package) -> None:
    """Run docker tests with external script."""
    LOG.info(f"Running tests in docker")
    try:
        subprocess.run(
            f"./aur-pkgbuild-tester.sh {package.name}", shell=True, check=True
        )
    except subprocess.CalledProcessError as error:
        logging.error(
            f"Wasn't able to build {package.name} with newest PKGBUILD, "
            f"more details: {error}"
        )
        return


def run_git_operations(package: Package, latest_version: Vers) -> None:
    """Add, commit and push submodule and main folder. Also cleanup submodule."""
    try:
        subprocess.run(
            (
                "git add . && "
                f'git commit -m "Bump version to {latest_version}" && '
                "git clean -xfd && "
                "git push origin master"
            ),
            shell=True,
            check=True,
            cwd=Path(".") / package.name,
        )
    except subprocess.CalledProcessError as error:
        logging.error(
            f"Wasn't able to run git commands for {package.name} submodule, "
            f"more details: {error}"
        )
        return

    # Git add, commit and push main repo
    try:
        subprocess.run(
            (
                "git add expo-cli && "
                f'git commit -m "Bump {package.name} version to {latest_version}" && '
                "git push origin master"
            ),
            shell=True,
            check=True,
            cwd=Path("."),
        )
    except subprocess.CalledProcessError as error:
        logging.error(
            "Wasn't able to run git commands for main repo, " f"more details: {error}"
        )
        return


def main() -> None:
    LOG.info("Starting auto updater")
    packages = [
        Package(
            "expo-cli",
            "https://registry.npmjs.org/expo-cli",
            ["dist-tags", "latest"],
            lambda version: f"https://registry.npmjs.org/expo-cli/-/expo-cli-{version}.tgz",
        )
    ]
    for package in packages:
        LOG.info(f"Checking updates for {package.name}")

        current_version = get_current_version(package)
        if not current_version:
            LOG.error("Current version cannot be empty!")
            continue

        latest_version = get_latest_version(package)
        if not latest_version:
            LOG.error("Latest version cannot be empty!")
            continue

        if latest_version == current_version:
            LOG.info("No updates")
            continue
        LOG.info(f"Updating to {latest_version}")

        create_new_pkgbuild(package, latest_version)
        run_docker_tests(package)
        run_git_operations(package, latest_version)
        LOG.info(f"Succesfully updated!")


if __name__ == "__main__":
    main()