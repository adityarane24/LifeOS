import { apiRequest } from "./client";
import type {
  HabitAnalyticsResponse,
  HabitCompletionCreate,
  HabitCompletionResponse,
  HabitCreate,
  HabitResponse,
  HabitUpdate,
} from "../types/habit";

export function getHabits(userId: string): Promise<HabitResponse[]> {
  return apiRequest<HabitResponse[]>(
    `/habits?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getHabit(habitId: string): Promise<HabitResponse> {
  return apiRequest<HabitResponse>(`/habits/${habitId}`);
}

export function createHabit(data: HabitCreate): Promise<HabitResponse> {
  return apiRequest<HabitResponse>("/habits", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateHabit(
  habitId: string,
  data: HabitUpdate,
): Promise<HabitResponse> {
  return apiRequest<HabitResponse>(`/habits/${habitId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteHabit(habitId: string): Promise<void> {
  return apiRequest<void>(`/habits/${habitId}`, {
    method: "DELETE",
  });
}

export function getHabitAnalytics(
  habitId: string,
): Promise<HabitAnalyticsResponse> {
  return apiRequest<HabitAnalyticsResponse>(
    `/habits/${habitId}/analytics`,
  );
}

export function getHabitCompletions(
  habitId: string,
): Promise<HabitCompletionResponse[]> {
  return apiRequest<HabitCompletionResponse[]>(
    `/habits/${habitId}/completions`,
  );
}

export function createHabitCompletion(
  habitId: string,
  data: HabitCompletionCreate,
): Promise<HabitCompletionResponse> {
  return apiRequest<HabitCompletionResponse>(
    `/habits/${habitId}/completions`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}

export function deleteHabitCompletion(
  habitId: string,
  completionDate: string,
): Promise<void> {
  return apiRequest<void>(
    `/habits/${habitId}/completions/${encodeURIComponent(completionDate)}`,
    {
      method: "DELETE",
    },
  );
}
