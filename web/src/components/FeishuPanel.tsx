import React, { useEffect, useMemo, useState } from "react";

import type { AppLanguage } from "../pages/DashboardPage";
import { fetchFeishuStatus, type FeishuStatusResponse } from "../services/api";

type FeishuPanelProps = {
  language: AppLanguage;
};

export function FeishuPanel({ language }: FeishuPanelProps) {
  const [status, setStatus] = useState<FeishuStatusResponse | null>(null);

  useEffect(() => {
    fetchFeishuStatus().then(setStatus).catch(() => setStatus(null));
  }, []);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        label: "飞书 / 投递",
        title: "飞书配置状态",
        configured: "配置",
        mode: "发送模式",
        appId: "App ID",
        secret: "App Secret",
        target: "目标会话",
        webhook: "Webhook",
        preview: "示例投递",
        ready: "已配置",
        missing: "未配置",
        sample: "示例卡片已生成，可用于验证投递通路。",
      };
    }

    return {
      label: "Feishu / Delivery",
      title: "Feishu Status",
      configured: "Configured",
      mode: "Delivery Mode",
      appId: "App ID",
      secret: "App Secret",
      target: "Target Chat",
      webhook: "Webhook",
      preview: "Preview Delivery",
      ready: "Ready",
      missing: "Missing",
      sample: "A sample card has been prepared to verify the delivery path.",
    };
  }, [language]);

  return (
    <section className="bau-panel bau-panel--blue">
      <div className="bau-panel__header">
        <div>
          <p className="bau-label">{copy.label}</p>
          <h2 className="bau-panel__title">{copy.title}</h2>
        </div>
        <span className="bau-pill bau-pill--white">
          {copy.mode} / {status?.delivery_mode ?? "mock"}
        </span>
      </div>

      <div className="bau-feishu-grid">
        <article className="bau-feishu-card">
          <div className="bau-feishu-card__row">
            <span className="bau-meta">{copy.configured}</span>
            <span className="bau-pill bau-pill--yellow">
              {status?.configured ? copy.ready : copy.missing}
            </span>
          </div>
          <div className="bau-feishu-checks">
            <div>{copy.appId}: {status?.app_id_configured ? copy.ready : copy.missing}</div>
            <div>{copy.secret}: {status?.app_secret_configured ? copy.ready : copy.missing}</div>
            <div>{copy.target}: {status?.target_chat_masked || copy.missing}</div>
            <div>{copy.webhook}: {status?.webhook_endpoint ?? "/api/feishu/webhook"}</div>
          </div>
        </article>

        <article className="bau-feishu-card bau-feishu-card--accent">
          <div className="bau-feishu-card__row">
            <span className="bau-meta">{copy.preview}</span>
            <span className="bau-pill bau-pill--white">
              {status?.preview_delivery.ok ? "OK" : "PENDING"}
            </span>
          </div>
          <p className="bau-feishu-card__text">{copy.sample}</p>
          <p className="bau-feishu-card__text">
            {copy.mode}: {status?.preview_delivery.delivery_mode ?? "mock"}
          </p>
          <p className="bau-feishu-card__text">
            {copy.target}: {status?.preview_delivery.chat_id || copy.missing}
          </p>
        </article>
      </div>
    </section>
  );
}
