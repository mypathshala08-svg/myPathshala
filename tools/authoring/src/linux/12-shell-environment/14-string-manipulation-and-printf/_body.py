import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

ST = r"""rm -rf ~/st; mkdir -p ~/st/in; cd ~/st
touch in/IMG_2041.JPG in/IMG_2042.JPG 'in/holiday photo.jpeg' in/report.final.v2.pdf
printf 'riya@example.com\naman.k@mail.co.in\nzoya@corp.example.org\n' > emails.txt"""

HOOK = hook('Riya needs the extension of a file name, the folder part of a path, the domain of an email, a name in capitals and a neatly aligned table. Her first scripts call <code>basename</code>, <code>sed</code>, <code>awk</code> and <code>tr</code> for each of these, starting a new program every time. Bash can do all of it inside the shell with <b>parameter expansion</b>: <code>${f%.*}</code> removes an extension, <code>${email#*@}</code> keeps the domain, <code>${name^^}</code> makes capitals, <code>${s/old/new}</code> replaces, <code>${s:0:3}</code> cuts. <b>printf</b> then prints it all in exact columns. In a loop over 10,000 files this is the difference between seconds and minutes.',
    ['measure, cut and slice strings with ${#s} and ${s:start:len}',
     'remove prefixes and suffixes with # ## % %% (for extensions, paths, emails)',
     'replace, change case and set defaults with ${s/a/b} ${s//a/b} ${s^^} ${s,,} ${s:-x}',
     'format output with printf: %s %d %f %x, widths, alignment, padding, -v and %q'])
ROAD = roadmap([
    ('story', 'The story', 3, 'strings without sed'),
    ('decide', 'Which form when?', 2, 'the quick chart'),
    ('definition', 'Parameter expansion', 6, 'simple meaning + 4 depths'),
    ('types', 'Every form', 5, 'the full table'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, '# vs ## and % vs %%'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'rename photos'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which form? (decide in 5 seconds)', [
    ('Length of a string', '${#s}', 'count'),
    ('Part of a string', '${s:0:4}   ${s: -3}', 'substring'),
    ('Remove the extension', '${f%.*}', 'shortest suffix'),
    ('Only the extension', '${f##*.}', 'longest prefix'),
    ('File name from a path', '${p##*/}', 'like basename'),
    ('Folder from a path', '${p%/*}', 'like dirname'),
    ('Replace text', '${s/old/new}  ${s//old/new}', 'first / all'),
    ('Upper / lower case', '${s^^}  ${s,,}  ${s^}', 'case'),
    ('Aligned columns', "printf '%-10s %5d\\n' …", 'printf'),
])

cmap = concept_map(
    [('12.1', 'Variables', '${var} and quotes'), ('12.11', 'Expansion', 'step 3: parameters'), ('12.13', 'Arrays', 'same forms on all items')],
    ['${#s} and ${s:off:len}', '# ## % %% (patterns)', '/ // /# /% replace', '^ ^^ , ,, case', ':- := :? :+ defaults', 'printf formats, widths, -v, %q'],
    [('6.4', 'sed', 'when patterns get complex'), ('6.5', 'awk', 'columns in big files'), ('13.5', 'Data one-liners', 'CSV text'), ('21.1', 'Capstone', 'reports')],
    'Parameter expansion changes the text of a variable without starting another program; printf prints it exactly as you want.')

sc = (term(20, 14, 316, 156, ['$ f=report.final.v2.pdf', '$ echo ${f%.*} ${f##*.}', ('report.final.v2 pdf', 'out'), '$ e=riya@example.com', '$ echo ${e#*@} ${e%@*}', ('example.com riya', 'acc')], title='riya@web01: ~/st', prompt='riya@web01:~/st$', size=6.8, step=17)
      + t(352, 36, 'Inside bash:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['% cut the end', '# cut the start', 'one sign: short', 'two signs: long', 'no sed needed'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Strings without sed</h2>
  <div class="story">
''' + puzzle('Riya wants the name without extension of <code>report.final.v2.pdf</code>. She writes <code>${f%%.*}</code> and gets <code>report</code>. Then <code>printf "%d items\\n" 3.5</code> prints an error and <code>printf "%s\\n" a b c</code> prints three lines although the format has only one %s. And <code>echo ${name^^}</code> on her Mac says “bad substitution”. What is going on?') + '''
    <p class="narration">Riya cuts a file name and an email apart without any other command.</p>
''' + scene('A terminal: removing and keeping the extension of a file name, and splitting an email into domain and user.', sc,
            '<tspan font-weight="700" class="s-acc">#</tspan> cuts from the start, <tspan font-weight="700" class="s-acc">%</tspan> from the end.') + '''
K> How do I remember which is which?
A> On a US keyboard <code>#</code> is left of <code>$</code> and <code>%</code> is right of it: # cuts the left side, % the right side. One sign removes the <b>shortest</b> match, two signs the <b>longest</b>.
R> And the pattern after it?
A> It is a glob, like in <code>ls</code>: <code>*.</code> means “anything, then a dot”. Today: every form, and printf for perfect output.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A ribbon with the text report.final.v2.pdf. Scissors from the left (#) and from the right (%) show the short and long cuts.">'
       + label_box(80, 30, 480, 40, ['r e p o r t . f i n a l . v 2 . p d f'], 'card', 11)
       + t(80, 96, '# *.  → final.v2.pdf', 9.4, 'blue', anchor='start') + t(80, 116, '## *. → pdf', 9.4, 'blue', anchor='start', bold=True)
       + t(560, 96, '%.*  → report.final.v2', 9.4, 'green', anchor='end') + t(560, 116, '%%.* → report', 9.4, 'green', anchor='end', bold=True)
       + t(320, 160, 'One sign: the smallest cut. Two signs: the biggest cut.', 10, 'acc', bold=True)
       + t(320, 182, '# from the left, % from the right.', 9.6, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Parameter expansion at four depths', [
    ('v', 'No jargon: scissors on a ribbon', '      <p>Cut from the left or the right, a little or a lot.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>echo ${#name}</code>: how many characters.</li>
        <li><code>echo ${file%.txt}</code>: drop .txt.</li>
        <li><code>echo ${name^^}</code>: capitals.</li>
        <li><code>printf '%s is %d\\n' Riya 24</code>: formatted line.</li>
      </ul>'''),
    ('i', 'Patterns and printf', '''      <ul>
        <li>Patterns in <code># % /</code> are globs: <code>*</code> <code>?</code> <code>[a-z]</code>, not regex.</li>
        <li><code>${s/#pre/X}</code> replaces only at the start, <code>${s/%suf/X}</code> only at the end.</li>
        <li><code>${s:-def}</code> default if empty, <code>${s:=def}</code> also assigns, <code>${s:?msg}</code> error, <code>${s:+alt}</code> alt if set.</li>
        <li>printf reuses the format until all arguments are used (the three lines in the puzzle).</li>
        <li><code>printf -v var …</code> stores the result instead of printing.</li>
      </ul>'''),
    ('a', 'Behind the screen: built-ins, bytes and locales', '''      <ul>
        <li>All of these are done by bash itself, no <code>fork</code>/<code>exec</code>; a loop with <code>$(basename "$f")</code> starts a process each time (Lesson 11.1).</li>
        <li><code>${#s}</code> counts characters in the current locale: “café” is 4 in a UTF-8 locale, 5 bytes with <code>LC_ALL=C</code>.</li>
        <li>Case operators <code>^^ ,,</code> and <code>${s: -3}</code> negative offsets need bash 4+ (macOS bash 3.2: “bad substitution”).</li>
        <li>printf follows C’s printf: <code>%d</code> needs an integer (3.5 is an error), <code>%f</code> floats, <code>%x %o</code> bases, <code>%5.2f</code> width.precision; <code>%b</code> expands backslashes in the argument; <code>%q</code> quotes for re-use as shell input.</li>
        <li>printf is safer than echo: echo’s handling of <code>-n</code>, <code>-e</code> and backslashes differs between shells.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>String manipulation with parameter expansion, and printf</h2>
''' + def_block(
    '<b>Parameter expansion</b> is the bash feature <code>${…}</code> that returns a changed version of a variable’s value: its length, a substring, the value with a prefix or suffix pattern removed, with text replaced, in another case, or a default. <b>printf</b> is a built-in that prints its arguments according to a <b>format string</b> with conversion specifiers such as <code>%s</code>, <code>%d</code> and <code>%f</code>.',
    'Change text with ${…}; print it exactly with printf.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('String', 'Text in a variable.'),
    ('Substring', 'A part of a string.'),
    ('Offset', 'Start position, from 0.'),
    ('Prefix / suffix', 'The start / end of a string.'),
    ('Pattern', 'A glob such as *. or [0-9]*.'),
    ('Format string', "printf’s template: '%s=%d\\n'."),
    ('Conversion', '%s, %d, %f, %x…'),
    ('Width / precision', '%-10s, %8.2f.'),
]) + '\n' + names('Where the names come from.', [
    ('printf', 'print formatted', 'From C, 1972.'),
    ('%s', 'string', 'Text.'),
    ('%d', 'decimal', 'Integer.'),
    ('%f', 'floating point', 'Decimals.'),
    ('%x / %o', 'hex / octal', 'Bases.'),
    ('#', 'left side of $', 'Prefix.'),
    ('%', 'right side of $', 'Suffix.'),
    ('^ ,', 'up / down', 'Case.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Length', '<code>${#s}</code>'),
    ('Substring', '<code>${s:2:3}</code>'),
    ('Drop suffix', '<code>${s%pat}</code>'),
    ('Drop prefix', '<code>${s#pat}</code>'),
    ('Replace all', '<code>${s//a/b}</code>'),
    ('Format', "<code>printf '%-8s|\\n' x</code>"),
]) + '\n' + lv + didyou('The # / % memory trick is from the bash manual’s own authors: on a US keyboard <b>#</b> sits left of <b>$</b> (cuts the left) and <b>%</b> sits right of it (cuts the right).') + '''
EXAM> “How do you get the length of a string in bash?” → ${#var}. (wc -c also counts the newline and starts a process.)
''' + qc('With <code>p=/var/log/nginx/access.log</code>, what are <code>${p##*/}</code> and <code>${p%/*}</code>?', 'access.log (like basename) and /var/log/nginx (like dirname).') + mistake('${f%%.*} to drop the extension of report.final.v2.pdf',
    '${f%.*} (one %: shortest match from the end)',
    '%% removes the longest match, so everything from the first dot goes: report (real run). One % gives report.final.v2.') + mistake("printf '%d' 3.5",
    "printf '%.0f' 3.5   ·   printf '%s' 3.5   ·   $(( )) is integer-only",
    '%d needs an integer: “invalid number” (real run).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Every string form, and printf’s conversions</h2>
''' + table(['Form', 'Does', 'With s=Hello-World-2026'], [
    ['<code>${#s}</code>', 'length', '16'],
    ['<code>${s:6}</code>', 'from offset 6', 'World-2026'],
    ['<code>${s:6:5}</code>', '5 chars from 6', 'World'],
    ['<code>${s: -4}</code>', 'last 4 (space!)', '2026'],
    ['<code>${s#*-}</code>', 'drop shortest prefix', 'World-2026'],
    ['<code>${s##*-}</code>', 'drop longest prefix', '2026'],
    ['<code>${s%-*}</code>', 'drop shortest suffix', 'Hello-World'],
    ['<code>${s%%-*}</code>', 'drop longest suffix', 'Hello'],
    ['<code>${s/-/ }</code>', 'replace first', 'Hello World-2026'],
    ['<code>${s//-/ }</code>', 'replace all', 'Hello World 2026'],
    ['<code>${s/#Hello/Hi}</code>', 'replace at start', 'Hi-World-2026'],
    ['<code>${s/%2026/27}</code>', 'replace at end', 'Hello-World-27'],
    ['<code>${s^^}</code> <code>${s,,}</code>', 'upper / lower', 'HELLO-WORLD-2026 / hello-world-2026'],
    ['<code>${s^}</code> <code>${s~~}</code>', 'first upper / swap', 'Hello… / hELLO-wORLD-2026'],
], minw=520) + table(['Form', 'If s is empty or unset', 'If s is set'], [
    ['<code>${s:-def}</code>', 'def', '$s'],
    ['<code>${s:=def}</code>', 'def, and s becomes def', '$s'],
    ['<code>${s:?msg}</code>', 'error msg, script stops', '$s'],
    ['<code>${s:+alt}</code>', 'nothing', 'alt'],
], minw=420) + table(['printf', 'Means', 'Example → output'], [
    ['<code>%s</code>', 'string', "<code>printf '%s|' a b</code> → a|b|"],
    ['<code>%d</code> <code>%i</code>', 'integer', "<code>printf '%d' 42</code> → 42"],
    ['<code>%5d</code> <code>%05d</code>', 'width / zero pad', '   42 / 00042'],
    ['<code>%-10s</code>', 'left-align in 10', '"name      "'],
    ['<code>%.2f</code>', '2 decimals', '3.14'],
    ['<code>%x %X %o</code>', 'hex / HEX / octal', 'ff FF 377'],
    ['<code>%e</code>', 'scientific', '1.234500e+03'],
    ['<code>%c</code>', 'first character', 'R'],
    ['<code>%b</code>', 'arg with \\n \\t expanded', 'tab inside'],
    ['<code>%q</code>', 'shell-quoted', "my\\ file"],
    ['<code>%%</code>', 'a literal %', '%'],
    ['<code>%(%F)T</code>', 'date/time (bash)', '2026-11-11'],
], minw=520) + table(['', 'echo', 'printf'], [
    ['New line', 'always (unless -n)', 'only with \\n'],
    ['Backslashes', 'differs by shell / -e', 'in the format always'],
    ['Columns', 'no', 'widths and alignment'],
    ['Safe for any text', 'no (-n, -e as data)', 'yes with %s'],
], minw=420) + qc('What does <code>${s:+x}</code> print when s is empty?', 'Nothing. :+ gives the alternative only when s is set and not empty.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Cutting, trimming, replacing, case and printf, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (bash 5.2, UTF-8 locale) as riya, in <code>~/st</code> with <code>in/</code> (IMG_2041.JPG, IMG_2042.JPG, holiday photo.jpeg, report.final.v2.pdf) and <code>emails.txt</code> (three addresses).</p>
''' + cmdcard_u(['fixed-width codes, dates, IDs', 'checking input length'],
               ['counting bytes for binary data (use wc -c)'])(
    'sub', '${#s} · ${s:off} · ${s:off:len} · ${s: -n}', 'length and substrings',
    '<code>${#s}</code> is the number of characters. <code>${s:off:len}</code> takes len characters from position off (from 0). A negative offset counts from the end but needs a space or brackets: <code>${s: -3}</code>, otherwise <code>:-</code> is the default operator.',
    '${#s}   ·   ${s:2:4}   ·   ${s: -4}', 'safe',
    [('${#s}', 'length', 'validation'),
     ('${s:3}', 'from 3 to end', 'skip prefix'),
     ('${s:0:3}', 'first 3', 'codes'),
     ('${s: -3}', 'last 3', 'suffix'),
     ('${s:(-3):2}', '2 chars from 3rd last', 'with brackets'),
     ('${s:i:1}', 'one char', 'loops')],
    dict(cmd="d=20261111; echo \"year=${d:0:4} month=${d:4:2} day=${d: -2}\"\npan=ABCDE1234F; echo \"${#pan} chars, last 4: ${pan: -4}\"\nmasked=\"XXXXXX${pan: -4}\"; echo \"$masked\"", note='Fixed positions turned a date into parts and masked an ID.'),
    [('qa', [
        dict(situation='Validate a PIN code length.', cmd="for p in 411001 4110 4110012; do (( ${#p} == 6 )) && echo \"$p ok\" || echo \"$p must be 6 digits (has ${#p})\"; done", why='${#p} inside (( )).')]),
     ('dev', [
        dict(situation='The :- trap.', cmd="s=abcdef; echo \"[${s:-3}] [${s: -3}] [${s:(-3)}]\"", why='Without the space, :-3 is “default 3”, so the whole string comes back.')]),
    ]
) + cmdcard_u(['extensions, folder and file names, emails, URLs, versions'],
               ['complex patterns (use [[ =~ ]] or sed)'])(
    'trim', '${s#p} · ${s##p} · ${s%p} · ${s%%p}', 'removing prefixes and suffixes',
    '<code>#</code> removes a matching prefix, <code>%</code> a matching suffix; one sign removes the shortest match, two the longest. The pattern is a glob. These replace basename, dirname and many cut/sed calls.',
    '${f%.*}   ·   ${f##*.}   ·   ${p##*/}   ·   ${p%/*}', 'safe',
    [('${f%.*}', 'name without extension', 'rename'),
     ('${f##*.}', 'extension only', 'type checks'),
     ('${p##*/}', 'file name', 'basename'),
     ('${p%/*}', 'folder', 'dirname'),
     ('${e#*@}', 'email domain', 'grouping'),
     ('${v#v}', 'drop a leading v', 'versions'),
     ('${url#*://}', 'drop the scheme', 'URLs')],
    dict(setup=ST, cmd="f=report.final.v2.pdf\necho \"${f%.*} | ${f%%.*} | ${f#*.} | ${f##*.}\"\np=/var/log/nginx/access.log\necho \"file=${p##*/} dir=${p%/*}\"\ne=aman.k@mail.co.in; echo \"user=${e%@*} domain=${e#*@} tld=${e##*.}\"", note='The puzzle: %% took everything after the first dot; one % gives report.final.v2.'),
    [('sys', [
        dict(situation='Split emails without awk.', setup=ST, cmd="cd ~/st; while read -r e; do printf '%-8s %-20s %s\\n' \"${e%@*}\" \"${e#*@}\" \"${e##*.}\"; done < emails.txt", why='User, domain and top-level domain from three different cuts.')]),
     ('data', [
        dict(situation='Version numbers.', cmd="v=v2.14.3; v=${v#v}; major=${v%%.*}; rest=${v#*.}; minor=${rest%%.*}; patch=${v##*.}\necho \"major=$major minor=$minor patch=$patch next=$major.$((minor+1)).0\"", why='Peel off one part at a time.')]),
    ],
    anat=anatomy([('${', 'opt', 'start'), ('f', 'cmd', 'variable'), ('%', 'opt', 'from the end, shortest'), ('.*', 'arg', 'glob pattern'), ('}', 'opt', 'end')], 'Variable, operator, pattern. No $ before the name inside.')
) + cmdcard_u(['clean-up of names, spaces, separators', 'case-insensitive comparisons'],
               ['regex replacements (sed -E)'])(
    'repl', '${s/a/b} · ${s//a/b} · ${s/#a/b} · ${s/%a/b} · ${s^^} ${s,,} ${s^}', 'replacing text and changing case',
    'One slash replaces the first match, two slashes every match; <code>/#</code> and <code>/%</code> anchor to the start or end. An empty replacement deletes. <code>^^</code> makes everything upper case, <code>,,</code> lower, <code>^</code> only the first letter. A pattern like <code>[aeiou]</code> limits which letters change.',
    '${s// /_}   ·   ${s//[0-9]/}   ·   ${s,,}   ·   ${s^}', 'safe',
    [('${s/a/b}', 'first', 'one fix'),
     ('${s//a/b}', 'all', 'spaces → _'),
     ('${s//[0-9]/}', 'delete digits', 'clean'),
     ('${s/#./X}', 'at start', 'prefixes'),
     ('${s^^}', 'UPPER', 'codes'),
     ('${s,,}', 'lower', 'comparisons'),
     ('${s^}', 'Capitalise', 'names')],
    dict(setup=ST, cmd="s='  holiday photo 2026.JPEG'\necho \"[${s// /_}] [${s/ /}]\"\nn='riya SHARMA'; first=${n%% *}; last=${n#* }; echo \"${first^} ${last,,}\" \"| ${last^^}\"\nans=YeS; [[ ${ans,,} == yes ]] && echo 'answer accepted'", note='Lower-casing the answer accepts yes, YES and YeS alike.'),
    [('dev', [
        dict(situation='Rename files to clean names (preview).', setup=ST, cmd="cd ~/st/in; for f in *; do new=${f,,}; new=${new// /_}; new=${new/%.jpeg/.jpg}; if [ \"$f\" != \"$new\" ]; then echo \"mv '$f' -> $new\"; fi; done", why='Lower case, spaces → _, .jpeg → .jpg; echo first, mv later.')]),
     ('sec', [
        dict(situation='Mask secrets in a log line.', cmd="line='login user=riya password=S3cret! token=abc123'\nmasked=${line//password=+([^ ])/password=****}; shopt -s extglob; masked=${line//password=+([^ ])/password=****}; echo \"$masked\"", why='With extglob, +([^ ]) means “one or more non-spaces”.')]),
    ]
) + cmdcard_u(['every report, table, log line, CSV and fixed-width file', 'numbers with padding or decimals'],
               ['echo -e (not portable)'])(
    'printf', "printf FORMAT args… · %s %d %f %x · %-10s %05d %.2f · -v · %q", 'printf',
    'printf prints its arguments using the format. Each <code>%</code> conversion takes the next argument; the format repeats until all are used. A number between % and the letter is the width (<code>-</code> left-aligns, <code>0</code> pads), a dot gives precision. <code>-v var</code> stores the result. printf never adds a newline on its own.',
    "printf '%-10s %6.2f\\n' name 3.5   ·   printf -v id 'EMP%04d' 7", 'safe',
    [('%s %d %f', 'string, integer, float', 'everything'),
     ('%-12s', 'left-aligned column', 'tables'),
     ('%8.2f', 'width 8, 2 decimals', 'money'),
     ('%05d', 'zero pad', 'IDs'),
     ('%x %o', 'hex, octal', 'perms, colours'),
     ('-v var', 'store, do not print', 'build strings'),
     ('%q', 'shell-quote', 'safe commands'),
     ('%(%F %T)T', 'date/time', 'logs')],
    dict(cmd="printf '%-8s %6s %8s\\n' NAME QTY PRICE\nprintf '%-8s %6d %8.2f\\n' pen 12 9.5 notebook 3 45 bag 1 799.999\nprintf -v id 'EMP%04d' 42; echo \"$id\"\nprintf '%s\\n' a b c | paste -sd,", note='The second printf used its format three times for the nine arguments.'),
    [('sys', [
        dict(situation='Number bases and permissions.', cmd="printf 'dec %d = hex %x = oct %o\\n' 255 255 255\nprintf '%o\\n' $((8#644))\nprintf '#%02x%02x%02x\\n' 255 128 0", why='Hex for colours and memory, octal for chmod.')]),
     ('dev', [
        dict(situation='The puzzle, printf parts.', cmd="printf '%s\\n' a b c\nprintf '%d items\\n' 3.5\nprintf '%.0f items\\n' 3.5\nprintf '%(%Y-%m-%d)T log start\\n' -1 | sed 's/[0-9-]*/DATE/'", expect='any', why='Reused format; %d reports “invalid number” for 3.5 (then prints only the 3, and the exit status is 1); %.0f rounds to 4; -1 means now.')]),
    ]
) + undo('Parameter expansion never changes the variable unless you assign it (or use :=).', [
    ('Unexpected result:', 'print each step with <code>declare -p</code> or <code>echo "[$s]"</code>.'),
    ('Renamed files wrongly:', 'always <code>echo mv</code> first; keep a list (Lesson 3.5).'),
    ('Case operators fail on macOS:', 'use <code>tr</code> or install bash 5.'),
    ('printf output mixed up:', 'count % conversions against arguments.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="printf '%d\\n' abc", meaning='%d needs a number.', fix='Use %s, or check input.'),
    dict(cmd='s=abc; echo ${s:0:-5}', meaning='A negative length that goes past the start.', fix='Check ${#s} first.'),
    dict(cmd='echo ${ s}', meaning='Space after { is not allowed.', fix='${s}.'),
    dict(cmd='unset s; echo ${s:?is required}', meaning=':? stops on empty or unset.', fix='Set the variable, or use :-.'),
]) + qc('Which printf conversion pads 7 to <code>007</code>?', '%03d.') + '''
'''
cards = cards + '</section>\n'

def cut(k):
    word = 'report.final.v2.pdf'
    res = [word, 'final.v2.pdf', 'pdf', 'report.final.v2', 'report'][k]
    opn = ['f', '${f#*.}', '${f##*.}', '${f%.*}', '${f%%.*}'][k]
    o = label_box(10, 30, 340, 36, [word], 'card', 9.6)
    o += label_box(10, 90, 340, 36, [res], ['card', 'blue', 'blue', 'green', 'green'][k], 9.6)
    o += t(180, 150, opn, 10, 'acc', bold=True)
    return o
see_cmds = [['$ f=report.final.v2.pdf'], ['$ echo ${f#*.}', ('final.v2.pdf', 'out')], ['$ echo ${f##*.}', ('pdf', 'out')], ['$ echo ${f%.*}', ('report.final.v2', 'out')], ['$ echo ${f%%.*}', ('report', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/st', prompt='riya@web01:~/st$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['A name with three dots.', '# shortest prefix.', '## longest prefix.', '% shortest suffix.', '%% longest suffix.'])]
behind = [cut(k) + t(180, 186, n, 8.4, 'violet', bold=True) for k, n in enumerate(['The original.', 'Up to the first dot removed.', 'Up to the last dot removed.', 'From the last dot removed.', 'From the first dot removed.'])]
two = anim_two('Four cuts of one name', 'Behind the screen: which part each form removes',
               'A terminal applying # ## % %% to report.final.v2.pdf.',
               'The name report.final.v2.pdf and the result of each cut below it.', see, behind,
               ['Name.', '#', '##', '%', '%%'],
               ['name', '#', '##', '%', '%%'])

def table_frame(k):
    rows = [('NAME', 'QTY', 'PRICE'), ('pen', '12', '9.50'), ('notebook', '3', '45.00'), ('bag', '1', '800.00')]
    o = ''
    for i in range(min(k + 1, 4)):
        for j, (x, w, a) in enumerate(zip(rows[i], [120, 70, 90], ['start', 'end', 'end'])):
            xs = [30, 210, 310][j]
            o += t(xs, 40 + i * 26, rows[i][j], 9.6, 'acc' if i == 0 else 'ink2', anchor=a, bold=(i == 0))
    o += t(180, 160, ["%-8s %6s %8s", "%-8s %6d %8.2f", 'format reused', 'perfect columns'][k], 9, 'violet', bold=True)
    return o
frames = [table_frame(k) for k in range(4)]
s1 = anim_one('Animated example', 'printf builds a table',
              'Widths keep every column lined up.',
              "printf '%-8s %6d %8.2f\\n' …", 'A table drawn line by line: header, then rows with left-aligned names and right-aligned numbers.', frames,
              ['Header.', 'Row 1.', 'Row 2.', 'Row 3.'], hid='scenario-printf')

dx = dissect('Layer by layer: what bash does with ${…}',
    'Each layer has a real command and output from our build machine.', [
    dict(key='glob', name='Patterns are globs', sub='not regex', why='Same as ls.', how='* ? [ ].', impl='fnmatch.', used='#, %, /.',
         cmd="f=data_2026_v3.csv; echo \"${f%_v[0-9]*} | ${f//[0-9]/#}\""),
    dict(key='loc', name='Characters vs bytes', sub='locale', why='UTF-8.', how='LC_ALL.', impl='mbstowcs.', used='${#s}.',
         cmd="s='café'; echo \"utf8: ${#s}\"; LC_ALL=C bash -c 's=café; echo \"C: ${#s}\"'"),
    dict(key='speed', name='No new process', sub='built-in', why='Speed.', how='Inside bash.', impl='No fork.', used='Loops.',
         cmd="p=/a/b/c.txt; s=$(date +%s%N); for i in $(seq 300); do b=$(basename $p); done; m=$(date +%s%N); for i in $(seq 300); do b=${p##*/}; done; e=$(date +%s%N); a=$(( (m-s)/1000000 )); c=$(( (e-m)/1000000 )); echo \"300 x basename: about ${a}ms; 300 x \\${p##*/}: about ${c}ms\"; (( a > 10*c )) && echo 'parameter expansion was more than 10 times faster'"),
    dict(key='q', name='printf %q', sub='safe quoting', why='Re-use as input.', how='Escapes.', impl='Built-in.', used='Generated commands.',
         cmd="f=\"it's a file.txt\"; printf '%q\\n' \"$f\"; printf 'rm -- %q\\n' \"$f\""),
], hint='From patterns to quoting. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Four cuts of one name, and a printf table</h2>
''' + two + s1 + dx + qc('Why is <code>${#s}</code> 4 for café in UTF-8 but 5 with LC_ALL=C?', 'é is one character but two bytes; the C locale counts bytes.') + '''
</section>
'''

VAR = variations('Eighteen more string and printf experiments. All were really run on our build machine.', [
    ('Cutting and trimming', [
        dict(title='Trim spaces from both ends', cmd="s='   padded text   '; shopt -s extglob; s=${s##+([[:space:]])}; s=${s%%+([[:space:]])}; echo \"[$s]\"", why='extglob +( ) for one or more spaces.'),
        dict(title='Trim with read (no extglob)', cmd="read -r s <<< '   padded text   '; echo \"[$s]\"", why='read strips leading and trailing IFS whitespace.'),
        dict(title='Change every extension in a loop', setup=ST, cmd="cd ~/st/in; for f in *.JPG; do echo \"$f -> ${f%.JPG}.jpg\"; done", why='% suffix then a new one.'),
        dict(title='Path parts', cmd="p=/home/riya/projects/app/src/main.py; echo \"name=${p##*/} stem=$(x=${p##*/}; echo ${x%.*}) dir=${p%/*} top=${p#/*/}\"", why='Combine # and % to get any part.'),
        dict(title='First and rest of a list', cmd="list='web01,web02,db01'; echo \"first=${list%%,*} rest=${list#*,} last=${list##*,}\"", why='Split CSV text without IFS.'),
        dict(title='URL pieces', cmd="u='https://myphatshala.in/courses/linux/?page=2'; noscheme=${u#*://}; echo \"host=${noscheme%%/*} path=/${noscheme#*/} query=${u#*\\?}\"", why='Escape ? in the pattern with \\.'),
    ]),
    ('Replacing and case', [
        dict(title='Remove all digits / keep only digits', cmd="s='Order #A-2041 on 11/11'; echo \"${s//[0-9]/} | ${s//[^0-9]/}\"", why='Bracket classes like glob.'),
        dict(title='Title Case each word', cmd="s='linux shell programming'; out=; for w in $s; do out+=\"${w^} \"; done; echo \"${out% }\"", why='^ on each word, then drop the trailing space.'),
        dict(title='Swap case', cmd="s='Hello World'; echo \"${s~~}\"", why='~~ toggles every letter.'),
        dict(title='Upper only vowels', cmd="s=education; echo \"${s^^[aeiou]}\"", why='A pattern limits which letters change.'),
        dict(title='Count a character', cmd="s='a,b,,c,d'; only=${s//[^,]/}; echo \"${#only} commas\"", why='Delete everything else, then measure.'),
        dict(title='Defaults for config', cmd="unset PORT HOST; : \"${HOST:=localhost}\"; echo \"$HOST:${PORT:-8080} debug=${DEBUG:+on}\"", why=':= assigns, :- only substitutes, :+ shows only if set.'),
    ]),
    ('printf', [
        dict(title='A report table with a total', cmd="printf '%-10s %8s\\n' ITEM AMOUNT; t=0; for r in rent:12000 food:5400.5 net:799; do printf '%-10s %8.2f\\n' \"${r%%:*}\" \"${r#*:}\"; done; printf '%-10s %8.2f\\n' TOTAL $(echo '12000+5400.5+799' | bc)", why='Columns line up for any value.'),
        dict(title='Repeat a character', cmd="printf -v line '%*s' 30 ''; echo \"${line// /-}\"", why='%*s takes the width from an argument; then spaces become dashes.'),
        dict(title='Progress lines', cmd="for p in 0 25 50 100; do printf '[%-10s] %3d%%\\n' \"$(printf '%*s' $((p/10)) '' | tr ' ' '#')\" $p; done", why='%% prints a literal percent sign.'),
        dict(title='Zero-padded file names', cmd="for i in 1 2 10; do printf -v f 'scan_%03d.png' $i; echo \"$f\"; done", why='-v stores into f; padding keeps sort order.'),
        dict(title='Characters and codes', cmd="printf '%d %d\\n' \"'A\" \"'a\"; printf \"\\\\$(printf '%03o' 66)\\n\"", why="A leading ' gives the character code; an octal escape turns a code back into a character."),
        dict(title='Log line with a timestamp', cmd="printf '%(%F %T)T [%-5s] %s\\n' -1 INFO 'service started' -1 WARN 'disk 81%' | sed 's/^[0-9-]* [0-9:]*/TIME/'", why='%(…)T is a bash date format; -1 means now.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Strings and printf at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['${f%.*}', 'files'], 'blue', 8.6), '1. Batch file conversion',
              'for f in *.png; do convert "$f" "${f%.png}.webp"; done — the standard pattern for media and documents.', ['Files', '*${f%.*}', 'new names']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['${e#*@}', 'data'], 'green', 8.6), '2. Cleaning data',
    'Domains from emails, digits from phone numbers, trimmed names before loading into a database.', ['Raw', '*${…}', 'clean']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['printf', 'reports'], 'amber', 8.6), '3. Reports and fixed-width files',
    'Banks and government systems still exchange fixed-width records; printf %-20s %010d builds them exactly.', ['Values', '*printf', 'record']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['v2.14.3', 'releases'], 'violet', 8.6), '4. Release scripts',
    'Split a version tag, bump the minor number, write the new tag.', ['Tag', '*# %', 'next tag']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['${x,,}', 'input'], 'red', 8.6), '5. User input',
    'Accept Yes/YES/y with ${ans,,}; validate lengths with ${#x}.', ['Answer', '*case', 'decision']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Length of your user name', scenario='Quick check.', cmd="echo \"${#USER}\"", explain='riya = 4.'),
    dict(level='b', title='Shout a message', scenario='Banner text.', cmd="m='deploy done'; echo \"${m^^}!\"", explain='^^.'),
    dict(level='i', title='Basename of every file in a list', scenario='No basename process.', cmd="for p in /etc/hosts /var/log/syslog /usr/bin/bash; do echo \"${p##*/}\"; done", explain='##*/.'),
    dict(level='i', title='Aligned key=value', scenario='Readable config dump.', cmd="for kv in host=db01 port=5432 timeout=30; do printf '%-8s : %s\\n' \"${kv%%=*}\" \"${kv#*=}\"; done", explain='Split at = and print in columns.'),
    dict(level='a', title='Safe command from untrusted name', scenario='Generated scripts.', cmd="f='a b; rm -rf ~'; printf 'cp -- %q /backup/\\n' \"$f\"", explain='%q quotes everything dangerous.'),
], extra=build_up('a photo renamer', 'Riya builds new names for photos step by step, previewing with echo.', ST, [
    ("cd ~/st/in; for f in *; do echo \"$f\"; done", '1. List the names.'),
    ("cd ~/st/in; for f in *; do ext=${f##*.}; echo \"$f  [ext=${ext,,}]\"; done", '2. The extension, lower case.'),
    ("cd ~/st/in; n=0; for f in *.[Jj][Pp]*; do ((n++)); ext=${f##*.}; ext=${ext,,}; printf -v new 'trip_%03d.%s' $n \"${ext/jpeg/jpg}\"; echo \"$f -> $new\"; done", '3. A numbered name, .jpeg → .jpg.'),
    ("cd ~/st/in; n=0; for f in *.[Jj][Pp]*; do ((n++)); ext=${f##*.}; ext=${ext,,}; printf -v new 'trip_%03d.%s' $n \"${ext/jpeg/jpg}\"; mv -- \"$f\" \"$new\"; done; ls", '4. Rename for real.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Simple cuts in a loop', '${…}', 'No process.', '$(basename) per file.'),
    ('Regex', '[[ $s =~ re ]] or sed -E', 'Real regex.', 'Globs for regex jobs.'),
    ('Columns of a big file', 'awk / cut', 'Fast on files.', 'bash loops over 1M lines.'),
    ('Formatted output', 'printf', 'Exact.', 'echo with spaces by hand.'),
    ('Case change on old bash', 'tr a-z A-Z', 'Portable.', '^^ on macOS bash 3.2.'),
]) + keys('Handy forms.', [
    ('${f%.*}', 'no extension', 'rename'),
    ('${f##*.}', 'extension', 'type'),
    ('${p##*/}', 'basename', 'paths'),
    ('${s//a/b}', 'replace all', 'clean'),
    ('${s,,}', 'lower', 'compare'),
    ("printf '%-10s|'", 'column', 'tables'),
]) + scriptit('fileinfo.sh', 'For each path given (or a default list), print a table with the folder, name, extension, length of the name and a cleaned name (lower case, spaces → _), using only parameter expansion and printf.',
'''[ $# -eq 0 ] && set -- '/home/riya/Photos/Holiday Photo.JPEG' /etc/nginx/nginx.conf /var/log/syslog
printf '%-20s %-18s %-6s %4s  %s\\n' FOLDER NAME EXT LEN CLEAN
for p in "$@"; do
  name=${p##*/}; dir=${p%/*}
  [[ $name == *.* ]] && ext=${name##*.} || ext=-
  clean=${name,,}; clean=${clean// /_}
  printf '%-20s %-18s %-6s %4d  %s\\n' "$dir" "$name" "${ext,,}" "${#name}" "$clean"
done''',
'<p>Run without arguments, so it uses three sample paths.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>%%</code> removes the <i>longest</i> suffix matching <code>.*</code>, which starts at the first dot; one <code>%</code> removes the shortest, from the last dot: <code>report.final.v2</code>. <b>2.</b> <code>%d</code> accepts only integers; use <code>%.0f</code> or <code>%s</code>. <b>3.</b> printf reuses its format until every argument is used, so one <code>%s\\n</code> and three arguments give three lines (a feature, used for lists). <b>4.</b> macOS ships bash 3.2, and <code>^^</code> needs bash 4: install a newer bash or use <code>tr a-z A-Z</code>.') + qc('Which form gives the folder part of a path?', '${p%/*}.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/st', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-shell-variables-and-environment-variables-env/">Lesson 12.1</a> (variables), <a href="../11-metacharacters-expansion-and-directory-stacks/">Lesson 12.11</a> (expansion) and <a href="../13-arrays-indexed-and-associative/">Lesson 12.13</a> (arrays).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
