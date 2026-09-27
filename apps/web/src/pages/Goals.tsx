import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createGoal,
  deleteGoal,
  getGoals,
  updateGoal,
} from "../api/goals";

import type {
  GoalPriority,
  GoalResponse,
  GoalStatus,
} from "../types/goal";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

const statuses: GoalStatus[] = [
  "pending",
  "in_progress",
  "completed",
  "cancelled",
];

const priorities: GoalPriority[] = [
  "low",
  "medium",
  "high",
  "urgent",
];

function formatStatus(status: GoalStatus): string {
  return status
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatPriority(priority: GoalPriority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function Goals() {
  const [goals, setGoals] = useState<GoalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<GoalPriority>("medium");
  const [targetDate, setTargetDate] = useState("");

  async function loadGoals() {
    try {
      setLoading(true);
      setError(null);

      const data = await getGoals(USER_ID);
      setGoals(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load goals.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadGoals();
  }, []);

  async function handleCreateGoal(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!title.trim()) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const goal = await createGoal({
        user_id: USER_ID,
        title: title.trim(),
        description: description.trim() || null,
        priority,
        target_date: targetDate || null,
        progress: 0,
      });

      setGoals((current) => [goal, ...current]);

      setTitle("");
      setDescription("");
      setPriority("medium");
      setTargetDate("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create goal.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(
    goalId: string,
    status: GoalStatus,
  ) {
    try {
      setError(null);

      const updatedGoal = await updateGoal(goalId, {
        status,
      });

      setGoals((current) =>
        current.map((goal) =>
          goal.id === goalId ? updatedGoal : goal,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update goal.",
      );
    }
  }

  async function handlePriorityChange(
    goalId: string,
    priority: GoalPriority,
  ) {
    try {
      setError(null);

      const updatedGoal = await updateGoal(goalId, {
        priority,
      });

      setGoals((current) =>
        current.map((goal) =>
          goal.id === goalId ? updatedGoal : goal,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update goal.",
      );
    }
  }

  async function handleProgressChange(
    goalId: string,
    progress: number,
  ) {
    const safeProgress = Math.min(
      100,
      Math.max(0, progress),
    );

    try {
      setError(null);

      const updatedGoal = await updateGoal(goalId, {
        progress: safeProgress,
      });

      setGoals((current) =>
        current.map((goal) =>
          goal.id === goalId ? updatedGoal : goal,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update goal progress.",
      );
    }
  }

  async function handleDeleteGoal(goalId: string) {
    const confirmed = window.confirm(
      "Delete this goal?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      await deleteGoal(goalId);

      setGoals((current) =>
        current.filter((goal) => goal.id !== goalId),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete goal.",
      );
    }
  }

  const activeCount = goals.filter(
    (goal) =>
      goal.status !== "completed" &&
      goal.status !== "cancelled",
  ).length;

  const completedCount = goals.filter(
    (goal) => goal.status === "completed",
  ).length;

  const averageProgress =
    goals.length === 0
      ? 0
      : goals.reduce(
          (total, goal) => total + goal.progress,
          0,
        ) / goals.length;

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Direction</span>
          <h1>Goals</h1>
          <p>
            Define what matters and track progress over time.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-card task-error">
          <strong>Something went wrong</strong>
          <p>{error}</p>
        </div>
      )}

      <div className="task-stats">
        <div className="task-stat">
          <span>Total Goals</span>
          <strong>{goals.length}</strong>
        </div>

        <div className="task-stat">
          <span>Active</span>
          <strong>{activeCount}</strong>
        </div>

        <div className="task-stat">
          <span>Average Progress</span>
          <strong>{averageProgress.toFixed(0)}%</strong>
        </div>

        <div className="task-stat">
          <span>Completed</span>
          <strong>{completedCount}</strong>
        </div>
      </div>

      <div className="task-layout">
        <article className="dashboard-card create-task-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">New Goal</span>
              <h2>Create a goal</h2>
            </div>
          </div>

          <form
            onSubmit={handleCreateGoal}
            className="task-form"
          >
            <label>
              Title
              <input
                type="text"
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                placeholder="What do you want to achieve?"
              />
            </label>

            <label>
              Description
              <textarea
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
                placeholder="Optional description"
                rows={4}
              />
            </label>

            <div className="form-row">
              <label>
                Priority
                <select
                  value={priority}
                  onChange={(event) =>
                    setPriority(
                      event.target.value as GoalPriority,
                    )
                  }
                >
                  {priorities.map((item) => (
                    <option key={item} value={item}>
                      {formatPriority(item)}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Target date
                <input
                  type="date"
                  value={targetDate}
                  onChange={(event) =>
                    setTargetDate(event.target.value)
                  }
                />
              </label>
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={saving || !title.trim()}
            >
              {saving ? "Creating..." : "Create Goal"}
            </button>
          </form>
        </article>

        <article className="dashboard-card task-list-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Your Direction</span>
              <h2>Goal List</h2>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              <strong>Loading goals...</strong>
            </div>
          ) : goals.length === 0 ? (
            <div className="empty-state">
              <strong>No goals yet</strong>
              <p>
                Create your first goal using the form.
              </p>
            </div>
          ) : (
            <div className="tasks-list">
              {goals.map((goal) => (
                <article
                  className="task-item"
                  key={goal.id}
                >
                  <div className="task-main">
                    <div className="task-title-row">
                      <h3>{goal.title}</h3>

                      <span
                        className={`priority-badge priority-${goal.priority}`}
                      >
                        {formatPriority(goal.priority)}
                      </span>
                    </div>

                    {goal.description && (
                      <p>{goal.description}</p>
                    )}

                    <div className="goal-progress-header">
                      <span>Progress</span>
                      <strong>{goal.progress}%</strong>
                    </div>

                    <div className="progress-track">
                      <div
                        className="progress-value"
                        style={{
                          width: `${goal.progress}%`,
                        }}
                      />
                    </div>

                    <input
                      className="goal-progress-slider"
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={goal.progress}
                      onChange={(event) =>
                        handleProgressChange(
                          goal.id,
                          Number(event.target.value),
                        )
                      }
                    />

                    {goal.target_date && (
                      <span className="task-due-date">
                        Target: {formatDate(goal.target_date)}
                      </span>
                    )}
                  </div>

                  <div className="task-actions">
                    <select
                      value={goal.status}
                      onChange={(event) =>
                        handleStatusChange(
                          goal.id,
                          event.target.value as GoalStatus,
                        )
                      }
                    >
                      {statuses.map((status) => (
                        <option
                          key={status}
                          value={status}
                        >
                          {formatStatus(status)}
                        </option>
                      ))}
                    </select>

                    <select
                      value={goal.priority}
                      onChange={(event) =>
                        handlePriorityChange(
                          goal.id,
                          event.target.value as GoalPriority,
                        )
                      }
                    >
                      {priorities.map((item) => (
                        <option
                          key={item}
                          value={item}
                        >
                          {formatPriority(item)}
                        </option>
                      ))}
                    </select>

                    <button
                      type="button"
                      className="delete-button"
                      onClick={() =>
                        handleDeleteGoal(goal.id)
                      }
                    >
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
