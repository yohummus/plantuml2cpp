"""
Module for generating C++ code from the parsed state diagram
"""

import textwrap

from .parser import PlantUmlStateDiagram, Transition


class CodeGenerator:
    """C++ code generator based on the parsed PlantUML state diagram"""

    def __init__(self, diagram: PlantUmlStateDiagram):
        """Constructs the code generator"""
        self.diagram = diagram

    def generate(self, namespace: str, class_name: str) -> None:
        """Generates the C++ code"""
        code = []
        nl = '\n'
        nlnl = '\n\n'

        namespace_begin = f'namespace {namespace} {{' if namespace else ''
        namespace_end = f'}}  // namespace {namespace}' if namespace else ''

        if self.diagram.copyright_header:
            code += ['/**']
            code += [f' * {x}' for x in self.diagram.copyright_header.split('\n')]
            code += [' */']

        code += textwrap.dedent(f'''
            // ============================================================================
            // AUTO-GENERATED FILE. DO NOT MODIFY!
            // ============================================================================

            # pragma once

            {namespace_begin}

            class {class_name}DummyBase {{}};

            template <typename T = {class_name}DummyBase>  // Define actions and guards in T
            class {class_name} : public T {{
              public:
                enum class State : unsigned char {{
                    {''.join(f'{x}, ' for x in self.diagram.state_names)}
                    NO_STATE_,
                }};

                enum class Event : unsigned char {{
                    {''.join(f'{x}, ' for x in self.diagram.event_names)}
                }};

                enum {{
                    kNumStates = {len(self.diagram.state_names)},
                    kNumEvents = {len(self.diagram.event_names)},
                    kNumTransitions = {len(self.diagram.transitions)},
                }};

                void init();
                void post_event(Event event);
                State current_state() const;
                static const char* to_string(State state);
                static const char* to_string(Event event);

              private:
                struct Transition {{
                    Event event;
                    State from_state;
                    State to_state;
                }};

                State state_;

                static State get_parent_state(State state);
                static const Transition* transitions();
                void call_state_entry_actions(State state);
                void call_state_exit_actions(State state);
                void call_entry_actions_recursively(State cur_state, State new_state);
                void call_exit_actions_recursively(State cur_state, State new_state);
                void call_transition_actions(int transition_idx);
                const Transition* find_transition_from_cur_state(Event event) const;
                bool check_transition_guard(int transition_idx) const;
            }};  // class {class_name}

            template <typename T>
            void {class_name}<T>::init() {{
                call_entry_actions_recursively(State::NO_STATE_, State::{self.diagram.initial_state.name});
                state_ = State::{self.diagram.initial_state.name};
            }}

            template <typename T>
            void {class_name}<T>::post_event(Event event) {{
                // Get transition from the current state
                const Transition* transition = find_transition_from_cur_state(event);
                if (transition == nullptr) {{
                    return;
                }}

                // Find the closest common ancestor between source and target state
                State common_ancestor = get_common_ancestor(transition->from_state, transition->to_state);

                // Call state exit, transition and state entry actions
                call_exit_actions_recursively(state_, common_ancestor);
                call_transition_actions(*transition);
                call_entry_actions_recursively(common_ancestor, transition->to_state);

                // Update the state
                state_ = transition->to_state;
            }}

            template <typename T>
            {class_name}<T>::State {class_name}<T>::current_state() const {{
                return state_;
            }}

            template <typename T>
            const char* {class_name}<T>::to_string(State state) {{
                static const char* lut[] = {{
                    {''.join(f'"{x}", ' for x in self.diagram.state_names)}
                }};
                
                int idx = static_cast<int>(state);
                const char* s = idx < sizeof(lut) / sizeof(lut[0]) ? lut[idx] : "INVALID";
                return s;
            }}

            template <typename T>
            const char* {class_name}<T>::to_string(Event event) {{
                static const char* lut[] = {{
                    {''.join(f'"{x}", ' for x in self.diagram.event_names)}
                }};
                
                int idx = static_cast<int>(event);
                const char* s = idx < sizeof(lut) / sizeof(lut[0]) ? lut[idx] : "INVALID";
                return s;
            }}

            template <typename T>
            {class_name}<T>::State {class_name}<T>::get_parent_state(State state) {{
                static const State lut[] = {{
                    {nl.join(f'{self._make_parent_state_enum_member(x)},  // Parent of {x}' for x in self.diagram.state_names)}
                }};
                
                return lut[static_cast<int>(state)];
            }}

            template <typename T>
            const {class_name}<T>::Transition* {class_name}<T>::transitions() {{
                static const Transition transitions[] = {{
                    {nl.join(self._make_transition_initializer(x) for x in self.diagram.transitions)}
                }};

                return transitions;
            }}

            template <typename T>
            void {class_name}<T>::call_state_entry_actions(State state) {{
                switch (state) {{
                    {nlnl.join(f'case State::{x}: {{ {self._make_state_entry_code(x)} }} break;'
                     for x in self.diagram.state_names if self.diagram.states[x].entry_transitions)}
                }}  // switch (state)
            }}  // run_state_entry_actions()

            template <typename T>
            void {class_name}<T>::call_state_exit_actions(State state) {{
                switch (state) {{
                    {nlnl.join(f'case State::{x}: {{ {self._make_state_exit_code(x)} }} break;'
                     for x in self.diagram.state_names if self.diagram.states[x].exit_transitions)}
                }}  // switch (state)
            }}  // run_state_exit_actions()

            template <typename T>
            void {class_name}<T>::call_entry_actions_recursively(State cur_state, State new_state) {{
                // Collect the (reverse) order in which we have to go through the states
                State sequence[{self._state_nesting_depth}];
                int idx = 0;
                for (State st = new_state; st != cur_state; st = get_parent_state(state)) {{
                    sequence[idx] = st;
                    ++idx;
                }}

                // Call the entry actions in the determined order
                do {{
                    idx -= 1;
                    call_entry_actions(sequence[idx]);
                }} while (idx > 0);
            }}

            template <typename T>
            void {class_name}<T>::call_exit_actions_recursively(State cur_state, State new_state) {{
                for (State st = cur_state; st != new_state; st = get_parent_state(state)) {{
                    call_exit_actions(st);
                }}
            }}

            template <typename T>
            void {class_name}<T>::call_transition_actions(int transition_idx) {{
                switch (transition_idx) {{
                    {nlnl.join(f'case {i}: {{  // {x}{nl}{self._make_transition_actions_code(i)} }}break;'
                     for i, x in enumerate(self.diagram.transitions) if x.actions)}
                }}  // switch(transition_idx)
            }}  // call_transition_actions()

            template <typename T>
            const {class_name}<T>::Transition* {class_name}<T>::find_transition_from_cur_state(Event event) const {{
                auto state = _state;
                while (state != State::NO_STATE_) {{
                    // Go through the whole transition table to find a matching transition
                    for (int i = 0; i < kNumTransitions; ++i) {{
                        auto& transition = transitions()[i];

                        // Ignore the transition if the "from" state or the event don't match
                        if (transition.event != event || transition.from_state != state) {{
                            continue;
                        }}
                        
                        // If the guard condition is met, we have a winner!
                        if (check_transition_guard(i)) {{
                            return &transition;
                        }}
                    }}

                    // Try the parent state if there is no direct transition from this state
                    state = get_parent_state(state);
                }}

                // We didn't find any matching transition or the guard condition failed
                return nullptr;
            }}

            template <typename T>
            bool {class_name}<T>::check_transition_guard(int transition_idx) const {{
                switch (transition_idx) {{
                    {nl.join(self._make_guard_code(i) for i, x in enumerate(self.diagram.transitions) if x.guard)}
                }}

                return true;
            }}

            {namespace_end}

            // ============================================================================
            // AUTO-GENERATED FILE. DO NOT MODIFY!
            // ============================================================================
        ''').split('\n')

        return '\n'.join(code)

    def _make_state_entry_code(self, state_name: str) -> str:
        """Generates the code that is called when entering the given state"""
        code = ''
        for trans in self.diagram.states[state_name].entry_transitions:
            for act in trans.actions:
                code += f'{act.code};'

        return code

    def _make_state_exit_code(self, state_name: str) -> str:
        """Generates the code that is called when exiting the given state"""
        code = ''
        for trans in self.diagram.states[state_name].exit_transitions:
            for act in trans.actions:
                code += f'{act.code};'

        return code

    def _make_parent_state_enum_member(self, state_name: str) -> str:
        """Returns the name of the State enum member of the given state's parent"""
        parent = self.diagram.states[state_name].parent_state
        name = parent.name if parent else 'NO_STATE_'
        return f'State::{name}'

    def _make_transition_initializer(self, transition: Transition) -> str:
        """Generates the code that initializes the Transition struct"""
        max_event_len = max(len(x.event.name) for x in self.diagram.transitions)
        event_code = f'Event::{transition.event.name + ",":{max_event_len + 1}}'

        max_from_state_len = max(len(x.from_state.name) for x in self.diagram.transitions)
        from_state_code = f'State::{transition.from_state.name + ",":{max_from_state_len + 1}}'

        max_to_state_len = max(len(x.to_state.name) for x in self.diagram.transitions)
        to_state_code = f'State::{transition.to_state.name:{max_to_state_len}}'

        code = f'/* clang-format off */ {{{event_code} {from_state_code} {to_state_code}}}  /* clang-format on */,'

        return code

    def _make_guard_code(self, transition_idx: int) -> str:
        """Generates the code that checks the guard condition for the given transition"""
        transitions = self.diagram.transitions
        trans = transitions[transition_idx]

        max_cond_len = max(len(x.guard.code if x.guard else 'true') for x in transitions)
        cond = trans.guard.code if trans.guard else 'true'
        case_code = f'case {transition_idx: 3}: {{ return {cond:{max_cond_len}} }}'

        return f'/* clang-format off */ {case_code} /* clang-format on */;'

    def _make_transition_actions_code(self, transition_idx: int) -> str:
        """Generates the code for the actions associated with the given transition"""
        trans = self.diagram.transitions[transition_idx]

        code = ''.join([f'{act.code};' for act in trans.actions])

        return code

    @property
    def _state_nesting_depth(self) -> int:
        """Returns the maximum hierarchical depth of the state machine"""
        depth = 0
        states = [x for x in self.diagram.states.values() if x.parent_state is None]
        while states:
            depth += 1
            states = [y for x in states for y in x.child_states]

        return depth
