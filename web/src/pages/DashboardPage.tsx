import React, { useEffect, useMemo, useRef, useState } from "react";

import { AlertPanel } from "../components/AlertPanel";
import { ChatInterface } from "../components/ChatInterface";
import { FeishuPanel } from "../components/FeishuPanel";
import { HistoryPanel } from "../components/HistoryPanel";
import { SchedulerPanel } from "../components/SchedulerPanel";
import type { AuthUser } from "../services/api";
import { ConfigPage } from "./ConfigPage";

export type AppLanguage = "zh" | "en";

type TabId = "analysis" | "alerts" | "history" | "operations" | "config";

class SectionErrorBoundary extends React.Component<
  { children: React.ReactNode; label: string },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; label: string }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error("Section render failed:", this.props.label, error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <section className="bau-panel bau-panel--white">
          <p className="bau-label">{this.props.label}</p>
          <h2 className="bau-panel__title">Section Error</h2>
          <p className="bau-helper">
            This section failed to render. The rest of the workspace is still available.
          </p>
        </section>
      );
    }
    return this.props.children;
  }
}

export function DashboardPage({
  currentUser,
  onLogout,
}: {
  currentUser: AuthUser;
  onLogout: () => void;
}) {
  const [language, setLanguage] = useState<AppLanguage>("zh");
  const [activeTab, setActiveTab] = useState<TabId>("analysis");
  const [tabPulseKey, setTabPulseKey] = useState(0);
  const [scrollY, setScrollY] = useState(0);
  const heroSectionRef = useRef<HTMLElement | null>(null);
  const workspaceSectionRef = useRef<HTMLElement | null>(null);
  const snapLockRef = useRef(false);

  const copy = useMemo(() => {
    if (language === "zh") {
      return {
        brandEyebrow: "\u5e02\u573a\u60c5\u62a5\u5de5\u4f5c\u53f0",
        heroTitle: "\u628a\u4fe1\u53f7\u6784\u9020\u6210\u51b3\u7b56",
        heroCopy:
          "\u7528\u4e8e\u7ade\u54c1\u626b\u63cf\u3001\u53d8\u5316\u5bf9\u6bd4\u548c\u56e2\u961f\u540c\u6b65\u7684\u5e02\u573a\u60c5\u62a5\u754c\u9762\u3002",
        pillAnalyze: "\u5206\u6790",
        pillAlert: "\u9884\u8b66",
        pillAct: "\u884c\u52a8",
        quote:
          "\u597d\u7684\u60c5\u62a5\u4e0d\u662f\u5806\u780c\u4fe1\u606f\uff0c\u800c\u662f\u628a\u5173\u952e\u4fe1\u53f7\u6574\u7406\u6210\u8db3\u4ee5\u652f\u6491\u4e0b\u4e00\u6b65\u5224\u65ad\u7684\u7ed3\u6784\u3002",
        tabs: {
          analysis: "\u5206\u6790",
          alerts: "\u9884\u8b66",
          history: "\u5386\u53f2",
          operations: "\u8fd0\u8425",
          config: "\u914d\u7f6e",
        },
        tabLeads: {
          analysis:
            "\u63d0\u4ea4\u7ade\u54c1\u5206\u6790\uff0c\u67e5\u770b\u6458\u8981\u3001\u56fe\u8868\u4e0e\u63a8\u8350\u52a8\u4f5c\u3002",
          alerts: "\u8ddf\u8e2a\u6700\u65b0\u9884\u8b66\u548c\u53d8\u5316\u4fe1\u53f7\u3002",
          history: "\u67e5\u770b\u5386\u53f2\u5feb\u7167\u3001\u8d8b\u52bf\u548c\u5feb\u7167\u5dee\u5f02\u3002",
          operations:
            "\u67e5\u770b\u8c03\u5ea6\u72b6\u6001\u3001\u5468\u671f\u6458\u8981\u548c\u98de\u4e66\u9001\u8fbe\u60c5\u51b5\u3002",
          config: "\u7ba1\u7406\u7ade\u54c1\u5217\u8868\u548c\u76d1\u63a7\u8bbe\u7f6e\u3002",
        },
        ctaLabel: "\u884c\u52a8\u6536\u675f",
        ctaTitle: "\u5206\u6790\u3002\u6bd4\u8f83\u3002\u51b3\u7b56\u3002",
        ctaCopy:
          "\u628a\u5173\u952e\u4fe1\u53f7\u6574\u7406\u6e05\u695a\uff0c\u8ba9\u56e2\u961f\u66f4\u5feb\u8fdb\u5165\u5224\u65ad\u548c\u6267\u884c\u3002",
        langButton: "EN",
        organizationChip: "\u7ec4\u7ec7",
        userChip: "\u7528\u6237",
        workspaceLabel: "\u5de5\u4f5c\u53f0",
        workspaceTitle: "\u5207\u6362\u4efb\u52a1\u89c6\u56fe",
        scrollButton: "\u5411\u4e0b\u8fdb\u5165\u5de5\u4f5c\u53f0",
      };
    }

    return {
      brandEyebrow: "Market intelligence workspace",
      heroTitle: "Build Signals Into Decisions",
      heroCopy:
        "A geometric monitoring console for scanning competitors, comparing change, and keeping the team aligned on what matters next.",
      pillAnalyze: "Analyze",
      pillAlert: "Alert",
      pillAct: "Act",
      quote:
        "Good intelligence is not about piling up information. It is about arranging the right signals so the next move is clear.",
      tabs: {
        analysis: "Analysis",
        alerts: "Alerts",
        history: "History",
        operations: "Operations",
        config: "Config",
      },
      tabLeads: {
        analysis: "Run competitor analysis and review summaries, charts, and actions.",
        alerts: "Track the latest alerts and change signals.",
        history: "Inspect historical snapshots, trends, and snapshot diffs.",
        operations: "Review scheduler status, digest output, and Feishu delivery.",
        config: "Manage monitored competitors and workspace settings.",
      },
      ctaLabel: "Operational Close",
      ctaTitle: "Analyze. Compare. Decide.",
      ctaCopy:
        "Turn the critical signals into a clear operating picture so the team can move faster.",
      langButton: "\u4e2d",
      organizationChip: "Org",
      userChip: "User",
      workspaceLabel: "Workspace",
      workspaceTitle: "Switch Task Views",
      scrollButton: "Scroll to Workspace",
    };
  }, [language]);

  const tabOrder: TabId[] = ["analysis", "alerts", "history", "operations", "config"];

  useEffect(() => {
    function handleScroll() {
      setScrollY(window.scrollY || 0);
    }
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    function releaseSnapLock() {
      window.setTimeout(() => {
        snapLockRef.current = false;
      }, 760);
    }

    function snapToSection(target: "hero" | "workspace") {
      snapLockRef.current = true;

      if (target === "hero") {
        window.scrollTo({ top: 0, behavior: "smooth" });
        releaseSnapLock();
        return;
      }

      const node = workspaceSectionRef.current;

      if (!node) {
        snapLockRef.current = false;
        return;
      }

      node.scrollIntoView({ behavior: "smooth", block: "start" });
      releaseSnapLock();
    }

    function handleWheel(event: WheelEvent) {
      if (snapLockRef.current) {
        event.preventDefault();
        return;
      }

      const viewportHeight = window.innerHeight;
      const currentScroll = window.scrollY;
      const workspaceTop = workspaceSectionRef.current?.offsetTop ?? viewportHeight;

      if (event.deltaY > 18 && currentScroll < viewportHeight * 0.45) {
        event.preventDefault();
        snapToSection("workspace");
        return;
      }

      if (
        event.deltaY < -18 &&
        currentScroll > workspaceTop - viewportHeight * 0.2 &&
        currentScroll < workspaceTop + viewportHeight * 0.75
      ) {
        event.preventDefault();
        snapToSection("hero");
      }
    }

    let touchStartY = 0;

    function handleTouchStart(event: TouchEvent) {
      touchStartY = event.touches[0]?.clientY ?? 0;
    }

    function handleTouchEnd(event: TouchEvent) {
      if (snapLockRef.current) {
        return;
      }

      const touchEndY = event.changedTouches[0]?.clientY ?? touchStartY;
      const deltaY = touchStartY - touchEndY;
      const viewportHeight = window.innerHeight;
      const currentScroll = window.scrollY;
      const workspaceTop = workspaceSectionRef.current?.offsetTop ?? viewportHeight;

      if (deltaY > 48 && currentScroll < viewportHeight * 0.45) {
        snapToSection("workspace");
        return;
      }

      if (
        deltaY < -48 &&
        currentScroll > workspaceTop - viewportHeight * 0.2 &&
        currentScroll < workspaceTop + viewportHeight * 0.75
      ) {
        snapToSection("hero");
      }
    }

    window.addEventListener("wheel", handleWheel, { passive: false });
    window.addEventListener("touchstart", handleTouchStart, { passive: true });
    window.addEventListener("touchend", handleTouchEnd, { passive: true });

    return () => {
      window.removeEventListener("wheel", handleWheel);
      window.removeEventListener("touchstart", handleTouchStart);
      window.removeEventListener("touchend", handleTouchEnd);
    };
  }, []);

  const viewportHeight = typeof window !== "undefined" ? window.innerHeight || 900 : 900;
  const pageTransitionProgress = Math.min(scrollY / Math.max(viewportHeight * 0.78, 1), 1);
  const workspaceHeaderProgress = Math.min(Math.max((pageTransitionProgress - 0.08) / 0.92, 0), 1);
  const workspaceTabsProgress = Math.min(Math.max((pageTransitionProgress - 0.16) / 0.84, 0), 1);
  const workspaceStageProgress = Math.min(Math.max((pageTransitionProgress - 0.24) / 0.76, 0), 1);
  const heroLeftStyle = {
    opacity: 1 - pageTransitionProgress * 0.9,
    transform: `translateY(${pageTransitionProgress * 72}px) scale(${1 - pageTransitionProgress * 0.14})`,
  };
  const heroRightStyle = {
    opacity: 1 - pageTransitionProgress * 0.94,
    transform: `translateY(${pageTransitionProgress * 112}px) scale(${1 - pageTransitionProgress * 0.18}) rotate(${pageTransitionProgress * 7}deg)`,
  };
  const heroScrollStyle = {
    opacity: 1 - pageTransitionProgress,
    transform: `translateY(${pageTransitionProgress * 48}px)`,
  };
  const heroVeilStyle = {
    opacity: pageTransitionProgress * 0.72,
  };
  const workspaceShellStyle = {
    opacity: 0.04 + pageTransitionProgress * 0.96,
    transform: `translateY(${(1 - pageTransitionProgress) * 140}px) scale(${0.84 + pageTransitionProgress * 0.16})`,
  };
  const workspaceHeaderStyle = {
    opacity: 0.08 + workspaceHeaderProgress * 0.92,
    transform: `translateY(${(1 - workspaceHeaderProgress) * 54}px)`,
  };
  const workspaceTabsStyle = {
    opacity: 0.06 + workspaceTabsProgress * 0.94,
    transform: `translateY(${(1 - workspaceTabsProgress) * 72}px)`,
  };
  const workspaceStageStyle = {
    opacity: 0.04 + workspaceStageProgress * 0.96,
    transform: `translateY(${(1 - workspaceStageProgress) * 96}px)`,
  };

  return (
    <div className="bau-page">
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>

      <header className="bau-topbar">
        <div className="bau-container bau-topbar__inner">
          <div className="bau-brand">
            <div className="bau-brand__mark" aria-hidden="true">
              <span className="bau-shape bau-shape--circle" />
              <span className="bau-shape bau-shape--square" />
              <span className="bau-shape bau-shape--triangle" />
            </div>
            <div className="bau-brand__text">
              <p className="bau-eyebrow">{copy.brandEyebrow}</p>
              <p className="bau-brand__title">MarketIntel Agent</p>
            </div>
          </div>

          <div className="bau-topbar__meta">
            <span className="bau-meta-chip">
              {copy.organizationChip} / {currentUser.organization_name}
            </span>
            <span className="bau-meta-chip">
              {copy.userChip} / {currentUser.full_name}
            </span>
            <button
              type="button"
              className="bau-button bau-button--white bau-button--lang"
              onClick={() => setLanguage((current) => (current === "zh" ? "en" : "zh"))}
            >
              {copy.langButton}
            </button>
            <button
              type="button"
              className="bau-button bau-button--white bau-button--lang"
              onClick={onLogout}
            >
              {language === "zh" ? "\u9000\u51fa" : "Logout"}
            </button>
          </div>
        </div>
      </header>

      <main id="main-content">
        <section ref={heroSectionRef} className="bau-section bau-section--hero">
          <div className="bau-container bau-hero bau-hero--compact bau-hero--fullscreen">
            <div className="bau-hero__left bau-reveal bau-reveal--1" style={heroLeftStyle}>
              <p className="bau-eyebrow">{copy.brandEyebrow}</p>
              <h1 className="bau-hero__title">{copy.heroTitle}</h1>
              <p className="bau-hero__copy">{copy.heroCopy}</p>
              <div className="bau-hero__row">
                <span className="bau-pill bau-pill--yellow">{copy.pillAnalyze}</span>
                <span className="bau-pill bau-pill--blue">{copy.pillAlert}</span>
                <span className="bau-pill bau-pill--red">{copy.pillAct}</span>
              </div>
            </div>

            <div
              className="bau-hero__right bau-reveal bau-reveal--2"
              aria-hidden="true"
              style={heroRightStyle}
            >
              <div className="bau-composition">
                <div className="bau-composition__circle" />
                <div className="bau-composition__square" />
                <div className="bau-composition__square-small" />
                <div className="bau-composition__triangle" />
                <div className="bau-composition__bar" />
              </div>
            </div>

            <div
              className="bau-hero__scroll bau-reveal bau-reveal--3"
              style={heroScrollStyle}
              aria-hidden="true"
            >
              <span className="bau-button bau-button--yellow bau-button--scroll">
                {copy.scrollButton}
              </span>
            </div>
          </div>
          <div className="bau-hero__veil" aria-hidden="true" style={heroVeilStyle} />
        </section>

        <section
          ref={workspaceSectionRef}
          id="workspace-section"
          className="bau-section bau-section--workspace"
        >
          <div className="bau-container bau-workspace-shell" style={workspaceShellStyle}>
            <div
              className="bau-workspace-header bau-reveal bau-reveal--1"
              style={workspaceHeaderStyle}
            >
              <div>
                <p className="bau-label">{copy.workspaceLabel}</p>
                <h2 className="bau-workspace-header__title">{copy.workspaceTitle}</h2>
              </div>
            </div>

            <nav
              className="bau-tabbar bau-reveal bau-reveal--2"
              aria-label="Workspace sections"
              style={workspaceTabsStyle}
            >
              {tabOrder.map((tabId) => (
                <button
                  key={tabId}
                  type="button"
                  className={activeTab === tabId ? "bau-tab bau-tab--active" : "bau-tab"}
                  onClick={() => {
                    setActiveTab(tabId);
                    setTabPulseKey((current) => current + 1);
                  }}
                >
                  {copy.tabs[tabId]}
                </button>
              ))}
            </nav>

            <div
              key={tabPulseKey}
              className="bau-tabstage bau-tabstage--animated bau-reveal bau-reveal--3"
              style={workspaceStageStyle}
            >
              <div className="bau-tabstage__intro">
                <p className="bau-label">{copy.tabs[activeTab]}</p>
                <p className="bau-helper">{copy.tabLeads[activeTab]}</p>
              </div>

              {activeTab === "analysis" ? (
                <div className="bau-workspace-stack">
                  <SectionErrorBoundary label="analysis">
                    <ChatInterface language={language} />
                  </SectionErrorBoundary>
                </div>
              ) : null}

              {activeTab === "alerts" ? (
                <div className="bau-workspace-grid">
                  <SectionErrorBoundary label="alerts">
                    <AlertPanel language={language} />
                  </SectionErrorBoundary>
                  <aside className="bau-quote">
                    <p className="bau-quote__mark" aria-hidden="true">
                      "
                    </p>
                    <p className="bau-quote__text">{copy.quote}</p>
                  </aside>
                </div>
              ) : null}

              {activeTab === "history" ? (
                <div className="bau-workspace-stack">
                  <SectionErrorBoundary label="history">
                    <HistoryPanel language={language} />
                  </SectionErrorBoundary>
                </div>
              ) : null}

              {activeTab === "operations" ? (
                <div className="bau-workspace-stack">
                  <SectionErrorBoundary label="scheduler">
                    <SchedulerPanel language={language} />
                  </SectionErrorBoundary>
                  <SectionErrorBoundary label="feishu">
                    <FeishuPanel language={language} />
                  </SectionErrorBoundary>
                </div>
              ) : null}

              {activeTab === "config" ? (
                <div className="bau-workspace-stack">
                  <SectionErrorBoundary label="config">
                    <ConfigPage language={language} />
                  </SectionErrorBoundary>
                </div>
              ) : null}
            </div>
          </div>
        </section>

        <section className="bau-section">
          <div className="bau-container">
            <div className="bau-cta">
              <p className="bau-label">{copy.ctaLabel}</p>
              <h2 className="bau-cta__title">{copy.ctaTitle}</h2>
              <p className="bau-cta__copy">{copy.ctaCopy}</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
