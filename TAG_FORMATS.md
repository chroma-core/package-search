# Git Tag Name Formatting

This documentation explains how to use the Git tag name formatting module to generate Git tags that adhere to specific naming conventions. The module allows you to define a **format string** using special placeholders (called "commands") that will be replaced with version numbers and dates. It also ensures the final tag name follows Git's naming rules.

## Basic Usage

To format a Git tag, you'll provide a format string that can include literal text and special commands enclosed in curly braces `{}`.

---

### Version Number Commands

You can include components of a version number using the following commands:

| Command   | Description              | Example (for version `1.2.3`) |
| :-------- | :----------------------- | :---------------------------- |
| `{major}` | The major version number | `1`                           |
| `{minor}` | The minor version number | `2`                           |
| `{patch}` | The patch version number | `3`                           |

**Example:**

To create a tag like `v1.2.3`:

v{major}.{minor}.{patch}

### Date Commands

Date commands allow you to incorporate the tag creation date into your tag name. If your format string includes any date commands, you **must** provide a date when formatting the tag.

#### Year Formatting

| Command  | Description          | Example (for `2025`) |
| :------- | :------------------- | :------------------- |
| `{YYYY}` | Full four-digit year | `2025`               |
| `{YY}`   | Two-digit year       | `25`                 |

#### Month Formatting

| Command   | Description                         | Example (for July) |
| :-------- | :---------------------------------- | :----------------- |
| `{M}`     | Numeric month (1-12)                | `7`                |
| `{MM}`    | Numeric month, zero-padded (01-12)  | `07`               |
| `{mo}`    | Abbreviated month name (lowercase)  | `jul`              |
| `{Mo}`    | Abbreviated month name (title case) | `Jul`              |
| `{MO}`    | Abbreviated month name (uppercase)  | `JUL`              |
| `{month}` | Full month name (lowercase)         | `july`             |
| `{Month}` | Full month name (title case)        | `July`             |
| `{MONTH}` | Full month name (uppercase)         | `JULY`             |

#### Day Formatting

| Command | Description                           | Example (for 14th, Monday) |
| :------ | :------------------------------------ | :------------------------- |
| `{D}`   | Numeric day of the month (1-31)       | `14`                       |
| `{DD}`  | Numeric day of the month, zero-padded | `14`                       |
| `{da}`  | Abbreviated weekday name (lowercase)  | `mon`                      |
| `{Da}`  | Abbreviated weekday name (title case) | `Mon`                      |
| `{DA}`  | Abbreviated weekday name (uppercase)  | `MON`                      |
| `{day}` | Full weekday name (lowercase)         | `monday`                   |
| `{Day}` | Full weekday name (title case)        | `Monday`                   |
| `{DAY}` | Full weekday name (uppercase)         | `MONDAY`                   |

**Example:**

To create a tag like `release-2025-07-14`:

release-{YYYY}-{MM}-{DD}

To create a tag like `build-Jul-Mon`:

build-{Mo}-{Da}

---

## Combining Literals and Commands

You can freely mix literal text with any of the commands. Any characters not part of a recognized command within `{}` will be treated as literal text.

**Example:**

prod/{YYYY}.{MM}.{DD}/v{major}.{minor}.{patch}

If the version is `2.0.1` and the date is July 14, 2025, this format string would produce:
`prod/2025.07.14/v2.0.1`

---

## Important Considerations

### Date Requirement

If your format string contains **any** date commands (e.g., `{YYYY}`, `{MM}`, `{DD}`), you **must** provide a date when generating the tag. Failure to do so will result in an error.

### Git Tag Validation

This library automatically validates the generated tag name against Git's naming conventions. If the formatted tag violates any of these rules, an error will be returned, and the tag will not be created.

Here are some of the rules enforced:

- Tags cannot start or end with a slash (`/`).
- Tags cannot end with `.lock`.
- Tags cannot start with a hyphen (`-`).
- Tags cannot contain consecutive slashes (`//`).
- Tags cannot contain `..` (double dots).
- Tags cannot contain `@{.`
- Tags cannot contain the following characters: ` `, `~`, `^`, `:`, `?`, `*`, `[`, `\`.
- Tags cannot contain ASCII control characters (e.g., null, tab, newline).

If you encounter an error during formatting, review your format string and the resulting tag name against these rules.