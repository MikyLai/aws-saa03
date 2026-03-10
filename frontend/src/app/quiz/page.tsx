"use client";

import { getQuestion, submitAttempt } from "@/lib/api";
import { AttemptResult, Question } from "@/types/quiz";
import { useEffect, useState } from "react";

type Language = "en" | "zh";

export default function QuizPage() {
  const [questionId, setQuestionId] = useState(11);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selectedChoiceIds, setSelectedChoiceIds] = useState<number[]>([]);
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [language, setLanguage] = useState<Language>("zh");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setError("");
        setResult(null);
        setSelectedChoiceIds([]);
        const data = await getQuestion(questionId);
        setQuestion(data);
      } catch (err) {
        setError("Failed to load question");
      }
    }
    load();
  }, [questionId]);

  function toggleChoice(choiceId: number) {
    if (!question) return;

    if (question.question_type === "single") {
      setSelectedChoiceIds([choiceId]);
      return;
    }

    setSelectedChoiceIds((prev) =>
      prev.includes(choiceId)
        ? prev.filter((id) => id !== choiceId)
        : [...prev, choiceId]
    );
  }

  async function handleSubmit() {
    if (!question) return;
    if (selectedChoiceIds.length === 0) return;

    try {
      setLoading(true);
      setError("");

      const data = await submitAttempt({
        user_id: "local",
        question_id: question.id,
        selected_choice_ids: selectedChoiceIds,
      });

      setResult(data);
    } catch (err) {
      setError("Failed to submit answer");
    } finally {
      setLoading(false);
    }
  }

  function getChoiceText(choice: Question["choices"][number]) {
    if (language === "zh") {
      return choice.text_zh || choice.text_en;
    }
    return choice.text_en;
  }

  function getStem() {
    if (!question) return "";
    return language === "zh" ? question.stem_zh || question.stem_en : question.stem_en;
  }

  function getExplanation() {
    if (!result) return "";
    return language === "zh"
      ? result.explanation_zh || result.explanation_en || ""
      : result.explanation_en || result.explanation_zh || "";
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <h1>AWS SAA Quiz</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => setLanguage("en")}>EN</button>
          <button onClick={() => setLanguage("zh")}>ZH</button>
        </div>
      </div>

      <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
        <button onClick={() => setQuestionId((id) => Math.max(1, id - 1))}>Previous</button>
        <button onClick={() => setQuestionId((id) => id + 1)}>Next</button>
        <a href="/summary" style={{ padding: "6px 12px", border: "1px solid #ccc" }}>
          View Summary
        </a>
      </div>

      {error && <p>{error}</p>}
      {!question && <p>Loading...</p>}

      {question && (
        <div style={{ border: "1px solid #ccc", borderRadius: 8, padding: 20 }}>
          <div style={{ marginBottom: 8, color: "#666" }}>
            Question {question.id} • {question.domain}
          </div>

          <h2 style={{ marginBottom: 20 }}>{getStem()}</h2>

          <div style={{ display: "grid", gap: 12 }}>
            {question.choices.map((choice) => {
              const checked = selectedChoiceIds.includes(choice.id);
              const isCorrect = result?.correct_choice_ids.includes(choice.id) ?? false;
              const isSelected = result?.selected_choice_ids.includes(choice.id) ?? false;

              let bg = "black";
              if (result && isCorrect) bg = "#eaf7ea";
              if (result && isSelected && !isCorrect) bg = "#fdecec";

              return (
                <label
                  key={choice.id}
                  style={{
                    display: "block",
                    border: "1px solid #ddd",
                    padding: 12,
                    borderRadius: 6,
                    background: bg,
                    cursor: "pointer",
                  }}
                >
                  <input
                    type={question.question_type === "single" ? "radio" : "checkbox"}
                    checked={checked}
                    onChange={() => toggleChoice(choice.id)}
                    disabled={!!result}
                    style={{ marginRight: 8 }}
                  />
                  <strong>{choice.label}.</strong> {getChoiceText(choice)}
                </label>
              );
            })}
          </div>

          {!result && (
            <button
              onClick={handleSubmit}
              disabled={loading || selectedChoiceIds.length === 0}
              style={{ marginTop: 20 }}
            >
              {loading ? "Submitting..." : "Submit"}
            </button>
          )}

          {result && (
            <div style={{ marginTop: 24 }}>
              <h3>{result.is_correct ? "Correct" : "Incorrect"}</h3>
              <p>Correct answer: {result.correct_labels.join(", ")}</p>
              <h4>Explanation</h4>
              <p>{getExplanation()}</p>
            </div>
          )}
        </div>
      )}
    </main>
  );
}