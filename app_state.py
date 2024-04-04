"""Store persistent states in JSON format"""
from typing import Set, Any
import json
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

@dataclass
class State:
    """A local state as one part of the app state"""
    name: str
    state: dict[str, Any]

    def __hash__(self):
        return hash(self.name)

# pylint: disable=too-few-public-methods)
class Stateful(metaclass=ABCMeta):
    """Base class for classes that contribute to app state"""
    @property
    @abstractmethod
    def state(self) -> State:
        """Return the state of instance"""

class AppState:
    """Manages loading and storing of the app state

    Polls Stateful instances for updates on states

    This class most likely is used as a singleton
    """
    _file: str
    _state_dict: dict[str, Any]
    _clients: Set[Stateful]

    def __init__(self, file: str):
        self._file = file
        self._state_dict = {}
        self.clients = set()
        self.load_state()

    def register_client(self, stateful: Stateful):
        """Register a state client with this instance"""
        self.clients.add(stateful)

    def _fetch_clients(self):
        """Fetch states from all clients and update state dict"""
        states = [c.state for c in self.clients]
        # Ensure states are unique
        assert len(states) == len(set(states))
        for state in states:
            self.set_state(state)

    def set_state(self, state: State) -> None:
        """Set/Update a client state given by name"""
        self._state_dict[state.name] = state.state

    def get_state(self, name: str) -> State:
        """Return a client state given by name"""
        state = self._state_dict.get(name)
        if state is not None:
            return State(name, state)
        return None

    def load_state(self):
        """Load states from file"""
        try:
            # The file is read, but also expected to be writeable
            with open(self._file, "r+", encoding="utf-8") as state_file:
                self._state_dict = json.load(state_file)
        except FileNotFoundError:
            # Ensure file can be created...
            self.store_state()

    def store_state(self):
        """Store state to file"""
        self._fetch_clients()
        try:
            with open(self._file, "w", encoding="utf-8") as state_file:
                json_str = json.dumps(self._state_dict, indent=4)
                state_file.write(json_str)
        except (PermissionError, FileNotFoundError) as err:
            print(f"Error storing states at {self._file}: {err}")
