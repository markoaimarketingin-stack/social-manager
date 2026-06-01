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
  const response = await apiFetch(path, init);

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

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  const requestInit = {
    ...init,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...getAuthHeaders(),
      ...(init?.headers ?? {}),
    },
  } satisfies RequestInit;

  try {
    return await fetch(`${apiBaseUrl}${path}`, requestInit);
  } catch (error) {
    if (!apiBaseUrl) throw error;
    return fetch(path, requestInit);
  }
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
