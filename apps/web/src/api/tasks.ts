import { apiRequest } from "./client";
import type {
  TaskCreate,
  TaskResponse,
  TaskUpdate,
} from "../types/task";

export function getTasks(userId: string): Promise<TaskResponse[]> {
  return apiRequest<TaskResponse[]>(
    `/tasks?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getTask(taskId: string): Promise<TaskResponse> {
  return apiRequest<TaskResponse>(`/tasks/${taskId}`);
}

export function createTask(data: TaskCreate): Promise<TaskResponse> {
  return apiRequest<TaskResponse>("/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateTask(
  taskId: string,
  data: TaskUpdate,
): Promise<TaskResponse> {
  return apiRequest<TaskResponse>(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteTask(taskId: string): Promise<void> {
  return apiRequest<void>(`/tasks/${taskId}`, {
    method: "DELETE",
  });
}
