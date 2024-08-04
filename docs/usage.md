# Usage

The general usage of the GSettings Array Utility is as follows:

```bash
gsettings-array COMMAND SCHEMA KEY [OPTIONS]
```

Replace `COMMAND` with one of the available commands:

- `insert`: Add one or more items to your array at a specified index.
- `ls`: Display all items in your array, each on a new line.
- `sort`: Sort all items in your array.
- `dedup`: Remove duplicate items from your array.
- `pop`: Print and remove the item at a specified index.
- `rm`: Delete one or more items from your array.
- `clear`: Remove all items from your array.

For detailed usage instructions for each command, use the `-h` or `--help` option after the command, like so:

```bash
gsettings-array COMMAND -h
```
