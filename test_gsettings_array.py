#!/usr/bin/env python3
#
# SPDX-FileCopyrightText:  ANNO DOMINI 2024  Jan Chren ~rindeal  <dev.rindeal gmail com>
#
# SPDX-License-Identifier: GPL-3.0-only OR GPL-2.0-only
#

import pytest
import subprocess
from pathlib import Path
import tempfile
from typing import Generator, Dict, NamedTuple, Any
import os
import io
import sys
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

# Import the main function from your script
from gsettings_array import main as gsettings_array_main

class CompletedProcess(NamedTuple):
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

class SchemaBuilder:
    def __init__(self, schema_id: str, path: str):
        self.schema_id = schema_id
        self.path = path
        self.keys: list[str] = []

    def add_key(self, name: str, type: str, default: str):
        self.keys.append(f"""
            <key name="{name}" type="{type}">
              <default>{default}</default>
              <summary>Test {name}</summary>
              <description>A {type} for testing purposes</description>
            </key>
        """)
        return self

    def build(self) -> str:
        return f"""
        <schemalist>
          <schema id="{self.schema_id}" path="{self.path}">
            {"".join(self.keys)}
          </schema>
        </schemalist>
        """

def setup_schema(schema_content: str, schema_dir: Path) -> str:
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_id = schema_content.split('id="')[1].split('"')[0]
    schema_path = schema_dir / f'{schema_id}.gschema.xml'
    schema_path.write_text(schema_content)
    subprocess.run(['glib-compile-schemas', str(schema_dir)], check=True)
    return schema_id

@pytest.fixture(scope="module")
def schema_setup() -> Generator[Dict[str, str], None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        schema_dir = Path(temp_dir) / 'glib-2.0' / 'schemas'
        
        schemas = {
            'array_schema': SchemaBuilder('org.example.test', '/org/example/test/')
                .add_key('test-array', 'as', '[]')
                .add_key('test-int-array', 'ai', '[]')
                .add_key('test-bool-array', 'ab', '[]')
                .add_key('test-double-array', 'ad', '[]')
                .add_key('test-array-of-arrays', 'aas', '[]')
                .add_key('test-array-of-tuples', 'a(si)', '[]')
                .add_key('test-array-of-tuples-of-arrays', 'a(sai)', '[]')
                .build(),
            'non_array_schema': SchemaBuilder('org.example.test2', '/org/example/test2/')
                .add_key('test-string', 's', "''")
                .build()
        }
        for x in schemas.values():
            print(x)
        
        schema_ids = {name: setup_schema(content, schema_dir) for name, content in schemas.items()}
        
        old_schema_path = os.environ.get('GSETTINGS_SCHEMA_DIR')
        os.environ['GSETTINGS_SCHEMA_DIR'] = str(schema_dir)
        
        yield schema_ids
        
        if old_schema_path:
            os.environ['GSETTINGS_SCHEMA_DIR'] = old_schema_path
        else:
            os.environ.pop('GSETTINGS_SCHEMA_DIR', None)

def run_cli(args: list[str]) -> CompletedProcess:
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    
    try:
        result = gsettings_array_main(args)
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
        
        if isinstance(result, str):
            returncode = 1
            stderr += result + '\n'
        else:
            returncode = 0 if result is None else result
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    
    return CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)

def set_and_test(schema_id: str, key: str, value: Any, expected: Any):
    settings = Gio.Settings.new(schema_id)
    settings[key] = GLib.Variant.parse(None, str(value))
    settings.sync()
    result = run_cli(['ls', schema_id, key])
    assert result.returncode == 0
    assert [line.strip() for line in result.stdout.strip().split('\n')] == expected
    return settings

@pytest.mark.parametrize("key,         value,                            expected", [
    ('test-array',                     "['item1', 'item2', 'item3']",    ["'item1'", "'item2'", "'item3'"]),
    ('test-int-array',                 "[1, 2, 3]",                      ["1", "2", "3"]),
    ('test-bool-array',                "[true, false, true]",            ["true", "false", "true"]),
    ('test-double-array',              "[1.1, 2.2, 3.3]",                ["1.1", "2.2", "3.3"]),
    ('test-array-of-arrays',           "[['a', 'b'], ['c', 'd']]",       ["['a', 'b']", "['c', 'd']"]),
    ('test-array-of-tuples',           "[('a', 1), ('b', 2)]",           ["('a', 1)", "('b', 2)"]),
    ('test-array-of-tuples-of-arrays', "[('a', [1, 2]), ('b', [3, 4])]", ["('a', [1, 2])", "('b', [3, 4])"]),
])
def test_ls_command(schema_setup, key, value, expected):
    set_and_test(schema_setup['array_schema'], key, value, expected)

@pytest.mark.parametrize("key,         initial,                    test,                         insert,   index, expected", [
    ('test-array',                     "['item1', 'item3']",       ["'item1'", "'item3'"],       'item2',      1, ['item1', 'item2', 'item3']),
    ('test-int-array',                 "[1, 3]",                   ['1', '3'],                   '2',          1, [1, 2, 3]),
    ('test-bool-array',                "[true, false]",            ['true', 'false'],            'true',       1, [True, True, False]),
    ('test-double-array',              "[1.1, 3.3]",               ['1.1', '3.3'],               '2.2',        1, [1.1, 2.2, 3.3]),
    ('test-array-of-arrays',           "[['a'], ['c']]",           ["['a']", "['c']"],           "['b']",      1, [['a'], ['b'], ['c']]),
    ('test-array-of-tuples',           "[('a', 1), ('c', 3)]",     ["('a', 1)", "('c', 3)"],     "('b', 2)",   1, [('a', 1), ('b', 2), ('c', 3)]),
    ('test-array-of-tuples-of-arrays', "[('a', [1]), ('c', [3])]", ["('a', [1])", "('c', [3])"], "('b', [2])", 1, [('a', [1]), ('b', [2]), ('c', [3])]),
])
def test_insert_command(schema_setup, key, initial, test, insert, index, expected):
    settings = set_and_test(schema_setup['array_schema'], key, initial, test)
    result = run_cli(['insert', schema_setup['array_schema'], key, str(index), insert])
    assert result.returncode == 0
    assert settings.get_value(key).unpack() == expected

@pytest.mark.parametrize("key,         initial,                          test,                                expected", [
    ('test-array',                     "['c', 'a', 'b']",                ["'c'", "'a'", "'b'"],               ['a', 'b', 'c']),
    ('test-int-array',                 "[3, 1, 2]",                      ['3', '1', '2'],                     [1, 2, 3]),
    ('test-bool-array',                "[true, false, true]",            ['true', 'false', 'true'],           [False, True, True]),
    ('test-double-array',              "[3.3, 1.1, 2.2]",                ['3.3', '1.1', '2.2'],               [1.1, 2.2, 3.3]),
    ('test-array-of-arrays',           "[['c'], ['a'], ['b']]",          ["['c']", "['a']", "['b']"],         [['a'], ['b'], ['c']]),
    ('test-array-of-tuples',           "[('c', 3), ('a', 1), ('b', 2)]", ["('c', 3)", "('a', 1)", "('b', 2)"], [('a', 1), ('b', 2), ('c', 3)]),
    ('test-array-of-tuples-of-arrays', "[('c', [3]), ('a', [1]), ('b', [2])]", ["('c', [3])", "('a', [1])", "('b', [2])"], [('a', [1]), ('b', [2]), ('c', [3])]),
])
def test_sort_command(schema_setup, key, initial, test, expected):
    settings = set_and_test(schema_setup['array_schema'], key, initial, test)
    result = run_cli(['sort', schema_setup['array_schema'], key])
    assert result.returncode == 0
    assert settings.get_value(key).unpack() == expected

@pytest.mark.parametrize("key,         initial,                          test,                                expected", [
    ('test-array',                     "['a', 'b', 'a', 'c', 'b']",      ["'a'", "'b'", "'a'", "'c'", "'b'"], ['a', 'b', 'c']),
    ('test-int-array',                 "[1, 2, 1, 3, 2]",                ['1', '2', '1', '3', '2'],           [1, 2, 3]),
    ('test-bool-array',                "[true, false, true, false]",     ['true', 'false', 'true', 'false'],  [True, False]),
    ('test-double-array',              "[1.1, 2.2, 1.1, 3.3, 2.2]",      ['1.1', '2.2', '1.1', '3.3', '2.2'], [1.1, 2.2, 3.3]),
    ('test-array-of-arrays',           "[['a'], ['b'], ['a'], ['c'], ['b']]", ["['a']", "['b']", "['a']", "['c']", "['b']"], [['a'], ['b'], ['c']]),
    ('test-array-of-tuples',           "[('a', 1), ('b', 2), ('a', 1), ('c', 3), ('b', 2)]", ["('a', 1)", "('b', 2)", "('a', 1)", "('c', 3)", "('b', 2)"], [('a', 1), ('b', 2), ('c', 3)]),
    ('test-array-of-tuples-of-arrays', "[('a', [1]), ('b', [2]), ('a', [1]), ('c', [3]), ('b', [2])]", ["('a', [1])", "('b', [2])", "('a', [1])", "('c', [3])", "('b', [2])"], [('a', [1]), ('b', [2]), ('c', [3])]),
])
def test_dedup_command(schema_setup, key, initial, test, expected):
    settings = set_and_test(schema_setup['array_schema'], key, initial, test)
    result = run_cli(['dedup', schema_setup['array_schema'], key])
    assert result.returncode == 0
    assert settings.get_value(key).unpack() == expected

@pytest.mark.parametrize("key,         initial,                          test,                         index,  expected_pop,  expected_remain", [
    ('test-array',                     "['item1', 'item2', 'item3']",    ["'item1'", "'item2'", "'item3'"],  1,     'item2',       ['item1', 'item3']),
    ('test-int-array',                 "[1, 2, 3]",                      ['1', '2', '3'],                    1,     '2',           [1, 3]),
    ('test-bool-array',                "[true, false, true]",            ['true', 'false', 'true'],          1,     'false',       [True, True]),
    ('test-double-array',              "[1.1, 2.2, 3.3]",                ['1.1', '2.2', '3.3'],              1,     '2.2',         [1.1, 3.3]),
    ('test-array-of-arrays',           "[['a'], ['b'], ['c']]",          ["['a']", "['b']", "['c']"],        1,     "['b']",       [['a'], ['c']]),
    ('test-array-of-tuples',           "[('a', 1), ('b', 2), ('c', 3)]", ["('a', 1)", "('b', 2)", "('c', 3)"], 1,   "('b', 2)",    [('a', 1), ('c', 3)]),
    ('test-array-of-tuples-of-arrays', "[('a', [1]), ('b', [2]), ('c', [3])]", ["('a', [1])", "('b', [2])", "('c', [3])"], 1, "('b', [2])", [('a', [1]), ('c', [3])]),
])
def test_pop_command(schema_setup, key, initial, test, index, expected_pop, expected_remain):
    settings = set_and_test(schema_setup['array_schema'], key, initial, test)
    result = run_cli(['pop', schema_setup['array_schema'], key, str(index)])
    assert result.returncode == 0
    assert expected_pop in result.stdout
    assert settings.get_value(key).unpack() == expected_remain

@pytest.mark.parametrize("key,         initial,                          test,                         remove,       expected", [
    ('test-array',                     "['item1', 'item2', 'item3']",    ["'item1'", "'item2'", "'item3'"], 'item2',       ['item1', 'item3']),
    ('test-int-array',                 "[1, 2, 3]",                      ['1', '2', '3'],                   '2',           [1, 3]),
    ('test-bool-array',                "[true, false, true]",            ['true', 'false', 'true'],         'false',       [True, True]),
    ('test-double-array',              "[1.1, 2.2, 3.3]",                ['1.1', '2.2', '3.3'],             '2.2',         [1.1, 3.3]),
    ('test-array-of-arrays',           "[['a'], ['b'], ['c']]",          ["['a']", "['b']", "['c']"],       "['b']",       [['a'], ['c']]),
    ('test-array-of-tuples',           "[('a', 1), ('b', 2), ('c', 3)]", ["('a', 1)", "('b', 2)", "('c', 3)"], "('b', 2)", [('a', 1), ('c', 3)]),
    ('test-array-of-tuples-of-arrays', "[('a', [1]), ('b', [2]), ('c', [3])]", ["('a', [1])", "('b', [2])", "('c', [3])"], "('b', [2])", [('a', [1]), ('c', [3])]),
])
def test_rm_command(schema_setup, key, initial, test, remove, expected):
    settings = set_and_test(schema_setup['array_schema'], key, initial, test)
    result = run_cli(['rm', schema_setup['array_schema'], key, remove])
    assert result.returncode == 0
    assert settings.get_value(key).unpack() == expected

if __name__ == '__main__':
    pytest.main([__file__])