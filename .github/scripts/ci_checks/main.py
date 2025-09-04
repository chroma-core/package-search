import os


def main():
    """
    Placeholder function to perform actions on the repository after a merge to main.
    This script has access to all files in the repository.
    """
    print("Starting CI checks...")

    print("\nListing all files in the repository:")
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        for name in files:
            file_path = os.path.join(root, name)
            print(f"- {file_path}")

    # TODO: implement CI checks

    readme_path = "README.md"
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"Successfully read {readme_path}.")
        except Exception as e:
            print(f"Could not read {readme_path}: {e}")
    else:
        print(f"{readme_path} not found.")

    print("\nCI checks completed successfully.")


if __name__ == "__main__":
    main()
