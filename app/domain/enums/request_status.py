from enum import Enum


class RequestStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @classmethod
    def get_valid_transitions(cls, status: 'RequestStatus') -> list['RequestStatus']:
        transitions = {
            cls.NEW: [cls.IN_PROGRESS],
            cls.IN_PROGRESS: [cls.COMPLETED],
            cls.COMPLETED: []
        }
        return transitions.get(status, [])

    def can_transition_to(self, new_status: 'RequestStatus') -> bool:
        return new_status in self.get_valid_transitions(self)