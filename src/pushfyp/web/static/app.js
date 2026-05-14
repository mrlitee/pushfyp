// pushfyp web — vanilla JS, no framework.

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

// ---------- Tabs ----------
$$(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const id = tab.dataset.tab;
    $$(".tab").forEach((t) => t.classList.toggle("active", t === tab));
    $$(".panel").forEach((p) => p.classList.toggle("active", p.id === `panel-${id}`));
  });
});

// ---------- Helpers ----------
async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

function setBusy(el, busy) {
  el.classList.toggle("busy", busy);
  $$("button", el).forEach((b) => (b.disabled = busy));
}

function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderError(target, msg) {
  target.className = "result error";
  target.innerHTML = `<strong>Error:</strong> ${escapeHtml(msg)}`;
}

// ---------- Analyze ----------
$("#form-analyze").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const out = $("#result-analyze");
  out.className = "result";
  out.textContent = "Loading...";
  setBusy(form, true);

  try {
    const url = new FormData(form).get("url");
    const data = await api("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ url }),
    });

    const cls = data.score >= 75 ? "good" : data.score >= 50 ? "warn" : "bad";
    const breakdownHtml = Object.entries(data.breakdown)
      .map(([k, v]) => {
        const pct = Math.min(100, (v / 20) * 100);
        return `<div class="breakdown-row">
          <span class="label">${k.replaceAll("_", " ")}</span>
          <div class="bar"><span style="width:${pct}%"></span></div>
          <span class="val">${v}</span>
        </div>`;
      })
      .join("");

    const suggHtml = data.suggestions.length
      ? `<div class="suggestions"><h3>Saran perbaikan</h3><ul>${data.suggestions
          .map((s) => `<li>${escapeHtml(s)}</li>`)
          .join("")}</ul></div>`
      : `<div class="suggestions success" style="border:0;background:transparent;padding:0;color:var(--accent);">Postingan sudah well-optimized!</div>`;

    out.innerHTML = `
      <div class="score">
        <span class="score-num ${cls}">${data.score}</span>
        <span style="color:var(--muted)">/100 — FYP readiness</span>
      </div>
      <div style="font-size:.9rem;color:var(--muted)">
        <strong>@${escapeHtml(data.meta.author || "-")}</strong>
      </div>
      <div style="margin:.5rem 0;font-size:.95rem">${escapeHtml((data.meta.caption || "").slice(0, 280))}${(data.meta.caption || "").length > 280 ? "…" : ""}</div>
      <div class="breakdown">${breakdownHtml}</div>
      ${suggHtml}
    `;
  } catch (err) {
    renderError(out, err.message);
  } finally {
    setBusy(form, false);
  }
});

// ---------- Hook ----------
$("#form-hook").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const out = $("#result-hook");
  out.className = "result";
  out.textContent = "Loading...";
  setBusy(form, true);

  try {
    const fd = new FormData(form);
    const data = await api("/api/hook", {
      method: "POST",
      body: JSON.stringify({
        topic: fd.get("topic"),
        use_llm: fd.get("use_llm") === "on",
      }),
    });
    out.innerHTML = data.hooks
      .map(
        (h) =>
          `<div class="hook-item">
            <span class="style">${escapeHtml(h.style)}</span>
            <span>${escapeHtml(h.text)}</span>
          </div>`
      )
      .join("");
  } catch (err) {
    renderError(out, err.message);
  } finally {
    setBusy(form, false);
  }
});

// ---------- Hashtags ----------
async function loadNiches() {
  try {
    const { niches } = await api("/api/niches");
    const sel = $("#select-niche");
    sel.innerHTML = niches.map((n) => `<option value="${n}">${n}</option>`).join("");
  } catch {
    /* ignore */
  }
}
loadNiches();

$("#form-hashtags").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const out = $("#result-hashtags");
  out.className = "result";
  out.textContent = "Loading...";
  setBusy(form, true);

  try {
    const fd = new FormData(form);
    const params = new URLSearchParams({
      niche: fd.get("niche"),
      count: fd.get("count") || 5,
      include_fyp: fd.get("include_fyp") === "on" ? "true" : "false",
    });
    const data = await api(`/api/hashtags?${params}`);
    out.innerHTML = `
      ${data.hashtags.map((t) => `<span class="tag" data-tag="${escapeHtml(t)}">${escapeHtml(t)}</span>`).join("")}
      <div style="margin-top:.75rem;font-size:.85rem;color:var(--muted)">Klik tag untuk salin.</div>
    `;
    $$(".tag", out).forEach((tag) => {
      tag.addEventListener("click", () => {
        navigator.clipboard.writeText(tag.dataset.tag);
        tag.textContent = "✓ copied";
        setTimeout(() => (tag.textContent = tag.dataset.tag), 900);
      });
    });
  } catch (err) {
    renderError(out, err.message);
  } finally {
    setBusy(form, false);
  }
});

// ---------- Schedule / Post ----------
$("#form-schedule").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const out = $("#result-schedule");
  out.className = "result";
  out.textContent = "Loading...";
  setBusy(form, true);

  try {
    const fd = new FormData(form);
    const body = {
      text: fd.get("text"),
      when: fd.get("when") || null,
    };
    const data = await api("/api/schedule", {
      method: "POST",
      body: JSON.stringify(body),
    });
    out.className = "result success";
    out.innerHTML = `Dijadwalkan pada <strong>${escapeHtml(data.scheduled_at)}</strong> (job: <code>${escapeHtml(data.job_id)}</code>)`;
  } catch (err) {
    renderError(out, err.message);
  } finally {
    setBusy(form, false);
  }
});

$("#btn-post-now").addEventListener("click", async () => {
  const form = $("#form-schedule");
  const text = new FormData(form).get("text");
  if (!text) return;
  const out = $("#result-schedule");
  out.className = "result";
  out.textContent = "Posting...";
  setBusy(form, true);

  try {
    const data = await api("/api/post", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    out.className = "result success";
    out.innerHTML = `Posted! media_id: <code>${escapeHtml(data.media_id || "-")}</code>`;
  } catch (err) {
    renderError(out, err.message);
  } finally {
    setBusy(form, false);
  }
});
