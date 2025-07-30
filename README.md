# Chroma Code Collections

This repository contains a curated list of public code packages that Chroma keeps indexed into Chroma collections. The `code_collections.json` file currently indexes **26K+** packages across various registries.

## Purpose

This repository serves as the authoritative source for packages that Chroma indexes for code search and retrieval. 

## Adding New Packages

Anyone can request additional packages to be indexed by creating a Pull Request. Here's how:

1. **Fork this repository**
2. **Add your package** to the `code_collections.json` file following the existing format:
   ```json
   {
     "native_identifier": "package-name",
     "repo": "owner/repository",
     "registry": "npm",
     "tag_format": "v{major}.{minor}.{patch}",
     "sentinel_timestamp": "2024-01-01T00:00:00+0000",
     "include": [".md", ".ts", ".js", ".tsx", ".jsx"]
   }
   ```

   **Required Fields:**
   - `native_identifier`: Package name on the registry (e.g., "react" for npm)
   - `repo`: GitHub repository as "owner/repository"
   - `registry`: Must be one of "npm", "pypi", "crates.io", or "go"
   - `tag_format`: GitHub tag format with placeholders like `{major}`, `{minor}`, `{patch}`, `{YYYY}`, `{MM}`, `{DD}`
   - `sentinel_timestamp`: ISO 8601 timestamp for earliest version to index
   - `include`: Array of file extensions to include (e.g., [".md", ".ts", ".js"])
3. **Create a Pull Request** with a clear description of the package you're adding
4. **Wait for review** - A member of the Chroma team will review your PR

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
- Use the correct registry value: "npm", "pypi", "crates.io", or "go"
- Format the `tag_format` to match the actual GitHub release tags
- Set `sentinel_timestamp` to a reasonable starting point for historical indexing
- Include relevant file extensions in the `include` array
- Provide context in your PR description about why the package should be indexed

---

*This repository is maintained by the Chroma team to support our code search and retrieval capabilities.*
