# Chroma Code Collections

This repository contains a curated list of public code packages that Chroma keeps indexed into Chroma collections. The repository currently indexes **26K+** packages across various registries.

## Purpose

This repository serves as the authoritative source for packages that Chroma indexes for code search and retrieval. 

## Repository Structure

The repository is organized as follows:

```
code-collections/
├── index.json                    # Tracks all packages being synced
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
├── crates.io/                   # Rust packages
│   ├── serde/
│   │   └── config.json
│   └── ...
└── go/                          # Go packages
    ├── gin/
    │   └── config.json
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
     "native_identifier": "package-name",
     "repo": "owner/repository",
     "registry": "npm",
     "tag_formats": [
       "v{major}.{minor}.{patch}",
       "v{major}.{minor}"
     ],
     "sentinel_timestamp": "2024-01-01T00:00:00Z",
     "include": [
       "**/*.md",
       "**/*.ts", 
       "**/*.js",
       "**/*.tsx",
       "**/*.jsx"
     ]
   }
   ```

   **Required Fields:**
   - `package_name`: The colloquial name of the package. Usually this is one word. It may only contain alphanumeric characters, underscores, periods, and hyphens. It must be between 3 and 512 characters long
   - `native_identifier`: The identifier used by the registry on which the package is hosted. For most registries, this should be the same as the `package_name`. For GitHub Releases, this should be the owning user's or organization's username, followed by a forward slash, followed by the name of the repository (e.g., `chroma-core/code-collections`). For Golang modules, this should be the full module path (e.g., `github.com/stretchr/testify/`)
   - `repo`: GitHub repository as `owner/repository`
   - `registry`: Must be one of "npm", "pypi", "crates.io", "go", or "github_releases"
   - `tag_formats`: Array of GitHub tag formats with placeholders like `{major}`, `{minor}`, `{patch}`, `{YYYY}`, `{MM}`, `{DD}`
   - `sentinel_timestamp`: RFC 3339 timestamp for earliest version to index
   - `include`: Array of glob patterns for files to include (e.g., `["**/*.md", "**/*.ts", "**/*.js"]`)

4. **Update the index.json file** to include your new package in the packages array
5. **Create a Pull Request** with a clear description of the package you're adding
6. **Wait for review** - A member of the Chroma team will review your PR

## Review Process

- All PRs are reviewed by Chroma team members
- We evaluate packages based on relevance, popularity, and community value
- Accepted packages will be indexed and made searchable through Chroma

## Current Index

The repository currently indexes packages from:
- **npm** - JavaScript/TypeScript packages
- **PyPI** - Python packages
- **crates.io** - Rust packages
- **Golang (GitHub)** - Go packages

## Contributing Guidelines

- Ensure the package is publicly available and well-maintained
- Verify the `native_identifier` matches the package name on the registry exactly
- Confirm the GitHub repository exists and is accessible
- Use the correct registry value: "npm", "pypi", "crates.io", "go", or "github_releases"
- Format the `tag_formats` array to match the actual GitHub release tags
- Set `sentinel_timestamp` to a reasonable starting point for historical indexing
- Use glob patterns in the `include` array (e.g., `"**/*.md"` instead of `".md"`)
- Update the `index.json` file to include your new package
- Provide context in your PR description about why the package should be indexed

## Monorepo Considerations

If the repository you're adding is a monorepo (contains multiple packages), you must format the glob patterns in the `include` array to target only the specific package's subdirectory. For example:

```json
{
  "package_name": "my-package",
  "native_identifier": "my-package",
  "repo": "owner/monorepo",
  "registry": "npm",
  "tag_formats": ["v{major}.{minor}.{patch}"],
  "sentinel_timestamp": "2024-01-01T00:00:00Z",
  "include": [
    "packages/my-package/**/*.md",
    "packages/my-package/**/*.ts",
    "packages/my-package/**/*.js"
  ]
}
```

This ensures that only files within the `packages/my-package/` directory are indexed, not the entire monorepo.

---

*This repository is maintained by the Chroma team to support our code search and retrieval capabilities.*
