"""
Command line script for plantuml2cpp
"""

import pathlib
import subprocess
import argparse
from typing import NamedTuple

from .codegen import CodeGenerator
from .parser import PlantUmlStateDiagram


class CommandLineArgs(NamedTuple):
    """Parsed command line arguments"""
    puml_file: pathlib.Path
    output_file: pathlib.Path
    namespace: str
    classname: str
    noformat: bool


def main() -> None:
    """Main entry point when running as a standalone script"""
    args = parse_command_line()

    diagram = PlantUmlStateDiagram(args.puml_file)

    codegen = CodeGenerator(diagram)
    content = codegen.generate(args.namespace, args.classname)

    with open(args.output_file, 'w') as f:
        f.write(content)

    if not args.noformat:
        run_clang_format(args.output_file)


def parse_command_line() -> CommandLineArgs:
    """Parse the command line"""
    parser = argparse.ArgumentParser(prog='plantuml2cpp', description='''
        C++ code generator for finite state machines from PlantUML state diagrams. The generated
        code will be run through clang-format in the directory of the output file, thereby using
        any existing .clang-format configuration files to match the code style of the project.''')

    parser.add_argument('puml_file', type=pathlib.Path,
                        help='PlantUML state machine description file')

    parser.add_argument('output_file', type=pathlib.Path, nargs='?',
                        help='output file (C++ header) or directory; default is the name of the input file with the'
                             ' .h extension')

    parser.add_argument('--namespace', '-n', type=str, default='',
                        help='namespace for the generated code; default is no namespace')

    parser.add_argument('--classname', '-c', type=str,
                        help='name of the generated class; default is the stem of the input filename in Pascal case')

    parser.add_argument('--noformat', '-f', action='store_true', default=False,
                        help='do not run clang-format to format the generated code')

    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = args.puml_file.with_suffix('.h')
    elif args.output_file.is_dir():
        args.output_file /= args.puml_file.with_suffix('.h').name

    if args.classname is None:
        args.classname = to_pascal_case(args.puml_file.stem)

    return args


def run_clang_format(filename: str) -> None:
    """Runs clang-format on the given file"""
    subprocess.check_call(['clang-format', '-assume-filename=fsm.h', '-i', filename])


def to_pascal_case(string: str) -> str:
    """Converts the given string to Pascal case"""
    return string.replace("_", " ").title().replace(" ", "")


if __name__ == '__main__':
    main()

# TODO: Fix internal transitions. They should be modeled like the entry/exit transitions and not as arrows
