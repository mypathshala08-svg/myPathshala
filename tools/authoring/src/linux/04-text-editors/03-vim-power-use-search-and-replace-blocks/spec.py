import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

V = "vim -u NONE -N -i NONE -es"

META = dict(
    module='04-text-editors', lesson='03-vim-power-use-search-and-replace-blocks', n='4.3',
    module_label='Module 4 · Text editors: nano and vim',
    title='vim power use: search and replace, blocks, registers and .vimrc',
    desc='vim beyond the basics: :s and :%s with ranges and the g, c and i flags, groups and \\v; :g and :v on matching lines; visual, line and block mode (Ctrl+V insert and append, indent, case); the dot command, macros (qa … q, @a), registers and text objects (ciw, ci", dap); :sort, :r !cmd and :%!filter; splits, buffers and vimdiff; and a practical ~/.vimrc. Every result verified by typing the keys into a real vim, with real vimdiff screens.',
    og_desc='40 replacements and 20 comments in seconds: :%s/old/new/gc, :g, Ctrl+V blocks, macros, registers, vimdiff and .vimrc, all verified in real vim.',
    minutes=40, level='Intermediate → Advanced',
    lead='A config needs 40 confirmed replacements and a block of lines commented out. This lesson teaches vim’s power tools: substitution, global commands, visual blocks, repeats, macros, registers, splits, vimdiff, shell filters and .vimrc, with every result verified in a real vim.',
    chips=['Keys verified in real vim', 'Real vimdiff screens', 'Tools by field', 'Practice lab with checker'],
)

MAIN = f"""# vim's ex commands in batch mode: the same commands you type after ':'
printf 'db=localhost\\nweb=localhost\\n# old setting\\ncache=localhost\\n' > hosts.conf
{V} -c '%s/localhost/db.internal/g' -c 'wq' hosts.conf
cat hosts.conf
{V} -c 'g/^#/d' -c 'wq' hosts.conf
cat hosts.conf
"""

RUN = dict(
    heading='Replace and delete by pattern',
    intro='<p>The browser runner has no full-screen terminal, so this uses vim’s batch mode: <code>:%s</code> replaces everywhere, <code>:g/^#/d</code> deletes comment lines. Try the interactive keys (<code>gc</code>, Ctrl+V, macros) on your PC.</p>',
    code=MAIN,
    anno=[
        (f"{V} -c '%s/localhost/db.internal/g' -c 'wq' hosts.conf", 'Replace every localhost.'),
        (f"{V} -c 'g/^#/d' -c 'wq' hosts.conf", 'Delete every line starting with #.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How many lines are left?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> no g flag. Which x remain? Then run.',
             code=f"printf 'x,x\\nx,x\\n' > f.txt\n{V} -c '%s/x/y/' -c 'wq' f.txt\ncat f.txt\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the slashes in the path break the command. Use # as the separator.',
             code=f"printf 'log=/var/log/app\\n' > f.txt\n{V} -c '%s//var/log//data/log/' -c 'wq' f.txt\ncat f.txt\n", expect='any'),
        dict(label='4 · Your turn', hint='Keep only the lines containing ERROR.',
             code=f"printf 'INFO a\\nERROR b\\nINFO c\\nERROR d\\n' > l.log\n{V} -c 'v/ERROR/d' -c 'wq' l.log\ncat l.log\n"),
        dict(label='5 · Challenge', hint='Swap “key=value” into “value=key” on every line with groups.',
             code=f"printf 'port=80\\nhost=db\\n' > f.txt\n{V} -c '%s/\\\\v(\\\\w+)\\\\=(\\\\w+)/\\\\2=\\\\1/' -c 'wq' f.txt\ncat f.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the interactive power keys',
    intro='<p>These need a keyboard. Screens are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Confirm each replacement', cmd=':%s/localhost/db.internal/gc', output='db=localhost\nreplace with db.internal (y/n/a/q/l/^E/^Y)?', note='Typical. y yes, n no, a all remaining, q quit, l this one and stop.'),
        dict(title='2 · Record and play a macro', cmd='qa A; Esc j q   then  10@a', output='(the bottom line shows “recording @a” while recording)', note='Typical. Always end the macro on the next line (j) so it can repeat.'),
        dict(title='3 · Compare two configs', cmd='vimdiff /etc/nginx/nginx.conf nginx.conf.new', output='(two windows; differences highlighted; ]c next, [c previous, do / dp get / put a change, :qa quit)', note='Typical.'),
        dict(title='4 · Does your vim have the system clipboard?', cmd="vim --version | grep -o '[+-]clipboard'", output=pc("vim --version | grep -o '[+-]clipboard'"), note='Recorded on our build machine: -clipboard means "+y will not reach other programs; install vim-gtk3 on a desktop if you need it.'),
    ],
)

TRACE = dict(
    heading='Batch power edits step by step',
    intro='<p>Each line runs one ex command. Watch the size of the file in the <b>Files</b> box.</p>',
    code=f'''printf 'a=1\\n# x\\nb=2\\n# y\\nc=3\\n' > app.conf
{V} -c 'g/^#/d' -c 'wq' app.conf
{V} -c '%s/=/ = /' -c 'wq' app.conf
{V} -c 'sort' -c 'wq' app.conf
cat app.conf
''',
    notes={2: ':g/^#/d :: Two comment lines removed.', 3: ':%s :: Spaces around every =.', 4: ':sort :: Lines in order.'},
)

WORKED_INTRO = 'Three tasks from real jobs, shown as the interactive keys and verified with vim’s batch mode.'
EXAMPLES = [
    dict(level='b', tag='Operations', title='Migrate a host name in one section only',
         problem='<p>Change localhost to db.internal only in lines 2–3 (keys: <code>:2,3s/localhost/db.internal/g</code>).</p>',
         inp='hosts.conf with 3 localhost lines',
         approach=['A range limits the change.', 'Line 1 must stay.'],
         code=f'''printf 'admin=localhost\\ndb=localhost\\ncache=localhost\\n' > hosts.conf
{V} -c '2,3s/localhost/db.internal/g' -c 'wq' hosts.conf
cat hosts.conf
''',
         notes={2: 'Range :: 2,3 = only those lines.'},
         tryit='Use a pattern range instead: :/^db/,$s/…/…/'),
    dict(level='i', tag='Data', title='Reformat dates with groups',
         problem='<p>Dates are DD/MM/YYYY; make them YYYY-MM-DD (keys: <code>:%s/\\v(\\d{2})\\/(\\d{2})\\/(\\d{4})/\\3-\\2-\\1/g</code>).</p>',
         inp='06/11/2026,1200',
         approach=['\\v very magic for readable groups.', 'Reorder with \\3-\\2-\\1.'],
         code=f'''printf '06/11/2026,1200\\n31/10/2026,950\\n' > sales.csv
{V} -c '%s/\\v(\\d{{2}})\\/(\\d{{2}})\\/(\\d{{4}})/\\3-\\2-\\1/g' -c 'wq' sales.csv
cat sales.csv
''',
         notes={2: 'Groups :: Three groups, written back in a new order.'},
         tryit='Do the same with sed -E (Lesson 6.4).'),
    dict(level='a', tag='Security', title='Collect all denied lines at the end of a log copy',
         problem='<p>In a copy of an auth log, copy every “Failed” line to the end for a quick report (keys: <code>:g/Failed/t$</code>).</p>',
         inp='auth.log copy',
         approach=[':g runs t$ (copy to end) on each matching line.'],
         code=f'''printf 'Accepted riya\\nFailed root\\nAccepted kabir\\nFailed admin\\n' > auth.log
{V} -c 'g/Failed/t$' -c 'wq' auth.log
cat auth.log
''',
         notes={2: ':g + t$ :: Each Failed line copied below the last line.'},
         tryit='Use m0 instead of t$ to move them to the top.'),
]

QUIZ = mix([
    dict(q='What does % mean in :%s/a/b/g?', options=['percent sign', 'all lines', 'current line', 'regex'], answer=1,
         why='% = 1,$ = every line.'),
    dict(q='Which flag asks before each replacement?', options=['g', 'c', 'i', 'e'], answer=1,
         why='c = confirm.'),
    dict(q=':g/^#/d does what?', options=['Deletes the first #', 'Deletes every line starting with #', 'Comments every line', 'Nothing'], answer=1,
         why=':g runs d on every matching line.'),
    dict(q='How do you insert "# " at the start of 5 lines at once?', options=['5I# ', 'Ctrl+V 4j I# Esc', ':5i #', 'V5># '], answer=1,
         why='Visual block insert.'),
    dict(q='What does the . key do?', options=['Ends the file', 'Repeats the last change', 'Shows the cursor', 'Saves'], answer=1,
         why='The dot repeats the last change.'),
    dict(q='How do you record a macro in register a?', options=['ma … m', 'qa … q', '@a … @', '"a … "'], answer=1,
         why='qa starts, q stops; @a plays.'),
    dict(q='ci" does what?', options=['Copies inside quotes', 'Changes the text inside quotes', 'Deletes the quotes', 'Inserts quotes'], answer=1,
         why='c (change) + i" (inside quotes).'),
    dict(q='How do you compare two files side by side in vim?', options=['vim -d or vimdiff a b', 'vim --compare', ':diff a b only', 'vimcmp'], answer=0,
         why='vimdiff a b (same as vim -d a b).'),
])

REVISION = [
    '<code>:[range]s/pat/rep/[gci]</code>: % all, 10,20, .,$; g all matches, c confirm, i ignore case.',
    'Groups <code>\\( \\)</code> → <code>\\1</code>; <code>\\v</code> very magic; other separators: <code>:%s#/a#/b#</code>.',
    '<code>:g/re/d</code> delete matching, <code>:v/re/d</code> keep matching; <code>:g/re/t$</code>, <code>m0</code>, <code>s///</code>.',
    'Visual: <code>v V Ctrl+V</code>; block <code>I…Esc</code> / <code>$A…Esc</code>; <code>&gt; &lt; ~ U u</code>.',
    '<code>.</code> repeat; macros <code>qa…q</code>, <code>@a</code>, <code>10@a</code>; registers <code>"ayy "ap "0p</code>, <code>:reg</code>.',
    'Text objects: <code>ciw ci" dap yi(</code>.',
    'Shell: <code>:sort</code>, <code>:r !cmd</code>, <code>:%!cmd</code>, <code>:!cmd</code>.',
    'Windows: <code>:sp :vsp</code>, <code>Ctrl+W w</code>, <code>vimdiff a b</code> (<code>]c</code>, <code>:qa</code>); settings in <code>~/.vimrc</code>.',
]

FAQ = [
    ('How do I search and replace in vim?', ':%s/old/new/g for the whole file; add c to confirm each change.'),
    ('How do I delete all lines containing a word?', ':g/word/d (and :v/word/d to keep only those lines).'),
    ('How do I comment out multiple lines in vim?', 'Ctrl+V, move down to select the first column, I, type # , Esc.'),
    ('What are vim macros?', 'Recorded key sequences: qa to start recording into register a, q to stop, @a to replay.'),
    ('How do I compare two files in vim?', 'vimdiff file1 file2 (or vim -d); ]c and [c jump between differences.'),
    ('Where are vim settings stored?', 'In ~/.vimrc (on Ubuntu, defaults.vim is used if you have none).'),
    ('How do I paste without auto-indent messing it up?', 'Use :set paste before pasting (or modern vim’s bracketed paste, often automatic).'),
]

PRACTICE_INTRO = 'Power-edit tasks you can check in the browser with batch mode; on your PC use the interactive keys.'
PROBLEMS = [
    dict(level='easy', title='Replace everywhere', stmt='Change every “dev” to “prod”.', inp='env=dev, url=dev.shop',
         code=f"printf 'env=dev\\nurl=dev.shop\\n' > f.conf\n{V} -c '%s/dev/prod/g' -c 'wq' f.conf\ncat f.conf\n", explain=':%s with g.'),
    dict(level='easy', title='Delete comments', stmt='Delete all lines starting with #.', inp='3 lines, 1 comment',
         code=f"printf 'a\\n# b\\nc\\n' > f.conf\n{V} -c 'g/^#/d' -c 'wq' f.conf\ncat f.conf\n", explain=':g/^#/d.'),
    dict(level='easy', title='Sort a list', stmt='Sort the lines.', inp='pear apple fig',
         code=f"printf 'pear\\napple\\nfig\\n' > l.txt\n{V} -c 'sort' -c 'wq' l.txt\ncat l.txt\n", explain=':sort.'),
    dict(level='medium', title='Only some lines', stmt='Replace 80 with 8080 only on lines 2–3.', inp='3 lines with 80',
         code=f"printf 'a=80\\nb=80\\nc=80\\n' > f.conf\n{V} -c '2,3s/80/8080/' -c 'wq' f.conf\ncat f.conf\n", explain='A range.'),
    dict(level='medium', title='Comment a block', stmt='Prefix every line with "# " (like Ctrl+V I# Esc).', inp='x y z',
         code=f"printf 'x\\ny\\nz\\n' > f.txt\n{V} -c '%s/^/# /' -c 'wq' f.txt\ncat f.txt\n", explain='^ = line start.'),
    dict(level='medium', title='Unique sort', stmt='Sort and remove duplicates.', inp='b a b c a',
         code=f"printf 'b\\na\\nb\\nc\\na\\n' > l.txt\n{V} -c 'sort u' -c 'wq' l.txt\ncat l.txt\n", explain=':sort u.'),
    dict(level='business', title='Path with slashes', stmt='Change /var/log to /data/log using # as separator.', inp='log=/var/log/app',
         code=f"printf 'log=/var/log/app\\n' > f.conf\n{V} -c '%s#/var/log#/data/log#' -c 'wq' f.conf\ncat f.conf\n", explain='Any separator works.'),
    dict(level='business', title='Keep only errors', stmt='Keep only lines with ERROR in a log copy.', inp='INFO/ERROR mix',
         code=f"printf 'INFO 1\\nERROR 2\\nERROR 3\\nINFO 4\\n' > a.log\n{V} -c 'v/ERROR/d' -c 'wq' a.log\ncat a.log\n", explain=':v deletes non-matching lines.'),
]

SCN_INTRO = 'Interview questions about advanced vim use.'
SCENARIOS = (
    scn('Any company', 'Fresher', '“Replace a word in the whole file.”',
        'Asked in many Linux rounds after “how do you exit vi”.',
        'do you know :%s?',
        '''<ul>
          <li><code>:%s/old/new/g</code>; with confirmation <code>gc</code>.</li>
          <li>One line: <code>:s/old/new/g</code>; a range: <code>:10,20s/…</code>.</li>
          <li>Undo the whole substitution with u.</li>
        </ul>''', 'replacing by hand line by line.') +
    scn('Operations', 'Mid-level', 'Two servers behave differently',
        'App works on server A, not on B. Same version, different configs?',
        'can you compare efficiently?',
        '''<ol>
          <li>Copy B’s config next to A’s (scp), strip comments (<code>:g/^#/d</code> or grep -v).</li>
          <li><code>vimdiff a.conf b.conf</code>, <code>]c</code> through the differences.</li>
          <li>Or <code>diff -u</code> for a text report (Lesson 6.3).</li>
        </ol>''', 'reading both files top to bottom by eye.') +
    scn('Developer tooling', 'Senior', 'Large, irregular edit',
        'You must convert 300 lines of a legacy format where each record needs several different changes.',
        'do you choose the right tool?',
        '''<ul>
          <li>If one regex fits: <code>:%s</code> with groups, tested on a copy.</li>
          <li>If not: record a macro on the first record, ending on the next one, then <code>299@a</code>; check a few results.</li>
          <li>For repeatable jobs: a script (sed/awk/Python) under version control.</li>
        </ul>''', 'a one-off macro for a job that runs every week.')
) + interview([
    ('Search and replace in the whole file with confirmation?', ':%s/old/new/gc'),
    ('Delete all blank lines?', ':g/^$/d'),
    ('Comment out lines 10–20?', ':10,20s/^/# / (or Ctrl+V block insert).'),
    ('What is a macro and how do you use it?', 'Recorded keys: qa … q to record, @a to play, 10@a to repeat.'),
    ('Copy into a named register and paste?', '"ayy then "ap.'),
    ('Compare two files in vim?', 'vimdiff a b; ]c next difference; :qa quit.'),
    ('Make settings permanent?', 'Put them in ~/.vimrc.'),
], [
    ('RHCSA (EX200)', '“Create and edit text files”; fast vim editing saves time in every task.'),
    ('LFCS', 'Essential Commands: edit files, search and replace text.'),
    ('CompTIA Linux+', 'vi/vim commands including search and replace.'),
]) + distro('Most power features need full vim, not vim.tiny or busybox vi.', [
    ('Visual block, macros, registers', 'vim: yes; vim.tiny: limited', 'vim-enhanced: yes; vi (minimal): limited', 'yes', 'WSL: install vim; Git Bash: yes'),
    ('vimdiff', 'with vim package', 'vim-enhanced', 'yes', 'yes'),
    ('System clipboard "+', 'vim-gtk3', 'vim-X11', 'macvim / vim via brew', 'WSL: via win32yank or clip.exe'),
    ('defaults.vim without .vimrc', 'yes', 'yes', 'yes', 'yes'),
]) + teaser('5.1', 'When Riya runs <code>ls notes.txt missing.txt</code>, one line is the answer and the other is an error. Both appear on the screen, yet only one goes into a file when she adds <code>&gt; out.txt</code>. Why?')

CHEATSHEET = cheatsheet('vim power use', [
    ('Substitute', [(':%s/a/b/g', 'all lines'), (':%s/a/b/gc', 'confirm'), (':10,20s/a/b/', 'range'), (':%s#/x#/y#g', 'other separator'), (':s/\\(a\\)\\(b\\)/\\2\\1/', 'groups')]),
    ('Global', [(':g/re/d', 'delete matching'), (':v/re/d', 'keep matching'), (':g/^$/d', 'blank lines'), (':g/re/t$', 'copy to end'), (':g/re/s/a/b/', 'targeted :s')]),
    ('Visual', [('v V Ctrl+V', 'char / line / block'), ('Ctrl+V…I# Esc', 'comment block'), ('Ctrl+V…$A; Esc', 'append block'), ('> < ', 'indent'), ('~ U u', 'case')]),
    ('Repeat · registers', [('.', 'repeat change'), ('qa … q', 'record'), ('@a 10@a @@', 'play'), ('"ayy "ap', 'register a'), ('"0p  :reg', 'last yank, list')]),
    ('Objects · shell · windows', [('ciw ci" dap', 'text objects'), (':sort u', 'sort unique'), (':r !cmd  :%!cmd', 'insert / filter'), (':sp :vsp Ctrl+W w', 'splits'), ('vimdiff a b  ]c', 'compare')]),
])

MINDMAP = mindmap('vim power use', [
    (':s', 'blue', ['% all, 10,20 range', 'g c i flags', 'groups \\1, \\v']),
    (':g / :v', 'green', ['g/re/d', 'v/re/d keep', 't$ m0 s///']),
    ('Visual', 'violet', ['v V Ctrl+V', 'I / A on a block', '> < ~ U']),
    ('Repeat', 'amber', ['. dot', 'qa…q @a', '"a registers']),
    ('Shell', 'red', [':sort', ':r !cmd', ':%!filter']),
    ('Setup', 'acc', ['splits, vimdiff', '~/.vimrc', 'set number …']),
])

LAB = lab('migrate a config with vim', 'Build the lab, open the file in vim on your PC and use this lesson’s commands (or batch mode), then run the checker.',
    setup='''mkdir -p ~/lab43 && cd ~/lab43 && rm -f app.conf
printf '# legacy settings\\ndb=localhost\\nweb=localhost\\n# old\\ncache=localhost\\nmode=dev\\n' > app.conf''',
    tasks=['Replace every <code>localhost</code> with <code>db.internal</code> (<code>:%s/localhost/db.internal/g</code>).',
           'Delete every comment line (<code>:g/^#/d</code>).',
           'Change <code>mode=dev</code> to <code>mode=prod</code>.',
           'Sort the remaining lines (<code>:sort</code>).'],
    solution=f'''{V} -c '%s/localhost/db.internal/g' -c 'g/^#/d' -c '%s/^mode=dev$/mode=prod/' -c 'sort' -c 'wq' app.conf''',
    check='''cd ~/lab43
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 no localhost"   '! grep -q localhost app.conf && [ "$(grep -c db.internal app.conf)" -eq 3 ]'
ok "2 no comments"    '! grep -q "^#" app.conf'
ok "3 mode=prod"      'grep -qx "mode=prod" app.conf'
ok "4 sorted"         'sort -c app.conf 2>/dev/null' ''')
