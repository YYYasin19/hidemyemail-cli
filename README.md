# hidemyemail-cli

CLI tool for managing Apple Hide My Email aliases with Touch ID authentication.

## Installation

Download [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```bash
uv tool install .
```

to install it as `hide-my-email` globally.

## Setup

Configure your Apple ID credentials (stored in macOS Keychain):

```bash
hide-my-email setup
```

## Usage

```bash
# List aliases
hide-my-email list
hide-my-email list --active          # Active only
hide-my-email list --limit 100       # Show more

# Search aliases
hide-my-email search "netflix"

# Create alias
hide-my-email create "Netflix"
hide-my-email create "Shopping" --note "Online stores"

# Update alias
hide-my-email update <email> --label "New Label"
hide-my-email update <email> --note "New note"

# Deactivate/reactivate
hide-my-email deactivate <email>
hide-my-email reactivate <email>

# Delete alias
hide-my-email delete <email>
hide-my-email delete <email> --force  # Skip confirmation
```

## Commands

| Command      | Description                        |
| ------------ | ---------------------------------- |
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
