import pytest
import stat
import json
from app_state import *
from mock import Mock, sentinel

class TestAppState():
    def test_no_file(self, tmp_path):
        p = tmp_path / "state.json"

        # No exception is expected
        s = AppState(str(p))

        assert s._file == str(p)
        assert s._state_dict == {}
        assert p.read_text() == "{}"

    def test_no_r_permission(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("{}")
        p.chmod(0)

        # Permission Error shall be handled.
        with pytest.raises(PermissionError):
            s = AppState(str(p))

    def test_no_w_permission(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("{}")
        p.chmod(stat.S_IREAD)

        # Permission Error (and others) shall be handled.
        with pytest.raises(PermissionError):
            s = AppState(str(p))

    def test_load_get(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text('{"TEST_OBJ": {"app_state": 42}}')
        s = AppState(str(p))
        assert s.get_state("TEST_OBJ") == State("TEST_OBJ", {"app_state": 42})

    def test_add_store(self, tmp_path):
        p = tmp_path / "state.json"
        s = AppState(str(p))
        app_state = {"state": 42}
        s.set_state(State("TEST_OBJ", app_state))
        s.store_state()
        assert p.read_text() == json.dumps({"TEST_OBJ": app_state}, indent=4)

    def test_change(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text('{"TEST_OBJ": {"app_state": 42}}')
        s = AppState(str(p))
        app_state = {"changed": 43}
        s.set_state(State("TEST_OBJ", app_state))
        s.store_state()
        assert p.read_text() == json.dumps({"TEST_OBJ": app_state}, indent=4)

    def test_fetch_client(self, tmp_path):
        p = tmp_path / "state.json"
        s = AppState(str(p))
        client = Mock()
        app_state = {"new": 44}
        client.state = State("Test", app_state)
        s.register_client(client)
        s.store_state()
        assert s._state_dict["Test"] == app_state

    def test_missing_dir(self, tmp_path):
        p = tmp_path / "missing" / "state.json"
        s = AppState(str(p))
        s.store_state()

    def test_missing_state(self, tmp_path):
        s = AppState(str(tmp_path / "state.json"))
        assert s.get_state("missing") == None
