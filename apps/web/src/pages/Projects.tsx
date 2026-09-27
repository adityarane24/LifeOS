import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  createProject,
  deleteProject,
  getProjects,
  updateProject,
} from "../api/projects";
import type {
  ProjectPriority,
  ProjectResponse,
  ProjectStatus,
} from "../types/project";

const USER_ID = "6ed7310b-a6d5-4b55-b656-af1726c62572";

function formatStatus(status: ProjectStatus): string {
  return status.replace("_", " ");
}

function formatPriority(priority: ProjectPriority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

function getToday(): string {
  return new Date().toISOString().split("T")[0];
}

export default function Projects() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<ProjectPriority>("medium");
  const [startDate, setStartDate] = useState(getToday());
  const [targetDate, setTargetDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadProjects() {
    try {
      setLoading(true);
      setError("");

      const data = await getProjects(USER_ID);
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  async function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim()) {
      setError("Project title is required.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      await createProject({
        user_id: USER_ID,
        title: title.trim(),
        description: description.trim() || null,
        priority,
        start_date: startDate,
        target_date: targetDate || null,
        status: "planned",
      });

      setTitle("");
      setDescription("");
      setPriority("medium");
      setStartDate(getToday());
      setTargetDate("");

      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project.");
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(
    project: ProjectResponse,
    status: ProjectStatus,
  ) {
    try {
      setError("");

      await updateProject(project.id, {
        status,
      });

      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update project.");
    }
  }

  async function handlePriorityChange(
    project: ProjectResponse,
    newPriority: ProjectPriority,
  ) {
    try {
      setError("");

      await updateProject(project.id, {
        priority: newPriority,
      });

      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update priority.");
    }
  }

  async function handleDeleteProject(projectId: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this project?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteProject(projectId);
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete project.");
    }
  }

  const activeProjects = projects.filter(
    (project) => project.status === "active",
  ).length;

  const plannedProjects = projects.filter(
    (project) => project.status === "planned",
  ).length;

  const completedProjects = projects.filter(
    (project) => project.status === "completed",
  ).length;

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <p className="eyebrow">LifeOS / Projects</p>
          <h1>Projects</h1>
          <p className="page-description">
            Organize larger pieces of work and track them from planning to
            completion.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Projects</span>
          <strong>{projects.length}</strong>
        </div>

        <div className="stat-card">
          <span>Planned</span>
          <strong>{plannedProjects}</strong>
        </div>

        <div className="stat-card">
          <span>Active</span>
          <strong>{activeProjects}</strong>
        </div>

        <div className="stat-card">
          <span>Completed</span>
          <strong>{completedProjects}</strong>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="content-grid">
        <form className="form-card" onSubmit={handleCreateProject}>
          <div className="card-header">
            <div>
              <h2>Create Project</h2>
              <p>Start a new project in your LifeOS workspace.</p>
            </div>
          </div>

          <label>
            Project title
            <input
              type="text"
              placeholder="e.g. Build LifeOS AI layer"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </label>

          <label>
            Description
            <textarea
              placeholder="What is this project about?"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={4}
            />
          </label>

          <div className="form-row">
            <label>
              Priority
              <select
                value={priority}
                onChange={(event) =>
                  setPriority(event.target.value as ProjectPriority)
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>

            <label>
              Start date
              <input
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </label>
          </div>

          <label>
            Target date
            <input
              type="date"
              value={targetDate}
              onChange={(event) => setTargetDate(event.target.value)}
            />
          </label>

          <button className="primary-button" type="submit" disabled={saving}>
            {saving ? "Creating..." : "Create Project"}
          </button>
        </form>

        <div className="list-card">
          <div className="card-header">
            <div>
              <h2>Your Projects</h2>
              <p>Manage your current and completed projects.</p>
            </div>
          </div>

          {loading ? (
            <p className="empty-state">Loading projects...</p>
          ) : projects.length === 0 ? (
            <p className="empty-state">
              No projects yet. Create your first project.
            </p>
          ) : (
            <div className="item-list">
              {projects.map((project) => (
                <article className="list-item project-item" key={project.id}>
                  <div className="item-main">
                    <div className="item-title-row">
                      <h3>{project.title}</h3>

                      <span
                        className={`status-badge status-${project.status}`}
                      >
                        {formatStatus(project.status)}
                      </span>
                    </div>

                    {project.description && (
                      <p className="item-description">
                        {project.description}
                      </p>
                    )}

                    <div className="project-meta">
                      <span>
                        Priority: {formatPriority(project.priority)}
                      </span>

                      <span>
                        Start: {project.start_date}
                      </span>

                      {project.target_date && (
                        <span>
                          Target: {project.target_date}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="task-actions">
                    <select
                      value={project.status}
                      onChange={(event) =>
                        void handleStatusChange(
                          project,
                          event.target.value as ProjectStatus,
                        )
                      }
                    >
                      <option value="planned">Planned</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="archived">Archived</option>
                    </select>

                    <select
                      value={project.priority}
                      onChange={(event) =>
                        void handlePriorityChange(
                          project,
                          event.target.value as ProjectPriority,
                        )
                      }
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>

                    <button
                      className="danger-button"
                      type="button"
                      onClick={() => void handleDeleteProject(project.id)}
                    >
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
