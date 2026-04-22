import { useEffect, useState, type CSSProperties } from "react";

import { fetchCompetitors, saveCompetitor } from "../services/api";

export function ConfigPage() {
  const [name, setName] = useState("");
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);

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
    await saveCompetitor({
      name: name.trim(),
      monitoring_frequency: "daily",
      is_active: true,
      aliases: [],
      search_keywords: [],
    });
    setName("");
    await loadItems();
  }

  return (
    <section style={containerStyle}>
      <h2 style={{ marginTop: 0 }}>竞品配置中心</h2>
      <div style={formStyle}>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="输入竞品名称"
          style={inputStyle}
        />
        <button type="button" onClick={handleSave} style={buttonStyle}>
          添加竞品
        </button>
      </div>
      <div style={listStyle}>
        {items.map((item, index) => (
          <div key={`${item.name ?? "competitor"}-${index}`} style={itemStyle}>
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
  background: "#f8f5f0",
};

const formStyle: CSSProperties = {
  display: "flex",
  gap: "12px",
  marginBottom: "20px",
  flexWrap: "wrap",
};

const inputStyle: CSSProperties = {
  flex: 1,
  minWidth: "220px",
  padding: "12px 14px",
  borderRadius: "14px",
  border: "1px solid #d0c4b6",
};

const buttonStyle: CSSProperties = {
  border: "none",
  borderRadius: "14px",
  padding: "12px 16px",
  background: "#1d6f42",
  color: "#fff",
  cursor: "pointer",
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
