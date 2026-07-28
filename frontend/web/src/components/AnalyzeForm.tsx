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
const POLL_INTERVAL_MS = 1500;
const SESSION_TIMEOUT_MS = 240_000;
const MAX_POLL_ATTEMPTS = Math.ceil(
  SESSION_TIMEOUT_MS / POLL_INTERVAL_MS
);
type JdInputMode = "text" | "pdf";

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function isPdf(file: File) {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

function validateInput(
  cvFile: File | null,
  jdMode: JdInputMode,
  jdText: string,
  jdFile: File | null
) {
  if (!cvFile) {
    throw new AppApiError("CV_REQUIRED", "Please upload a CV PDF.");
  }

  if (!isPdf(cvFile)) {
    throw new AppApiError("CV_FILE_NOT_PDF", "Please upload a PDF file.");
  }

  if (jdMode === "pdf") {
    if (!jdFile) {
      throw new AppApiError("JD_INPUT_REQUIRED", "Please upload a JD PDF.");
    }
    if (!isPdf(jdFile)) {
      throw new AppApiError("JD_FILE_NOT_PDF", "Please upload a JD PDF.");
    }
    return;
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
  const [jdMode, setJdMode] = useState<JdInputMode>("text");
  const [jdText, setJdText] = useState("");
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [result, setResult] = useState<CompletedAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fileInputKey, setFileInputKey] = useState(0);

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

  async function runCurrentAnalysis() {
    setError(null);
    setResult(null);

    try {
      validateInput(cvFile, jdMode, jdText, jdFile);
      setIsSubmitting(true);

      const started = await startAnalysis(
        cvFile as File,
        jdMode === "text" ? jdText.trim() : null,
        jdMode === "pdf" ? jdFile : null
      );

      await pollUntilFinished(started.session_id);
    } catch (caughtError) {
      setError(toFriendlyMessage(caughtError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runCurrentAnalysis();
  }

  function clearAnalysis() {
    setCvFile(null);
    setJdMode("text");
    setJdText("");
    setJdFile(null);
    setResult(null);
    setError(null);
    setFileInputKey((value) => value + 1);
  }

  return (
    <div className="workspace">
      <section className="card panel">
        <h2>Start analysis</h2>
        <p className="hint">
          Frontend sends the request only to API Gateway. Document Parser and
          Agent Service stay internal behind the backend flow.
        </p>
        <p className="privacy-note">
          Privacy: your CV and JD are processed only to produce this result. The
          Gateway keeps the temporary session in memory for about 30 minutes;
          it is not saved to an account or application database and can disappear
          sooner if the backend restarts.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="cv_file">CV PDF</label>
            <input
              id="cv_file"
              key={fileInputKey}
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
            <fieldset className="input-mode">
              <legend>Job Description</legend>
              <label>
                <input
                  type="radio"
                  name="jd_mode"
                  value="text"
                  checked={jdMode === "text"}
                  onChange={() => {
                    setJdMode("text");
                    setJdFile(null);
                  }}
                  disabled={isSubmitting}
                />
                Paste text
              </label>
              <label>
                <input
                  type="radio"
                  name="jd_mode"
                  value="pdf"
                  checked={jdMode === "pdf"}
                  onChange={() => {
                    setJdMode("pdf");
                    setJdText("");
                  }}
                  disabled={isSubmitting}
                />
                Upload PDF
              </label>
            </fieldset>

            {jdMode === "text" ? (
              <>
                <textarea
                  id="jd_text"
                  className="textarea"
                  value={jdText}
                  onChange={(event) => setJdText(event.target.value)}
                  placeholder="Paste the full Job Description here..."
                  disabled={isSubmitting}
                />
                <p className="hint">Minimum {MIN_JD_LENGTH} characters.</p>
              </>
            ) : (
              <>
                <input
                  id="jd_file"
                  key={`jd-${fileInputKey}`}
                  className="file-input"
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(event) => setJdFile(event.target.files?.item(0) ?? null)}
                  disabled={isSubmitting}
                />
                <p className="hint">Use a text-based JD PDF for best results.</p>
              </>
            )}
          </div>

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Analyzing..." : "Analyze CV"}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={clearAnalysis}
            disabled={isSubmitting || (!cvFile && !jdText && !jdFile && !result && !error)}
          >
            Clear
          </button>
        </form>
      </section>

      <section>
        {error ? (
          <div className="error-actions">
            <ErrorMessage message={error} />
            <button className="secondary-button" type="button" onClick={runCurrentAnalysis}>
              Retry analysis
            </button>
          </div>
        ) : null}

        {isSubmitting ? (
          <StatusCard
            title="Analysis is running"
            description="We are reading your documents and comparing the CV with the Job Description."
            showSpinner
          />
        ) : null}

        {!isSubmitting && !error && !result ? (
          <StatusCard
            title="Ready when you are"
            description="Upload a CV PDF, then paste a Job Description or upload a JD PDF."
          />
        ) : null}

        {result ? <AnalysisResult result={result} /> : null}
      </section>
    </div>
  );
}
