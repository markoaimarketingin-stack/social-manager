import { isDemoModeEnabled, mockRequest } from "./mock";

const DEFAULT_API_BASE_URL = "";
const RAW_API_BASE_URL =
  localStorage.getItem("custom_backend_url") ||
  (import.meta.env.VITE_API_URL?.toString() ??
    import.meta.env.VITE_API_BASE_URL?.toString() ??
    DEFAULT_API_BASE_URL);

export const apiBaseUrl = RAW_API_BASE_URL.replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("auth_token");
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (isDemoModeEnabled()) {
    return mockRequest<T>(path, init);
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let errorMessage = `${init?.method ?? "GET"} ${path} failed`;
    try {
      const payload = await response.json();
      errorMessage = payload?.detail ?? payload?.error?.message ?? errorMessage;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(errorMessage, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  return request<TResponse>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function apiPut<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  return request<TResponse>(path, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function apiPatch<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  return request<TResponse>(path, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function apiDelete(path: string): Promise<void> {
  await request<void>(path, { method: "DELETE" });
}
