/* Static SVG chart renderers — no interactivity, just plausible visuals.
   All charts read deterministic data so they render consistently.
   Usage: <div data-chart="stacked-area" data-src="..."></div>
   We render synchronously on DOMContentLoaded. */

(function () {
  const PALETTE = {
    forest:    "#3b6b4b",
    forestDeep:"#2a4f37",
    forestSoft:"#a9c4b3",
    forestTint:"#dfeae3",
    sky:       "#7a96a8",
    rust:      "#c45a3a",
    sand:      "#c9a96e",
    plum:      "#86627d",
    slate:     "#5a5e5f",
    ink:       "#1a1714",
    inkSoft:   "#6b6358",
    rule:      "#d8d1c2",
    paper:     "#faf7f1",
  };

  // ── deterministic pseudo-random for plausible series
  function rng(seed) {
    let s = seed | 0;
    return () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  }

  // ── SHAPES: deterministic domain-shape generators ───────────
  // Each returns an array of length N. All accept opts (including seed).
  // Inputs index i in [0, N), so a sample index maps to time-of-day via i/N * 24.
  const SHAPES = {
    // Sinusoidal demand curve, peak afternoon (~17:30).
    "diurnal-load": (N, opts = {}) => {
      const peakHour = opts.peak_hour != null ? opts.peak_hour : 17.5;
      const peak = opts.peak != null ? opts.peak : 1.0;
      const trough = opts.trough != null ? opts.trough : 0.6;
      const noise = opts.noise != null ? opts.noise : 0.04;
      const mid = (peak + trough) / 2;
      const amp = (peak - trough) / 2;
      const r = rng(opts.seed || 11);
      return Array.from({ length: N }, (_, i) => {
        const hour = (i / N) * 24;
        // cosine bowl: trough at peakHour - 12, peak at peakHour
        const phase = ((hour - peakHour) / 24) * 2 * Math.PI;
        const base = mid - amp * Math.cos(phase);
        return base + (r() - 0.5) * 2 * noise * amp;
      });
    },
    // Bell curve, zero outside daylight window.
    "diurnal-solar": (N, opts = {}) => {
      const peakHour = opts.peak_hour != null ? opts.peak_hour : 12.5;
      const halfWidth = opts.half_width != null ? opts.half_width : 5;
      const peak = opts.peak != null ? opts.peak : 1.0;
      const noise = opts.noise != null ? opts.noise : 0.05;
      const r = rng(opts.seed || 13);
      return Array.from({ length: N }, (_, i) => {
        const hour = (i / N) * 24;
        const dt = hour - peakHour;
        const g = peak * Math.exp(-(dt * dt) / (2 * halfWidth * halfWidth / 4));
        const wob = (r() - 0.5) * 2 * noise * peak;
        return Math.max(0, g + wob);
      });
    },
    // Variable, weather-driven via AR(1) with persistence.
    "diurnal-wind": (N, opts = {}) => {
      const mean = opts.mean != null ? opts.mean : 0.5;
      const vol = opts.volatility != null ? opts.volatility : 0.3;
      const persistence = opts.persistence != null ? opts.persistence : 0.7;
      const r = rng(opts.seed || 17);
      const out = new Array(N);
      let prev = mean;
      for (let i = 0; i < N; i++) {
        const innov = (r() - 0.5) * 2 * vol;
        prev = mean + persistence * (prev - mean) + innov;
        // clamp soft to [0, 2*mean]
        out[i] = Math.max(0, Math.min(2 * mean, prev));
      }
      return out;
    },
    // Twin peaks: morning + evening, deeper trough in early hours.
    "diurnal-price": (N, opts = {}) => {
      const base = opts.base != null ? opts.base : 80;
      const morningPeak = opts.morning_peak != null ? opts.morning_peak : 110;
      const eveningPeak = opts.evening_peak != null ? opts.evening_peak : 140;
      const morningH = opts.morning_h != null ? opts.morning_h : 8;
      const eveningH = opts.evening_h != null ? opts.evening_h : 18;
      const trough = opts.trough != null ? opts.trough : 50;
      const noise = opts.noise != null ? opts.noise : 0.05;
      const sigma = 1.8; // peak half-width in hours
      const r = rng(opts.seed || 23);
      return Array.from({ length: N }, (_, i) => {
        const hour = (i / N) * 24;
        const dm = hour - morningH;
        const de = hour - eveningH;
        const m = (morningPeak - base) * Math.exp(-(dm * dm) / (2 * sigma * sigma));
        const e = (eveningPeak - base) * Math.exp(-(de * de) / (2 * sigma * sigma));
        // deep low between midnight and 5am
        const lowDip = (base - trough) * Math.max(0, Math.cos(((hour - 3) / 24) * 2 * Math.PI));
        const v = base + m + e - lowDip * 0.6;
        return v + (r() - 0.5) * 2 * noise * base;
      });
    },
    // Smooth daily temperature curve.
    "diurnal-temp": (N, opts = {}) => {
      const peakHour = opts.peak_hour != null ? opts.peak_hour : 15;
      const peak = opts.peak != null ? opts.peak : 18;
      const trough = opts.trough != null ? opts.trough : 6;
      const noise = opts.noise != null ? opts.noise : 0.5;
      const mid = (peak + trough) / 2;
      const amp = (peak - trough) / 2;
      const r = rng(opts.seed || 29);
      return Array.from({ length: N }, (_, i) => {
        const hour = (i / N) * 24;
        const phase = ((hour - peakHour) / 24) * 2 * Math.PI;
        return mid - amp * Math.cos(phase) + (r() - 0.5) * 2 * noise;
      });
    },
    // Mostly flat with small noise (baseload / nuclear / capacity-bounded).
    "flat-baseload": (N, opts = {}) => {
      const mean = opts.mean != null ? opts.mean : 1.0;
      const noise = opts.noise != null ? opts.noise : 0.02;
      const r = rng(opts.seed || 31);
      return Array.from({ length: N }, () => mean + (r() - 0.5) * 2 * noise);
    },
    // Tight oscillation around midpoint (grid frequency style).
    "frequency": (N, opts = {}) => {
      const mean = opts.mean != null ? opts.mean : 50;
      const amplitude = opts.amplitude != null ? opts.amplitude : 0.15;
      const noise = opts.noise != null ? opts.noise : 0.03;
      const r = rng(opts.seed || 37);
      let prev = mean;
      const out = new Array(N);
      for (let i = 0; i < N; i++) {
        // slow wander + tight oscillation
        const slow = Math.sin((i / N) * 2 * Math.PI * 3) * amplitude * 0.6;
        const innov = (r() - 0.5) * 2 * noise;
        prev = mean * 0.05 + prev * 0.95 + innov;
        out[i] = mean + slow + (prev - mean) * 0.4 + (r() - 0.5) * 2 * noise;
      }
      return out;
    },
    // Back-and-forth around zero (interconnector net flow style).
    "bipolar-flow": (N, opts = {}) => {
      const amplitude = opts.amplitude != null ? opts.amplitude : 1.0;
      const period = opts.period != null ? opts.period : 8;
      const noise = opts.noise != null ? opts.noise : 0.2;
      const r = rng(opts.seed || 41);
      return Array.from({ length: N }, (_, i) => {
        const t = (i / N) * 24;
        return amplitude * Math.sin((t / period) * 2 * Math.PI) + (r() - 0.5) * 2 * noise * amplitude;
      });
    },
    // Mostly low with occasional spikes (imbalance / scarcity / LOLP).
    "volatile-spikes": (N, opts = {}) => {
      const base = opts.base != null ? opts.base : 0.1;
      const spikeProb = opts.spike_prob != null ? opts.spike_prob : 0.05;
      const spikeHeight = opts.spike_height != null ? opts.spike_height : 1.0;
      const noise = opts.noise != null ? opts.noise : 0.04;
      const r = rng(opts.seed || 43);
      return Array.from({ length: N }, () => {
        const wob = (r() - 0.5) * 2 * noise * base;
        if (r() < spikeProb) {
          const k = 0.4 + r(); // 0.4-1.4 of nominal spike
          return base + spikeHeight * k + wob;
        }
        return Math.max(0, base + wob);
      });
    },
  };

  // ── 24h stacked area, GB generation by fuel ──────────────────
  function stackedArea(el, opts = {}) {
    const W = opts.width || 880;
    const H = opts.height || 320;
    const padL = 48, padR = 16, padT = 16, padB = 36;
    const innerW = W - padL - padR;
    const innerH = H - padT - padB;

    // Path A: explicit series — accept [{name, color, shape, params?}, ...]
    if (Array.isArray(opts.series) && opts.series.length > 0) {
      const N = opts.n || 48;
      const labels = opts.series.map((s) => s.name);
      const colors = opts.series.map((s, i) => s.color || [PALETTE.rust, PALETTE.forest, PALETTE.plum, PALETTE.sky, PALETTE.sand, "#d4a73a", "#5a8aa6", PALETTE.slate][i % 8]);
      // generate each layer's raw series
      const series = opts.series.map((s, i) => {
        const params = Object.assign({ seed: 7 + i * 13 }, s.params || {});
        const gen = SHAPES[s.shape];
        if (!gen) return new Array(N).fill(0);
        return gen(N, params);
      });
      // build per-i stacks
      const stacks = Array.from({ length: N }, (_, i) => {
        let acc = 0;
        const layers = series.map((sv) => {
          const v = Math.max(0, sv[i]);
          const out = [acc, acc + v];
          acc += v;
          return out;
        });
        return { layers, total: acc };
      });
      const totalMax = Math.max(...stacks.map((s) => s.total));
      const yMax = Math.max(totalMax * 1.08, 1e-6);
      // dynamic y-tick spacing
      const niceStep = (() => {
        const raw = yMax / 4;
        const mag = Math.pow(10, Math.floor(Math.log10(raw)));
        const norm = raw / mag;
        const step = norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10;
        return step * mag;
      })();
      const yTicks = [];
      for (let v = 0; v <= yMax; v += niceStep) yTicks.push(v);
      const xTickHours = [0, 6, 12, 18, 24];
      const yLabel = opts.yLabel || "";
      const x = (i) => padL + (i / (N - 1)) * innerW;
      const y = (v) => padT + innerH - (v / yMax) * innerH;
      const paths = labels.map((_, layerIdx) => {
        const top = stacks.map((s, i) => `${x(i)},${y(s.layers[layerIdx][1])}`);
        const bot = stacks.map((s, i) => `${x(i)},${y(s.layers[layerIdx][0])}`).reverse();
        return `M${top.join(" L")} L${bot.join(" L")} Z`;
      });
      let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" font-family="Inter, sans-serif" font-size="11">`;
      svg += `<g stroke="${PALETTE.rule}" stroke-width="1">`;
      yTicks.forEach((v) => {
        const yy = y(v);
        svg += `<line x1="${padL}" y1="${yy}" x2="${W - padR}" y2="${yy}" stroke-dasharray="${v === 0 ? "" : "2 4"}"/>`;
      });
      svg += `</g>`;
      svg += `<g fill="${PALETTE.inkSoft}" text-anchor="end">`;
      yTicks.forEach((v) => svg += `<text x="${padL - 8}" y="${y(v) + 3}">${niceStep < 1 ? v.toFixed(1) : Math.round(v)}${yLabel ? " " + yLabel : ""}</text>`);
      svg += `</g>`;
      svg += `<g fill="${PALETTE.inkSoft}" text-anchor="middle">`;
      xTickHours.forEach((h) => {
        const xx = padL + (h / 24) * innerW;
        svg += `<text x="${xx}" y="${H - padB + 18}">${String(h).padStart(2, "0")}:00</text>`;
      });
      svg += `</g>`;
      paths.forEach((p, i) => {
        svg += `<path d="${p}" fill="${colors[i]}" fill-opacity="0.85" stroke="${colors[i]}" stroke-width="0.5"/>`;
      });
      svg += `</svg>`;
      el.innerHTML = svg;
      if (opts.legend !== false) {
        const legendEl = document.createElement("div");
        legendEl.className = "chart-legend";
        legendEl.innerHTML = labels.map((l, i) => `<span><i style="background:${colors[i]}"></i>${l}</span>`).join("");
        el.appendChild(legendEl);
      }
      return;
    }

    // Path B: legacy hardcoded GB fuel mix (byte-identical to pre-D-22 output)
    const labels = ["Gas", "Wind", "Nuclear", "Imports", "Biomass", "Solar", "Hydro", "Coal"];
    const colors = [PALETTE.rust, PALETTE.forest, PALETTE.plum, PALETTE.sky, PALETTE.sand, "#d4a73a", "#5a8aa6", PALETTE.slate];

    // 48 half-hour points per day
    const N = 48;
    const r = rng(7);
    // base profiles per fuel
    const profile = (i) => {
      const t = (i / (N - 1)) * 2 * Math.PI;
      return {
        gas:     14 + 5 * Math.sin(t - 0.5) + 2 * Math.cos(t * 2),
        wind:     9 + 3 * Math.sin(t * 0.7 + 1.2) + r() * 1.5,
        nuclear:  5.6 + 0.05 * Math.sin(t),
        imports:  3.8 + 1.2 * Math.sin(t * 1.3),
        biomass:  2.2 + 0.3 * Math.sin(t),
        solar:    Math.max(0, 4.6 * Math.sin((i / N) * Math.PI - 0.3)),
        hydro:    1.0 + 0.4 * Math.sin(t * 2),
        coal:     0.2 + 0.1 * Math.sin(t),
      };
    };
    const data = Array.from({ length: N }, (_, i) => profile(i));
    const stacks = data.map((d) => {
      let acc = 0;
      const order = ["gas", "wind", "nuclear", "imports", "biomass", "solar", "hydro", "coal"];
      const layers = order.map((k) => {
        const v = d[k];
        const out = [acc, acc + v];
        acc += v;
        return out;
      });
      return { layers, total: acc };
    });
    const yMax = Math.max(...stacks.map((s) => s.total)) * 1.05;

    const x = (i) => padL + (i / (N - 1)) * innerW;
    const y = (v) => padT + innerH - (v / yMax) * innerH;

    // build paths per layer (top of layer + bottom of layer reversed)
    const paths = labels.map((_, layerIdx) => {
      const top = stacks.map((s, i) => `${x(i)},${y(s.layers[layerIdx][1])}`);
      const bot = stacks.map((s, i) => `${x(i)},${y(s.layers[layerIdx][0])}`).reverse();
      return `M${top.join(" L")} L${bot.join(" L")} Z`;
    });

    // gridlines
    const yTicks = [0, 10, 20, 30, 40];
    const xTickHours = [0, 6, 12, 18, 24];

    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" font-family="Inter, sans-serif" font-size="11">`;
    // grid
    svg += `<g stroke="${PALETTE.rule}" stroke-width="1">`;
    yTicks.forEach((v) => {
      const yy = y(v);
      svg += `<line x1="${padL}" y1="${yy}" x2="${W - padR}" y2="${yy}" stroke-dasharray="${v === 0 ? "" : "2 4"}"/>`;
    });
    svg += `</g>`;
    // y labels
    svg += `<g fill="${PALETTE.inkSoft}" text-anchor="end">`;
    yTicks.forEach((v) => svg += `<text x="${padL - 8}" y="${y(v) + 3}">${v} GW</text>`);
    svg += `</g>`;
    // x labels
    svg += `<g fill="${PALETTE.inkSoft}" text-anchor="middle">`;
    xTickHours.forEach((h) => {
      const xx = padL + (h / 24) * innerW;
      svg += `<text x="${xx}" y="${H - padB + 18}">${String(h).padStart(2, "0")}:00</text>`;
    });
    svg += `</g>`;
    // stacked layers
    paths.forEach((p, i) => {
      svg += `<path d="${p}" fill="${colors[i]}" fill-opacity="0.85" stroke="${colors[i]}" stroke-width="0.5"/>`;
    });
    svg += `</svg>`;

    el.innerHTML = svg;

    // legend
    if (opts.legend !== false) {
      const legendEl = document.createElement("div");
      legendEl.className = "chart-legend";
      legendEl.innerHTML = labels.map((l, i) => `<span><i style="background:${colors[i]}"></i>${l}</span>`).join("");
      el.appendChild(legendEl);
    }
  }

  // ── single-line sparkline ───────────────────────────────────
  function sparkline(el, opts = {}) {
    const W = opts.width || 200;
    const H = opts.height || 40;
    const seed = opts.seed || 1;
    const N = opts.n || 48;
    // Data source precedence: explicit values > shape generator > legacy seed-based.
    let data;
    if (Array.isArray(opts.values) && opts.values.length > 0) {
      data = opts.values.slice();
    } else if (opts.shape && SHAPES[opts.shape]) {
      const params = Object.assign({ seed }, opts.params || {});
      data = SHAPES[opts.shape](N, params);
    } else {
      const r = rng(seed);
      data = Array.from({ length: N }, (_, i) => {
        const t = i / (N - 1);
        return 0.5 + 0.4 * Math.sin(t * 4 + seed) + r() * 0.15 - 0.075;
      });
    }
    const min = Math.min(...data), max = Math.max(...data);
    const x = (i) => (i / (N - 1)) * W;
    const y = (v) => H - 4 - ((v - min) / (max - min || 1)) * (H - 8);
    const pts = data.map((v, i) => `${x(i)},${y(v)}`).join(" ");
    const color = opts.color || PALETTE.forest;
    const fill = opts.fill || PALETTE.forestTint;
    const area = `M0,${H} L${pts.split(" ").join(" L")} L${W},${H} Z`;
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
      <path d="${area}" fill="${fill}" />
      <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5"/>
    </svg>`;
  }

  // ── horizontal bars (e.g. dataset rows per dataset) ─────────
  function barsH(el, opts = {}) {
    const items = opts.items || [];
    const W = opts.width || 320;
    const rowH = 22;
    const labelW = 120;
    const barW = W - labelW - 60;
    const max = Math.max(...items.map((d) => d.value));
    const H = items.length * rowH + 8;
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" font-family="Inter, sans-serif" font-size="11">`;
    items.forEach((d, i) => {
      const yy = i * rowH + 6;
      const w = (d.value / max) * barW;
      svg += `<text x="0" y="${yy + 12}" fill="${PALETTE.ink}">${d.label}</text>`;
      svg += `<rect x="${labelW}" y="${yy}" width="${w}" height="14" fill="${d.color || PALETTE.forest}" fill-opacity="0.85"/>`;
      svg += `<text x="${labelW + w + 6}" y="${yy + 12}" fill="${PALETTE.inkSoft}">${d.display || d.value}</text>`;
    });
    svg += `</svg>`;
    el.innerHTML = svg;
  }

  // ── timeline / availability heatmap (24×30) ─────────────────
  function heatmap(el, opts = {}) {
    const cols = opts.cols || 30; // days
    const rows = opts.rows || 24; // hours
    const W = opts.width || 720;
    const H = opts.height || 180;
    const padL = 28, padT = 16, padB = 24, padR = 8;
    const cellW = (W - padL - padR) / cols;
    const cellH = (H - padT - padB) / rows;
    const r = rng(opts.seed || 11);
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" font-family="Inter, sans-serif" font-size="10">`;
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        // mostly green; rare misses
        const miss = r() < 0.012;
        const partial = !miss && r() < 0.04;
        const fill = miss ? "#c45a3a" : partial ? PALETTE.sand : PALETTE.forest;
        const op = miss ? 0.85 : partial ? 0.7 : 0.78;
        svg += `<rect x="${padL + i * cellW + 0.5}" y="${padT + j * cellH + 0.5}" width="${cellW - 1}" height="${cellH - 1}" fill="${fill}" fill-opacity="${op}"/>`;
      }
    }
    // y labels
    [0, 6, 12, 18].forEach((h) => {
      svg += `<text x="${padL - 6}" y="${padT + h * cellH + 9}" text-anchor="end" fill="${PALETTE.inkSoft}">${String(h).padStart(2, "0")}</text>`;
    });
    // x labels
    [0, 7, 14, 21, 29].forEach((d) => {
      svg += `<text x="${padL + d * cellW + cellW / 2}" y="${H - 8}" text-anchor="middle" fill="${PALETTE.inkSoft}">${d === 29 ? "today" : `d-${29 - d}`}</text>`;
    });
    svg += `</svg>`;
    el.innerHTML = svg;
  }

  // ── price ladder (system price last 48 SP) ─────────────────
  function priceLadder(el, opts = {}) {
    const W = opts.width || 280, H = opts.height || 110;
    const N = opts.n || 48;
    const seed = opts.seed || 3;
    // Data source precedence: explicit values > shape generator > legacy seed-based.
    let data;
    if (Array.isArray(opts.values) && opts.values.length > 0) {
      data = opts.values.slice();
    } else if (opts.shape && SHAPES[opts.shape]) {
      const params = Object.assign({ seed }, opts.params || {});
      data = SHAPES[opts.shape](N, params);
    } else {
      const r = rng(seed);
      data = Array.from({ length: N }, (_, i) => {
        const t = i / N;
        return 70 + 28 * Math.sin(t * 6) + r() * 18 - 9;
      });
    }
    const min = Math.min(...data), max = Math.max(...data);
    const x = (i) => 4 + (i / (N - 1)) * (W - 8);
    const y = (v) => 8 + (1 - (v - min) / (max - min || 1)) * (H - 16);
    const pts = data.map((v, i) => `${x(i)},${y(v)}`);
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}">`;
    svg += `<polyline points="${pts.join(" ")}" fill="none" stroke="${PALETTE.ink}" stroke-width="1.4"/>`;
    svg += `<circle cx="${x(N-1)}" cy="${y(data[N-1])}" r="3" fill="${PALETTE.forest}"/>`;
    svg += `</svg>`;
    el.innerHTML = svg;
  }

  // ── donut (split percentage) ───────────────────────────────
  function donut(el, opts = {}) {
    const data = opts.data || [];
    const total = data.reduce((s, d) => s + d.value, 0);
    const W = opts.width || 140, H = opts.height || 140;
    const cx = W / 2, cy = H / 2, r = Math.min(W, H) / 2 - 6, ir = r - 16;
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">`;
    let acc = -Math.PI / 2;
    data.forEach((d) => {
      const ang = (d.value / total) * Math.PI * 2;
      const a0 = acc, a1 = acc + ang;
      acc = a1;
      const large = ang > Math.PI ? 1 : 0;
      const x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0);
      const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
      const xi0 = cx + ir * Math.cos(a0), yi0 = cy + ir * Math.sin(a0);
      const xi1 = cx + ir * Math.cos(a1), yi1 = cy + ir * Math.sin(a1);
      const path = `M${x0},${y0} A${r},${r} 0 ${large} 1 ${x1},${y1} L${xi1},${yi1} A${ir},${ir} 0 ${large} 0 ${xi0},${yi0} Z`;
      svg += `<path d="${path}" fill="${d.color}" />`;
    });
    if (opts.center) {
      svg += `<text x="${cx}" y="${cy - 2}" text-anchor="middle" font-family="Fraunces, serif" font-size="22" fill="${PALETTE.ink}">${opts.center}</text>`;
      if (opts.centerSub) svg += `<text x="${cx}" y="${cy + 14}" text-anchor="middle" font-family="Inter, sans-serif" font-size="10" fill="${PALETTE.inkSoft}" letter-spacing="0.05em">${opts.centerSub}</text>`;
    }
    svg += `</svg>`;
    el.innerHTML = svg;
  }

  // dispatch
  window.GFCharts = { stackedArea, sparkline, barsH, heatmap, priceLadder, donut, PALETTE, SHAPES };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-chart]").forEach((el) => {
      const kind = el.dataset.chart;
      const opts = {};
      try { if (el.dataset.opts) Object.assign(opts, JSON.parse(el.dataset.opts)); } catch {}
      if (window.GFCharts[kind]) window.GFCharts[kind](el, opts);
      // Decorative, illustrative-only chart ("shape only · seeded SVG") — hide the
      // rendered svg + legend from assistive tech (F-A8 / WCAG 1.1.1).
      el.setAttribute("aria-hidden", "true");
    });
  });
})();
