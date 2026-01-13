# hidemyemail-cli

CLI tool for managing Apple Hide My Email aliases with Touch ID authentication.

## Installation

Requires Python 3.13+ and macOS.

```bash
pip install .
```

## Setup

Configure your Apple ID credentials (stored in macOS Keychain):

```bash
hme setup
```

## Usage

```bash
# List aliases
hme list
hme list --active          # Active only
hme list --limit 100       # Show more

# Search aliases
hme search "netflix"

# Create alias
hme create "Netflix"
hme create "Shopping" --note "Online stores"

# Update alias
hme update <email> --label "New Label"
hme update <email> --note "New note"

# Deactivate/reactivate
hme deactivate <email>
hme reactivate <email>

# Delete alias
hme delete <email>
hme delete <email> --force  # Skip confirmation
```

## Commands

| Command      | Description                        |
|--------------|------------------------------------|
| `setup`      | Configure Apple ID credentials     |
| `logout`     | Remove stored credentials          |
| `status`     | Show authentication status         |
| `list`       | List all aliases                   |
| `search`     | Search aliases by label/email/note |
| `create`     | Create a new alias                 |
| `update`     | Update alias label or note         |
| `deactivate` | Stop forwarding (reversible)       |
| `reactivate` | Resume forwarding                  |
| `delete`     | Permanently delete alias           |
