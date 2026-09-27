export type HabitFrequency =
  | "daily"
  | "weekly";

export interface HabitCreate {
  user_id: string;
  title: string;
  description?: string | null;
  frequency?: HabitFrequency;
  days_of_week?: unknown[] | null;
  target?: number;
  unit?: string;
  start_date?: string;
  is_active?: boolean;
}

export interface HabitUpdate {
  title?: string | null;
  description?: string | null;
  frequency?: HabitFrequency | null;
  days_of_week?: unknown[] | null;
  target?: number | null;
  unit?: string | null;
  start_date?: string | null;
  is_active?: boolean | null;
}

export interface HabitResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  frequency: HabitFrequency;
  days_of_week: unknown[] | null;
  target: number;
  unit: string;
  start_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface HabitCompletionCreate {
  completion_date: string;
  value?: number;
  completed?: boolean;
}

export interface HabitCompletionResponse {
  id: string;
  habit_id: string;
  completion_date: string;
  value: number;
  completed: boolean;
  created_at: string;
}

export interface HabitAnalyticsResponse {
  habit_id: string;
  current_streak: number;
  longest_streak: number;
  completion_rate: number;
}
