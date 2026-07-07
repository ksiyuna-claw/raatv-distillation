#!/usr/bin/env python3
"""
Post-distillation cleanup — removes intermediate files after report delivery.
Keeps: distillation analysis + transcripts.json + metadata/ + distill_state.json
Removes: audio/, status/, scripts/, logs/, segments/ and other temp files

Usage:
  python3 cleanup.py --project-dir "/path/to/your/project"
  python3 cleanup.py --project-dir "/path/to/your/project" --dry-run  # Preview only
"""

import argparse
import os
import shutil
import json
from pathlib import Path

# Directories to remove
DIRS_TO_REMOVE = ['audio', 'status', 'scripts', 'logs', 'segments', '__pycache__']

# File patterns to remove
FILES_TO_REMOVE = ['*.pyc', '*.tmp', '*.bak', 'transcripts_batch_*.json', 'batch*_notes.md']

# Files/directories to keep
KEEP_ITEMS = [
    'distill-analysis.md', 'distillation-report.md',
    'transcripts.json', 'distill_state.json',
    'metadata',
]


def cleanup(project_dir, dry_run=False):
    project = Path(project_dir)
    if not project.exists():
        print(f"❌ Project directory does not exist: {project_dir}")
        return

    removed = []
    kept = []

    # Remove target directories
    for dirname in DIRS_TO_REMOVE:
        target = project / dirname
        if target.exists() and target.is_dir():
            size = sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
            file_count = sum(1 for f in target.rglob('*') if f.is_file())
            if dry_run:
                print(f"  🗑️  [dry-run] {dirname}/ ({file_count} files, {size/1024:.1f}KB)")
            else:
                shutil.rmtree(target)
                print(f"  🗑️  Deleted {dirname}/ ({file_count} files, {size/1024:.1f}KB)")
            removed.append((dirname, size))
        else:
            print(f"  ⏭️  {dirname}/ does not exist, skipping")

    # Remove temp files in root
    import glob
    for pattern in FILES_TO_REMOVE:
        for fpath in glob.glob(str(project / pattern)):
            p = Path(fpath)
            if p.name in [k for k in KEEP_ITEMS]:
                continue
            size = p.stat().st_size
            if dry_run:
                print(f"  🗑️  [dry-run] File {p.name} ({size/1024:.1f}KB)")
            else:
                p.unlink()
                print(f"  🗑️  Deleted file {p.name} ({size/1024:.1f}KB)")
            removed.append((p.name, size))

    # Check kept items
    print(f"\n📦 Kept files:")
    for item in KEEP_ITEMS:
        target = project / item
        if target.exists():
            if target.is_dir():
                file_count = sum(1 for f in target.rglob('*') if f.is_file())
                print(f"  ✅ {item}/ ({file_count} files)")
            else:
                size = target.stat().st_size
                print(f"  ✅ {item} ({size/1024:.1f}KB)")
            kept.append(item)
        else:
            print(f"  ⚠️  {item} does not exist")

    # Summary
    total_freed = sum(s for _, s in removed)
    print(f"\n{'[dry-run] ' if dry_run else ''}Total cleaned: {len(removed)} items, freed {total_freed/1024/1024:.1f}MB")


def main():
    parser = argparse.ArgumentParser(description='Post-distillation cleanup tool')
    parser.add_argument('--project-dir', required=True, help='Project directory path')
    parser.add_argument('--dry-run', action='store_true', help='Preview without deleting')
    args = parser.parse_args()

    print("=" * 50)
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Cleanup: {args.project_dir}")
    print("=" * 50)
    cleanup(args.project_dir, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
