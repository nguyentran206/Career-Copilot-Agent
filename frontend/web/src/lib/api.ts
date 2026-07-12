import type {
  AnalysisSessionResponse,
  AnalyzeStartResponse
} from "@/types/analysis";
import { createApiError } from "./errors";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export async function startAnalysis(
  cvFile: File,
  jdText: string
): Promise<AnalyzeStartResponse> {
  const formData = new FormData();
  formData.append("cv_file", cvFile);
  formData.append("jd_text", jdText);

  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return (await response.json()) as AnalyzeStartResponse;
}

export async function getAnalysisSession(
  sessionId: string
): Promise<AnalysisSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/session/${sessionId}`, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return (await response.json()) as AnalysisSessionResponse;
}
