#!/usr/bin/env python3
"""
Deploy Slime OS 2 to Pico Calc Hardware
Automatically detects and uploads changed files
"""

import os
import sys
import json
import hashlib
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Set, List


class PicoDeployer:
    def __init__(self, source_dir: str, clean: bool = False, verbose: bool = False):
        self.source_dir = Path(source_dir).resolve()
        self.clean = clean
        self.verbose = verbose
        self.cache_file = self.source_dir.parent / ".deploy_cache.json"
        self.ignore_file = self.source_dir.parent / "slime_os_2" / ".slime_ignore"
        self.ignore_patterns: List[str] = []
        self.file_hashes: Dict[str, str] = {}
        self.uploaded_count = 0
        self.skipped_count = 0

    def load_ignore_patterns(self):
        """Load patterns from .slime_ignore file"""
        if self.ignore_file.exists():
            with open(self.ignore_file, 'r') as f:
                self.ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith('#')
                ]


    def load_cache(self) -> Dict[str, str]:
        """Load previously stored file hashes"""
        if self.clean or not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            return {}

    def save_cache(self):
        """Save current file hashes to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def should_ignore(self, path: Path) -> bool:
        """Check if path matches any ignore pattern"""
        rel_path = str(path.relative_to(self.source_dir))
        for pattern in self.ignore_patterns:
            # Simple pattern matching
            if pattern.startswith('*'):
                # Extension pattern like *.pyc
                if rel_path.endswith(pattern[1:]):
                    return True
            elif pattern in rel_path:
                # Substring match
                return True
        return False

    def check_mpremote(self) -> bool:
        """Check if mpremote is installed"""
        try:
            subprocess.run(['mpremote', '--version'],
                         capture_output=True,
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_device(self) -> bool:
        """Check if Pico is connected"""
        try:
            result = subprocess.run(['mpremote', 'connect', 'list'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def mkdir_remote(self, remote_path: str):
        """Create directory on Pico"""
        try:
            subprocess.run(['mpremote', 'mkdir', f':{remote_path}'],
                         capture_output=True,
                         timeout=10)
        except Exception as e:
            if self.verbose:
                print(f"    (mkdir {remote_path} skipped: {e})")

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Upload a single file to Pico"""
        try:
            if self.verbose:
                print(f"  → {local_path.relative_to(self.source_dir)} → :{remote_path}")
            else:
                print(f"  → {local_path.relative_to(self.source_dir)}")

            subprocess.run(['mpremote', 'cp', str(local_path), f':{remote_path}'],
                         capture_output=not self.verbose,
                         check=True,
                         timeout=30)
            self.uploaded_count += 1
            return True
        except subprocess.CalledProcessError as e:
            print(f"    ERROR uploading {local_path}: {e}")
            return False
        except Exception as e:
            print(f"    ERROR: {e}")
            return False

    def process_directory(self, local_dir: Path, remote_dir: str = ""):
        """Recursively process and upload directory"""
        old_cache = self.load_cache() if not self.clean else {}

        for item in sorted(local_dir.rglob('*')):
            if not item.is_file():
                continue

            # Skip ignored files
            if self.should_ignore(item):
                if self.verbose:
                    print(f"  ✗ {item.relative_to(self.source_dir)} (ignored)")
                continue

            # Calculate relative path
            rel_path = item.relative_to(self.source_dir)
            remote_path = str(rel_path).replace('\\', '/')

            # Compute hash
            file_hash = self.compute_hash(item)
            cache_key = str(rel_path)

            # Check if file changed
            if not self.clean and cache_key in old_cache and old_cache[cache_key] == file_hash:
                if self.verbose:
                    print(f"  ✓ {rel_path} (unchanged)")
                self.skipped_count += 1
                self.file_hashes[cache_key] = file_hash
                continue

            # Create remote directory if needed
            remote_parent = str(Path(remote_path).parent)
            if remote_parent and remote_parent != '.':
                self.mkdir_remote(remote_parent)

            # Upload file
            if self.upload_file(item, remote_path):
                self.file_hashes[cache_key] = file_hash

    def reset_device(self):
        """Reset the Pico"""
        try:
            subprocess.run(['mpremote', 'reset'],
                         capture_output=True,
                         timeout=10)
        except Exception as e:
            print(f"    ERROR resetting device: {e}")
            return False
        return True

    def deploy(self):
        """Main deployment process"""
        print("=" * 50)
        print("Slime OS 2 - Hardware Deployment Script (Python)")
        print("=" * 50)
        print()

        # Check source directory
        if not self.source_dir.exists():
            print(f"ERROR: Source directory not found: {self.source_dir}")
            sys.exit(1)

        # Load ignore patterns
        self.load_ignore_patterns()

        # Check mpremote
        print("Checking for mpremote...")
        if not self.check_mpremote():
            print("ERROR: mpremote not found!")
            print("Install with: pip3 install mpremote")
            sys.exit(1)
        print("✓ mpremote found")

        # Check device
        print("Checking for connected Pico...")
        if not self.check_device():
            print("ERROR: No MicroPython device found!")
            print("Please connect your Pico via USB")
            sys.exit(1)
        print("✓ Pico detected")
        print()

        if self.clean:
            print("⚠ Clean deploy - uploading all files")
            print()

        print("Uploading files...")
        print()

        # Process all files
        self.process_directory(self.source_dir)

        # Save cache
        self.save_cache()

        # Summary
        print()
        print("=" * 50)
        print(f"✓ Upload complete!")
        print(f"  Uploaded: {self.uploaded_count} files")
        print(f"  Skipped:  {self.skipped_count} files (unchanged)")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Reset your Pico (press reset button or unplug/replug)")
        print("2. The launcher should appear on the display")
        print()
        print("To view serial output:")
        print("  mpremote connect /dev/ttyACM0 repl")
        print()
        print("To run without reset:")
        print("  mpremote run main.py")
        print()

        # Reset device
        print("Resetting device...")
        if not self.reset_device():
            print("ERROR: Failed to reset device")
            sys.exit(1)
        print("✓ Device reset")



def main():
    parser = argparse.ArgumentParser(
        description='Deploy Slime OS 2 to Pico with incremental uploads'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Upload all files, ignoring cache'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--source',
        default='../slime_os_2',
        help='Source directory to upload (default: ../slime_os_2)'
    )

    args = parser.parse_args()

    # Resolve source directory relative to script location
    script_dir = Path(__file__).parent
    source_dir = (script_dir / args.source).resolve()

    deployer = PicoDeployer(
        source_dir=str(source_dir),
        clean=args.clean,
        verbose=args.verbose
    )

    try:
        deployer.deploy()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
