import React, { useEffect, useState } from "react";

import {
  clearStoredAuthToken,
  fetchCurrentUser,
  getStoredAuthToken,
  type AuthUser,
} from "./services/api";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";

export function App() {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    const token = getStoredAuthToken();
    if (!token) {
      setBooting(false);
      return;
    }

    fetchCurrentUser()
      .then((payload) => {
        setCurrentUser(payload.user);
      })
      .catch(() => {
        clearStoredAuthToken();
        setCurrentUser(null);
      })
      .finally(() => {
        setBooting(false);
      });
  }, []);

  if (booting) {
    return (
      <div className="bau-auth-page">
        <div className="bau-container bau-auth-loading">
          <p className="bau-eyebrow">MarketIntel Agent</p>
          <h1 className="bau-auth-card__title">Loading Workspace</h1>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <AuthPage onAuthenticated={setCurrentUser} />;
  }

  return (
    <DashboardPage
      currentUser={currentUser}
      onLogout={() => {
        clearStoredAuthToken();
        setCurrentUser(null);
      }}
    />
  );
}

