from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.signal_state import SignalState


class SignalStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_signal(
        self,
        user_id: UUID,
        signal_type: str,
    ) -> SignalState | None:
        return (
            self.db.query(SignalState)
            .filter(
                SignalState.user_id == user_id,
                SignalState.signal_type == signal_type,
            )
            .first()
        )

    def activate_signal(
        self,
        user_id: UUID,
        signal_type: str,
    ) -> SignalState:
        signal_state = self.get_by_signal(user_id, signal_type)

        if signal_state is None:
            signal_state = SignalState(
                user_id=user_id,
                signal_type=signal_type,
                is_active=True,
            )
            self.db.add(signal_state)
        else:
            signal_state.is_active = True
            signal_state.last_detected_at = datetime.now(timezone.utc)

        return signal_state

    def deactivate_signal(
        self,
        user_id: UUID,
        signal_type: str,
    ) -> None:
        signal_state = self.get_by_signal(user_id, signal_type)

        if signal_state is not None:
            signal_state.is_active = False


    def get_active_by_user(
        self,
        user_id: UUID,
    ) -> list[SignalState]:
        return (
            self.db.query(SignalState)
            .filter(
                SignalState.user_id == user_id,
                SignalState.is_active.is_(True),
            )
            .all()
        )