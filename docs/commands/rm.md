# Remove Command

The `rm` command deletes one or more specified items from your GSettings array.

## Usage

```bash
gsettings-array rm SCHEMA KEY ITEM [ITEM ...]
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")
- `ITEM`: One or more items to remove from the array

## Examples

1. Remove a single item:

```bash
gsettings-array rm org.gnome.desktop.input-sources sources "('xkb', 'us')"
```

2. Remove multiple items:

```bash
gsettings-array rm org.gnome.desktop.input-sources sources "('xkb', 'us')" "('xkb', 'de')"
```

3. Remove all occurrences of an item:

```bash
gsettings-array rm org.gnome.desktop.input-sources sources "('xkb', 'us')"
```

This will remove all instances of `('xkb', 'us')` from the array.

4. Remove items from a list of integers:

```bash
gsettings-array rm org.example.app.settings integer-list 42 17
```

5. Remove items and print the updated array:

```bash
gsettings-array rm org.gnome.desktop.input-sources sources "('xkb', 'us')" && gsettings-array ls org.gnome.desktop.input-sources sources
```

This command removes the specified item and then lists the updated array.

Note that the `remove` command will remove all occurrences of the specified item(s) from the array. If you need to remove an item at a specific position, consider using the `pop` command instead.
