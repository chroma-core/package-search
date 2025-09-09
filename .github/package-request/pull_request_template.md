## Package Request

### Package Information
- **Package Name**: 
- **Registry**: <!-- npm / py_pi / crates_io / golang_proxy / github_releases -->
- **GitHub Repository**: <!-- Format: owner/repo -->

### Why should this package be indexed?
<!-- Provide context about the package's relevance, popularity, and community value -->

### Package Details
- **Description**: <!-- Brief description of what the package does -->
- **Weekly Downloads/Stars**: <!-- Provide metrics showing package popularity -->
- **Last Updated**: <!-- When was the package last updated? -->
- **License**: <!-- Package license type -->

### Checklist
Please verify the following before submitting:

- [ ] Package is publicly available and actively maintained
- [ ] Created directory at `<registry>/<native_identifier>/`
- [ ] Added `config.json` with all required fields:
  - [ ] `native_identifier` matches the package name exactly as it appears in the registry
  - [ ] `collection_name_prefix` is globally unique within the registry
  - [ ] `repo` points to a valid, accessible GitHub repository
  - [ ] `registry` is one of: "npm", "py_pi", "crates_io", "golang_proxy", or "github_releases"
  - [ ] `tag_formats` array matches actual GitHub release tag patterns
  - [ ] `sentinel_timestamp` is in RFC 3339/ISO 8601 format
  - [ ] `include` contains valid glob patterns (e.g., `"**/*.md"` not `".md"`)
  - [ ] `version_sample_relative_size` is set
  - [ ] `version_sample_max_size` is set
- [ ] Updated `index.json` to include the new package
- [ ] For monorepos: glob patterns target only the specific package subdirectory

### Additional Notes
<!-- Any other relevant information about the package or special considerations -->