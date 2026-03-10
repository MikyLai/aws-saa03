export type Choice = {
  id: number;
  label: string;
  text_en: string;
  text_zh: string | null;
};

export type Question = {
  id: number;
  stem_en: string;
  stem_zh: string | null;
  explanation_en: string | null;
  explanation_zh: string | null;
  difficulty: number;
  domain: string | null;
  question_type: "single" | "multi";
  active: boolean;
  created_at: string;
  choices: Choice[];
  answer_labels: string[];
};

export type AttemptResult = {
  question_id: number;
  user_id: string;
  selected_choice_ids: number[];
  is_correct: boolean;
  correct_choice_ids: number[];
  correct_labels: string[];
  domain: string | null;
  explanation_en: string | null;
  explanation_zh: string | null;
};

export type DomainScore = {
  domain: string;
  answered: number;
  correct: number;
  incorrect: number;
  percentage: number;
};

export type AttemptSummary = {
  user_id: string;
  total_questions: number;
  total_answered: number;
  total_correct: number;
  total_incorrect: number;
  total_unanswered: number;
  overall_percentage: number;
  by_domain: DomainScore[];
};