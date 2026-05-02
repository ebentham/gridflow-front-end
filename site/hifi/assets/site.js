/* Shared site chrome: nav + footer, injected per page.
   Each page sets <body data-page="home|sources|vendor|dataset"> and we mark active link. */

(function () {
  const page = document.body.dataset.page || "";
  const root = document.body.dataset.root || ""; // path back to /hifi

  const navHTML = `
    <nav class="nav">
      <div class="nav-inner">
        <a href="${root}index.html" class="nav-logo">
          <span class="mark"></span>
          <span>Gridflow</span>
        </a>
        <div class="nav-links">
          <a href="${root}index.html"           data-key="home">Overview</a>
          <a href="${root}data-sources.html"    data-key="sources">Data sources</a>
          <a href="${root}#pipelines"           data-key="pipelines">Pipelines</a>
          <a href="${root}#schemas"             data-key="schemas">Schemas</a>
          <a href="${root}#changelog"           data-key="changelog">Changelog</a>
        </div>
        <div class="nav-search">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"></circle><path d="m21 21-4.3-4.3"></path></svg>
          <span>Search datasets, fields, codes…</span>
          <kbd>⌘K</kbd>
        </div>
      </div>
    </nav>
  `;

  const footerHTML = `
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-grid">
          <div>
            <a href="${root}index.html" class="nav-logo" style="margin-bottom:14px">
              <span class="mark"></span>
              <span>Gridflow</span>
            </a>
            <p class="small" style="max-width:340px">
              A personal data warehouse for European energy markets.
              Bronze · silver · gold layers built on open data.
            </p>
            <p class="tiny mt-16">v0.4.2 · build 2026.04.30</p>
          </div>
          <div>
            <h4>Catalog</h4>
            <a href="${root}data-sources.html">All sources</a>
            <a href="${root}data-sources.html#electricity">Electricity</a>
            <a href="${root}data-sources.html#gas">Gas</a>
            <a href="${root}data-sources.html#weather">Weather</a>
          </div>
          <div>
            <h4>Pipeline</h4>
            <a href="#">Run history</a>
            <a href="#">Schemas</a>
            <a href="#">Quality</a>
            <a href="#">Backfills</a>
          </div>
          <div>
            <h4>Reference</h4>
            <a href="#">SQL cookbook</a>
            <a href="#">Python client</a>
            <a href="#">Glossary</a>
            <a href="#">Changelog</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© 2026 Gridflow · Personal project</span>
          <span class="mono tiny">last sync 2026-04-30 14:02 UTC · 7 sources · 49 datasets</span>
        </div>
      </div>
    </footer>
  `;

  // inject
  document.body.insertAdjacentHTML("afterbegin", navHTML);
  document.body.insertAdjacentHTML("beforeend", footerHTML);

  // mark active
  if (page) {
    const map = { home: "home", sources: "sources", vendor: "sources", dataset: "sources" };
    const key = map[page];
    if (key) {
      const link = document.querySelector(`.nav-links a[data-key="${key}"]`);
      if (link) link.classList.add("active");
    }
  }

  // copy buttons
  document.querySelectorAll(".code-wrap").forEach((wrap) => {
    if (wrap.querySelector(".copy")) return;
    const btn = document.createElement("button");
    btn.className = "copy";
    btn.textContent = "Copy";
    btn.addEventListener("click", () => {
      const code = wrap.querySelector("pre, code");
      if (!code) return;
      navigator.clipboard?.writeText(code.textContent || "");
      btn.textContent = "Copied";
      btn.classList.add("copied");
      setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("copied"); }, 1200);
    });
    wrap.appendChild(btn);
  });

  // tabs
  document.querySelectorAll("[data-tabs]").forEach((group) => {
    const buttons = group.querySelectorAll(".tabs button");
    const panels = group.querySelectorAll(".tab-panel");
    buttons.forEach((b, i) => {
      b.addEventListener("click", () => {
        buttons.forEach((x) => x.classList.remove("active"));
        panels.forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
        panels[i]?.classList.add("active");
      });
    });
  });
})();
