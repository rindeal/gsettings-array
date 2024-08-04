# List Command

The `list` command (aliased as `ls`) displays all items in your GSettings array, each on a new line.

## Usage

```bash
gsettings-array ls SCHEMA KEY
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")

## Examples

1. List all input sources:

```bash
gsettings-array ls org.gnome.desktop.input-sources sources
```

2. List all startup applications:

```bash
gsettings-array ls org.gnome.gnome-session startup-applications
```

3. List with custom formatting (using shell commands):

```bash
gsettings-array ls org.gnome.desktop.input-sources sources | sed 's/^/- /'
```

This will prefix each item with a dash, creating a Markdown-style list.

4. Count the number of items:

```bash
gsettings-array ls org.gnome.desktop.input-sources sources | wc -l
```

5. Search for specific items:

```bash
gsettings-array ls org.gnome.desktop.input-sources sources | grep 'xkb'
```

This will only show items containing 'xkb'.

The `list` command is particularly useful for inspecting your current settings or as part of more complex shell scripts and pipelines.
