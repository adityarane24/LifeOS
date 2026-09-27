import { apiRequest } from "./client";
import type { UserAnalytics } from "../types/analytics";

/**
 * Fetch personal activity analytics for a user
 * within the requested time range.
 */
export async function getUserAnalytics(
  userId: string,
  start: string,
  end: string,
): Promise<UserAnalytics> {
  const params = new URLSearchParams({
    user_id: userId,
    start,
    end,
  });

  return apiRequest<UserAnalytics>(`/analytics?${params.toString()}`);
}
