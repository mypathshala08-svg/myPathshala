/**
 * MyPhatshala: AWS Lab Simulator — practise a lab without an AWS account.
 * ----------------------------------------------------------------------
 * Markup:  <div class="awssim"><script type="application/json">{ …config… }</script></div>
 * Config:
 *   title, intro (html), vars {name: value} (defaults, e.g. acct, region, you),
 *   diagram (svg markup; elements with data-k="key" light up when a step lists that key),
 *   free [{re, out}]  commands accepted at any time (e.g. aws sts get-caller-identity)
 *   steps [{
 *     title, goal (html), hint (html), answer (text: one correct CLI command),
 *     cli    [{re, out, set:{var:value}}]   regex for an accepted command; named groups become vars
 *     errors [{re, out}]                     realistic error output for a common wrong command
 *     console {crumbs, fields:[{label,key,re,ph,help,type:'text'|'check'|'select',options,must}], button, out, set}
 *     lights [keys], explain (html shown after the step: what happened inside AWS)
 *   }]
 * In regexes and outputs, {var} is replaced by the variable's value (regex-escaped inside regexes).
 * Nothing is sent anywhere: the simulator is a teaching model of AWS, not AWS itself.
 */
(function () {
  "use strict";
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const reEsc = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const norm = s => s.replace(/\s+/g, " ").replace(/\s*\\\s*/g, " ").trim();

  function Sim(root, cfg) {
    const steps = cfg.steps || [];
    const dsrc = root.querySelector(".as-diagsrc"); if (dsrc && !cfg.diagram) cfg.diagram = dsrc.innerHTML;
    let vars, done, cur, hist, hidx;
    const fill = (s, forRe) => String(s ?? "").replace(/\{(\w+)\}/g, (m, k) => k in vars ? (forRe ? reEsc(vars[k]) : vars[k]) : m);
    const rx = r => { try { return new RegExp(fill(r, true)); } catch (e) { return /^\b$/; } };

    root.innerHTML = `
      <div class="as-head"><div><b class="as-badge">Practice without an account</b> <span class="as-title">${esc(cfg.title || "AWS lab simulator")}</span></div>
        <div class="as-prog" aria-live="polite"></div></div>
      ${cfg.intro ? `<p class="as-intro">${cfg.intro}</p>` : ""}
      <div class="as-grid">
        <div class="as-side"><ol class="as-list"></ol>
          <div class="as-goal"></div>
          <div class="as-btns"><button type="button" data-a="hint">Hint</button><button type="button" data-a="answer">Show answer</button><button type="button" data-a="reset">Reset</button></div>
          <div class="as-tip" hidden></div></div>
        <div class="as-main">
          <div class="as-tabs" role="tablist"><button type="button" role="tab" data-t="console" aria-selected="true">Console</button><button type="button" role="tab" data-t="cli" aria-selected="false">CloudShell</button></div>
          <div class="as-pane as-console" data-p="console"></div>
          <div class="as-pane as-cli" data-p="cli" hidden><div class="as-out" tabindex="0" aria-live="polite"></div>
            <form class="as-in"><label><span class="as-ps">[cloudshell-user@ip-10-0-0-1 ~]$</span><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Type a command"></label></form></div>
        </div>
      </div>
      <div class="as-diag">${cfg.diagram || ""}</div>
      <div class="as-explain" aria-live="polite"></div>
      <p class="as-note">A teaching model of AWS: it accepts the commands and clicks this lab needs and shows realistic results. No real resources are created. Do the same lab on your own account using the steps above.</p>`;
    const $ = s => root.querySelector(s);
    const out = $(".as-out"), input = $(".as-in input");

    function print(txt, cls) { const d = document.createElement("pre"); d.className = cls || ""; d.textContent = txt; out.appendChild(d); out.scrollTop = out.scrollHeight; }
    function tab(t) {
      root.querySelectorAll(".as-tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.t === t));
      root.querySelectorAll(".as-pane").forEach(p => p.hidden = p.dataset.p !== t);
      if (t === "cli") input.focus({ preventScroll: true });
    }
    function light(keys, fresh) {
      (keys || []).forEach(k => root.querySelectorAll(`.as-diag [data-k="${k}"]`).forEach(e => {
        e.classList.add("on"); if (fresh) { e.classList.remove("pulse"); void e.getBBox?.(); e.classList.add("pulse"); }
      }));
    }
    function render() {
      $(".as-list").innerHTML = steps.map((s, i) => `<li class="${done[i] ? "ok" : ""} ${i === cur ? "cur" : ""}"><button type="button" data-s="${i}">${done[i] ? "✓" : i + 1 + "."} ${esc(s.title)}</button></li>`).join("");
      const n = done.filter(Boolean).length;
      $(".as-prog").innerHTML = `<span class="as-bar"><i style="width:${Math.round(100 * n / Math.max(1, steps.length))}%"></i></span> ${n}/${steps.length} done`;
      const s = steps[cur];
      $(".as-tip").hidden = true;
      if (!s) {
        $(".as-goal").innerHTML = `<p class="as-win"><b>Lab complete.</b> Every requirement is met in the simulator. Now repeat it on your own AWS account — and clean up afterwards.</p>`;
        $(".as-console").innerHTML = `<div class="as-card as-done">All steps completed ✓</div>`; return;
      }
      $(".as-goal").innerHTML = `<p><b>Step ${cur + 1}:</b> ${fill(s.goal)}</p>` + (s.console && s.cli ? `<p class="as-small">Do it in the <b>Console</b> tab <i>or</i> the <b>CloudShell</b> tab.</p>` : s.cli ? `<p class="as-small">Use the <b>CloudShell</b> tab.</p>` : `<p class="as-small">Use the <b>Console</b> tab.</p>`);
      const c = s.console;
      if (!c) { $(".as-console").innerHTML = `<div class="as-card">This step is done in CloudShell. <button type="button" data-a="tocli">Open CloudShell</button></div>`; return; }
      const f = (c.fields || []).map((x, j) => {
        const id = `as-${Math.random().toString(36).slice(2, 8)}-${j}`;
        if (x.type === "check") return `<label class="as-chk"><input type="checkbox" data-f="${j}" id="${id}"> ${esc(x.label)}</label>`;
        if (x.type === "select") return `<label for="${id}">${esc(x.label)}</label><select id="${id}" data-f="${j}"><option value="">— choose —</option>${(x.options || []).map(o => `<option>${esc(fill(o))}</option>`).join("")}</select>`;
        return `<label for="${id}">${esc(x.label)}</label><input id="${id}" data-f="${j}" type="text" placeholder="${esc(fill(x.ph || ""))}" autocomplete="off">${x.help ? `<small>${esc(fill(x.help))}</small>` : ""}`;
      }).join("");
      $(".as-console").innerHTML = `<div class="as-card"><div class="as-crumb">AWS Management Console › ${esc(fill(c.crumbs || ""))}</div><form class="as-form">${f}<p class="as-err" hidden></p><button type="submit" class="as-go">${esc(c.button || "Create")}</button></form></div>`;
    }
    function complete(i, msg) {
      const s = steps[i]; done[i] = true;
      if (s.set) Object.assign(vars, Object.fromEntries(Object.entries(s.set).map(([k, v]) => [k, fill(v)])));
      light(s.lights, true);
      $(".as-explain").innerHTML = `<div class="as-card as-what"><b>✓ ${esc(s.title)}</b>${msg ? `<div class="as-res">${msg}</div>` : ""}${s.explain ? `<p><b>What happened inside AWS:</b> ${fill(s.explain)}</p>` : ""}</div>`;
      cur = done.findIndex(d => !d); if (cur < 0) cur = steps.length;
      render();
    }
    function run(raw) {
      const cmd = norm(raw); if (!cmd) return;
      hist.push(raw); hidx = hist.length;
      print("$ " + raw, "as-cmd");
      if (cmd === "clear") { out.innerHTML = ""; return; }
      if (cmd === "help") { print("This simulator understands the commands this lab needs.\nType  hint  for a clue, or  answer  for a correct command.  clear  empties the screen.", "as-sys"); return; }
      const s = steps[cur];
      if (cmd === "hint") { print(s ? stripTags(fill(s.hint || "Read the step goal on the left.")) : "Lab complete.", "as-sys"); return; }
      if (cmd === "answer") { print(s && s.answer ? fill(s.answer) : "No CLI answer for this step — use the Console tab.", "as-sys"); return; }
      if (s) for (const c of s.cli || []) {
        const m = rx(c.re).exec(cmd);
        if (m) { if (m.groups) Object.assign(vars, m.groups); if (c.set) for (const k in c.set) vars[k] = fill(c.set[k]); const o = fill(c.out); if (o) print(o); complete(cur, ""); return; }
      }
      if (s) for (const e of s.errors || []) { if (rx(e.re).test(cmd)) { print(fill(e.out), e.ok ? "" : "as-e"); return; } }
      for (const f of cfg.free || []) { const m = rx(f.re).exec(cmd); if (m) { if (m.groups) Object.assign(vars, m.groups); print(fill(f.out)); return; } }
      for (let i = 0; i < steps.length; i++) if (done[i]) for (const c of steps[i].cli || []) if (rx(c.re).test(cmd)) { print(fill(c.again || c.out)); return; }
      if (/^aws\s/.test(cmd)) print("The simulator does not model this command at this step. Type  hint  for what this step needs.", "as-sys");
      else print(`bash: ${cmd.split(" ")[0]}: not available in this simulation (type  help )`, "as-e");
    }
    const stripTags = h => { const d = document.createElement("div"); d.innerHTML = h; return d.textContent; };

    root.addEventListener("click", ev => {
      const b = ev.target.closest("button"); if (!b) return;
      if (b.dataset.t) tab(b.dataset.t);
      if (b.dataset.s) { const i = +b.dataset.s; if (!done[i] && i !== cur) { const tip = $(".as-tip"); tip.hidden = false; tip.textContent = "Finish the current step first — labs build on each other."; } }
      const a = b.dataset.a; const s = steps[cur];
      if (a === "hint" || a === "answer") { const tip = $(".as-tip"); tip.hidden = false; tip.innerHTML = !s ? "Lab complete." : a === "hint" ? fill(s.hint || "Read the goal.") : (s.answer ? `<code>${esc(fill(s.answer))}</code>` : "") + (s.console ? `<br>Console: ${esc(fill(s.console.crumbs || ""))} → fill the fields → <b>${esc(s.console.button || "Create")}</b>.` : ""); }
      if (a === "reset") init();
      if (a === "tocli") tab("cli");
    });
    root.addEventListener("submit", ev => {
      ev.preventDefault();
      if (ev.target.classList.contains("as-in")) { run(input.value); input.value = ""; return; }
      const s = steps[cur]; if (!s || !s.console) return;
      const err = $(".as-err"); const got = {};
      for (const [j, x] of (s.console.fields || []).entries()) {
        const e = root.querySelector(`[data-f="${j}"]`);
        if (x.type === "check") { if (x.must !== undefined && e.checked !== !!x.must) { err.hidden = false; err.textContent = x.why || `Check the setting “${x.label}”.`; return; } continue; }
        const v = e.value.trim();
        if (x.re && !rx(x.re).test(v)) { err.hidden = false; err.textContent = fill(x.why || `“${x.label}” is not valid for this step.`); e.focus(); return; }
        if (x.key) got[x.key] = v;
      }
      Object.assign(vars, got);
      if (s.console.set) for (const k in s.console.set) vars[k] = fill(s.console.set[k]);
      complete(cur, `<span class="as-flash">${esc(fill(s.console.out || "Done."))}</span>`);
    });
    input.addEventListener("keydown", ev => {
      if (ev.key === "ArrowUp" && hidx > 0) { hidx--; input.value = hist[hidx]; ev.preventDefault(); }
      if (ev.key === "ArrowDown") { hidx = Math.min(hist.length, hidx + 1); input.value = hist[hidx] || ""; ev.preventDefault(); }
    });
    function init() {
      vars = Object.assign({ acct: "123456789012", region: "ap-south-1", you: "riya-admin", rnd: String(Math.floor(1000 + Math.random() * 9000)) }, cfg.vars || {});
      done = steps.map(() => false); cur = 0; hist = []; hidx = 0;
      $(".as-diag").innerHTML = fill(cfg.diagram || "");
      out.innerHTML = ""; $(".as-explain").innerHTML = "";
      root.querySelectorAll(".as-diag [data-k]").forEach(e => e.classList.remove("on", "pulse"));
      light(cfg.lit || [], false);
      print(fill(cfg.banner || "Welcome to AWS CloudShell (simulated).\nRegion: {region}   Signed in as: {you}\nType  help  for help."), "as-sys");
      render();
    }
    init();
  }
  function boot() {
    document.querySelectorAll(".awssim").forEach(r => {
      if (r.dataset.ready) return; r.dataset.ready = "1";
      const j = r.querySelector('script[type="application/json"]');
      try { new Sim(r, JSON.parse(j.textContent)); } catch (e) { r.innerHTML = "<p>Simulator failed to load.</p>"; console.error(e); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
