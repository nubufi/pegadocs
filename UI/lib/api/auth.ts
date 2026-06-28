import type {
  ApiErrorResponse,
  AuthResponse,
  ForgotPasswordRequest,
  LoginRequest,
  MessageResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  RegisterRequest,
  RegisterResponse,
  ResetPasswordRequest,
} from "@/types/auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export class ApiError extends Error {
  code?: string;
  status: number;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<TResponse>(
  path: string,
  init: RequestInit,
): Promise<TResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });
  } catch {
    throw new ApiError("Unable to reach the PegaDocs API.", 0, "NETWORK_ERROR");
  }

  const payload = (await response.json().catch(() => ({}))) as
    | TResponse
    | ApiErrorResponse;

  if (!response.ok) {
    const errorPayload = payload as ApiErrorResponse;
    const message =
      errorPayload.error?.message ??
      errorPayload.detail ??
      errorPayload.message ??
      "Request failed.";
    throw new ApiError(message, response.status, errorPayload.error?.code);
  }

  return payload as TResponse;
}

export const authApi = {
  login(input: LoginRequest) {
    return request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  register(input: RegisterRequest) {
    return request<RegisterResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  resendEmail(email: string) {
    return request<MessageResponse>("/auth/resend-email", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },

  forgotPassword(input: ForgotPasswordRequest) {
    return request<MessageResponse>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  resetPassword(input: ResetPasswordRequest) {
    return request<MessageResponse>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  refresh(input: RefreshTokenRequest) {
    return request<RefreshTokenResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },
};
