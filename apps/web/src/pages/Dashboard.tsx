import { useEffect, useState } from "react";

import { getTasks } from "../api/tasks";
import { getGoals } from "../api/goals";
import { getHabits } from "../api/habits";
import { getProjects } from "../api/projects";
import { getActivityTimeline } from "../api/activity";
import { getUserAnalytics } from "../api/analytics";

import type { TaskResponse } from "../types/task";
import type { GoalResponse } from "../types/goal";
import type { HabitResponse } from "../types/habit";
import type { ProjectResponse } from "../types/project";
import type { ActivityEventResponse } from "../types/activity";
import type { UserAnalytics } from "../types/analytics";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

interface DashboardData {
  tasks: TaskResponse[];
  goals: GoalResponse[];
  habits: HabitResponse[];
  projects: ProjectResponse[];
  activity: ActivityEventResponse[];
  analytics: UserAnalytics;
}

function formatEventType(eventType: string): string {
  return eventType
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
  });
}

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

function getGreeting(): string {
  const hour = new Date().getHours();

  if (hour < 12) {
    return "Good morning";
  }

  if (hour < 18) {
    return "Good afternoon";
  }

  return "Good evening";
}

function formatDueDate(value: string | null): string {
  if (!value) {
    return "No due date";
  }

  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - 30);

        const [
          tasks,
          goals,
          habits,
          projects,
          activity,
          analytics,
        ] = await Promise.all([
          getTasks(USER_ID),
          getGoals(USER_ID),
          getHabits(USER_ID),
          getProjects(USER_ID),
          getActivityTimeline(USER_ID, 10),
          getUserAnalytics(
            USER_ID,
            start.toISOString(),
            end.toISOString(),
          ),
        ]);

        setData({
          tasks,
          goals,
          habits,
          projects,
          activity,
          analytics,
        });
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load the LifeOS dashboard.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  if (loading) {
    return (
      <section>
        <div className="dashboard-heading">
          <div>
            <span className="eyebrow">Overview</span>
            <h1>Loading your LifeOS...</h1>
            <p>Getting your latest tasks, goals, habits, and activity.</p>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <div className="dashboard-heading">
          <div>
            <span className="eyebrow">Overview</span>
            <h1>Dashboard</h1>
            <p>Something went wrong while loading your data.</p>
          </div>
        </div>

        <div className="error-card">
          <strong>API connection error</strong>
          <p>{error}</p>
        </div>
      </section>
    );
  }

  if (!data) {
    return null;
  }

  const today = getToday();

  const pendingTasks = data.tasks.filter(
    (task) =>
      task.status !== "completed" &&
      task.status !== "cancelled",
  );

  const todayTasks = pendingTasks.filter(
    (task) => task.due_date?.startsWith(today),
  );

  const activeGoals = data.goals.filter(
    (goal) =>
      goal.status !== "completed" &&
      goal.status !== "cancelled",
  );

  const activeHabits = data.habits.filter(
    (habit) => habit.is_active,
  );

  const activeProjects = data.projects.filter(
    (project) => project.status === "active",
  );

  const averageGoalProgress =
    activeGoals.length === 0
      ? 0
      : activeGoals.reduce(
          (total, goal) => total + goal.progress,
          0,
        ) / activeGoals.length;

  return (
    <section>
      <div className="dashboard-heading dashboard-hero">
        <div>
          <span className="eyebrow">LifeOS / Overview</span>
          <h1>
            {getGreeting()}, Aditya.
          </h1>
          <p>
            Here is what is happening across your personal operating
            system today.
          </p>
        </div>

        <div className="dashboard-date">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
          })}
        </div>
      </div>

      <div className="stats-grid">
        <article className="stat-card">
          <span>Pending Tasks</span>
          <strong>{pendingTasks.length}</strong>
          <small>
            {todayTasks.length} due today
          </small>
        </article>

        <article className="stat-card">
          <span>Active Goals</span>
          <strong>{activeGoals.length}</strong>
          <small>
            {Math.round(averageGoalProgress)}% average progress
          </small>
        </article>

        <article className="stat-card">
          <span>Active Habits</span>
          <strong>{activeHabits.length}</strong>
          <small>
            {data.analytics.habits.consistency_rate.toFixed(1)}%
            consistency
          </small>
        </article>

        <article className="stat-card">
          <span>Active Projects</span>
          <strong>{activeProjects.length}</strong>
          <small>
            {data.analytics.projects.completed} completed in 30 days
          </small>
        </article>
      </div>

      <div className="quick-actions">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Quick Actions</span>
            <h2>What do you want to work on?</h2>
          </div>
        </div>

        <div className="quick-action-grid">
          <button
            className="quick-action"
            type="button"
            onClick={() => window.dispatchEvent(
              new CustomEvent("lifeos:navigate", {
                detail: "tasks",
              }),
            )}
          >
            <strong>+ Task</strong>
            <span>Add something you need to get done.</span>
          </button>

          <button
            className="quick-action"
            type="button"
            onClick={() => window.dispatchEvent(
              new CustomEvent("lifeos:navigate", {
                detail: "goals",
              }),
            )}
          >
            <strong>+ Goal</strong>
            <span>Set something meaningful to achieve.</span>
          </button>

          <button
            className="quick-action"
            type="button"
            onClick={() => window.dispatchEvent(
              new CustomEvent("lifeos:navigate", {
                detail: "habits",
              }),
            )}
          >
            <strong>+ Habit</strong>
            <span>Build a repeatable daily behavior.</span>
          </button>

          <button
            className="quick-action"
            type="button"
            onClick={() => window.dispatchEvent(
              new CustomEvent("lifeos:navigate", {
                detail: "projects",
              }),
            )}
          >
            <strong>+ Project</strong>
            <span>Organize a larger piece of work.</span>
          </button>
        </div>
      </div>

      <div className="dashboard-grid dashboard-main-grid">
        <article className="dashboard-card focus-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Today</span>
              <h2>Today's Focus</h2>
            </div>

            <span className="activity-count">
              {todayTasks.length} tasks
            </span>
          </div>

          {todayTasks.length === 0 ? (
            <div className="empty-state">
              <strong>No tasks due today</strong>
              <p>
                You have no pending tasks with today's due date.
              </p>
            </div>
          ) : (
            <div className="focus-list">
              {todayTasks.slice(0, 6).map((task) => (
                <div className="focus-item" key={task.id}>
                  <div className="focus-indicator" />

                  <div className="focus-content">
                    <strong>{task.title}</strong>

                    <span>
                      {task.priority} priority ·{" "}
                      {formatDueDate(task.due_date)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">30 Days</span>
              <h2>Activity Overview</h2>
            </div>
          </div>

          <div className="metric-row">
            <div>
              <span>Total events</span>
              <strong>{data.analytics.total_events}</strong>
            </div>

            <div>
              <span>Task completion</span>
              <strong>
                {data.analytics.tasks.completion_rate.toFixed(1)}%
              </strong>
            </div>

            <div>
              <span>Habit consistency</span>
              <strong>
                {data.analytics.habits.consistency_rate.toFixed(1)}%
              </strong>
            </div>
          </div>
        </article>
      </div>

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Goals</span>
              <h2>Goal Progress</h2>
            </div>

            <span className="activity-count">
              {activeGoals.length} active
            </span>
          </div>

          {activeGoals.length === 0 ? (
            <div className="empty-state">
              <strong>No active goals</strong>
              <p>Create a goal to start tracking progress.</p>
            </div>
          ) : (
            <div className="goal-dashboard-list">
              {activeGoals.slice(0, 5).map((goal) => (
                <div className="goal-dashboard-item" key={goal.id}>
                  <div className="progress-label">
                    <span>{goal.title}</span>
                    <strong>{goal.progress}%</strong>
                  </div>

                  <div className="progress-track">
                    <div
                      className="progress-value"
                      style={{
                        width: `${Math.min(
                          Math.max(goal.progress, 0),
                          100,
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Tasks</span>
              <h2>Task Progress</h2>
            </div>

            <span className="activity-count">
              {data.analytics.tasks.completed} completed
            </span>
          </div>

          <div className="progress-section">
            <div className="progress-label">
              <span>30-day completion rate</span>
              <strong>
                {data.analytics.tasks.completion_rate.toFixed(1)}%
              </strong>
            </div>

            <div className="progress-track">
              <div
                className="progress-value"
                style={{
                  width: `${Math.min(
                    data.analytics.tasks.completion_rate,
                    100,
                  )}%`,
                }}
              />
            </div>

            <p>
              {data.analytics.tasks.created === 0
                ? "No task activity recorded in the last 30 days."
                : `${data.analytics.tasks.completed} of ${data.analytics.tasks.created} created tasks were completed.`}
            </p>
          </div>
        </article>
      </div>

      <article className="dashboard-card activity-card">
        <div className="card-header">
          <div>
            <span className="eyebrow">Timeline</span>
            <h2>Recent Activity</h2>
          </div>

          <span className="activity-count">
            {data.activity.length} events
          </span>
        </div>

        {data.activity.length === 0 ? (
          <div className="empty-state">
            <strong>No activity yet</strong>
            <p>
              Your recent LifeOS actions will appear here as you use
              the system.
            </p>
          </div>
        ) : (
          <div className="activity-list">
            {data.activity.map((event) => (
              <div className="activity-item" key={event.id}>
                <div className="activity-dot" />

                <div className="activity-content">
                  <strong>
                    {formatEventType(event.event_type)}
                  </strong>

                  <span>
                    {event.entity_type} ·{" "}
                    {formatDate(event.occurred_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
