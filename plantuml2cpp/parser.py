"""
Module for parsing PlantUML state diagram files
"""

import pathlib
import itertools
import re
from typing import NamedTuple, List, Optional, Tuple, Dict, Union


class Line(NamedTuple):
    """Represents a single line in a .puml file"""
    filename: pathlib.Path
    line_no: int
    orig_text: str
    text: str

    def __str__(self):
        return f'{self.filename}:{self.line_no}'


class Event(NamedTuple):
    """Represents an event in the FSM"""
    name: str


EventDict = Dict[str, Event]


class Guard(NamedTuple):
    """Represents a guard transition in the FSM"""
    code: str


class Action(NamedTuple):
    """Represents an action in the FSM"""
    code: str


class Transition(NamedTuple):
    """Represents a transition in the FSM"""
    event: str
    guard: Optional[Guard]
    from_state: 'State'
    to_state: 'State'        # Target state as written in the .puml file
    actions: List[Action]

    def __str__(self):
        guard_str = '' if not self.guard else f' [{self.guard.code}]'
        return f'{self.from_state.name} --- {self.event.name}{guard_str} --> {self.to_state.name}'

    def __repr__(self):
        return str(self)


class State(NamedTuple):
    """Represents a state in the FSM"""
    name: str
    parent_state: Optional['State']
    child_states: 'StateDict'
    is_initial_state: bool
    out_transitions: List[Transition]
    int_transitions: List[Transition]
    entry_transitions: List[Transition]
    exit_transitions: List[Transition]

    @property
    def initial_child_state(self) -> Union['State', None]:
        """Returns the child state that is the initial state when entering this state"""
        states = [x for x in self.child_states if x.is_initial_state]
        return states[0] if states else None

    @property
    def entry_target_state(self) -> 'State':
        """Returns the state in the hierarchy of this state that is the final target when entering this state"""
        if not self.initial_child_state:
            return self
        else:
            return self.initial_child_state.entry_target_state

    def __str__(self):
        parent = 'None' if not self.parent_state else self.parent_state.name
        transition_nums = ', '.join([f'{len(self.out_transitions)} out',
                                     f'{len(self.int_transitions)} int',
                                     f'{len(self.entry_transitions)} entry',
                                     f'{len(self.exit_transitions)} exit'])

        return f'State {self.name}: ' + ', '.join([
            f'parent={parent}',
            f'children={len(self.child_states)}',
            f'initial={self.is_initial_state}',
            f'transitions=({transition_nums})',
        ])

    def __repr__(self):
        return str(self)


StateDict = Dict[str, State]


class PlantUmlStateDiagram:
    """Parser for PlantUML state diagram files"""

    def __init__(self, filename: pathlib.Path):
        """Constructs the state diagram representation for the given .puml file"""
        self.states = self.parse_puml_file(filename)

    def parse_puml_file(self, filename: pathlib.Path) -> StateDict:
        """Parses the FSM definition in the given .puml file"""
        lines = self._read_puml_file(filename)

        self.copyright_header = self._parse_copyright_header(lines)
        lines = self._cleanup_lines(lines)

        initial_state_names, lines = self._parse_initial_state_transitions(lines)
        states, lines = self._parse_states(lines, initial_state_names)
        self._check_initial_states_exist(initial_state_names, states)
        self._check_states(states)

        lines = self._parse_transitions(states, lines)

        assert not lines, 'No idea how to parse the following lines:' + \
            ''.join([f'\n{x}: {x.orig_text}' for x in lines])

        return states

    @property
    def event_names(self) -> List[str]:
        """Returns a list containing all event names sorted alphabetically"""
        transitions = []
        for state in self.states.values():
            transitions += state.int_transitions
            transitions += state.out_transitions

        return sorted({trans.event.name for trans in transitions})

    @property
    def state_names(self) -> List[str]:
        """Returns a list containing all state names sorted alphabetically"""
        return sorted(self.states.keys())

    @property
    def transitions(self) -> List[Transition]:
        """Returns a list containing all transitions, sorted alphabetically by the event and the source state"""
        transitions = []
        for state in self.states.values():
            transitions += state.int_transitions
            transitions += state.out_transitions

        return sorted(transitions, key=lambda x: (x.event.name, x.from_state.name))

    @property
    def initial_state(self) -> State:
        """Returns the initial state"""
        state = [x for x in self.states.values() if x.is_initial_state and x.parent_state is None][0]
        while state.child_states:
            state = [x for x in state.child_states if x.is_initial_state][0]

        return state

    def _read_puml_file(self, filename: pathlib.Path) -> List[Line]:
        """Reads the .puml file into a list of lines"""
        with open(filename, 'r') as f:
            content = f.read()

        return [Line(filename, i + 1, x, x) for i, x in enumerate(content.split('\n'))]

    def _parse_copyright_header(self, lines: List[Line]) -> str:
        """Extracts the copyright header at the top of the file (comments starting with a single quote)"""
        copyright_lines = itertools.takewhile(lambda x: x.text.lstrip().startswith("'"), lines)
        copyright_header = '\n'.join([x.text.lstrip(" \t'") for x in copyright_lines])
        return copyright_header

    def _cleanup_lines(self, lines: List[Line]) -> List[Line]:
        """Removes empty lines and uninteresting things from non-empty lines"""
        clean_lines = []
        for filename, line_no, orig_text, text in lines:
            if any(text.startswith(x) for x in ['@', 'title ', 'hide empty ', 'note ']):
                text = ''
            else:
                text = re.sub(r'#\w+', '', text)
                text = text if "'" not in text else text[:text.index("'")]
                text = text.strip()

            if text:
                clean_lines.append(Line(filename, line_no, orig_text, text))

        return clean_lines

    def _parse_initial_state_transitions(self, lines: List[Line]) -> Tuple[Dict[str, Line], List[Line]]:
        """Extracts the initial states and returns only the remaining lines"""
        remaining_lines = []
        initial_state_names = {}

        for line in lines:
            m = re.fullmatch(r'^\[\*\]\s+-+>\s+(\w+)\s*(.*)', line.text)
            if not m:
                remaining_lines.append(line)
                continue

            name, trailing_text = m.groups()
            assert name not in initial_state_names, f'Duplicate initial transition for state {name} in {line}'
            assert not trailing_text, f'Additional text after initial transition in {line}: {line.orig_text}'
            initial_state_names[name] = line

        return initial_state_names, remaining_lines

    def _parse_states(self, lines: List[Line], inital_state_names: Dict[str, Line]) -> Tuple[StateDict, List[Line]]:
        """Extracts all states and returns only the remaining lines"""
        remaining_lines = []
        states = {}
        state_stack = [None]

        for line in lines:
            if line.text == '}':
                state_stack.pop()
                assert state_stack, f'Closing brace }} in {line} does not match any opening brace'
                continue

            m = re.fullmatch(r'^(state\s+)?(\w+)\s*(:\s*(.*?)\s*)?(\{?)$', line.text)
            if not m:
                remaining_lines.append(line)
                continue

            _, name, _, trans_txt, open_brace = m.groups()
            parent_state = state_stack[-1]
            state = states.setdefault(name, State(name, parent_state, [], name in inital_state_names, [], [], [], []))

            if parent_state and state not in parent_state.child_states:
                parent_state.child_states.append(state)

            if trans_txt:
                transition = self._parse_transition_line(line, trans_txt, state, state)
                if transition.event.name == 'entry':
                    state.entry_transitions.append(transition)
                elif transition.event.name == 'exit':
                    state.exit_transitions.append(transition)
                else:
                    state.int_transitions.append(transition)

            if open_brace:
                state_stack.append(state)

        return states, remaining_lines

    def _check_initial_states_exist(self, inital_state_names: Dict[str, Line], states: StateDict) -> None:
        """Checks that every state in the list of initial state names actually exists"""
        for name, line in inital_state_names.items():
            assert name in states, f'The target state "{name}" of the initial transition in {line} has not been defined'

    def _check_states(self, states: StateDict) -> None:
        """Checks for errors in the states such as missing initial states"""
        names = [x.name for x in states.values() if x.parent_state is None and x.is_initial_state]
        assert names, 'No initial top level state specified'
        assert len(names) == 1, f'Multiple initial top level states specified: {", ".join(names)}'

        for state in states.values():
            if not state.child_states:
                continue

            names = [x.name for x in state.child_states if x.is_initial_state]
            assert names, f'No initial state specified in composite state {state.name}'
            assert len(names) == 1, f'Multiple initial states specified in composite state {state.name}'

    def _parse_transitions(self, states: StateDict, lines: List[Line]) -> List[Line]:
        """Extracts all transitions and puts them into the state definitions"""
        remaining_lines = []

        for line in lines:
            m = re.fullmatch(r'^(\w+)\s+-+>\s(\w+)\s*(:\s*(.*?)\s*)?', line.text)
            if not m:
                remaining_lines.append(line)
                continue

            from_state, to_state, _, trans_txt = m.groups()
            assert trans_txt, f'Missing event in transition in {line}: {line.orig_text}'
            assert from_state in states, f'State "{from_state}" in {line} has not been defined'
            assert to_state in states, f'State "{to_state}" in {line} has not been defined'

            transition = self._parse_transition_line(line, trans_txt, states[from_state], states[to_state])
            states[from_state].out_transitions.append(transition)

        return remaining_lines

    def _parse_transition_line(self, line: Line, trans_txt: str, from_state: State, to_state: State) -> Transition:
        """Creates a transition from the text on a transition or inside a state"""

        # Replace \\ with \ and \n with a space
        trans_txt = '\\'.join([x.replace('\\n', ' ') for x in trans_txt.split('\\\\')])

        # Extract the individual parts from the line
        m = re.fullmatch(r'^(\w+)\s*(\[\s*(.*?)\s*\]\s*)?(/(.*))?', trans_txt)
        assert m, f'Invalid transition format in {line}: {line.orig_text}'
        event_name, _, guard_code, _, actions_txt = m.groups()
        actions_code = [] if not actions_txt else [x.strip() for x in actions_txt.split('/') if x.strip()]

        # Create the transition
        event = Event(event_name)
        guard = None if not guard_code else Guard(guard_code)
        actions = [Action(x) for x in actions_code]
        transition = Transition(event, guard, from_state, to_state, actions)

        return transition
