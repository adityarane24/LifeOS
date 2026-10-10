from uuid import UUID

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        recommendation_type: str,
        title: str,
        message: str,
        reason: str | None = None,
        source_signal: str | None = None,
        priority: float = 0.0,
        status: str = "generated",
    ) -> Recommendation:
        recommendation = Recommendation(
            user_id=user_id,
            recommendation_type=recommendation_type,
            title=title,
            message=message,
            reason=reason,
            source_signal=source_signal,
            priority=priority,
            status=status,
        )

        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)

        return recommendation

    def get_by_id(
        self,
        recommendation_id: UUID,
    ) -> Recommendation | None:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.id == recommendation_id)
            .first()
        )

    def get_active_by_signal(
        self,
        user_id: UUID,
        source_signal: str,
    ) -> Recommendation | None:
        return (
            self.db.query(Recommendation)
            .filter(
                Recommendation.user_id == user_id,
                Recommendation.source_signal == source_signal,
                Recommendation.status == "generated",
            )
            .order_by(Recommendation.created_at.desc())
            .first()
        )

    def get_by_user(
        self,
        user_id: UUID,
    ) -> list[Recommendation]:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .all()
        )

    def update_status(
        self,
        recommendation_id: UUID,
        status: str,
    ) -> Recommendation | None:
        recommendation = self.get_by_id(recommendation_id)

        if recommendation is None:
            return None

        recommendation.status = status

        self.db.commit()
        self.db.refresh(recommendation)

        return recommendation

