import { getSummary } from "@/lib/api";

export default async function SummaryPage() {
  const summary = await getSummary("local");

  return (
    <main style={{ maxWidth: 1000, margin: "0 auto", padding: 24 }}>
      <h1>Result Summary</h1>

      <div style={{ marginBottom: 24 }}>
        <h2>{summary.overall_percentage}%</h2>
        <p>
          {summary.total_correct} correct • {summary.total_incorrect} incorrect •{" "}
          {summary.total_unanswered} unanswered
        </p>
        <p>
          Answered {summary.total_answered} / {summary.total_questions}
        </p>
      </div>

      <h3>Topic scores</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
        {summary.by_domain.map((item) => (
          <div
            key={item.domain}
            style={{
              border: "1px solid #ddd",
              borderRadius: 8,
              padding: 16,
            }}
          >
            <div style={{ marginBottom: 8 }}>{item.domain}</div>
            <div style={{ fontSize: 28, fontWeight: 600 }}>{item.percentage}%</div>
            <div>
              {item.correct}/{item.answered}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 24 }}>
        <a href="/quiz">Back to Quiz</a>
      </div>
    </main>
  );
}