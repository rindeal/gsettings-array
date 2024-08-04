# GSettings Array Utility Usage Guide

This guide provides a quick overview of how to use the GSettings Array Utility. For detailed information on each command, please refer to their individual documentation pages.

## Basic Syntax

The general syntax for using the GSettings Array Utility is:

```bash
gsettings-array COMMAND SCHEMA KEY [OPTIONS]
```

- `COMMAND`: The operation you want to perform (e.g., insert, ls, sort)
- `SCHEMA`: The GSettings schema you're working with
- `KEY`: The specific key within the schema that holds the array
- `[OPTIONS]`: Additional options specific to each command

## Available Commands

1. 🎯 **insert**: Add items to your array
   ```bash
   gsettings-array insert org.gnome.example my-array-key
   ```

2. 📋 **ls**: List all items in your array
   ```bash
   gsettings-array ls org.gnome.example my-array-key
   ```

3. 🔄 **sort**: Sort all items in your array
   ```bash
   gsettings-array sort org.gnome.example my-array-key
   ```

4. 🧹 **dedup**: Remove duplicate items from your array
   ```bash
   gsettings-array dedup org.gnome.example my-array-key
   ```

5. 🎣 **pop**: Remove and print an item at a specified index
   ```bash
   gsettings-array pop org.gnome.example my-array-key
   ```

6. ❌ **rm**: Remove specific items from your array
   ```bash
   gsettings-array rm org.gnome.example my-array-key
   ```

7. 🧼 **clear**: Remove all items from your array
   ```bash
   gsettings-array clear org.gnome.example my-array-key
   ```

## Getting Help

For quick help on any command, use the `-h` or `--help` option:

```bash
gsettings-array COMMAND -h
```

## Further Reading

For more detailed information on each command, including all available options and examples, please refer to the following pages:

- [🎯 Insert Command](commands/insert.md)
- [📋 List Command](commands/list.md)
- [🔄 Sort Command](commands/sort.md)
- [🧹 Deduplicate Command](commands/dedup.md)
- [🎣 Pop Command](commands/pop.md)
- [❌ Remove Command](commands/rm.md)
- [🧼 Clear Command](commands/clear.md)
