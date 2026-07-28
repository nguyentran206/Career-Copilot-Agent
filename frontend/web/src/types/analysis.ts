export type SessionStatus = "processing" | "completed" | "failed";

export type FitLevel = "high" | "medium" | "low";

export type MatchLevel = "strong" | "partial" | "missing";
export type SkillPriority = "required" | "preferred" | "unknown";
export type MatchType = "exact" | "alias" | "taxonomy" | "semantic" | "none";

export interface AnalyzeStartResponse {
  session_id: string;
  status: "processing";
}

export interface SessionError {
  code: string;
  message: string;
  detail?: unknown;
}

export interface DocumentParseResult {
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
  project_relevance_score: number;
  education_cert_relevance_score: number;
  unknown_skill_score: number;
  skill_coverage_score: number;
  component_weights: ComponentWeight[];
}

export interface ComponentWeight {
  component: string;
  configured_weight: number;
  enabled: boolean;
  effective_weight: number;
}

export interface ParsedCv {
  language_info: LanguageInfo;
  skills: string[];
  experience_summary: string | null;
  experience_evidence: string[];
  projects: string[];
  education: string[];
  certifications: string[];
  localized_evidence: LocalizedEvidence[];
}

export interface ParsedJd {
  language_info: LanguageInfo;
  required_skills: string[];
  preferred_skills: string[];
  unknown_skills: string[];
  skill_requirements: JdSkillRequirement[];
  job_title: string | null;
  responsibilities: string[];
  experience_requirements: string[];
  project_requirements: string[];
  education_requirements: string[];
  domain_keywords: string[];
}

export interface LanguageInfo {
  primary_language: string;
  detected_languages: string[];
  is_mixed_language: boolean;
  confidence: number;
}

export interface LocalizedEvidence {
  source_language: string;
  english_text: string | null;
}

export interface JdSkillRequirement {
  skill: string;
  classification: SkillPriority;
  critical: boolean;
  evidence: string | null;
  english_evidence: string | null;
  base_weight: number;
}

export interface SkillMatch {
  jd_skill: string;
  resume_skill: string | null;
  similarity: number;
  match_level: MatchLevel;
  importance: number;
  classification: SkillPriority;
  match_type: MatchType;
  evidence_score: number;
}

export interface SkillWeightSource {
  skill: string;
  jd_classification: SkillPriority;
  jd_base_weight: number;
  final_weight: number;
  cv_evidence_score: number;
  contribution: number;
}

export interface ScoreAdjustment {
  rule: string;
  reason: string;
  score_before: number;
  score_after: number;
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
  raw_fit_score: number;
  score_confidence: number;
  scoring_version: string;
  skill_weight_sources: SkillWeightSource[];
  score_adjustments: ScoreAdjustment[];
  analysis_warnings: string[];
}

export interface CompletedAnalysis {
  cv_parse_result: DocumentParseResult;
  jd_parse_result: DocumentParseResult | null;
  analysis_result: AnalysisResult;
}

export interface AnalysisSessionResponse {
  session_id: string;
  status: SessionStatus;
  result: CompletedAnalysis | null;
  error: SessionError | null;
  expires_at: string;
}
