#!/usr/bin/env python3
#
# SPDX-FileCopyrightText:  ANNO DOMINI 2024  Jan Chren ~rindeal
#
# SPDX-License-Identifier: GPL-3.0-only OR GPL-2.0-only
#

import sys

MIN_SUPPORTED_PYTHON_VERSION = '3.11'
assert sys.version_info >= tuple(map(int, MIN_SUPPORTED_PYTHON_VERSION.split('.')))

import argparse
import copy
import enum
from textwrap import dedent
from typing import Any, Generator


import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib


PROG        = """@@PROG@@"""
VERSION     = """@@VERSION@@"""
HOMEPAGE    = """@@HOMEPAGE@@"""
LICENSE     = """@@LICENSE@@"""
COPYRIGHT   = """@@COPYRIGHT@@"""
DESCRIPTION = """@@DESCRIPTION@@"""


class ArgsMeta(type):
	def __new__(metacls, cls, bases, classdict):
		def is_arg_flag(k, v): return k[0] != '_' and k.isupper() and issubclass(v, str)
		classdict.update({k: k.lower() for k, v in classdict.get('__annotations__', {}).items() if is_arg_flag(k, v)})
		return super().__new__(metacls, cls, bases, classdict)


class ArgsBase(metaclass=ArgsMeta):
	def _arg_dir(self) -> Generator[str, None, None]:
		return (k for k in dir(self) if k[0] != '_' and k.islower())

	def __init__(self, args_ns: argparse.Namespace):
		for key in self._arg_dir():
			if hasattr(args_ns, key) and (old_val := getattr(args_ns, key)) is not None:
				attr_t = type(getattr(self, key))
				try:
					new_val = attr_t(old_val)
				except TypeError as e:
					raise TypeError(f"Invalid type for arg/opt '{key}', expected '{attr_t}', is '{type(old_val)}'") from e
			else:
				new_val = copy.copy(getattr(self, key))
			setattr(self, key, new_val)

	def __repr__(self) -> str:
		attributes = ', '.join(f"{k}={getattr(self, k)!r}" for k in self._arg_dir())
		return f"{self.__class__.__name__}({attributes})"


class SubCmdParserFactory:
	class SubCmdParser:
		def __init__(self, subcmdp: argparse.ArgumentParser):
			self.subcmdp = subcmdp

		def arg(self, *args: Any, **kwargs: Any) -> argparse.Action:
			return self.subcmdp.add_argument(*args, **kwargs)

	def __init__(self, subparsers: argparse._SubParsersAction):
		self.subparsers = subparsers

	def __call__(self, *args: Any, **kwargs: Any) -> SubCmdParser:
		return self.SubCmdParser(self.subparsers.add_parser(*args, **kwargs))


class ArgCmdName(enum.StrEnum):
	_       = ''
	INSERT  = enum.auto()
	LS      = enum.auto()
	SORT    = enum.auto()
	DEDUP   = enum.auto()
	POP     = enum.auto()
	RM      = enum.auto()
	CLEAR   = enum.auto()


class Args(ArgsBase):
	CMD:     str; cmd:     ArgCmdName = ArgCmdName('')
	SCHEMA:  str; schema:  str        = str()
	KEY:     str; key:     str        = str()
	INDEX:   str; index:   int        = int(sys.maxsize)
	ITEMS:   str; items:   list[str]  = list()

	OPT_SORT:    str; opt_sort:    bool = bool(False)
	OPT_REVERSE: str; opt_reverse: bool = bool(False)
	OPT_DEDUP:   str; opt_dedup:   bool = bool(False)
	OPT_CLEAR:   str; opt_clear:   bool = bool(False)


class Utils:
	@staticmethod
	def _maybe_get_schema(schema_str: str) -> Gio.SettingsSchema | None:
		if default_source := Gio.SettingsSchemaSource.get_default():
			return Gio.SettingsSchemaSource.lookup(default_source, schema_str, True)
		return None

	@staticmethod
	def _quote_possible_strings(items: list[Any]):
		checkers = dict(
			is_bool   = lambda s: s.lower() in {'true', 'false'}         ,
			is_array  = lambda s: s[0] == '[' and s[-1] == ']'           ,
			is_tuple  = lambda s: s[0] == '(' and s[-1] == ')'           ,
			is_string = lambda s: (s[0], s[-1]) in {('"',)*2, ("'",)*2}  ,
			is_number = lambda s: s.replace('.', '', 1).isdigit()        ,
		)
		quoted = []
		for item in items:
			if isinstance(item, str) and not any(checker(item) for checker in checkers.values()):
				quote = '"' if "'" in item else "'"
				item = quote + item.replace(quote, "\\" + quote) + quote
			if isinstance(item, bool):
				item = str(item).lower()
			quoted.append(item)
		return quoted


class App:
	@staticmethod
	def _parse_args(raw_arg_list: list[str] | None = None) -> Args:
		indent = ' ' * 4
		main_parser = argparse.ArgumentParser(
			PROG,
			description=DESCRIPTION,
			epilog="\n".join([
				indent*0 + "additional information:",
				indent*1 + f'''Homepage:  {HOMEPAGE}''',
				*[indent*1 + f'''Copyright: {c.strip()}''' for c in COPYRIGHT.split('\n')],
				indent*1 + f'''License:   {LICENSE}''',
			]),
			formatter_class=argparse.RawDescriptionHelpFormatter
		)
		main_parser.add_argument('--version', action='version', version=f"%(prog)s {VERSION}")

		cmdpar = main_parser.add_subparsers(metavar='COMMAND', dest=Args.CMD, help="Task to perform on the array. Available commands are:", required=True)
		
		subcmd = SubCmdParserFactory(cmdpar)
		C = ArgCmdName
		P = {
			C.INSERT:  subcmd(C.INSERT, help="Insert one or more items starting at a specified index."),
			C.LS:      subcmd(C.LS,     help="List all items in the array, each on a new line."),
			C.SORT:    subcmd(C.SORT,   help="Sort all items in the array."),
			C.DEDUP:   subcmd(C.DEDUP,  help="Remove duplicated items from the array."),
			C.POP:     subcmd(C.POP,    help="Print and remove the item at a specified index."),
			C.RM:      subcmd(C.RM,     help="Remove one or more items from the array."),
			C.CLEAR:   subcmd(C.CLEAR,  help="Clear all items from the array."),
		}

		for c in P.values():
			c.arg(metavar='SCHEMA', dest=Args.SCHEMA, help="GSettings schema, eg. `org.gnome.desktop.input-sources`")
			c.arg(metavar='KEY',    dest=Args.KEY,    help="GSettings key, eg. `sources`")
		for c in (P[C.INSERT], P[C.POP]):
			c.arg(metavar='INDEX',  dest=Args.INDEX,  help="Array index, 0 = first, ..., -1 = last", type=int)
		for c in (P[C.INSERT], P[C.RM]):
			c.arg(metavar='ITEM',   dest=Args.ITEMS,  help="Value formatted according to the array's inner type. Use `gsettings range` command to inspect array type.", nargs=argparse.ONE_OR_MORE)
		for c in (P[C.INSERT],):
			c.arg('--clear',   dest=Args.OPT_CLEAR,   help="Run `clear` before main task",    action='store_true')
		for c in (P[C.INSERT], P[C.POP], P[C.RM]):
			c.arg('--sort',    dest=Args.OPT_SORT,    help="Run `sort`  after  main task",    action='store_true')
		for c in (P[C.INSERT], P[C.POP], P[C.RM], P[C.SORT]):
			c.arg('--reverse', dest=Args.OPT_REVERSE, help="Reverse orientation of the sort", action='store_true')
			c.arg('--dedup',   dest=Args.OPT_DEDUP,   help="Run `dedup` after  main task",    action='store_true')

		args_ns = main_parser.parse_args(raw_arg_list)
		args = Args(args_ns)

		if args.opt_reverse and not (args.opt_sort or ArgCmdName.SORT == args.cmd):
			main_parser.error("--reverse requires --sort or sort command")

		return args

	@classmethod
	def run(cls, raw_arg_list: list[str] | None = None) -> int | str:
		args = cls._parse_args(raw_arg_list)
		
		schema = Utils._maybe_get_schema(args.schema)
		if not schema:
			return dedent(f"""
				Error: Schema '{args.schema}' not found. 
				Please check if the schema name is correct and exists in your system. 
				You can list available schemas using 'gsettings list-schemas'.
				Args: {args}
				""").strip()
		if not schema.has_key(args.key):
			return dedent(f"""
				Error: Key '{args.key}' not found in schema '{args.schema}'.
				Please check if the key name is correct. 
				You can list available keys for this schema using 'gsettings list-keys {args.schema}'.
				Args: {args}
				""").strip()

		array_type = schema.get_key(args.key).get_value_type()
		if not array_type.is_array():
			return dedent(f"""
				Error: The key '{args.key}' in schema '{args.schema}' is not an array.
				Its type is '{array_type.dup_string()}'. This tool only works with array-type keys.
				Please choose a different key or use plain 'gsettings' command for non-array types.
				Args: {args}
				""").strip()

		gsettings = Gio.Settings.new(args.schema)
		old_array = gsettings[args.key]

		should_print_diff = args.cmd not in (ArgCmdName.LS, )
		if should_print_diff:
			print("Old value:", old_array, file=sys.stderr)

		input_array_str = "[%s]" % ",".join(Utils._quote_possible_strings(args.items)) if args.items else "[]"
		parsed_array = GLib.Variant.parse(array_type, input_array_str)

		if ArgCmdName.LS == args.cmd:
			for item in Utils._quote_possible_strings(old_array):
				print(item)

		if ArgCmdName.CLEAR == args.cmd or args.opt_clear:
			old_array = gsettings[args.key] = []

		if ArgCmdName.INSERT == args.cmd:
			i = args.index
			if i < 0:
				i += len(old_array) + 1
			gsettings[args.key] = old_array[:i] + list(parsed_array) + old_array[i:]

		if ArgCmdName.POP == args.cmd and len(old_array):
			i = args.index
			mn, mx = -len(old_array), len(old_array)
			if mn <= i < mx:
				if i < 0:
					i += len(old_array)
				print(Utils._quote_possible_strings([old_array[i]])[0])
				gsettings[args.key] = old_array[:i] + old_array[i + 1:]
			else:
				return dedent(f"""
					Error: Index {args.index} is out of bounds.
					The valid range for this array is {mn} <= INDEX < {mx}.
					Please choose an index within this range.
					Current array length: {len(old_array)}
					""").strip()

		if ArgCmdName.RM == args.cmd:
			gsettings[args.key] = [x for x in old_array if x not in parsed_array]

		if ArgCmdName.DEDUP == args.cmd or args.opt_dedup:
			def make_hashable(item: Any) -> Any:
				return tuple(make_hashable(e) for e in item) if isinstance(item, (list, tuple)) else item
			new_array, seen = list(), set()
			for item in old_array:
				item_hash = make_hashable(item)
				if item_hash not in seen:
					seen.add(item_hash)
					new_array.append(item)
			gsettings[args.key] = new_array

		if ArgCmdName.SORT == args.cmd or args.opt_sort:
			new_arr = sorted(old_array)
			if args.opt_reverse:
				new_arr = list(reversed(new_arr))
			gsettings[args.key] = new_arr

		# Writes made to a GSettings are handled asynchronously.
		# Without sync(), new changes won't take effect at all!
		gsettings.sync()

		if should_print_diff:
			print("New value:", gsettings[args.key], file=sys.stderr)

		return 0


def main(raw_arg_list: list[str] | None = None) -> int | str:
	return App().run(raw_arg_list)


if __name__ == '__main__':
	sys.exit(main())
