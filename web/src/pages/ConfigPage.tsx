import { useEffect, useState, type CSSProperties } from "react";

import { fetchCompetitors, saveCompetitor } from "../services/api";

export function ConfigPage() {
  const [name, setName] = useState("");
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [saving, setSaving] = useState(false);

  async function loadItems() {
    const payload = await fetchCompetitors();
    setItems(payload.competitors);
  }

  useEffect(() => {
    loadItems().catch(() => setItems([]));
  }, []);

  async function handleSave() {
    if (!name.trim()) {
      return;
    }
    setSaving(true);
    try {
      await saveCompetitor({
        name: name.trim(),
        monitoring_frequency: "daily",
        is_active: true,
        aliases: [],
        search_keywords: [],
      });
      setName("");
      await loadItems();
    } finally {
      setSaving(false);
    }
  }

  return (
    <section style={containerStyle}>
      <div style={headerStyle}>
        <div>
          <p style={tagStyle}>Config Center</p>
          <h2 style={{ marginTop: 0, marginBottom: "8px" }}>竞品配置中心</h2>
          <p style={hintStyle}>维护日常监测对象，供调度任务和手动分析复用。</p>
        </div>
        <div style={countCardStyle}>
          <span style={countLabelStyle}>已配置</span>
          <strong>{items.length}</strong>
        </div>
      </div>
      <div style={formStyle}>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="输入竞品名称"
          style={inputStyle}
        />
        <button type="button" onClick={handleSave} style={buttonStyle} disabled={saving}>
          {saving ? "保存中..." : "添加竞品"}
        </button>
      </div>
      <div style={listStyle}>
        {items.map((item, index) => (
          <div key={`${String(item.name ?? "competitor")}-${index}`} style={itemStyle}>
            <strong>{String(item.name ?? "未命名")}</strong>
            <span>{String(item.monitoring_frequency ?? "manual")}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

const containerStyle: CSSProperties = {
  padding: "24px",
  borderRadius: "24px",
  background:
    "linear-gradient(160deg, rgba(29,111,66,0.10), transparent 28%), #f8f5f0",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: "16px",
  flexWrap: "wrap",
};

const tagStyle: CSSProperties = {
  margin: "0 0 6px",
  color: "#1d6f42",
  fontSize: "12px",
  textTransform: "uppercase",
  letterSpacing: "0.12em",
};

const hintStyle: CSSProperties = {
  margin: 0,
  color: "#5b5f6b",
};

const countCardStyle: CSSProperties = {
  minWidth: "96px",
  padding: "12px 14px",
  borderRadius: "16px",
  background: "#fff",
  color: "#1d6f42",
};

const countLabelStyle: CSSProperties = {
  display: "block",
  marginBottom: "4px",
  fontSize: "12px",
  color: "#667085",
};

const formStyle: CSSProperties = {
  display: "flex",
  gap: "12px",
  marginTop: "18px",
  marginBottom: "20px",
  flexWrap: "wrap",
};

const inputStyle: CSSProperties = {
  flex: 1,
  minWidth: "220px",
  padding: "12px 14px",
  borderRadius: "14px",
  border: "1px solid #d0c4b6",
  background: "#fff",
};

const buttonStyle: CSSProperties = {
  border: "none",
  borderRadius: "14px",
  padding: "12px 16px",
  background: "#1d6f42",
  color: "#fff",
  cursor: "pointer",
  fontWeight: 700,
};

const listStyle: CSSProperties = {
  display: "grid",
  gap: "12px",
};

const itemStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  padding: "14px 16px",
  borderRadius: "16px",
  background: "#fff",
};
