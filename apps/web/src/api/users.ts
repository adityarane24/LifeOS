import { apiRequest } from "./client";
import type { UserCreate, UserResponse } from "../types/user";

export function createUser(data: UserCreate): Promise<UserResponse> {
  return apiRequest<UserResponse>("/users", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
