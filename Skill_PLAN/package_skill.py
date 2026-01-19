#!/usr/bin/env python3
"""
Skill Packaging Script

This script packages a skill directory into a .skill file.
"""

import os
import zipfile
import sys
from pathlib import Path


def package_skill(skill_dir, output_path=None):
    """
    Package a skill directory into a .skill file.

    Args:
        skill_dir: Path to the skill directory
        output_path: Path for the output .skill file (optional)
    """
    skill_dir = Path(skill_dir)
    if not skill_dir.exists():
        print(f"Error: Skill directory '{skill_dir}' does not exist.")
        sys.exit(1)

    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.skill"
    else:
        output_path = Path(output_path)

    print(f"Packaging skill from: {skill_dir}")
    print(f"Output file: {output_path}")

    # Validate skill directory structure
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        print("Warning: SKILL.md not found in skill directory.")
        print("Continuing anyway...")

    # Create the .skill file (which is a zip file)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as skill_zip:
        for root, dirs, files in os.walk(skill_dir):
            # Skip the output file itself if it exists in the directory
            if root == str(output_path.parent) and output_path.name in files:
                continue

            for file in files:
                file_path = Path(root) / file
                # Get the relative path from skill_dir
                arcname = file_path.relative_to(skill_dir)
                skill_zip.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\nSuccessfully packaged skill to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill-directory> [output-file]")
        print("\nExample:")
        print("  python package_skill.py claude-plan-extracted")
        print("  python package_skill.py claude-plan-extracted my-custom-skill.skill")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        package_skill(skill_dir, output_path)
    except Exception as e:
        print(f"Error packaging skill: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
