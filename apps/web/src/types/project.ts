export type ProjectStatus =
  | "planned"
  | "active"
  | "completed"
  | "archived";

export type ProjectPriority =
  | "low"
  | "medium"
  | "high";

export interface ProjectCreate {
  user_id: string;
  title: string;
  description?: string | null;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  start_date?: string;
  target_date?: string | null;
}

export interface ProjectUpdate {
  title?: string | null;
  description?: string | null;
  status?: ProjectStatus | null;
  priority?: ProjectPriority | null;
  start_date?: string | null;
  target_date?: string | null;
}

export interface ProjectResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: ProjectStatus;
  priority: ProjectPriority;
  start_date: string;
  target_date: string | null;
  created_at: string;
  updated_at: string;
}
