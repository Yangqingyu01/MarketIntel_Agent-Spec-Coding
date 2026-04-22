import React, { useEffect, useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import { fetchCompetitors, saveCompetitor } from "../services/api";

type ConfigPageProps = {
  language: AppLanguage;
};

export function ConfigPage({ language }: ConfigPageProps) {
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

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        label: "配置 / 注册",
        title: "配置目标",
        activeSet: "启用集合",
        helper:
          "把竞品登记到监测索引中，这样同一份目标列表就可以复用于定时扫描、飞书推送和横向对比。",
        placeholder: "输入竞品名称",
        saving: "保存中",
        add: "添加竞品",
        emptyTitle: "监测列表为空",
        emptyBody: "先添加第一个目标，建立竞品监测集合。",
        company: "公司",
        cardBody: "已写入监测注册表，可直接用于后续扫描。",
      };
    }

    return {
      label: "Registry / Config",
      title: "Configure Targets",
      activeSet: "Active Set",
      helper:
        "Register companies in the monitoring index so the same watch list can be reused across scheduled scans, Feishu delivery, and side-by-side comparison.",
      placeholder: "Enter a competitor name",
      saving: "Saving",
      add: "Add Competitor",
      emptyTitle: "Watch List Empty",
      emptyBody: "Add the first target to establish the competitive monitoring set.",
      company: "Company",
      cardBody: "Saved in the monitoring registry and ready for recurring scans.",
    };
  }, [language]);

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
    <section className="bau-panel bau-panel--yellow">
      <div className="bau-panel__header">
        <div>
          <p className="bau-label">{copy.label}</p>
          <h2 className="bau-panel__title">{copy.title}</h2>
        </div>
        <span className="bau-pill bau-pill--white">
          {copy.activeSet} / {items.length}
        </span>
      </div>

      <div className="bau-config-grid">
        <div className="bau-config-form">
          <p className="bau-helper">{copy.helper}</p>

          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder={copy.placeholder}
            className="bau-field"
          />

          <button
            type="button"
            className="bau-button bau-button--red"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? copy.saving : copy.add}
          </button>
        </div>

        <div className="bau-config-list">
          {items.length === 0 ? (
            <div className="bau-config-card">
              <h3 className="bau-config-card__title">{copy.emptyTitle}</h3>
              <p className="bau-config-card__text">{copy.emptyBody}</p>
            </div>
          ) : null}

          {items.map((item, index) => (
            <article
              key={`${String(item.name ?? "competitor")}-${index}`}
              className="bau-config-card"
            >
              <div className="bau-config-card__meta">
                <span className="bau-meta">{copy.company}</span>
                <span className="bau-pill bau-pill--blue">
                  {String(item.monitoring_frequency ?? "manual").toUpperCase()}
                </span>
              </div>
              <h3 className="bau-config-card__title">{String(item.name ?? "Untitled")}</h3>
              <p className="bau-config-card__text">{copy.cardBody}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
