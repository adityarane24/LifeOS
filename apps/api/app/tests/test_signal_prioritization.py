from app.services.signal_prioritization import SignalPrioritizationService


def test_prioritize_signals_by_score():
    service = SignalPrioritizationService()

    signals = [
        {
            "type": "due_today",
            "severity": "medium",
            "message": "You have tasks due today.",
            "source": "tasks",
            "evidence": {
                "tasks_due_today": 2,
            },
            "confidence": 1.0,
        },
        {
            "type": "task_pressure",
            "severity": "high",
            "message": "You have a high number of pending tasks.",
            "source": "tasks",
            "evidence": {
                "pending_tasks": 10,
            },
            "confidence": 1.0,
        },
    ]

    result = service.prioritize(signals)

    assert len(result) == 2

    assert result[0]["type"] == "task_pressure"
    assert result[0]["priority_score"] == 3.0

    assert result[1]["type"] == "due_today"
    assert result[1]["priority_score"] == 2.4


def test_prioritize_empty_signals():
    service = SignalPrioritizationService()

    result = service.prioritize([])

    assert result == []