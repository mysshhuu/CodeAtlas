import { useEffect, useMemo, useState } from "react";
import "./App.css";
import MarkdownContent from "./MarkdownContent";

const API_URL = "https://codeatlas-api-jrw5.onrender.com";

const initialRepository = "https://github.com/tiangolo/fastapi";

function App() {
  const [activePage, setActivePage] = useState("overview");

  const [repositoryUrl, setRepositoryUrl] =
    useState(initialRepository);

  const [repository, setRepository] = useState(null);
  const [repositoryFiles, setRepositoryFiles] = useState([]);

  const [isBackendConnected, setIsBackendConnected] =
    useState(false);

  const [isIndexing, setIsIndexing] = useState(false);
  const [indexError, setIndexError] = useState("");

  const [question, setQuestion] = useState(
    "Where is the FastAPI class implemented?"
  );

  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState("");

  const [fileSearch, setFileSearch] = useState("");

  const [dependencyData, setDependencyData] = useState(null);
  const [isLoadingDependencies, setIsLoadingDependencies] = useState(false);
  const [dependencyError, setDependencyError] = useState("");

  const [historyData, setHistoryData] = useState(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState("");

  /* ========================================================
     RESTORE LAST INDEXED REPOSITORY
     ======================================================== */

  useEffect(() => {
    try {
      const saved = localStorage.getItem(
        "codeatlas_repository"
      );

      if (!saved) {
        return;
      }

      const parsed = JSON.parse(saved);

      if (
        parsed &&
        parsed.name &&
        parsed.url &&
        Number(parsed.files) > 0 &&
        Number(parsed.chunks) > 0
      ) {
        setRepository({
          name: parsed.name,
          url: parsed.url,
          path: parsed.path || "",
          files: Number(parsed.files),
          chunks: Number(parsed.chunks),
        });

        setRepositoryUrl(parsed.url);
      }
    } catch (error) {
      console.error(
        "Could not restore repository:",
        error
      );

      localStorage.removeItem(
        "codeatlas_repository"
      );
    }
  }, []);

  /* ========================================================
     BACKEND CHECK
     ======================================================== */

  useEffect(() => {
    checkBackend();
  }, []);

  async function checkBackend() {
    try {
      const response = await fetch(
        `${API_URL}/health`
      );

      if (!response.ok) {
        setIsBackendConnected(false);
        return;
      }

      setIsBackendConnected(true);

      /*
       * IMPORTANT:
       *
       * This only loads the FILE EXPLORER data.
       *
       * It does NOT change repository.files
       * or repository.chunks.
       *
       * The dashboard statistics come from
       * POST /repository/index.
       */
      await loadRepositoryFiles();
    } catch (error) {
      console.error(
        "Backend connection failed:",
        error
      );

      setIsBackendConnected(false);
    }
  }

  /* ========================================================
     LOAD REPOSITORY FILES
     ======================================================== */

  async function loadRepositoryFiles() {
    try {
      const response = await fetch(
        `${API_URL}/repository/files`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (!data.repository_path) {
        return;
      }

      const files = data.files || [];

      /*
       * ONLY store these for the Files page.
       *
       * DO NOT use data.files.length for dashboard
       * statistics.
       *
       * DO NOT calculate chunks from these files.
       *
       * The backend may return the entire cloned
       * repository here.
       */
      setRepositoryFiles(files);
    } catch (error) {
      console.error(
        "Could not load repository files:",
        error
      );
    }
  }

  /* ========================================================
     LOAD DEPENDENCIES
     ======================================================== */

  useEffect(() => {
    if (
      activePage !== "dependencies" ||
      !repository
    ) {
      return;
    }

    loadDependencies();
  }, [activePage, repository]);

  async function loadDependencies() {
    setIsLoadingDependencies(true);
    setDependencyError("");

    try {
      const response = await fetch(
        `${API_URL}/repository/dependencies`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not load dependency graph."
        );
      }

      setDependencyData(data);
    } catch (error) {
      console.error(
        "Dependency graph error:",
        error
      );

      setDependencyError(
        error.message ||
          "Could not load dependency graph."
      );
    } finally {
      setIsLoadingDependencies(false);
    }
  }

  /* ========================================================
     LOAD GIT HISTORY
     ======================================================== */

  useEffect(() => {
    if (
      activePage !== "history" ||
      !repository
    ) {
      return;
    }

    loadHistory();
  }, [activePage, repository]);

  async function loadHistory() {
    setIsLoadingHistory(true);
    setHistoryError("");

    try {
      const response = await fetch(
        `${API_URL}/repository/history`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not load Git history."
        );
      }

      setHistoryData(data);
    } catch (error) {
      console.error(
        "Git history error:",
        error
      );

      setHistoryError(
        error.message ||
          "Could not load Git history."
      );
    } finally {
      setIsLoadingHistory(false);
    }
  }

  /* ========================================================
     INDEX REPOSITORY
     ======================================================== */

  async function indexRepository() {
    const url = repositoryUrl.trim();

    if (!url) {
      setIndexError(
        "Please enter a GitHub repository URL."
      );
      return;
    }

    if (!url.includes("github.com/")) {
      setIndexError(
        "Please enter a valid GitHub repository URL."
      );
      return;
    }

    setIsIndexing(true);
    setIndexError("");

    try {
      const response = await fetch(
        `${API_URL}/repository/index`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_url: url,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Repository indexing failed."
        );
      }

      console.log(
        "CODEATLAS INDEX RESULT:",
        data
      );

      /*
       * The backend returns:
       *
       * {
       *   message: "...",
       *   repository_url: "...",
       *   repository_path: "...",
       *   files: 48,
       *   chunks: 520
       * }
       *
       * These are the numbers we want.
       */

      const cleanUrl =
        data.repository_url || url;

      const urlParts = cleanUrl
        .replace(/\/+$/, "")
        .split("/");

      let repositoryName =
        urlParts[urlParts.length - 1] ||
        "repository";

      repositoryName =
        repositoryName.replace(
          /\.git$/,
          ""
        );

      const indexedFiles = Number(
        data.files ?? 0
      );

      const indexedChunks = Number(
        data.chunks ?? 0
      );

      /*
       * Safety check.
       *
       * If the backend somehow doesn't return
       * the indexing statistics, don't create
       * a fake repository with 0 chunks.
       */
      if (
        indexedFiles <= 0 ||
        indexedChunks <= 0
      ) {
        console.warn(
          "Unexpected indexing result:",
          data
        );
      }

      const indexedRepository = {
        name: repositoryName,
        url: cleanUrl,
        path:
          data.repository_path || "",
        files: indexedFiles,
        chunks: indexedChunks,
      };

      /*
       * THIS is the state used by the dashboard.
       */
      setRepository(
        indexedRepository
      );

      /*
       * Save the EXACT indexing result.
       */
      localStorage.setItem(
        "codeatlas_repository",
        JSON.stringify(
          indexedRepository
        )
      );

      setIsBackendConnected(true);

      setAnswer("");
      setSources([]);

      /*
       * Load file explorer separately.
       *
       * This cannot overwrite the 48 / 520
       * statistics.
       */
      await loadRepositoryFiles();
    } catch (error) {
      console.error(
        "Repository indexing error:",
        error
      );

      setIndexError(
        error.message ||
          "Could not connect to the backend."
      );
    } finally {
      setIsIndexing(false);
    }
  }

  /* ========================================================
     ASK CODEBASE
     ======================================================== */

  async function askCodebase() {
    if (!question.trim() || isAsking) {
      return;
    }

    if (!repository) {
      setAskError(
        "Please index a repository before asking questions."
      );
      return;
    }

    setIsAsking(true);
    setAskError("");

    try {
      const response = await fetch(
        `${API_URL}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question.trim(),
            limit: 5,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Could not generate an answer."
        );
      }

      setAnswer(
        data.answer || ""
      );

      setSources(
        data.sources || []
      );
    } catch (error) {
      console.error(
        "Ask error:",
        error
      );

      setAskError(
        error.message ||
          "Could not connect to the CodeAtlas AI service."
      );
    } finally {
      setIsAsking(false);
    }
  }

  function handleQuestionKeyDown(
    event
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askCodebase();
    }
  }

  function useSuggestedQuestion(
    value
  ) {
    setQuestion(value);
    setActivePage("overview");

    setTimeout(() => {
      document
        .getElementById(
          "ai-assistant"
        )
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  }

  /* ========================================================
     FILTER FILES
     ======================================================== */

  const filteredFiles = useMemo(() => {
    const search = fileSearch
      .trim()
      .toLowerCase();

    if (!search) {
      return repositoryFiles;
    }

    return repositoryFiles.filter(
      (file) =>
        file.file_path
          ?.toLowerCase()
          .includes(search)
    );
  }, [
    repositoryFiles,
    fileSearch,
  ]);

  /* ========================================================
     RENDER
     ======================================================== */

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            C
          </div>

          <div>
            <div className="brand-name">
              CodeAtlas
            </div>

            <div className="brand-subtitle">
              CODEBASE INTELLIGENCE
            </div>
          </div>

        </div>

        <nav className="navigation">

          <NavButton
            id="overview"
            label="Overview"
            icon="⌂"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            id="files"
            label="Files"
            icon="▣"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            id="dependencies"
            label="Dependencies"
            icon="⌘"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            id="history"
            label="Git History"
            icon="◷"
            activePage={activePage}
            setActivePage={setActivePage}
          />

        </nav>

        <div className="sidebar-bottom">

          <div className="sidebar-label">
            AI ASSISTANT
          </div>

          <button
            className={`ai-nav-button ${
              activePage === "overview"
                ? "selected"
                : ""
            }`}
            onClick={() => {
              setActivePage(
                "overview"
              );

              setTimeout(() => {
                document
                  .getElementById(
                    "ai-assistant"
                  )
                  ?.scrollIntoView({
                    behavior:
                      "smooth",
                  });
              }, 50);
            }}
          >
            <span>✦</span>
            Ask CodeAtlas
          </button>

        </div>

      </aside>

      {/* MAIN */}

      <main className="main-content">

        <header className="topbar">

          <div className="topbar-repository">

            {repository ? (
              <>
                <span className="topbar-dot" />
                {repository.name}
              </>
            ) : (
              "No repository"
            )}

          </div>

          <div
            className={`connection-status ${
              isBackendConnected
                ? "connected"
                : "disconnected"
            }`}
          >

            <span className="status-dot" />

            {isBackendConnected
              ? "Backend connected"
              : "Backend offline"}

          </div>

        </header>

        {/* OVERVIEW */}

        {activePage ===
          "overview" && (
          <OverviewPage
            repositoryUrl={
              repositoryUrl
            }
            setRepositoryUrl={
              setRepositoryUrl
            }
            repository={
              repository
            }
            isIndexing={
              isIndexing
            }
            indexError={
              indexError
            }
            indexRepository={
              indexRepository
            }
            question={
              question
            }
            setQuestion={
              setQuestion
            }
            answer={answer}
            sources={sources}
            isAsking={
              isAsking
            }
            askError={
              askError
            }
            askCodebase={
              askCodebase
            }
            handleQuestionKeyDown={
              handleQuestionKeyDown
            }
            useSuggestedQuestion={
              useSuggestedQuestion
            }
          />
        )}

        {/* FILES */}

        {activePage === "files" && (
          <FilesPage
            repository={
              repository
            }
            files={
              filteredFiles
            }
            totalFiles={
              repositoryFiles.length
            }
            search={
              fileSearch
            }
            setSearch={
              setFileSearch
            }
          />
        )}

        {/* DEPENDENCIES */}

        {activePage ===
          "dependencies" && (
          <DependenciesPage
            repository={
              repository
            }
            files={
              repositoryFiles
            }
            dependencyData={
              dependencyData
            }
            isLoading={
              isLoadingDependencies
            }
            error={
              dependencyError
            }
          />
        )}

        {/* HISTORY */}

        {activePage === "history" && (
          <HistoryPage
            repository={
              repository
            }
            historyData={
              historyData
            }
            isLoading={
              isLoadingHistory
            }
            error={
              historyError
            }
          />
        )}

      </main>

    </div>
  );
}


/* ==========================================================
   NAV BUTTON
   ========================================================== */

function NavButton({
  id,
  label,
  icon,
  activePage,
  setActivePage,
}) {
  return (
    <button
      className={`nav-item ${
        activePage === id
          ? "active"
          : ""
      }`}
      onClick={() =>
        setActivePage(id)
      }
    >

      <span className="nav-icon">
        {icon}
      </span>

      <span>{label}</span>

    </button>
  );
}


/* ==========================================================
   OVERVIEW PAGE
   ========================================================== */

function OverviewPage({
  repositoryUrl,
  setRepositoryUrl,
  repository,
  isIndexing,
  indexError,
  indexRepository,
  question,
  setQuestion,
  answer,
  sources,
  isAsking,
  askError,
  askCodebase,
  handleQuestionKeyDown,
  useSuggestedQuestion,
}) {
  return (
    <div className="page">

      <section className="hero">

        <div className="eyebrow">
          REPOSITORY INTELLIGENCE
        </div>

        <h1>
          Understand your
          <br />
          codebase.
        </h1>

        <p>
          Explore architecture,
          dependencies and code
          with AI-powered search.
        </p>

      </section>


      {/* REPOSITORY */}

      <section className="repository-card card">

        <div className="section-label">
          REPOSITORY
        </div>

        <h2>
          Connect a GitHub repository
        </h2>

        <div className="repository-form">

          <div className="url-input-wrapper">

            <span className="input-icon">
              ↗
            </span>

            <input
              value={
                repositoryUrl
              }
              onChange={(event) =>
                setRepositoryUrl(
                  event.target.value
                )
              }
              placeholder="https://github.com/owner/repository"
              disabled={
                isIndexing
              }
              onKeyDown={(event) => {
                if (
                  event.key ===
                  "Enter"
                ) {
                  indexRepository();
                }
              }}
            />

          </div>

          <button
            className="primary-button index-button"
            onClick={
              indexRepository
            }
            disabled={
              isIndexing
            }
          >

            {isIndexing ? (
              <>
                <span className="spinner" />
                Indexing...
              </>
            ) : (
              <>
                Index Repository
                <span>→</span>
              </>
            )}

          </button>

        </div>

        {isIndexing && (
          <div className="indexing-message">

            <span className="spinner small" />

            Cloning, parsing and
            embedding the
            repository...

          </div>
        )}

        {indexError && (
          <div className="error-banner">

            <strong>
              Something went wrong
            </strong>

            <span>
              {indexError}
            </span>

          </div>
        )}

      </section>


      {/* STATS */}

      <section className="stats-grid">

        <StatCard
          icon="◇"
          label="REPOSITORY"
          value={
            repository
              ? repository.name
              : "No repository indexed"
          }
        />

        <StatCard
          icon="▣"
          label="SOURCE FILES"
          value={
            repository
              ? repository.files
              : 0
          }
        />

        <StatCard
          icon="✦"
          label="CODE CHUNKS"
          value={
            repository
              ? repository.chunks
              : 0
          }
        />

      </section>


      {/* QUICK INSIGHT */}

      {repository && (
        <section className="quick-insight-grid">

          <div className="insight-card">

            <div className="insight-icon">
              ✓
            </div>

            <div>

              <strong>
                Repository indexed
              </strong>

              <p>
                CodeAtlas has analyzed
                the repository and
                prepared it for
                semantic search.
              </p>

            </div>

          </div>

          <div className="insight-card">

            <div className="insight-icon">
              ✦
            </div>

            <div>

              <strong>
                AI ready
              </strong>

              <p>
                Ask natural-language
                questions about the
                implementation.
              </p>

            </div>

          </div>

        </section>
      )}


      {/* AI */}

      <section
        className="ai-card card"
        id="ai-assistant"
      >

        <div className="ai-header">

          <div>

            <div className="section-label purple">
              CODEATLAS AI
            </div>

            <h2>
              Ask anything about your
              codebase
            </h2>

            <p>
              CodeAtlas searches your
              indexed code and explains
              the answer with source
              locations.
            </p>

          </div>

          <div className="rag-badge">
            ✦ RAG
          </div>

        </div>


        <div className="question-box">

          <textarea
            value={
              question
            }
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            onKeyDown={
              handleQuestionKeyDown
            }
            placeholder="e.g. Where is authentication implemented?"
            disabled={
              isAsking
            }
          />

          <button
            className="ask-button"
            onClick={
              askCodebase
            }
            disabled={
              isAsking ||
              !question.trim()
            }
          >

            {isAsking ? (
              <>
                <span className="spinner" />
                Thinking...
              </>
            ) : (
              <>
                Ask CodeAtlas
                <span>↑</span>
              </>
            )}

          </button>

        </div>


        <div className="suggestions">

          <span className="try-label">
            Try asking:
          </span>

          <button
            onClick={() =>
              useSuggestedQuestion(
                "Where is the FastAPI class implemented?"
              )
            }
          >
            Where is the FastAPI
            class implemented?
          </button>

          <button
            onClick={() =>
              useSuggestedQuestion(
                "How does routing work?"
              )
            }
          >
            How does routing work?
          </button>

          <button
            onClick={() =>
              useSuggestedQuestion(
                "Where is authentication implemented?"
              )
            }
          >
            Where is authentication
            implemented?
          </button>

        </div>


        {askError && (
          <div className="error-banner">

            <strong>
              Could not answer the
              question
            </strong>

            <span>
              {askError}
            </span>

          </div>
        )}

      </section>


      {answer && (
        <AnswerSection
          answer={answer}
          sources={sources}
        />
      )}

    </div>
  );
}


/* ==========================================================
   STAT CARD
   ========================================================== */

function StatCard({
  icon,
  label,
  value,
}) {
  return (
    <div className="stat-card card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>

        <div className="stat-label">
          {label}
        </div>

        <div className="stat-value">
          {value}
        </div>

      </div>

    </div>
  );
}


/* ==========================================================
   ANSWER
   ========================================================== */

function AnswerSection({
  answer,
  sources,
}) {
  return (
    <section className="answer-card card">

      <div className="answer-header">

        <div>

          <div className="section-label purple">
            CODEATLAS RESPONSE
          </div>

        </div>

        <span className="generated">
          Answer generated
        </span>

      </div>

      <div className="answer-content">
        <MarkdownContent content={answer} />
      </div>


      {sources.length > 0 && (
        <div className="sources-section">

          <div className="sources-heading">

            <div>

              <div className="section-label">
                RETRIEVED CODE
              </div>

              <h3>
                Sources
              </h3>

            </div>

            <span className="source-count">
              {sources.length} relevant
              {sources.length === 1 ? " chunk" : " chunks"}
            </span>

          </div>


          <div className="source-list">

            {sources.map(
              (
                source,
                index
              ) => {
                const cleanPath =
                  (source.file_path || "")
                    .replace(
                      /^.*?[\\/]repos[\\/][^\\/]+[\\/]/,
                      ""
                    )
                    .replace(
                      /\\/g,
                      "/"
                    );

                const score = Math.round(
                  (source.score || 0) * 100
                );

                return (
                  <div
                    className="source-row"
                    key={`${source.file_path}-${source.start_line}-${index}`}
                  >

                    <div className="source-number">
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </div>

                    <div className="source-type">
                      CODE
                    </div>

                    <div className="source-main">

                      <div className="source-path">
                        {cleanPath ||
                          "Unknown source"}
                      </div>

                      <div className="source-meta">

                        <span className="source-symbol">
                          {source.symbol ||
                            "module"}
                        </span>

                        <span>
                          •
                        </span>

                        <span>
                          Lines{" "}
                          {source.start_line}
                          –
                          {source.end_line}
                        </span>

                      </div>

                    </div>

                    <div className="source-score">
                      <span className="score-value">
                        {score}%
                      </span>
                      <span className="score-label">
                        match
                      </span>
                    </div>

                  </div>
                );
              }
            )}

          </div>

        </div>
      )}

    </section>
  );
}


/* ==========================================================
   FILES PAGE
   ========================================================== */

function FilesPage({
  repository,
  files,
  totalFiles,
  search,
  setSearch,
}) {
  return (
    <div className="page">

      <PageHero
        eyebrow="SOURCE EXPLORER"
        title="Files"
        description={
          repository
            ? `Explore the ${repository.name} source tree.`
            : "Explore the indexed source code."
        }
      />

      {!repository ? (
        <EmptyState
          icon="▣"
          title="No repository indexed"
          description="Connect and index a GitHub repository from the Overview page to explore its source files."
        />
      ) : (
        <section className="page-card">

          <div className="page-card-header">

            <div>

              <div className="section-label">
                SOURCE TREE
              </div>

              <h2>
                Repository files
              </h2>

            </div>

            <span className="page-count">
              {totalFiles} files
            </span>

          </div>


          <div className="file-search">

            <span>
              🔎
            </span>

            <input
              value={
                search
              }
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search files..."
            />

          </div>


          {files.length ===
          0 ? (
            <div className="empty-inline">
              No files match your
              search.
            </div>
          ) : (
            <div className="file-list">

              {files.map(
                (
                  file,
                  index
                ) => (
                  <div
                    className="file-row"
                    key={`${file.file_path}-${index}`}
                  >

                    <div className="file-icon">
                      {file.language ===
                      "Python"
                        ? "PY"
                        : "FILE"}
                    </div>

                    <div className="file-details">

                      <div className="file-name">
                        {
                          file.file_path
                        }
                      </div>

                      <div className="file-meta">

                        {
                          file.language ||
                          "Unknown"
                        }

                        <span>
                          {" · "}
                        </span>

                        {
                          file.chunks ||
                          0
                        }{" "}
                        chunks

                      </div>

                    </div>

                    <div className="file-score">

                      {
                        file.chunks ||
                        0
                      }

                    </div>

                  </div>
                )
              )}

            </div>
          )}

        </section>
      )}

    </div>
  );
}


/* ==========================================================
   DEPENDENCIES PAGE
   ========================================================== */

/* =========================================================
   DEPENDENCIES PAGE
   ========================================================= */

function DependenciesPage({
  repository,
  files,
  dependencyData,
  isLoading,
  error,
}) {
  const pythonFiles =
    files.filter(
      (file) =>
        file.language === "Python" ||
        file.file_path
          ?.toLowerCase()
          .endsWith(".py")
    );

  const totalChunks =
    files.reduce(
      (total, file) =>
        total + Number(file.chunks || 0),
      0
    );

  const graphFiles =
    dependencyData?.files ??
    pythonFiles.length;

  const graphNodes =
    dependencyData?.nodes ?? 0;

  const graphFunctions =
    dependencyData?.functions ?? 0;

  const graphClasses =
    dependencyData?.classes ?? 0;

  const graphCalls =
    dependencyData?.calls ?? 0;

  const nodes =
    dependencyData?.nodes_data ?? [];

  const edges =
    dependencyData?.edges ?? [];

  /*
   * Show a useful sample instead of dumping
   * thousands of relationships onto the page.
   */
  const visibleNodes =
    nodes.slice(0, 12);

  const visibleEdges =
    edges.slice(0, 20);

  function formatNodeType(
    value
  ) {
    if (!value) {
      return "code";
    }

    return value
      .replace(
        /^./,
        (character) =>
          character.toUpperCase()
      );
  }

  function formatEdgeName(
    value
  ) {
    if (!value) {
      return "Unknown";
    }

    const parts =
      value.split(":");

    return parts[
      parts.length - 1
    ];
  }

  return (
    <div className="page">

      <PageHero
        eyebrow="ARCHITECTURE"
        title="Dependencies"
        description="Explore the structural relationships discovered inside the repository."
      />

      {!repository ? (
        <EmptyState
          icon="⌘"
          title="No repository indexed"
          description="Index a repository first to build its code structure and dependency graph."
        />
      ) : (
        <>

          {error && (
            <div className="error-banner">

              <strong>
                Could not load dependencies
              </strong>

              <span>
                {error}
              </span>

            </div>
          )}

          {/* =================================================
              GRAPH SUMMARY
              ================================================= */}

          <section className="page-card">

            <div className="page-card-header">

              <div>

                <div className="section-label">
                  CODE GRAPH
                </div>

                <h2>
                  Repository structure
                </h2>

              </div>

              <span className="graph-live">

                ●{" "}

                {isLoading
                  ? "Loading"
                  : "Indexed"}

              </span>

            </div>


            <div className="dependency-graph">

              <div className="graph-node graph-root">

                <span>
                  ◇
                </span>

                {repository.name}

              </div>


              <div className="graph-connector" />


              <div className="graph-row">

                <div className="graph-node">

                  <span>
                    ▣
                  </span>

                  {graphFiles} Files

                </div>


                <div className="graph-node">

                  <span>
                    ƒ
                  </span>

                  {graphFiles} Python

                </div>


                <div className="graph-node">

                  <span>
                    ✦
                  </span>

                  {repository.chunks ??
                    totalChunks} Chunks

                </div>

              </div>


              <div className="graph-connector" />


              <div className="graph-row">

                <div className="graph-node">

                  <span>
                    ƒ
                  </span>

                  {graphFunctions} Functions

                </div>


                <div className="graph-node">

                  <span>
                    ◇
                  </span>

                  {graphClasses} Classes

                </div>


                <div className="graph-node">

                  <span>
                    →
                  </span>

                  {graphCalls} Calls

                </div>

              </div>


              <p className="graph-description">

                CodeAtlas analyzes source
                code structurally by
                extracting classes,
                functions and function
                calls.

                {" "}

                The current graph contains{" "}

                <strong>
                  {graphNodes}
                </strong>{" "}

                code nodes and{" "}

                <strong>
                  {graphCalls}
                </strong>{" "}

                call relationships.

              </p>

            </div>

          </section>


          {/* =================================================
              REAL CODE NODES
              ================================================= */}

          <section className="page-card dependency-data-card">

            <div className="page-card-header">

              <div>

                <div className="section-label">
                  STRUCTURAL NODES
                </div>

                <h2>
                  Code entities
                </h2>

              </div>

              <span className="page-count">
                {graphNodes} total
              </span>

            </div>


            {isLoading ? (

              <div className="empty-inline">

                <span className="spinner small" />

                Loading code graph...

              </div>

            ) : visibleNodes.length === 0 ? (

              <div className="empty-inline">

                No structural nodes were found.

              </div>

            ) : (

              <div className="dependency-node-list">

                {visibleNodes.map(
                  (node, index) => (

                    <div
                      className="dependency-node-row"
                      key={
                        node.id ||
                        index
                      }
                    >

                      <div className="dependency-node-number">

                        {String(
                          index + 1
                        ).padStart(
                          2,
                          "0"
                        )}

                      </div>


                      <div className="dependency-node-icon">

                        {node.node_type ===
                        "class"
                          ? "◇"
                          : "ƒ"}

                      </div>


                      <div className="dependency-node-main">

                        <div className="dependency-node-name">

                          {node.name}

                        </div>


                        <div className="dependency-node-meta">

                          <span>
                            {formatNodeType(
                              node.node_type
                            )}
                          </span>

                          <span>
                            •
                          </span>

                          <span>
                            {node.file_path}
                          </span>

                          <span>
                            •
                          </span>

                          <span>
                            Lines{" "}
                            {node.start_line}
                            –
                            {node.end_line}
                          </span>

                        </div>

                      </div>

                    </div>

                  )
                )}

              </div>

            )}

          </section>


          {/* =================================================
              REAL CALL RELATIONSHIPS
              ================================================= */}

          <section className="page-card dependency-data-card">

            <div className="page-card-header">

              <div>

                <div className="section-label">
                  CALL RELATIONSHIPS
                </div>

                <h2>
                  How code connects
                </h2>

              </div>

              <span className="page-count">
                {graphCalls} total
              </span>

            </div>


            {isLoading ? (

              <div className="empty-inline">

                <span className="spinner small" />

                Loading relationships...

              </div>

            ) : visibleEdges.length === 0 ? (

              <div className="empty-inline">

                No call relationships were found.

              </div>

            ) : (

              <div className="dependency-edge-list">

                {visibleEdges.map(
                  (edge, index) => (

                    <div
                      className="dependency-edge-row"
                      key={`${edge.source}-${edge.target}-${index}`}
                    >

                      <div className="dependency-edge-number">

                        {String(
                          index + 1
                        ).padStart(
                          2,
                          "0"
                        )}

                      </div>


                      <div className="dependency-edge-source">

                        {formatEdgeName(
                          edge.source
                        )}

                      </div>


                      <div className="dependency-edge-arrow">

                        →

                      </div>


                      <div className="dependency-edge-target">

                        {formatEdgeName(
                          edge.target
                        )}

                      </div>


                      <div className="dependency-edge-label">

                        {edge.relationship ||
                          "calls"}

                      </div>

                    </div>

                  )
                )}

              </div>

            )}


            {edges.length > 20 && (

              <div className="dependency-more">

                Showing 20 of{" "}
                {edges.length}{" "}
                call relationships.

                The complete graph is available
                through the CodeAtlas API.

              </div>

            )}

          </section>


          {/* =================================================
              EXPLANATION
              ================================================= */}

          <div className="feature-grid">

            <Feature
              icon="◇"
              title="Code nodes"
              text={`${graphNodes} structural nodes were discovered across the repository.`}
            />


            <Feature
              icon="→"
              title="Call relationships"
              text={`${graphCalls} function-call relationships were extracted from the Python AST.`}
            />


            <Feature
              icon="✦"
              title="Semantic retrieval"
              text={`${repository.chunks} code chunks are available for natural-language retrieval.`}
            />

          </div>

        </>
      )}

    </div>
  );
}

/* ==========================================================
   HISTORY PAGE
   ========================================================== */

function HistoryPage({
  repository,
  historyData,
  isLoading,
  error,
}) {
  const commits =
    historyData?.commits || [];

  function formatCommitDate(
    value
  ) {
    if (!value) {
      return "Unknown date";
    }

    try {
      return new Date(
        value
      ).toLocaleString(
        undefined,
        {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }
      );
    } catch {
      return value;
    }
  }

  return (
    <div className="page">

      <PageHero
        eyebrow="VERSION INTELLIGENCE"
        title="Git History"
        description="Understand how the repository evolves over time."
      />

      {!repository ? (
        <EmptyState
          icon="◷"
          title="No repository indexed"
          description="Index a GitHub repository to start exploring repository intelligence."
        />
      ) : (
        <>

          {error && (
            <div className="error-banner">
              <strong>
                Could not load Git history
              </strong>
              <span>
                {error}
              </span>
            </div>
          )}

          <section className="page-card">

            <div className="page-card-header">

              <div>

                <div className="section-label">
                  REPOSITORY HISTORY
                </div>

                <h2>
                  {repository.name}
                </h2>

              </div>

              <span className="page-count">
                {isLoading
                  ? "Loading..."
                  : `${commits.length} commits`}
              </span>

            </div>

            {isLoading ? (
              <div className="empty-inline">
                <span className="spinner small" />
                Loading Git history...
              </div>
            ) : commits.length === 0 ? (
              <div className="empty-inline">
                No Git commits were found in this repository.
              </div>
            ) : (
              <div className="timeline">

                {commits.map(
                  (
                    commit,
                    index
                  ) => (
                    <div
                      className="timeline-item"
                      key={
                        commit.hash ||
                        index
                      }
                    >

                      <div className="timeline-dot" />

                      <div>

                        <div className="timeline-title">
                          {commit.message ||
                            "No commit message"}
                        </div>

                        <div className="timeline-text">
                          {commit.author ||
                            "Unknown author"}
                          {" · "}
                          {formatCommitDate(
                            commit.date
                          )}
                        </div>

                        <div className="timeline-text">
                          <span>
                            {commit.short_hash ||
                              commit.hash?.slice(
                                0,
                                7
                              )}
                          </span>
                        </div>

                      </div>

                    </div>
                  )
                )}

              </div>
            )}

          </section>

          <div className="info-banner">

            <strong>
              Real Git intelligence
            </strong>

            <span>
              CodeAtlas is reading the
              repository's Git history
              directly from the cloned
              repository. The dashboard
              currently shows the 20 most
              recent commits with their
              message, author, timestamp
              and commit hash.
            </span>

          </div>

        </>
      )}

    </div>
  );
}

/* ==========================================================
   PAGE HERO
   ========================================================== */

function PageHero({
  eyebrow,
  title,
  description,
}) {
  return (
    <section className="page-hero">

      <div className="eyebrow">
        {eyebrow}
      </div>

      <h1>
        {title}
      </h1>

      <p>
        {description}
      </p>

    </section>
  );
}


/* ==========================================================
   EMPTY STATE
   ========================================================== */

function EmptyState({
  icon,
  title,
  description,
}) {
  return (
    <div className="empty-state">

      <div className="empty-icon">
        {icon}
      </div>

      <h2>
        {title}
      </h2>

      <p>
        {description}
      </p>

    </div>
  );
}


/* ==========================================================
   FEATURE
   ========================================================== */

function Feature({
  icon,
  title,
  text,
}) {
  return (
    <div className="feature-item">

      <div className="feature-icon">
        {icon}
      </div>

      <div>

        <strong>
          {title}
        </strong>

        <p>
          {text}
        </p>

      </div>

    </div>
  );
}


/* ==========================================================
   TIMELINE ITEM
   ========================================================== */

function TimelineItem({
  title,
  text,
}) {
  return (
    <div className="timeline-item">

      <div className="timeline-dot" />

      <div>

        <div className="timeline-title">
          {title}
        </div>

        <div className="timeline-text">
          {text}
        </div>

      </div>

    </div>
  );
}


/* ==========================================================
   EXPORT
   ========================================================== */

export default App;