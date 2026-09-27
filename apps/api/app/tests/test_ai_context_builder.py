from app.services.ai.context_builder import AIContextBuilder


def test_ai_context_builder_selects_relevant_context():
    builder = AIContextBuilder()

    intelligence = {
        "context": {
            "tasks": {
                "total": 10,
                "pending": 7,
                "due_today": 2,
            },
            "goals": {
                "total": 3,
                "active": 3,
                "average_progress": 42.5,
            },
            "habits": {
                "total": 4,
                "active": 4,
            },
            "projects": {
                "total": 2,
                "active": 2,
            },
            "recent_activity": {
                "count": 10,
                "events": ["internal-event-data"],
            },
            "analytics": {
                "internal": "analytics-data",
            },
            "analysis": {
                "signals": [
                    {
                        "type": "task_pressure",
                        "severity": "high",
                    }
                ],
            },
        },
        "prioritized_signals": [
            {
                "type": "task_pressure",
                "priority_score": 3.0,
            }
        ],
        "recommendations": [
            {
                "title": "Reduce your pending task load",
            }
        ],
    }

    result = builder.build(intelligence)

    assert result["current_state"]["tasks"]["pending"] == 7
    assert result["current_state"]["tasks"]["due_today"] == 2

    assert result["current_state"]["goals"]["active"] == 3
    assert result["current_state"]["habits"]["active"] == 4
    assert result["current_state"]["projects"]["active"] == 2

    assert len(result["signals"]) == 1
    assert result["signals"][0]["type"] == "task_pressure"

    assert result["prioritized_signals"][0]["priority_score"] == 3.0

    assert (
        result["recommendations"][0]["title"]
        == "Reduce your pending task load"
    )

    # Raw activity and analytics should not be passed to the AI.
    assert "recent_activity" not in result["current_state"]
    assert "analytics" not in result["current_state"]