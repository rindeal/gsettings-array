# Insert Command

The `insert` command allows you to add one or more items to your GSettings array at a specified index.

## Usage

```bash
gsettings-array insert SCHEMA KEY INDEX ITEM [ITEM ...]
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")
- `INDEX`: The position where the item(s) should be inserted (0-based)
- `ITEM`: One or more items to insert

## Options

- `--dedup`: Remove duplicates after insertion
- `--sort`: Sort the array after insertion
- `--reverse`: Reverse the sort order (only applicable with --sort)

## Examples

1. Insert a single item:

```bash
gsettings-array insert org.gnome.desktop.input-sources sources 0 "('xkb', 'us')"
```

2. Insert multiple items:

```bash
gsettings-array insert org.gnome.desktop.input-sources sources 1 "('xkb', 'de')" "('xkb', 'fr')"
```

3. Insert and deduplicate:

```bash
gsettings-array insert --dedup org.gnome.desktop.input-sources sources 0 "('xkb', 'us')"
```

4. Insert, sort, and deduplicate:

```bash
gsettings-array insert --sort --dedup org.gnome.desktop.input-sources sources 0 "('xkb', 'es')"
```

5. Insert at the end of the array:

```bash
gsettings-array insert org.gnome.desktop.input-sources sources -1 "('xkb', 'it')"
```

Remember to use the appropriate data types for your specific GSettings schema and key.
