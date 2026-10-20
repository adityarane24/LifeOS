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

def test_context_analysis_detects_medium_task_pressure():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 5,
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
    assert signal["severity"] == "medium"
    assert signal["evidence"]["pending_tasks"] == 5
    assert signal["confidence"] == 1.0


def test_context_analysis_ignores_low_task_pressure():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 4,
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

    assert result["signal_count"] == 0
    assert result["signals"] == []

def test_context_analysis_detects_low_goal_progress():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 0,
        },
        "goals": {
            "active": 2,
            "average_progress": 20,
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

    assert signal["type"] == "low_goal_progress"
    assert signal["severity"] == "medium"
    assert signal["evidence"]["active_goals"] == 2
    assert signal["evidence"]["average_progress"] == 20
    assert signal["confidence"] == 1.0


def test_context_analysis_ignores_goal_progress_at_30_percent():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 0,
        },
        "goals": {
            "active": 2,
            "average_progress": 30,
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

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_ignores_goal_progress_without_active_goals():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 0,
        },
        "goals": {
            "active": 0,
            "average_progress": 10,
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

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_detects_low_habit_consistency():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 0,
        },
        "goals": {
            "active": 0,
            "average_progress": 0,
        },
        "habits": {
            "active": 2,
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
                "consistency_rate": 40,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 1

    signal = result["signals"][0]

    assert signal["type"] == "habit_consistency"
    assert signal["severity"] == "medium"
    assert signal["evidence"]["active_habits"] == 2
    assert signal["evidence"]["consistency_rate"] == 40
    assert signal["confidence"] == 1.0

def test_context_analysis_ignores_habit_consistency_at_50_percent():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 0,
        },
        "goals": {
            "active": 0,
            "average_progress": 0,
        },
        "habits": {
            "active": 2,
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
                "consistency_rate": 50,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_ignores_habit_consistency_without_active_habits():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
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
                "consistency_rate": 20,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_detects_low_task_completion():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
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
                "created": 10,
                "completion_rate": 40,
            },
            "habits": {
                "consistency_rate": 0,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 1

    signal = result["signals"][0]

    assert signal["type"] == "task_completion"
    assert signal["severity"] == "medium"
    assert signal["evidence"]["created_tasks"] == 10
    assert signal["evidence"]["completion_rate"] == 40
    assert signal["confidence"] == 1.0


def test_context_analysis_ignores_task_completion_at_50_percent():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
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
                "created": 10,
                "completion_rate": 50,
            },
            "habits": {
                "consistency_rate": 0,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_ignores_task_completion_without_created_tasks():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
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
                "completion_rate": 20,
            },
            "habits": {
                "consistency_rate": 0,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_context_analysis_detects_tasks_due_today():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
            "due_today": 3,
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

    assert signal["type"] == "due_today"
    assert signal["severity"] == "medium"
    assert signal["evidence"]["tasks_due_today"] == 3
    assert signal["confidence"] == 1.0


def test_context_analysis_ignores_when_no_tasks_due_today():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 0,
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

    assert result["signal_count"] == 0
    assert result["signals"] == []
