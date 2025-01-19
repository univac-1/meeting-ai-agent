import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
  const [backendData, setBackendData] = useState("");

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        {!backendData && (
          <button
            onClick={async () => {
              const response = await fetch(
                "https://meeting-ai-agent-132459894103.asia-northeast1.run.app/"
              );
              const data = await response.text();
              setBackendData(data);
            }}
          >
            Backendとの疎通確認
          </button>
        )}
        {backendData && (
          <div className="backend-data-success">
            <h2>Backend Data Fetched Successfully!</h2>
            <p>Response Data: {backendData}</p>
          </div>
        )}
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
