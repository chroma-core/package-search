import os
import sys


def main():

    print("Kicking off sync job...")

    chroma_tenant_uuid = os.getenv("CHROMA_TENANT_UUID")

    # TODO: implement sync logic

    if chroma_tenant_uuid:
        print("Successfully accessed the CHROMA_TENANT_UUID environment variable.")
    else:
        print("CRITICAL: The CHROMA_TENANT_UUID environment variable was not found.")
        print(
            "\tPlease ensure you have created the secret in your repository settings."
        )
        sys.exit(1)

    print("Scheduled task finished successfully.")


if __name__ == "__main__":
    main()
