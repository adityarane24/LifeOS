import { useEffect, useState } from "react";
import {
  getActivityRange,
  getActivityTimeline,
} from "../api/activity";
import type {
  ActivityEntityType,
  ActivityEventResponse,
  ActivityEventType,
} from "../types/activity";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

type ActivityFilter = "all" | ActivityEntityType;

function formatEventType(eventType: ActivityEventType): string {
  return eventType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatEntityType(entityType: ActivityEntityType): string {
  return entityType.charAt(0).toUpperCase() + entityType.slice(1);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getEventIcon(eventType: ActivityEventType): string {
  if (eventType.includes("completed")) return "✓";
  if (eventType.includes("created")) return "+";
  if (eventType.includes("cancelled")) return "×";
  if (eventType.includes("missed")) return "!";
  if (eventType.includes("archived")) return "→";
  if (eventType.includes("progress")) return "%";
  if (eventType.includes("reopened")) return "↻";
  if (eventType.includes("deactivated")) return "−";
  return "•";
}

export default function Activity() {
  const [events, setEvents] = useState<ActivityEventResponse[]>([]);
  const [filter, setFilter] = useState<ActivityFilter>("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadActivity() {
    try {
      setLoading(true);
      setError("");

      let data: ActivityEventResponse[];

      if (startDate && endDate) {
        data = await getActivityRange(
          USER_ID,
          `${startDate}T00:00:00`,
          `${endDate}T23:59:59`,
          100,
        );
      } else {
        data = await getActivityTimeline(USER_ID, 100);
      }

      setEvents(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load activity.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadActivity();
  }, []);

  async function handleApplyDateFilter() {
    await loadActivity();
  }

  async function handleClearDateFilter() {
    setStartDate("");
    setEndDate("");

    try {
      setLoading(true);
      setError("");

      const data = await getActivityTimeline(USER_ID, 100);
      setEvents(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load activity.",
      );
    } finally {
      setLoading(false);
    }
  }

  const filteredEvents =
    filter === "all"
      ? events
      : events.filter((event) => event.entity_type === filter);

  const counts = {
    total: events.length,
    tasks: events.filter((event) => event.entity_type === "task").length,
    goals: events.filter((event) => event.entity_type === "goal").length,
    habits: events.filter((event) => event.entity_type === "habit").length,
    projects: events.filter((event) => event.entity_type === "project").length,
  };

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">LifeOS / Activity</p>
          <h1>Activity Timeline</h1>
          <p className="page-description">
            See what has happened across your LifeOS workspace over time.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Events</span>
          <strong>{counts.total}</strong>
        </div>

        <div className="stat-card">
          <span>Tasks</span>
          <strong>{counts.tasks}</strong>
        </div>

        <div className="stat-card">
          <span>Goals</span>
          <strong>{counts.goals}</strong>
        </div>

        <div className="stat-card">
          <span>Habits</span>
          <strong>{counts.habits}</strong>
        </div>

        <div className="stat-card">
          <span>Projects</span>
          <strong>{counts.projects}</strong>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="activity-controls">
        <div className="activity-filters">
          <button
            className={filter === "all" ? "filter-button active" : "filter-button"}
            type="button"
            onClick={() => setFilter("all")}
          >
            All
          </button>

          <button
            className={
              filter === "task" ? "filter-button active" : "filter-button"
            }
            type="button"
            onClick={() => setFilter("task")}
          >
            Tasks
          </button>

          <button
            className={
              filter === "goal" ? "filter-button active" : "filter-button"
            }
            type="button"
            onClick={() => setFilter("goal")}
          >
            Goals
          </button>

          <button
            className={
              filter === "habit" ? "filter-button active" : "filter-button"
            }
            type="button"
            onClick={() => setFilter("habit")}
          >
            Habits
          </button>

          <button
            className={
              filter === "project" ? "filter-button active" : "filter-button"
            }
            type="button"
            onClick={() => setFilter("project")}
          >
            Projects
          </button>
        </div>

        <div className="date-filter">
          <label>
            From
            <input
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
          </label>

          <label>
            To
            <input
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
          </label>

          <button
            className="primary-button"
            type="button"
            onClick={() => void handleApplyDateFilter()}
            disabled={!startDate || !endDate}
          >
            Apply
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={() => void handleClearDateFilter()}
          >
            Clear
          </button>
        </div>
      </div>

      <div className="activity-card">
        <div className="card-header">
          <div>
            <h2>Recent Activity</h2>
            <p>
              {filteredEvents.length} event
              {filteredEvents.length === 1 ? "" : "s"} shown
            </p>
          </div>
        </div>

        {loading ? (
          <p className="empty-state">Loading activity...</p>
        ) : filteredEvents.length === 0 ? (
          <p className="empty-state">
            No activity found for the selected filters.
          </p>
        ) : (
          <div className="timeline">
            {filteredEvents.map((event) => (
              <article className="timeline-item" key={event.id}>
                <div className="timeline-icon">
                  {getEventIcon(event.event_type)}
                </div>

                <div className="timeline-content">
                  <div className="timeline-title-row">
                    <h3>{formatEventType(event.event_type)}</h3>

                    <span className="timeline-entity">
                      {formatEntityType(event.entity_type)}
                    </span>
                  </div>

                  <p className="timeline-date">
                    {formatDateTime(event.occurred_at)}
                  </p>

                  {event.event_metadata &&
                    Object.keys(event.event_metadata).length > 0 && (
                      <div className="activity-metadata">
                        {Object.entries(event.event_metadata).map(
                          ([key, value]) => (
                            <span key={key}>
                              <strong>{key.replace(/_/g, " ")}:</strong>{" "}
                              {String(value)}
                            </span>
                          ),
                        )}
                      </div>
                    )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
