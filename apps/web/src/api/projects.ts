import { apiRequest } from "./client";
import type {
  ProjectCreate,
  ProjectResponse,
  ProjectUpdate,
} from "../types/project";

export function getProjects(userId: string): Promise<ProjectResponse[]> {
  return apiRequest<ProjectResponse[]>(
    `/projects?user_id=${encodeURIComponent(userId)}`,
  );
}

export function getProject(projectId: string): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/projects/${projectId}`);
}

export function createProject(
  data: ProjectCreate,
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateProject(
  projectId: string,
  data: ProjectUpdate,
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteProject(projectId: string): Promise<void> {
  return apiRequest<void>(`/projects/${projectId}`, {
    method: "DELETE",
  });
}
