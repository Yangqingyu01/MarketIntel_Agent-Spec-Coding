import { useState, type CSSProperties } from "react";

import { analyzeCompetitors, type AnalyzeResponse } from "../services/api";

const DIMENSIONS = ["product", "pricing", "funding", "talent", "strategy"];

export function ChatInterface() {
  const [targetInput, setTargetInput] = useState("飞书");
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(["product", "strategy"]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    try {
      const targets = targetInput
        .split(/[，,]/)
        .map((item) => item.trim())
        .filter(Boolean);
      const response = await analyzeCompetitors({
        targets,
        dimensions: selectedDimensions,
        time_range: "近3个月",
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "分析失败");
    } finally {
      setLoading(false);
    }
  }

  function toggleDimension(dimension: string) {
    setSelectedDimensions((current) =>
      current.includes(dimension)
        ? current.filter((item) => item !== dimension)
        : [...current, dimension]
    );
  }

  return (
    <section style={panelStyle}>
      <h2 style={titleStyle}>市场情报对话台</h2>
      <p style={mutedStyle}>输入一个或多个竞品名称，快速发起分析。</p>
      <textarea
        value={targetInput}
        onChange={(event) => setTargetInput(event.target.value)}
        rows={3}
        style={textareaStyle}
      />
      <div style={chipGroupStyle}>
        {DIMENSIONS.map((dimension) => (
          <button
            key={dimension}
            type="button"
            onClick={() => toggleDimension(dimension)}
            style={{
              ...chipStyle,
              background: selectedDimensions.includes(dimension) ? "#1746a2" : "#f4f6fb",
              color: selectedDimensions.includes(dimension) ? "#fff" : "#1746a2",
            }}
          >
            {dimension}
          </button>
        ))}
      </div>
      <button type="button" onClick={handleAnalyze} disabled={loading} style={buttonStyle}>
        {loading ? "分析中..." : "开始分析"}
      </button>
      {error ? <p style={errorStyle}>{error}</p> : null}
      {result ? (
        <div style={resultStyle}>
          <h3 style={subtitleStyle}>{result.report.target}</h3>
          <p>{result.report.executive_summary}</p>
          <p>{result.report.changes_summary}</p>
          <p>结构化情报数：{result.intel_count}</p>
        </div>
      ) : null}
    </section>
  );
}

const panelStyle: CSSProperties = {
  padding: "24px",
  borderRadius: "24px",
  background: "linear-gradient(145deg, #fff9f0, #eef6ff)",
  boxShadow: "0 20px 60px rgba(23, 70, 162, 0.12)",
};

const titleStyle: CSSProperties = {
  margin: 0,
  fontSize: "28px",
  color: "#1f2a44",
};

const subtitleStyle: CSSProperties = {
  marginBottom: "8px",
  color: "#1f2a44",
};

const mutedStyle: CSSProperties = {
  color: "#5e6983",
};

const textareaStyle: CSSProperties = {
  width: "100%",
  marginTop: "12px",
  padding: "14px 16px",
  borderRadius: "16px",
  border: "1px solid #cfd7ea",
  resize: "vertical",
  fontSize: "15px",
};

const chipGroupStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
  marginTop: "16px",
  marginBottom: "16px",
};

const chipStyle: CSSProperties = {
  border: "none",
  borderRadius: "999px",
  padding: "10px 14px",
  cursor: "pointer",
};

const buttonStyle: CSSProperties = {
  padding: "12px 18px",
  borderRadius: "14px",
  border: "none",
  background: "#e85d04",
  color: "#fff",
  cursor: "pointer",
  fontWeight: 600,
};

const resultStyle: CSSProperties = {
  marginTop: "18px",
  padding: "18px",
  borderRadius: "18px",
  background: "#fff",
};

const errorStyle: CSSProperties = {
  color: "#b42318",
};
