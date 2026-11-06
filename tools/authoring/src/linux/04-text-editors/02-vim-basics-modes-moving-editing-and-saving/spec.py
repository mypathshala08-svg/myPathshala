import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='04-text-editors', lesson='02-vim-basics-modes-moving-editing-and-saving', n='4.2',
    module_label='Module 4 · Text editors: nano and vim',
    title='vim basics: modes, moving, editing and saving',
    desc='vi and vim from zero: Normal, Insert, Command-line and Visual modes; i a o I A O and Esc; moving with h j k l (j down, k up), w b e, 0 $, gg G and :N; x, dd, yy, p, P, r, cw, counts, u and Ctrl+R; :w :q :wq :q! ZZ; searching with / ? n N; swap files and vimtutor. Every key verified by really typing it into vim, real screens, and examples for admins, developers, DBAs and data teams.',
    og_desc='Why vi ignored your typing: modes, the 30 keys that cover daily work, and how to exit vim, every result verified in a real vim.',
    minutes=38, level='Beginner → Intermediate',
    lead='vi is on every Linux server, but typing into it the first time goes wrong. This lesson explains modes and the keys for moving, editing, saving and searching, with every result proven by really typing the keys into vim, plus real screens.',
    chips=['Keys verified in real vim', 'Real screens', 'Keys by field', 'Practice lab with checker'],
)

MAIN = """# vim can run commands without a screen (-es): the same ex commands you type after ':'
printf 'line 1\\nline 2\\nline 3\\nline 4\\n' > notes.txt
vim -u NONE -N -i NONE -es -c '2d' -c 'wq' notes.txt     # like: 2G dd :wq
cat notes.txt
vim -u NONE -N -i NONE -es -c '1t$' -c 'wq' notes.txt    # like: yy G p :wq
cat notes.txt
"""

RUN = dict(
    heading='vim without a screen',
    intro='<p>The browser runner has no full-screen terminal, but vim can also run ex commands in batch mode (<code>-es</code>). These are the same commands you type after <code>:</code>. Practise the real keys on your PC with <code>vimtutor</code>.</p>',
    code=MAIN,
    anno=[
        ("vim -u NONE -N -i NONE -es -c '2d' -c 'wq' notes.txt     # like: 2G dd :wq", 'Delete line 2, save, quit.'),
        ("vim -u NONE -N -i NONE -es -c '1t$' -c 'wq' notes.txt    # like: yy G p :wq", 'Copy line 1 to the end.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which line disappeared, and which was copied?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which lines remain after deleting lines 2 to 3? Then run.',
             code="printf 'a\\nb\\nc\\nd\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '2,3d' -c 'wq' f.txt\ncat f.txt\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the file is not saved. Fix the last command.',
             code="printf 'a\\nb\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '1d' -c 'q!' f.txt\ncat f.txt\n"),
        dict(label='4 · Your turn', hint='Append the line <code>timeout=30</code> at the end of app.conf.',
             code="printf 'port=80\\n' > app.conf\nvim -u NONE -N -i NONE -es -c \"call append('$', 'timeout=30')\" -c 'wq' app.conf\ncat app.conf\n"),
        dict(label='5 · Challenge', hint='Move line 1 to the end (like dd G p).',
             code="printf 'one\\ntwo\\nthree\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '1m$' -c 'wq' f.txt\ncat f.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the real keys',
    intro='<p>vim needs a keyboard. These are the best ways to practise. Screens are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · The built-in 30-minute course', cmd='vimtutor', output='===============================================================================\n=    W e l c o m e   t o   t h e   V I M   T u t o r    -    Version 1.7      =\n===============================================================================', note='Typical. The best first step: it edits a copy of a lesson file, so you cannot break anything.'),
        dict(title='2 · Which vim is installed?', cmd='vim --version | head -1; readlink -f $(command -v vi)', output=pc('vim --version | head -1; readlink -f $(command -v vi)'), note='Recorded on our build machine.'),
        dict(title='3 · Open at a line', cmd='vim +3 /etc/hosts', output='127.0.0.1 localhost\n127.0.1.1 riya-laptop\n# The following lines are desirable for IPv6 capable hosts\n"/etc/hosts" [readonly] 9L, 221B', note='Typical: [readonly] because normal users may not write /etc/hosts (use sudoedit).'),
        dict(title='4 · Recover after a crash', cmd='vim -r app.conf', output='Using swap file ".app.conf.swp"\nRecovery completed. You should check if everything is OK.', note='Typical. After checking, save and delete the old .swp file.'),
    ],
)

TRACE = dict(
    heading='ex commands step by step',
    intro='<p>Each line runs one vim command in batch mode. Watch the <b>Files</b> box: the size of notes.txt changes as lines are deleted and added.</p>',
    code='''printf 'line 1\\nline 2\\nline 3\\n' > notes.txt
vim -u NONE -N -i NONE -es -c '2d' -c 'wq' notes.txt
vim -u NONE -N -i NONE -es -c "call append('$', 'line 9')" -c 'wq' notes.txt
vim -u NONE -N -i NONE -es -c '1d' -c 'q!' notes.txt
cat notes.txt
''',
    notes={2: ':2d :: Line 2 deleted and saved.', 3: 'append() :: A line added at the end.', 4: ':q! :: Change thrown away: size unchanged.'},
)

WORKED_INTRO = 'Three tasks from real jobs, shown as the keys you type and verified with vim’s batch mode.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Change a port and save',
         problem='<p>In app.conf change port=80 to port=8080. Keys: <code>/port⏎ $ xx a8080 Esc :wq⏎</code>. Here the same with ex commands.</p>',
         inp='app.conf',
         approach=['Find the line, change the value.', 'Write and quit.'],
         code='''printf 'port=80\\nhost=localhost\\n' > app.conf
vim -u NONE -N -i NONE -es -c '/^port/s/80/8080/' -c 'wq' app.conf
cat app.conf
''',
         notes={2: 'Edit :: Search the line, substitute on it, save.'},
         tryit='Change host instead.'),
    dict(level='i', tag='Development', title='Comment out a line',
         problem='<p>Disable the debug setting by adding <code># </code> in front (keys: <code>/debug⏎ I# Esc :wq⏎</code>).</p>',
         inp='settings.py',
         approach=['Find the line.', 'Insert at its start.'],
         code='''printf 'DEBUG = True\\nPORT = 8000\\n' > settings.py
vim -u NONE -N -i NONE -es -c '/DEBUG/s/^/# /' -c 'wq' settings.py
cat settings.py
''',
         notes={2: 'Prefix :: s/^/# / inserts at the line start.'},
         tryit='Uncomment it again with s/^# //.'),
    dict(level='a', tag='Data', title='Remove a footer and add a header',
         problem='<p>A CSV export has a “Total” line at the end and no header. Delete the last line (<code>G dd</code>) and add a header on top (<code>gg O … Esc</code>).</p>',
         inp='rows + Total line',
         approach=['$d deletes the last line.', '0put inserts before line 1.'],
         code='''printf '1,Asha,91\\n2,Ravi,78\\nTotal,,169\\n' > marks.csv
vim -u NONE -N -i NONE -es -c '$d' -c "call append(0, 'id,name,marks')" -c 'wq' marks.csv
cat marks.csv
''',
         notes={2: 'Two edits, one save.'},
         tryit='Delete the last two lines with $-1,$d.'),
]

QUIZ = mix([
    dict(q='vim opens in which mode?', options=['Insert', 'Normal', 'Visual', 'Command-line'], answer=1,
         why='Normal mode: keys are commands.'),
    dict(q='Which key moves the cursor down?', options=['k', 'j', 'h', 'l'], answer=1,
         why='j = down, k = up (verified by a real run).'),
    dict(q='How do you quit without saving?', options=[':q', ':wq', ':q!', 'ZZ'], answer=2,
         why=':q! forces quit and discards changes.'),
    dict(q='dd then p does what?', options=['Deletes two lines', 'Moves the line below the next one', 'Duplicates', 'Nothing'], answer=1,
         why='dd cuts the line, p pastes it below the next line.'),
    dict(q='Which key starts typing at the end of the line?', options=['a', 'A', 'o', 'I'], answer=1,
         why='A appends at the line end.'),
    dict(q=':q says “E37: No write since last change”. Why?', options=['Disk full', 'Unsaved changes', 'Read-only', 'Wrong mode'], answer=1,
         why=':wq to save or :q! to discard.'),
    dict(q='How do you undo and redo?', options=['Ctrl+Z / Ctrl+Y', 'u / Ctrl+R', 'z / Z', ':undo / :redo only'], answer=1,
         why='u undo, Ctrl+R redo.'),
    dict(q='How do you search for “port”?', options=['Ctrl+F port', '/port Enter', ':find port', 's port'], answer=1,
         why='/ searches forward; n for the next match.'),
])

REVISION = [
    'Modes: Normal (commands), Insert (<code>i</code>, typing), Command-line (<code>:</code>), Visual (<code>v</code>). <b>Esc</b> → Normal.',
    'Insert at: <code>i</code> before, <code>a</code> after, <code>I</code> line start, <code>A</code> line end, <code>o</code>/<code>O</code> new line below/above.',
    'Move: <code>h j k l</code> (j down, k up), <code>w b e</code>, <code>0 $</code>, <code>gg G</code>, <code>:42</code>.',
    'Edit: <code>x</code>, <code>dd</code>, <code>yy</code>, <code>p P</code>, <code>r</code>, <code>cw</code>, counts like <code>3dd</code>.',
    'Undo <code>u</code>, redo <code>Ctrl+R</code>, repeat <code>.</code>.',
    'Save/quit: <code>:w</code>, <code>:q</code>, <code>:wq</code> (= <code>ZZ</code>, <code>:x</code>), <code>:q!</code>; <code>:w name</code> save as.',
    'Search: <code>/text</code>, <code>?text</code>, <code>n N</code>, <code>*</code>.',
    'Swap file <code>.file.swp</code> = crash recovery; <code>vimtutor</code> to practise.',
]

FAQ = [
    ('How do I exit vim?', 'Press Esc, then type :q and Enter (or :q! to discard changes, :wq to save and quit).'),
    ('Why can I not type in vi?', 'vi starts in Normal mode where keys are commands. Press i to enter Insert mode.'),
    ('What is the difference between vi and vim?', 'vim (Vi IMproved) is an extended vi with undo history, syntax colours, visual mode and much more; on Linux, vi usually starts vim.'),
    ('How do I delete a line in vim?', 'dd in Normal mode; 3dd deletes three lines.'),
    ('How do I copy and paste in vim?', 'yy copies a line, p pastes below (P above). With a selection: v, move, y, then p.'),
    ('How do I go to a line number?', ':42 Enter, or 42G, or open with vim +42 file.'),
    ('What is a .swp file?', 'vim’s swap file for crash recovery; it appears while a file is open and is removed on a clean exit.'),
]

PRACTICE_INTRO = 'vim tasks you can check in the browser with batch mode (-es). On your PC, do the same with the real keys shown.'
PROBLEMS = [
    dict(level='easy', title='Delete the first line', stmt='Keys <code>dd :wq</code>. Batch: delete line 1.', inp='a b c',
         code="printf 'a\\nb\\nc\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '1d' -c 'wq' f.txt\ncat f.txt\n", explain=':1d = line 1 dd.'),
    dict(level='easy', title='Append a line', stmt='Keys <code>G o text Esc :wq</code>. Add “end” at the end.', inp='a b',
         code="printf 'a\\nb\\n' > f.txt\nvim -u NONE -N -i NONE -es -c \"call append('$', 'end')\" -c 'wq' f.txt\ncat f.txt\n", explain='append(\'$\', …) adds a line after the last one (like G o).'),
    dict(level='easy', title='Quit without saving', stmt='Keys <code>dd :q!</code>. The file must stay unchanged.', inp='a b',
         code="printf 'a\\nb\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '1d' -c 'q!' f.txt\ncat f.txt\n", explain=':q! discards.'),
    dict(level='medium', title='Copy a line to the end', stmt='Keys <code>yy G p :wq</code>.', inp='x y z',
         code="printf 'x\\ny\\nz\\n' > f.txt\nvim -u NONE -N -i NONE -es -c '1t$' -c 'wq' f.txt\ncat f.txt\n", explain=':t = copy (to).'),
    dict(level='medium', title='Delete three lines', stmt='Keys <code>3dd :wq</code> from line 2.', inp='1 to 5',
         code="seq 1 5 > n.txt\nvim -u NONE -N -i NONE -es -c '2,4d' -c 'wq' n.txt\ncat n.txt\n", explain='A range 2,4 = three lines.'),
    dict(level='business', title='Fix a config value', stmt='Change <code>env=dev</code> to <code>env=prod</code> (keys: /env⏎ $ cw… or :s).', inp='env=dev',
         code="printf 'name=shop\\nenv=dev\\n' > app.conf\nvim -u NONE -N -i NONE -es -c '/^env/s/dev/prod/' -c 'wq' app.conf\ncat app.conf\n", explain='Search the line, substitute.'),
]

SCN_INTRO = 'Interview questions about vi and vim, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you exit vi?”',
        'The famous question, sometimes as a joke, often as a real test.',
        'do you understand modes?',
        '''<ul>
          <li>Esc to be sure you are in Normal mode.</li>
          <li><code>:wq</code> save and quit, <code>:q!</code> quit without saving, <code>ZZ</code> save if changed.</li>
          <li>Explain why: typed keys are commands in Normal mode.</li>
        </ul>''', 'closing the terminal window.') +
    scn('Operations', 'Junior', 'Swap file warning on a production config',
        'Opening /etc/nginx/nginx.conf shows “E325 ATTENTION Found a swap file”.',
        'do you know swap files?',
        '''<ol>
          <li>Someone may be editing it now, or vim crashed earlier: check with <code>ps aux | grep vim</code> and <code>who</code>.</li>
          <li>If nobody is editing: R to recover and compare, or delete the stale <code>.nginx.conf.swp</code>.</li>
          <li>Never edit the same config from two sessions.</li>
        </ol>''', 'pressing E and overwriting a colleague’s edit.') +
    scn('Certification', 'Mid-level', '“Edit /etc/fstab during the exam”',
        'RHCSA-style tasks need quick, exact edits.',
        'are you fluent with vim keys?',
        '''<ul>
          <li><code>sudo vim /etc/fstab</code> (exam context), <code>G o</code> to add a line, Esc, <code>:wq</code>.</li>
          <li>Use <code>:set number</code>, <code>/UUID</code> to find lines, <code>yy p</code> to copy a similar line and edit it.</li>
          <li>Validate (<code>mount -a</code>) before rebooting.</li>
        </ul>''', 'a typo that stops the system from booting.')
) + interview([
    ('Name the vim modes.', 'Normal, Insert, Command-line, Visual (and Replace).'),
    ('How do you save and quit / quit without saving?', ':wq (or ZZ, :x) / :q!'),
    ('How do you delete 5 lines?', '5dd in Normal mode.'),
    ('Copy and paste a line?', 'yy then p (below) or P (above).'),
    ('Which keys move left, down, up, right?', 'h, j, k, l.'),
    ('How do you undo and redo?', 'u and Ctrl+R.'),
    ('How do you go to the last line?', 'G (gg for the first).'),
], [
    ('RHCSA (EX200)', '“Create and edit text files” with vim is used in almost every task.'),
    ('LFCS', 'Essential Commands: edit text files with vi/vim.'),
    ('CompTIA Linux+', 'vi/vim modes and basic commands.'),
]) + distro('vi is everywhere, but which vi differs.', [
    ('vi command', 'vim.tiny (minimal) or vim', 'vi = vim-minimal; vim = vim-enhanced', 'vim', 'WSL: as Ubuntu; Git Bash: vim'),
    ('Arrow keys in Insert mode', 'vim: yes; vim.tiny: sometimes letters', 'vim-minimal: mostly yes', 'yes', 'yes'),
    ('vimtutor', 'with vim package', 'with vim-enhanced', 'yes', 'WSL yes'),
    ('Containers (busybox)', 'busybox vi: basic keys only', '—', '—', '—'),
]) + teaser('4.3', 'A config has “localhost” on 40 lines and Riya must change all of them to “db.internal”, but only after confirming each one. Then she needs to add “# ” in front of 20 lines at once. Which two vim commands do this in seconds?')

CHEATSHEET = cheatsheet('vim basics', [
    ('Modes', [('i a o', 'insert / after / new line'), ('I A O', 'line start / end / above'), ('Esc', 'back to Normal'), (':', 'command line'), ('v V', 'visual select')]),
    ('Move', [('h j k l', '← ↓ ↑ →'), ('w b e', 'words'), ('0 ^ $', 'line start / end'), ('gg G', 'file top / end'), (':42  42G', 'line 42')]),
    ('Edit', [('x', 'delete char'), ('dd 3dd', 'delete line(s)'), ('yy p P', 'copy, paste'), ('r cw C', 'replace, change'), ('u Ctrl+R .', 'undo, redo, repeat')]),
    ('Save · quit', [(':w', 'save'), (':wq ZZ :x', 'save + quit'), (':q', 'quit'), (':q! ZQ', 'discard + quit'), (':w name', 'save as')]),
    ('Search · help', [('/text ?text', 'search'), ('n N', 'next / previous'), ('*', 'word under cursor'), ('vimtutor', '30-min lesson'), (':help x', 'help')]),
])

MINDMAP = mindmap('vim basics', [
    ('Modes', 'blue', ['Normal = commands', 'i → Insert', 'Esc → Normal']),
    ('Move', 'green', ['h j↓ k↑ l', 'w b, 0 $', 'gg G :42']),
    ('Edit', 'amber', ['x dd yy p', 'r cw, counts', 'u Ctrl+R .']),
    ('Save', 'red', [':w :q', ':wq ZZ', ':q! discard']),
    ('Search', 'violet', ['/text ?text', 'n N *', '/ then d/…']),
    ('Safety', 'acc', ['swap files', 'sudoedit', 'vimtutor']),
])

LAB = lab('first vim edits', 'Build the lab, open each file with vim on your PC and make the changes with the keys from this lesson (or batch mode), then run the checker.',
    setup='''mkdir -p ~/lab42 && cd ~/lab42 && rm -f app.conf notes.txt
printf 'port=80\\nhost=localhost\\nuser=admin\\ndebug=true\\n' > app.conf
printf 'line 1\\nline 2\\nline 3\\n' > notes.txt''',
    tasks=['app.conf: change <code>port=80</code> to <code>port=8080</code>.',
           'app.conf: delete the line <code>debug=true</code> (<code>G dd</code>).',
           'notes.txt: add a line <code>line 0</code> above line 1 (<code>gg O</code>).',
           'notes.txt: copy line 3 to the end so it appears twice (<code>G yy p</code>).'],
    solution='''vim -u NONE -N -i NONE -es -c '/^port/s/80/8080/' -c 'g/^debug/d' -c 'wq' app.conf
vim -u NONE -N -i NONE -es -c "call append(0, 'line 0')" -c '$t$' -c 'wq' notes.txt''',
    check='''cd ~/lab42
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 port 8080"     'grep -qx "port=8080" app.conf'
ok "2 debug removed" '! grep -q "^debug" app.conf'
ok "3 line 0 first"  '[ "$(head -n 1 notes.txt)" = "line 0" ]'
ok "4 line 3 twice"  '[ "$(grep -cx "line 3" notes.txt)" -eq 2 ]' ''')
