import unittest
import subprocess
import pathlib
import sys
import shutil
import textwrap
from typing import List, Union


class TestMain(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

        self.tests_dir = pathlib.Path(__file__).parent
        self.out_dir = self.tests_dir / 'out'

        shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def run_command(self, *args, **kwargs) -> str:
        """Runs an external command and returns the output captured from stdout"""
        res = subprocess.run(*args, **kwargs, capture_output=True)
        err_msg = '\n'.join([f'{args[0][0]} exited with code {res.returncode}',
                             f'===== stdout =====\n{(res.stdout or b"").decode()}------------------',
                             f'===== stderr =====\n{(res.stderr or b"").decode()}------------------'])
        self.assertEqual(res.returncode, 0, msg=err_msg)
        return (res.stdout or b'').decode()

    def run_compiled_executable(self, executable_file: str) -> str:
        """Runs the compiled, generated C++ code and returns the output captured from stdout"""
        out_file = self.out_dir / executable_file
        return self.run_command([out_file])

    def run_main(self, *args: List[Union[str, pathlib.Path]]):
        """Runs the plantuml2cpp main script"""
        cwd = pathlib.Path(__file__).parent.parent
        self.run_command([sys.executable, '-m', 'plantuml2cpp'] + list(args), cwd=cwd)

    def compile(self, cc_file: str):
        """Compiles the given source file"""
        out_file = (self.out_dir / cc_file).with_suffix('')
        self.run_command(['clang', '-std=c++11', '-Werror', '-Wall', self.tests_dir / cc_file, '-o', out_file])

    def run_main_compile_and_run_executable(self, puml_file: str) -> str:
        """Runs the plantuml2cpp main script, compiles the generated code, runs the created
        executable and returns the output captured from stdout"""
        self.run_main(self.tests_dir / puml_file, self.out_dir)
        self.compile(pathlib.Path(puml_file).with_suffix('.cc'))
        return self.run_compiled_executable(pathlib.Path(puml_file).with_suffix(''))

    def test_simple_fsm(self):
        """Verifies that working code can be generated for a simple FSM"""
        output = self.run_main_compile_and_run_executable('simple_fsm.puml')
        self.assertEqual(output, textwrap.dedent('''
            Entered Idle
            --- Posting JobReceived...
            Left Idle
            Job received
            Entered Working
            --- Posting JobDone...
            Left Working
            Job done
            Entered Idle
        ''').lstrip())

        with open(self.out_dir / 'simple_fsm.h') as f:
            content = f.read()

        self.assertIn('This is', content)
        self.assertIn('the multiline', content)
        self.assertIn('copyright header', content)

    def test_internal_transitions(self):
        """Verifies that internal transitions do not lead to a change of state"""
        output = self.run_main_compile_and_run_executable('internal_transitions_fsm.puml')
        self.assertEqual(output, textwrap.dedent('''
            Entered Working
            Entered Drilling
            --- Posting GotHungry...
            Trans GotHungry
            --- Posting HitSomething...
            Trans HitSomething
        ''').lstrip())

    def test_self_transition(self):
        """Verifies that transitions back to the same state trigger the state exit and entry events"""
        output = self.run_main_compile_and_run_executable('self_transition_fsm.puml')
        self.assertEqual(output, textwrap.dedent('''
            Entered Idle
            --- Posting Timeout...
            Left Idle
            Trans Timeout
            Entered Idle
        ''').lstrip())

    def test_deep_hierarchy(self):
        """Verifies that entry/exit actions and transitions are executed properly for an FSM with nested states"""
        output = self.run_main_compile_and_run_executable('deep_hierarchy_fsm.puml')
        self.assertEqual(output, textwrap.dedent('''
            Entered Passive
            Entered Sleeping
            Entered DeepSleep
            --- Posting New4kMonitorArrived...
            Left DeepSleep
            Left Sleeping
            Left Passive
            Trans New4kMonitorArrived
            Entered Active
            Entered Watching
            Entered InColor
            Entered HighDefinition
            --- Posting HeardSomeNoise...
            Left HighDefinition
            Left InColor
            Left Watching
            Trans HeardSomeNoise
            Entered Listening
            --- Posting SawSomething...
            Left Listening
            Trans SawSomething
            Entered Watching
            Entered BlackAndWhite
            --- Posting Glitch...
            Left BlackAndWhite
            Trans Glitch
            Entered BlackAndWhite
            --- Posting Timeout...
            Left BlackAndWhite
            Left Watching
            Left Active
            Trans Timeout
            Entered Passive
            Entered Sleeping
            Entered DeepSleep
            --- Posting HeardSomething...
            Left DeepSleep
            Trans HeardSomething
            Entered Napping
        ''').lstrip())


if __name__ == '__main__':
    unittest.main()
