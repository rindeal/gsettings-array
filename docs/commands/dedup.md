# Deduplicate Command

The `dedup` command removes duplicate items from your GSettings array, keeping only the first occurrence of each unique item.

## Usage

```bash
gsettings-array dedup SCHEMA KEY [OPTIONS]
```

- `SCHEMA`: The GSettings schema (e.g., "org.gnome.desktop.input-sources")
- `KEY`: The key within the schema (e.g., "sources")

## Options

- `--sort`: Sort the array after removing duplicates
- `--reverse`: Reverse the sort order (only applicable with --sort)

## Examples

1. Remove duplicates from input sources:

```bash
gsettings-array dedup org.gnome.desktop.input-sources sources
```

2. Remove duplicates and sort:

```bash
gsettings-array dedup --sort org.gnome.desktop.input-sources sources
```

3. Remove duplicates, sort in reverse order:

```bash
gsettings-array dedup --sort --reverse org.gnome.desktop.input-sources sources
```

4. Remove duplicates from a list of integers:

```bash
gsettings-array dedup org.example.app.settings integer-list
```

5. Remove duplicates and print the result without modifying the original array:

```bash
gsettings-array dedup org.gnome.desktop.input-sources sources | tee >(gsettings-array ls org.gnome.desktop.input-sources sources)
```

This command removes duplicates, prints the result, but doesn't modify the original array.

Note that the deduplication process considers items as duplicates if they have the exact same value and type. For complex types like tuples, all elements within the tuple must match for it to be considered a duplicate.
