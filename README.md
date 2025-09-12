# Chroma Package Search

This repository contains a curated list of public code packages that Chroma keeps indexed into Chroma collections. The repository currently indexes **3K+** packages across various registries. Please create a PR or open an issue for any dependency you would like to see indexed!

Quick links:

* [Install Package Search MCP](https://trychroma.com/package-search)
* [View available packages](https://github.com/chroma-core/package-search/blob/main/versions.json)
* [Add a package](https://github.com/chroma-core/package-search/issues/new?template=package-request.md)

## How to Install

Chroma’s Package Search MCP server is a remote MCP server you can use from many clients.

| Field | Value |
|-------|-------|
| Server URL | `https://mcp.trychroma.com/package-search/v1` |
| Auth header | `x-chroma-token: <YOUR_CHROMA_API_KEY>` |

> [!NOTE]
> Get an API key at [trychroma.com/package-search](https://trychroma.com/package-search)

### How to configure in common clients

<details>
<summary><b>Cursor</b></summary>


Create or edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "package-search": {
      "transport": "streamable_http",
      "url": "https://mcp.trychroma.com/package-search/v1",
      "headers": {
        "x-chroma-token": "<YOUR_CHROMA_API_KEY>"
      }
    }
  }
}
```

</details>


<details>
<summary><b>VS Code (Copilot Chat MCP)</b></summary>

Create or edit `.vscode/mcp.json`:

```json
{
  "servers": {
    "package-search": {
      "type": "http",
      "url": "https://mcp.trychroma.com/package-search/v1",
      "headers": {
        "x-chroma-token": "<YOUR_CHROMA_API_KEY>"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Windsurf</b></summary>


Open the Windsurf MCP settings and edit to include:

```json
{
  "mcpServers": {
    "package-search": {
      "serverUrl": "https://mcp.trychroma.com/package-search/v1",
      "headers": {
        "x-chroma-token": "<YOUR_CHROMA_API_KEY>"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Codex</b></summary>

Add the following to your `~/.codex/config.toml` file with your Chroma Cloud API key:

```toml
[mcp_servers.package-search]
command = "npx"
args = ["mcp-remote", "https://mcp.trychroma.com/package-search/v1", "--header", "x-chroma-token: ${X_CHROMA_TOKEN}"]
env = { X_CHROMA_TOKEN = "<YOUR_CHROMA_API_KEY>" }
```

</details>

<details>
<summary><b>Claude Code</b></summary>

Run the following command in your terminal:

```bash
claude mcp add --transport http package-search https://mcp.trychroma.com/package-search/v1 --header "x-chroma-token: <YOUR_CHROMA_API_KEY>"
```

</details>

<details>
<summary><b>OpenAI SDK</b></summary>

```python
from openai import OpenAI

client = OpenAI(api_key="<YOUR_OPENAI_API_KEY>")

resp = client.responses.create(
    model="gpt-5",
    input="Explain how colorlog implements testing in python",
    tools=[
        {
            "type": "mcp",
            "server_label": "package-search",
            "server_url": "https://mcp.trychroma.com/package-search/v1",
            "headers": {"x-chroma-token": "<YOUR_CHROMA_API_KEY>"},
            "require_approval": "never"
        }
    ],
)
print(resp)
```

</details>


<details>
<summary><b>Anthropic SDK</b></summary>

```
import anthropic

client = anthropic.Anthropic(api_key="<YOUR_ANTHROPIC_API_KEY>")

response = client.beta.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Explain how colorlog implements testing in python"}],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://mcp.trychroma.com/package-search/v1",
            "name": "package-search",
            "authorization_token": "<YOUR_CHROMA_API_KEY>"
        }
    ],
    betas=["mcp-client-2025-04-04"],
)
print(response)
```

(The Package Search MCP server has special-case handling for the Anthropic SDK's authorization headers.)

</details>


<details>
<summary><b>MCP SDK (Python)</b></summary>

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client(
        "https://mcp.trychroma.com/package-search/v1",
        headers={"x-chroma-token": "<YOUR_CHROMA_API_KEY>"},
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool(
                name="package_search_grep",
                arguments={"package_name": "colorlog", "registry_name": "py_pi", "pattern": "\bclass\b"},
            )
            print(f"Got result: {result}")
            print(f"Available tools: {[t.name for t in tools.tools]}")

asyncio.run(main())
```

</details>


<details>
<summary><b>Google Gemini SDK</b></summary>

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from google import genai

client = genai.Client(api_key="<YOUR_GEMINI_API_KEY>")

async def run():
    async with streamablehttp_client(
        "https://mcp.trychroma.com/package-search/v1",
        headers={"x-chroma-token": "<YOUR_CHROMA_API_KEY>"},
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            prompt = "what logging levels are available in uber's zap go module?"
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(temperature=0, tools=[session]),
            )
            print(response.text if hasattr(response, "text") else response)
asyncio.run(run())
```

</details>


<details>
<summary><b>Ollama (via <code>ollmcp</code>)</b></summary>


Create mcp_config.json:

```json
{
  "mcpServers": {
    "package-search": {
      "type": "streamable_http",
      "url": "https://mcp.trychroma.com/package-search/v1",
      "headers": { "x-chroma-token": "<YOUR_CHROMA_API_KEY>" },
      "disabled": false
    }
  }
}
```

Run:

```
ollmcp --servers-json /path/to/mcp_config.json --model qwen2.5
```

</details>


<details>
<summary><b>Open Code</b></summary>


Add to `~/.config/opencode/opencode.json:`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "package-search": {
      "type": "remote",
      "url": "https://mcp.trychroma.com/package-search/v1",
      "enabled": true,
      "headers": { "x-chroma-token": "<YOUR_CHROMA_API_KEY>" }
    }
  }
}
```

</details>

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

### Preferred Method: Pull Request (Faster Review)

We strongly encourage submitting a Pull Request when you have all the required configuration information, as PRs receive **faster review turnaround times**. Here's how:

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
5. **Create a Pull Request** with a clear description of the package you're adding (use our [PR template](.github/pull_request_template.md))
6. **Wait for review** - a member of the Chroma team will review your PR

### Alternative Method: Submit an Issue

If you don't have all the required configuration details (such as version sampling logic or tag formats), you can submit an issue instead:

1. **Create a new issue** using our [package request issue template](.github/ISSUE_TEMPLATE/package-request.md)
2. **Provide the package name, registry, and a link** to its homepage or GitHub repository
3. **Include any configuration details you know** - the more information you provide, the faster we can process your request
4. **Wait for the Chroma team** to gather the missing configuration details and add the package

**Note**: Issues typically have longer processing times compared to PRs since our team needs to research and configure the missing details.

## Review Process

- All PRs are reviewed by Chroma team members
- We evaluate packages based on relevance, popularity, and community value
- Accepted packages will be indexed and made searchable through Chroma's [Package Search MCP Server]()

## Current Index

The repository currently indexes packages from:
- **NPM** - JavaScript/TypeScript packages
- **PyPI** - Python packages
- **crates.io** - Rust crates
- **Golang Proxy** - Go modules
- **GitHub Releases** - Packages distributed via GitHub Releases

## Contributing Guidelines

- Ensure the package is publicly available and well-maintained
- Verify the `native_identifier` matches the package name in the registry exactly
- Confirm the GitHub repository exists and is accessible
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
