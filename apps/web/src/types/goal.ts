export type GoalStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "cancelled";

export type GoalPriority =
  | "low"
  | "medium"
  | "high"
  | "urgent";

export interface GoalCreate {
  user_id: string;
  title: string;
  description?: string | null;
  status?: GoalStatus;
  priority?: GoalPriority;
  target_date?: string | null;
  progress?: number;
}

export interface GoalUpdate {
  title?: string | null;
  description?: string | null;
  status?: GoalStatus | null;
  priority?: GoalPriority | null;
  target_date?: string | null;
  progress?: number | null;
}

export interface GoalResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: GoalStatus;
  priority: GoalPriority;
  target_date: string | null;
  progress: number;
  created_at: string;
  updated_at: string;
}
