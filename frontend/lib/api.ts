const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Shared types
// ---------------------------------------------------------------------------

export interface Source {
  filename: string;
  chunk_index: number;
  excerpt: string;
  score: number | null;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface UploadResponse {
  job_id: string;
  filenames: string[];
}

export interface IndexStatusResponse {
  job_id: string;
  status: "uploaded" | "indexing" | "done" | "error";
  chunks_added: number;
  error: string;
}

// ---------------------------------------------------------------------------
// API client
// ---------------------------------------------------------------------------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export async function ask(sessionId: string, message: string): Promise<AskResponse> {
  return request<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f, f.name));
  const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<UploadResponse>;
}

export async function indexDocuments(jobId: string): Promise<void> {
  await request("/index", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId }),
  });
}

export async function getIndexStatus(jobId: string): Promise<IndexStatusResponse> {
  return request<IndexStatusResponse>(`/index/status/${jobId}`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/session/${sessionId}`, { method: "DELETE" });
}

/**
 * Upload files then kick off indexing. Calls onProgress repeatedly until done.
 * Returns the number of chunks added, or throws on error.
 */
export async function uploadAndIndex(
  files: File[],
  onProgress: (status: IndexStatusResponse) => void,
): Promise<number> {
  const { job_id } = await uploadFiles(files);
  await indexDocuments(job_id);

  return new Promise((resolve, reject) => {
    const iv = setInterval(async () => {
      try {
        const status = await getIndexStatus(job_id);
        onProgress(status);
        if (status.status === "done") {
          clearInterval(iv);
          resolve(status.chunks_added);
        } else if (status.status === "error") {
          clearInterval(iv);
          reject(new Error(status.error || "Indexing failed"));
        }
      } catch (err) {
        clearInterval(iv);
        reject(err);
      }
    }, 800);
  });
}
