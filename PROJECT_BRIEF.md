# MyPhatshala: Project Brief (handoff for any AI assistant)

Read this whole file before doing any work on this project. It records every decision made so far.

## 1. What the project is
**MyPhatshala** ("pathshala" = school) is a free educational website for students learning IT:
programming, databases, data analytics, big data, AI/ML, cloud and DevOps, in the spirit of
GeeksforGeeks / W3Schools / TutorialsPoint / DataFlair, but with a distinct teaching method:
**every concept is shown in two views: what you see on screen, and what happens behind the screen.**

- Owner: Anuj. Project folder on his PC: `E:\myPhatshala`.
- Audience: Indian students (college, job-seekers, interview prep). Simple English, Indian examples (UPI, IRCTC-style booking, chai stall, Kharghar/Navi Mumbai).

## 2. Decisions already made (do not change without asking Anuj)
| Topic | Decision |
|---|---|
| Login / accounts | **None.** All content is free and open. |
| Money | **Google AdSense only.** No premium tier, no Razorpay, no paid content. |
| Ad slots | `<div class="ad-slot" data-slot="top|mid|side|bottom">`, filled by `assets/js/ads.js` from `assets/js/config.js`. Grey placeholders on localhost; hidden on the live site until an AdSense ID is set. |
| Watermark | Faint tiled "MyPhatshala" over every page (`body.has-watermark::after`) plus "myphatshala.in" text inside every SVG. Must stay readable. |
| Code running | **Sandboxed. Nothing runs on our server.** Java uses the **OneCompiler embed** iframe, loaded only on click and filled via `postMessage({eventType:'populateCode'…})`. Docs: https://onecompiler.com/apis/embed-editor. Swappable later (CheerpJ, Pyodide for Python). |
| Tech stack | Plain HTML + CSS + vanilla JS. No framework, no database, no npm dependencies. Node.js is only used for the build script. |
| Hosting plan | GitHub repo → Cloudflare Pages (free). Build command `node tools/build-manifest.js`, output `/`. |
| Security | Static site, HTTPS, `_headers` file with security headers, 2FA on accounts. No secrets in frontend. |
| Design | Light theme: mint-white background `#F5FAF7` (panels `#E9F3EE`, lines `#D5E6DD`, changed 15 Oct 2026), ink navy, saffron accent `#E8772E`, chalkboard dark green `#1F2B26`. Fonts: Fraunces (headings), Atkinson Hyperlegible (body), JetBrains Mono (code). Light + dark mode. Must work at 390px phone width with **no horizontal scroll**. |

## 3. Content structure
```
Track (10, in courses/_tracks.json) → Course (59) → Module (297) → Lesson (1,119)
```
Tracks: Programming Languages · Web Development · CS Fundamentals · Databases (SQL & NoSQL) · Data Analytics · Big Data Engineering · AI & ML · Cloud · DevOps & Tools · Security & Software Engineering.
Career paths are in `courses/_paths.json` (Data Analyst, Data Engineer, ML Engineer, Java Backend, Full-Stack, Cloud/DevOps).

## 4. Folder structure and build
```
index.html                        home: hero search, tracks, course grid, career paths
about/contact/privacy/disclaimer.html   (AdSense needs these; owner must fill About + contact email)
assets/css/style.css              site-wide styles
assets/css/lesson.css             lesson components
assets/js/config.js               siteUrl, adsenseClient, adSlots, watermark
assets/js/main.js                 home page
assets/js/course.js               course page
assets/js/lesson.js               LESSON ENGINE (see section 6)
assets/js/site.js, ads.js
courses/_tracks.json, _paths.json
courses/<course-id>/course.json   syllabus: the single source of truth for a course
courses/<course-id>/index.html    GENERATED course page (never edit by hand)
courses/<course-id>/<module-slug>/<lesson-slug>/index.html   a lesson; if the file exists, the lesson is LIVE
tools/build-manifest.js           the builder
tools/templates/course.html       template for course pages
data/                             GENERATED: catalog.js, search-index.js, courses/<id>.js, manifest.json
build.bat                         double-click on Windows to rebuild
```
**After adding or changing any lesson or course.json, run `node tools/build-manifest.js`** (or `build.bat`).
It marks lessons live, regenerates course pages, the search index, per-course outlines (used for lesson
Previous/Next), and `sitemap.xml`. A lesson folder name must exactly equal the slug in course.json.


**Authoring helpers (optional, for AI assistants):** `tools/authoring/gen.py SRC SITE_ROOT` wraps a lesson body (with `<part>`, `<riya>`, `<arjun>`, `<exam>`, `<tip>`, `<warn>`, `{{AD}}` macros and a META JSON header) in the standard page shell. `tools/authoring/verify.py SITE_ROOT courses/<course>/<module>/<lesson> [--shots]` checks JSON, quiz, animation captions, compiles/runs every Java example (runner tasks may set `"_expect": "compile-error"|"exception"`), compares printed output, and tests the page in a browser at 1280/390px (needs a local server on port 8765, JDK, Python Playwright). `tools/authoring/mkworked.py SPEC.py OUT.html` builds the worked-examples block: it compiles each solution with `-g`, runs it under the JDI tracer in `tools/authoring/jtrace` (compile `JTrace.java` and `JTraceBoot.java` with javac first), checks the traced output against a normal run, and pairs each recorded step with the author's note (`--skeleton` prints the step list to write notes against). verify.py also checks text contrast in light and dark themes. The generated `index.html` remains the source of truth.

## 5. The lesson format: every lesson has these 9 parts, in this order
1. **The story**: a short scene with **Riya** (student) and **Arjun Sir** (mentor), using comic panels (`.panel`, `.bubble`) and one SVG scene. It shows why the concept exists.
2. **Definition**: formal exam-ready definition (dark box) + "In simple words" + key terms grid + facts table + exam-tip callout.
3. **Types and ways to use it**: all variants/forms, as cards and/or a comparison table.
4. **Step by step**: `.stepper` with a "Behind the screen" note (`.behind`) on each step.
5. **Two-view animation**: `.anim` with "What you see" and "Behind the screen" SVGs, 5–7 frames, captions per frame.
6. **Real-world use**: 5–7 `.usecase` blocks with small SVG art + a flow line showing where the concept fits. Add a note that examples are simplified.
7. **Run the code**: annotated code block, then a `.runner` with 4–5 challenges (include a "predict first" and a "spot the error").
8. **Line by line**: `.tracer` with stack / heap / console per step.
9. **Quiz and revision**: 6–8 MCQs with explanations, a one-screen revision card, and interview/viva Q&A (`.faq`).
   For heavier topics (Module 3 onwards): **Practice problems** (`<h3 id="practice">` + `.probs` > `article.prob`, added 15 Oct 2026): 5–15 problems tagged Easy / Medium / Business problem (`.prob__tag--easy|medium|business`), each with a simple statement, an Input/Expected output box (`.prob__io`), and a collapsible `details.prob__sol` "Show solution and explanation" containing a verified `.code` block plus a step-by-step explanation. A few per lesson are real-world business problems. TOC entry "Practice problems" before "Industry scenarios".
   **Worked examples** (every lesson from Module 4 on, added 15 Oct 2026): `<h3 id="worked">` at the end of part 8 ("Line by line"), then 3 × `article.wx`. Each has: a business/real-time problem statement, Input / Expected output (`.prob__io`, output taken from a real run), a numbered Approach, a one-task live runner with the full solution, and a tracer whose stack frames, local variables, heap objects (numbered #1, #2 …) and console output are **recorded from the real JVM** (JDI, `tools/authoring/jtrace`), with a plain-language note for every step explaining what was called, pushed, popped, created or changed. Prefer examples with a helper method so readers see frames being pushed and popped. Keep each trace to roughly 8–30 steps. TOC entry "Worked examples" after "Line by line".
   Then **Industry scenarios** (`<h3 id="scenarios">` + `.scenarios` > `.scn` cards, added 15 Oct 2026): 4–5 real workplace situations a company interviewer would describe. Each card has an industry/level tag (`.scn__tag`, `.scn__tag--level`), the situation, "The interviewer is checking" (`.scn__look`), a collapsible strong answer (`.scn__answer`) and an "Avoid saying" line (`.scn__avoid`). Add `<li><a href="#scenarios">Industry scenarios</a></li>` to the TOC. See Lesson 1.2 for the pattern.

Each lesson head needs `<title>… | MyPhatshala</title>`, `<meta name="description">`, `<meta name="mp:minutes" content="15">`, canonical URL, JSON-LD LearningResource.
Body: `style="--track:<track colour>" data-lesson="<module-slug>/<lesson-slug>" data-course-root="../../"`.
Scripts at end: `data/courses/<course-id>.js`, `lesson.js`, `ads.js`, `site.js` (relative paths `../../../../`).
**Use `courses/core-java/01-introduction/01-what-is-java/index.html` as the reference template.** Copy its structure.

**Authoring pipeline (used for Modules 5–10):** each lesson has `tools/authoring/src/<course>/<module>/<lesson>/lesson.html` + `spec.py`; run `python3 tools/authoring/build.py SRC_DIR SITE_ROOT`, then `node tools/build-manifest.js`, then `verify.py`. Additions on 16 Oct 2026:
- `spec.py` may define `BLOCKS = {'KEY': html}`; `{{KEY}}` in lesson.html is replaced. Part 5's two-view animation is built with `mkanim.two_view(title, see_anim, behind_anim)` and placed with `{{ANIM}}`.
- Tracer notes written `"Phase :: = text"` **replace** the automatic description instead of adding to it (use when the automatic text would mislead).
- Automatic notes call small boxed values (Integer/Long/Short/Byte -128..127, Boolean) *cached* objects, not new ones.
- `jtrace/JTrace.java` now shows the synthetic fields `this$0` (inner class → outer object) and `val$x` (captured locals) on the heap. Recompile it with `javac JTrace.java JTraceBoot.java` after pulling.
- JTrace also shows ArrayList **capacity**, ArrayDeque contents (front → back), PriorityQueue's heap array and `List.of` contents, and skips javac's generic **bridge methods** (e.g. `compareTo(Object)`) so sorting traces show only your code.
- verify.py compares outputs exactly: avoid trailing spaces in printed lines (`print(x + " ")` at line end).
- Known limit: JDI does not step into an **enum's** static initialiser, so traces show enum constants already built; explain this in the note.
- Text inside mkanim `A.text/A.box` is raw SVG: write generics as `List&lt;Integer&gt;`.

## 6. Lesson engine data formats (assets/js/lesson.js)
- **Code block:** `<div class="code" data-lang="java" data-file="Main.java"><pre><code>…</code></pre><div class="output">…</div></div>`. Highlighting + copy button are automatic (java, python, sql, bash).
- **Animation:** `<div class="anim" data-frames="6">`. Any SVG element with `data-on="2-4"`, `"3"`, `"2,5"` or `"3-"` is visible only on those frames. `data-pos='{"1":"0,0","3":"120,40"}'` moves an element per frame. Captions: `<ol class="caps" hidden><li>…</li></ol>` inside each `.view`, one `<li>` per frame. Use theme-aware SVG classes: `s-card s-card2 s-board s-ink s-ink2 s-ink3 s-chalk s-kw s-str s-acc s-green s-blue s-red s-wire s-line s-soft-green s-soft-blue s-soft-acc s-wm mono`.
- **Tracer:** `<div class="tracer"><script type="application/json">{"lang":"java","code":[lines],"steps":[{"line":3 or [1,8],"phase":"JVM","note":"html","stack":[{"frame":"main(String[] args)","vars":[["year","1995"]]}],"heap":["html"],"out":"printed text\n","newVar":"year"}]}</script></div>`. Stack and heap are full snapshots per step; output accumulates.
- **Runner:** `<div class="runner"><script type="application/json">{"lang":"java","file":"Main.java","tasks":[{"label":"1 · …","hint":"html","code":"…"}]}</script></div>`. Java class must be `public class Main`.
- **Quiz:** `<div class="quiz"><script type="application/json">[{"q":"…","options":["…"],"answer":1,"why":"html"}]</script></div>`.
- Previous/Next and the module outline are automatic.

## 7. Writing and quality rules
- Simple, friendly English. Short sentences. Explain every new term the first time.
- All diagrams are **original SVG**. Never draw logos, mascots or copyrighted characters (e.g. no Android robot, no Minecraft characters, no brand logos).
- Facts must be correct. Don't claim a specific company's internal technology unless it's well established; phrase generally ("many banks use Java…").
- **Verify before delivering:** compile and run every code example with a real compiler and confirm the output written in the lesson matches. Check bytecode/internals claims with tools (e.g. `javap -c`). Test pages at 1280px and 390px, light and dark, with no JS errors and no horizontal scroll.
- Never remove the watermark or the ad slots.

## 8. Status (as of 15 Oct 2026)
- ✅ Site structure, home page, 59 course pages, search, career paths, policy pages.
- ✅ Lesson engine built.
- ✅ **Core Java Lesson 1.1 "What is Java and why learn it?"** is complete and live (the reference template).
- ✅ **Core Java Modules 1–4 (Lessons 1.1–4.6)** are complete and live (15 Oct 2026).
- ✅ **Core Java Modules 5–9** are live (added before 16 Oct 2026).
- ✅ **16 Oct 2026:** Lesson 6.5 (Access modifiers) now has a **modifier lab** (`.modlab`): one field `ifsc` in `bank.Account`, read from 5 places (same class, same package, subclass in another package, unrelated class in another package, subclass via a parent object). Buttons switch public/protected/default/private and show the real javac result per place, the `Main` that compiles, and its real output (5 → 3 → 2 → 1 lines), plus a summary table. Generated by `tools/authoring/mkmodlab.py` from `spec.py` (`BLOCKS`).
- ✅ **16 Oct 2026: Module 10 Core Classes (Lessons 10.1–10.5)** complete and live: wrapper classes, autoboxing, Object class (equals/hashCode/toString), enums, inner/static nested/anonymous classes. Sources in `tools/authoring/src/core-java/10-core-classes/`.
- ✅ **16 Oct 2026: Module 11 Collections (Lessons 11.1–11.8)** complete and live: overview, generics, ArrayList, LinkedList, HashSet/LinkedHashSet/TreeSet, HashMap internals (real JVM traces of a collision in bucket 9 and the 16 → 32 resize), Iterator/ListIterator, Comparable vs Comparator. Sources in `tools/authoring/src/core-java/11-collections/`.
- ✅ **16 Oct 2026: Module 12 Multithreading (Lessons 12.1–12.6)** complete and live: processes vs threads, Thread vs Runnable, lifecycle (all six states observed deterministically), synchronization (race on count++ at bytecode level, monitors, volatile, atomics, deadlock), wait/notify (monitor wait set, producer–consumer, BlockingQueue), ExecutorService (Callable/Future, invokeAll, timeouts, shutdown, CompletableFuture, virtual threads). Sources in `tools/authoring/src/core-java/12-multithreading/` (helper `m12.py`). JTrace: lambda variables now shown as "lambda".
- ✅ **16 Oct 2026: Module 13 File Handling and I/O (Lessons 13.1–13.4)** complete and live: byte vs character streams (₹ = 3 UTF-8 bytes, charset bugs like "â‚¹"), Path/Files (create, append, read, copy, move, delete, working directory), buffered I/O (OS-call counts proven with a counting stream, readLine loop, flush vs close), serialization (transient, static, object graphs and shared references, serialVersionUID, security). Sources in `tools/authoring/src/core-java/13-file-io/` (helper `m13.py`). Code that prints ₹ wraps System.out in a UTF-8 PrintStream so output is the same on every console.
- ✅ **17 Oct 2026: Module 14 Modern Java (Lessons 14.1–14.5)** complete and live: lambdas (anonymous class → lambda, invokedynamic), functional interfaces (Predicate/Function/Consumer/Supplier, composition, method references), Stream API (lazy, one-element-at-a-time pipelines, groupingBy), Optional (orElse vs orElseGet, flatMap chains), var/records/text blocks. Sources in `tools/authoring/src/core-java/14-modern-java/` (helper `m14.py`). Modules 12–13 refreshed: some worked-example notes were attached to the wrong line. `build.py` now prints a WARNING when a trace note never matches a traced line.
- ✅ **17 Oct 2026: Modules 1–3 brought to the full standard.** Every lesson now has 3 worked examples (business problem, live code, JVM trace). Modules 1–2 also gained 8 practice problems per lesson. These were added to the already-built pages with `tools/authoring/addblocks.py PAGE extra.py`; per-lesson sources are in `tools/authoring/src/core-java/0[1-3]-*/<lesson>/extra.py`. build.py fix: worked-example traces now pass their stdin to the page (needed for Scanner examples).
- ✅ **Core Java: all 14 modules (84 lessons) live, every lesson with worked examples and practice problems.** From Module 4 on, every lesson also has 3 **worked examples** (business problem, live solution, JVM-recorded memory trace). Home hero redesigned (rotating topic headline, feature points, count-up stats); track chips wrap instead of scrolling.
- ⏳ Waiting for Anuj's feedback on Lesson 1.1's format before writing more.
- ⏳ OneCompiler live editor still needs testing on a real internet connection (click "Open the live editor").

## 9. Next steps
1. Get Anuj's approval/changes on Lesson 1.1.
2. Write Core Java Module 1: 1.2 History and features, 1.3 JDK vs JRE vs JVM, 1.4 How Java code runs, 1.5 Installing Java and first program, 1.6 Structure of a Java program. Then continue module by module.
3. Owner to-dos: copy `.github/workflows/build-manifest.yml` into the folder; fill About page + contact email; buy a domain and set `siteUrl` in `config.js` and `robots.txt`; push to GitHub + Cloudflare Pages; apply for AdSense after ~15–20 live lessons, then add the publisher ID to `config.js` and `ads.txt`.

## Big Data track: Python lesson pipeline (added 19 Oct 2026)
- Big Data lessons use **Python simulations** in the browser runner plus **"Run on your PC"** panels (`.pcrun`, real commands with output recorded from a real run).
- Source per lesson: `tools/authoring/src/<course>/<module>/<lesson>/` with `body.html` (parts 1–6; lines starting `A>`, `R>`, `EXAM>`, `TIP>`, `WARN>` are macros) and `spec.py` (runner tasks, PC panels, trace, worked examples, quiz, revision, FAQ, practice, scenarios). Shared course settings: `src/<course>/course.py`.
- Build: `python3 tools/authoring/pylesson.py tools/authoring/src/<course>/<module>/<lesson>` — every program is really run; expected outputs and line-by-line traces (sys.settrace) are generated, never typed by hand. Then `node tools/build-manifest.js`.
- Visual check: `python3 tools/authoring/svgprev.py <page.html> tools/authoring/_preview/<name>` renders every SVG/animation frame to PNG (folder is git-ignored).
- ✅ Big Data Fundamentals Module 1 (lessons 1.1–1.3) live.
- ✅ Big Data Fundamentals Module 2 (lessons 2.1–2.4) live, in the richer format: a Beginner/Intermediate/Advanced tab block (`LEVELS>` macro in body.html, reuses the `.modlab` tabs), 1 two-view + 3 real-time scenario animations per lesson, examples tagged with `level` ('b'/'i'/'a'), practice level `advanced`, and a recurring character Kabir (`K>` macro). New CSS: `.levels`, `.lvl--b/i/a`, `.live`, `--violet`/`.s-violet`/`.s-soft-violet`.
- ✅ Big Data Fundamentals Module 3 (lesson 3.1 careers) live → the whole Big Data Fundamentals course (8 lessons) is complete. Salary table in 3.1 uses indicative 2026 India ranges from published salary guides; refresh yearly.

## Hadoop capstone + AdSense (added 23 Oct 2026)
- ✅ **Hadoop Module 14 Capstone (Lessons 14.1–14.3) live** → the whole Apache Hadoop course is complete. Sources: `tools/authoring/src/hadoop/14-capstone/`; lab scripts and real transcripts in `14-capstone/lab/` (`txout/`).
- Dataset: `lab/make_capstone.py` (seed 14) → "Kadak Canteens" (fictional), 4 canteens, Sept 2026: 104 POS CSVs + 26 UPI JSONL + menu + `truth.json`. Generated data (`capstone_raw/`) and local test files (`local_*`) are git-ignored.
- Real runs on the Module 8 lab (Hadoop 3.5.0, 3 workers) + Spark 4.0.4: clean job 104 maps 4m39s; Spark silver/gold 1m32s; check.py 10/10 PASS; compaction → 4 maps 53 s, byte-identical (md5 e4cb8704…); failure drill and the 3-DataNode job-history fix (`replace-datanode-on-failure.policy=NEVER`).
- AdSense: publisher ID `ca-pub-5906362345660187` set in `assets/js/config.js` and `ads.txt`; Google's `adsbygoogle.js` tag is now static in the `<head>` of every page and in all generators (gen.py, pylesson.py, extras.py, templates/course.html). `ads.js` skips loading it twice. Ad slot IDs are still empty (create ad units after approval). Owner to-do: fill About page text and contact email before applying.
