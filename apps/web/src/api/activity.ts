import { apiRequest } from "./client";
import type {
  ActivityEntityType,
  ActivityEventResponse,
} from "../types/activity";

export function getActivityTimeline(
  userId: string,
  limit = 100,
): Promise<ActivityEventResponse[]> {
  return apiRequest<ActivityEventResponse[]>(
    `/activity/timeline?user_id=${encodeURIComponent(userId)}&limit=${limit}`,
  );
}

export function getActivityRange(
  userId: string,
  start: string,
  end: string,
  limit = 1000,
): Promise<ActivityEventResponse[]> {
  const params = new URLSearchParams({
    user_id: userId,
    start,
    end,
    limit: String(limit),
  });

  return apiRequest<ActivityEventResponse[]>(
    `/activity/range?${params.toString()}`,
  );
}

export function getEntityHistory(
  entityType: ActivityEntityType,
  entityId: string,
  limit = 100,
): Promise<ActivityEventResponse[]> {
  return apiRequest<ActivityEventResponse[]>(
    `/activity/entity/${entityType}/${entityId}?limit=${limit}`,
  );
}

export function getActivitySummary(
  userId: string,
  start: string,
  end: string,
): Promise<unknown> {
  const params = new URLSearchParams({
    user_id: userId,
    start,
    end,
  });

  return apiRequest<unknown>(`/activity/summary?${params.toString()}`);
}
