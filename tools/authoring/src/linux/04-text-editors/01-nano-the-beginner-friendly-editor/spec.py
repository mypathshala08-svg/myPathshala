import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='04-text-editors', lesson='01-nano-the-beginner-friendly-editor', n='4.1',
    module_label='Module 4 · Text editors: nano and vim',
    title='nano: the beginner-friendly editor',
    desc='Edit files in the terminal with GNU nano: open, save (Ctrl+O, Ctrl+S) and exit (Ctrl+X), cut, copy and paste lines (Ctrl+K, Ctrl+U, Alt+A, Alt+6), search, replace and go to line (Ctrl+W, Ctrl+\\, Ctrl+_), undo (Alt+U), line numbers, backups (-B), read-only view (-v), sudoedit for system files, ~/.nanorc and the EDITOR variable. Real recorded nano screens and examples for admins, developers, DBAs, data and DevOps teams.',
    og_desc='A one-line fix at 11 pm with no mouse: nano’s keys, safe editing with sudoedit, and real recorded screens.',
    minutes=32, level='Beginner → Intermediate',
    lead='A server needs a one-line config change and there is no desktop. This lesson teaches nano completely: the keys, what saving really does, editing system files safely and how every IT role uses it, with real recorded nano screens.',
    chips=['Real nano screens', 'Keys by field', 'Errors decoded', 'Practice lab with checker'],
)

MAIN = """# nano is interactive; this script prepares a file and shows
# what an edit changes (the edit itself is done by sed here)
printf 'port=80\\nhost=localhost\\nuser=admin\\n' > app.conf
cp app.conf app.conf.bak
sed -i 's/^port=80$/port=8080/' app.conf
diff app.conf.bak app.conf
cat -n app.conf
"""

RUN = dict(
    heading='Before and after an edit',
    intro='<p>nano needs a real keyboard, so the browser runner cannot open it. This script does what you would do around a nano edit: back up, change, compare. Then open nano on your own PC (see “Run on your PC”).</p>',
    code=MAIN,
    anno=[
        ('cp app.conf app.conf.bak', 'Backup first, always.'),
        ("sed -i 's/^port=80$/port=8080/' app.conf", 'The change you would make in nano.'),
        ('diff app.conf.bak app.conf', 'Exactly what changed.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which line changed?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which editor will tools open here? Then run.',
             code='echo "${EDITOR:-not set}"\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this “edit” destroyed the file’s other lines. Fix it so only the port changes.',
             code="printf 'port=80\\nhost=db\\n' > app.conf\necho 'port=8080' > app.conf\ncat app.conf\n"),
        dict(label='4 · Your turn', hint='Create a ~/.nanorc with line numbers and 4-space tabs, and show it.',
             code="printf 'set linenumbers\\nset tabsize 4\\n' > ~/.nanorc\ncat ~/.nanorc\n"),
        dict(label='5 · Challenge', hint='Make nano the default editor for this session and print it.',
             code='export EDITOR=nano\necho "$EDITOR"\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: nano for real',
    intro='<p>nano needs a terminal with a keyboard. Try these on Ubuntu, WSL or a server. Screens are <b>typical</b>.</p>',
    items=[
        dict(title='1 · Open and save', cmd='nano notes.txt', output='  GNU nano 7.2          notes.txt\n\n\n                       [ New File ]\n^G Help   ^O Write Out ^W Where Is ^K Cut   ^T Execute\n^X Exit   ^R Read File ^\\ Replace  ^U Paste ^J Justify', note='Typical. Type a line, Ctrl+O, Enter, Ctrl+X.'),
        dict(title='2 · A root file, the safe way', cmd='sudoedit /etc/hosts', output='[sudo] password for riya:\n  GNU nano 7.2     /var/tmp/hostsXXQk2a.txt', note='Typical. You edit a temporary copy; sudo writes it back on exit.'),
        dict(title='3 · nano for crontab', cmd='EDITOR=nano crontab -e', output='  GNU nano 7.2   /tmp/crontab.Xb3k8F/crontab\n# Edit this file to introduce tasks to be run by cron.', note='Typical (Lesson 17.4).'),
        dict(title='4 · Is nano installed?', cmd='nano --version | head -1', output=pc('nano --version | head -1'), note='Recorded on our build machine. Missing? <code>sudo apt install nano</code> (or <code>sudo dnf install nano</code>).'),
    ],
)

TRACE = dict(
    heading='The steps around an edit',
    intro='<p>Step through the safe-edit routine. Watch the <b>Files</b> box: the backup appears, then the file changes.</p>',
    code='''printf 'port=80\\nhost=db\\n' > app.conf
cp app.conf app.conf.bak
sed -i 's/80/8080/' app.conf
cmp -s app.conf app.conf.bak || echo "changed"
''',
    notes={1: 'File :: Two settings.', 2: 'Backup :: Same size copy.', 3: 'Edit :: What you would do in nano.', 4: 'Check :: Files now differ.'},
)

WORKED_INTRO = 'nano itself is interactive; these worked examples prepare, check and undo edits from the shell, as professionals do around every manual change.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Back up, edit, compare',
         problem='<p>Change <code>port=80</code> to <code>port=8080</code> safely and prove what changed.</p>',
         inp='app.conf',
         approach=['cp to .bak first.', 'Edit (nano by hand; sed here).', 'diff the two.'],
         code='''printf 'port=80\\nhost=localhost\\n' > app.conf
cp app.conf app.conf.bak
sed -i 's/^port=80$/port=8080/' app.conf
diff app.conf.bak app.conf
''',
         notes={2: 'Backup :: Your undo.', 4: 'Proof :: Only one line changed.'},
         tryit='Roll back with <code>cp app.conf.bak app.conf</code>.', expect='any'),
    dict(level='i', tag='DevOps', title='Check a YAML file after editing',
         problem='<p>After editing a YAML file in nano, check it has no tab characters (YAML forbids tabs for indentation).</p>',
         inp='app.yml with one tab',
         approach=['grep for a tab character.', 'Show where with cat -A.'],
         code='''printf 'app:\\n  port: 8080\\n\\thost: db\\n' > app.yml
grep -n "$(printf '\\t')" app.yml && echo "tabs found: fix them in nano"
cat -A app.yml
''',
         notes={2: 'Find :: grep with a real tab.', 3: 'Show :: ^I is the tab.'},
         tryit='Set <code>set tabstospaces</code> in ~/.nanorc so this never happens.'),
    dict(level='a', tag='Security', title='Who may edit what?',
         problem='<p>Before editing, check whether you can write a file, and use sudoedit only if needed.</p>',
         inp='/etc/hosts and ./app.conf',
         approach=['test -w for write permission.', 'Choose nano or sudoedit.'],
         code='''touch app.conf
for f in app.conf /etc/hosts; do
  if [ -w "$f" ]; then echo "nano $f"; else echo "sudoedit $f"; fi
done
''',
         notes={3: 'Test :: -w = writable by me.'},
         tryit='Add /etc/shadow to the list.'),
]

QUIZ = mix([
    dict(q='How do you save in nano?', options=['Ctrl+S only', 'Ctrl+O then Enter', ':w', 'Esc then S'], answer=1,
         why='Ctrl+O = Write Out (Ctrl+S also works in nano 7).'),
    dict(q='How do you exit nano?', options=['Ctrl+Q', 'Ctrl+X', ':q', 'Esc'], answer=1,
         why='Ctrl+X; it asks Y/N if there are unsaved changes.'),
    dict(q='What does ^K mean in nano’s shortcut list?', options=['Alt+K', 'Ctrl+K', 'Shift+K', 'the K key'], answer=1,
         why='^ = Ctrl; M- = Alt.'),
    dict(q='Ctrl+K then Ctrl+U on another line does what?', options=['Deletes both', 'Moves the line', 'Copies the file', 'Nothing'], answer=1,
         why='Cut, then paste elsewhere = move.'),
    dict(q='Which is the safe way to edit /etc/hosts?', options=['sudo nano /etc/hosts', 'sudoedit /etc/hosts', 'nano -v /etc/hosts', 'chmod 777 /etc/hosts'], answer=1,
         why='sudoedit runs your editor as you on a temporary copy.'),
    dict(q='How do you open nano at line 42?', options=['nano -42 f', 'nano +42 f', 'nano --line=42 f', 'nano f:42'], answer=1,
         why='+N starts at that line.'),
    dict(q='The title bar shows “app.conf *”. Meaning?', options=['Read-only', 'Unsaved changes', 'A backup exists', 'File is new'], answer=1,
         why='* = the buffer differs from the file.'),
])

REVISION = [
    '<code>nano file</code>: type to edit; <b>Ctrl+O</b> Enter save; <b>Ctrl+X</b> exit (Y/N if unsaved).',
    '^ = Ctrl, M- = Alt (or Esc then the key).',
    'Ctrl+K cut line, Ctrl+U paste, Alt+A mark, Alt+6 copy; Alt+U undo, Alt+E redo.',
    'Ctrl+W search, Alt+W next, Ctrl+\\ replace (Y/N/A), Ctrl+_ go to line.',
    'Options: -l line numbers, +N start line, -B backup file~, -v read-only.',
    'System files: <code>sudoedit file</code>, not sudo nano.',
    '~/.nanorc for settings; <code>export EDITOR=nano</code> for crontab, git, visudo.',
    'The * in the title = unsaved; nothing changes on disk until you write out.',
]

FAQ = [
    ('How do I save and exit nano?', 'Ctrl+O, Enter to save; Ctrl+X to exit. Or Ctrl+X, Y, Enter.'),
    ('How do I exit nano without saving?', 'Ctrl+X, then N.'),
    ('What do ^ and M- mean in nano?', '^ is the Ctrl key, M- is the Meta key (Alt, or press Esc first).'),
    ('How do I search and replace in nano?', 'Ctrl+\\, type the text, Enter, the replacement, Enter, then Y, N or A (all).'),
    ('How do I show line numbers?', 'Alt+# while editing, nano -l, or set linenumbers in ~/.nanorc.'),
    ('Why use sudoedit instead of sudo nano?', 'sudoedit runs your editor as you on a copy and only the final write is done as root; it is safer and uses your settings.'),
    ('nano or vim?', 'nano is easier to start; vim is installed almost everywhere and much faster once learned (Lessons 4.2, 4.3).'),
]

PRACTICE_INTRO = 'nano is interactive, so these problems practise what happens around an edit. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Make a backup', stmt='Copy <code>hosts.txt</code> to <code>hosts.txt.bak</code> before editing.', inp='hosts.txt',
         code='echo "127.0.0.1 localhost" > hosts.txt\ncp hosts.txt hosts.txt.bak\nls\n', explain='The simplest undo.'),
    dict(level='easy', title='Default editor', stmt='Set EDITOR to nano and print it.', inp='—',
         code='export EDITOR=nano\necho "$EDITOR"\n', explain='Tools read $EDITOR.'),
    dict(level='easy', title='Can I write it?', stmt='Print yes if you may write <code>/etc/passwd</code>, otherwise no.', inp='/etc/passwd',
         code='[ -w /etc/passwd ] && echo yes || echo no\n', explain='Normal users cannot; use sudoedit.'),
    dict(level='medium', title='Show the change', stmt='After changing port 80 to 8080, show the difference.', inp='app.conf',
         code="printf 'port=80\\n' > a.conf; cp a.conf a.bak\nsed -i 's/80/8080/' a.conf\ndiff a.bak a.conf\n", explain='diff &lt; old, &gt; new.', expect='any'),
    dict(level='medium', title='nanorc', stmt='Write a ~/.nanorc with linenumbers and autoindent.', inp='—',
         code="printf 'set linenumbers\\nset autoindent\\n' > ~/.nanorc\ncat ~/.nanorc\n", explain='One setting per line.'),
    dict(level='business', title='Roll back', stmt='The edited config is broken. Restore the backup and show it.', inp='app.conf.bak',
         code="echo good > app.conf.bak; echo broken > app.conf\ncp app.conf.bak app.conf\ncat app.conf\n", explain='Backup = rollback.'),
]

SCN_INTRO = 'Interview questions about terminal editors and safe editing.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you edit a file on a Linux server?”',
        'The interviewer wants to see you are comfortable without a desktop.',
        'do you know at least one terminal editor?',
        '''<ul>
          <li><code>nano file</code>: edit, Ctrl+O save, Ctrl+X exit.</li>
          <li>Or vim: i, edit, Esc, :wq (Lesson 4.2).</li>
          <li>Back up first, check with diff afterwards.</li>
        </ul>''', '“I copy it to my laptop and use Notepad”.') +
    scn('Operations', 'Junior', 'Editing a system file',
        'You must change /etc/ssh/sshd_config on a server.',
        'do you edit privileged files safely?',
        '''<ol>
          <li><code>sudo cp -p /etc/ssh/sshd_config{,.bak}</code>.</li>
          <li><code>sudoedit /etc/ssh/sshd_config</code>.</li>
          <li>Validate (<code>sudo sshd -t</code>) before reloading, and keep your session open (Lesson 16.5).</li>
        </ol>''', 'editing and restarting without a test or a backup.') +
    scn('DevOps · automation', 'Mid-level', '“Can the deploy script open nano to change the version?”',
        'A junior adds <code>nano version.txt</code> to a CI script.',
        'do you know interactive vs automated?',
        '''<ul>
          <li>CI has no keyboard: the job hangs or fails.</li>
          <li>Use non-interactive tools: <code>sed -i</code>, <code>printf &gt;</code>, templates (envsubst), config management.</li>
          <li>Keep manual edits for humans, with backups and reviews.</li>
        </ul>''', 'adding a timeout and hoping.')
) + interview([
    ('Save and exit in nano?', 'Ctrl+O Enter, Ctrl+X (or Ctrl+X, Y, Enter).'),
    ('Cut and paste a line?', 'Ctrl+K to cut, Ctrl+U to paste.'),
    ('Search and replace?', 'Ctrl+\\, search text, replacement, then Y/N/A.'),
    ('Edit a root-owned file?', 'sudoedit file (preferred over sudo nano).'),
    ('Change the default editor?', 'export EDITOR=nano (and VISUAL) in ~/.bashrc.'),
], [
    ('RHCSA (EX200)', '“Create and edit text files” (vim is expected, nano accepted where installed).'),
    ('LFCS', 'Essential Commands: create and edit text files with a terminal editor.'),
    ('CompTIA Linux+', 'Text editors (nano, vi/vim) in file management objectives.'),
]) + distro('nano is common, but not everywhere by default.', [
    ('Installed by default', 'yes', 'often not on minimal; dnf install nano', 'pico/nano (older); brew install nano', 'WSL yes; Git Bash: nano included'),
    ('Default $EDITOR', 'nano (select-editor)', 'vi', 'vim / nano', 'WSL as Ubuntu; Git Bash: vim'),
    ('Ctrl+S saves', 'yes (nano 7)', 'nano 5.6 (RHEL 9): yes', 'depends on version', 'yes'),
    ('sudoedit', 'yes', 'yes', 'yes', 'WSL yes'),
]) + teaser('4.2', 'Riya opens a file on a server with <code>vi</code>, types her name, and it does not appear: instead the cursor jumps around and a line disappears. Why does vi ignore her typing, and which single key fixes it?')

CHEATSHEET = cheatsheet('nano', [
    ('Start', [('nano file', 'open / create'), ('nano +42 file', 'at line 42'), ('nano -l file', 'line numbers'), ('nano -B file', 'backup file~'), ('nano -v file', 'read-only')]),
    ('Save · exit', [('^O Enter', 'save'), ('^S', 'quick save'), ('^X', 'exit'), ('^X N', 'exit, discard'), ('^C', 'cancel a question')]),
    ('Edit', [('^K', 'cut line'), ('^U', 'paste'), ('M-A', 'mark (select)'), ('M-6', 'copy'), ('M-U / M-E', 'undo / redo')]),
    ('Find', [('^W', 'search'), ('M-W', 'next'), ('^\\', 'replace Y/N/A'), ('^_', 'go to line'), ('M-# ', 'line numbers')]),
    ('Safe setup', [('sudoedit /etc/f', 'root files'), ('export EDITOR=nano', 'default editor'), ('~/.nanorc', 'settings'), ('cp f f.bak', 'backup first'), ('diff f.bak f', 'check')]),
])

MINDMAP = mindmap('nano', [
    ('Basics', 'blue', ['type to edit', '^O save, ^X exit', '* = unsaved']),
    ('Edit', 'green', ['^K cut, ^U paste', 'M-A mark, M-6 copy', 'M-U undo']),
    ('Find', 'violet', ['^W search', '^\\ replace', '^_ go to line']),
    ('Start options', 'amber', ['+42, -l', '-B backup', '-v read-only']),
    ('Safety', 'red', ['sudoedit', 'backup + diff', 'no editors in CI']),
    ('Setup', 'acc', ['~/.nanorc', 'EDITOR=nano', 'crontab -e, git']),
])

LAB = lab('prepare a safe edit', 'Build the lab, do the four tasks (use nano for task 3 on your PC), then run the checker.',
    setup='''mkdir -p ~/lab41 && cd ~/lab41 && rm -f app.conf* .nanorc_test
printf 'port=80\\nhost=localhost\\nuser=admin\\n' > app.conf''',
    tasks=['Make a backup <code>app.conf.bak</code>.',
           'Write a file <code>.nanorc_test</code> containing the line <code>set linenumbers</code>.',
           'In <code>app.conf</code>, change <code>port=80</code> to <code>port=8080</code> (with nano: Ctrl+\\ or edit, Ctrl+O, Ctrl+X).',
           'Delete the line <code>user=admin</code> (nano: Ctrl+K on that line).'],
    solution='''cp app.conf app.conf.bak
echo 'set linenumbers' > .nanorc_test
sed -i 's/^port=80$/port=8080/' app.conf
sed -i '/^user=admin$/d' app.conf''',
    check='''cd ~/lab41
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 backup"        'grep -qx "port=80" app.conf.bak 2>/dev/null'
ok "2 nanorc"        'grep -qx "set linenumbers" .nanorc_test 2>/dev/null'
ok "3 port changed"  'grep -qx "port=8080" app.conf'
ok "4 user removed"  '! grep -q "^user=" app.conf' ''')
