# Pop Command

The `pop` command prints and removes the item at a specified index from your GSettings array.

## Usage

```bash
gsettings-array pop SCHEMA KEY INDEX
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")
- `INDEX`: The position of the item to remove (0-based, use negative numbers to count from the end)

## Examples

1. Remove and print the first item:

```bash
gsettings-array pop org.gnome.desktop.input-sources sources 0
```

2. Remove and print the last item:

```bash
gsettings-array pop org.gnome.desktop.input-sources sources -1
```

3. Remove and print the second-to-last item:

```bash
gsettings-array pop org.gnome.desktop.input-sources sources -2
```

4. Pop an item and use it in a script:

```bash
popped_item=$(gsettings-array pop org.gnome.desktop.input-sources sources 0)
echo "Removed item: $popped_item"
```

5. Pop an item and immediately insert it at a different position:

```bash
popped_item=$(gsettings-array pop org.gnome.desktop.input-sources sources 0)
gsettings-array insert org.gnome.desktop.input-sources sources -1 "$popped_item"
```

This example moves the first item to the end of the array.

Remember that the `pop` command modifies your GSettings array by removing the specified item. If you need to preserve the original array, consider using the `ls` command to view items without modifying the array.
