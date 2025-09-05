import sys
import os
from pathlib import Path

# Import validation utilities from common module
sys.path.insert(0, str(Path(__file__).parent / ".." / "common"))
from validation_utils import validate_file, find_all_validation_files
from logger import logger


def main():
    """Main CI check function that validates all files in the repository."""
    logger.section("COMPREHENSIVE CI VALIDATION")
    logger.info("Running comprehensive CI checks on all validation files")

    # Find all files to validate from repository root
    repo_root = Path(__file__).parent.parent.parent.parent
    all_files = find_all_validation_files(repo_root)

    if not all_files:
        logger.warning("No validation files found in repository")
        return True

    logger.info(f"Found {len(all_files)} files to validate")

    all_files_valid = True
    failed_files = []

    for i, file_path in enumerate(all_files, 1):
        # Convert to relative path for cleaner output
        relative_path = os.path.relpath(file_path, repo_root)

        logger.progress(i, len(all_files), os.path.basename(relative_path))

        is_valid, message = validate_file(file_path)

        if is_valid:
            logger.file_status(relative_path, "valid", message)
        else:
            logger.file_status(relative_path, "invalid", message)
            all_files_valid = False
            failed_files.append(relative_path)

    # Print summary
    passed_count = len(all_files) - len(failed_files)
    logger.summary(passed_count, len(failed_files), len(all_files))

    if not all_files_valid:
        logger.subsection("FAILED FILES")
        for failed_file in failed_files:
            logger.error(f"Failed: {failed_file}")

    return all_files_valid


if __name__ == "__main__":
    success = main()
    if success:
        logger.success("All CI checks passed")
    else:
        logger.error("CI checks failed")
    sys.exit(0 if success else 1)
