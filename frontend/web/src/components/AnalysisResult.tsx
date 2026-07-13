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
  const { cv_parse_result: parseResult, analysis_result: analysis } = result;

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
            Parsed {parseResult.page_count} page(s), extracted{" "}
            {parseResult.text_length.toLocaleString()} characters from{" "}
            {parseResult.filename}.
          </p>
        </div>
      </section>

      {parseResult.warnings.length > 0 ? (
        <section className="card section-card">
          <h3>Parser warnings</h3>
          <TextList
            className="warning-list"
            items={parseResult.warnings}
            emptyText="No parser warnings."
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
