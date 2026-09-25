from typing import Dict, Set
from packages.domain.enums import ApplicationState

class InvalidStateTransitionError(Exception):
    pass

VALID_TRANSITIONS: Dict[ApplicationState, Set[ApplicationState]] = {
    ApplicationState.DISCOVERED: {
        ApplicationState.SAVED,
        ApplicationState.SKIP,
    },
    ApplicationState.SAVED: {
        ApplicationState.ANALYZED,
        ApplicationState.SKIP,
    },
    ApplicationState.ANALYZED: {
        ApplicationState.PREPARING,
        ApplicationState.SKIP,
    },
    ApplicationState.PREPARING: {
        ApplicationState.AWAITING_REVIEW,
        ApplicationState.FAILED,
        ApplicationState.SKIP,
    },
    ApplicationState.AWAITING_REVIEW: {
        ApplicationState.APPROVED,
        ApplicationState.SKIP,
        ApplicationState.PREPARING,
    },
    ApplicationState.APPROVED: {
        ApplicationState.SUBMITTING,
        ApplicationState.AWAITING_REVIEW,
        ApplicationState.SKIP,
    },
    ApplicationState.SKIP: {
        ApplicationState.SAVED,
    },
    ApplicationState.SUBMITTING: {
        ApplicationState.SUBMITTED,
        ApplicationState.FAILED,
    },
    ApplicationState.FAILED: {
        ApplicationState.AWAITING_REVIEW,
        ApplicationState.SKIP,
    },
    ApplicationState.SUBMITTED: {
        ApplicationState.FOLLOW_UP,
        ApplicationState.ASSESSMENT,
        ApplicationState.INTERVIEW,
        ApplicationState.REJECTED,
        ApplicationState.OFFER,
        ApplicationState.WITHDRAWN,
        ApplicationState.CLOSED,
    },
    ApplicationState.FOLLOW_UP: {
        ApplicationState.ASSESSMENT,
        ApplicationState.INTERVIEW,
        ApplicationState.REJECTED,
        ApplicationState.OFFER,
        ApplicationState.WITHDRAWN,
        ApplicationState.CLOSED,
    },
    ApplicationState.ASSESSMENT: {
        ApplicationState.INTERVIEW,
        ApplicationState.REJECTED,
        ApplicationState.WITHDRAWN,
        ApplicationState.CLOSED,
    },
    ApplicationState.INTERVIEW: {
        ApplicationState.OFFER,
        ApplicationState.REJECTED,
        ApplicationState.WITHDRAWN,
        ApplicationState.CLOSED,
    },
    ApplicationState.REJECTED: set(),
    ApplicationState.OFFER: {
        ApplicationState.CLOSED,
    },
    ApplicationState.WITHDRAWN: set(),
    ApplicationState.CLOSED: set(),
}

def validate_transition(current: ApplicationState, target: ApplicationState) -> bool:
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Illegal state transition from {current.value} to {target.value}. "
            f"Allowed next states: {[s.value for s in allowed]}"
        )
    return True
