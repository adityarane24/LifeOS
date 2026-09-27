export interface TaskAnalytics {
  created: number;
  completed: number;
  cancelled: number;
  reopened: number;
  completion_rate: number;
}

export interface GoalAnalytics {
  completed: number;
  progress_updates: number;
}

export interface HabitAnalytics {
  completed: number;
  missed: number;
  consistency_rate: number;
}

export interface ProjectAnalytics {
  completed: number;
  archived: number;
}

export interface UserAnalytics {
  total_events: number;
  tasks: TaskAnalytics;
  goals: GoalAnalytics;
  habits: HabitAnalytics;
  projects: ProjectAnalytics;
}
