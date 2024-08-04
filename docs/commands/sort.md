# Sort Command

The `sort` command allows you to sort all items in your GSettings array.

## Usage

```bash
gsettings-array sort SCHEMA KEY [OPTIONS]
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")

## Options

- `--reverse`: Sort in descending order
- `--dedup`: Remove duplicates after sorting

## Examples

1. Sort input sources:

```bash
gsettings-array sort org.gnome.desktop.input-sources sources
```

2. Sort in reverse order:

```bash
gsettings-array sort --reverse org.gnome.desktop.input-sources sources
```

3. Sort and remove duplicates:

```bash
gsettings-array sort --dedup org.gnome.desktop.input-sources sources
```

4. Sort a list of integers:

```bash
gsettings-array sort org.example.app.settings integer-list
```

5. Sort and print the result without modifying the original array:

```bash
gsettings-array sort org.gnome.desktop.input-sources sources | tee >(gsettings-array ls org.gnome.desktop.input-sources sources)
```

This command sorts the array, prints the sorted result, but doesn't modify the original array.

Remember that the sorting behavior depends on the data type of the array elements. Strings are sorted alphabetically, numbers numerically, and complex types (like tuples) are sorted based on their string representation.
