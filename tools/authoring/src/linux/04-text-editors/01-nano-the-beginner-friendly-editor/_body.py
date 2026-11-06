import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

CONF = "printf 'port=80\\nhost=localhost\\nuser=admin\\n' > app.conf"
RS = 'Real screen: nano 7.2 run in a terminal on Ubuntu 24.04, keys sent one by one'
def NS(steps, setup=CONF, cmd='nano app.conf', w=64, h=9):
    return (RS, tmux_screens(setup, cmd, steps, w, h)[-1])
def NI(sit, keys_shown, steps, why, setup=CONF, cmd='nano app.conf'):
    return dict(situation=sit, cmd=f'{cmd}\n# then press: {keys_shown}', rec=NS(steps, setup, cmd), why=why)

HOOK = hook('A server stops working at 11 pm. The fix is one line in a config file: change <code>port=80</code> to <code>port=8080</code>. There is no mouse, no Notepad, no VS Code, only a black terminal over SSH. <b>nano</b> is installed on almost every Linux system, shows its own shortcuts on screen, and you can learn the five keys you need in five minutes.',
    ['open, edit, save and exit a file with nano (<code>Ctrl+O</code>, <code>Ctrl+X</code>)',
     'cut, paste, search, replace and jump to a line (<code>Ctrl+K</code>, <code>Ctrl+U</code>, <code>Ctrl+W</code>, <code>Ctrl+\\</code>, <code>Ctrl+_</code>)',
     'edit system files safely (<code>sudoedit</code>, backups with <code>-B</code>) and set nano as your default editor',
     'read nano’s screen: the title bar, the status line and the shortcut list'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a fix at 11 pm'),
    ('decide', 'Which key when?', 2, 'the five keys first'),
    ('definition', 'What nano is', 4, 'simple meaning + 4 depths'),
    ('commands', 'Keys by field', 12, 'real screens, your field'),
    ('screens', 'A full edit, screen by screen', 4, 'real recording'),
    ('errors', 'Errors decoded', 3, 'permission, read-only'),
    ('run', 'Run on your PC', 4, 'nano needs a real terminal'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'screens', 'lab'])
DECIDE = decide('Which nano key? (^ means the Ctrl key, M- means Alt)', [
    ('Open or create a file', 'nano file.txt', 'creates it on save'),
    ('Save', 'Ctrl+O, then Enter', 'O = write Out'),
    ('Exit', 'Ctrl+X', 'asks Y/N if not saved'),
    ('Cut the current line / paste it', 'Ctrl+K / Ctrl+U', 'move lines around'),
    ('Search', 'Ctrl+W, word, Enter', 'Alt+W = next match'),
    ('Search and replace', 'Ctrl+\\', 'then A = all'),
    ('Go to line 25', 'Ctrl+_  25  Enter', 'or start: nano +25 file'),
    ('Undo / redo', 'Alt+U / Alt+E', 'many steps'),
    ('Show line numbers', 'Alt+#  or nano -l', 'for error messages'),
    ('Edit a system file safely', 'sudoedit /etc/hosts', 'your own nano settings'),
])

cmap = concept_map(
    [('3.1', 'Creating files', 'echo, printf, cat > file'), ('3.5', 'Viewing files', 'less, cat -A'), ('2.3', 'Paths', 'which file you open')],
    ['open, save (Ctrl+O), exit (Ctrl+X)', 'cut, copy, paste lines; mark text', 'search, replace, go to line', 'sudoedit, backups, line numbers', '~/.nanorc and the EDITOR variable'],
    [('4.2', 'vim basics', 'the editor every server has'), ('8.4', 'sudo', 'editing files you do not own'), ('12.2', 'Startup files', 'edit .bashrc'), ('17.4', 'cron', 'crontab -e opens nano')],
    'Every admin, developer and data engineer edits config files on servers. nano is the gentle start; vim (4.2) comes next.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ ssh riya@app-01', '$ nano /etc/myapp/app.conf', ('  GNU nano 7.2   app.conf', 'acc'), ('port=80', 'out'), ('host=localhost', 'out'), ('^O Write Out  ^X Exit  ^W Where Is', 'dim')], title='riya@laptop', size=7.6, step=15)
      + t(352, 36, 'The five keys:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• just type to edit', '• Ctrl+O, Enter: save', '• Ctrl+X: exit', '• Ctrl+W: search', '• Ctrl+K / U: cut / paste'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A one-line fix at 11 pm</h2>
  <div class="story">
''' + puzzle('Riya edits a file in nano, presses <code>Ctrl+S</code> out of Windows habit, then <code>Ctrl+X</code>. nano asks “Save modified buffer?” Did Ctrl+S save the file or not? (Hint: look at the title bar in the real screens of this lesson.)') + '''
    <p class="narration">The shop’s staging server must move to port 8080 tonight. Riya connects over SSH (Lesson 16.5). There is no desktop, only a terminal.</p>
''' + scene('A terminal over SSH: nano opens app.conf; the bottom lines show the shortcuts ^O Write Out, ^X Exit, ^W Where Is.', sc,
            'nano shows its own shortcuts: <tspan font-weight="700" class="s-acc">^ means Ctrl</tspan>.') + '''
R> No mouse… how do I even start?
A> <code>nano app.conf</code>. Use the arrow keys, type your change, then <b>Ctrl+O</b> and Enter to save, <b>Ctrl+X</b> to exit. The two bottom lines always show the shortcuts: <code>^</code> means Ctrl, <code>M-</code> means Alt.
K> And if I mess it up?
A> Exit with Ctrl+X and answer <b>N</b>: nothing is saved. Today you learn nano completely: the keys, editing system files safely, and how each IT role uses it. Every screen in this lesson is a real recording of nano.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="nano is like Notepad inside the terminal: the title bar on top, your text in the middle, a status line, and two lines of shortcuts at the bottom.">'
       + label_box(20, 16, 600, 26, ['GNU nano 7.2          app.conf *          ← title bar: file name, * = changed'], 'acc', 9)
       + label_box(20, 46, 600, 70, ['port=8080', 'host=localhost         ← your text: just type, arrows to move', 'user=admin'], 'card', 9)
       + label_box(20, 120, 600, 22, ['[ Wrote 3 lines ]          ← status line: messages and questions'], 'green', 9)
       + label_box(20, 146, 600, 36, ['^G Help  ^O Write Out  ^W Where Is  ^K Cut  ^X Exit  ^U Paste', '← shortcut list: ^ = Ctrl, M- = Alt'], 'violet', 9)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('nano at four depths', [
    ('v', 'No jargon: Notepad inside the terminal', '      <p>nano is like Notepad, but inside the black terminal window.</p>' + pic + '''
      <ul>
        <li>You open a file, move with the arrow keys and type, exactly like Notepad.</li>
        <li>There is no mouse menu, so the menu is printed at the bottom: <code>^O</code> means hold Ctrl and press O.</li>
        <li>Two keys are enough to start: <b>Ctrl+O</b> to save, <b>Ctrl+X</b> to exit.</li>
      </ul>'''),
    ('b', 'The keys you will use every day', '''      <ul>
        <li><code>nano file</code> opens (or creates, on save) a file. Arrows, Home, End, PgUp, PgDn move.</li>
        <li><b>Ctrl+O</b> then Enter saves (“Write Out”); <b>Ctrl+X</b> exits, asking Y/N if there are unsaved changes.</li>
        <li><b>Ctrl+K</b> cuts the whole line, <b>Ctrl+U</b> pastes it (“uncut”). Several Ctrl+K in a row cut several lines.</li>
        <li><b>Ctrl+W</b> searches (“Where is”), <b>Alt+W</b> finds the next match. <b>Ctrl+\\</b> replaces.</li>
        <li><b>Alt+U</b> undo, <b>Alt+E</b> redo. <b>Ctrl+G</b> shows the help page.</li>
      </ul>'''),
    ('i', 'Selecting, line numbers and options', '''      <ul>
        <li><b>Alt+A</b> starts a selection (mark), move the cursor, then Ctrl+K cuts it or <b>Alt+6</b> copies it.</li>
        <li><b>Ctrl+_</b> (or Alt+G) goes to a line number: perfect when an error says “line 42”. <code>nano +42 file</code> opens there.</li>
        <li><b>Alt+#</b> toggles line numbers; <code>nano -l</code> starts with them. <code>-B</code> keeps a backup <code>file~</code>; <code>-v</code> opens read-only.</li>
        <li><b>Ctrl+R</b> inserts another file; <b>Ctrl+T</b> runs a command and can insert its output.</li>
        <li><code>Ctrl+S</code> also saves in modern nano (no question); <code>Ctrl+O</code> lets you change the name first.</li>
      </ul>'''),
    ('a', 'Behind the screen: buffers, sudoedit and settings', '''      <ul>
        <li>nano loads the file into memory (a <b>buffer</b>); nothing on disk changes until you write it out. The <code>*</code> in the title bar means the buffer differs from the file.</li>
        <li>On save, nano rewrites the file in place (same inode, permissions kept). With <code>-B</code> it first copies the old version to <code>file~</code>.</li>
        <li><code>sudo nano /etc/x</code> runs the whole editor as root (root’s settings, risky). <code>sudoedit /etc/x</code> copies the file to a temp file, runs <b>your</b> editor as you, and copies it back as root: safer, and the preferred way.</li>
        <li>Settings live in <code>~/.nanorc</code> (e.g. <code>set linenumbers</code>, <code>set tabsize 4</code>, <code>set autoindent</code>); syntax colours come from <code>/usr/share/nano/*.nanorc</code>.</li>
        <li>Programs such as crontab, git, sudoedit and visudo open the editor named in <code>$VISUAL</code> / <code>$EDITOR</code>; <code>export EDITOR=nano</code> in ~/.bashrc picks nano.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What nano is</h2>
''' + def_block(
    '<b>GNU nano</b> is a small, modeless text editor for the terminal. Text is typed directly; commands are given with Ctrl and Alt (Meta) key combinations, the most important of which are listed in two shortcut lines at the bottom of the screen. It edits a copy of the file in memory and writes it to disk when you save.',
    'nano = Notepad in the terminal. Type to edit, <b>Ctrl+O</b> save, <b>Ctrl+X</b> exit.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Buffer', 'The copy of the file in nano’s memory.'),
    ('Write Out', 'nano’s word for Save (Ctrl+O).'),
    ('^ and M-', 'Ctrl and Meta (Alt, or Esc then the key).'),
    ('Mark', 'The start of a selection (Alt+A).'),
    ('Modeless', 'Keys always type text; commands use Ctrl/Alt (unlike vim).'),
    ('sudoedit', f'Edit a root file as yourself. {gl("sudo", "Glossary →")}'),
    ('EDITOR', f'Variable naming your default editor. {gl("shell-variable-vs-environment-variable", "Glossary →")}'),
    ('.nanorc', f'nano’s settings file in your home. {gl("startup-files-bashrc-profile", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('nano', '“nano’s another editor”', 'A free replacement for Pico (1999).'),
    ('pico', 'Pine composer', 'The editor of the Pine e-mail program.'),
    ('^O', 'write Out', 'Save.'),
    ('^W', 'Where is', 'Search.'),
    ('^K / ^U', 'Kut / Uncut', 'Cut and paste.'),
    ('^X', 'eXit', 'Close nano.'),
    ('^_', 'go to line', 'Also Alt+G.'),
    ('M-', 'Meta key', 'Alt on PCs; or press Esc first.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Open / create', '<code>nano notes.txt</code>'),
    ('Save · Exit', '<b>Ctrl+O</b> Enter · <b>Ctrl+X</b>'),
    ('Cut · Paste line', '<b>Ctrl+K</b> · <b>Ctrl+U</b>'),
    ('Search · Replace', '<b>Ctrl+W</b> · <b>Ctrl+\\</b>'),
    ('Go to line', '<b>Ctrl+_</b> or <code>nano +42 file</code>'),
    ('System files', '<code>sudoedit /etc/hosts</code>'),
]) + '\n' + lv + didyou('nano started in 1999 as “TIP” (This Isn’t Pico), a free clone of the Pico editor, whose licence was not fully free. It was renamed nano (a pun: nano is 1000 times bigger than pico) and became the default editor on Ubuntu and Debian.') + '''
EXAM> “How do you edit a file in the terminal and save it?” → nano file, edit, Ctrl+O + Enter to save, Ctrl+X to exit (answer Y/N when asked); mention vi/vim as the alternative available everywhere, and sudoedit for system files.
''' + qc('What does the <code>*</code> after the file name in nano’s title bar mean?', 'The buffer has unsaved changes. After Ctrl+O it disappears.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to start nano</h2>
''' + table(['Command', 'What it does', 'When to use it'], [
    ['<code>nano file</code>', 'open, or create when you save', 'everyday editing'],
    ['<code>nano +42 file</code>', 'open at line 42', 'an error message names a line'],
    ['<code>nano -l file</code>', 'show line numbers', 'code, configs'],
    ['<code>nano -B file</code>', 'keep a backup <code>file~</code> on save', 'risky edits'],
    ['<code>nano -v file</code>', 'view only (read-only)', 'look without risk'],
    ['<code>nano -m file</code>', 'mouse support', 'clicking in desktop terminals'],
    ['<code>nano -w file</code>', 'no hard-wrapping of long lines', 'configs with long lines'],
    ['<code>sudoedit /etc/file</code>', 'edit a root-owned file as yourself', 'system configuration'],
    ['<code>EDITOR=nano crontab -e</code>', 'use nano for another program', 'cron, git commit, visudo'],
], minw=560) + mistake('sudo nano /etc/ssh/sshd_config', 'sudoedit /etc/ssh/sshd_config',
                       'sudo nano runs the whole editor as root with root’s settings; a plugin or a typo in a file name can do damage as root. sudoedit edits a temporary copy as you and writes it back with root rights.') + qc('An error says “syntax error on line 37 of app.conf”. How do you open nano right there?', '<code>nano +37 app.conf</code> (inside nano: Ctrl+_ 37 Enter).') + '''
</section>
'''

# ---------------------------------------------------------------- 4. key cards
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each group of keys explained, then used in every field</h2>
  <p id="commands">Every screen below is a <b>real recording</b>: nano 7.2 was run in a terminal on Ubuntu 24.04, the keys were sent one by one, and the screen was captured. The demo file <code>app.conf</code> has three lines: <code>port=80</code>, <code>host=localhost</code>, <code>user=admin</code>.</p>
''' + cmdcard_u(['every edit: type, save, exit', 'leaving without saving after a mistake', 'saving under a new name (Ctrl+O lets you change it)'],
               ['you want to look only (use less or nano -v)', 'a huge file of many GB (use less, head, tail)'])(
    'save', 'Ctrl+O · Ctrl+X', 'save and exit',
    'Type to edit. <b>Ctrl+O</b> writes the buffer to the file (press Enter to confirm the name). <b>Ctrl+X</b> exits; if there are unsaved changes nano asks <b>Y</b> (save), <b>N</b> (discard) or Ctrl+C (cancel).',
    'nano FILE  →  type  →  Ctrl+O  Enter  →  Ctrl+X', 'change',
    [('Ctrl+O, Enter', 'save (Write Out) under the shown name', 'save often'),
     ('Ctrl+O, new name, Enter', 'save as a different file', 'keep the original'),
     ('Ctrl+S', 'save without questions', 'quick save'),
     ('Ctrl+X', 'exit (asks if unsaved)', 'done'),
     ('Ctrl+X, N', 'exit and throw away changes', 'undo everything'),
     ('Ctrl+X, Y, Enter', 'save and exit in one go', 'the usual end'),
     ('Ctrl+C', 'cancel the current question', 'pressed a key by mistake')],
    dict(cmd='nano app.conf\n# then press: Down  End  type 8080 … Ctrl+O', rec=NS(['Up', 'End', 'BSpace', 'BSpace', '-l 8080', 'C-o']), note='Real screen: line 1 changed, <code>*</code> in the title (unsaved), and nano asks for the file name. Enter confirms.'),
    [('sys', [
        NI('Change the port and save: the * disappears and nano confirms.', 'End  ⌫⌫ 8080  Ctrl+O  Enter', ['End', 'BSpace', 'BSpace', '-l 8080', 'C-o', 'Enter'],
           '“[ Wrote 3 lines ]” is your proof that the file on disk changed.'),
        NI('Changed your mind: exit without saving.', 'x  Ctrl+X  (question)', ['-l x', 'C-x'],
           'Answer N to discard. The file on disk is exactly as before.')]),
     ('dev', [
        NI('Save a copy under a new name before experimenting.', 'Ctrl+O, change name to app.conf.new, Enter', ['C-o', 'C-u', '-l app.conf.new', 'Enter'],
           'The original stays untouched; nano now edits app.conf.new.')]),
     ('qa', [
        dict(situation='Check what nano really wrote, from the shell afterwards.', cmd=CONF + "\nprintf 'port=8080\\nhost=localhost\\nuser=admin\\n' > app.conf   # what nano saved\ncat -A app.conf",
             why='cat -A shows every line ends with $ (Linux line endings) and no hidden characters were added (Lesson 3.5).')]),
    ],
    anat=anatomy([('nano', 'cmd', 'command'), ('-l -B', 'opt', 'line numbers, backup'), ('+42', 'opt', 'start at line 42'), ('app.conf', 'arg', 'file')], 'In the shortcut list, <code>^X</code> = Ctrl+X and <code>M-U</code> = Alt+U (or Esc then U).')
) + cmdcard_u(['moving lines (Ctrl+K then Ctrl+U somewhere else)', 'deleting whole lines quickly', 'copying a block with Alt+A and Alt+6'],
               ['changing one word (just use Backspace and type)', 'huge moves between files (use cat, Lesson 3.5)'])(
    'cut', 'Ctrl+K · Ctrl+U', 'cut and paste lines',
    '<b>Ctrl+K</b> cuts the whole current line (or the selected text). Pressing it several times cuts several lines into one clipboard. <b>Ctrl+U</b> pastes (“uncuts”) at the cursor.',
    'Ctrl+K (cut)  ·  Ctrl+U (paste)  ·  Alt+A (mark) · Alt+6 (copy)', 'change',
    [('Ctrl+K', 'cut the current line', 'delete or move a line'),
     ('Ctrl+K ×3', 'cut three lines together', 'move a block'),
     ('Ctrl+U', 'paste what was cut', 'put it somewhere else'),
     ('Alt+A', 'start / stop selecting (mark)', 'part of a line, many lines'),
     ('Alt+6', 'copy the line or selection', 'duplicate'),
     ('Alt+U / Alt+E', 'undo / redo', 'mistakes')],
    dict(cmd='nano app.conf\n# then press: Ctrl+K  Down  Ctrl+U', rec=NS(['C-k', 'Down', 'C-u']), note='Line 1 was cut and pasted below host: port and host changed places.'),
    [('dev', [
        NI('Duplicate a line to make a similar one.', 'Alt+6 (copy)  Ctrl+U (paste)', ['M-6', 'C-u'],
           'Copy then paste gives two identical lines; then change the copy.')]),
     ('sys', [
        NI('Delete the user line completely.', 'Down Down  Ctrl+K', ['Down', 'Down', 'C-k'],
           'Ctrl+K on a line removes it. Alt+U brings it back if needed.'),
        NI('Oops: undo the cut.', 'Ctrl+K  Alt+U', ['C-k', 'M-u'],
           'Alt+U undoes; nano can undo many steps.')]),
    ]
) + cmdcard_u(['finding a setting in a long config', 'changing one value everywhere (replace all)', 'jumping to the line from an error message'],
               ['searching in many files at once (use grep, Lesson 6.1)', 'complex patterns (nano supports regex with Alt+R, but sed is easier, Lesson 6.4)'])(
    'search', 'Ctrl+W · Ctrl+\\ · Ctrl+_', 'search, replace, go to line',
    '<b>Ctrl+W</b> (Where is) finds text; <b>Alt+W</b> repeats. <b>Ctrl+\\</b> replaces: it asks for the text, the replacement, then for each match <b>Y</b>es, <b>N</b>o or <b>A</b>ll. <b>Ctrl+_</b> jumps to a line number.',
    'Ctrl+W text Enter  ·  Ctrl+\\ old Enter new Enter A  ·  Ctrl+_ N Enter', 'change',
    [('Ctrl+W', 'search forward', 'find a setting'),
     ('Alt+W', 'next match', 'repeat the search'),
     ('Ctrl+Q', 'search backward', 'go up'),
     ('Ctrl+\\', 'replace (Y / N / A)', 'change values'),
     ('Alt+C / Alt+R (in the search bar)', 'case-sensitive / regex', 'precise searches'),
     ('Ctrl+_ or Alt+G', 'go to line (and column)', 'error messages'),
     ('Alt+\\ / Alt+/', 'first / last line', 'jump to start / end')],
    dict(cmd='nano app.conf\n# then press: Ctrl+\\  localhost Enter  db.internal Enter  A', rec=NS(["'C-\\'", '-l localhost', 'Enter', '-l db.internal', 'Enter', 'a']), note='“[ Replaced 1 occurrence ]”, and the * shows the change is not saved yet.'),
    [('dba', [
        NI('Find the user line in a database config.', 'Ctrl+W  user  Enter', ['C-w', '-l user', 'Enter'],
           'The cursor jumps to the match; in a 500-line my.cnf this saves scrolling.')]),
     ('devops', [
        NI('Open a config directly at the line an error reported.', 'nano +3 app.conf', [],
           'The cursor starts on line 3. (Use <code>-l</code> as well to see the numbers.)', cmd='nano -l +3 app.conf')]),
     ('data', [
        NI('Fix a CSV header: rename a column everywhere in the file.', 'Ctrl+\\  amt Enter  amount Enter  A', ["'C-\\'", '-l amt', 'Enter', '-l amount', 'Enter', 'a'],
           'Replace all changes every “amt”; check the count in the status line.', setup="printf 'id,amt\\n1,10\\n2,20\\n' > sales.csv", cmd='nano sales.csv')]),
    ]
) + cmdcard_u(['editing system files (/etc/…)', 'choosing nano for crontab, git and visudo', 'personal settings you want every time'],
               ['a quick look (use less or nano -v)', 'automated changes in scripts (use sed or printf, never an interactive editor)'])(
    'system', 'sudoedit · -B · .nanorc · EDITOR', 'safe editing and settings',
    'How professionals use nano on real servers: edit root-owned files with <code>sudoedit</code>, keep backups with <code>-B</code>, show line numbers, and make nano the editor other tools open.',
    'sudoedit FILE  ·  nano -B -l FILE  ·  ~/.nanorc  ·  export EDITOR=nano', 'change',
    [('sudoedit /etc/hosts', 'edit a root file as yourself', 'system configs'),
     ('nano -B file', 'keep the old version as file~', 'risky edits'),
     ('nano -l / Alt+#', 'line numbers', 'code and configs'),
     ('nano -v file', 'read-only view', 'look safely'),
     ('set linenumbers (~/.nanorc)', 'numbers every time', 'personal setup'),
     ('export EDITOR=nano', 'nano for crontab -e, git, visudo', 'consistent tools')],
    dict(cmd='nano -l app.conf', rec=NS([], cmd='nano -l app.conf'), note='Line numbers on the left. They are not part of the file.'),
    [('sec', [
        dict(situation='Edit the hosts file as yourself (needs sudo rights).', cmd='sudoedit /etc/hosts',
             typical='[sudo] password for riya:\n  GNU nano 7.2        /var/tmp/hostsXXQk2a.txt\n127.0.0.1 localhost\n127.0.1.1 riya-laptop',
             why='The title shows a temporary copy: you edit as riya, and sudo writes it back to /etc/hosts when you exit.')]),
     ('sys', [
        dict(situation='Keep a backup automatically when editing an important file.', cmd=CONF + "\nprintf 'port=8080\\nhost=localhost\\nuser=admin\\n' > app.conf.new; cp app.conf app.conf~; mv app.conf.new app.conf   # what nano -B does on save\nls app.conf*",
             why='nano -B saves the old version as app.conf~ before writing: a one-step rollback (<code>mv app.conf~ app.conf</code>).')]),
     ('devops', [
        dict(situation='Make nano the editor for crontab, git and other tools.', cmd="echo 'export EDITOR=nano VISUAL=nano' >> ~/.bashrc\ntail -n 1 ~/.bashrc",
             why='After a new login, <code>crontab -e</code> and <code>git commit</code> open nano (Lesson 12.2).'),
        dict(situation='Personal settings in ~/.nanorc.', cmd="printf 'set linenumbers\\nset tabsize 4\\nset tabstospaces\\nset autoindent\\n' > ~/.nanorc\ncat ~/.nanorc",
             why='Line numbers, 4-space indentation for Python and YAML, auto-indent for code.')]),
    ], sudo='for /etc'
) + undo('If an edit went wrong…', [
    ('Before saving:', 'Ctrl+X and answer <b>N</b>: nothing on disk changed. Or Alt+U to undo step by step.'),
    ('After saving:', 'Alt+U still works while nano is open; then save again.'),
    ('After closing:', 'only a backup helps: <code>file~</code> (nano -B), your <code>cp file file.bak</code> (Lesson 3.2), or git.'),
    ('nano says the file is locked / being edited:', 'another nano has it open (a <code>.file.swp</code> lock). Close the other one, or answer the question carefully.'),
    ('Pressed Ctrl+Z:', 'nano was suspended, not closed: type <code>fg</code> to return (Lesson 11.3).'),
]) + screens_block('A complete edit, screen by screen', 'Riya changes the port, saves and exits. Each step shows the real nano screen.',
    CONF, 'nano app.conf', [
        ('End', 'End', 'moves to the end of line 1.'),
        ('Backspace ×2', 'BSpace BSpace', 'deletes “80”: the title shows <code>*</code> (changed).'),
        ('8080', "-l 8080", 'types the new port.'),
        ('Ctrl+O', 'C-o', 'asks for the file name to write.'),
        ('Enter', 'Enter', 'saves: “[ Wrote 3 lines ]”, the * is gone.'),
        ('Ctrl+X', 'C-x', 'exits back to the shell (the screen is the shell again).'),
    ], h=9, w=64, after='cat app.conf', hid='screens') + errors('The problems students see with nano. Messages were really produced on our build machine.', [
    dict(cmd='nano --version | head -1\nls -l /etc/hostname | cut -c1-10\ntouch /etc/hostname', meaning='/etc files belong to root. nano opens them read-only for you and shows “[ File ’/etc/hostname’ is unwritable ]”; saving fails with “Permission denied”.', fix='Use <code>sudoedit /etc/hostname</code> (if you are allowed).'),
    dict(cmd='mkdir -p cfg && touch cfg/a.conf && chmod -w cfg/a.conf && echo x >> cfg/a.conf', meaning='The file itself is write-protected; nano will say “Permission denied” when you save.', fix='Save under another name with Ctrl+O, or fix permissions (Lesson 9.2) if it is your file.'),
]) + screens_block('Real screens: editing a file you are not allowed to change', 'Riya opens /etc/hostname as a normal user, types a letter and tries to save.',
    '', 'nano /etc/hostname', [
        ('x', "-l x", 'changes the buffer (the * appears), even though the file is protected.'),
        ('Ctrl+O', 'C-o', 'asks for the name.'),
        ('Enter', 'Enter', 'fails: “Error writing … Permission denied”. Nothing on disk changed.'),
    ], h=9, w=64) + qc('You opened the wrong file and typed a few characters. How do you leave without changing it?', 'Ctrl+X, then N (do not save).') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animation
ns = lambda steps, note, tone='blue': (term(14, 12, 332, 132, tmux_screens(CONF, 'nano app.conf', steps, 46, 9)[-1].split('\n')[:9], title='nano', size=6.8, step=13.2, prompt='') + cap(note, '', tone, y=150, h=34))
see = [ns([], 'nano opens app.conf; shortcuts at the bottom.'),
       ns(['End', 'BSpace', 'BSpace', '-l 8080'], 'Typed 8080: title shows * (unsaved).', 'amber'),
       ns(['End', 'BSpace', 'BSpace', '-l 8080', 'C-o'], 'Ctrl+O: “File Name to Write”.', 'blue'),
       ns(['End', 'BSpace', 'BSpace', '-l 8080', 'C-o', 'Enter'], 'Enter: “Wrote 3 lines”, * gone.', 'green'),
       ns(['-l x', 'C-x'], 'Other case: Ctrl+X with changes asks Y/N.', 'red')]
def buf(hl, note, tone='blue', disk='port=80'):
    o = label_box(14, 20, 150, 60, ['nano buffer (memory)', 'port=8080' if hl else 'port=80'], 'amber' if hl else 'card', 9)
    o += label_box(196, 20, 150, 60, ['app.conf (disk)', disk], 'green' if disk.endswith('8080') else 'card', 9)
    o += arrow(164, 50, 196, 50, 'ink3')
    return o + t(180, 120, note, 8.8, tone, bold=True)
behind = [buf(False, 'nano reads the file into a buffer.'),
          buf(True, 'You change only the buffer.', 'amber'),
          buf(True, 'Nothing on disk yet: the * warns you.', 'amber'),
          buf(True, 'Ctrl+O writes the buffer to the disk.', 'green', 'port=8080'),
          buf(True, 'Exit with N = buffer thrown away, disk unchanged.', 'red')]
two = anim_two('Buffer vs file: what Ctrl+O really does', 'Memory and disk',
               'Real nano screens: opening app.conf, typing 8080 with an unsaved star, Ctrl+O asking for the name, Enter writing 3 lines, and Ctrl+X asking to save modified buffer.',
               'nano edits a buffer in memory; the disk file changes only when Ctrl+O writes it; exiting without saving discards the buffer.', see, behind,
               ['nano opens the file and lists shortcuts.',
                'After typing, the title bar shows <code>*</code>: changed, not saved.',
                'Ctrl+O asks which file name to write.',
                'Enter writes it: “[ Wrote 3 lines ]” and the star disappears.',
                'Ctrl+X with unsaved changes always asks first.'],
               ['The file is copied into nano’s memory (the buffer).',
                'Every key changes only the buffer.',
                'The disk still has the old content until you save.',
                'Write Out copies the buffer to the file.',
                'Answering N on exit discards the buffer; the disk is unchanged.'])

dx = dissect('Layer by layer: what happens when you save',
    'From the key you press to the file on disk. Each layer has a real command and its output from our build machine.', [
    dict(key='key', name='Ctrl+O', sub='a control character',
         why='Terminals send keys as bytes.',
         how='Ctrl+O is byte 15 (0x0F); nano reads it and starts Write Out.',
         impl='The terminal driver passes keys to nano in raw mode.', used='Every terminal program.',
         cmd="printf '\\x0f' | od -An -tx1"),
    dict(key='buf', name='Buffer', sub='lines in memory',
         why='Editing in memory is fast and undoable.',
         how='nano keeps a list of lines and an undo history.',
         impl='nano’s own data structures.', used='All editors.',
         cmd="nano --version | head -1"),
    dict(key='write', name='Write', sub='same file, new content',
         why='The file keeps its permissions and inode.',
         how='nano opens the file for writing and replaces its content.',
         impl='open() with O_TRUNC, write(), close().', used='Saving.',
         cmd=CONF + "; stat -c 'inode=%i size=%s' app.conf; printf 'port=8080\\nhost=localhost\\nuser=admin\\n' > app.conf; stat -c 'inode=%i size=%s' app.conf"),
    dict(key='perm', name='Permissions', sub='who may write',
         why='System files must be protected.',
         how='Writing needs w permission on the file; root files need sudo / sudoedit.',
         impl='Kernel permission checks (Lesson 9.1).', used='/etc configs.',
         cmd="stat -c '%A %U %n' /etc/hosts"),
], hint='From your key to the disk. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Buffer, star and Write Out</h2>
  <p>Left: real nano screens (small terminal). Right: memory vs disk.</p>
''' + two + dx + qc('You typed changes and the title shows <code>*</code>. Has the file on disk changed?', 'No. Only nano’s buffer has; the file changes when you press Ctrl+O (or answer Y when exiting).') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>nano at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ sudoedit', 'prompt'), ('/etc/hosts', 'acc')], title='admin', size=6.4, step=12),
              '1. Quick config fixes on servers', 'Admins change one setting over SSH, save, and restart the service (Lesson 17.2).', ['Problem', '*nano', 'fixed']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['crontab -e', 'EDITOR=nano'], 'green', 8.6), '2. Schedules and commits',
    'crontab -e, git commit and visudo open the default editor; many teams set it to nano for beginners.', ['crontab -e', '*nano', 'saved']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ nano', 'prompt'), ('+37 app.yml', 'acc')], title='devops', size=6.4, step=12),
    '3. Fixing YAML and .env files', 'DevOps engineers jump to the line in an error message and fix indentation in YAML.', ['Error line 37', '*nano +37', 'deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Ctrl+\\', 'replace all'], 'amber', 8.6), '4. Small data fixes',
    'Analysts fix a header or a few values in a small CSV directly on the server.', ['Bad header', '*replace', 'load ok']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('nano is interactive, so these one-liners prepare or check files around an edit. All really run on our build machine.', [
    dict(level='b', title='Back up, then edit', scenario='Always keep a copy before editing.', setup=CONF,
         cmd='cp -v app.conf app.conf.bak   # then: nano app.conf',
         explain='A copy is the simplest undo (Lesson 3.2).'),
    dict(level='b', title='Which editor will tools open?', scenario='Check EDITOR and VISUAL.',
         cmd='echo "EDITOR=${EDITOR:-not set} VISUAL=${VISUAL:-not set}"',
         explain='Not set → tools fall back to a default (often nano on Ubuntu, vi elsewhere).'),
    dict(level='i', title='What did my edit change?', scenario='Compare after editing.', setup=CONF + "; cp app.conf app.conf.bak; printf 'port=8080\\nhost=localhost\\nuser=admin\\n' > app.conf",
         cmd='diff app.conf.bak app.conf',
         explain='diff shows the changed line (Lesson 6.3).', expect='any'),
    dict(level='a', title='No editor at all in a script', scenario='Change the port without opening an editor.', setup=CONF,
         cmd="sed -i 's/^port=.*/port=8080/' app.conf && cat app.conf",
         explain='For automation never open an interactive editor; use sed (Lesson 6.4).'),
]) + which('Choosing how to edit.', [
    ('Change one line by hand', 'nano file', 'Easy, keys on screen.', 'Editing with echo > (overwrites).'),
    ('Root-owned config', 'sudoedit file', 'Safe, your settings.', 'sudo nano.'),
    ('Look only', 'less / nano -v', 'No risk.', 'Opening in edit mode on production.'),
    ('Go to an error line', 'nano +N file', 'Direct.', 'Scrolling and counting.'),
    ('Same change in a script', 'sed -i', 'Automatic.', 'Interactive editors in scripts.'),
    ('Big file (GB)', 'less, head, tail', 'Fast.', 'nano loads it all into memory.'),
    ('Server without nano', 'vi / vim (4.2)', 'Always installed.', 'Panic.'),
]) + keys('nano keys, all on one screen (^ = Ctrl, M- = Alt).', [
    ('^O  ^S', 'save (with / without name question)', '^O Enter'),
    ('^X', 'exit (asks if unsaved)', '^X Y Enter'),
    ('^K  ^U  M-6', 'cut line, paste, copy', '^K ↓ ^U'),
    ('M-A', 'start / stop selection', 'M-A ↓↓ ^K'),
    ('^W  M-W  ^Q', 'search, next, backward', '^W port'),
    ('^\\', 'replace (Y/N/A)', '^\\ 80 ⏎ 8080 ⏎ A'),
    ('^_  M-\\  M-/', 'go to line, first line, last line', '^_ 37'),
    ('M-U  M-E', 'undo, redo', 'M-U'),
    ('M-#  ^G', 'line numbers, help', 'M-#'),
]) + scriptit('safe-edit.sh', 'A wrapper professionals use around manual edits: backup first, open the editor, then show what changed. (Here the “edit” is simulated with sed so the script can run unattended.)',
'''#!/bin/bash
f=${1:-app.conf}
printf 'port=80\\nhost=localhost\\n' > "$f"          # demo file
cp -p "$f" "$f.bak"                                # 1. backup
${EDITOR_DEMO:-sed -i s/80/8080/} "$f"             # 2. real use: ${EDITOR:-nano} "$f"
if cmp -s "$f" "$f.bak"; then echo "no changes"; else echo "changes:"; diff "$f.bak" "$f" || true; fi''',
'<p>In real life line 2 is <code>${EDITOR:-nano} "$f"</code>: it opens your editor and waits until you exit.</p>') + puzzle_answer('Yes, it saved. In nano 7, <b>Ctrl+S</b> saves the file without asking for a name (older nano versions used Ctrl+S for nothing or for flow control). After Ctrl+S the * disappears from the title bar, so Ctrl+X exits at once. If nano still asks “Save modified buffer?”, the save did not happen (for example in an old nano, or if the terminal swallowed Ctrl+S): answer Y. Ctrl+O is the safe key on every version.') + qc('Your colleague wants nano to open when she runs <code>crontab -e</code>. What does she add to ~/.bashrc?', '<code>export EDITOR=nano</code> (and VISUAL=nano).') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../03-files-and-directories/01-creating-files-and-folders-touch-mkdir-and-rmdir/">Lesson 3.1</a>: creating files.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
