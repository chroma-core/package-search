import os
import json
import re
from pathlib import Path

VALID_REGISTRIES = ["npm", "py_pi", "crates_io", "golang_proxy", "github_releases"]
REQUIRED_REGISTRIES = ["github_releases", "golang_proxy", "py_pi", "npm", "crates_io"]
TIMESTAMP_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
VERSION_PATTERN = r"^\d+\.\d+(\.\d+)?$"


def validate_config_json(_, content):
    """Validate a config.json file according to the README format."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Check required fields
    required_fields = [
        "native_identifier",
        "collection_name_prefix",
        "repo",
        "registry",
        "tag_formats",
        "sentinel_timestamp",
        "include",
        "version_sample_relative_size",
        "version_sample_max_size",
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate registry value
    if data["registry"] not in VALID_REGISTRIES:
        return (
            False,
            f"Invalid registry '{data['registry']}'. Must be one of {VALID_REGISTRIES}",
        )

    # Validate field types
    type_validations = [
        ("native_identifier", str, "string"),
        ("collection_name_prefix", str, "string"),
        ("repo", str, "string"),
        ("tag_formats", list, "array"),
        ("include", list, "array"),
        ("version_sample_relative_size", (int, float), "number"),
        ("version_sample_max_size", int, "integer"),
    ]

    for field_name, expected_type, type_description in type_validations:
        if not isinstance(data[field_name], expected_type):
            return False, f"{field_name} must be a {type_description}"

    # Validate timestamp format (RFC 3339/ISO 8601)
    if not re.match(TIMESTAMP_PATTERN, data["sentinel_timestamp"]):
        return (
            False,
            "sentinel_timestamp must be in RFC 3339/ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)",
        )

    return True, "Valid config.json"


def validate_index_json(file_path, content):
    """Validate the index.json file."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Check required structure
    if "packages" not in data:
        return False, "Missing required key 'packages'"

    packages = data["packages"]
    if not isinstance(packages, list):
        return False, "'packages' must be an array"

    # Check for duplicate packages
    if len(packages) != len(set(packages)):
        duplicates = [pkg for pkg in set(packages) if packages.count(pkg) > 1]
        return False, f"Found duplicate packages: {duplicates}"

    # Validate each package
    base_path = Path(file_path).parent
    for package in packages:
        if not isinstance(package, str):
            return False, f"Package '{package}' must be a string"

        # Verify package path exists
        package_path = base_path / package
        if not package_path.exists():
            return False, f"Package path '{package}' does not exist"

    return True, "Valid index.json"


def validate_versions_json(file_path, content):
    """Validate the versions.json file."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # Check required structure
    if "versions" not in data:
        return False, "Missing required key 'versions'"

    versions = data["versions"]
    if not isinstance(versions, dict):
        return False, "'versions' must be an object"

    # Validate required registries exist
    for registry in REQUIRED_REGISTRIES:
        if registry not in versions:
            return False, f"Missing required registry: {registry}"
        if not isinstance(versions[registry], dict):
            return False, f"Registry '{registry}' must be an object"

    # Load and validate index.json for cross-validation
    base_path = Path(file_path).parent
    index_packages = load_index_packages(base_path)
    if index_packages is None:
        return False, "index.json not found or invalid for cross-validation"

    # Collect all validation errors
    errors = []

    # Validate each registry's packages and versions
    for registry, packages in versions.items():
        if registry not in REQUIRED_REGISTRIES:
            continue

        errors.extend(
            validate_registry_packages(registry, packages, base_path, index_packages)
        )

    if errors:
        return False, f"Found {len(errors)} validation errors:\n" + "\n".join(
            f"  • {error}" for error in errors
        )

    return True, "Valid versions.json"


def load_index_packages(base_path):
    """Load and validate index.json, returning set of packages or None if invalid."""
    index_path = base_path / "index.json"
    if not index_path.exists():
        return None

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.loads(f.read())
            if "packages" not in index_data:
                return None
            return set(index_data["packages"])
    except Exception:
        return None


def validate_registry_packages(registry, packages, base_path, index_packages):
    """Validate all packages in a registry, returning list of errors."""
    errors = []

    for native_id, package_versions in packages.items():
        # Validate basic types
        if not isinstance(native_id, str):
            errors.append(
                f"Native identifier '{native_id}' in {registry} must be a string"
            )
            continue

        if not isinstance(package_versions, list):
            errors.append(f"Versions for '{native_id}' in {registry} must be an array")
            continue

        # Validate package exists in index
        errors.extend(validate_package_in_index(native_id, registry, index_packages))

        # Validate versions
        errors.extend(validate_package_versions(native_id, registry, package_versions))

        # Validate corresponding config exists
        errors.extend(validate_config_exists(native_id, registry, base_path))

    return errors


def validate_package_in_index(native_id, registry, index_packages):
    """Validate that package exists in index.json."""
    possible_restorations = get_possible_restorations(native_id, registry)

    for restored_id in possible_restorations:
        expected_index_entry = f"{registry}/{restored_id}"
        if expected_index_entry in index_packages:
            return []

    attempted = [f"{registry}/{r}" for r in possible_restorations]
    return [
        f"Package for '{native_id}' in {registry} not found in index.json. Tried: {attempted}"
    ]


def validate_package_versions(native_id, registry, package_versions):
    """Validate version list for a package."""
    errors = []

    # Check for duplicate versions
    if len(package_versions) != len(set(package_versions)):
        duplicates = [v for v in set(package_versions) if package_versions.count(v) > 1]
        errors.append(
            f"Found duplicate versions for '{native_id}' in {registry}: {duplicates}"
        )

    # Validate version format
    for version in package_versions:
        if not isinstance(version, str):
            errors.append(
                f"Version '{version}' for '{native_id}' in {registry} must be a string"
            )
        elif not re.match(VERSION_PATTERN, version):
            errors.append(
                f"Version '{version}' for '{native_id}' in {registry} must be in x.y.z or x.y format"
            )

    return errors


def validate_config_exists(native_id, registry, base_path):
    """Validate that config.json exists for the package."""
    possible_restorations = get_possible_restorations(native_id, registry)

    for restored_id in possible_restorations:
        config_path = base_path / registry / restored_id / "config.json"
        if config_path.exists():
            return []

    return [
        f"Missing config.json for '{native_id}' in {registry}. Tried restorations: {possible_restorations}"
    ]


def get_possible_restorations(native_id, registry):
    """Get all possible restorations of a native identifier."""
    possibilities = []

    if registry == "npm":
        possibilities.extend(get_npm_restorations(native_id))
    elif registry == "golang_proxy":
        possibilities.extend(get_golang_restorations(native_id))
    else:
        # For other registries, simple underscore to slash conversion
        if "_" in native_id:
            possibilities.append(native_id.replace("_", "/"))
        possibilities.append(native_id)

    # Remove duplicates while preserving order
    return deduplicate_list(possibilities)


def get_npm_restorations(native_id):
    """Get possible restorations for npm packages."""
    possibilities = []

    if "_" in native_id:
        if native_id.startswith("_"):
            # _types_node -> @types/node
            parts = native_id[1:].split("_", 1)
            if len(parts) == 2:
                possibilities.append(f"@{parts[0]}/{parts[1]}")
            else:
                possibilities.append(f"@{parts[0]}")
        else:
            # Scoped package: aws-crypto_util -> @aws-crypto/util
            parts = native_id.split("_", 1)
            if len(parts) == 2:
                possibilities.append(f"@{parts[0]}/{parts[1]}")

    # Handle known special cases
    if "socketio" in native_id:
        possibilities.append(native_id.replace("socketio", "socket.io"))

    # Always try as-is
    possibilities.append(native_id)
    return possibilities


def get_golang_restorations(native_id):
    """Get possible restorations for golang modules."""
    possibilities = []

    if "_" in native_id:
        if native_id.startswith("github.com_"):
            parts = native_id.split("_")
            if len(parts) >= 3:
                domain = parts[0]
                user = parts[1]
                repo = "_".join(parts[2:])
                possibilities.append(f"{domain}/{user}/{repo}")
            else:
                possibilities.append(native_id.replace("_", "/"))
        else:
            possibilities.append(native_id.replace("_", "/"))

    possibilities.append(native_id)
    return possibilities


def deduplicate_list(items):
    """Remove duplicates from list while preserving order."""
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    return unique_items


def validate_file(file_path):
    """Validate a single file based on its type."""
    if not os.path.exists(file_path):
        return False, f"File '{file_path}' not found"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Determine validation based on filename
    file_name = os.path.basename(file_path)
    validators = {
        "config.json": validate_config_json,
        "index.json": validate_index_json,
        "versions.json": validate_versions_json,
    }

    if file_name not in validators:
        return True, f"Unknown file type '{file_name}', skipping validation"

    return validators[file_name](file_path, content)


def find_all_validation_files(root_path):
    """Find all config.json, index.json, and versions.json files in the repository."""
    root = Path(root_path)
    files_to_validate = []

    # Find all JSON files that we validate
    for pattern in ["**/config.json", "**/index.json", "**/versions.json"]:
        files_to_validate.extend(root.glob(pattern))

    # Convert to strings and sort for consistent output
    return sorted([str(f) for f in files_to_validate])
