export type ActivityEventType =
  | "task_created"
  | "task_updated"
  | "task_completed"
  | "task_cancelled"
  | "task_reopened"
  | "goal_created"
  | "goal_updated"
  | "goal_completed"
  | "goal_progress_updated"
  | "goal_cancelled"
  | "habit_created"
  | "habit_updated"
  | "habit_completed"
  | "habit_missed"
  | "habit_deactivated"
  | "project_created"
  | "project_updated"
  | "project_completed"
  | "project_archived"
  | "user_created";

export type ActivityEntityType =
  | "task"
  | "goal"
  | "habit"
  | "project"
  | "user";

export interface ActivityEventResponse {
  id: string;
  user_id: string;
  event_type: ActivityEventType;
  entity_type: ActivityEntityType;
  entity_id: string;
  occurred_at: string;
  event_metadata: Record<string, unknown> | null;
  created_at: string;
}
