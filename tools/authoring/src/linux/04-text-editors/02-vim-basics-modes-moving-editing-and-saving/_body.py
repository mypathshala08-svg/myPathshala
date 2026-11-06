import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

VL = 'Real run: the keys were typed into vim 9.1 on Ubuntu 24.04; the file after saving'
T4 = 'line 1\nline 2\nline 3\nline 4\n'
CONF = 'port=80\nhost=localhost\nuser=admin\n'
def VI(sit, content, keys, why, name='notes.txt'):
    shown = keys.replace('<CR>', '⏎')
    return dict(situation=sit, cmd=f'vim {name}\n# keys: {shown}', rec=(VL, vimrun(content, keys, name)), why=why)
def VB(content, keys, name='notes.txt', note=''):
    shown = keys.replace('<CR>', '⏎')
    return dict(cmd=f'vim {name}\n# keys: {shown}', rec=(VL, vimrun(content, keys, name)), note=note)
VSET = "printf 'port=80\\nhost=localhost\\nuser=admin\\n' > app.conf"

HOOK = hook('Riya opens a config on a server with <code>vi</code> and types her change. Nothing appears; the cursor jumps, a line vanishes, and she cannot even quit. Every Linux and Unix machine has vi, including minimal servers and rescue systems where nano is missing. Once you understand <b>modes</b>, vim stops being scary and becomes the fastest editor you will ever use.',
    ['understand vim’s modes and always know which one you are in (Normal, Insert, Command-line, Visual)',
     'move by character, word, line and file (<code>h j k l w b 0 $ gg G</code>)',
     'insert, delete, copy, paste, undo and redo (<code>i a o</code>, <code>x dd yy p</code>, <code>u Ctrl+R</code>)',
     'save and quit in every situation (<code>:w :q :wq :q! ZZ</code>), and search with <code>/</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'why typing did not work'),
    ('decide', 'Which key when?', 3, 'the survival keys'),
    ('definition', 'Modes explained', 5, 'simple meaning + 4 depths'),
    ('commands', 'Keys by field', 15, 'verified results, your field'),
    ('screens', 'Real vim screens', 4, 'INSERT, E37, :wq'),
    ('errors', 'Errors decoded', 3, 'E37, E45, swap files'),
    ('run', 'Run on your PC', 4, 'vimtutor'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'screens', 'lab'])
DECIDE = decide('Survival keys (Esc first if unsure: it always returns to Normal mode)', [
    ('Start typing text', 'i', 'Insert mode; Esc to stop'),
    ('Stop typing', 'Esc', 'back to Normal mode'),
    ('Save and quit', ':wq  Enter  (or ZZ)', 'from Normal mode'),
    ('Quit without saving', ':q!  Enter', 'throw changes away'),
    ('Just save', ':w  Enter', 'keep editing'),
    ('Move down / up', 'j / k', 'not the other way round!'),
    ('Delete a line', 'dd', 'it is also copied'),
    ('Undo / redo', 'u / Ctrl+R', 'many steps'),
    ('Search', '/word  Enter, then n', 'N = backwards'),
    ('Go to line 42', ':42  Enter  (or 42G)', 'gg top, G bottom'),
])

cmap = concept_map(
    [('4.1', 'nano', 'editing basics'), ('3.5', 'less', 'same / n G keys'), ('2.5', 'man pages', 'also use / and q')],
    ['Normal, Insert, Command-line and Visual mode', 'moving: h j k l, w b e, 0 $, gg G, :N', 'editing: i a o, x dd yy p, u Ctrl+R, r cw', 'saving and quitting: :w :q :wq :q! ZZ', 'searching: / ? n N'],
    [('4.3', 'vim power use', 'replace, blocks, .vimrc'), ('6.4', 'sed', 'vim’s :s comes from sed'), ('17.4', 'cron', 'crontab -e often opens vi'), ('21.3', 'Interviews', '“how do you exit vi?”')],
    'vi is on every Unix-like system, including tiny containers and rescue shells. Certification exams (RHCSA) expect it.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ vi app.conf', ('port=80', 'out'), ('(types: change port)', 'dim'), ('…cursor jumps, a line is gone', 'err'), ('Esc  u  i … Esc  :wq', 'acc'), ('"app.conf" 3L, 32B written', 'out')], title='riya@app-01', size=7.6, step=15)
      + t(352, 36, 'vim has modes:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• Normal: keys are commands', '• Insert: keys type text', '• i = Insert, Esc = Normal', '• :wq = save and quit', '• u = undo the accident'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Why vi ignored Riya’s typing</h2>
  <div class="story">
''' + puzzle('Riya opened a file in vi and typed the word <code>change</code>. The cursor moved and part of the file changed strangely. In Normal mode, which letters of “change” are commands, and which one finally put her into typing mode? (The answer uses keys from this lesson.)') + '''
    <p class="narration">A minimal production server has no nano. Riya opens the config with <code>vi</code>, as the runbook says, and starts typing.</p>
''' + scene('A terminal: vi opens app.conf; typing does not insert text but moves the cursor and deletes a line; after Esc, u, i, typing, Esc and :wq the file is written.', sc,
            'In vim, keys are <tspan font-weight="700" class="s-acc">commands</tspan> until you press i.') + '''
R> I typed and it went crazy!
A> vim starts in <b>Normal mode</b>, where every key is a command: <code>h j k l</code> move, <code>d</code> deletes, <code>c</code> changes. Press <b>Esc</b>, then <b>u</b> to undo the damage.
K> And to actually type?
A> Press <b>i</b> (insert). The bottom shows <code>-- INSERT --</code>; now keys are text. <b>Esc</b> returns to Normal mode, and <code>:wq</code> saves and quits. Today you learn the four modes and the 30 keys that cover daily work, every result verified by really typing the keys into vim.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 230" role="img" aria-label="vim modes as a car gearbox: Normal mode is neutral in the centre; i, a, o go to Insert; colon goes to Command-line; v goes to Visual; Esc always returns to Normal.">'
       + label_box(240, 86, 160, 52, ['NORMAL', 'keys = commands'], 'acc', 10)
       + label_box(20, 14, 170, 52, ['INSERT', 'keys type text'], 'green', 9.6)
       + label_box(450, 14, 170, 52, ['COMMAND-LINE  :', ':w  :q  :wq  :42'], 'blue', 9.6)
       + label_box(20, 160, 170, 52, ['VISUAL  v V Ctrl+V', 'select text'], 'violet', 9.6)
       + label_box(450, 160, 170, 52, ['press Esc', 'from anywhere → NORMAL'], 'amber', 9.6)
       + arrow(240, 100, 190, 52, 'ink3') + t(205, 92, 'i a o', 9, 'green', bold=True)
       + arrow(400, 100, 450, 52, 'ink3') + t(432, 92, ':', 11, 'blue', bold=True)
       + arrow(240, 126, 190, 172, 'ink3') + t(205, 158, 'v', 10, 'violet', bold=True)
       + arrow(450, 186, 400, 132, 'ink3') + t(436, 158, 'Esc', 9, 'amber', bold=True)
       + '<text x="632" y="224" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('vim at four depths', [
    ('v', 'No jargon: a car with gears', '      <p>vim is like a car gearbox: the same pedal does different things in different gears.</p>' + pic + '''
      <ul>
        <li><b>Normal</b> mode is “neutral”: keys give orders (move, delete, copy). vim starts here.</li>
        <li><b>Insert</b> mode is “drive”: keys type letters. Enter it with <code>i</code>.</li>
        <li><b>Esc</b> always brings you back to neutral. When lost: Esc, Esc, then decide.</li>
      </ul>'''),
    ('b', 'The keys you will use every day', '''      <ul>
        <li><code>vim file</code> opens; <code>i</code> insert, type, <code>Esc</code>; <code>:wq</code> Enter saves and quits; <code>:q!</code> quits without saving.</li>
        <li>Move: <code>h</code> left, <code>j</code> <b>down</b>, <code>k</code> <b>up</b>, <code>l</code> right (arrows also work).</li>
        <li><code>x</code> deletes a character, <code>dd</code> a line, <code>yy</code> copies a line, <code>p</code> pastes below.</li>
        <li><code>u</code> undo, <code>Ctrl+R</code> redo.</li>
        <li><code>/word</code> Enter searches, <code>n</code> next match.</li>
      </ul>'''),
    ('i', 'Faster: words, counts and combinations', '''      <ul>
        <li>Enter Insert mode in the right place: <code>i</code> before the cursor, <code>a</code> after, <code>I</code> line start, <code>A</code> line end, <code>o</code> / <code>O</code> new line below / above.</li>
        <li>Move by word <code>w b e</code>, line start/end <code>0 $</code>, file <code>gg G</code>, line number <code>:42</code> or <code>42G</code>.</li>
        <li><b>Counts</b>: <code>3dd</code> deletes 3 lines, <code>5j</code> moves 5 down.</li>
        <li><b>Operator + motion</b>: <code>d</code>, <code>c</code>, <code>y</code> combine with motions: <code>dw</code> delete word, <code>cw</code> change word, <code>d$</code> to line end, <code>y</code> + motion copies. <code>r</code> replaces one character.</li>
        <li><code>.</code> repeats the last change (more in 4.3).</li>
      </ul>'''),
    ('a', 'Behind the screen: vi, vim, buffers and swap files', '''      <ul>
        <li>On Ubuntu, <code>vi</code> starts vim (often “vim.tiny” on minimal installs, with fewer features); RHEL ships vi (vim-minimal) and vim (vim-enhanced). <code>:version</code> shows which.</li>
        <li>vim edits a <b>buffer</b>; <code>:w</code> writes it. While editing it keeps a <b>swap file</b> <code>.file.swp</code> for crash recovery; if vim or SSH dies, the next open offers to recover.</li>
        <li><code>:wq</code> always writes; <code>ZZ</code> and <code>:x</code> write only if changed (keep the file date when nothing changed).</li>
        <li>The command-line mode is the old <b>ex</b> editor: <code>:s</code>, <code>:g</code>, <code>:w</code>, ranges. vi was built on top of ex (1976).</li>
        <li><code>vim -u NONE</code> starts without settings; <code>:set nocompatible</code> gives vim (not vi) behaviour; settings go in <code>~/.vimrc</code> (Lesson 4.3).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>vi, vim and modes</h2>
''' + def_block(
    '<b>vi</b> is the standard screen editor of Unix, required by POSIX; <b>vim</b> (Vi IMproved) is the enhanced version used on Linux. It is a <b>modal</b> editor: in Normal mode keys are commands (move, delete, copy), in Insert mode keys insert text, in Command-line mode (after <code>:</code>) you type ex commands such as <code>:w</code> and <code>:q</code>, and in Visual mode you select text. <code>Esc</code> returns to Normal mode.',
    'Normal mode = commands, Insert mode (<code>i</code>) = typing, <code>Esc</code> = back, <code>:wq</code> = save and quit.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Mode', 'What keys mean right now: commands or text.'),
    ('Normal mode', 'The default: keys are commands.'),
    ('Insert mode', 'Keys type text; shows -- INSERT --.'),
    ('Command-line mode', 'After :, commands like :w :q :42.'),
    ('Operator + motion', 'd, c, y combined with w, $, j…'),
    ('Register', 'Where yanked and deleted text is kept.'),
    ('Swap file', 'Crash-recovery copy: .file.swp.'),
    ('EDITOR', f'Which editor tools open. {gl("shell-variable-vs-environment-variable", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('vi', 'visual', 'The visual mode of the ex editor (Bill Joy, 1976).'),
    ('vim', 'Vi IMproved', 'Bram Moolenaar, 1991.'),
    ('h j k l', 'arrow keys of the ADM-3A', 'Bill Joy’s terminal had arrows printed on these keys.'),
    ('y', 'yank', 'Copy (c was already “change”).'),
    ('p', 'put', 'Paste.'),
    ('u', 'undo', 'Ctrl+R = redo.'),
    ('ZZ', 'sleep (zz)', 'Save if needed and go away.'),
    (':q!', 'quit, no matter what', '! = force.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Type text', '<code>i</code> … <code>Esc</code>'),
    ('Save and quit', '<code>:wq</code> or <code>ZZ</code>'),
    ('Quit, discard', '<code>:q!</code>'),
    ('Move', '<code>h</code> ← <code>j</code> ↓ <code>k</code> ↑ <code>l</code> →'),
    ('Delete / copy / paste line', '<code>dd</code> · <code>yy</code> · <code>p</code>'),
    ('Undo / redo', '<code>u</code> · <code>Ctrl+R</code>'),
]) + '\n' + lv + didyou('The keys h, j, k and l move the cursor because Bill Joy wrote vi in 1976 on a Lear Siegler ADM-3A terminal, which had no separate arrow keys: the arrows were printed on H, J, K and L. The same keyboard had Esc where Tab is today, which is why vi uses Esc so much.') + mistake('j = up, k = down   (as written in some notes)', 'j = down ↓, k = up ↑',
    'Verified by a real run: from line 1, <code>jj</code> then <code>x</code> deletes on line 3; adding <code>k</code> deletes on line 2. Memory trick: <b>j</b> has a tail that hangs <b>down</b>.') + '''
EXAM> “Explain the modes of vi and how to save and quit” → Normal (command) mode, Insert mode (i, a, o; Esc to leave), Command-line mode (:w save, :q quit, :wq save and quit, :q! quit without saving), Visual mode (v); mention dd, yy, p, u and /search.
''' + qc('You are in Insert mode and want to save and quit. Which keys?', '<code>Esc</code>, then <code>:wq</code> and Enter (or Esc then ZZ).') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The four modes and how to switch</h2>
''' + table(['Mode', 'Keys do', 'How to enter', 'Screen shows', 'Leave with'], [
    ['Normal', 'commands: move, delete, copy', 'start of vim; Esc', 'nothing at the bottom', '—'],
    ['Insert', 'type text', '<code>i a o I A O</code>, <code>cw</code>…', '<code>-- INSERT --</code>', '<code>Esc</code>'],
    ['Command-line', 'ex commands', '<code>:</code> (also <code>/</code> <code>?</code> for search)', '<code>:</code> and what you type', 'Enter (run) or Esc (cancel)'],
    ['Visual', 'select text', '<code>v</code> chars, <code>V</code> lines, <code>Ctrl+V</code> block', '<code>-- VISUAL --</code>', '<code>Esc</code> or an operator'],
    ['Replace', 'overwrite text', '<code>R</code>', '<code>-- REPLACE --</code>', '<code>Esc</code>'],
], minw=620) + '''
  <h3>Ways to start vim</h3>
''' + table(['Command', 'What it does'], [
    ['<code>vim file</code> / <code>vi file</code>', 'open (or create on save)'],
    ['<code>vim +42 file</code>', 'open at line 42'],
    ['<code>vim +/port file</code>', 'open at the first “port”'],
    ['<code>view file</code> / <code>vim -R file</code>', 'read-only'],
    ['<code>vimtutor</code>', 'the built-in 30-minute interactive lesson'],
    ['<code>sudoedit file</code> (with EDITOR=vim)', 'edit root files safely'],
], minw=420) + qc('The bottom line shows <code>-- INSERT --</code>. What happens if you press <code>dd</code>?', 'It types the letters “dd” into the file. Commands work only in Normal mode: press Esc first.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. cards
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each group of keys explained, then used in every field</h2>
  <p id="commands">Every result below is <b>real</b>: the keys were typed into vim 9.1 on Ubuntu 24.04 (fed from a key file with <code>vim -s</code>), and the file is shown after saving. The demo file <code>notes.txt</code> has four lines: <code>line 1</code> … <code>line 4</code>; <code>app.conf</code> has <code>port=80</code>, <code>host=localhost</code>, <code>user=admin</code>.</p>
''' + cmdcard_u(['adding text: before, after, at line start or end, on a new line', 'every edit starts with one of these keys', 'Esc when you are done typing'],
               ['you only want to delete or move text (stay in Normal mode)', 'you are not sure which mode you are in (press Esc first)'])(
    'insert', 'i a o · Esc', 'entering and leaving Insert mode',
    'Six keys switch to Insert mode, each at a different place. Type your text, then <b>Esc</b> returns to Normal mode.',
    'i a I A o O  →  type  →  Esc', 'change',
    [('i', 'insert before the cursor', 'fix inside a word'),
     ('a', 'append after the cursor', 'add after a character'),
     ('I', 'insert at the start of the line', 'add a prefix, comment out'),
     ('A', 'append at the end of the line', 'add to a value'),
     ('o', 'open a new line below', 'add a setting'),
     ('O', 'open a new line above', 'add a header'),
     ('Esc', 'back to Normal mode', 'always, after typing')],
    VB(T4, 'iNEW <Esc>:wq<CR>', note='i at the start of line 1, typed “NEW ”, Esc, saved.'),
    [('sys', [
        VI('Add a new setting below the port line.', CONF, 'otimeout=30<Esc>:wq<CR>', '<code>o</code> opens a line below the cursor and enters Insert mode.', 'app.conf'),
        VI('Comment out the user line (prefix #).', CONF, 'GI# <Esc>:wq<CR>', '<code>G</code> to the last line, <code>I</code> inserts at its start.', 'app.conf')]),
     ('dev', [
        VI('Add a semicolon at the end of a line of code.', 'let x = 1\nlet y = 2\n', 'A;<Esc>j.:wq<CR>', '<code>A</code> appends at the end; <code>j.</code> moves down and repeats the last change.', 'main.js')]),
     ('data', [
        VI('Add a header line above the CSV data.', '1,Asha,91\n2,Ravi,78\n', 'Oid,name,marks<Esc>:wq<CR>', '<code>O</code> opens a line above line 1.', 'marks.csv')]),
    ],
    anat=anatomy([('d', 'cmd', 'operator: delete'), ('3', 'opt', 'count'), ('w', 'arg', 'motion: word')], 'Many vim commands are “operator + count + motion”: <code>d3w</code> deletes three words, <code>y$</code> copies to the end of the line.')
) + cmdcard_u(['you know where the cursor must go', 'jumping by words, lines and to the top or bottom', 'going to a line number from an error message'],
               ['long files where you know the text (search with / instead)'])(
    'move', 'h j k l · w b · 0 $ · gg G', 'moving in Normal mode',
    'Move without leaving the home row. Each key moves by a unit: character, word, line, file. A number in front repeats it.',
    '[count] h|j|k|l|w|b|e|0|$  ·  gg  G  :N', 'safe',
    [('h j k l', 'left, down, up, right', 'small moves'),
     ('w / b / e', 'next word start / previous word / word end', 'within a line'),
     ('0 / ^ / $', 'line start / first non-blank / line end', 'edit ends of lines'),
     ('gg / G', 'first line / last line', 'top and bottom'),
     (':42 or 42G', 'go to line 42', 'error messages'),
     ('5j', 'five lines down', 'counts'),
     ('Ctrl+D / Ctrl+U', 'half a page down / up', 'long files')],
    VB(T4, 'jjx:wq<CR>', note='Two <code>j</code> = two lines <b>down</b>: the x deleted the “l” of line 3.'),
    [('qa', [
        VI('Prove the direction of k: down twice, up once.', T4, 'jjkx:wq<CR>', 'The x lands on line 2: k goes <b>up</b>.'),
        VI('Last line, then back to the first.', T4, 'Gggx:wq<CR>', '<code>G</code> to the bottom, <code>gg</code> to the top: x on line 1.')]),
     ('devops', [
        VI('An error says “line 3 of app.conf”: jump there.', CONF, ':3<CR>x:wq<CR>', '<code>:3</code> jumps to line 3 (or open with <code>vim +3 app.conf</code>).', 'app.conf')]),
     ('dev', [
        VI('Change the second word of a line.', 'let total = 10\n', 'wcwsum<Esc>:wq<CR>', '<code>w</code> to the next word, <code>cw</code> changes that word.', 'main.js')]),
    ]
) + cmdcard_u(['deleting characters and lines quickly', 'copying and pasting lines', 'fixing mistakes with undo'],
               ['big moves between files (use :r or the shell)', 'many repeated changes (use :s, Lesson 4.3)'])(
    'edit', 'x dd yy p · u Ctrl+R', 'delete, copy, paste, undo',
    'In Normal mode: <code>x</code> deletes a character, <code>dd</code> a line (and keeps it for pasting), <code>yy</code> copies (yanks) a line, <code>p</code>/<code>P</code> paste below/above. <code>u</code> undoes, <code>Ctrl+R</code> redoes.',
    '[count] x | dd | yy | p | P | r c | u | Ctrl+R | .', 'change',
    [('x', 'delete the character under the cursor', 'typos'),
     ('dd / 3dd', 'delete (cut) a line / three lines', 'remove or move lines'),
     ('yy / 3yy', 'copy a line / three lines', 'duplicate'),
     ('p / P', 'paste below / above', 'after dd or yy'),
     ('r<char>', 'replace one character', 'fix one letter'),
     ('cw / C', 'change word / to end of line', 'rewrite a value'),
     ('u / Ctrl+R', 'undo / redo', 'mistakes'),
     ('.', 'repeat the last change', 'same edit again')],
    VB(T4, 'yyGp:wq<CR>', note='<code>yy</code> copied line 1, <code>G</code> went to the end, <code>p</code> pasted below.'),
    [('sys', [
        VI('Delete the user line from a config.', CONF, 'Gdd:wq<CR>', '<code>G</code> to the last line, <code>dd</code> deletes it.', 'app.conf'),
        VI('Deleted the wrong line: undo it.', T4, 'jddu:wq<CR>', '<code>u</code> brings line 2 back.')]),
     ('dev', [
        VI('Move a line down (cut and paste).', T4, 'ddp:wq<CR>', '<code>dd</code> cuts line 1, <code>p</code> pastes it below line 2: they swap.'),
        VI('Duplicate a line to make a similar one.', T4, 'yyP:wq<CR>', '<code>yy</code> then <code>P</code> pastes above: line 1 twice.')]),
     ('dba', [
        VI('Change the port value 80 to 3306.', CONF, '$xxa3306<Esc>:wq<CR>', '<code>$</code> line end, <code>xx</code> delete “80”, <code>a</code> append the new value.', 'app.conf'),
        VI('Fix one wrong letter: “Port” → “port”.', 'Port=80\n', 'rp:wq<CR>', '<code>r</code> replaces just the character under the cursor.', 'app.conf')]),
     ('data', [
        VI('Remove the first three rows of a file.', T4, '3dd:wq<CR>', 'A count in front: <code>3dd</code>.')]),
    ]
) + cmdcard_u(['every session: save, quit, or both', 'escaping when something went wrong (:q!)', 'saving under another name (:w newname)'],
               ['you are in Insert mode (press Esc first, or you will type “:wq”)'])(
    'quit', ':w :q :wq :q! ZZ', 'saving and quitting',
    'From Normal mode, <code>:</code> opens the command line at the bottom. <code>:w</code> writes, <code>:q</code> quits (refused if unsaved), <code>:wq</code> both, <code>:q!</code> quits and throws changes away. <code>ZZ</code> = save if changed and quit.',
    ':w [name]  ·  :q  ·  :wq  ·  :q!  ·  ZZ  ·  ZQ', 'change',
    [(':w', 'write (save)', 'save often'),
     (':w newname', 'save a copy under another name', 'keep the original'),
     (':q', 'quit (only if saved)', 'leave'),
     (':wq / :x / ZZ', 'save and quit (:x and ZZ only write if changed)', 'normal end'),
     (':q! / ZQ', 'quit without saving', 'abandon changes'),
     (':wq!', 'force write (e.g. read-only file you own)', 'rare'),
     (':e!', 'reload the file, discard changes', 'start again')],
    VB(T4, 'dd:q!<CR>', note='<code>dd</code> then <code>:q!</code>: the file on disk still has all four lines.'),
    [('sys', [
        VI('Delete a line and save with ZZ.', T4, 'ddZZ', '<code>ZZ</code> saved and quit: line 1 is gone.'),
        VI('Save a copy first, then quit without changing the original.', CONF, 'ddo# test<Esc>:w app.conf.test<CR>:q!<CR>', '<code>:w app.conf.test</code> writes the buffer to a new file; <code>:q!</code> leaves app.conf as it was (shown here).', 'app.conf')]),
    ]
) + cmdcard_u(['finding a setting or an error text', 'jumping to the next occurrence quickly', 'together with operators: d/word deletes up to it'],
               ['searching many files (use grep, Lesson 6.1)'])(
    'search', '/ ? n N', 'searching',
    '<code>/text</code> Enter searches forward, <code>?text</code> backward; <code>n</code> repeats in the same direction, <code>N</code> in the other. <code>*</code> searches the word under the cursor.',
    '/pattern ⏎  ·  ?pattern ⏎  ·  n  N  *  #', 'safe',
    [('/text', 'search forward', 'find a setting'),
     ('?text', 'search backward', 'look above'),
     ('n / N', 'next / previous match', 'repeat'),
     ('* / #', 'next / previous of the word under the cursor', 'variables in code'),
     (':set hlsearch / :noh', 'highlight matches / clear highlight', 'see all'),
     ('/\\cport', 'ignore case for this search', 'mixed case')],
    VB(T4, '/3<CR>x:wq<CR>', note='The search jumped to the “3”; x deleted it.'),
    [('dba', [
        VI('Jump to the host setting and change its value.', CONF, '/host<CR>f=lCdb.internal<Esc>:wq<CR>', '<code>/host</code> finds the line, <code>f=</code> jumps to “=”, <code>l</code> one right, <code>C</code> changes to the end.', 'app.conf')]),
     ('sys', [
        VI('Delete every line from the cursor up to the line with “admin”.', CONF, 'd/admin<CR>:wq<CR>', 'Operator + search: <code>d/admin</code> deletes from the cursor up to the match, but not the match itself, so “admin” stays.', 'app.conf')]),
    ]
) + undo('If something went wrong in vim…', [
    ('Keys did strange things:', 'Esc (twice), then <code>u</code> as many times as needed.'),
    ('Want to leave without saving:', 'Esc, <code>:q!</code> Enter. The file on disk is unchanged.'),
    ('Want to start the edit again:', '<code>:e!</code> reloads the file from disk.'),
    ('Saved by mistake:', 'undo still works while vim is open (<code>u</code>, then <code>:w</code>); after closing, use your backup (Lesson 3.2) or git.'),
    ('Terminal looks frozen:', 'you may have pressed Ctrl+S (pauses output): press <b>Ctrl+Q</b>. Ctrl+Z suspended vim: type <code>fg</code>.'),
]) + screens_block('Real vim screens: modes and quitting', 'Riya opens app.conf, deletes a character, tries to quit, and learns the right way. Each screen is captured from a real vim.',
    VSET, 'vim app.conf', [
        ('x', 'x', 'deletes the “p” of port in Normal mode.'),
        (':q  Enter', "':q' Enter", 'is refused: E37, there are unsaved changes.'),
        ('i', 'i', 'switches to Insert mode: see <code>-- INSERT --</code>.'),
        ('p  Esc', "p Escape", 'types the “p” back and returns to Normal mode.'),
        (':wq  Enter', "':wq' Enter", 'saves and quits.'),
    ], w=64, h=8, after='cat app.conf', hid='screens') + errors('Messages students see in vim. The E37 screen above is real; these are produced by real runs too.', [
    dict(cmd="printf 'a\\n' > f.txt; vim -u NONE -N -i NONE -es -c 'normal x' -c 'q' f.txt; echo \"vim exit status: $?\"", meaning='E37 “No write since last change”: you tried <code>:q</code> with unsaved changes (here vim in batch mode exits with an error).', fix='<code>:wq</code> to save, or <code>:q!</code> to discard.'),
]) + '''  <p><b>E212: Can’t open file for writing</b> (typical): you saved into a folder you may not change, such as /etc. Save elsewhere with <code>:w ~/copy.conf</code>, and open root files with <code>sudoedit</code>.</p>
  <p><b>E325 ATTENTION – Found a swap file</b> (typical): vim found <code>.app.conf.swp</code> because the file is open elsewhere or vim crashed. Press <b>R</b> to recover, <b>E</b> to edit anyway, <b>Q</b> to quit; delete the old swap file afterwards if you recovered.</p>
''' + qc('After pressing <code>i</code> you see <code>-- INSERT --</code>. How do you get back to commands?', 'Press <code>Esc</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animation
vs = lambda steps, note, tone='blue': (term(14, 12, 332, 116, tmux_screens(VSET, 'vim app.conf', steps, 46, 7)[-1].split('\n')[:7], title='vim app.conf', size=7.2, step=14, prompt='') + cap(note, '', tone, y=150, h=34))
see = [vs([], 'Normal mode: nothing at the bottom.'),
       vs(['i'], 'i → Insert mode: -- INSERT --', 'green'),
       vs(['i', '-l new', 'Escape'], 'Typed “new”, Esc → Normal again.', 'blue'),
       vs(['i', '-l new', 'Escape', "':'"], ': → command line at the bottom.', 'blue'),
       vs(['v', 'l', 'l'], 'v → Visual mode: select text.', 'violet')]
def gear(hl, note, tone='blue'):
    o = label_box(130, 60, 100, 40, ['NORMAL'], 'acc' if hl == 'N' else 'card', 10)
    o += label_box(10, 10, 100, 36, ['INSERT'], 'green' if hl == 'I' else 'card', 9.6)
    o += label_box(250, 10, 100, 36, ['CMD-LINE :'], 'blue' if hl == 'C' else 'card', 9.6)
    o += label_box(10, 112, 100, 36, ['VISUAL'], 'violet' if hl == 'V' else 'card', 9.6)
    o += arrow(130, 72, 110, 40, 'ink3') + arrow(230, 72, 250, 40, 'ink3') + arrow(130, 90, 110, 120, 'ink3')
    return o + t(240, 135, note, 8.6, tone, bold=True)
behind = [gear('N', 'Start: Normal.'), gear('I', 'i a o → Insert.', 'green'), gear('N', 'Esc → Normal.'),
          gear('C', ': → Command-line.', 'blue'), gear('V', 'v → Visual.', 'violet')]
two = anim_two('Four modes, real screens', 'Mode switches',
               'Real vim screens: Normal mode, -- INSERT -- after i, back to Normal after Esc, the colon command line, and -- VISUAL -- after v.',
               'A map of vim modes: Normal in the centre; i to Insert, colon to Command-line, v to Visual; Esc back to Normal.', see, behind,
               ['vim starts in Normal mode: the last line is empty.',
                '<code>i</code> shows <code>-- INSERT --</code>: keys are text now.',
                'After Esc the indicator disappears: Normal mode.',
                '<code>:</code> puts the cursor on the bottom line for a command.',
                '<code>v</code> starts Visual mode: moving selects text.'],
               ['Normal mode is the centre.', 'Insert mode for typing.', 'Esc always returns to Normal.', 'Command-line for :w, :q, :42, :s.', 'Visual for selections (Lesson 4.3).'])

dx = dissect('Layer by layer: what happens when you type :wq',
    'From your keys to the file. Each layer has a real command and its output from our build machine.', [
    dict(key='key', name='Keys', sub='bytes from the terminal',
         why='vim reads raw keys, not lines.',
         how='Esc is byte 27; “:” starts the command line.',
         impl='Terminal in raw mode.', used='All full-screen programs.',
         cmd="printf '\\x1b:wq\\r' | od -An -c"),
    dict(key='ex', name='Command line', sub='the ex editor inside vim',
         why='Commands like :w :q :s :g come from ex (1976).',
         how='vim parses the line after : as an ex command.',
         impl='vim’s ex command parser.', used='ex scripts, sed’s syntax.',
         cmd="printf 'line 1\\nline 2\\n' > n.txt; ex -s -c '1d' -c 'wq' n.txt; cat n.txt"),
    dict(key='write', name=':w', sub='write the buffer',
         why='The disk changes only when you write.',
         how='vim writes the buffer (by default via a new file and rename, keeping permissions), and a backup if set.',
         impl='writefile() in vim.', used=':w, :wq, ZZ.',
         cmd=VSET + "; vim -u NONE -N -i NONE -es -c '1d' -c 'wq' app.conf; cat app.conf"),
    dict(key='swap', name='Swap file', sub='crash safety',
         why='SSH can drop while you edit.',
         how='While a file is open vim keeps .name.swp; it is removed on a clean exit.',
         impl='Swap/recovery files.', used='vim -r file to recover.',
         cmd="vim --version | grep -o '+[a-z]*swap[a-z]*\\|-[a-z]*swap[a-z]*' | head -1; vim --version | head -1"),
], hint='From keys to disk. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Modes on a real screen</h2>
  <p>Left: real vim screens captured after each key. Right: the mode map.</p>
''' + two + dx + qc('Which key gets you back to Normal mode from any other mode?', '<code>Esc</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>vim at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ vi /etc/', 'prompt'), ('fstab', 'acc')], title='admin', size=6.4, step=12),
              '1. Minimal servers and rescue mode', 'When nothing else is installed, vi is. Admins fix /etc files in rescue shells with vi.', ['Broken boot', '*vi', 'fixed']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['RHCSA', 'vim only'], 'red', 8.6), '2. Exams and interviews',
    'The RHCSA practical exam expects you to edit files with vim; “how do you exit vi?” is a classic interview question.', ['Exam', '*vim', 'pass']) + '\n' + usecase(
    term(8, 14, 104, 62, [('git commit', 'prompt'), ('→ vim', 'acc')], title='dev', size=6.4, step=12),
    '3. Git and crontab', 'git commit, git rebase -i and crontab -e open vi by default on many systems.', ['git commit', '*vim', 'message']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['containers', 'vi only'], 'green', 8.6), '4. Inside containers',
    'Small container images often have only busybox vi: the basic keys of this lesson work there too.', ['docker exec', '*vi', 'debug']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Non-interactive vim: the same commands run from the shell (vim -es), really run on our build machine.', [
    dict(level='b', title='Which vi do I have?', scenario='Is vi really vim, and which version?',
         cmd="readlink -f \"$(command -v vi)\"; vim --version | head -1",
         explain='On Ubuntu vi points to vim (or vim.tiny on minimal systems).'),
    dict(level='i', title='Delete line 1 without opening the editor', scenario='Remove a header line in a script.', setup="printf 'header\\ndata\\n' > f.txt",
         cmd="vim -u NONE -N -i NONE -es -c '1d' -c 'wq' f.txt; cat f.txt",
         explain='-es runs vim silently as ex; the same keys as :1d and :wq.'),
    dict(level='a', title='Append a line at the end', scenario='Add a setting without an editor window.', setup="printf 'port=80\\n' > app.conf",
         cmd="vim -u NONE -N -i NONE -es -c \"call append('$', 'timeout=30')\" -c 'wq' app.conf; cat app.conf",
         explain='append() adds a line after the last one (like G o … Esc).'),
]) + which('Choosing how to edit.', [
    ('Quick edit, any server', 'vi file', 'Always there.', 'Typing before pressing i.'),
    ('Beginners, Ubuntu', 'nano file', 'Keys on screen.', 'Searching nano on minimal servers.'),
    ('Leave without saving', ':q!', 'Safe exit.', 'Closing the terminal (leaves a swap file).'),
    ('Root-owned file', 'sudoedit file', 'Safe.', 'sudo vim.'),
    ('Scripts', 'sed / vim -es', 'No keyboard needed.', 'Interactive vim in CI.'),
    ('Learn properly', 'vimtutor', '30 minutes, built in.', 'Memorising lists only.'),
]) + keys('The 20 keys of this lesson.', [
    ('i a o / I A O', 'insert here, after, new line below / at start, at end, above', 'o'),
    ('Esc', 'back to Normal mode', 'Esc'),
    ('h j k l', '← ↓ ↑ →', 'j'),
    ('w b e  0 $  gg G', 'words, line ends, file ends', 'gg'),
    ('x dd yy p P', 'delete char, delete line, copy line, paste', 'yyp'),
    ('u  Ctrl+R  .', 'undo, redo, repeat', 'u'),
    ('/text n N', 'search, next, previous', '/port'),
    (':w :q :wq :q! ZZ', 'save, quit, both, discard, save-and-quit', ':wq'),
]) + scriptit('quick-fix.sh', 'The same kind of edit you would do in vim, done with vim itself in batch mode: open, change, save. Useful in scripts and Dockerfiles where nobody can type.',
'''#!/bin/bash
f=${1:-app.conf}
printf 'port=80\\nhost=localhost\\nuser=admin\\n' > "$f"   # demo file
cp "$f" "$f.bak"
vim -u NONE -N -i NONE -es \\
  -c '%s/^port=.*/port=8080/' \\
  -c 'g/^user=/d' \\
  -c 'wq' "$f"
diff "$f.bak" "$f" || true''',
'<p><code>%s</code> and <code>g</code> are covered in Lesson 4.3; in scripts, sed (Lesson 6.4) is the more common choice.</p>') + puzzle_answer('In Normal mode, <code>c</code> is “change” and waits for a motion, <code>h</code> moves left (so <code>ch</code> changed the character to the left and <b>entered Insert mode</b>), and the remaining letters “ange” were then typed as text. So the first two letters were commands, and <code>c</code> + <code>h</code> together switched to Insert mode. A real run with the cursor at the start of <code>port=80</code> turned the line into <code>angeport=80</code> (nothing to the left to change, but Insert mode started anyway). Fix: Esc, <code>u</code> to undo, then <code>i</code> before typing.') + qc('You are in Normal mode on line 1 of a 100-line file. How do you go to the last line, and back?', '<code>G</code>, then <code>gg</code>.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-nano-the-beginner-friendly-editor/">Lesson 4.1</a>: nano, buffers and saving.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
