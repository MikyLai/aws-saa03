import { AttemptResult, AttemptSummary, Question } from "@/types/quiz";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function getQuestion(questionId: number): Promise<Question> {
  const res = await fetch(`${API_BASE}/questions/${questionId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch question ${questionId}`);
  }

  return res.json();
}

export async function submitAttempt(payload: {
  user_id: string;
  question_id: number;
  selected_choice_ids: number[];
}): Promise<AttemptResult> {
  const res = await fetch(`${API_BASE}/attempts/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Failed to submit attempt`);
  }

  return res.json();
}

export async function getSummary(userId: string): Promise<AttemptSummary> {
  const res = await fetch(`${API_BASE}/attempts/summary?user_id=${userId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch summary");
  }

  return res.json();
}