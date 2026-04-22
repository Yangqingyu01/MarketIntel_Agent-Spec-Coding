import React, { useMemo, useState } from "react";

import {
  loginAccount,
  registerAccount,
  setStoredAuthToken,
  type AuthUser,
} from "../services/api";

type AuthMode = "login" | "register";
type AuthLanguage = "zh" | "en";

export function AuthPage({
  onAuthenticated,
}: {
  onAuthenticated: (user: AuthUser) => void;
}) {
  const [language, setLanguage] = useState<AuthLanguage>("zh");
  const [mode, setMode] = useState<AuthMode>("login");
  const [organizationName, setOrganizationName] = useState("MarketIntel Lab");
  const [fullName, setFullName] = useState("Demo User");
  const [email, setEmail] = useState("demo@marketintel.ai");
  const [password, setPassword] = useState("demo123");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const copy = useMemo(() => {
    if (language === "zh") {
      if (mode === "register") {
        return {
          eyebrow: "\u4f01\u4e1a\u5165\u53e3",
          title: "\u521b\u5efa\u4f01\u4e1a\u5de5\u4f5c\u53f0",
          helper: "\u5148\u6ce8\u518c\u4e00\u4e2a\u7ec4\u7ec7\u8d26\u53f7\uff0c\u8fdb\u5165\u5c5e\u4e8e\u5f53\u524d\u7ec4\u7ec7\u7684\u72ec\u7acb\u6570\u636e\u7a7a\u95f4\u3002",
          primary: "\u521b\u5efa\u5de5\u4f5c\u53f0",
          secondary: "\u5df2\u6709\u8d26\u53f7\uff0c\u76f4\u63a5\u767b\u5f55",
          heroTitle: "\u5e02\u573a\u60c5\u62a5\u76d1\u6d4b\u667a\u80fd\u4f53",
          heroCopy: "\u5148\u5b8c\u6210\u4f01\u4e1a\u767b\u5f55\uff0c\u518d\u8fdb\u5165\u60c5\u62a5\u5de5\u4f5c\u53f0\u3002",
          organization: "\u4f01\u4e1a\u540d\u79f0",
          fullName: "\u59d3\u540d",
          email: "\u90ae\u7bb1",
          password: "\u5bc6\u7801",
          orgPlaceholder: "\u8f93\u5165\u4f01\u4e1a\u540d\u79f0",
          namePlaceholder: "\u8f93\u5165\u4f60\u7684\u59d3\u540d",
          emailPlaceholder: "name@company.com",
          passwordPlaceholder: "\u81f3\u5c11 6 \u4f4d",
          loading: "\u5904\u7406\u4e2d...",
          langButton: "EN",
        };
      }

      return {
        eyebrow: "\u4f01\u4e1a\u5165\u53e3",
        title: "\u767b\u5f55 MarketIntel",
        helper: "\u4f7f\u7528\u4f01\u4e1a\u8d26\u53f7\u8fdb\u5165\u5e02\u573a\u60c5\u62a5\u5de5\u4f5c\u53f0\uff0c\u5e76\u52a0\u8f7d\u5c5e\u4e8e\u5f53\u524d\u7ec4\u7ec7\u7684\u72ec\u7acb\u6570\u636e\u3002",
        primary: "\u767b\u5f55",
        secondary: "\u9700\u8981\u8d26\u53f7\uff1f\u7acb\u5373\u521b\u5efa",
        heroTitle: "\u5e02\u573a\u60c5\u62a5\u76d1\u6d4b\u667a\u80fd\u4f53",
        heroCopy: "\u5148\u5b8c\u6210\u4f01\u4e1a\u767b\u5f55\uff0c\u518d\u8fdb\u5165\u60c5\u62a5\u5de5\u4f5c\u53f0\u3002",
        organization: "\u4f01\u4e1a\u540d\u79f0",
        fullName: "\u59d3\u540d",
        email: "\u90ae\u7bb1",
        password: "\u5bc6\u7801",
        orgPlaceholder: "\u8f93\u5165\u4f01\u4e1a\u540d\u79f0",
        namePlaceholder: "\u8f93\u5165\u4f60\u7684\u59d3\u540d",
        emailPlaceholder: "name@company.com",
        passwordPlaceholder: "\u81f3\u5c11 6 \u4f4d",
        loading: "\u5904\u7406\u4e2d...",
        langButton: "EN",
      };
    }

    if (mode === "register") {
      return {
        eyebrow: "Enterprise Access",
        title: "Create Your Workspace",
        helper: "Create an organization account and enter an isolated workspace for your team.",
        primary: "Create Workspace",
        secondary: "Already have an account? Sign in",
        heroTitle: "Market Intelligence Monitoring Agent",
        heroCopy: "Complete organization login first, then enter the intelligence workspace.",
        organization: "Organization",
        fullName: "Full Name",
        email: "Email",
        password: "Password",
        orgPlaceholder: "Your company name",
        namePlaceholder: "Your name",
        emailPlaceholder: "name@company.com",
        passwordPlaceholder: "Minimum 6 characters",
        loading: "Loading...",
        langButton: "\u4e2d",
      };
    }

    return {
      eyebrow: "Enterprise Access",
      title: "Sign In To MarketIntel",
      helper: "Use a workspace account to enter the market intelligence console with your own organization data.",
      primary: "Sign In",
      secondary: "Need an account? Create one",
      heroTitle: "Market Intelligence Monitoring Agent",
      heroCopy: "Complete organization login first, then enter the intelligence workspace.",
      organization: "Organization",
      fullName: "Full Name",
      email: "Email",
      password: "Password",
      orgPlaceholder: "Your company name",
      namePlaceholder: "Your name",
      emailPlaceholder: "name@company.com",
      passwordPlaceholder: "Minimum 6 characters",
      loading: "Loading...",
      langButton: "\u4e2d",
    };
  }, [language, mode]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const payload =
        mode === "register"
          ? await registerAccount({
              organization_name: organizationName,
              full_name: fullName,
              email,
              password,
            })
          : await loginAccount({ email, password });
      setStoredAuthToken(payload.access_token);
      onAuthenticated(payload.user);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Authentication failed";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="bau-auth-page">
      <div className="bau-container bau-auth-shell">
        <section className="bau-auth-hero">
          <div className="bau-auth-hero__actions">
            <button
              type="button"
              className="bau-button bau-button--white bau-button--lang"
              onClick={() => setLanguage((current) => (current === "zh" ? "en" : "zh"))}
            >
              {copy.langButton}
            </button>
          </div>
          <p className="bau-eyebrow">MarketIntel Agent</p>
          <h1 className="bau-auth-hero__title">{copy.heroTitle}</h1>
          <p className="bau-auth-hero__copy">{copy.heroCopy}</p>

          <div className="bau-auth-hero__grid" aria-hidden="true">
            <span className="bau-auth-shape bau-auth-shape--circle" />
            <span className="bau-auth-shape bau-auth-shape--square" />
            <span className="bau-auth-shape bau-auth-shape--triangle" />
          </div>
        </section>

        <section className="bau-auth-card">
          <p className="bau-eyebrow">{copy.eyebrow}</p>
          <h2 className="bau-auth-card__title">{copy.title}</h2>
          <p className="bau-helper">{copy.helper}</p>

          <form className="bau-auth-form" onSubmit={handleSubmit}>
            {mode === "register" ? (
              <label className="bau-auth-field">
                <span className="bau-label">{copy.organization}</span>
                <input
                  className="bau-field"
                  value={organizationName}
                  onChange={(event) => setOrganizationName(event.target.value)}
                  placeholder={copy.orgPlaceholder}
                />
              </label>
            ) : null}

            {mode === "register" ? (
              <label className="bau-auth-field">
                <span className="bau-label">{copy.fullName}</span>
                <input
                  className="bau-field"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  placeholder={copy.namePlaceholder}
                />
              </label>
            ) : null}

            <label className="bau-auth-field">
              <span className="bau-label">{copy.email}</span>
              <input
                className="bau-field"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder={copy.emailPlaceholder}
              />
            </label>

            <label className="bau-auth-field">
              <span className="bau-label">{copy.password}</span>
              <input
                className="bau-field"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder={copy.passwordPlaceholder}
              />
            </label>

            {error ? <p className="bau-auth-error">{error}</p> : null}

            <button
              type="submit"
              className="bau-button bau-button--red"
              disabled={submitting}
            >
              {submitting ? copy.loading : copy.primary}
            </button>
          </form>

          <button
            type="button"
            className="bau-auth-switch"
            onClick={() => setMode((current) => (current === "login" ? "register" : "login"))}
          >
            {copy.secondary}
          </button>
        </section>
      </div>
    </div>
  );
}

