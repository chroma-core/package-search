import concurrent.futures
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import requests
from chromadb import CloudClient, Collection
from packaging import version

# Import logger from common module
sys.path.insert(0, str(Path(__file__).parent / ".." / "common"))
from logger import logger


# Configuration
DATABASES = ["npm", "py_pi", "crates_io", "golang_proxy", "github_releases"]
MAX_CONCURRENT_CHROMA_READS = 10
MAX_CONCURRENT_DASHBOARD_BACKEND_WRITES = 50
MAX_RETRIES_MARK_PUBLIC = 3
BASE_RETRY_DELAY = 1.0
VERSIONS_JSON_PATH = "../../../versions.json"


class SyncError(Exception):
    pass


def initialize_clients(
    chroma_api_url: str, chroma_tenant_uuid: str, chroma_api_key: str
) -> Dict[str, CloudClient]:
    clients = {}
    for database in DATABASES:
        try:
            clients[database] = CloudClient(
                cloud_host=chroma_api_url.split("https://")[1],
                tenant=chroma_tenant_uuid,
                database=database,
                api_key=chroma_api_key,
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize client for database '{database}': {str(e)}"
            )
    return clients


def get_collection_counts(clients: Dict[str, CloudClient]) -> Dict[str, int]:
    counts = {}
    for database, client in clients.items():
        try:
            count = client.count_collections()
            counts[database] = count
            logger.info(f"Database '{database}': {count} total collections")
        except Exception as e:
            logger.error(
                f"Failed to count collections for database '{database}': {str(e)}"
            )
            counts[database] = 0
    return counts


def list_collections_for_database(
    database: str, client: CloudClient
) -> Tuple[str, List[str], Optional[str]]:
    try:
        all_collection_names: List[str] = []
        offset = 0
        limit = 1000

        # Get all collections in batches
        while True:
            collections_page = client.list_collections(limit=limit, offset=offset)
            if not collections_page:
                break
            all_collection_names.extend([coll.name for coll in collections_page])
            offset += limit

        return database, all_collection_names, None
    except Exception as e:
        return database, [], str(e)


def get_collection_metadata(
    database: str, collection_name: str, client: CloudClient
) -> Tuple[str, str, Optional[Collection], Optional[str]]:
    try:
        full_collection = client.get_collection(name=collection_name)
        if (
            full_collection.metadata
            and full_collection.metadata.get("finished_ingest") is True
        ):
            return database, collection_name, full_collection, None
        return database, collection_name, None, None
    except Exception as e:
        return database, collection_name, None, str(e)


def parse_collection_name(collection_name: str) -> Tuple[Optional[str], Optional[str]]:
    pattern = re.compile(r"^(.*)_([^_]*)$")
    match = pattern.match(collection_name)
    if match:
        prefix, version_str = match.groups()
        return prefix, version_str
    return None, None


def mark_collection_public(
    collection: Collection,
    chroma_backend_url: str,
    chroma_team_id: str,
    database: str,
    chroma_api_key: str,
) -> Tuple[bool, Optional[str]]:
    url = f"{chroma_backend_url}/api/v1/public-collections"
    headers = {"x-api-key": chroma_api_key}
    payload = {
        "teamId": chroma_team_id,
        "teamStaticName": "chroma",
        "databaseName": database,
        "collectionName": collection.name,
        "dataPlaneCollectionId": str(collection.id),
    }

    for attempt in range(MAX_RETRIES_MARK_PUBLIC):
        try:
            response = requests.post(url=url, headers=headers, json=payload)

            if response.status_code == 409:
                # Collection is already public, this is fine
                return True, None
            elif response.status_code == 200 or response.status_code == 201:
                # Successfully marked as public
                return True, None
            else:
                # Other error, we'll retry
                if attempt == MAX_RETRIES_MARK_PUBLIC - 1:
                    return (
                        False,
                        f"Failed to mark collection {collection.name} as public: HTTP {response.status_code} - {response.text}",
                    )

                # Exponential backoff
                delay = BASE_RETRY_DELAY * (2**attempt)
                time.sleep(delay)

        except Exception as e:
            if attempt == MAX_RETRIES_MARK_PUBLIC - 1:
                return (
                    False,
                    f"Failed to mark collection {collection.name} as public: {str(e)}",
                )

            # Exponential backoff
            delay = BASE_RETRY_DELAY * (2**attempt)
            time.sleep(delay)

    return (
        False,
        f"Failed to mark collection {collection.name} as public after {MAX_RETRIES_MARK_PUBLIC} attempts",
    )


def load_versions_json() -> Dict:
    try:
        with open(VERSIONS_JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise SyncError(
            "versions.json file not found. The file must exist before running sync job."
        )
    except Exception as e:
        raise SyncError(f"Failed to load versions.json: {str(e)}")


def save_versions_json(versions_data: Dict) -> None:
    try:
        with open(VERSIONS_JSON_PATH, "w") as f:
            json.dump(versions_data, f, indent=2)
    except Exception as e:
        raise SyncError(f"Failed to save versions.json: {str(e)}")


def update_versions_json(
    versions_data: Dict, database: str, collections: List[Collection]
) -> None:
    if database not in versions_data["versions"]:
        versions_data["versions"][database] = {}

    # Group collections by prefix
    grouped_by_prefix = {}
    for collection in collections:
        prefix, version_str = parse_collection_name(collection.name)
        if prefix and version_str:
            if prefix not in grouped_by_prefix:
                grouped_by_prefix[prefix] = []
            grouped_by_prefix[prefix].append(version_str)
        else:
            logger.warning(
                f"Could not parse collection name '{collection.name}' in database '{database}'"
            )

    # Sort versions for each prefix and update the data
    for prefix, version_strings in grouped_by_prefix.items():
        try:
            # Sort versions in descending order using the 'packaging' library
            sorted_versions = sorted(version_strings, key=version.parse, reverse=True)
            versions_data["versions"][database][prefix] = sorted_versions
        except Exception as e:
            logger.warning(
                f"Could not sort versions for prefix '{prefix}' in database '{database}': {str(e)}"
            )
            logger.info("Falling back to simple string sorting")
            # Fallback to simple string sorting
            versions_data["versions"][database][prefix] = sorted(
                version_strings, reverse=True
            )


def main():
    logger.section("CHROMA SYNC JOB")
    logger.info("Initializing sync job")

    # Get environment variables
    chroma_tenant_uuid = os.getenv("CHROMA_TENANT_UUID")
    chroma_team_id = os.getenv("CHROMA_TEAM_ID")
    chroma_api_key = os.getenv("CHROMA_API_KEY")
    chroma_api_url = os.getenv("CHROMA_API_URL")
    chroma_backend_url = os.getenv("CHROMA_BACKEND_URL")

    if not chroma_tenant_uuid:
        logger.critical("The CHROMA_TENANT_UUID environment variable was not found")
        logger.error(
            "Please ensure you have created the secret in your repository settings"
        )
        sys.exit(1)

    if not chroma_team_id:
        logger.critical("The CHROMA_TEAM_ID environment variable was not found")
        logger.error(
            "Please ensure you have created the secret in your repository settings"
        )
        sys.exit(1)

    if not chroma_api_key:
        logger.critical("The CHROMA_API_KEY environment variable was not found")
        logger.error(
            "Please ensure you have created the secret in your repository settings"
        )
        sys.exit(1)

    if not chroma_api_url:
        logger.critical("The CHROMA_API_URL environment variable was not found")
        logger.error(
            "Please ensure you have created the secret in your repository settings"
        )
        sys.exit(1)

    if not chroma_backend_url:
        logger.critical("The CHROMA_BACKEND_URL environment variable was not found")
        logger.error(
            "Please ensure you have created the secret in your repository settings"
        )
        sys.exit(1)

    logger.success("Successfully accessed required environment variables")

    # Initialize chroma clients for all databases
    logger.subsection("Initializing Clients")
    logger.info("Initializing chroma clients for all databases")

    clients = initialize_clients(chroma_api_url, chroma_tenant_uuid, chroma_api_key)
    if len(clients) != len(DATABASES):
        logger.critical("Failed to initialize clients for all databases")
        sys.exit(1)

    logger.success(f"Successfully initialized clients for {len(clients)} databases")

    # Get collection counts for progress tracking
    logger.info("Getting collection counts for progress tracking")
    collection_counts = get_collection_counts(clients)
    total_collections_to_list = sum(collection_counts.values())
    logger.info(f"Total collections to process: {total_collections_to_list}")

    # List all collections globally in parallel
    logger.subsection("Listing Collections")
    logger.info("Listing all collections with global parallelism")

    db_to_collections = {}
    list_errors = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT_CHROMA_READS
    ) as executor:
        # Submit list_collections tasks for all databases
        future_to_db = {
            executor.submit(list_collections_for_database, db, client): db
            for db, client in clients.items()
        }

        for i, future in enumerate(concurrent.futures.as_completed(future_to_db), 1):
            db_name = future_to_db[future]
            logger.progress(i, len(DATABASES), f"Listing collections for {db_name}")

            db_name, collection_names, error = future.result()
            if error:
                error_msg = f"Error listing collections for '{db_name}': {error}"
                logger.error(error_msg)
                list_errors.append(error_msg)
            else:
                db_to_collections[db_name] = collection_names
                logger.success(
                    f"Listed {len(collection_names)} collections in '{db_name}'"
                )

    if list_errors:
        logger.critical("Errors occurred while listing collections")
        for error in list_errors:
            logger.error(error)
        sys.exit(1)

    # Check metadata globally in parallel
    logger.subsection("Checking Metadata")
    logger.info("Checking collection metadata with global parallelism")

    # Create list of (database, collection_name, client) tuples for global processing
    metadata_tasks = []
    for db_name, collection_names in db_to_collections.items():
        client = clients[db_name]
        for collection_name in collection_names:
            metadata_tasks.append((db_name, collection_name, client))

    total_metadata_checks = len(metadata_tasks)
    logger.info(f"Checking metadata for {total_metadata_checks} collections")

    all_finished_collections = {}
    metadata_errors = []
    processed_metadata = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT_CHROMA_READS
    ) as executor:
        # Submit metadata check tasks globally
        future_to_task = {
            executor.submit(
                get_collection_metadata, db_name, collection_name, client
            ): (db_name, collection_name)
            for db_name, collection_name, client in metadata_tasks
        }

        for future in concurrent.futures.as_completed(future_to_task):
            db_name, collection_name = future_to_task[future]
            processed_metadata += 1
            logger.progress(
                processed_metadata,
                total_metadata_checks,
                f"Checking {collection_name} in {db_name}",
            )

            db_name, collection_name, collection, error = future.result()
            if error:
                metadata_errors.append(
                    f"Error checking metadata for '{collection_name}' in '{db_name}': {error}"
                )
            elif collection:  # Collection has finished_ingest = true
                if db_name not in all_finished_collections:
                    all_finished_collections[db_name] = []
                all_finished_collections[db_name].append(collection)

    if metadata_errors:
        logger.warning(
            f"Encountered {len(metadata_errors)} metadata check errors (continuing anyway)"
        )
        for error in metadata_errors[:10]:
            logger.warning(error)
        if len(metadata_errors) > 10:
            logger.warning(f"... and {len(metadata_errors) - 10} more errors")

    # Summary of found collections
    total_finished = sum(
        len(collections) for collections in all_finished_collections.values()
    )
    logger.success(f"Found {total_finished} collections with finished_ingest = true")
    for db_name, collections in all_finished_collections.items():
        logger.info(f"  • {db_name}: {len(collections)} finished collections")

    # Update versions.json and mark collections as public
    logger.subsection("Updating Data")
    logger.info("Updating versions.json and marking collections as public")

    # Load current versions.json
    try:
        versions_data = load_versions_json()
        logger.success("Loaded current versions.json")
    except SyncError as e:
        logger.critical(str(e))
        sys.exit(1)

    # Update versions.json with new collections
    for database, collections in all_finished_collections.items():
        if collections:
            logger.info(
                f"Updating versions.json for {len(collections)} collections in '{database}'"
            )
            update_versions_json(versions_data, database, collections)

    # Mark collections as public with global concurrent processing
    logger.subsection("Marking Collections Public")

    # Create a list of (collection, database) tuples for global processing
    collections_to_mark = []
    for database, collections in all_finished_collections.items():
        for collection in collections:
            collections_to_mark.append((collection, database))

    total_collections = len(collections_to_mark)
    logger.info(
        f"Marking {total_collections} collections as public with global parallelism"
    )

    public_marking_errors = []
    processed_count = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT_DASHBOARD_BACKEND_WRITES
    ) as executor:
        # Submit all marking tasks globally
        future_to_collection = {
            executor.submit(
                mark_collection_public,
                collection,
                chroma_backend_url,
                chroma_team_id,
                database,
                chroma_api_key,
            ): (collection, database)
            for collection, database in collections_to_mark
        }

        for future in concurrent.futures.as_completed(future_to_collection):
            collection, database = future_to_collection[future]
            processed_count += 1
            logger.progress(
                processed_count,
                total_collections,
                f"Marking {collection.name} public in {database}",
            )

            success, error = future.result()
            if not success:
                public_marking_errors.append(error)
                logger.error(f"Error marking collection as public: {error}")

    # Check for public marking errors
    if public_marking_errors:
        logger.critical("Errors occurred while marking collections as public")
        for error in public_marking_errors:
            logger.error(error)
        sys.exit(1)

    # Save updated versions.json
    logger.subsection("Saving Results")
    logger.info("Saving updated versions.json")

    try:
        save_versions_json(versions_data)
        logger.success("Successfully updated versions.json")
    except SyncError as e:
        logger.critical(str(e))
        sys.exit(1)

    # Summary
    total_collections = sum(
        len(collections) for collections in all_finished_collections.values()
    )

    logger.section("SYNC COMPLETION")
    logger.success("Sync job completed successfully!")
    logger.info(f"Total collections processed: {total_collections}")
    logger.info(f"Databases processed: {len(all_finished_collections)}")

    # Print per-database summary
    for database, collections in all_finished_collections.items():
        if collections:
            logger.info(f"  • {database}: {len(collections)} collections")

    sys.exit(0)


if __name__ == "__main__":
    main()
