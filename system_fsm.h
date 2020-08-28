/**
 * Copyright (c) 2020, Johannes Bergmann
 *
 * All rights reserved.
 */

// ============================================================================
// AUTO-GENERATED FILE. DO NOT MODIFY!
// ============================================================================

#pragma once

class SystemFsmDummyBase {};

template <typename T = SystemFsmDummyBase> // Define actions and guards in T
class SystemFsm : public T {
public:
  enum class State : unsigned char {
    Charge,
    Charge_Charging,
    Charge_Done,
    Discharge,
    Discharge_PowerOn,
    Discharge_PowerOnWarn,
    Discharge_PreCharge,
    FactoryMode,
    OnForSoc,
    OnForSoc_PowerUpForSoc,
    OnForSoc_ShowingSoc,
    PoweringDown,
    PoweringUp,
    Standby,
    Standby_Idle,
    Standby_PoweringUpForFlash,
    Standby_PoweringUpForSoc,
    Standby_ShowingFlash,
    Standby_ShowingSoc,
    SystemError,
    SystemOff,
    SystemOn,
    NO_STATE_,
  };

  enum class Event : unsigned char {
    AuxPwrSwitchedOff,
    AuxPwrSwitchedOn,
    BackUnderSoftLimits,
    BuzzerPatternFinished,
    ChargingDone,
    CriticalErrorDetected,
    CriticallyLowSocDetected,
    EnterFactoryModeBleRequest,
    ExtraLongPress,
    InactivityDetected,
    LongPress,
    PreChargeDone,
    ShortPress,
    SoftLimitsExceeded,
    StandbyFlashTimerExpired,
    StatusLedPatternFinished,
  };

  enum {
    kNumStates = 22,
    kNumEvents = 16,
    kNumTransitions = 28,
  };

  void init();
  void post_event(Event event);
  State current_state() const;
  static const char *to_string(State state);
  static const char *to_string(Event event);

private:
  struct Transition {
    Event event;
    State from_state;
    State to_state;
  };

  State state_;

  static State get_parent_state(State state);
  static const Transition *transitions();
  void call_state_entry_actions(State state);
  void call_state_exit_actions(State state);
  void call_entry_actions_recursively(State cur_state, State new_state);
  void call_exit_actions_recursively(State cur_state, State new_state);
  void call_transition_actions(int transition_idx);
  const Transition *find_transition_from_cur_state(Event event) const;
  bool check_transition_guard(int transition_idx) const;
}; // class SystemFsm

template <typename T> void SystemFsm<T>::init() {
  call_entry_actions_recursively(State::NO_STATE_, State::SystemOff);
  state_ = State::SystemOff;
}

template <typename T> void SystemFsm<T>::post_event(Event event) {
  // Get transition from the current state
  const Transition *transition = find_transition_from_cur_state(event);
  if (transition == nullptr) {
    return;
  }

  // Find the closest common ancestor between source and target state
  State common_ancestor =
      get_common_ancestor(transition->from_state, transition->to_state);

  // Call state exit, transition and state entry actions
  call_exit_actions_recursively(state_, common_ancestor);
  call_transition_actions(*transition);
  call_entry_actions_recursively(common_ancestor, transition->to_state);

  // Update the state
  state_ = transition->to_state;
}

template <typename T> SystemFsm<T>::State SystemFsm<T>::current_state() const {
  return state_;
}

template <typename T> const char *SystemFsm<T>::to_string(State state) {
  static const char *lut[] = {
      "Charge",
      "Charge_Charging",
      "Charge_Done",
      "Discharge",
      "Discharge_PowerOn",
      "Discharge_PowerOnWarn",
      "Discharge_PreCharge",
      "FactoryMode",
      "OnForSoc",
      "OnForSoc_PowerUpForSoc",
      "OnForSoc_ShowingSoc",
      "PoweringDown",
      "PoweringUp",
      "Standby",
      "Standby_Idle",
      "Standby_PoweringUpForFlash",
      "Standby_PoweringUpForSoc",
      "Standby_ShowingFlash",
      "Standby_ShowingSoc",
      "SystemError",
      "SystemOff",
      "SystemOn",
  };

  int idx = static_cast<int>(state);
  const char *s = idx < sizeof(lut) / sizeof(lut[0]) ? lut[idx] : "INVALID";
  return s;
}

template <typename T> const char *SystemFsm<T>::to_string(Event event) {
  static const char *lut[] = {
      "AuxPwrSwitchedOff",
      "AuxPwrSwitchedOn",
      "BackUnderSoftLimits",
      "BuzzerPatternFinished",
      "ChargingDone",
      "CriticalErrorDetected",
      "CriticallyLowSocDetected",
      "EnterFactoryModeBleRequest",
      "ExtraLongPress",
      "InactivityDetected",
      "LongPress",
      "PreChargeDone",
      "ShortPress",
      "SoftLimitsExceeded",
      "StandbyFlashTimerExpired",
      "StatusLedPatternFinished",
  };

  int idx = static_cast<int>(event);
  const char *s = idx < sizeof(lut) / sizeof(lut[0]) ? lut[idx] : "INVALID";
  return s;
}

template <typename T>
SystemFsm<T>::State SystemFsm<T>::get_parent_state(State state) {
  static const State lut[] = {
      State::SystemOn,  // Parent of Charge
      State::Charge,    // Parent of Charge_Charging
      State::Charge,    // Parent of Charge_Done
      State::SystemOn,  // Parent of Discharge
      State::Discharge, // Parent of Discharge_PowerOn
      State::Discharge, // Parent of Discharge_PowerOnWarn
      State::Discharge, // Parent of Discharge_PreCharge
      State::NO_STATE_, // Parent of FactoryMode
      State::NO_STATE_, // Parent of OnForSoc
      State::OnForSoc,  // Parent of OnForSoc_PowerUpForSoc
      State::OnForSoc,  // Parent of OnForSoc_ShowingSoc
      State::NO_STATE_, // Parent of PoweringDown
      State::SystemOn,  // Parent of PoweringUp
      State::SystemOn,  // Parent of Standby
      State::Standby,   // Parent of Standby_Idle
      State::Standby,   // Parent of Standby_PoweringUpForFlash
      State::Standby,   // Parent of Standby_PoweringUpForSoc
      State::Standby,   // Parent of Standby_ShowingFlash
      State::Standby,   // Parent of Standby_ShowingSoc
      State::NO_STATE_, // Parent of SystemError
      State::NO_STATE_, // Parent of SystemOff
      State::NO_STATE_, // Parent of SystemOn
  };

  return lut[static_cast<int>(state)];
}

template <typename T>
const SystemFsm<T>::Transition *SystemFsm<T>::transitions() {
  static const Transition transitions[] = {
      /* clang-format off */ {Event::AuxPwrSwitchedOff,          State::PoweringDown,               State::SystemOff                 } /* clang-format on */,
      /* clang-format off */ {Event::AuxPwrSwitchedOn,           State::OnForSoc_PowerUpForSoc,     State::OnForSoc_ShowingSoc       } /* clang-format on */,
      /* clang-format off */ {Event::AuxPwrSwitchedOn,           State::PoweringUp,                 State::Discharge                 } /* clang-format on */,
      /* clang-format off */ {Event::AuxPwrSwitchedOn,           State::PoweringUp,                 State::Charge                    } /* clang-format on */,
      /* clang-format off */ {Event::AuxPwrSwitchedOn,           State::Standby_PoweringUpForFlash, State::Standby_ShowingFlash      } /* clang-format on */,
      /* clang-format off */ {Event::AuxPwrSwitchedOn,           State::Standby_PoweringUpForSoc,   State::Standby_ShowingSoc        } /* clang-format on */,
      /* clang-format off */ {Event::BackUnderSoftLimits,        State::Discharge_PowerOnWarn,      State::Discharge_PowerOn         } /* clang-format on */,
      /* clang-format off */ {Event::BuzzerPatternFinished,      State::Discharge_PowerOnWarn,      State::Discharge_PowerOnWarn     } /* clang-format on */,
      /* clang-format off */ {Event::ChargingDone,               State::Charge_Charging,            State::Charge_Done               } /* clang-format on */,
      /* clang-format off */ {Event::CriticalErrorDetected,      State::OnForSoc,                   State::SystemError               } /* clang-format on */,
      /* clang-format off */ {Event::CriticalErrorDetected,      State::SystemOn,                   State::SystemError               } /* clang-format on */,
      /* clang-format off */ {Event::CriticallyLowSocDetected,   State::Standby,                    State::PoweringDown              } /* clang-format on */,
      /* clang-format off */ {Event::EnterFactoryModeBleRequest, State::SystemOn,                   State::FactoryMode               } /* clang-format on */,
      /* clang-format off */ {Event::ExtraLongPress,             State::SystemOff,                  State::SystemOff                 } /* clang-format on */,
      /* clang-format off */ {Event::InactivityDetected,         State::Discharge,                  State::Standby                   } /* clang-format on */,
      /* clang-format off */ {Event::LongPress,                  State::Standby,                    State::PoweringUp                } /* clang-format on */,
      /* clang-format off */ {Event::LongPress,                  State::SystemError,                State::PoweringDown              } /* clang-format on */,
      /* clang-format off */ {Event::LongPress,                  State::SystemOff,                  State::SystemOn                  } /* clang-format on */,
      /* clang-format off */ {Event::LongPress,                  State::SystemOn,                   State::PoweringDown              } /* clang-format on */,
      /* clang-format off */ {Event::PreChargeDone,              State::Discharge_PreCharge,        State::Discharge_PowerOn         } /* clang-format on */,
      /* clang-format off */ {Event::ShortPress,                 State::OnForSoc_ShowingSoc,        State::OnForSoc_ShowingSoc       } /* clang-format on */,
      /* clang-format off */ {Event::ShortPress,                 State::Standby_Idle,               State::Standby_PoweringUpForSoc  } /* clang-format on */,
      /* clang-format off */ {Event::ShortPress,                 State::SystemOff,                  State::OnForSoc                  } /* clang-format on */,
      /* clang-format off */ {Event::SoftLimitsExceeded,         State::Discharge_PowerOn,          State::Discharge_PowerOnWarn     } /* clang-format on */,
      /* clang-format off */ {Event::StandbyFlashTimerExpired,   State::Standby_Idle,               State::Standby_PoweringUpForFlash} /* clang-format on */,
      /* clang-format off */ {Event::StatusLedPatternFinished,   State::OnForSoc_ShowingSoc,        State::PoweringDown              } /* clang-format on */,
      /* clang-format off */ {Event::StatusLedPatternFinished,   State::Standby_ShowingFlash,       State::Standby_Idle              } /* clang-format on */,
      /* clang-format off */ {Event::StatusLedPatternFinished,   State::Standby_ShowingSoc,         State::Standby_Idle              } /* clang-format on */,
  };

  return transitions;
}

template <typename T> void SystemFsm<T>::call_state_entry_actions(State state) {
  switch (state) {
  case State::Charge_Charging: {
    show_charging_progress();
  } break;

  case State::Charge_Done: {
    ::global::show_status_led_pattern_fn(StatusLed::kFadeInThenOn);
  } break;

  case State::Discharge_PowerOn: {
    ::global::show_status_led_pattern_fn(StatusLed::kOn);
  } break;

  case State::Discharge_PowerOnWarn: {
    long_beep();
    ::global::show_status_led_pattern_fn(StatusLed::kFlashFast);
  } break;

  case State::Discharge_PreCharge: {
    ::global::show_status_led_pattern_fn(StatusLed::kFadeIn);
  } break;

  case State::FactoryMode: {
    ::global::show_status_led_pattern_fn(StatusLed::kFadeOut);
  } break;

  case State::OnForSoc_PowerUpForSoc: {
    set_aux_power_enabled(true);
  } break;

  case State::OnForSoc_ShowingSoc: {
    short_beep();
    show_soc();
  } break;

  case State::PoweringDown: {
    set_aux_power_enabled(false);
    ::global::show_status_led_pattern_fn(StatusLed::kOff);
  } break;

  case State::PoweringUp: {
    set_aux_power_enabled(true);
  } break;

  case State::Standby: {
    set_aux_power_enabled(false);
  } break;

  case State::Standby_Idle: {
    set_aux_power_enabled(false);
    ::global::show_status_led_pattern_fn(StatusLed::kOff);
  } break;

  case State::Standby_PoweringUpForFlash: {
    set_aux_power_enabled(true);
  } break;

  case State::Standby_PoweringUpForSoc: {
    set_aux_power_enabled(true);
  } break;

  case State::Standby_ShowingFlash: {
    ::global::show_status_led_pattern_fn(StatusLed::kFlashRarely);
  } break;

  case State::Standby_ShowingSoc: {
    show_soc();
  } break;

  case State::SystemError: {
    show_error_code();
  } break;
  } // switch (state)
} // run_state_entry_actions()

template <typename T> void SystemFsm<T>::call_state_exit_actions(State state) {
  switch (state) {
  case State::PoweringUp: {
    short_beep();
  } break;
  } // switch (state)
} // run_state_exit_actions()

template <typename T>
void SystemFsm<T>::call_entry_actions_recursively(State cur_state,
                                                  State new_state) {
  // Collect the (reverse) order in which we have to go through the states
  State sequence[3];
  int idx = 0;
  for (State st = new_state; st != cur_state; st = get_parent_state(state)) {
    sequence[idx] = st;
    ++idx;
  }

  // Call the entry actions in the determined order
  do {
    idx -= 1;
    call_entry_actions(sequence[idx]);
  } while (idx > 0);
}

template <typename T>
void SystemFsm<T>::call_exit_actions_recursively(State cur_state,
                                                 State new_state) {
  for (State st = cur_state; st != new_state; st = get_parent_state(state)) {
    call_exit_actions(st);
  }
}

template <typename T>
void SystemFsm<T>::call_transition_actions(int transition_idx) {
  switch (transition_idx) {
  case 0: { // PoweringDown --- AuxPwrSwitchedOff --> SystemOff
    activate_afe_ship_mode();
  } break;

  case 9: { // OnForSoc --- CriticalErrorDetected --> SystemError
    long_beep();
  } break;

  case 10: { // SystemOn --- CriticalErrorDetected --> SystemError
    long_beep();
  } break;

  case 12: { // SystemOn --- EnterFactoryModeBleRequest --> FactoryMode
    tripple_beep();
  } break;

  case 13: { // SystemOff --- ExtraLongPress --> SystemOff
    boot_into_bootloader();
  } break;

  case 14: { // Discharge --- InactivityDetected --> Standby
    long_beep();
  } break;

  case 16: { // SystemError --- LongPress --> PoweringDown
    long_beep();
  } break;

  case 18: { // SystemOn --- LongPress --> PoweringDown
    long_beep();
  } break;
  } // switch(transition_idx)
} // call_transition_actions()

template <typename T>
const SystemFsm<T>::Transition *
SystemFsm<T>::find_transition_from_cur_state(Event event) const {
  auto state = _state;
  while (state != State::NO_STATE_) {
    // Go through the whole transition table to find a matching transition
    for (int i = 0; i < kNumTransitions; ++i) {
      auto &transition = transitions()[i];

      // Ignore the transition if the "from" state or the event don't match
      if (transition.event != event || transition.from_state != state) {
        continue;
      }

      // If the guard condition is met, we have a winner!
      if (check_transition_guard(i)) {
        return &transition;
      }
    }

    // Try the parent state if there is no direct transition from this state
    state = get_parent_state(state);
  }

  // We didn't find any matching transition or the guard condition failed
  return nullptr;
}

template <typename T>
bool SystemFsm<T>::check_transition_guard(int transition_idx) const {
  switch (transition_idx) {
  /* clang-format off */ case   2: { return charger_connected() == false } /* clang-format on */;
  /* clang-format off */ case   3: { return charger_connected() == true  } /* clang-format on */;
  }

  return true;
}

// ============================================================================
// AUTO-GENERATED FILE. DO NOT MODIFY!
// ============================================================================
