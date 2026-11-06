import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

VL = 'Real run: the keys were typed into vim 9.1 on Ubuntu 24.04; the file after saving'
H = 'db=localhost\nweb=localhost\ncache=localhost\n'
T = 'alpha\nbeta\ngamma\ndelta\n'
def VI(sit, content, keys, why, name='notes.txt'):
    shown = keys.replace('<CR>', '⏎')
    return dict(situation=sit, cmd=f'vim {name}\n# keys: {shown}', rec=(VL, vimrun(content, keys, name)), why=why)
def VB(content, keys, name='notes.txt', note=''):
    shown = keys.replace('<CR>', '⏎')
    return dict(cmd=f'vim {name}\n# keys: {shown}', rec=(VL, vimrun(content, keys, name)), note=note)
HSET = "printf 'db=localhost\\nweb=localhost\\ncache=localhost\\n' > hosts.conf"

HOOK = hook('A config has <code>localhost</code> on 40 lines; Riya must change all of them to <code>db.internal</code>, but look at each one first. Then 20 lines need <code># </code> in front, and the same small edit must be repeated on 300 lines. Doing this by hand takes an hour and invites typos. In vim each job is <b>one command</b>, and you see every change before it happens.',
    ['search and replace in the whole file, a range, or with confirmation (<code>:%s/old/new/gc</code>)',
     'act on many lines at once with <code>:g</code>, visual mode and block selections (<code>Ctrl+V</code>)',
     'repeat work with <code>.</code>, macros (<code>qa … q</code>, <code>@a</code>) and registers (<code>"ayy</code>)',
     'work with several files and splits, compare files with vimdiff, run shell commands, and set up <code>~/.vimrc</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, '40 replacements, 20 comments'),
    ('decide', 'Which tool when?', 2, ':s, :g, Ctrl+V or a macro?'),
    ('definition', 'What makes vim fast', 5, 'simple meaning + 4 depths'),
    ('commands', 'Power tools by field', 16, 'verified results, your field'),
    ('screens', 'Splits and vimdiff', 4, 'real screens'),
    ('errors', 'Errors decoded', 3, 'E486, pattern not found'),
    ('vimrc', 'Your .vimrc', 3, 'settings that help every day'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which power tool? (decide in 5 seconds)', [
    ('Replace everywhere', ':%s/old/new/g', '% = all lines'),
    ('Replace, but check each', ':%s/old/new/gc', 'y / n / a / q'),
    ('Replace in lines 10–20', ':10,20s/old/new/g', 'a range'),
    ('Delete all lines that match', ':g/pattern/d', ':v = lines that do NOT match'),
    ('Comment out a block', 'Ctrl+V, select, I# , Esc', 'block insert'),
    ('Indent lines', 'V, select, >', '< to unindent'),
    ('Repeat the last change', '.', 'the dot'),
    ('Repeat a sequence on many lines', 'qa … q, then 10@a', 'a macro'),
    ('Two files side by side', ':vsplit file  /  vimdiff a b', 'Ctrl+W w switches'),
    ('Insert command output', ':r !date', '! runs a shell command'),
])

cmap = concept_map(
    [('4.2', 'vim basics', 'modes, dd, yy, :wq'), ('3.7', 'Regular expressions', 'the patterns in :s'), ('3.4', 'Wildcards', 'not the same as regex')],
    [':s and :%s with flags g c i, ranges', ':g and :v for many lines', 'visual, line and block mode (Ctrl+V)', '. repeat, macros, registers, text objects', 'splits, buffers, vimdiff, :r !cmd, ~/.vimrc'],
    [('6.4', 'sed', 'the same s/// in scripts'), ('6.6', 'Regex', 'grep, sed, awk'), ('6.3', 'diff', 'vimdiff’s big brother'), ('12.2', 'Startup files', '.vimrc like .bashrc')],
    'These are the features that make experienced engineers prefer vim: big, exact, repeatable edits in seconds.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ vim hosts.conf', (':%s/localhost/db.internal/gc', 'acc'), ('replace with db.internal (y/n/a/q/l/^E/^Y)?', 'out'), ('y n y …', 'dim'), ('3 substitutions on 3 lines', 'out'), (':wq', 'acc')], title='riya@app-01', size=7.4, step=15)
      + t(352, 36, 'One command per job:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• :%s/old/new/gc', '• :g/^#/d', '• Ctrl+V … I# Esc', '• qa … q  @a', '• vimdiff a b'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>40 replacements and 20 comments before lunch</h2>
  <div class="story">
''' + puzzle('Riya runs <code>:%s/localhost/db.internal/</code> (without <code>g</code>) on a line that says <code>db=localhost,backup=localhost</code>. How many “localhost” remain on that line, and which single letter fixes it?') + '''
    <p class="narration">The shop is moving its database to a new server. Several configs point to localhost; some lines must change, some must not. Then a block of old settings must be disabled.</p>
''' + scene('A terminal: vim runs :%s/localhost/db.internal/gc, asks for each match, and reports 3 substitutions; then :wq.', sc,
            'Big edits, <tspan font-weight="700" class="s-acc">each one confirmed</tspan>.') + '''
A> <code>:%s/localhost/db.internal/gc</code>: substitute in every line (<code>%</code>), every match (<code>g</code>), and ask (<code>c</code>). Answer <code>y</code> or <code>n</code> for each.
R> And commenting out 20 lines?
K> <code>Ctrl+V</code> to select a column down the 20 lines, <code>I</code>, type <code># </code>, <code>Esc</code>: all 20 at once.
A> Today: substitution, :g, visual blocks, the dot, macros, registers, splits, vimdiff, running shell commands and your own .vimrc. Every result is verified by typing the keys into a real vim.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Doing work once and repeating it: find-and-replace for the whole document, a stamp for a column of lines, and a tape recorder that replays a sequence of keys.">'
       + ''.join(label_box(16 + k * 208, 22, 192, 110, [a, b, c, d], tone, 9.4) for k, (a, b, c, d, tone) in enumerate([
           ('Find & replace', ':%s/old/new/gc', 'whole file at once', 'ask for each one', 'blue'),
           ('A column stamp', 'Ctrl+V … I# Esc', 'same text on', 'many lines', 'green'),
           ('A tape recorder', 'qa … q, @a', 'record keys once', 'replay many times', 'violet')]))
       + t(320, 160, 'Experts do not type faster: they type less.', 9.6, 'ink2')
       + t(320, 182, 'Describe the change once, let vim repeat it.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('vim power features at four depths', [
    ('v', 'No jargon: do it once, repeat it', '      <p>Three ideas from everyday life.</p>' + pic + '''
      <ul>
        <li>Find and replace, like Word, but you can ask for each change.</li>
        <li>A stamp: select a column of lines and type once; it appears on all of them.</li>
        <li>A tape recorder: record what you type once, replay it on the other lines.</li>
      </ul>'''),
    ('b', 'The commands you will use every day', '''      <ul>
        <li><code>:%s/old/new/g</code> replaces in the whole file; add <code>c</code> to confirm each one.</li>
        <li><code>.</code> repeats your last change: change one line, move, press <code>.</code>.</li>
        <li><code>v</code> select characters, <code>V</code> whole lines, <code>Ctrl+V</code> a block; then <code>d</code>, <code>y</code>, <code>&gt;</code>, or <code>I</code> to insert on every line.</li>
        <li><code>:set number</code> shows line numbers.</li>
        <li><code>:e file</code> opens another file; <code>:sp</code>/<code>:vsp</code> split the window.</li>
      </ul>'''),
    ('i', 'Ranges, :g, macros and registers', '''      <ul>
        <li>Ranges: <code>:10,20s/…</code>, <code>:.,$s/…</code> (here to end), <code>:'&lt;,'&gt;s/…</code> (the visual selection).</li>
        <li>Flags: <code>g</code> all matches in a line, <code>c</code> confirm, <code>i</code> ignore case. Groups: <code>\\(…\\)</code> and <code>\\1</code>.</li>
        <li><code>:g/pattern/d</code> deletes matching lines; <code>:v/pattern/d</code> deletes the others; <code>:g</code> can run any command (<code>:g/ERROR/t$</code> copies them to the end).</li>
        <li>Macro: <code>qa</code> record into a, do the edit, <code>q</code> stop, <code>@a</code> replay, <code>10@a</code> ten times.</li>
        <li>Registers: <code>"ayy</code> copy into a, <code>"ap</code> paste from a; <code>:reg</code> shows them all.</li>
      </ul>'''),
    ('a', 'Behind the screen: ex, regex flavours and the shell', '''      <ul>
        <li><code>:s</code> and <code>:g</code> are ex commands (the editor vi grew out of); sed uses the same <code>s///</code> syntax because both come from <code>ed</code>.</li>
        <li>vim regex is close to grep’s basic regex: <code>\\(</code> <code>\\)</code> <code>\\+</code> need backslashes; <code>\\v</code> (“very magic”) at the start makes it like Perl/ERE: <code>:%s/\\v(\\d+)-(\\d+)/\\2-\\1/</code>.</li>
        <li><b>Text objects</b> select by meaning: <code>iw</code> inner word, <code>i"</code> inside quotes, <code>ap</code> a paragraph: <code>ci"</code> changes a quoted string from anywhere inside it.</li>
        <li><code>:r !cmd</code> inserts command output, <code>:%!cmd</code> filters the whole buffer through a command (e.g. <code>sort</code>, <code>jq .</code>), <code>:w !sudo tee %</code> saves a root file you opened without sudo (prefer sudoedit).</li>
        <li><code>~/.vimrc</code> is read at start; on Ubuntu, without one, vim loads <code>defaults.vim</code> (ruler, incremental search, last cursor position).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Substitution, global commands, visual mode, macros and registers</h2>
''' + def_block(
    '<code>:[range]s/pattern/replacement/[flags]</code> substitutes text matching a regular expression in the given lines (<code>%</code> = all). <code>:g/pattern/command</code> runs an ex command on every line that matches (<code>:v</code> on those that do not). <b>Visual mode</b> (<code>v</code>, <code>V</code>, <code>Ctrl+V</code>) selects text for an operator. A <b>macro</b> is a recorded sequence of keys stored in a <b>register</b> and replayed with <code>@</code>; registers also hold yanked and deleted text.',
    'Describe a change once (<code>:s</code>, <code>:g</code>, a selection, a macro) and let vim apply it everywhere.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Range', 'Which lines: 10,20 · % (all) · . (current) · $ (last).'),
    ('Flag', 'g all matches, c confirm, i ignore case.'),
    ('Visual block', 'A rectangle of text: Ctrl+V.'),
    ('Register', 'A named clipboard: "a … "z, "0, "+.'),
    ('Macro', 'Recorded keys in a register, replayed with @.'),
    ('Text object', 'iw, i", ap: select by meaning.'),
    ('Buffer / window', 'An open file / a view on the screen.'),
    ('Regex', f'The pattern language. {gl("regular-expression-regex", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    (':s', 'substitute', 'From ed (1969) via ex; sed uses it too.'),
    (':g', 'global', 'g/re/p in ed gave us “grep”.'),
    (':v', 'inverse global', 'Lines that do not match.'),
    ('q / @', 'record / execute', 'Record a macro, run it.'),
    ('"a', 'register a', 'The double quote selects a register.'),
    ('Ctrl+V', 'visual block', 'Ctrl+Q on Windows gvim.'),
    ('vimdiff', 'vim + diff', 'Side-by-side comparison.'),
    ('.vimrc', 'vim run commands', 'Like .bashrc for vim.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Replace all', '<code>:%s/old/new/g</code> (+c to confirm)'),
    ('Delete matching lines', '<code>:g/pattern/d</code>'),
    ('Comment a block', '<code>Ctrl+V</code> ↓↓ <code>I# </code> <code>Esc</code>'),
    ('Repeat', '<code>.</code> · macro <code>qa…q</code> <code>@a</code>'),
    ('Compare files', '<code>vimdiff a b</code>'),
    ('Settings', '<code>~/.vimrc</code>: <code>set number</code>'),
]) + '\n' + lv + didyou('The command <code>g/re/p</code> of the old Unix editor <i>ed</i> meant “globally, for every line matching the regular expression, print it”. Ken Thompson turned exactly that into a separate program in 1973: <b>grep</b>. vim still understands <code>:g/re/p</code>.') + '''
EXAM> “How do you replace a word in the whole file in vi, with confirmation?” → :%s/old/new/gc (% all lines, g all matches per line, c confirm; answer y/n/a/q); mention ranges like :10,20s and :g/pattern/d.
''' + qc('What do <code>%</code>, <code>g</code> and <code>c</code> mean in <code>:%s/a/b/gc</code>?', '% = every line, g = every match in a line, c = confirm each change.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ranges and flags for :s and :g</h2>
''' + table(['Range', 'Lines', 'Example'], [
    ['(none)', 'current line only', '<code>:s/80/8080/</code>'],
    ['<code>%</code>', 'all lines', '<code>:%s/a/b/g</code>'],
    ['<code>10,20</code>', 'lines 10 to 20', '<code>:10,20s/^/# /</code>'],
    ['<code>.,$</code>', 'here to the end', '<code>:.,$s/x/y/</code>'],
    ["<code>'&lt;,'&gt;</code>", 'the visual selection (typed for you after V and :)', '<code>:\'&lt;,\'&gt;s/a/b/g</code>'],
    ['<code>/start/,/end/</code>', 'between two patterns', '<code>:/\\[db\\]/,/^$/s/localhost/db/</code>'],
], minw=520) + table(['Flag / piece', 'Meaning', 'Example'], [
    ['<code>g</code>', 'every match on the line', '<code>:%s/,/;/g</code>'],
    ['<code>c</code>', 'confirm: y n a q l', '<code>:%s/x/y/gc</code>'],
    ['<code>i</code> / <code>\\c</code>', 'ignore case', '<code>:%s/error/ERROR/gi</code>'],
    ['<code>\\(…\\)</code> + <code>\\1</code>', 'group and reuse', '<code>:s/\\(foo\\) \\(bar\\)/\\2 \\1/</code>'],
    ['<code>\\v</code>', 'very magic: Perl-like regex', '<code>:%s/\\v(\\d+)/[\\1]/g</code>'],
    ['<code>&amp;</code>', 'the whole match', '<code>:%s/[0-9]\\+/"&amp;"/g</code>'],
    ['<code>\\t \\r</code>', 'tab / new line in the replacement', '<code>:%s/,/\\t/g</code>'],
], minw=520) + mistake(':%s/localhost/db.internal/', ':%s/localhost/db.internal/g',
                       'Without <code>g</code>, only the <b>first</b> match on each line changes. Lines with two matches keep the second one.') + qc('How do you replace “dev” with “prod” only in lines 5 to 9?', '<code>:5,9s/dev/prod/g</code>') + '''
</section>
'''

# ---------------------------------------------------------------- 4. cards
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each power tool explained, then used in every field</h2>
  <p id="commands">Every result is real: the keys were typed into vim 9.1 (fed with <code>vim -s</code>), and the file is shown after saving. Demo files: <code>hosts.conf</code> (db=, web=, cache=localhost) and <code>notes.txt</code> (alpha, beta, gamma, delta).</p>
''' + cmdcard_u(['the same text change on many lines', 'changes you want to confirm one by one (c)', 'reordering parts with groups'],
               ['the change depends on context a regex cannot see (edit by hand or use a macro)', 'many files at once (use sed -i, Lesson 6.4)'])(
    'subst', ':s', 'substitute',
    'Replaces text matching a pattern. Choose the lines with a range, and the behaviour with flags.',
    ':[range]s/pattern/replacement/[g][c][i]', 'change',
    [(':s/a/b/', 'first match in the current line', 'one fix'),
     (':s/a/b/g', 'all matches in the current line', 'one line'),
     (':%s/a/b/g', 'all matches in all lines', 'whole file'),
     (':%s/a/b/gc', 'ask y/n/a/q for each', 'careful changes'),
     (':10,20s/a/b/g', 'only lines 10–20', 'a section'),
     (':%s/a/b/gi', 'ignore case', 'Mixed Case'),
     (':%s/\\(x\\) \\(y\\)/\\2 \\1/', 'groups', 'reorder')],
    VB(H, ':%s/localhost/db.internal/g<CR>:wq<CR>', 'hosts.conf', 'Every localhost on every line replaced.'),
    [('sys', [
        VI('Replace with confirmation: say yes, no, yes.', H, ':%s/localhost/db.internal/gc<CR>yny:wq<CR>', 'The web line was kept (answered n). <code>a</code> would accept all remaining, <code>q</code> stops.', 'hosts.conf'),
        VI('Only in lines 2 and 3.', H, ':2,3s/localhost/x/<CR>:wq<CR>', 'A range limits the change; line 1 is untouched.', 'hosts.conf')]),
     ('data', [
        VI('Turn a CSV into tab-separated values.', 'id,name\n1,a\n', ':%s/,/\\t/g<CR>:wq<CR>', '<code>\\t</code> in the replacement inserts a real tab (shown here as a gap).', 'data.csv')]),
     ('dev', [
        VI('Swap two words with groups.', 'foo bar\n', ':s/\\(foo\\) \\(bar\\)/\\2 \\1/<CR>:wq<CR>', 'Groups <code>\\( \\)</code> are remembered as \\1 and \\2 (like $1 in rename, Lesson 3.7).', 'main.txt')]),
    ],
    anat=anatomy([(':', 'sep', 'command line'), ('%', 'opt', 'range: all lines'), ('s/localhost/db.internal/', 'cmd', 'substitute'), ('gc', 'arg', 'flags: all, confirm')], 'Read it as: on <b>all lines</b>, <b>substitute</b> localhost with db.internal, <b>every match</b>, <b>confirm</b>.')
) + cmdcard_u(['deleting or keeping all lines that match', 'running a command on every matching line', 'cleaning logs and configs'],
               ['you need to change text inside the lines (combine: :g/x/s/a/b/)'])(
    'global', ':g · :v', 'global commands',
    '<code>:g/pattern/cmd</code> runs an ex command on every line matching the pattern; <code>:v/pattern/cmd</code> on every line that does <b>not</b> match.',
    ':g/pattern/command   ·   :v/pattern/command', 'change',
    [(':g/re/d', 'delete matching lines', 'remove comments, noise'),
     (':v/re/d', 'keep only matching lines', 'extract errors'),
     (':g/re/t$', 'copy matching lines to the end', 'collect'),
     (':g/re/m0', 'move matching lines to the top', 'reverse / reorder'),
     (':g/re/s/a/b/', 'substitute only on matching lines', 'targeted changes'),
     (':g/re/p', 'print them (the origin of grep)', 'look')],
    VB('a=1\n# old\nb=2\n# old\n', ':g/^#/d<CR>:wq<CR>', 'app.conf', 'Every line starting with # was deleted.'),
    [('sec', [
        VI('Keep only the lines with DEBUG to review them.', 'a=1\nb=2\nDEBUG=1\n', ':v/DEBUG/d<CR>:wq<CR>', '<code>:v</code> deletes every line that does not match: only DEBUG=1 remains (in a copy, of course).', 'app.conf')]),
     ('sys', [
        VI('Remove all comment lines from a config before diffing it.', 'port=80\n# comment\nhost=db\n', ':g/^#/d<CR>:wq<CR>', 'Comments often differ between servers; removing them shows the real settings.', 'app.conf')]),
    ]
) + cmdcard_u(['commenting out or indenting a block', 'editing a column (same position on many lines)', 'selecting exactly what an operator should act on'],
               ['the lines are far apart (use :g or :s with a range)'])(
    'visual', 'v · V · Ctrl+V', 'visual mode and blocks',
    'Select first, act second. <code>v</code> selects characters, <code>V</code> whole lines, <code>Ctrl+V</code> a rectangular block. Then use an operator: <code>d y c &gt; &lt;</code>, or <code>I</code>/<code>A</code> in a block to insert on every line.',
    'v | V | Ctrl+V  → move →  d y c > < ~ | I…Esc | A…Esc | :', 'change',
    [('v / V / Ctrl+V', 'characters / lines / block', 'choose the shape'),
     ('d y c', 'delete / copy / change the selection', 'act'),
     ('> <', 'indent / unindent lines', 'code, YAML'),
     ('Ctrl+V … I text Esc', 'insert text on every line of the block', 'comments'),
     ('Ctrl+V … $ A text Esc', 'append at the end of every line', 'add ; or ,'),
     ('~ / u / U', 'toggle / lower / upper case', 'fix case'),
     ('gv', 'reselect the last selection', 'do more with it')],
    VB(T, '<C-v>3jI# <Esc>:wq<CR>', note='Ctrl+V, three lines down, I, “# ”, Esc: all four lines commented at once.'),
    [('dev', [
        VI('Indent two lines of code.', T, 'Vj>:wq<CR>', '<code>V</code> selects lines, <code>j</code> extends, <code>&gt;</code> indents (by a tab here; set shiftwidth in .vimrc).')]),
     ('devops', [
        VI('Add a comma at the end of four lines (block append).', T, '<C-v>3j$A,<Esc>:wq<CR>', 'In a block, <code>$</code> extends to every line end; <code>A</code> appends there.')]),
     ('data', [
        VI('Uppercase a header line.', 'id,name,marks\n1,a,9\n', 'VU:wq<CR>', '<code>V</code> selects the line, <code>U</code> uppercases it.', 'marks.csv')]),
    ]
) + cmdcard_u(['the same edit on many lines that a regex cannot describe', 'repeating your last change exactly', 'keeping several clipboards'],
               ['a simple text replacement (use :s)'])(
    'repeat', '. · qa…q @a · "a', 'repeat, macros and registers',
    '<code>.</code> repeats the last change. A <b>macro</b> records keys into a register (<code>qa</code> … <code>q</code>) and replays them (<code>@a</code>, <code>10@a</code>). <b>Registers</b> are named clipboards: <code>"ayy</code> copies into a, <code>"ap</code> pastes from a.',
    '.  ·  q{reg} … q  ·  [count]@{reg}  ·  "{reg}y / "{reg}p', 'change',
    [('.', 'repeat the last change', 'same edit again'),
     ('qa … q', 'record a macro into register a', 'complex repeated edits'),
     ('@a / 10@a / @@', 'run macro a / ten times / last macro again', 'replay'),
     ('"ayy / "ap', 'copy to / paste from register a', 'several clipboards'),
     ('"0p', 'paste the last yank (not the last delete)', 'after dd overwrote the clipboard'),
     ('"+y / "+p', 'system clipboard (if vim has +clipboard)', 'copy to other programs'),
     (':reg', 'show all registers', 'what is stored')],
    VB('1\n2\n3\n4\n', 'qaA;<Esc>jq3@a:wq<CR>', 'items.txt', 'Recorded “A; Esc j” once into a, replayed it 3 times.'),
    [('dev', [
        VI('Two clipboards: copy alpha to a and beta to b, paste both at the end.', T, '"ayyj"byyG"ap"bp:wq<CR>', 'Named registers keep both copies; the normal clipboard would only hold the last one.')]),
     ('qa', [
        VI('Change a quoted value from anywhere inside the quotes.', 'name = "old value"\n', 'f"lci"new<Esc>:wq<CR>', '<code>ci"</code> = change inside quotes (a text object).', 'test.ini'),
        VI('Delete a whole paragraph.', 'para one\nline\n\npara two\n', 'dap:wq<CR>', '<code>dap</code> = delete a paragraph, including the blank line after it.')]),
    ]
) + cmdcard_u(['sorting or formatting lines', 'inserting the output of a command', 'filtering the buffer through any Unix tool'],
               ['running long jobs (use another terminal)'])(
    'shell', ':r ! · :%! · :!', 'vim and the shell',
    'vim works with any shell command: <code>:!cmd</code> runs it, <code>:r !cmd</code> inserts its output, <code>:%!cmd</code> replaces the buffer with the command’s output when the buffer is fed to it.',
    ':!cmd  ·  :r !cmd  ·  :[range]!cmd  ·  :sort', 'change',
    [(':sort / :sort u / :sort n', 'sort lines / unique / numeric', 'lists, configs'),
     (':r !date', 'insert the output of date', 'timestamps in notes'),
     (':%!sort', 'filter the whole buffer through sort', 'any filter'),
     (':%!jq .', 'pretty-print JSON (if jq is installed)', 'APIs'),
     (':!ls', 'run a command, then return', 'quick look'),
     (':w !sudo tee %', 'save a root-owned file you opened as yourself', 'emergency only')],
    VB('banana\napple\ncherry\n', ':sort<CR>:wq<CR>', 'fruits.txt', ':sort sorted the lines in place.'),
    [('sys', [
        VI('Insert a command’s output into the file.', 'x\n', ':r !echo inserted<CR>:wq<CR>', '<code>:r !cmd</code> reads the output below the cursor (try <code>:r !date</code> or <code>:r !hostname</code>).')]),
     ('data', [
        VI('Sort the data with the sort command.', 'c3\nc1\nc2\n', ':%!sort<CR>:wq<CR>', 'The whole buffer goes through sort and comes back sorted. Any filter works: <code>uniq</code>, <code>column -t</code>, <code>jq</code>.')]),
    ]
) + undo('If a big edit went wrong…', [
    ('Right after it:', '<code>u</code> undoes the whole :s or :g in one step.'),
    ('Several steps back:', '<code>u</code> repeatedly, or <code>:earlier 2m</code> (the file as it was 2 minutes ago).'),
    ('Before a risky :s:', 'add <code>c</code> to confirm, or try on a range first; <code>:w file.bak</code> saves a copy first.'),
    ('A macro ran wild:', 'stop with Ctrl+C, then <code>u</code>.'),
    ('Saved and closed:', 'only backups, git or snapshots help (Lesson 3.2).'),
]) + screens_block('Real screens: split windows and vimdiff', 'Riya compares the old and new config side by side. Screens are captured from a real vim.',
    "printf 'port=80\\nhost=localhost\\nuser=admin\\n' > old.conf; printf 'port=8080\\nhost=localhost\\nuser=admin\\n' > new.conf",
    'vimdiff old.conf new.conf', [
        (']c', "']c'", 'jumps to the next difference (the port line).'),
        ('do', "d o", '(“diff obtain”) copies the other side’s version into this window. Now both files are identical, so vimdiff folds the equal lines into one: “+--  3 lines”.'),
        (':wqa', "':wqa' Enter", 'saves both files and quits.'),
    ], w=72, h=9, after='cat old.conf', hid='screens') + errors('Messages students see with these commands. Produced by real vim runs on our build machine.', [
]) + screens_block('Real screen: E486 Pattern not found', 'A substitution for text that does not exist.',
    "printf 'port=80\\nhost=db\\n' > app.conf", 'vim app.conf', [
        (':%s/zzz/x/  Enter', "':%s/zzz/x/' Enter", 'shows E486 at the bottom: nothing was changed.'),
    ], w=60, h=6) + '''  <p><b>Slashes in the pattern:</b> to replace a path like <code>/var/log</code>, use another separator: <code>:%s#/var/log#/data/log#g</code>.</p>
''' + qc('Your :%s did the wrong thing on 40 lines. How do you undo it?', 'Press <code>u</code> once: a whole :s command is a single undo step.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animation
def rows(lines, hl, note, tone='blue'):
    o = ''.join(label_box(14, 12 + k * 30, 210, 25, [ln], 'green' if k in hl else 'card', 9) for k, ln in enumerate(lines))
    return o + t(290, 70, note, 8.6, tone, bold=True)
see = [rows(['alpha', 'beta', 'gamma', 'delta'], [], 'Four lines.') + cap('Cursor on line 1, Normal mode.', '', 'card', y=150, h=34),
       rows(['alpha', 'beta', 'gamma', 'delta'], [0], 'Ctrl+V: block mode.', 'violet') + cap('Ctrl+V starts a block on line 1.', '', 'violet', y=150, h=34),
       rows(['alpha', 'beta', 'gamma', 'delta'], [0, 1, 2, 3], '3j: four lines.', 'violet') + cap('3j extends the block down.', '', 'violet', y=150, h=34),
       rows(['# alpha', 'beta', 'gamma', 'delta'], [0], 'I# : typed on line 1…', 'amber') + cap('I, then “# ”: only line 1 shows it yet.', '', 'amber', y=150, h=34),
       rows(['# alpha', '# beta', '# gamma', '# delta'], [0, 1, 2, 3], 'Esc: copied to all.', 'green') + cap('Esc: the text appears on every line (verified).', '', 'green', y=150, h=34)]
def stage(k, note, tone='blue'):
    items = [('Normal mode', 'card'), ('Ctrl+V → visual block', 'violet'), ('motion 3j → 4 lines selected', 'violet'), ('I → insert on the first line', 'amber'), ('Esc → vim repeats the text on each line', 'green')]
    o = ''.join(label_box(14, 10 + i * 31, 332, 26, [s], tn if i == k else 'card', 8.8) for i, (s, tn) in enumerate(items))
    return o + t(180, 175, note, 8.8, tone, bold=True)
behind = [stage(0, 'Start.'), stage(1, 'Block selection begins.', 'violet'), stage(2, 'A rectangle 1 column × 4 lines.', 'violet'),
          stage(3, 'You type once.', 'amber'), stage(4, 'On Esc, vim inserts it in the other lines.', 'green')]
two = anim_two('Comment out four lines at once', 'Visual block insert',
               'Four lines; Ctrl+V starts a block; 3j selects four lines; I and “# ” type on the first line; Esc copies it to all four.',
               'The steps of a visual block insert: Normal, Ctrl+V, motion, I, Esc repeats the inserted text on each line.', see, behind,
               ['Four lines, cursor on the first.', 'Ctrl+V starts a visual block.', '3j selects the first column of four lines.', 'I and “# ”: while typing, only line 1 shows it.', 'Esc: the text is inserted on every line (real result: four commented lines).'],
               ['Normal mode.', 'Block mode selects a rectangle.', 'The motion sets its height.', 'Insert mode for the first line.', 'Esc applies the insert to all lines of the block.'])

dx = dissect('Layer by layer: :%s/localhost/db.internal/gc',
    'Each part of the command, with a real run on our build machine (vim batch mode or perl/sed for comparison).', [
    dict(key='range', name='%', sub='which lines',
         why='Changes should be limited to where you want them.',
         how='% = 1,$ = every line. Without it, only the current line (in batch mode below, vim starts on the last line, so only a2 changes).',
         impl='ex ranges.', used=':s, :g, :d, :w.',
         cmd="printf 'a1\\na2\\n' > f.txt; vim -u NONE -N -i NONE -es -c 's/a/b/' -c 'wq' f.txt; cat f.txt"),
    dict(key='pat', name='pattern', sub='a regex',
         why='Describe what to find, not where it is.',
         how='vim regex: . * [ ] ^ $, \\( \\) groups, \\v for Perl style.',
         impl='vim’s regex engine.', used='/, :s, :g.',
         cmd="printf 'port=80\\n' > f.txt; vim -u NONE -N -i NONE -es -c '%s/\\v(\\d+)/[\\1]/' -c 'wq' f.txt; cat f.txt"),
    dict(key='g', name='g flag', sub='every match',
         why='Lines can contain the word more than once.',
         how='Without g only the first match per line is replaced.',
         impl='Substitute flags.', used='Nearly always.',
         cmd="printf 'x,x,x\\n' > f.txt; vim -u NONE -N -i NONE -es -c 's/x/y/' -c 'wq' f.txt; cat f.txt"),
    dict(key='same', name='Same in sed', sub='scripts',
         why='Automate what you did by hand.',
         how='sed uses the same s/// syntax (Lesson 6.4).',
         impl='Both come from ed.', used='CI, scripts.',
         cmd="printf 'db=localhost\\n' | sed 's/localhost/db.internal/g'"),
], hint='Each part of one command. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Block insert, step by step</h2>
  <p>Left: what you see (the final result is the verified run from the Visual card). Right: what vim does.</p>
''' + two + dx + qc('In a visual block insert, why does the text appear on the other lines only after Esc?', 'vim records what you typed on the first line and repeats it on the others when you leave Insert mode.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world + vimrc
VIMRC = '''set number            " line numbers
set relativenumber    " distance to other lines (great with 5j, 3dd)
set ignorecase smartcase
set incsearch hlsearch
set expandtab tabstop=4 shiftwidth=4   " spaces, 4 wide (Python, YAML)
set autoindent
syntax on
filetype plugin indent on
'''
vimrc = '''  <h3 id="vimrc">Your ~/.vimrc</h3>
  <p>Settings typed after <code>:</code> last until you quit. Put them in <code>~/.vimrc</code> to have them every time. A good starting file:</p>
  <div class="code" data-lang="text" data-file="~/.vimrc"><pre><code>''' + E(VIMRC.rstrip()) + '''</code></pre></div>
''' + (lambda r: f'''  <p class="wx__label">Check that vim really reads it (real run)</p>
  <div class="code" data-lang="bash" data-file="Terminal"><pre><code>vim -u ~/.vimrc -e -c 'redir! &gt; /tmp/o.txt | set number? shiftwidth? expandtab? | redir END' -c 'q'
cat /tmp/o.txt</code></pre><div class="output">{E(r)}</div></div>
''')(shlesson.run_sh("cat > ~/.vimrc <<'EOF'\n" + VIMRC + "EOF\nvim -u ~/.vimrc -i NONE -e -c 'redir! > /tmp/o.txt | set number? shiftwidth? expandtab? | redir END' -c 'q' < /dev/null > /dev/null 2>&1; tr -s ' \\n' ' ' < /tmp/o.txt; echo; rm -f ~/.vimrc /tmp/o.txt", 'any').strip())

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>vim power use at work</h2>
''' + usecase(term(8, 14, 104, 62, [(':%s/old/', 'prompt'), ('new/gc', 'acc')], title='ops', size=6.4, step=12),
              '1. Migrations', 'Changing host names, ports or paths across a config, with confirmation, during a migration.', ['Old host', '*:%s…gc', 'new host']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['vimdiff', 'two servers'], 'violet', 8.6), '2. Comparing configs',
    'Admins compare a working and a broken server’s config side by side with vimdiff.', ['Two files', '*vimdiff', 'the difference']) + '\n' + usecase(
    term(8, 14, 104, 62, [('Ctrl+V', 'prompt'), ('I# Esc', 'acc')], title='dev', size=6.4, step=12),
    '3. Disabling blocks of code', 'Developers comment out blocks, indent YAML and fix columns with visual block mode.', ['Block', '*Ctrl+V', 'done']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['qa … q', '@a ×300'], 'amber', 8.6), '4. One-off data fixes',
    'Analysts use macros to reshape a few hundred irregular lines that no regex fits.', ['Messy lines', '*macro', 'clean data']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + vimrc + oneliners('The same power commands in batch mode (vim -es), really run on our build machine; handy in scripts.', [
    dict(level='b', title='Replace everywhere from the shell', scenario='Change localhost in a config without opening vim.', setup="printf 'db=localhost\\nweb=localhost\\n' > h.conf",
         cmd="vim -u NONE -N -i NONE -es -c '%s/localhost/db.internal/g' -c 'wq' h.conf && cat h.conf",
         explain='The exact :%s from this lesson, run by a script.'),
    dict(level='i', title='Delete comment lines', scenario='Strip comments before comparing.', setup="printf 'a=1\\n# x\\nb=2\\n' > c.conf",
         cmd="vim -u NONE -N -i NONE -es -c 'g/^#/d' -c 'wq' c.conf && cat c.conf",
         explain=':g/^#/d in batch mode.'),
    dict(level='a', title='Sort unique, in place', scenario='A list with duplicates.', setup="printf 'b\\na\\nb\\nc\\n' > l.txt",
         cmd="vim -u NONE -N -i NONE -es -c 'sort u' -c 'wq' l.txt && cat l.txt",
         explain=':sort u removes duplicates while sorting.'),
]) + which('Choosing the right power tool.', [
    ('Same text change everywhere', ':%s/a/b/g', 'One command.', 'Forgetting g.'),
    ('Careful change', ':%s/a/b/gc', 'Confirm each.', 'Blind replace on production.'),
    ('Delete lines by pattern', ':g/re/d', 'Fast.', 'Deleting one by one.'),
    ('A column / block', 'Ctrl+V', 'Rectangle.', 'Using :s for positions.'),
    ('Irregular repeated edit', 'macro qa…q @a', 'Records anything.', 'Doing it 300 times by hand.'),
    ('Compare two files', 'vimdiff a b', 'Side by side.', 'Reading both by eye.'),
    ('Same change in many files', 'sed -i (6.4)', 'Scriptable.', 'Opening each file.'),
]) + keys('Power keys of this lesson.', [
    (':%s/a/b/gc', 'replace all, confirm', 'y n a q'),
    (':g/re/d  :v/re/d', 'delete matching / non-matching lines', ':g/^#/d'),
    ('v V Ctrl+V', 'select chars / lines / block', 'Ctrl+V 3j I# Esc'),
    ('> <  ~  U u', 'indent, unindent, case', 'Vj>'),
    ('.  qa…q  @a  @@', 'repeat, record, play, play again', '3@a'),
    ('"ayy "ap  :reg', 'named registers', '"0p'),
    ('ciw ci" dap', 'text objects', 'ci"'),
    (':sp :vsp Ctrl+W w', 'split, vertical split, switch', ':vsp other.conf'),
    (':r !cmd  :%!cmd', 'insert / filter through a command', ':%!sort'),
]) + scriptit('migrate-host.sh', 'Apply the same vim substitution to several config files, with a backup and a count of changed lines per file.',
'''#!/bin/bash
old=localhost new=db.internal
printf 'db=localhost\\n' > a.conf; printf 'web=localhost\\ncache=localhost\\n' > b.conf   # demo
for f in *.conf; do
  cp "$f" "$f.bak"
  n=$(grep -c "$old" "$f")
  vim -u NONE -N -i NONE -es -c "%s/$old/$new/ge" -c 'wq' "$f"
  echo "$f: $n line(s) changed"
done
cat a.conf b.conf''',
'<p>The <code>e</code> flag stops vim from failing on files without a match. In larger scripts, <code>sed -i</code> is the more common tool (Lesson 6.4).</p>') + puzzle_answer('One “localhost” remains: without <code>g</code>, <code>:s</code> replaces only the <b>first</b> match on each line, giving <code>db=db.internal,backup=localhost</code>. Adding the <code>g</code> flag (<code>:%s/localhost/db.internal/g</code>) replaces every match on every line.') + qc('How do you add “;” at the end of 10 lines with visual block?', 'Ctrl+V, 9j, $, A;, Esc.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-vim-basics-modes-moving-editing-and-saving/">Lesson 4.2</a>: modes and the basic keys.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
