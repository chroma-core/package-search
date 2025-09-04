import sys
import os


def main(file_paths):
    print("Running validation on the following files:")
    all_files_valid = True

    if not file_paths:
        print("No files to validate.")
        return True

    for file_path in file_paths:
        print(f"- {file_path}")

        if not os.path.exists(file_path):
            print(f"\tError: File '{file_path}' not found.")
            all_files_valid = False
            continue

        try:
            # TODO: implement validation logic

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"\tSuccessfully read {len(content)} characters from the file.")

        except Exception as e:
            print(f"\tAn error occurred while processing '{file_path}': {e}")
            all_files_valid = False

    return all_files_valid


if __name__ == "__main__":
    files_to_check = sys.argv[1:]

    if main(files_to_check):
        print("All files passed validation.")
        sys.exit(0)
    else:
        print("Some files failed validation.")
        sys.exit(1)
