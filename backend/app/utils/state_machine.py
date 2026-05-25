"""
State machine validator untuk ITSM workflows.
Mencegah Business Logic Abuse — transisi status yang tidak valid
(OWASP Top 10 for Business Logic Abuse 2025).

Prinsip: server selalu validasi transisi, tidak percaya client.
"""
from typing import Dict, Set

# ── Incident state transitions ────────────────────────────────
INCIDENT_TRANSITIONS: Dict[str, Set[str]] = {
    'Open':        {'In Progress', 'Cancelled'},
    'In Progress': {'Resolved', 'Cancelled'},
    'Resolved':    {'Closed', 'Open'},       # bisa re-open
    'Closed':      set(),                    # terminal state
    'Cancelled':   set(),                    # terminal state
}

# ── Change state transitions ──────────────────────────────────
CHANGE_TRANSITIONS: Dict[str, Set[str]] = {
    'Draft':       {'Submitted', 'Cancelled'},
    'Submitted':   {'Approved', 'Rejected', 'Cancelled'},
    'Approved':    {'In Progress', 'Cancelled'},
    'Rejected':    {'Draft'},                # bisa revisi
    'In Progress': {'Completed', 'Cancelled'},
    'Completed':   set(),                    # terminal
    'Cancelled':   set(),                    # terminal
}

# ── Problem state transitions ─────────────────────────────────
PROBLEM_TRANSITIONS: Dict[str, Set[str]] = {
    'Open':                  {'Under Investigation', 'Closed'},
    'Under Investigation':   {'Known Error', 'Resolved', 'Closed'},
    'Known Error':           {'Resolved', 'Closed'},
    'Resolved':              {'Closed', 'Open'},   # bisa re-open
    'Closed':                set(),
}

# ── Request state transitions ─────────────────────────────────
REQUEST_TRANSITIONS: Dict[str, Set[str]] = {
    'Draft':       {'Submitted', 'Cancelled'},
    'Submitted':   {'Approved', 'Rejected', 'Cancelled'},
    'Approved':    {'In Progress', 'Cancelled'},
    'Rejected':    {'Draft'},
    'In Progress': {'Completed', 'Cancelled'},
    'Completed':   set(),
    'Cancelled':   set(),
}


def validate_transition(
    transitions: Dict[str, Set[str]],
    current_status: str,
    new_status: str,
) -> tuple[bool, str]:
    """
    Validasi apakah transisi status diizinkan.
    Returns: (is_valid, error_message)
    """
    if current_status == new_status:
        return True, ''

    allowed = transitions.get(current_status, set())
    if new_status not in allowed:
        return False, (
            f"Invalid status transition: '{current_status}' → '{new_status}'. "
            f"Allowed: {sorted(allowed) or 'none (terminal state)'}"
        )
    return True, ''
