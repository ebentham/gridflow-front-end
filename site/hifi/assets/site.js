/* Shared site chrome: nav + footer, injected per page.
   Each page sets <body data-page="home|architecture|sources|vendor|dataset|model|about">
   and we mark the active link. data-root is the path back to /hifi root. */

(function () {
  const page = document.body.dataset.page || "";
  const root = document.body.dataset.root || ""; // e.g. "" on root, "../" on /data-sources/, "../../" on /data-sources/elexon/

  const navHTML = `
    <nav class="nav">
      <div class="nav-inner">
        <a href="${root}index.html" class="nav-logo">
          <span class="mark"></span>
          <span>Gridflow</span>
        </a>
        <div class="nav-links" id="nav-links">
          <a href="${root}architecture.html"          data-key="architecture">Architecture</a>
          <a href="${root}data-sources.html"          data-key="sources">Catalogue</a>
          <a href="${root}models/demand-forecast.html" data-key="model">Models</a>
          <a href="${root}index.html#about"           data-key="about">About</a>
        </div>
        <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu" aria-expanded="false">
          <svg width="16" height="14" viewBox="0 0 16 14" fill="none" stroke="currentColor" stroke-width="1.5">
            <line x1="0" y1="1" x2="16" y2="1"></line>
            <line x1="0" y1="7" x2="16" y2="7"></line>
            <line x1="0" y1="13" x2="16" y2="13"></line>
          </svg>
          <span style="font-size:12px;font-weight:500;">Menu</span>
        </button>
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
              A personal research platform for European power markets.
              Built around a bronze–silver–gold data warehouse and a
              probabilistic modelling stack.
            </p>
            <p class="tiny mt-16">v0.4.2 · build 2026.04.30</p>
          </div>
          <div>
            <h4>Project</h4>
            <a href="${root}architecture.html">Architecture</a>
            <a href="${root}data-sources.html">Catalogue</a>
            <a href="${root}models/demand-forecast.html">Models</a>
            <a href="${root}index.html#about">About</a>
          </div>
          <div>
            <h4>Catalogue</h4>
            <a href="${root}data-sources.html#electricity">Electricity</a>
            <a href="${root}data-sources.html#gas">Gas</a>
            <a href="${root}data-sources.html#weather">Weather</a>
            <a href="${root}data-sources.html#carbon">Carbon</a>
          </div>
          <div>
            <h4>Code</h4>
            <a href="https://github.com/EBentham/gridflow" target="_blank" rel="noopener">gridflow ↗</a>
            <a href="https://github.com/EBentham/gridflow-models" target="_blank" rel="noopener">gridflow-models ↗</a>
            <a href="https://github.com/EBentham/gridflow-front-end" target="_blank" rel="noopener">gridflow-front-end ↗</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© 2026 E. Bentham · Personal project · MIT</span>
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
    const map = {
      home: null, // home doesn't highlight any nav item (logo only)
      architecture: "architecture",
      sources: "sources",
      vendor: "sources",
      dataset: "sources",
      model: "model",
      about: "about",
    };
    const key = map[page];
    if (key) {
      const link = document.querySelector(`.nav-links a[data-key="${key}"]`);
      if (link) link.classList.add("active");
    }
  }

  // mobile menu toggle
  const toggle = document.getElementById("nav-toggle");
  const links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // close menu when an in-page anchor is clicked
    links.addEventListener("click", (e) => {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
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

  // tabs — selector covers both index.html's stripped .tabs row and the
  // dataset-page chip-strip variant wrapped in .tab-buttons
  document.querySelectorAll("[data-tabs]").forEach((group) => {
    const buttons = group.querySelectorAll(".tabs button, .tab-buttons button");
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

  // scroll-spy — highlight the active in-page anchor in any sticky sidebar.
  // Gated by selector presence so it generalises to future pages (vendor
  // hubs etc.) without needing data-page checks.
  if (document.querySelector('.sidebar a[href^="#"]')) {
    const sections = document.querySelectorAll("section[id]");
    const anchors = document.querySelectorAll('.sidebar a[href^="#"]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          anchors.forEach((l) => l.classList.remove("active"));
          const match = document.querySelector('.sidebar a[href="#' + e.target.id + '"]');
          if (match) match.classList.add("active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    sections.forEach((s) => observer.observe(s));
  }
})();
