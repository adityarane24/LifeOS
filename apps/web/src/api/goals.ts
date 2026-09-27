import { apiRequest } from "./client";
import type {
  GoalCreate,
  GoalResponse,
  GoalUpdate,
} from "../types/goal";

export function getGoals(userId: string): Promise<GoalResponse[]> {
  return apiRequest<GoalResponse[]>(
    `/goals?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getGoal(goalId: string): Promise<GoalResponse> {
  return apiRequest<GoalResponse>(`/goals/${goalId}`);
}

export function createGoal(data: GoalCreate): Promise<GoalResponse> {
  return apiRequest<GoalResponse>("/goals", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateGoal(
  goalId: string,
  data: GoalUpdate,
): Promise<GoalResponse> {
  return apiRequest<GoalResponse>(`/goals/${goalId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteGoal(goalId: string): Promise<void> {
  return apiRequest<void>(`/goals/${goalId}`, {
    method: "DELETE",
  });
}
