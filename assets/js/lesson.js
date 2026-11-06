/**
 * MyPhatshala: lesson engine
 * ------------------------------------------------------------
 * Every lesson page is plain HTML. This script adds the interactive parts:
 *   .code            syntax colours + copy button
 *   .anim            two-view frame-by-frame animation (What you see / Behind the screen)
 *   .tracer          line-by-line code tracer (stack, heap, console)
 *   .runner          live code editor (OneCompiler embed, loaded on click)
 *   .quiz            multiple-choice quiz with explanations
 *   .modlab          switch an access modifier and compare what compiles / prints
 *   #lesson-nav, #outline   previous/next + module outline (from data/courses/<id>.js)
 *   .toc             highlights the part you are reading
 * Data for tracer/runner/quiz sits in <script type="application/json"> inside each block.
 */
(function () {
  "use strict";
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const readJSON = el => { const s = el.querySelector('script[type="application/json"]'); try { return s ? JSON.parse(s.textContent) : null; } catch (e) { console.error("Bad JSON in", el, e); return null; } };
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ICON = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M15 18l-6-6 6-6"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M9 6l6 6-6 6"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l13 8-13 8z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
    reset: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M3 12a9 9 0 1 0 3-6.7M3 4v5h5"/></svg>',
  };

  /* ================= syntax highlighting ================= */
  const KW = {
    java: "abstract assert boolean break byte case catch char class const continue default do double else enum extends final finally float for goto if implements import instanceof int interface long native new package private protected public return short static strictfp super switch synchronized this throw throws transient try void volatile while var record yield true false null",
    python: "and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield print",
    bash: "if then else elif fi for while until do done case esac in function return exit export local readonly select time break continue shift source alias unalias declare read echo printf cd pwd ls mkdir rmdir touch cp mv rm cat less head tail grep sed awk sort uniq cut tr wc find chmod chown sudo man whoami date uname ps kill",
    sql: "select from where and or not insert into values update set delete create table alter drop primary key foreign references join inner left right full outer on group by order having limit distinct as count sum avg min max union all case when then else end index view null is in between like",
  };
  function highlight(code, lang) {
    const kw = new Set((KW[lang] || KW.java).split(" ").map(k => lang === "sql" ? k.toLowerCase() : k));
    if (lang === "bash") return highlightBash(code, kw);
    const re = /(\/\/[^\n]*|#[^\n]*|\/\*[\s\S]*?\*\/|--[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+(?:\.\d+)?[lLfFdD]?\b)|([A-Za-z_]\w*)|([\s\S])/g;
    let out = "", m;
    while ((m = re.exec(code))) {
      if (m[1]) {
        const isComment = lang === "python" ? m[1][0] === "#" : lang === "sql" ? m[1].startsWith("--") || m[1].startsWith("/*") : !m[1].startsWith("#") && !m[1].startsWith("--");
        out += isComment ? `<span class="tk-com">${esc(m[1])}</span>` : esc(m[1]);
      } else if (m[2]) out += `<span class="tk-str">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="tk-num">${m[3]}</span>`;
      else if (m[4]) {
        const w = m[4], key = lang === "sql" ? w.toLowerCase() : w;
        if (kw.has(key)) out += `<span class="tk-kw">${w}</span>`;
        else if (/^[A-Z]/.test(w) && lang !== "sql") out += `<span class="tk-type">${w}</span>`;
        else if (code[re.lastIndex] === "(") out += `<span class="tk-fn">${w}</span>`;
        else out += w;
      } else out += esc(m[5]);
    }
    return out;
  }

  /* Bash: # starts a comment only at the start of a word ($#, ${#x}, a#b are not comments); $VARS coloured as types. */
  function highlightBash(code, kw) {
    const re = /((?:^|(?<=[\s;|&(]))#[^\n]*)|("(?:\\.|[^"\\])*"|'[^']*')|(\$\{[^}]*\}|\$[A-Za-z_]\w*|\$[0-9?#$!@*-])|(\b\d+\b)|([A-Za-z_][\w-]*)|([\s\S])/gm;
    let out = "", m;
    while ((m = re.exec(code))) {
      if (m[1]) out += `<span class="tk-com">${esc(m[1])}</span>`;
      else if (m[2]) out += `<span class="tk-str">${esc(m[2])}</span>`;
      else if (m[3]) out += `<span class="tk-type">${esc(m[3])}</span>`;
      else if (m[4]) out += `<span class="tk-num">${m[4]}</span>`;
      else if (m[5]) out += kw.has(m[5]) ? `<span class="tk-kw">${m[5]}</span>` : esc(m[5]);
      else out += esc(m[6]);
    }
    return out;
  }

  $$(".code").forEach(box => {
    const pre = box.querySelector("pre code");
    if (!pre) return;
    const lang = box.dataset.lang || "java";
    const raw = pre.textContent.replace(/^\n/, "").replace(/\s+$/, "");
    pre.innerHTML = highlight(raw, lang);
    const bar = document.createElement("div");
    bar.className = "code__bar";
    bar.innerHTML = `<span class="dots"><i></i><i></i><i></i></span><span>${esc(box.dataset.file || lang)}</span><button class="copy-btn" type="button">Copy</button>`;
    box.prepend(bar);
    bar.querySelector(".copy-btn").addEventListener("click", e => {
      const done = ok => { e.target.textContent = ok ? "Copied ✓" : "Select & copy"; setTimeout(() => (e.target.textContent = "Copy"), 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(raw).then(() => done(true), () => done(false)); else done(false);
    });
  });

  /* ================= shared player controls ================= */
  function makeControls(total, onGo, opts = {}) {
    const wrap = document.createElement("div");
    wrap.className = "controls";
    wrap.innerHTML =
      `<button class="ctl" data-a="prev" aria-label="Previous step">${ICON.prev}Back</button>` +
      `<button class="ctl ctl--play" data-a="play" aria-label="Play">${ICON.play}<span>Play</span></button>` +
      `<button class="ctl" data-a="next" aria-label="Next step">Next${ICON.next}</button>` +
      `<button class="ctl" data-a="reset" aria-label="Restart">${ICON.reset}</button>` +
      `<span class="frame-count"></span>` +
      `<span class="frame-dots">${Array.from({ length: total }, (_, i) => `<button aria-label="Step ${i + 1}" data-i="${i}"></button>`).join("")}</span>`;
    let cur = 0, timer = null;
    const playBtn = wrap.querySelector('[data-a="play"]');
    const setPlaying = on => {
      clearInterval(timer); timer = null;
      playBtn.innerHTML = on ? `${ICON.pause}<span>Pause</span>` : `${ICON.play}<span>${cur === total - 1 ? "Replay" : "Play"}</span>`;
      if (on) timer = setInterval(() => { if (cur >= total - 1) setPlaying(false); else go(cur + 1); }, opts.delay || 3600);
    };
    function go(i) {
      cur = Math.max(0, Math.min(total - 1, i));
      wrap.querySelector('[data-a="prev"]').disabled = cur === 0;
      wrap.querySelector('[data-a="next"]').disabled = cur === total - 1;
      wrap.querySelector(".frame-count").textContent = `${cur + 1} / ${total}`;
      $$(".frame-dots button", wrap).forEach((b, k) => b.classList.toggle("on", k === cur));
      if (!timer) playBtn.innerHTML = `${ICON.play}<span>${cur === total - 1 ? "Replay" : "Play"}</span>`;
      onGo(cur);
    }
    wrap.addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return;
      const a = b.dataset.a;
      if (b.dataset.i) { setPlaying(false); go(+b.dataset.i); }
      else if (a === "prev") { setPlaying(false); go(cur - 1); }
      else if (a === "next") { setPlaying(false); go(cur + 1); }
      else if (a === "reset") { setPlaying(false); go(0); }
      else if (a === "play") {
        if (timer) setPlaying(false);
        else { if (cur === total - 1) go(0); setPlaying(true); }
      }
    });
    go(0);
    return { el: wrap, play: () => setPlaying(true), go };
  }
  function autoplayWhenVisible(el, ctl) {
    if (reduceMotion || !("IntersectionObserver" in window)) return;
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { ctl.play(); io.disconnect(); } }), { threshold: 0.45 });
    io.observe(el);
  }

  /* ================= two-view animation =================
     <div class="anim" data-frames="5"> … SVG elements with data-on="2-4" | "3" | "2,5" | "3-"
     and optional data-pos='{"1":"0,0","3":"140,0"}' (translate per frame)
     Each .view has <ol class="caps" hidden><li>caption for frame 1</li>…</ol> */
  const inRange = (spec, f) => spec.split(",").some(part => {
    const [a, b] = part.split("-");
    const lo = +a, hi = b === undefined ? +a : b === "" ? Infinity : +b;
    return f >= lo && f <= hi;
  });
  $$(".anim").forEach(anim => {
    const total = +anim.dataset.frames || 1;
    const views = $$(".view", anim).map(v => {
      const caps = $$(".caps li", v).map(li => li.innerHTML);
      let capEl = v.querySelector(".caption");
      if (!capEl) { capEl = document.createElement("div"); capEl.className = "caption"; capEl.setAttribute("aria-live", "polite"); v.appendChild(capEl); }
      return { caps, capEl };
    });
    const onEls = $$("[data-on]", anim), posEls = $$("[data-pos]", anim);
    posEls.forEach(el => { try { el._pos = JSON.parse(el.dataset.pos); } catch (e) { el._pos = {}; } });
    const ctl = makeControls(total, i => {
      const f = i + 1;
      onEls.forEach(el => el.classList.toggle("on", inRange(el.dataset.on, f)));
      posEls.forEach(el => {
        let p = null;
        for (let k = 1; k <= f; k++) if (el._pos[k]) p = el._pos[k];
        if (p) { const [x, y] = p.split(",").map(Number); el.style.transform = `translate(${x}px,${y}px)`; }
      });
      views.forEach(v => { v.capEl.innerHTML = v.caps[i] || ""; });
    }, { delay: +anim.dataset.delay || 4200 });
    anim.appendChild(ctl.el);
    autoplayWhenVisible(anim, ctl);
  });

  /* ================= code tracer =================
     JSON: { "lang":"java", "code":[lines…], "steps":[ { "line":3 | [1,7], "phase":"JVM",
            "note":"html", "stack":[{"frame":"main()","vars":[["args","String[0]"]]}],
            "heap":["html"], "out":"text printed at this step", "newVar":"name" } ] } */
  $$(".tracer").forEach(tr => {
    const d = readJSON(tr); if (!d) return;
    const lang = d.lang || "java";
    // optional "labels": {"stack":[title, sub], "heap":[title, sub], "emptyStack": text, "emptyHeap": text}
    const L = Object.assign({ stack: ["Stack", "method calls + local variables"], heap: ["Heap", "objects"], emptyStack: "empty: no method is running", emptyHeap: "no objects yet" }, d.labels || {});
    tr.insertAdjacentHTML("beforeend", `
      <div class="tracer__grid">
        <div class="tracer__code">${d.code.map((l, i) => `<div class="tline" data-ln="${i + 1}"><span class="ln">${i + 1}</span><span>${highlight(l, lang) || " "}</span></div>`).join("")}</div>
        <div class="tracer__state">
          <div class="tracer__note"></div>
          <div class="mem"><h5>${esc(L.stack[0])} <em>${esc(L.stack[1])}</em></h5><div class="mem__body" data-k="stack"></div></div>
          <div class="mem"><h5>${esc(L.heap[0])} <em>${esc(L.heap[1])}</em></h5><div class="mem__body" data-k="heap"></div></div>
          <div class="mem"><h5>Console <em>output</em></h5><div class="console" data-k="out"></div></div>
        </div>
      </div>`);
    const lines = $$(".tline", tr), note = tr.querySelector(".tracer__note");
    const stackEl = tr.querySelector('[data-k="stack"]'), heapEl = tr.querySelector('[data-k="heap"]'), outEl = tr.querySelector('[data-k="out"]');
    const ctl = makeControls(d.steps.length, i => {
      const s = d.steps[i];
      const act = Array.isArray(s.line) ? s.line : s.line ? [s.line, s.line] : [0, -1];
      const doneTo = d.steps.slice(0, i).reduce((mx, st) => Math.max(mx, Array.isArray(st.line) ? 0 : st.line || 0), 0);
      lines.forEach((el, k) => {
        const n = k + 1;
        el.classList.toggle("is-active", n >= act[0] && n <= act[1]);
        el.classList.toggle("is-done", !(n >= act[0] && n <= act[1]) && n <= doneTo && !Array.isArray(s.line));
      });
      const activeEl = lines[act[0] - 1];
      if (activeEl) { const box = activeEl.parentElement; const t = activeEl.offsetTop - box.clientHeight / 2; if (box.scrollHeight > box.clientHeight) box.scrollTop = t; }
      note.innerHTML = (s.phase ? `<b>${esc(s.phase)} · </b>` : "") + (s.note || "");
      stackEl.innerHTML = (s.stack && s.stack.length)
        ? s.stack.slice().reverse().map(f => `<div class="frame"><b>${esc(f.frame)}</b>${(f.vars || []).map(v => `<div class="var${v[0] === s.newVar ? " new" : ""}"><span>${esc(v[0])}</span><span>${esc(v[1])}</span></div>`).join("") || '<span class="empty-note">no local variables yet</span>'}</div>`).join("")
        : `<span class="empty-note">${esc(L.emptyStack)}</span>`;
      heapEl.innerHTML = (s.heap && s.heap.length) ? s.heap.map(h => `<span class="obj">${h}</span>`).join("") : `<span class="empty-note">${esc(L.emptyHeap)}</span>`;
      outEl.textContent = d.steps.slice(0, i + 1).map(st => st.out || "").join("");
    }, { delay: 3200 });
    tr.appendChild(ctl.el);
  });

  /* ================= live code runner =================
     JSON: { "lang":"java", "file":"Main.java", "tasks":[{"label":"…","hint":"html","code":"…"}] } */
  $$(".runner").forEach(rn => {
    const d = readJSON(rn); if (!d || !d.tasks || !d.tasks.length) return;
    const cfg = window.MP_CONFIG || {};
    let task = 0, frame = null;
    rn.insertAdjacentHTML("beforeend", `
      <div class="runner__tasks">${d.tasks.map((t, i) => `<button type="button" data-i="${i}" class="${i ? "" : "on"}">${esc(t.label)}</button>`).join("")}</div>
      <div class="runner__hint">${d.tasks[0].hint || ""}</div>
      <div class="runner__stage">
        <div class="runner__gate">
          <div>
            <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#F5C77E" stroke-width="1.6" style="margin:0 auto"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8h18"/><path d="M10 12l4 2.5-4 2.5z" fill="#F5C77E"/></svg>
            <p>${d.lang === "bash" ? "Loads a real Bash shell on a Linux machine." : `Loads a real ${esc((d.lang || "java").toUpperCase())} compiler.`} Edit the code, press <b>Run</b>, and see your own output. Your code is sent to OneCompiler only to run it.</p>
            <button class="btn btn--solid" type="button" data-load>Open the live editor</button>
          </div>
        </div>
      </div>
      <div class="runner__foot">Editor powered by OneCompiler. Tip: on a phone, turn your screen sideways for a bigger editor.</div>`);
    const stage = rn.querySelector(".runner__stage"), hint = rn.querySelector(".runner__hint");
    const send = () => {
      if (!frame) return;
      const t = d.tasks[task];
      frame.contentWindow.postMessage({ eventType: "populateCode", language: d.lang || "java", files: [{ name: d.file || "Main.java", content: t.code }] }, "*");
    };
    rn.querySelector("[data-load]").addEventListener("click", () => {
      const dark = document.documentElement.dataset.theme === "dark" || (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
      const base = cfg.runnerUrl || "https://onecompiler.com/embed/";
      frame = document.createElement("iframe");
      frame.title = "Live code editor";
      frame.loading = "lazy";
      frame.src = `${base}${d.lang || "java"}?listenToEvents=true&hideLanguageSelection=true&hideNew=true&hideNewFileOption=true&hideTitle=true&hideEditorOptions=true${dark ? "&theme=dark" : ""}`;
      frame.addEventListener("load", () => { send(); setTimeout(send, 1200); setTimeout(send, 3000); });
      stage.innerHTML = ""; stage.appendChild(frame);
    });
    rn.querySelector(".runner__tasks").addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return;
      task = +b.dataset.i;
      $$(".runner__tasks button", rn).forEach(x => x.classList.toggle("on", x === b));
      hint.innerHTML = d.tasks[task].hint || "";
      send();
    });
  });

  /* ================= modifier lab =================
     <div class="modlab"> .modlab__bar buttons[data-mod] + .modlab__panel[data-mod]. All panels are plain HTML
     (readable without JS); the script turns them into switchable tabs. */
  $$(".modlab").forEach(ml => {
    const btns = $$(".modlab__bar button", ml), panels = $$(".modlab__panel", ml);
    if (!btns.length) return;
    ml.classList.add("is-js");
    const show = m => {
      btns.forEach(b => { const on = b.dataset.mod === m; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); });
      panels.forEach(p => p.classList.toggle("on", p.dataset.mod === m));
    };
    btns.forEach(b => b.addEventListener("click", () => show(b.dataset.mod)));
    show(btns[0].dataset.mod);
  });

  /* ================= quiz =================
     JSON: [ { "q":"…", "options":["…"], "answer":1, "why":"html" } ] */
  $$(".quiz").forEach(qz => {
    const d = readJSON(qz); if (!d) return;
    let answered = 0, right = 0;
    qz.insertAdjacentHTML("beforeend", d.map((q, i) => `
      <div class="q" data-i="${i}">
        <p><span>Q${i + 1}.</span>${esc(q.q)}</p>
        <div class="opts">${q.options.map((o, k) => `<button class="opt" type="button" data-k="${k}">${esc(o)}</button>`).join("")}</div>
        <div class="why">${q.why || ""}</div>
      </div>`).join("") + `<div class="score" hidden></div>`);
    qz.addEventListener("click", e => {
      const b = e.target.closest(".opt"); if (!b) return;
      const box = b.closest(".q"), q = d[+box.dataset.i];
      if (box.classList.contains("done")) return;
      box.classList.add("done");
      const k = +b.dataset.k;
      $$(".opt", box).forEach((o, j) => { o.disabled = true; if (j === q.answer) o.classList.add("right"); });
      if (k !== q.answer) b.classList.add("wrong"); else right++;
      answered++;
      if (answered === d.length) {
        const s = qz.querySelector(".score"); s.hidden = false;
        s.textContent = `You scored ${right} / ${d.length}. ${right === d.length ? "Perfect! 🎉" : right >= d.length * 0.6 ? "Well done. Review the explanations above for the ones you missed." : "Read the lesson once more and try again. Every expert started here."}`;
      }
    });
  });

  /* ================= previous / next + outline ================= */
  const C = window.MP_COURSE, here = document.body.dataset.lesson;
  if (C && here) {
    const flat = [];
    C.modules.forEach(m => m.lessons.forEach(l => flat.push({ ...l, mod: m, path: `${m.slug}/${l.slug}/` })));
    const idx = flat.findIndex(l => l.path === here + "/" || l.path === here);
    const root = document.body.dataset.courseRoot || "../../";
    const link = (l, cls, label) => !l ? `<span class="${cls}"><small>${label}</small>${cls === "prev" ? "Start of course" : "End of course"}</span>`
      : l.live ? `<a class="${cls}" href="${root}${l.path}"><small>${label}</small>${esc(l.n)} ${esc(l.title)}</a>`
      : `<span class="${cls}"><small>${label} · coming soon</small>${esc(l.n)} ${esc(l.title)}</span>`;
    const nav = document.getElementById("lesson-nav");
    if (nav && idx >= 0) nav.innerHTML = link(flat[idx - 1], "prev", "← Previous") + link(flat[idx + 1], "next", "Next →");
    const out = document.getElementById("outline");
    if (out && idx >= 0) {
      const m = flat[idx].mod;
      out.innerHTML = `<h4>Module ${m.n}: ${esc(m.title)}</h4>` + m.lessons.map(l => {
        const p = `${m.slug}/${l.slug}/`;
        if (p === flat[idx].path) return `<a class="here" href="#">${esc(l.n)} ${esc(l.title)}</a>`;
        return l.live ? `<a href="${root}${p}">${esc(l.n)} ${esc(l.title)}</a>` : `<span>${esc(l.n)} ${esc(l.title)} · soon</span>`;
      }).join("") + `<a href="${root}" style="margin-top:6px;font-weight:700">Full ${esc(C.title)} syllabus →</a>`;
    }
  }

  /* ================= TOC + reading progress ================= */
  const bar = document.createElement("div"); bar.className = "read-progress"; document.body.appendChild(bar);
  addEventListener("scroll", () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + "%";
  }, { passive: true });
  const tocLinks = $$(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    const map = new Map(tocLinks.map(a => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { tocLinks.forEach(a => a.classList.remove("is-current")); const a = map.get(e.target.id); if (a) { a.classList.add("is-current"); const ol = a.closest("ol"); if (ol && ol.scrollWidth > ol.clientWidth) ol.scrollLeft = a.offsetLeft - ol.clientWidth / 2; } }
    }), { rootMargin: "-30% 0px -60% 0px" });
    $$(".part[id]").forEach(s => io.observe(s));
  }
})();
