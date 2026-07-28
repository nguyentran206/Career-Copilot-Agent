import type { CompletedAnalysis, FitLevel } from "@/types/analysis";
import { SkillList } from "./SkillList";

interface AnalysisResultProps {
  result: CompletedAnalysis;
}

const FIT_LEVEL_LABELS: Record<FitLevel, string> = {
  high: "High fit",
  medium: "Medium fit",
  low: "Low fit"
};

function TextList({
  items,
  emptyText,
  className
}: {
  items: string[];
  emptyText: string;
  className?: string;
}) {
  if (items.length === 0) {
    return <p>{emptyText}</p>;
  }

  return (
    <ul className={`text-list ${className ?? ""}`}>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function AnalysisResult({ result }: AnalysisResultProps) {
  const { analysis_result: analysis } = result;
  const parserWarnings = [
    ...result.cv_parse_result.warnings,
    ...(result.jd_parse_result?.warnings ?? [])
  ];

  return (
    <div className="result">
      <section className="card score-card">
        <div className="score-circle">{Math.round(analysis.fit_score)}</div>
        <div>
          <span className={`badge ${analysis.fit_level}`}>
            {FIT_LEVEL_LABELS[analysis.fit_level]}
          </span>
          <h2>Analysis completed</h2>
          <p className="hint">
            This fit score is decision support based on the submitted CV and JD, not a hiring decision or guarantee.
          </p>
        </div>
      </section>

      {parserWarnings.length > 0 ? (
        <section className="card section-card">
          <h3>Document warnings</h3>
          <TextList
            className="warning-list"
            items={parserWarnings}
            emptyText="No document warnings."
          />
        </section>
      ) : null}

      {analysis.analysis_warnings.length > 0 ? (
        <section className="card section-card">
          <h3>Analysis warnings</h3>
          <TextList
            className="warning-list"
            items={analysis.analysis_warnings}
            emptyText="No analysis warnings."
          />
        </section>
      ) : null}

      {analysis.score_adjustments.length > 0 ? (
        <section className="card section-card">
          <h3>Score guardrails</h3>
          <TextList
            items={analysis.score_adjustments.map((item) => item.reason)}
            emptyText="No score guardrails were applied."
          />
        </section>
      ) : null}

      <section className="card section-card">
        <h3>Matched skills</h3>
        <SkillList
          items={analysis.matched_skills}
          emptyText="No matched skills were detected yet."
        />
      </section>

      <section className="card section-card">
        <h3>Missing skills</h3>
        <SkillList
          items={analysis.missing_skills}
          variant="missing"
          emptyText="No missing skills were detected."
        />
      </section>

      <section className="card section-card">
        <h3>CV improvement suggestions</h3>
        <TextList
          items={analysis.cv_improvement_suggestions}
          emptyText="No specific suggestions were returned."
        />
      </section>

      {analysis.cover_letter ? (
        <section className="card section-card">
          <h3>Cover letter draft</h3>
          <p className="cover-letter">{analysis.cover_letter}</p>
        </section>
      ) : null}

      {analysis.learning_roadmap && analysis.learning_roadmap.length > 0 ? (
        <section className="card section-card">
          <h3>Learning roadmap</h3>
          <TextList
            items={analysis.learning_roadmap}
            emptyText="No learning roadmap was returned."
          />
        </section>
      ) : null}
    </div>
  );
}
