import { useState, type CSSProperties } from "react";

import { analyzeCompetitors, type AnalyzeResponse } from "../services/api";

const DIMENSIONS = ["product", "pricing", "funding", "talent", "strategy"];

const STAGES = ["目标识别", "公开搜索", "页面抓取", "信息提取", "结构化报告"];

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
      <div style={heroStyle}>
        <div>
          <p style={eyebrowStyle}>MarketIntel Console</p>
          <h2 style={titleStyle}>市场情报对话台</h2>
          <p style={mutedStyle}>输入一个或多个竞品名称，快速发起分析并返回结构化结论。</p>
        </div>
        <div style={statusCardStyle}>
          <span style={statusLabelStyle}>当前模式</span>
          <strong>{loading ? "执行中" : "待命"}</strong>
        </div>
      </div>
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
      <div style={progressRowStyle}>
        {STAGES.map((stage, index) => (
          <div key={stage} style={progressItemStyle}>
            <div
              style={{
                ...progressDotStyle,
                background: loading || result ? "#e85d04" : "#d0d5dd",
                opacity: !loading && !result && index > 0 ? 0.5 : 1,
              }}
            />
            <span style={progressTextStyle}>{stage}</span>
          </div>
        ))}
      </div>
      {error ? <p style={errorStyle}>{error}</p> : null}
      {result ? (
        <div style={resultStyle}>
          <div style={resultHeaderStyle}>
            <h3 style={subtitleStyle}>{result.report.target}</h3>
            <span style={metricStyle}>情报 {result.intel_count}</span>
          </div>
          <p>{result.report.executive_summary}</p>
          <p>{result.report.changes_summary}</p>
        </div>
      ) : null}
    </section>
  );
}

const panelStyle: CSSProperties = {
  padding: "28px",
  borderRadius: "28px",
  background:
    "radial-gradient(circle at top right, rgba(232,93,4,0.22), transparent 24%), linear-gradient(145deg, #fff8ef, #eef6ff)",
  boxShadow: "0 24px 70px rgba(23, 70, 162, 0.14)",
};

const heroStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: "16px",
  flexWrap: "wrap",
  alignItems: "flex-start",
};

const eyebrowStyle: CSSProperties = {
  margin: "0 0 8px",
  color: "#e85d04",
  fontSize: "12px",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
};

const statusCardStyle: CSSProperties = {
  minWidth: "140px",
  padding: "14px 16px",
  borderRadius: "18px",
  background: "rgba(255,255,255,0.78)",
  color: "#1f2a44",
};

const statusLabelStyle: CSSProperties = {
  display: "block",
  marginBottom: "6px",
  color: "#5e6983",
  fontSize: "12px",
};

const titleStyle: CSSProperties = {
  margin: 0,
  fontSize: "30px",
  color: "#1f2a44",
};

const subtitleStyle: CSSProperties = {
  margin: 0,
  color: "#1f2a44",
};

const mutedStyle: CSSProperties = {
  color: "#5e6983",
  maxWidth: "620px",
};

const textareaStyle: CSSProperties = {
  width: "100%",
  marginTop: "16px",
  padding: "16px 18px",
  borderRadius: "18px",
  border: "1px solid #cfd7ea",
  resize: "vertical",
  fontSize: "15px",
  background: "rgba(255,255,255,0.88)",
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
  fontWeight: 600,
};

const buttonStyle: CSSProperties = {
  padding: "12px 18px",
  borderRadius: "14px",
  border: "none",
  background: "#e85d04",
  color: "#fff",
  cursor: "pointer",
  fontWeight: 700,
};

const progressRowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
  gap: "12px",
  marginTop: "18px",
};

const progressItemStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "10px",
  padding: "10px 12px",
  borderRadius: "14px",
  background: "rgba(255,255,255,0.68)",
};

const progressDotStyle: CSSProperties = {
  width: "12px",
  height: "12px",
  borderRadius: "999px",
};

const progressTextStyle: CSSProperties = {
  fontSize: "13px",
  color: "#344054",
};

const resultStyle: CSSProperties = {
  marginTop: "18px",
  padding: "18px",
  borderRadius: "18px",
  background: "#fff",
};

const resultHeaderStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: "12px",
};

const metricStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  padding: "6px 10px",
  borderRadius: "999px",
  background: "#eef2ff",
  color: "#1746a2",
  fontWeight: 700,
};

const errorStyle: CSSProperties = {
  color: "#b42318",
};
