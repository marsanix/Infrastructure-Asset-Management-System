"""
Unit tests: state_machine.py
Memastikan semua transisi ITSM (Incident, Change, Problem, Request) valid/invalid.
"""
import pytest
from app.utils.state_machine import (
    validate_transition,
    INCIDENT_TRANSITIONS,
    CHANGE_TRANSITIONS,
    PROBLEM_TRANSITIONS,
    REQUEST_TRANSITIONS,
)


class TestValidateTransition:
    """Test fungsi validate_transition itu sendiri."""

    def test_same_status_always_valid(self):
        """Tidak berubah = selalu valid."""
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, "Open", "Open")
        assert ok is True
        assert msg == ""

    def test_valid_transition_returns_true(self):
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, "Open", "In Progress")
        assert ok is True
        assert msg == ""

    def test_invalid_transition_returns_false_with_message(self):
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, "Open", "Closed")
        assert ok is False
        assert "Invalid status transition" in msg
        assert "Open" in msg
        assert "Closed" in msg

    def test_terminal_state_no_transitions(self):
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, "Closed", "Open")
        assert ok is False
        assert "terminal state" in msg

    def test_unknown_current_status_returns_false(self):
        """Status yang tidak dikenal → tidak ada allowed transitions → invalid."""
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, "NonExistent", "Open")
        assert ok is False


class TestIncidentTransitions:
    """Semua jalur validasi Incident."""

    @pytest.mark.parametrize("from_s, to_s", [
        ("Open",        "In Progress"),
        ("Open",        "Cancelled"),
        ("In Progress", "Resolved"),
        ("In Progress", "Cancelled"),
        ("Resolved",    "Closed"),
        ("Resolved",    "Open"),   # re-open
    ])
    def test_valid_paths(self, from_s, to_s):
        ok, _ = validate_transition(INCIDENT_TRANSITIONS, from_s, to_s)
        assert ok is True, f"Expected {from_s} → {to_s} to be VALID"

    @pytest.mark.parametrize("from_s, to_s", [
        ("Open",     "Closed"),      # skip step
        ("Open",     "Resolved"),    # skip step
        ("Closed",   "Open"),        # terminal
        ("Cancelled","Open"),        # terminal
        ("Resolved", "In Progress"), # tidak boleh mundur ke In Progress
    ])
    def test_invalid_paths(self, from_s, to_s):
        ok, _ = validate_transition(INCIDENT_TRANSITIONS, from_s, to_s)
        assert ok is False, f"Expected {from_s} → {to_s} to be INVALID"


class TestChangeTransitions:
    """Semua jalur validasi Change."""

    @pytest.mark.parametrize("from_s, to_s", [
        ("Draft",       "Submitted"),
        ("Draft",       "Cancelled"),
        ("Submitted",   "Approved"),
        ("Submitted",   "Rejected"),
        ("Submitted",   "Cancelled"),
        ("Approved",    "In Progress"),
        ("Rejected",    "Draft"),      # revisi
        ("In Progress", "Completed"),
        ("In Progress", "Cancelled"),
    ])
    def test_valid_paths(self, from_s, to_s):
        ok, _ = validate_transition(CHANGE_TRANSITIONS, from_s, to_s)
        assert ok is True

    @pytest.mark.parametrize("from_s, to_s", [
        ("Draft",     "Approved"),    # skip Submitted
        ("Draft",     "Completed"),   # skip steps
        ("Completed", "Draft"),       # terminal
        ("Cancelled", "Draft"),       # terminal
    ])
    def test_invalid_paths(self, from_s, to_s):
        ok, _ = validate_transition(CHANGE_TRANSITIONS, from_s, to_s)
        assert ok is False


class TestProblemTransitions:
    @pytest.mark.parametrize("from_s, to_s", [
        ("Open",                "Under Investigation"),
        ("Open",                "Closed"),
        ("Under Investigation", "Known Error"),
        ("Under Investigation", "Resolved"),
        ("Known Error",         "Resolved"),
        ("Resolved",            "Closed"),
        ("Resolved",            "Open"),  # re-open
    ])
    def test_valid_paths(self, from_s, to_s):
        ok, _ = validate_transition(PROBLEM_TRANSITIONS, from_s, to_s)
        assert ok is True

    @pytest.mark.parametrize("from_s, to_s", [
        ("Open",   "Resolved"),   # skip Under Investigation
        ("Closed", "Open"),       # terminal
    ])
    def test_invalid_paths(self, from_s, to_s):
        ok, _ = validate_transition(PROBLEM_TRANSITIONS, from_s, to_s)
        assert ok is False


class TestRequestTransitions:
    @pytest.mark.parametrize("from_s, to_s", [
        ("Draft",       "Submitted"),
        ("Submitted",   "Approved"),
        ("Submitted",   "Rejected"),
        ("Approved",    "In Progress"),
        ("Rejected",    "Draft"),
        ("In Progress", "Completed"),
    ])
    def test_valid_paths(self, from_s, to_s):
        ok, _ = validate_transition(REQUEST_TRANSITIONS, from_s, to_s)
        assert ok is True

    @pytest.mark.parametrize("from_s, to_s", [
        ("Completed", "Draft"),    # terminal
        ("Cancelled", "Submitted"),# terminal
        ("Draft",     "Completed"),# skip steps
    ])
    def test_invalid_paths(self, from_s, to_s):
        ok, _ = validate_transition(REQUEST_TRANSITIONS, from_s, to_s)
        assert ok is False
