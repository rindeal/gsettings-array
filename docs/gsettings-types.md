# GSettings GVariant Value Types

> Official docs: https://docs.gtk.org/glib/gvariant-format-strings.html

Each value type in GSettings has a unique representation. Here's how you can set different types of values in dconf:

## String (`s`)
A string is a sequence of characters. 
```py
'my-string-value'  # Example of a string
```

## Boolean (`b`)
A boolean represents a truth value and can be either `true` or `false`.
```py
false  # Example of a boolean
```

## Integer (`i`)
An integer is a number without a fractional component.
```py
10  # Example of an integer
```

## Array (`a`)
An array is an ordered collection of values.
```py
['foo', 'bar', 'baz']  # Example of an array of strings (`as`)
[10, 20, 30]  # Example of an array of integers (`ai`)
```

## Tuple (`(ss)`, `(si)`, `(sib)`, `(s(is))`, etc.)
A tuple is an ordered collection of values that may have different types.
```py
('my-string', 10)  # Example of a tuple consisting of a string and an integer (`si`)
('yet-another-string', 30, false)  # Example of a tuple consisting of a string, an integer, and a boolean (`sib`)
('tuple-string', (50, 'inner-string'))  # Example of a tuple consisting of a string and another tuple (`s(is)`)
```

**Note:** The short syntax is represented in parentheses for each type: `s` for string, `b` for boolean, `i` for integer, `a` for array,
and parentheses with types inside for tuple. For example, `a(ss)` represents an array of tuples, each containing two strings.
