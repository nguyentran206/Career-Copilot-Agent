"use client";

import { FormEvent, useState } from "react";
import { getAnalysisSession, startAnalysis } from "@/lib/api";
import {
  AppApiError,
  sessionErrorToAppError,
  toFriendlyMessage
} from "@/lib/errors";
import type { CompletedAnalysis } from "@/types/analysis";
import { AnalysisResult } from "./AnalysisResult";
import { ErrorMessage } from "./ErrorMessage";
import { StatusCard } from "./StatusCard";

const MIN_JD_LENGTH = 50;
const MAX_POLL_ATTEMPTS = 120;
const POLL_INTERVAL_MS = 1500;

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function validateInput(cvFile: File | null, jdText: string) {
  if (!cvFile) {
    throw new AppApiError("CV_REQUIRED", "Please upload a CV PDF.");
  }

  const isPdf =
    cvFile.type === "application/pdf" ||
    cvFile.name.toLowerCase().endsWith(".pdf");

  if (!isPdf) {
    throw new AppApiError("CV_NOT_PDF", "Please upload a PDF file.");
  }

  if (jdText.trim().length < MIN_JD_LENGTH) {
    throw new AppApiError(
      "JD_TEXT_TOO_SHORT",
      "The Job Description is too short for a useful analysis."
    );
  }
}

export function AnalyzeForm() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<CompletedAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function pollUntilFinished(nextSessionId: string) {
    for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
      const session = await getAnalysisSession(nextSessionId);

      if (session.status === "completed" && session.result) {
        setResult(session.result);
        return;
      }

      if (session.status === "failed") {
        if (session.error) {
          throw sessionErrorToAppError(session.error);
        }

        throw new AppApiError("ANALYSIS_FAILED", "Analysis failed.");
      }

      await delay(POLL_INTERVAL_MS);
    }

    throw new AppApiError(
      "SESSION_TIMEOUT",
      "Analysis is taking longer than expected. Please check the session again later."
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setResult(null);
    setSessionId(null);

    try {
      validateInput(cvFile, jdText);
      setIsSubmitting(true);

      const started = await startAnalysis(cvFile as File, jdText.trim());
      setSessionId(started.session_id);

      await pollUntilFinished(started.session_id);
    } catch (caughtError) {
      setError(toFriendlyMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="workspace">
      <section className="card panel">
        <h2>Start analysis</h2>
        <p className="hint">
          Frontend sends the request only to API Gateway. Document Parser and
          Agent Service stay internal behind the backend flow.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="cv_file">CV PDF</label>
            <input
              id="cv_file"
              className="file-input"
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) =>
                setCvFile(event.target.files?.item(0) ?? null)
              }
              disabled={isSubmitting}
            />
            <p className="hint">Use a text-based PDF for best parser results.</p>
          </div>

          <div className="field">
            <label htmlFor="jd_text">Job Description</label>
            <textarea
              id="jd_text"
              className="textarea"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
              placeholder="Paste the full Job Description here..."
              disabled={isSubmitting}
            />
            <p className="hint">
              Minimum {MIN_JD_LENGTH} characters. JD remains the primary source
              of truth for analysis.
            </p>
          </div>

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Analyzing..." : "Analyze CV"}
          </button>
        </form>
      </section>

      <section>
        {error ? <ErrorMessage message={error} /> : null}

        {isSubmitting ? (
          <StatusCard
            title="Analysis is running"
            description={
              sessionId
                ? `Session ${sessionId} is processing. The UI is polling the API Gateway.`
                : "Starting an analysis session through the API Gateway."
            }
            showSpinner
          />
        ) : null}

        {!isSubmitting && !error && !result ? (
          <StatusCard
            title="Ready when you are"
            description="Upload a CV PDF and paste a JD to run the first frontend-to-backend MVP flow."
          />
        ) : null}

        {result ? <AnalysisResult result={result} /> : null}
      </section>
    </div>
  );
}
