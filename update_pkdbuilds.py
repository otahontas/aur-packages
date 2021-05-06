import hashlib
import logging
from collections import namedtuple
from functools import reduce
from operator import getitem
from pathlib import Path
from string import Template
from typing import Any, Optional, Union, Final

import requests
from packaging import version
from packaging.version import LegacyVersion, Version

# Set up logging
FORMAT = "[%(asctime)s][%(process)d %(processName)s][%(levelname)-4s] (L:%(lineno)s) %(funcName)s: %(message)s"
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
LOG: Final = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

# Custom types and other
Vers = Union[LegacyVersion, Version]
Package = namedtuple("Package", ["name", "info_url", "version_path", "latest_package"])

# Constants
SCRIPT_FOLDER: Final = Path(__file__).parent


def recursively_get_value(data: Any, path: list[str]) -> str:
    """Walk given path on data, return value."""
    return str(reduce(getitem, path, data))


def get_current_version(package: Package) -> Optional[Vers]:
    """Get current package version from PKGBUILD file."""
    pkgbuild_path = SCRIPT_FOLDER / package.name / "PKGBUILD"
    with pkgbuild_path.open() as file:
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
    CHUNK_SIZE: Final = 8192
    file = requests.get(package.latest_package(latest_version))
    message = hashlib.sha512()
    for data in file.iter_content(CHUNK_SIZE):
        message.update(data)
    return message.hexdigest()


def create_new_pkgbuild(package: Package, latest_version: Vers) -> None:
    """Create new PKGBUILD by substituting stuff in template, then write it to file."""
    LOG.info(f"Creating pkgbuild")
    template = SCRIPT_FOLDER / "PKGBUILD_templates" / package.name
    replacements = {
        "latest_pkgver": latest_version,
        "latest_shasum": get_shasum_for_latest_package(package, latest_version),
    }
    with template.open() as file:
        pkgbuild = Template(file.read()).substitute(replacements)

    pkgbuild_path = SCRIPT_FOLDER / package.name / "PKGBUILD"
    pkgbuild_path.write_text(pkgbuild)

    print("PKGBUILD that was written")
    print(pkgbuild)


def main() -> None:
    LOG.info("Starting updater")
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

    LOG.info("Finished")


if __name__ == "__main__":
    main()
