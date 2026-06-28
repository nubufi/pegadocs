export type AuthUser = {
  userId: string;
  email: string;
  name: string | null;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type AuthResponse = {
  user_id: string;
  email: string;
  name?: string | null;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
  name: string;
  phone: string;
  reference_code?: string;
  company?: string;
};

export type RegisterResponse = {
  user_id: string;
  email: string;
  message: string;
};

export type RefreshTokenRequest = {
  refresh_token: string;
};

export type RefreshTokenResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ResetPasswordRequest = {
  access_token: string;
  new_password: string;
};

export type MessageResponse = {
  message: string;
};

export type ApiErrorDetail = {
  code?: string;
  message?: string;
  type?: string;
};

export type ApiErrorResponse = {
  error?: ApiErrorDetail;
  detail?: string;
  message?: string;
};
