from app.services.context_analysis import ContextAnalysisService


def test_context_analysis_detects_high_task_pressure():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 10,
            "due_today": 0,
        },
        "goals": {
            "active": 0,
            "average_progress": 0,
        },
        "habits": {
            "active": 0,
        },
        "projects": {
            "active": 0,
        },
        "analytics": {
            "tasks": {
                "created": 0,
                "completion_rate": 0,
            },
            "habits": {
                "consistency_rate": 0,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 1

    signal = result["signals"][0]

    assert signal["type"] == "task_pressure"
    assert signal["severity"] == "high"
    assert signal["message"] == "You have a high number of pending tasks."
    assert signal["source"] == "tasks"
    assert signal["evidence"]["pending_tasks"] == 10
    assert signal["confidence"] == 1.0