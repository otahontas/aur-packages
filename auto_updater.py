#!/usr/bin/env python3
import requests
import hashlib
import subprocess
import logging
from string import Template
from pathlib import Path
from packaging import version

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
templates_folder = Path(".") / "PKGBUILD_templates/"


def main() -> None:
    submodule_folder = Path(".") / "expo-cli"
    base_url = "https://registry.npmjs.org/expo-cli"

    # Open current pkgbuild and check for current version
    current_pkgbuild = submodule_folder / "PKGBUILD"
    with current_pkgbuild.open() as file:
        try:
            current_version = version.parse(
                next(
                    line for line in file.readlines() if line.startswith("pkgver")
                ).split("=")[1]
            )
        except StopIteration:
            logging.error("There was no pkgver line in PKGBUILD")
            return

    # Get latest version number from npm registry
    latest_version = version.parse(requests.get(base_url).json()["dist-tags"]["latest"])

    # If versions differ, update PKGBUILD file based on template file
    if latest_version != current_version:
        template = templates_folder / "expo-cli"

        # Calculate sha512sum for package
        package = requests.get(f"{base_url}/-/expo-cli-{latest_version}.tgz")
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

        # Write new PKGBUILD file
        pkgbuild_file = submodule_folder / "PKGBUILD"
        pkgbuild_file.write_text(result)

        # Run tests in docker
        try:
            subprocess.run("./aur-pkgbuild-tester.sh expo-cli", shell=True, check=True)
        except subprocess.CalledProcessError as error:
            logging.error(
                "Wasn't able to build expo-cli with newest PKGBUILD, "
                f"more details: {error}"
            )
            return

        # Git add, commit, cleanup and push submodule
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
                cwd=submodule_folder,
            )
        except subprocess.CalledProcessError as error:
            logging.error(
                "Wasn't able to run git commands for expo-cli submodule, "
                f"more details: {error}"
            )
            return

        # Git add, commit and push main repo
        try:
            subprocess.run(
                (
                    "git add expo-cli && "
                    f'git commit -m "Bump expo-cli version to {latest_version}" && '
                    "git push origin master"
                ),
                shell=True,
                check=True,
                cwd=Path("."),
            )
        except subprocess.CalledProcessError as error:
            logging.error(
                "Wasn't able to run git commands for main repo, "
                f"more details: {error}"
            )
            return


if __name__ == "__main__":
    main()
