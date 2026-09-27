import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
} from "../api/tasks";

import type {
  TaskPriority,
  TaskResponse,
  TaskStatus,
} from "../types/task";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

const statuses: TaskStatus[] = [
  "pending",
  "in_progress",
  "completed",
  "cancelled",
];

const priorities: TaskPriority[] = [
  "low",
  "medium",
  "high",
  "urgent",
];

function formatStatus(status: TaskStatus): string {
  return status
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatPriority(priority: TaskPriority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

export default function Tasks() {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [dueDate, setDueDate] = useState("");

  async function loadTasks() {
    try {
      setLoading(true);
      setError(null);

      const data = await getTasks(USER_ID);
      setTasks(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load tasks.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  async function handleCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim()) {
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const task = await createTask({
        user_id: USER_ID,
        title: title.trim(),
        description: description.trim() || null,
        priority,
        due_date: dueDate || null,
      });

      setTasks((current) => [task, ...current]);

      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create task.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(
    taskId: string,
    status: TaskStatus,
  ) {
    try {
      setError(null);

      const updatedTask = await updateTask(taskId, {
        status,
      });

      setTasks((current) =>
        current.map((task) =>
          task.id === taskId ? updatedTask : task,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update task.",
      );
    }
  }

  async function handlePriorityChange(
    taskId: string,
    priority: TaskPriority,
  ) {
    try {
      setError(null);

      const updatedTask = await updateTask(taskId, {
        priority,
      });

      setTasks((current) =>
        current.map((task) =>
          task.id === taskId ? updatedTask : task,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update task.",
      );
    }
  }

  async function handleDeleteTask(taskId: string) {
    const confirmed = window.confirm(
      "Delete this task?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      await deleteTask(taskId);

      setTasks((current) =>
        current.filter((task) => task.id !== taskId),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete task.",
      );
    }
  }

  const completedCount = tasks.filter(
    (task) => task.status === "completed",
  ).length;

  const pendingCount = tasks.filter(
    (task) =>
      task.status === "pending" ||
      task.status === "in_progress",
  ).length;

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Productivity</span>
          <h1>Tasks</h1>
          <p>Capture, organize, and complete your work.</p>
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
          <span>Total</span>
          <strong>{tasks.length}</strong>
        </div>

        <div className="task-stat">
          <span>Pending</span>
          <strong>{pendingCount}</strong>
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
              <span className="eyebrow">New Task</span>
              <h2>Create a task</h2>
            </div>
          </div>

          <form onSubmit={handleCreateTask} className="task-form">
            <label>
              Title
              <input
                type="text"
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                placeholder="What needs to be done?"
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
                      event.target.value as TaskPriority,
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
                Due date
                <input
                  type="date"
                  value={dueDate}
                  onChange={(event) =>
                    setDueDate(event.target.value)
                  }
                />
              </label>
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={saving || !title.trim()}
            >
              {saving ? "Creating..." : "Create Task"}
            </button>
          </form>
        </article>

        <article className="dashboard-card task-list-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">Your Work</span>
              <h2>Task List</h2>
            </div>
          </div>

          {loading ? (
            <div className="empty-state">
              <strong>Loading tasks...</strong>
            </div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">
              <strong>No tasks yet</strong>
              <p>Create your first task using the form.</p>
            </div>
          ) : (
            <div className="tasks-list">
              {tasks.map((task) => (
                <article className="task-item" key={task.id}>
                  <div className="task-main">
                    <div className="task-title-row">
                      <h3>{task.title}</h3>

                      <span
                        className={`priority-badge priority-${task.priority}`}
                      >
                        {formatPriority(task.priority)}
                      </span>
                    </div>

                    {task.description && (
                      <p>{task.description}</p>
                    )}

                    {task.due_date && (
                      <span className="task-due-date">
                        Due:{" "}
                        {new Date(
                          task.due_date,
                        ).toLocaleDateString("en-IN")}
                      </span>
                    )}
                  </div>

                  <div className="task-actions">
                    <select
                      value={task.status}
                      onChange={(event) =>
                        handleStatusChange(
                          task.id,
                          event.target.value as TaskStatus,
                        )
                      }
                    >
                      {statuses.map((status) => (
                        <option key={status} value={status}>
                          {formatStatus(status)}
                        </option>
                      ))}
                    </select>

                    <select
                      value={task.priority}
                      onChange={(event) =>
                        handlePriorityChange(
                          task.id,
                          event.target.value as TaskPriority,
                        )
                      }
                    >
                      {priorities.map((item) => (
                        <option key={item} value={item}>
                          {formatPriority(item)}
                        </option>
                      ))}
                    </select>

                    <button
                      type="button"
                      className="delete-button"
                      onClick={() =>
                        handleDeleteTask(task.id)
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
