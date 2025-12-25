#!/usr/bin/env python3
"""
Version Bumping Script for SpyHunt

This script automatically increments the version number across all project files.
Supports semantic versioning: major.minor.patch

Location: .github/bump_version.py
This script is designed to run from the .github directory but can also be run
from the project root.

Usage:
    python .github/bump_version.py [major|minor|patch]
    cd .github && python bump_version.py [major|minor|patch]
    
Examples:
    python .github/bump_version.py patch  # 4.0.0 -> 4.0.1
    python .github/bump_version.py minor  # 4.0.0 -> 4.1.0
    python .github/bump_version.py major  # 4.0.0 -> 5.0.0
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Tuple
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def get_project_root() -> Path:
    """
    Get the project root directory.
    Works whether script is run from .github/ or project root.
    """
    script_dir = Path(__file__).parent.resolve()
    
    # If we're in .github directory, go up one level
    if script_dir.name == '.github':
        return script_dir.parent
    
    # Otherwise assume we're in project root
    return script_dir


def get_current_version(file_path: Path) -> str:
    """Extract current version from pyproject.toml"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = file_path.read_text(encoding='utf-8')
    match = re.search(r'^version = ["\']([0-9]+\.[0-9]+\.[0-9]+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Version not found in pyproject.toml")


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into (major, minor, patch) tuple"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, parts))


def bump_version(version: str, bump_type: str) -> str:
    """Increment version based on bump type"""
    major, minor, patch = parse_version(version)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version in pyproject.toml"""
    if not file_path.exists():
        print(f"⚠️  Warning: {file_path} not found, skipping")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # Update version line
    new_content = re.sub(
        r'^version = ["\']' + re.escape(old_version) + r'["\']',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    if new_content == content:
        print(f"⚠️  Warning: No version found in {file_path}")
        return
    
    file_path.write_text(new_content, encoding='utf-8')
    print(f"✓ Updated {file_path.relative_to(get_project_root())}")


def update_init_file(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version in __init__.py if it exists"""
    if not file_path.exists():
        print(f"⚠️  Warning: {file_path} not found, skipping")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # Update __version__ if it exists
    if '__version__' in content:
        new_content = re.sub(
            r'__version__ = ["\']' + re.escape(old_version) + r'["\']',
            f'__version__ = "{new_version}"',
            content
        )
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✓ Updated {file_path.relative_to(get_project_root())}")
        else:
            print(f"⚠️  Warning: __version__ not updated in {file_path}")
    else:
        # Add version if not present
        lines = content.split('\n')
        insert_index = 0
        
        # Find appropriate place to insert
        if lines and (lines[0].startswith('#') or lines[0].startswith('"""')):
            insert_index = 1
            if lines[0].startswith('"""'):
                # Find end of docstring
                for i, line in enumerate(lines[1:], 1):
                    if '"""' in line:
                        insert_index = i + 1
                        break
        
        lines.insert(insert_index, f'\n__version__ = "{new_version}"')
        file_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✓ Added __version__ to {file_path.relative_to(get_project_root())}")


def update_readme(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version references in README.md"""
    if not file_path.exists():
        print(f"⚠️  Info: {file_path} not found, skipping")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # Update version badges and references
    patterns = [
        (r'spyhunt/' + re.escape(old_version), f'spyhunt/{new_version}'),
        (r'v' + re.escape(old_version), f'v{new_version}'),
        (r'version-' + re.escape(old_version), f'version-{new_version}'),
        (r'Version: ' + re.escape(old_version), f'Version: {new_version}'),
    ]
    
    new_content = content
    updated = False
    
    for pattern, replacement in patterns:
        if re.search(pattern, new_content):
            new_content = re.sub(pattern, replacement, new_content)
            updated = True
    
    if updated:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✓ Updated {file_path.relative_to(get_project_root())}")


def create_version_file(file_path: Path, version: str) -> None:
    """Create a VERSION file with the current version"""
    file_path.write_text(version, encoding='utf-8')
    print(f"✓ Created/Updated {file_path.relative_to(get_project_root())}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Bump version number for SpyHunt project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .github/bump_version.py patch    # Increment patch version (4.0.0 -> 4.0.1)
  python .github/bump_version.py minor    # Increment minor version (4.0.0 -> 4.1.0)
  python .github/bump_version.py major    # Increment major version (4.0.0 -> 5.0.0)
  
  # With dry-run:
  python .github/bump_version.py patch --dry-run

  # From .github directory:
  cd .github && python bump_version.py patch
        """
    )
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump to perform'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Get project root directory
    root_dir = get_project_root()
    print(f"Project root: {root_dir}")
    print()
    
    # Define file paths relative to project root
    pyproject_path = root_dir / 'pyproject.toml'
    init_path = root_dir / 'spyhunt' / '__init__.py'
    readme_path = root_dir / 'README.md'
    version_path = root_dir / 'VERSION'
    
    # Verify pyproject.toml exists
    if not pyproject_path.exists():
        print(f"❌ Error: {pyproject_path} not found!", file=sys.stderr)
        print(f"   Please run this script from the project root or .github directory", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Get current version
        current_version = get_current_version(pyproject_path)
        print(f"Current version: {current_version}")
        
        # Calculate new version
        new_version = bump_version(current_version, args.bump_type)
        print(f"New version:     {new_version}")
        print(f"Bump type:       {args.bump_type}")
        
        if args.dry_run:
            print("\n" + "="*60)
            print("[DRY RUN] Would update the following files:")
            print("="*60)
            if pyproject_path.exists():
                print(f"  ✓ {pyproject_path.relative_to(root_dir)}")
            if init_path.exists():
                print(f"  ✓ {init_path.relative_to(root_dir)}")
            if readme_path.exists():
                print(f"  ✓ {readme_path.relative_to(root_dir)}")
            print(f"  ✓ {version_path.relative_to(root_dir)} (will be created/updated)")
            print("="*60)
            return
        
        # Update all files
        print("\n" + "="*60)
        print("Updating files...")
        print("="*60)
        update_pyproject_toml(pyproject_path, current_version, new_version)
        update_init_file(init_path, current_version, new_version)
        update_readme(readme_path, current_version, new_version)
        create_version_file(version_path, new_version)
        
        print("\n" + "="*60)
        print(f"✅ Successfully bumped version: {current_version} → {new_version}")
        print("="*60)
        print("\nNext steps:")
        print(f"  1. Review the changes:")
        print(f"     git diff")
        print(f"  2. Commit the changes:")
        print(f"     git add -A && git commit -m 'chore: bump version to {new_version}'")
        print(f"  3. Create a tag:")
        print(f"     git tag -a v{new_version} -m 'Release v{new_version}'")
        print(f"  4. Push to repository:")
        print(f"     git push origin main --tags")
        print()
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

