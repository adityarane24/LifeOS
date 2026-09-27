import { useEffect, useState } from "react";
import {
  getUserAnalytics,
} from "../api/analytics";
import type { UserAnalytics } from "../types/analytics";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

function getDateDaysAgo(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString().split("T")[0];
}

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export default function Analytics() {
  const [analytics, setAnalytics] =
    useState<UserAnalytics | null>(null);

  const [startDate, setStartDate] = useState(getDateDaysAgo(30));
  const [endDate, setEndDate] = useState(getToday());

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadAnalytics(
    start = startDate,
    end = endDate,
  ) {
    try {
      setLoading(true);
      setError("");

      const data = await getUserAnalytics(
        USER_ID,
        `${start}T00:00:00`,
        `${end}T23:59:59`,
      );

      setAnalytics(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load analytics.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAnalytics();
  }, []);

  async function handleApply() {
    if (!startDate || !endDate) {
      setError("Please select both dates.");
      return;
    }

    if (startDate > endDate) {
      setError("Start date cannot be after end date.");
      return;
    }

    await loadAnalytics(startDate, endDate);
  }

  async function handleLast7Days() {
    const start = getDateDaysAgo(7);
    const end = getToday();

    setStartDate(start);
    setEndDate(end);

    await loadAnalytics(start, end);
  }

  async function handleLast30Days() {
    const start = getDateDaysAgo(30);
    const end = getToday();

    setStartDate(start);
    setEndDate(end);

    await loadAnalytics(start, end);
  }

  if (loading && !analytics) {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <p className="eyebrow">LifeOS / Analytics</p>
            <h1>Analytics</h1>
            <p className="page-description">
              Understand your activity and progress over time.
            </p>
          </div>
        </div>

        <div className="analytics-loading">
          Loading analytics...
        </div>
      </section>
    );
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">LifeOS / Analytics</p>
          <h1>Analytics</h1>
          <p className="page-description">
            Understand your activity and progress over time.
          </p>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="analytics-controls">
        <div className="quick-range-buttons">
          <button
            className="secondary-button"
            type="button"
            onClick={() => void handleLast7Days()}
          >
            Last 7 Days
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={() => void handleLast30Days()}
          >
            Last 30 Days
          </button>
        </div>

        <div className="analytics-date-filter">
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
            onClick={() => void handleApply()}
            disabled={loading}
          >
            {loading ? "Loading..." : "Apply"}
          </button>
        </div>
      </div>

      {analytics && (
        <>
          <div className="analytics-overview">
            <div className="analytics-highlight">
              <span>Total Activity</span>
              <strong>{analytics.total_events}</strong>
              <small>events</small>
            </div>

            <div className="analytics-highlight">
              <span>Task Completion</span>
              <strong>
                {formatPercentage(
                  analytics.tasks.completion_rate,
                )}
              </strong>
              <small>
                {analytics.tasks.completed} completed
              </small>
            </div>

            <div className="analytics-highlight">
              <span>Habit Consistency</span>
              <strong>
                {formatPercentage(
                  analytics.habits.consistency_rate,
                )}
              </strong>
              <small>
                {analytics.habits.completed} completed
              </small>
            </div>
          </div>

          <div className="analytics-grid">
            <article className="analytics-card">
              <div className="analytics-card-header">
                <div>
                  <span className="analytics-card-label">
                    TASKS
                  </span>
                  <h2>Task Activity</h2>
                </div>

                <span className="analytics-card-value">
                  {formatPercentage(
                    analytics.tasks.completion_rate,
                  )}
                </span>
              </div>

              <div className="metric-list">
                <div className="metric-row">
                  <span>Created</span>
                  <strong>{analytics.tasks.created}</strong>
                </div>

                <div className="metric-row">
                  <span>Completed</span>
                  <strong>{analytics.tasks.completed}</strong>
                </div>

                <div className="metric-row">
                  <span>Cancelled</span>
                  <strong>{analytics.tasks.cancelled}</strong>
                </div>

                <div className="metric-row">
                  <span>Reopened</span>
                  <strong>{analytics.tasks.reopened}</strong>
                </div>
              </div>

              <div className="analytics-progress">
                <div
                  className="analytics-progress-fill"
                  style={{
                    width: `${Math.min(
                      analytics.tasks.completion_rate,
                      100,
                    )}%`,
                  }}
                />
              </div>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-header">
                <div>
                  <span className="analytics-card-label">
                    HABITS
                  </span>
                  <h2>Habit Consistency</h2>
                </div>

                <span className="analytics-card-value">
                  {formatPercentage(
                    analytics.habits.consistency_rate,
                  )}
                </span>
              </div>

              <div className="metric-list">
                <div className="metric-row">
                  <span>Completed</span>
                  <strong>{analytics.habits.completed}</strong>
                </div>

                <div className="metric-row">
                  <span>Missed</span>
                  <strong>{analytics.habits.missed}</strong>
                </div>

                <div className="metric-row">
                  <span>Total Outcomes</span>
                  <strong>
                    {analytics.habits.completed +
                      analytics.habits.missed}
                  </strong>
                </div>
              </div>

              <div className="analytics-progress">
                <div
                  className="analytics-progress-fill"
                  style={{
                    width: `${Math.min(
                      analytics.habits.consistency_rate,
                      100,
                    )}%`,
                  }}
                />
              </div>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-header">
                <div>
                  <span className="analytics-card-label">
                    GOALS
                  </span>
                  <h2>Goal Progress</h2>
                </div>
              </div>

              <div className="metric-list">
                <div className="metric-row">
                  <span>Completed</span>
                  <strong>{analytics.goals.completed}</strong>
                </div>

                <div className="metric-row">
                  <span>Progress Updates</span>
                  <strong>
                    {analytics.goals.progress_updates}
                  </strong>
                </div>
              </div>
            </article>

            <article className="analytics-card">
              <div className="analytics-card-header">
                <div>
                  <span className="analytics-card-label">
                    PROJECTS
                  </span>
                  <h2>Project Activity</h2>
                </div>
              </div>

              <div className="metric-list">
                <div className="metric-row">
                  <span>Completed</span>
                  <strong>
                    {analytics.projects.completed}
                  </strong>
                </div>

                <div className="metric-row">
                  <span>Archived</span>
                  <strong>
                    {analytics.projects.archived}
                  </strong>
                </div>
              </div>
            </article>
          </div>
        </>
      )}
    </section>
  );
}
