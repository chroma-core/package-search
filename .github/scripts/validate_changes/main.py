import sys
import os
from pathlib import Path

# Import validation utilities from common module
sys.path.insert(0, str(Path(__file__).parent / ".." / "common"))
from validation_utils import validate_file
from logger import logger


def find_repo_root(start_path=None):
    """Find the repository root by looking for .git directory."""
    current = Path(start_path or __file__).resolve()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # Assume we're in .github/scripts/validate_changes and go up 3 levels
    return Path(__file__).resolve().parent.parent.parent.parent


def resolve_file_path(file_path, repo_root):
    """Resolve file path relative to repo root."""
    # Only resolve paths relative to repo root
    repo_relative_path = repo_root / file_path
    if repo_relative_path.exists():
        return str(repo_relative_path)

    # Error if file doesn't exist relative to repo root
    raise FileNotFoundError(f"File not found relative to repo root: {file_path}")


def main(file_paths):
    """Main validation function that processes multiple files."""
    logger.section("FILE VALIDATION")
    logger.info("Running validation on specified files")

    if not file_paths:
        logger.warning("No files to validate")
        return True

    # Find repo root for path resolution
    repo_root = find_repo_root()
    logger.info(f"Repository root: {repo_root}")

    all_files_valid = True
    failed_files = []

    # Resolve all file paths relative to repo root
    resolved_paths = []
    for file_path in file_paths:
        try:
            resolved_path = resolve_file_path(file_path, repo_root)
            resolved_paths.append(resolved_path)
        except FileNotFoundError as e:
            logger.error(str(e))
            failed_files.append(file_path)
            all_files_valid = False

    logger.info(f"Found {len(resolved_paths)} file(s) to validate")

    for i, file_path in enumerate(resolved_paths, 1):
        logger.progress(i, len(resolved_paths), os.path.basename(file_path))

        is_valid, message = validate_file(file_path)

        if is_valid:
            logger.file_status(file_path, "valid", message)
        else:
            logger.file_status(file_path, "invalid", message)
            all_files_valid = False
            failed_files.append(file_path)

    # Print summary
    passed_count = len(resolved_paths) - len(failed_files)
    logger.summary(passed_count, len(failed_files), len(resolved_paths))

    return all_files_valid


if __name__ == "__main__":
    files_to_check = sys.argv[1:]

    if main(files_to_check):
        logger.success("All files passed validation")
        sys.exit(0)
    else:
        logger.error("Some files failed validation")
        sys.exit(1)
