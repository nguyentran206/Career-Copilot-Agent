import type { SessionError } from "@/types/analysis";

export class AppApiError extends Error {
  code: string;
  detail?: unknown;

  constructor(code: string, message: string, detail?: unknown) {
    super(message);
    this.name = "AppApiError";
    this.code = code;
    this.detail = detail;
  }
}

const FRIENDLY_MESSAGES: Record<string, string> = {
  CV_FILE_TOO_LARGE: "CV PDF is too large. Please upload a smaller file.",
  CV_FILE_NOT_PDF: "Please upload the CV as a PDF file.",
  EMPTY_CV_FILE: "The uploaded CV file is empty. Please choose another PDF.",
  JD_INPUT_REQUIRED: "Please paste a Job Description or upload a JD PDF.",
  JD_INPUT_CONFLICT: "Choose either JD text or a JD PDF, not both.",
  JD_TEXT_REQUIRED: "Please provide a Job Description before starting analysis.",
  JD_TEXT_TOO_SHORT: "The Job Description is too short for a useful analysis.",
  JD_TEXT_TOO_LONG: "The Job Description is too long. Please shorten it and try again.",
  JD_FILE_NOT_PDF: "Please upload the Job Description as a PDF file.",
  EMPTY_JD_FILE: "The uploaded Job Description PDF is empty.",
  JD_FILE_TOO_LARGE: "The Job Description PDF is too large. Please upload a smaller file.",
  DOCUMENT_PARSER_UNAVAILABLE:
    "Document Parser Service is unavailable. Please start it and try again.",
  DOCUMENT_PARSER_TIMEOUT:
    "PDF parsing took too long. Please try another text-based PDF.",
  DOCUMENT_PARSER_ERROR:
    "A document could not be parsed. If it is scanned, try a text-based PDF.",
  DOCUMENT_PARSER_INVALID_RESPONSE:
    "Document Parser Service returned an unexpected response.",
  CV_TEXT_TOO_SHORT:
    "The CV text is too short after parsing. The PDF may be scanned or image-based.",
  AGENT_SERVICE_UNAVAILABLE:
    "Agent Service is unavailable. Please start it and try again.",
  AGENT_SERVICE_TIMEOUT:
    "The analysis took longer than expected. Please try again.",
  AGENT_SERVICE_ERROR: "Agent Service could not complete the analysis.",
  AGENT_SERVICE_INVALID_RESPONSE:
    "Agent Service returned an unexpected analysis response.",
  ANALYSIS_FAILED: "Analysis failed unexpectedly. Please try again.",
  SESSION_NOT_FOUND:
    "This temporary analysis session has expired or is no longer available. Please run the analysis again.",
  SESSION_CAPACITY_REACHED:
    "Temporary session storage is full. Please wait briefly and try again.",
  ANALYZE_RATE_LIMITED:
    "You have started too many analyses recently. Please wait and try again.",
  ANALYSIS_CAPACITY_REACHED:
    "All analysis slots are currently busy. Please retry shortly."
};

interface FastApiErrorPayload {
  detail?: unknown;
  error?: SessionError;
  code?: string;
  message?: string;
}

function extractError(payload: FastApiErrorPayload | null): SessionError | null {
  if (!payload) return null;

  if (payload.error?.code) {
    return payload.error;
  }

  if (
    payload.detail &&
    typeof payload.detail === "object" &&
    "code" in payload.detail &&
    "message" in payload.detail
  ) {
    return payload.detail as SessionError;
  }

  if (payload.code && payload.message) {
    return {
      code: payload.code,
      message: payload.message,
      detail: payload.detail
    };
  }

  return null;
}

export function toFriendlyMessage(error: unknown): string {
  if (error instanceof AppApiError) {
    return FRIENDLY_MESSAGES[error.code] ?? error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

export function sessionErrorToAppError(error: SessionError): AppApiError {
  return new AppApiError(
    error.code,
    FRIENDLY_MESSAGES[error.code] ?? error.message,
    error.detail
  );
}

export async function createApiError(response: Response): Promise<AppApiError> {
  let payload: FastApiErrorPayload | null = null;

  try {
    payload = (await response.json()) as FastApiErrorPayload;
  } catch {
    payload = null;
  }

  const extracted = extractError(payload);

  if (extracted) {
    return sessionErrorToAppError(extracted);
  }

  return new AppApiError(
    `HTTP_${response.status}`,
    `Request failed with status ${response.status}.`
  );
}
