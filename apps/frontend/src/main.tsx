import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import AgoraRTC, { AgoraRTCProvider } from "agora-rtc-react";
import App from "./App";

// In voice call, set mode to "rtc"
const client = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });

const rootElement = document.getElementById("root");
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(
    <StrictMode>
      <AgoraRTCProvider client={client}>
        <App />
      </AgoraRTCProvider>
    </StrictMode>
  );
} else {
  console.error("Failed to find the root element");
}
