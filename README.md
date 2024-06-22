# GSettings Array Manipulator

[![Codecov](https://img.shields.io/codecov/c/github/rindeal/gsettings-array)](https://app.codecov.io/github/rindeal/gsettings-array/blob/master/gsettings_array.py)

Welcome to the **GSettings Array Manipulator**, a powerful command-line tool designed to simplify and streamline your interactions with GSettings arrays. With this tool, you can perform a variety of tasks, from inserting items into an array to sorting and deduplicating items, all with a few simple commands.

## Features

- **Insert**: Add one or more items to your array at a specified index.
- **List**: Display all items in your array, each on a new line.
- **Sort**: Sort all items in your array.
- **Deduplicate**: Remove duplicate items from your array.
- **Pop**: Print and remove the item at a specified index.
- **Remove**: Delete one or more items from your array.
- **Clear**: Remove all items from your array.

## Installation

You can download and make the script executable using the following commands:

```bash
wget https://gist.github.com/rindeal/c5786254410028f760ee2351d884a744/raw/gsettings-array.py
chmod +x gsettings-array.py
```

## Usage

The general usage of the GSettings Array Manipulator is as follows:

```bash
./gsettings-array.py COMMAND
```

Replace `COMMAND` with one of the available commands listed in the Features section.

For detailed usage instructions for each command, use the `-h` or `--help` option after the command, like so:

```bash
./gsettings-array.py COMMAND -h
```

## Examples

Here are some examples of how to use the various commands:

1. **Insert Command**:

    ```bash
    gsettings-array insert --dedup "org.gnome.desktop.input-sources" "sources" 0 "('xkb', 'us+cz_sk_de')"
    ```

    This command inserts the tuple `('xkb', 'us+cz_sk_de')` at index 0 in the `sources` array of the `org.gnome.desktop.input-sources` schema. The `--dedup` option ensures that no duplicates will be present in the array.

2. **List Command**:

    ```bash
    gsettings-array ls "org.gnome.desktop.input-sources" "sources"
    ```

    This command lists all items in the `sources` array of the `org.gnome.desktop.input-sources` schema.

3. **Sort Command**:

    ```bash
    gsettings-array sort "org.gnome.desktop.input-sources" "sources"
    ```

    This command sorts all items in the `sources` array of the `org.gnome.desktop.input-sources` schema.

4. **Deduplicate Command**:

    ```bash
    gsettings-array dedup "org.gnome.desktop.input-sources" "sources"
    ```

    This command removes duplicate items from the `sources` array of the `org.gnome.desktop.input-sources` schema.

5. **Pop Command**:

    ```bash
    gsettings-array pop "org.gnome.desktop.input-sources" "sources" 0
    ```

    This command prints and removes the item at index 0 from the `sources` array of the `org.gnome.desktop.input-sources` schema.

6. **Remove Command**:

    ```bash
    gsettings-array rm "org.gnome.desktop.input-sources" "sources" "('xkb', 'us+cz_sk_de')"
    ```

    This command removes the tuple `('xkb', 'us+cz_sk_de')` from the `sources` array of the `org.gnome.desktop.input-sources` schema.

7. **Clear Command**:

    ```bash
    gsettings-array clear "org.gnome.desktop.input-sources" "sources"
    ```

    This command removes all items from the `sources` array of the `org.gnome.desktop.input-sources` schema.
