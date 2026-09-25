"""
Tests for Application State Machine Transition Rules
"""
import pytest
from packages.domain.enums import ApplicationState
from packages.domain.state_machine import validate_transition, InvalidStateTransitionError

def test_valid_forward_flow():
    assert validate_transition(
        ApplicationState.DISCOVERED,
        ApplicationState.SAVED
    ) is True
    
    assert validate_transition(
        ApplicationState.AWAITING_REVIEW,
        ApplicationState.APPROVED
    ) is True
    
    assert validate_transition(
        ApplicationState.APPROVED,
        ApplicationState.SUBMITTING
    ) is True
    
    assert validate_transition(
        ApplicationState.SUBMITTING,
        ApplicationState.SUBMITTED
    ) is True

def test_invalid_bypass_approval_fails():
    """State machine MUST prevent jumping from AWAITING_REVIEW straight to SUBMITTED without APPROVAL."""
    with pytest.raises(InvalidStateTransitionError) as exc:
        validate_transition(
            ApplicationState.AWAITING_REVIEW,
            ApplicationState.SUBMITTED
        )
    assert "Illegal state transition" in str(exc.value)
