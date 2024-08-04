# Clear Command

The `clear` command removes all items from your GSettings array, resulting in an empty array.

## Usage

```bash
gsettings-array clear SCHEMA KEY
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")

## Examples

1. Clear all input sources:

```bash
gsettings-array clear org.gnome.desktop.input-sources sources
```

2. Clear a list of integers:

```bash
gsettings-array clear org.example.app.settings integer-list
```

3. Clear and verify:

```bash
gsettings-array clear org.gnome.desktop.input-sources sources && gsettings-array ls org.gnome.desktop.input-sources sources
```

This command clears the array and then lists its contents (which should be empty).

4. Clear, then add a default item:

```bash
gsettings-array clear org.gnome.desktop.input-sources sources && gsettings-array insert org.gnome.desktop.input-sources sources 0 "('xkb', 'us')"
```

This example clears the array and then adds a default item.

5. Backup, clear, and restore:

```bash
backup=$(gsettings-array ls org.gnome.desktop.input-sources sources)
gsettings-array clear org.gnome.desktop.input-sources sources
echo "$backup" | xargs gsettings-array insert org.gnome.desktop.input-sources sources 0
```

This script backs up the current array, clears it, and then restores the backup.

Be cautious when using the `clear` command, as it will remove all items from the array without confirmation. It's a good practice to back up your settings before clearing them, especially for critical system settings.
