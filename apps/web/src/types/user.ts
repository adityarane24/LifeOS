export interface UserCreate {
  email: string;
  name: string;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
}
