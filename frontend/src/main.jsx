import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { createWorker } from "tesseract.js";
import {
  Shield,
  MessageSquare,
  Link as LinkIcon,
  Globe,
  Mail,
  Image as ImageIcon,
  QrCode,
  Search,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  RotateCcw,
  History as HistoryIcon,
  Clock3,
  X,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Sparkles,
  Lock,
} from "lucide-react";
import "./index.css";

const API = `${import.meta.env.VITE_API_URL}/api/analyze`;
const HISTORY_KEY = "contextshield_history";

const inputs = [
  ["message", "Message", MessageSquare, "Suspicious SMS, WhatsApp or chat"],
  ["url", "URL", LinkIcon, "Check a suspicious link"],
  ["website", "Website", Globe, "Inspect a website address"],
  ["email", "Email", Mail, "Analyze email content"],
  ["screenshot", "Screenshot", ImageIcon, "Analyze a screenshot"],
  ["qr", "QR Code", QrCode, "Scan a QR destination"],
];

function App() {

  async function extractTextFromImage(imageFile) {
    const worker = await createWorker("eng");

    try {
      const result = await worker.recognize(imageFile);
      return result.data.text.trim();
    } finally {
      await worker.terminate();
    }
  }
  const [type, setType] = useState("message");
  const [value, setValue] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch {
      return [];
    }
  });

  const [historyOpen, setHistoryOpen] = useState(false);

  const selected = inputs.find((item) => item[0] === type);
  const resultRef = useRef(null);
  const historyRef = useRef(null);
  const inputRefs = useRef([]);
  const textareaRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    if (result && resultRef.current) {
      requestAnimationFrame(() => {
        resultRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    }
  }, [result]);

  function selectInput(id) {
    setType(id);
    setValue("");
    setFile(null);
    setResult(null);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  }

  const navigateInput = (direction) => {
  const currentIndex = inputs.findIndex(([id]) => id === type);

  if (currentIndex === -1) return;

  let nextIndex = currentIndex;

  if (direction === "right") {
    nextIndex = Math.min(currentIndex + 1, inputs.length - 1);
  }

  if (direction === "left") {
    nextIndex = Math.max(currentIndex - 1, 0);
  }

  if (direction === "down") {
    nextIndex = Math.min(currentIndex + 3, inputs.length - 1);
  }

  if (direction === "up") {
    nextIndex = Math.max(currentIndex - 3, 0);
  }

  selectInput(inputs[nextIndex][0]);
};

  async function analyze() {
    if (loading) return;

setLoading(true);

try {
  let content = value.trim();

  // =========================
  // SCREENSHOT → OCR
  // =========================
  if (type === "screenshot") {
    if (!file) {
      setLoading(false);
      return;
    }

    content = await extractTextFromImage(file);

    if (!content) {
      throw new Error(
        "No readable text was detected in the screenshot."
      );
    }
  }

  // =========================
  // QR CODE
  // =========================
  if (type === "qr") {
    if (!file) {
      setLoading(false);
      return;
    }

    content = `[QR image: ${file.name}]`;
  }

  if (!content) {
    setLoading(false);
    return;
  }

  // =========================
  // SEND REAL CONTENT
  // =========================
  const response = await fetch(API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      input_type: type,
      content,
    }),
  });

  if (!response.ok) {
    throw new Error("API request failed");
  }

  const data = await response.json();

  // =========================
  // SHOW RESULT
  // =========================
  setResult(data);

  // =========================
  // SAVE HISTORY
  // =========================
  const historyItem = {
    id: Date.now(),
    inputType: type,
    inputLabel: selected?.[1] || type,
    content,
    result: data,
    createdAt: new Date().toLocaleString(),
  };

  setHistory((prev) => [
    historyItem,
    ...prev,
  ].slice(0, 30));

  

} catch (error) {

  console.error(
    "Analysis error:",
    error
  );

  setResult({
    error:
      error.message ||
      "Unable to analyze this input.",
  });

} finally {

  setLoading(false);

}
function reset() {
  setResult(null);
  setValue("");
  setFile(null);
}
}
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      analyze();
    }
  }

  function openHistory() {
    setHistoryOpen(true);

    setTimeout(() => {
      historyRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 50);
  }

  function closeHistory() {
    setHistoryOpen(false);
  }

  function clearHistory() {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  }

  function loadHistoryItem(item) {
    setType(item.inputType);

    if (item.content.startsWith("[Uploaded file:")) {
      setValue("");
    } else {
      setValue(item.content);
    }

    setFile(null);
    setResult(item.result);
    setHistoryOpen(false);
  }

  function copyResult() {
    if (!result) return;

    const text = `
ContextShield Analysis

Risk: ${result.risk_level}
Score: ${result.risk_score}/100
Category: ${result.category}

Why:
${(result.reasons || []).map((r) => `• ${r}`).join("\n")}

What to do:
${result.safe_action || ""}
`;

    navigator.clipboard?.writeText(text);
  }

  return (
    <div className="app-shell">
      {/* HEADER */}
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-icon">
              <Shield size={21} />
            </div>

            <div>
              <div className="brand-name">ContextShield</div>
              <div className="brand-subtitle">
                Explainable Scam Intelligence
              </div>
            </div>
          </div>

          <div className="nav-actions">
            <button
              className={`nav-button ${
                historyOpen ? "nav-active" : ""
              }`}
              onClick={openHistory}
            >
              <HistoryIcon size={16} />
              <span>History</span>

              {history.length > 0 && (
                <span className="history-count">{history.length}</span>
              )}
            </button>

            <button
              className="nav-button about-button"
              onClick={() =>
                document
                  .getElementById("about")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              About
            </button>
          </div>
        </div>
      </header>

      <main className="main-container">
        {/* HERO */}
        <section className="hero">
          <div className="hero-badge">
            <span className="status-dot" />
            <ShieldCheck size={15} />
            Detect · Explain · Protect
          </div>

          <h1>
            Is this <span>safe?</span>
          </h1>

          <p>
            Analyze suspicious messages, links, websites, emails, screenshots
            and QR codes before you click, pay or share sensitive information.
          </p>

          <div className="trust-row">
            <div>
              <Lock size={14} />
              Privacy focused
            </div>

            <div>
              <Sparkles size={14} />
              Explainable analysis
            </div>

            <div>
              <ShieldCheck size={14} />
              Risk-based detection
            </div>
          </div>
        </section>

        {/* INPUT TYPE SELECTOR */}
        <section className="input-selector">
          <div className="section-heading">
            <div>
              <span className="eyebrow">STEP 01</span>
              <h2>What do you want to check?</h2>
            </div>

            <span className="selection-label">
              {selected?.[1]} selected
            </span>
          </div>

          <div className="input-grid">
          {inputs.map(([id, label, Icon, desc], index) => (
  <button
    key={id}
    type="button"
    onClick={() => selectInput(id)}
    onKeyDown={(e) => {
      let nextIndex = index;

      if (e.key === "ArrowRight" && index % 3 !== 2) {
        nextIndex = index + 1;
      }

      if (e.key === "ArrowLeft" && index % 3 !== 0) {
        nextIndex = index - 1;
      }

      if (e.key === "ArrowDown" && index + 3 < inputs.length) {
        nextIndex = index + 3;
      }

      if (e.key === "ArrowUp" && index - 3 >= 0) {
        nextIndex = index - 3;
      }

      if (nextIndex !== index) {
        e.preventDefault();

        selectInput(inputs[nextIndex][0]);

       e.currentTarget.parentElement
  .querySelectorAll("button")[nextIndex]
  ?.focus();
      }
    }}
    className={`input-card ${
      type === id ? "input-card-selected" : ""
    }`}
  >
                <div className="input-card-top">
                  <div className="input-icon">
                    <Icon size={20} />
                  </div>

                  {type === id && (
                    <CheckCircle2
                      className="selected-check"
                      size={18}
                    />
                  )}
                </div>

                <div className="input-title">{label}</div>

                <div className="input-description">{desc}</div>

                <ChevronRight className="input-arrow" size={17} />
              </button>
            ))}
          </div>
        </section>

        {/* ANALYSIS PANEL */}
        <section className="analysis-panel">
          <div className="analysis-header">
            <div>
              <span className="eyebrow">STEP 02</span>

              <h2>
                Analyze your{" "}
                <strong>{selected?.[1]?.toLowerCase()}</strong>
              </h2>
            </div>

            <div className="analysis-icon">
              <Search size={19} />
            </div>
          </div>

          {["screenshot", "qr"].includes(type) ? (
            <label className="upload-area">
              <input
                type="file"
                accept="image/*"
                onChange={(e) =>
                  setFile(e.target.files?.[0] || null)
                }
              />

              <div className="upload-icon">
                {type === "qr" ? (
                  <QrCode size={28} />
                ) : (
                  <ImageIcon size={28} />
                )}
              </div>

              <strong>
                {file ? file.name : "Drop your image here"}
              </strong>

              <span>
                {file
                  ? "Image selected and ready for analysis"
                  : "Click to browse • PNG, JPG, JPEG"}
              </span>
            </label>
          ) : (
            <div className="textarea-wrapper">
              <textarea
                ref={textareaRef}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  type === "message"
                    ? "Paste the suspicious message here..."
                    : type === "email"
                    ? "Paste the complete email content here..."
                    : type === "url" || type === "website"
                    ? "https://example.com/..."
                    : "Paste the content you want to analyze..."
                }
              />

              <div className="textarea-footer">
                <span>
                  {type === "message"
                    ? "Enter to analyze • Shift + Enter for new line"
                    : "Your input is analyzed locally through ContextShield"}
                </span>

                <span>{value.length} characters</span>
              </div>
            </div>
          )}

          <button
            className="analyze-button"
            onClick={analyze}
            disabled={loading || (!value.trim() && !file)}
          >
            <span>
              {loading ? "Analyzing threat..." : "Analyze Threat"}
            </span>

            {loading ? (
              <span className="spinner" />
            ) : (
              <ArrowRight size={19} />
            )}
          </button>
        </section>

        {/* LOADING */}
        {loading && (
          <section className="loading-panel">
            <div className="loading-header">
              <div className="loading-orb">
                <Shield size={20} />
              </div>

              <div>
                <strong>ContextShield is analyzing</strong>
                <span>Running multiple detection layers...</span>
              </div>
            </div>

            <div className="loading-steps">
              {[
                "Detecting language",
                "Extracting suspicious signals",
                "Analyzing context",
                "Checking URL patterns",
                "Evaluating scam indicators",
                "Preparing explanation",
              ].map((step, index) => (
                <div className="loading-step" key={step}>
                  <span className="loading-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  <span>{step}</span>

                  <span className="loading-dot" />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* RESULT */}
        {result && (
          <div ref={resultRef}>
            <Result
              result={result}
              reset={() => {
                setResult(null);
                setValue("");
                setFile(null);
              }}
              copyResult={copyResult}
            />
          </div>
        )}

        {/* HISTORY */}
        <section
          ref={historyRef}
          className={`history-section ${
            historyOpen ? "history-open" : ""
          }`}
        >
          <div className="history-header">
            <div>
              <span className="eyebrow">ACTIVITY</span>

              <h2>
                <HistoryIcon size={21} />
                Analysis History
              </h2>

              <p>Your completed security checks appear here.</p>
            </div>

            <div className="history-controls">
              {history.length > 0 && (
                <button
                  className="clear-button"
                  onClick={clearHistory}
                >
                  Clear history
                </button>
              )}

              {historyOpen && (
                <button
                  className="close-button"
                  onClick={closeHistory}
                >
                  <X size={17} />
                </button>
              )}
            </div>
          </div>

          {history.length === 0 ? (
            <div className="empty-history">
              <Clock3 size={27} />

              <strong>No analyses yet</strong>

              <span>
                Your previous threat checks will appear here.
              </span>
            </div>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <button
                  key={item.id}
                  className="history-item"
                  onClick={() => loadHistoryItem(item)}
                >
                  <div className="history-item-icon">
                    {item.inputType === "message" && (
                      <MessageSquare size={18} />
                    )}

                    {item.inputType === "url" && (
                      <LinkIcon size={18} />
                    )}

                    {item.inputType === "website" && (
                      <Globe size={18} />
                    )}

                    {item.inputType === "email" && (
                      <Mail size={18} />
                    )}

                    {item.inputType === "screenshot" && (
                      <ImageIcon size={18} />
                    )}

                    {item.inputType === "qr" && (
                      <QrCode size={18} />
                    )}
                  </div>

                  <div className="history-content">
                    <div className="history-meta">
                      <span>{item.inputLabel}</span>
                      <time>{item.createdAt}</time>
                    </div>

                    <p>{item.content}</p>
                  </div>

                  <div className="history-result">
                    {item.result?.risk_level && (
                      <>
                        <strong>{item.result.risk_level}</strong>
                        <span>
                          {item.result.risk_score}/100
                        </span>
                      </>
                    )}

                    <ChevronRight size={17} />
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>

        {/* ABOUT */}
        <section id="about" className="about-section">
          <div className="about-icon">
            <Shield size={23} />
          </div>

          <div>
            <span className="eyebrow">ABOUT CONTEXTSHIELD</span>

            <h2>Detect. Explain. Protect.</h2>

            <p>
              ContextShield analyzes suspicious digital content and
              provides a risk assessment together with human-readable
              reasons and safer next steps.
            </p>
          </div>
        </section>
      </main>

      <footer>
        <Shield size={15} />
        ContextShield
        <span>•</span>
        Explainable Scam Detection
      </footer>
    </div>
  );
}

function Result({ result, reset, copyResult }) {
  if (result.error) {
    return (
      <section className="result-panel result-error">
        <AlertTriangle size={23} />

        <div>
          <strong>Analysis unavailable</strong>
          <p>{result.error}</p>
        </div>
      </section>
    );
  }

  const level = String(result.risk_level || "").toUpperCase();

  const riskClass =
    level === "HIGH"
      ? "risk-high"
      : level === "MEDIUM"
      ? "risk-medium"
      : "risk-low";

  return (
    <section className={`result-panel ${riskClass}`}>
      <div className="result-top">
        <div>
          <span className="eyebrow">STEP 03 · RESULT</span>

          <div className="risk-title">
            <span className="risk-status-dot" />

            {level === "HIGH"
              ? "HIGH RISK"
              : level === "MEDIUM"
              ? "MEDIUM RISK"
              : "LOW RISK"}
          </div>

          <h2>{result.category || "Potential Scam"}</h2>

          <p className="result-language">
            Detected language:{" "}
            <strong>{result.language || "Unknown"}</strong>
          </p>
        </div>

        <div className="score-card">
          <div className="score-number">
            {result.risk_score ?? "--"}
          </div>

          <span>/ 100</span>

          <small>Risk Score</small>
        </div>
      </div>

      <div className="result-grid">
        {/* WHY */}
        <div className="reason-card">
          <div className="result-card-heading">
            <div className="reason-heading-icon">
              <AlertTriangle size={17} />
            </div>

            <div>
              <span>WHY?</span>
              <strong>Why this looks suspicious</strong>
            </div>
          </div>

          <div className="reason-list">
            {(result.reasons || []).map((reason, index) => (
              <div className="reason-item" key={`${reason}-${index}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{reason}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ACTION */}
        <div className="action-card">
          <div className="result-card-heading">
            <div className="action-heading-icon">
              <ShieldCheck size={17} />
            </div>

            <div>
              <span>WHAT TO DO</span>
              <strong>Stay protected</strong>
            </div>
          </div>

          <p className="safe-action">
            {result.safe_action ||
              "Avoid interacting with the suspicious content until it is verified."}
          </p>

          {result.official_url && (
            <a
              href={result.official_url}
              target="_blank"
              rel="noreferrer"
              className="official-button"
            >
              Visit Official Source
              <ExternalLink size={15} />
            </a>
          )}
        </div>
      </div>

      <div className="result-footer">
        <span>
          Analysis engine:{" "}
          <strong>
            {result.engine || "ContextShield"}
          </strong>
        </span>

        <div>
          <button onClick={copyResult}>
            <Copy size={14} />
            Copy result
          </button>

          <button onClick={reset}>
            <RotateCcw size={14} />
            Analyze another
          </button>
        </div>
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);