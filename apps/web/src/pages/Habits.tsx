import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createHabit,
  createHabitCompletion,
  deleteHabit,
  getHabitAnalytics,
  getHabits,
  updateHabit,
} from "../api/habits";

import type {
  HabitAnalyticsResponse,
  HabitFrequency,
  HabitResponse,
} from "../types/habit";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

function formatFrequency(frequency: HabitFrequency): string {
  return frequency.charAt(0).toUpperCase() + frequency.slice(1);
}

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

interface HabitWithAnalytics extends HabitResponse {
  analytics?: HabitAnalyticsResponse;
}

export default function Habits() {
  const [habits, setHabits] = useState<HabitWithAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [frequency, setFrequency] =
    useState<HabitFrequency>("daily");
  const [target, setTarget] = useState("1");
  const [unit, setUnit] = useState("time");

  async function loadHabits() {
    try {
      setLoading(true);
      setError(null);

      const data = await getHabits(USER_ID);

      const habitsWithAnalytics = await Promise.all(
        data.map(async (habit) => {
          try {
            const analytics = await getHabitAnalytics(
              habit.id,
            );

            return {
              ...habit,
              analytics,
            };
          } catch {
            return habit;
          }
        }),
      );

      setHabits(habitsWithAnalytics);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load habits.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHabits();
  }, []);

  async function handleCreateHabit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!title.trim()) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const habit = await createHabit({
        user_id: USER_ID,
        title: title.trim(),
        description: description.trim() || null,
        frequency,
        target: Number(target) || 1,
        unit: unit.trim() || "time",
        start_date: getToday(),
        is_active: true,
      });

      let analytics: HabitAnalyticsResponse | undefined;

      try {
        analytics = await getHabitAnalytics(habit.id);
      } catch {
        // Analytics may not have data immediately.
      }

      setHabits((current) => [
        {
          ...habit,
          analytics,
        },
        ...current,
      ]);

      setTitle("");
      setDescription("");
      setFrequency("daily");
      setTarget("1");
      setUnit("time");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create habit.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(
    habit: HabitWithAnalytics,
  ) {
    try {
      setError(null);

      const updatedHabit = await updateHabit(habit.id, {
        is_active: !habit.is_active,
      });

      setHabits((current) =>
        current.map((item) =>
          item.id === habit.id
            ? {
                ...item,
                ...updatedHabit,
              }
            : item,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update habit.",
      );
    }
  }

  async function handleCompleteToday(
    habit: HabitWithAnalytics,
  ) {
    try {
      setError(null);

      await createHabitCompletion(habit.id, {
        completion_date: getToday(),
        value: habit.target,
        completed: true,
      });

      const analytics = await getHabitAnalytics(
        habit.id,
      );

      setHabits((current) =>
        current.map((item) =>
          item.id === habit.id
            ? {
                ...item,
                analytics,
              }
            : item,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to record today's completion.",
      );
    }
  }

  async function handleDeleteHabit(habitId: string) {
    const confirmed = window.confirm(
      "Delete this habit?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      await deleteHabit(habitId);

      setHabits((current) =>
        current.filter((habit) => habit.id !== habitId),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete habit.",
      );
    }
  }

  const activeCount = habits.filter(
    (habit) => habit.is_active,
  ).length;

  const averageCompletionRate =
    habits.length === 0
      ? 0
      : habits.reduce(
          (total, habit) =>
            total + (habit.analytics?.completion_rate ?? 0),
          0,
        ) / habits.length;

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Consistency</span>
          <h1>Habits</h1>
          <p>
            Build routines and understand your consistency
            over time.
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
          <span>Total Habits</span>
          <strong>{habits.length}</strong>
        </div>

        <div className="task-stat">
          <span>Active</span>
          <strong>{activeCount}</strong>
        </div>

        <div className="task-stat">
          <span>Average Completion</span>
          <strong>
            {averageCompletionRate.toFixed(0)}%
          </strong>
        </div>
      </div>

      <div className="task-layout">
        <article className="dashboard-card create-task-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">New Habit</span>
              <h2>Create a habit</h2>
            </div>
          </div>

          <form
            onSubmit={handleCreateHabit}
            className="task-form"
          >
            <label>
              Habit name
              <input
                type="text"
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                placeholder="e.g. Read for 30 minutes"
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
                Frequency
                <select
                  value={frequency}
                  onChange={(event) =>
                    setFrequency(
                      event.target.value as HabitFrequency,
                    )
                  }
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </label>

              <label>
                Target
                <input
                  type="number"
                  min="1"
                  value={target}
                  onChange={(event) =>
                    setTarget(event.target.value)
                  }
                />
              </label>
            </div>

            <label>
              Unit
              <input
                type="text"
                value={unit}
                onChange={(event) =>
                  setUnit(event.target.value)
                }
                placeholder="time, pages, glasses..."
              />
            </label>

            <button
              type="submit"
              className="primary-button"
              disabled={saving || !title.trim()}
            >
              {saving
                ? "Creating..."
                : "Create Habit"}
            </button>
          </form>
        </article>

        <article className="dashboard-card task-list-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Your Routines</span>
              <h2>Habit List</h2>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              <strong>Loading habits...</strong>
            </div>
          ) : habits.length === 0 ? (
            <div className="empty-state">
              <strong>No habits yet</strong>
              <p>
                Create your first habit using the form.
              </p>
            </div>
          ) : (
            <div className="tasks-list">
              {habits.map((habit) => (
                <article
                  className="task-item"
                  key={habit.id}
                >
                  <div className="task-main">
                    <div className="task-title-row">
                      <h3>{habit.title}</h3>

                      <span
                        className={
                          habit.is_active
                            ? "priority-badge priority-medium"
                            : "priority-badge priority-low"
                        }
                      >
                        {habit.is_active
                          ? "Active"
                          : "Paused"}
                      </span>
                    </div>

                    {habit.description && (
                      <p>{habit.description}</p>
                    )}

                    <div className="habit-meta">
                      <span>
                        {formatFrequency(habit.frequency)}
                      </span>

                      <span>
                        Target: {habit.target} {habit.unit}
                      </span>
                    </div>

                    <div className="goal-progress-header">
                      <span>Completion rate</span>
                      <strong>
                        {(
                          habit.analytics
                            ?.completion_rate ?? 0
                        ).toFixed(0)}
                        %
                      </strong>
                    </div>

                    <div className="progress-track">
                      <div
                        className="progress-value"
                        style={{
                          width: `${Math.min(
                            habit.analytics
                              ?.completion_rate ?? 0,
                            100,
                          )}%`,
                        }}
                      />
                    </div>

                    <div className="habit-streak">
                      <span>
                        Current streak:{" "}
                        <strong>
                          {habit.analytics
                            ?.current_streak ?? 0}
                        </strong>
                      </span>

                      <span>
                        Best streak:{" "}
                        <strong>
                          {habit.analytics
                            ?.longest_streak ?? 0}
                        </strong>
                      </span>
                    </div>
                  </div>

                  <div className="task-actions">
                    <button
                      type="button"
                      className="primary-button"
                      onClick={() =>
                        handleCompleteToday(habit)
                      }
                      disabled={!habit.is_active}
                    >
                      Done Today
                    </button>

                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() =>
                        handleToggleActive(habit)
                      }
                    >
                      {habit.is_active
                        ? "Pause"
                        : "Resume"}
                    </button>

                    <button
                      type="button"
                      className="delete-button"
                      onClick={() =>
                        handleDeleteHabit(habit.id)
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
