import { AlertPanel } from "../components/AlertPanel";
import { ChatInterface } from "../components/ChatInterface";
import { ConfigPage } from "./ConfigPage";

export function DashboardPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "24px",
        background:
          "linear-gradient(180deg, #f6efe7 0%, #eef4ff 52%, #f5fbf8 100%)",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          display: "grid",
          gap: "20px",
        }}
      >
        <ChatInterface />
        <AlertPanel />
        <ConfigPage />
      </div>
    </main>
  );
}
