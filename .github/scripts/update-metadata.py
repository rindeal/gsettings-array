#!/usr/bin/env python3
#
# SPDX-FileCopyrightText:  ANNO DOMINI 2024  Jan Chren ~rindeal
#
# SPDX-License-Identifier: GPL-3.0-only OR GPL-2.0-only
#
"""
PyPI Metadata Updater

This script updates metadata for a Python package before publishing to PyPI.
It is designed to be run from a GitHub Action on a tagged push event.
"""

import argparse
import re
import sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Dict, Self

import tomlkit
from tomlkit.toml_document import TOMLDocument
from loguru import logger


# Configure loguru with the specified format
logger.remove()
logger.add(sys.stderr, colorize=True, format="<level>{level.name[0]}</> {message}")
logger = logger.opt(colors=True)


@dataclass
class CommonMetadata:
    """Dataclass to hold common metadata for a Python package."""
    version:     str = ''
    homepage:    str = ''
    description: str = ''


@dataclass
class Metadata(CommonMetadata):
    """Dataclass to hold all metadata for a Python package."""
    prog:      str = ''
    license:   str = ''
    copyright: str = ''

    @classmethod
    def from_common(cls, common: CommonMetadata, prog: str | None = None,
                    license: str | None = None, copyright: str | None = None) -> Self:
        m = cls(
            version     = common.version,
            homepage    = common.homepage,
            description = common.description,
        )
        if prog      is not None: m.prog      = prog
        if license   is not None: m.license   = license
        if copyright is not None: m.copyright = copyright
        return m


class PyProjectTomlFile:
    DEFAULT_PATH = Path('pyproject.toml')

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path

    def read_all(self) -> TOMLDocument:
        with self.path.open('r') as f:
            return tomlkit.parse(f.read())

    def write_all(self, toml_content: TOMLDocument) -> None:
        with self.path.open('w') as f:
            f.write(tomlkit.dumps(toml_content).strip())
        logger.success("✅ <green>Updated <bold>{}</></>", self.path)


def get_script_files(toml_content: TOMLDocument) -> Dict[str, str]:
    """
    Extract script files from pyproject.toml.

    Args:
        toml_content (TOMLDocument): The parsed TOML content.

    Returns:
        Dict[str, str]: A dictionary mapping program names to script file names.
    """
    scripts = toml_content['tool']['poetry']['scripts']
    return {prog: f"{script.split(':')[0]}.py" for prog, script in scripts.items()}


def update_metadata_from_file(metadata: Metadata, file_path: Path) -> None:
    """
    Update metadata object with license and copyright information from a file.

    Args:
        metadata (Metadata): The metadata object to update.
        file_path (Path): Path to the file to parse.
    """
    content = file_path.read_text()
    
    license_match = re.search(r"^\s*#\s*SPDX-License-Identifier:\s*(.*?)\s*$", content, re.MULTILINE)
    if license_match:
        metadata.license = license_match.group(1)
    
    copyright_lines = []
    for line in content.split('\n'):
        if copyright_match := re.match(r"^\s*#\s*SPDX-FileCopyrightText:\s*(.*?)\s*$", line):
            copyright_lines.append(copyright_match.group(1))
        elif copyright_lines:
            break
    metadata.copyright = '\n'.join(copyright_lines)


def update_script_file(file_path: Path, metadata: Metadata) -> None:
    """
    Update metadata placeholders in a script file.

    Args:
        file_path (Path): Path to the script file.
        metadata (Metadata): The metadata to insert.
    """
    content = file_path.read_text()
    
    for field in fields(metadata):
        placeholder = f"@@{field.name.upper()}@@"
        if value := getattr(metadata, field.name):
            content = content.replace(placeholder, value)
            for v in value.split('\n'):
                logger.info("  🔄 <yellow>Updated <y><b>{:<13}</></> <b>{}</></>", f"{field.name}:", v)
    
    file_path.write_text(content)
    logger.success("✅ <green>Updated <bold>{}</></>", file_path)


def process_script_file(file_path: Path, metadata: Metadata) -> None:
    """
    Process a single script file, updating its metadata.

    Args:
        file_path (Path): Path to the script file.
        prog (str): The program name associated with this script.
        common_metadata (CommonMetadata): Common metadata for all scripts.
    """
    if not file_path.exists():
        logger.warning("⚠️ <red><bold>{}</> not found. Skipping.</>", file_path)
        return

    logger.info("🔍 <blue>Processing <bold>{}</></>", file_path)
    update_metadata_from_file(metadata, file_path)
    update_script_file(file_path, metadata)


def main() -> None:
    """Main function to update metadata for PyPI package."""
    parser = argparse.ArgumentParser(description="Update metadata for PyPI package")
    parser.add_argument('version', help="Version tag from GitHub Action")
    args = parser.parse_args()

    logger.info("🚀 <magenta>Starting PyPI Metadata Updater</>")

    # Read pyproject.toml
    pyproject_toml_file = PyProjectTomlFile()
    toml_content = pyproject_toml_file.read_all()

    # Get common metadata from pyproject.toml
    poetry_section = toml_content['tool']['poetry']
    common_metadata = CommonMetadata(
        version     = args.version,
        homepage    = poetry_section.get('homepage', ""),
        description = poetry_section.get('description', "")
    )
    del poetry_section

    logger.info("📊 <cyan>Common Metadata:</>")
    logger.info("  🏷️  <cyan>Version:     <bold>{}</></>", common_metadata.version)
    logger.info("  🌐 <cyan>Homepage:    <bold>{}</></>", common_metadata.homepage)
    logger.info("  📝 <cyan>Description: <bold>{}</></>", common_metadata.description)

    # Update pyproject.toml with new version
    toml_content['tool']['poetry']['version'] = common_metadata.version
    pyproject_toml_file.write_all(toml_content)

    # Get script files
    script_files = get_script_files(toml_content)
    logger.info("📁 <yellow>Found script files:</>")
    for prog, file_name in script_files.items():
        logger.info("  📄 <yellow>{:<15} <bold>{}</></>", f"{prog}:", file_name)

    # Update each script file
    for prog, file_name in script_files.items():
        metadata = Metadata.from_common(common_metadata, prog=prog)
        process_script_file(Path(file_name), metadata)

    logger.success("🎉 <green><u>PyPI Metadata Update Complete</></>")


if __name__ == '__main__':
    main()