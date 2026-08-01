import { AnalyzeForm } from "@/components/AnalyzeForm";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Career Copilot Agent</p>
        <h1>Analyze your CV against a Job Description</h1>
        <p className="hero-copy">
          Upload a CV PDF, then paste the JD or upload a text-based JD PDF to get
          a fit score, matched and missing skills, improvement suggestions, and
          the next recommended action.
        </p>
      </section>

      <AnalyzeForm />
    </main>
  );
}
