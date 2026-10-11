// frontend/app/api/client.ts
/** Shared API client that automatically sends cookies for authentication. */
export async function api<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const resp = await fetch(path, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });
  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`API error ${resp.status}: ${txt}`);
  }
  return (await resp.json()) as T;
}
