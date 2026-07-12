export type SessionStatus = "processing" | "completed" | "failed";

export type FitLevel = "high" | "medium" | "low";

export type MatchLevel = "strong" | "partial" | "missing";

export interface AnalyzeStartResponse {
  session_id: string;
  status: "processing";
}

export interface SessionError {
  code: string;
  message: string;
  detail?: unknown;
}

export interface CvParseResult {
  filename: string;
  document_type: string | null;
  content_type: string | null;
  file_size_bytes: number;
  page_count: number;
  text_length: number;
  warnings: string[];
}

export interface ScoreBreakdown {
  required_skill_score: number;
  preferred_skill_score: number;
  experience_relevance_score: number;
  project_domain_relevance_score: number;
  education_cert_tool_score: number;
}

export interface ParsedCv {
  skills: string[];
  experience_summary: string | null;
  projects: string[];
  education: string[];
  certifications: string[];
}

export interface ParsedJd {
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  domain_keywords: string[];
}

export interface SkillMatch {
  jd_skill: string;
  resume_skill: string | null;
  similarity: number;
  match_level: MatchLevel;
  importance: number;
}

export interface AnalysisResult {
  fit_score: number;
  fit_level: FitLevel;
  score_breakdown: ScoreBreakdown;
  parsed_cv: ParsedCv;
  parsed_jd: ParsedJd;
  skill_matches: SkillMatch[];
  matched_skills: string[];
  missing_skills: string[];
  cv_improvement_suggestions: string[];
  cover_letter: string | null;
  learning_roadmap: string[] | null;
}

export interface CompletedAnalysis {
  cv_parse_result: CvParseResult;
  analysis_result: AnalysisResult;
}

export interface AnalysisSessionResponse {
  session_id: string;
  status: SessionStatus;
  result: CompletedAnalysis | null;
  error: SessionError | null;
}
