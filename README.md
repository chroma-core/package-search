# Chroma Package Search

This repository contains a curated list of public code packages that Chroma keeps indexed into Chroma collections. The repository currently indexes **26K+** packages across various registries.

## Purpose

This repository serves as the authoritative source of truth for packages that Chroma indexes for code search and retrieval. 

## Repository Structure

The repository is organized as follows:

```
package-search/
├── index.json                   # Enumerates all packages that have been or are being run through the indexing pipeline
├── versions.json                # Enumerates all presently indexed packages and versions
├── npm/                         # npm packages
│   ├── react/
│   │   └── config.json
│   ├── vue/
│   │   └── config.json
│   └── ...
├── pypi/                        # PyPI packages
│   ├── requests/
│   │   └── config.json
│   └── ...
├── crates_io/                   # Rust packages
│   ├── serde/
│   │   └── config.json
│   └── ...
└── go/                          # Go packages
    ├── github.com/
    │   └── gin-gonic/
    │       └── gin/
    │           └── config.json
    └── ...
```

Each package has its own configuration file located at `<registry>/<native_identifier>/config.json`.

## Adding New Packages

Anyone can request additional packages to be indexed by creating a Pull Request. Here's how:

1. **Fork this repository**
2. **Create a new directory** at `<registry>/<native_identifier>/`
3. **Add a `config.json` file** in that directory following this format:
   ```json
   {
     "native_identifier": "chromadb",
     "collection_name_prefix": "chromadb",
     "repo": "chroma-core/chroma",
     "registry": "py_pi",
     "tag_formats": [
       "{major}.{minor}.{patch}",
     ],
     "sentinel_timestamp": "2024-01-01T00:00:00Z",
     "include": [
       "**/*.md",
       "**/*.py", 
       "**/*.rs",
     ]
   }
   ```

   **Required Fields:**
   - `native_identifier`: The identifier used by the registry on which the package is hosted. For most registries, this should be the colloquial name of the package. For GitHub Releases, this should be the owning user's or organization's username, followed by a forward slash, followed by the name of the repository (e.g., `chroma-core/code-collections`). For Golang modules, this should be the full module path (e.g., `github.com/stretchr/testify/`).
   - `collection_name_prefix`: The text that will precede the version in the name of Chroma collections created for this package. We name collections as `<collection_name_prefix>_<version>`. The collection name is used to query the indexed records within Chroma, so this should generally be the colloquial name of the package or some permutation of it. Note that the collection name prefix must be globally unique within a registry. That is, no two packages in the same registry may have the same collection name prefix.
   - `repo`: The GitHub repository in which the package's source code is maintained. Provide the username of the owning user or organization, followed by a forward slash, followed by the name of the repository.
   - `registry`: The registry to which versions of the package are published. Must be one of "npm", "py_pi", "crates_io", "golang_proxy", or "github_releases".
   - `tag_formats`: Array of git tag formats enumerating **all possible tag formats** for versions of the package you'd like to be indexed. Please note that Chroma assumes that a package version can be resolved to a tagged—either annotated or lightweight—git commit. We handle the version-to-tag resolution for you, but we can only resolve to tag formats we know exist, which we obtain from this configuration field. See the [Tag Formatting Guide](./TAG_FORMATS.md) for more information.
   - `sentinel_timestamp`: The earliest indexed time; versions published before it are excluded. Must be a [RFC 3339/ISO 8601](https://ijmacd.github.io/rfc3339-iso8601/)-compliant timestamp.
   - `include`: Array of [glob patterns](https://code.visualstudio.com/docs/editor/glob-patterns) for files to index (e.g., `["**/*.md", "**/*.ts", "**/*.js"]`).
   - `version_sample_relative_size`: The proportion of all published versions of the package to index in a single pass. Currently, Chroma runs an index job every day for each package in the `index.json` file at the root of this repository. Each index job operates on a subset of the available versions of a given package. This parameter controls the size of that subset for each index job run.
   - `version_sample_max_size`: This field bounds the sample size in the case that there are many versions. The number of versions in a sample for a given package will never be more than the value provided for this field.

4. **Update the index.json file** to include your new package in the packages that Chroma will scan during the next index job
5. **Create a Pull Request** with a clear description of the package you're adding
6. **Wait for review** - a member of the Chroma team will review your PR

## Review Process

- All PRs are reviewed by Chroma team members
- We evaluate packages based on relevance, popularity, and community value
- Accepted packages will be indexed and made searchable through Chroma's [Package Search MCP Server]()

## Current Index

The repository currently indexes packages from:
- **npm** - JavaScript/TypeScript packages
- **PyPI** - Python packages
- **crates_io** - Rust packages
- **Golang** - Go packages
- **GitHub Releases** - Packages distributed via GitHub Releases

## Contributing Guidelines

- Ensure the package is publicly available and well-maintained
- Verify the `native_identifier` matches the package name in the registry exactly
- Confirm the GitHub repository exists and is accessible
- Use the correct registry value: "npm", "py_pi", "crates_io", "golang_proxy", or "github_releases"
- Format the `tag_formats` array to match the actual GitHub release tags
- Set `sentinel_timestamp` to a reasonable starting point for historical indexing
- Use glob patterns in the `include` array (e.g., `"**/*.md"` instead of `".md"`)
- Update the `index.json` file to include your new package
- Provide context in your PR description about why the package should be indexed

## Monorepo Considerations

If the repository you're adding is a monorepo (contains multiple packages), you must format the glob patterns in the `include` array to target only the specific package's subdirectory. For example:

```json
{
  "native_identifier": "my-package",
  "collection_name_prefix": "my-package",
  "repo": "owner/monorepo",
  "registry": "npm",
  "tag_formats": ["v{major}.{minor}.{patch}"],
  "sentinel_timestamp": "2024-01-01T00:00:00Z",
  "include": [
    "my-package/**/*.md",
    "my-package/**/*.ts",
    "my-package/**/*.js"
  ]
}
```

This ensures that only files within the `my-package/` directory are indexed, not the entire monorepo.

---

*This repository is maintained by the Chroma team to support our code search and retrieval capabilities.*
