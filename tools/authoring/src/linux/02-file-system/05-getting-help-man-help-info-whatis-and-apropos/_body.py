import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

cmap = concept_map(
    [('1.6', 'Command, options, arguments', 'what you are looking up'), ('2.2', 'Builtins', 'cd and pwd live inside bash')],
    ['--help: the quick summary', 'man: the full manual, sections 1–8', 'reading a SYNOPSIS line', 'whatis and apropos: find the right command', 'help for builtins, info for GNU tools'],
    [('3.1', 'Creating files', 'look up every new command'), ('7.2', 'which, type, whereis', 'where a command lives'), ('8.1', '/etc/passwd', 'man 5 passwd'), ('21.2', 'Cheat sheet', 'your own notes')],
    'Nobody remembers every option. Professionals know how to find them in ten seconds, offline.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 300, 124, ['$ # server has no internet...', '$ # how do I sort ls by size?', '$ ls --help | grep size', ('  -S    sort by file size, largest first', 'acc'), '$ ls -lS', ('(biggest file on top)', 'out')], title='riya@app-01', prompt='$', size=8.2)
      + t(350, 36, 'No browser, no problem:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(350, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• --help: quick summary', '• man: the full manual', '• apropos: which command?', '• help: for builtins', '• all already installed'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The manual is already on the server</h2>
  <div class="story">
''' + puzzle('On her Ubuntu laptop Riya types <code>man cd</code> and gets “No manual entry for cd”, yet <code>man ls</code> works. Is cd undocumented? Where is its help? (Hint: remember from Lesson 2.2 what kind of command cd is.)') + '''
    <p class="narration">Riya is on a production server with no internet access. She needs to sort files by size and cannot remember the option. She is about to message Kabir when Arjun Sir stops her.</p>
''' + scene('A terminal on a server with no internet: ls --help piped to grep finds the -S option for sorting by size.', sc,
            'Every Linux system ships with <tspan font-weight="700" class="s-acc">its own documentation</tspan>.') + '''
A> Before you ask anyone, ask the system. Try <code>ls --help | grep size</code>.
R> <code>-S</code>, sort by file size! It was there all along.
K> For the full story, <code>man ls</code>: the manual page. Space to scroll, <code>/</code> to search, <code>q</code> to quit. And if you don’t even know the command’s name, <code>apropos</code> searches all the manual descriptions.
A> There are a few help systems, each with a job: <code>--help</code> for a quick summary, <code>man</code> for the complete reference, <code>whatis</code> and <code>apropos</code> to find commands, <code>help</code> for commands built into bash, and <code>info</code> for the long GNU manuals. Today you learn all of them, and how to read the strange brackets in a usage line.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
book = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A library: the label on the spine is whatis, the catalogue is apropos, the back cover summary is --help, the full book is man, the long textbook is info.">'
        + ''.join(label_box(16 + k * 124, 24, 112, 92, [a, b, c], tone, 9) for k, (a, b, c, tone) in enumerate([
            ('Spine label', 'whatis', 'one line', 'card'), ('Library catalogue', 'apropos', 'search by topic', 'violet'),
            ('Back cover', '--help', 'quick summary', 'green'), ('The full book', 'man', 'complete reference', 'blue'), ('Long textbook', 'info', 'chapters, links', 'amber')]))
        + t(320, 150, 'Do not know the name? Catalogue (apropos). Know the name? Back cover first (--help),', 9.2, 'ink2')
        + t(320, 170, 'then the full book (man) when you need every detail.', 9.2, 'acc', bold=True)
        + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Getting help at four depths', [
    ('v', 'No jargon: a library on your computer', '''      <p>Your Linux comes with a whole library of instructions, already installed.</p>''' + book + '''
      <ul>
        <li>Each command has a short <b>summary</b> (like the back cover of a book) and a full <b>manual</b> (the whole book).</li>
        <li>If you do not know which command you need, you search the <b>catalogue</b> by topic.</li>
        <li>No internet is needed: it is all on the machine.</li>
      </ul>'''),
    ('b', 'The four commands to start with', '''      <ul>
        <li><code>command --help</code> (or <code>-h</code> for some tools): a quick list of options, printed straight to the screen.</li>
        <li><code>man command</code>: the manual page. Keys: <b>Space</b> next page, <b>b</b> back, <b>/word</b> search, <b>n</b> next match, <b>q</b> quit.</li>
        <li><code>whatis command</code>: a one-line description. <code>apropos word</code> (same as <code>man -k word</code>): every command whose description mentions the word.</li>
        <li><code>help cd</code>: help for commands built into bash (cd, pwd, echo, export…), which have no man page of their own.</li>
      </ul>'''),
    ('i', 'Reading manuals like a professional', '''      <ul>
        <li>Manuals are split into numbered <b>sections</b>: 1 user commands, 5 file formats, 8 admin commands (table below). <code>man 5 passwd</code> explains the file <code>/etc/passwd</code>; <code>man passwd</code> shows the command.</li>
        <li>A man page has standard parts: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, EXAMPLES, SEE ALSO.</li>
        <li>In a SYNOPSIS, <code>[ ]</code> = optional, <code>...</code> = may repeat, UPPERCASE or <i>underlined</i> = replace with your value, <code>a|b</code> = one or the other.</li>
        <li>Combine with filters: <code>ls --help | grep -i time</code>, <code>man -k compress</code>, <code>man -f printf</code> (= whatis).</li>
        <li><code>info coreutils</code> holds long GNU manuals with chapters and links; many <code>--help</code> outputs end with “Full documentation … info '(coreutils) ls invocation'”.</li>
      </ul>'''),
    ('a', 'Behind the screen: where the docs live', '''      <ul>
        <li>Man pages are compressed text files in <b>roff</b> format, e.g. <code>/usr/share/man/man1/ls.1.gz</code>. <code>man</code> finds the file, formats it with <b>groff</b> and shows it with a <b>pager</b> (<code>less</code>, or <code>$MANPAGER</code>).</li>
        <li><code>whatis</code> and <code>apropos</code> do not read every page: they search an index database built by <code>mandb</code> (run daily by a timer, or by hand with <code>sudo mandb</code>).</li>
        <li><code>--help</code> text is compiled into the program itself, so it always matches the installed version; man pages come with the package and can be removed (minimal Docker images often do this; Ubuntu’s <code>unminimize</code> restores them).</li>
        <li><code>help</code> exists because builtins are part of bash: their documentation is inside bash, and <code>man bash</code> covers them all in one huge page.</li>
        <li>Section suffixes: <code>1p</code> = POSIX version, <code>3p</code> = Perl, <code>ssl</code>… <code>man -a name</code> shows every section in turn.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>man, --help, info, whatis, apropos and help</h2>
''' + def_block(
    'Linux systems include offline documentation. <code>man</code> displays <b>manual pages</b>, organised in numbered sections, each describing one command, file format or interface. Most programs print a usage summary with the option <code>--help</code>. <code>whatis</code> shows the one-line description of a page, and <code>apropos</code> (<code>man -k</code>) searches those descriptions by keyword. The bash builtin <code>help</code> documents shell builtins, and <code>info</code> reads the longer, hyperlinked Texinfo manuals of GNU software.',
    '<code>--help</code> for a quick look, <code>man</code> for everything, <code>apropos</code> when you do not know the name, <code>help</code> for builtins.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Man page', f'The manual entry for one command or file. {gl("man-page-and-sections", "Glossary →")}'),
    ('Section', 'A numbered part of the manual: 1 commands, 5 files, 8 admin…'),
    ('whatis / apropos', f'One-line description / keyword search. {gl("apropos-and-whatis", "Glossary →")}'),
    ('info pages', f'Long GNU manuals with links. {gl("info-pages", "Glossary →")}'),
    ('Builtin', f'A command inside bash; use help. {gl("builtin-vs-external-command", "Glossary →")}'),
    ('SYNOPSIS', 'The usage line: how to type the command.'),
    ('Pager', 'The program that scrolls long text: less.'),
    ('Option, argument', f'The parts you look up. {gl("command-option-and-argument", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('man', 'manual', 'The Unix Programmer’s Manual, since 1971.'),
    ('whatis', 'what is (it)?', 'One line: what is this command?'),
    ('apropos', 'French “à propos”: about', 'Find commands about a topic.'),
    ('info', 'information', 'GNU’s Texinfo documentation.'),
    ('--help', 'help option', 'Built into the program.'),
    ('help', 'bash builtin help', 'For cd, echo, export, read…'),
    ('man -k', 'keyword', 'Same as apropos.'),
    ('man -f', 'f = whatis', 'Same as whatis.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Quick options list', '<code>ls --help</code> (pipe to <code>grep</code> or <code>less</code>)'),
    ('Full manual', '<code>man ls</code> · Space / b / <code>/word</code> / n / q'),
    ('Do not know the command', '<code>apropos copy</code> or <code>man -k copy</code>'),
    ('File format manual', '<code>man 5 passwd</code>, <code>man 5 crontab</code>'),
    ('Builtins (cd, echo, export)', '<code>help cd</code> (and <code>type cd</code> to check)'),
    ('Index out of date', '<code>sudo mandb</code>'),
]) + '\n' + lv + didyou('The first <i>Unix Programmer’s Manual</i> was written by Ken Thompson and Dennis Ritchie in November 1971, and it already used numbered sections. The format has barely changed in over fifty years, which is why old man pages and new ones look so alike.') + '''
EXAM> “Explain the man command and the sections of the manual” → man shows manual pages; list sections 1 (user commands), 2 (system calls), 3 (library functions), 4 (special files), 5 (file formats), 6 (games), 7 (miscellaneous), 8 (administration); example man 5 passwd vs man 1 passwd; mention whatis, apropos and --help.
''' + qc('You want the manual of the <b>file</b> <code>/etc/crontab</code>, not the command <code>crontab</code>. What do you type?', '<code>man 5 crontab</code>: section 5 is file formats.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which help system for which question?</h2>
''' + table(['Tool', 'Gives you', 'Works for', 'Example'], [
    ['<code>--help</code>', 'short usage and options', 'almost every program', '<code>cp --help</code>'],
    ['<code>man</code>', 'full reference page', 'installed commands, files, functions', '<code>man rsync</code>'],
    ['<code>whatis</code> / <code>man -f</code>', 'one-line description', 'any name with a man page', '<code>whatis tar</code>'],
    ['<code>apropos</code> / <code>man -k</code>', 'commands matching a keyword', 'when you do not know the name', '<code>apropos partition</code>'],
    ['<code>help</code>', 'builtin documentation', 'bash builtins only', '<code>help export</code>'],
    ['<code>info</code>', 'long manual with chapters', 'GNU tools (coreutils, bash, tar)', '<code>info coreutils</code>'],
    ['<code>/usr/share/doc/pkg</code>', 'README, changelog, examples', 'installed packages', '<code>ls /usr/share/doc/git</code>'],
    ['<code>tldr</code> (optional)', 'community examples', 'popular commands (install it)', '<code>tldr tar</code>'],
], minw=600) + '''
  <h3>The sections of the manual</h3>
''' + table(['Section', 'Contains', 'Example'], [
    ['1', 'User commands', '<code>man 1 ls</code>'],
    ['2', 'System calls (kernel functions)', '<code>man 2 open</code>'],
    ['3', 'Library functions (C)', '<code>man 3 printf</code>'],
    ['4', 'Special files (devices)', '<code>man 4 null</code>'],
    ['5', 'File formats and configuration files', '<code>man 5 passwd</code>'],
    ['6', 'Games', '<code>man 6 fortune</code>'],
    ['7', 'Overviews and conventions', '<code>man 7 hier</code>, <code>man 7 regex</code>'],
    ['8', 'System administration commands (often need root)', '<code>man 8 mount</code>'],
], minw=440) + didyou('That is why manuals write commands with a number in brackets: <code>ls(1)</code>, <code>passwd(5)</code>, <code>open(2)</code>. The number tells you which section to open, as in <code>man 2 open</code>.') + qc('<code>printf</code> exists in section 1 (a command) and section 3 (a C function). Which does <code>man printf</code> show?', 'Section 1: man searches sections in order and shows the first match. Use <code>man 3 printf</code> for the C function, or <code>man -a printf</code> for all.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From “I don’t know the command” to the exact option</h2>
''' + stepper([
    ('1. Search by topic', '<p><code>apropos compress</code> lists gzip, bzip2, xz, zip…</p>', 'Behind the screen: apropos searches the NAME lines in the mandb index, not the full pages.'),
    ('2. Check one candidate', '<p><code>whatis gzip</code>: “compress or expand files”.</p>', 'Behind the screen: the same index, exact name match.'),
    ('3. Quick summary', '<p><code>gzip --help</code>: the options at a glance.</p>', 'Behind the screen: the text is built into the gzip program itself.'),
    ('4. Find one option fast', '<p><code>gzip --help | grep -i keep</code> → <code>-k, --keep</code>.</p>', 'Behind the screen: help text is just output, so any filter works on it.'),
    ('5. Full details when needed', '<p><code>man gzip</code>, then type <code>/keep</code> and Enter, <code>n</code> for the next match, <code>q</code> to quit.</p>', 'Behind the screen: man formats ls.1.gz-style roff files and opens them in less.'),
    ('6. Try it safely', '<p>Test on a copy in a scratch folder before using it on real data.</p>', 'Behind the screen: reading is not enough; one test run removes all doubt.'),
]) + qc('In <code>man</code>, how do you search for the word “recursive” and jump to the next match?', 'Type <code>/recursive</code> and press Enter; press <code>n</code> for the next match (<code>N</code> for the previous).') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
see = [term(20, 18, 320, 100, ['$ man cd', ('No manual entry for cd', 'err')], title='riya@laptop', size=8.2) + t(180, 150, 'cd seems to have no manual…', 9, 'ink2'),
       term(20, 18, 320, 100, ['$ type cd', ('cd is a shell builtin', 'acc')], title='riya@laptop', size=8.2) + t(180, 150, 'type: cd is inside bash.', 9, 'ink2'),
       term(20, 18, 320, 100, ['$ help cd', ('cd: cd [-L|[-P [-e]] [-@]] [dir]', 'acc'), ('    Change the shell working directory.', 'out')], title='riya@laptop', size=8.2) + t(180, 150, 'help: documentation for builtins.', 9, 'green', bold=True),
       term(20, 18, 320, 100, ['$ type ls', ('ls is /usr/bin/ls', 'acc'), '$ ls --help | head -1', ('Usage: ls [OPTION]... [FILE]...', 'out')], title='riya@laptop', size=8.2) + t(180, 150, 'ls is a program: --help and man work.', 9, 'ink2'),
       term(20, 18, 320, 100, ['$ man ls', ('LS(1)       User Commands       LS(1)', 'acc'), ('NAME', 'out'), ('     ls - list directory contents', 'out')], title='riya@laptop', size=8.2) + t(180, 150, 'man: the full manual page.', 9, 'green', bold=True)]
def route(hl, note, tone='blue'):
    items = [('your command', 'acc'), ('builtin? → bash’s own help text', 'violet'), ('program? → --help text inside the binary', 'green'), ('man → /usr/share/man/…gz → groff → less', 'blue')]
    o = ''.join(label_box(14, 14 + k * 40, 332, 32, [s], tn if k in hl else 'card', 8.8) for k, (s, tn) in enumerate(items))
    return o + t(180, 192, note, 8.8, tone, bold=True)
behind = [route([0, 3], 'man finds no ls-like file for cd: no page.', 'red'),
          route([0, 1], 'type asks bash how it would run the name.', 'violet'),
          route([0, 1], 'The builtin’s documentation is compiled into bash.', 'violet'),
          route([0, 2], 'For a program, --help is printed by the program.', 'green'),
          route([0, 3], 'man reads /usr/share/man/man1/ls.1.gz.', 'blue')]
two = anim_two('Help for cd vs help for ls', 'Which help system answers?', 'A terminal: man cd and cd --help fail, type cd shows a builtin, help cd works, while ls has --help and a man page.',
               'The route a help request takes: builtin help inside bash, help text inside a program, or a man page file formatted by groff and shown in less.', see, behind,
               ['<code>man cd</code> finds nothing on a standard Ubuntu install. (Some systems open the bash builtins page instead.)',
                '<code>type cd</code> explains why: cd is built into bash.',
                '<code>help cd</code> prints the builtin’s documentation (in bash 4.4 and later, <code>cd --help</code> prints the same text).',
                '<code>ls</code> is a separate program, so it answers <code>--help</code> itself.',
                'And it has a man page in section 1.'],
               ['A man page is a file installed by a package. bash does not install one per builtin.',
                '<code>type</code> tells you which route applies: builtin, alias, function or file.',
                'Builtin help is stored inside bash; <code>help</code> prints it.',
                'Programs print their own <code>--help</code>, so it always matches the installed version.',
                '<code>man</code> locates the compressed roff file, formats it and opens it in the pager.'])

# scenario 1: apropos
a1 = term(14, 14, 332, 104, ['$ # “how do I see disk partitions?”', '$ apropos partition', ('cfdisk (8)   - display or manipulate a disk partition table', 'out'), ('fdisk (8)    - manipulate disk partition table', 'out'), ('parted (8)   - a partition manipulation program', 'out')], title='riya@laptop', size=7.2) + cap('apropos searches every one-line description.', '', 'blue', y=150, h=34)
a2 = term(14, 14, 332, 104, ['$ apropos "block device"', ('blkid (8)    - locate/print block device attributes', 'out'), ('lsblk (8)    - list block devices', 'acc')], title='riya@laptop', size=7.2) + cap('Those tools change disks. Another keyword finds lsblk.', '', 'blue', y=150, h=34)
a3 = term(14, 14, 332, 104, ['$ lsblk --help | head -3', ('Usage:', 'out'), (' lsblk [options] [<device> ...]', 'acc')], title='riya@laptop', size=7.4) + cap('--help: how to call it.', '', 'blue', y=150, h=34)
a4 = term(14, 14, 332, 104, ['$ apropos partition | wc -l', ('0', 'err'), ('$ sudo mandb', 'prompt'), ('... index rebuilt', 'dim')], title='riya@laptop', size=7.4) + cap('Empty results? The index may be missing: sudo mandb.', '', 'red', y=150, h=34)
a5 = (t(180, 30, 'Finding the right command', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• apropos word  (or man -k word)', '• several words: apropos -a copy file', '• narrow by section: apropos -s 8 disk', '• read the descriptions, then --help, man'])) + cap('Search by what you want to do, not by name.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', '“There must be a command for this…”',
              'Riya needs to list the disk partitions of a server and does not know the command. Typical output on Ubuntu 24.04 (shortened; your list may differ).',
              'apropos and --help', 'apropos partition lists partition editors, apropos block device finds lsblk, --help shows usage, and mandb rebuilds an empty index.', [a1, a2, a3, a4, a5],
              ['<code>apropos partition</code> lists every command whose one-line description mentions “partition”.',
               'Those tools <b>manipulate</b> partition tables: risky for a simple look. Searching “block device” finds <code>lsblk</code>, which only lists disks and partitions (Lesson 15.1).',
               'Then <code>lsblk --help</code> shows how to call it.',
               'If apropos finds nothing at all, the index may be missing or old: <code>sudo mandb</code> rebuilds it.',
               'Habit: describe the task in one word, apropos it, then narrow down.'],
              hid='scenario-apropos')

# scenario 2: reading a synopsis
def syn(hl, note, tone='blue'):
    parts = [('cp', 'command'), ('[OPTION]...', 'optional, repeatable'), ('SOURCE', 'your value'), ('DEST', 'your value')]
    o, x = '', 14
    for k, (p, d) in enumerate(parts):
        w = 40 + len(p) * 5.5
        o += label_box(x, 30, w, 46, [p, d], 'acc' if k in hl else 'card', 8.6)
        x += w + 8
    return o + t(180, 110, note, 9, tone, bold=True)
r1 = syn([0], 'The command name: type it exactly.') + cap('Usage: cp [OPTION]... SOURCE DEST', '', 'card', y=150, h=34)
r2 = syn([1], '[ ] = optional · ... = as many as you like.') + cap('cp -r -v …  or no option at all.', '', 'blue', y=150, h=34)
r3 = syn([2, 3], 'UPPERCASE = replace with your own value.') + cap('cp notes.txt backup.txt', '', 'blue', y=150, h=34)
r4 = label_box(14, 26, 332, 54, ['or:  cp [OPTION]... SOURCE... DIRECTORY', 'SOURCE... = one or more sources, then a folder'], 'violet', 8.8) + t(180, 110, 'Several “or:” lines = several ways to call it.', 9, 'violet', bold=True) + cap('cp a.txt b.txt c.txt backup/', '', 'violet', y=150, h=34)
r5 = (t(180, 30, 'SYNOPSIS notation', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start', mono=True) for k, s in enumerate(['[x]   optional', 'x...  repeat x', 'X     your value (or underlined)', 'a|b   a or b, not both'])) + cap('Read it once, and every man page makes sense.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Decoding a usage line',
              'The first line of <code>cp --help</code> (real output on our build machine) looks cryptic. Every symbol has a meaning.',
              'Reading a SYNOPSIS', 'The cp usage line broken into command, optional repeatable options, and placeholders, plus the alternative form with several sources.', [r1, r2, r3, r4, r5],
              ['The first word is the command itself.',
               '<code>[OPTION]...</code>: options are optional (brackets) and you may give several (dots).',
               'Capital words are placeholders: put your real file names there.',
               'The “or:” line is a second form: many sources, then a directory.',
               'These conventions are the same in <code>--help</code> output and in man page SYNOPSIS sections.'],
              hid='scenario-synopsis')

# scenario 3: man sections
n1 = term(14, 14, 332, 104, ['$ whatis passwd', ('passwd (1)   - change user password', 'out'), ('passwd (5)   - the password file', 'acc')], title='riya@laptop', size=7.6) + cap('One name, two manual pages.', '', 'card', y=150, h=34)
n2 = term(14, 14, 332, 104, ['$ man passwd', ('PASSWD(1)     User Commands     PASSWD(1)', 'acc'), ('NAME  passwd - change user password', 'out')], title='riya@laptop', size=7.6) + cap('Without a number: the first section found (1).', '', 'blue', y=150, h=34)
n3 = term(14, 14, 332, 104, ['$ man 5 passwd', ('PASSWD(5)  File Formats  PASSWD(5)', 'acc'), ('NAME  passwd - the password file', 'out'), ('... name:password:UID:GID:GECOS:dir:shell', 'dim')], title='riya@laptop', size=7.6) + cap('Section 5 explains the format of /etc/passwd.', '', 'blue', y=150, h=34)
n4 = term(14, 14, 332, 104, ['$ man 5 crontab', '$ man 5 sshd_config', '$ man 7 hier', ('(file formats and overviews)', 'dim')], title='riya@laptop', size=7.6) + cap('Admins use sections 5 and 7 all the time.', '', 'blue', y=150, h=34)
n5 = (t(180, 30, 'Pick the right section', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• 1 commands · 8 admin commands', '• 5 config files: passwd, fstab, crontab', '• 2 and 3 for programmers: open, printf', '• whatis name shows which exist'])) + cap('passwd(5) = section 5 of passwd.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The command or the file? Manual sections',
              'Riya must explain the columns of <code>/etc/passwd</code> in a ticket. The command’s manual will not help; the file’s manual will. Typical output on Ubuntu (shortened).',
              'Manual sections', 'whatis passwd shows sections 1 and 5; man passwd opens the command; man 5 passwd opens the file format; other section 5 and 7 pages.', [n1, n2, n3, n4, n5],
              ['<code>whatis passwd</code> shows two pages: the command (1) and the file (5).',
               'Plain <code>man passwd</code> opens section 1, the command.',
               '<code>man 5 passwd</code> describes each colon-separated field of the file (Lesson 8.1).',
               'Most configuration files have a section 5 page: crontab, sshd_config, fstab.',
               'Use <code>whatis</code> to see which sections exist, then open the one you need.'],
              hid='scenario-sections')

dx = dissect('Layer by layer: dissect a usage line',
    'Take the real first lines of <code>cp --help</code>: <code>Usage: cp [OPTION]... [-T] SOURCE DEST</code>. Open each symbol: what it means, why it exists, where the text really comes from, and where you will meet it. Each comes with a real command and its output on our build machine.', [
    dict(key='usage', name='Usage: cp', sub='the command',
         why='Shows exactly what to type first.',
         how='The first word after “Usage:” is the command name. Several lines starting with “or:” are alternative forms.',
         impl='Text compiled into the cp program (GNU coreutils), printed by its <code>--help</code> code.', used='Every <code>--help</code>; man pages call this part SYNOPSIS.',
         cmd='cp --help | head -3'),
    dict(key='brackets', name='[OPTION]', sub='square brackets',
         why='Some parts are optional; the line must say which.',
         how='Anything in <code>[ ]</code> may be left out. Do not type the brackets themselves.',
         impl='A convention from the first Unix manuals, later fixed by POSIX.', used='<code>ls [OPTION]... [FILE]...</code>: plain <code>ls</code> is valid.',
         cmd='ls --help | head -1'),
    dict(key='dots', name='...', sub='repeatable',
         why='Many commands accept any number of files or options.',
         how='<code>X...</code> = one or more X; <code>[X]...</code> = zero or more.',
         impl='Same convention; in man pages it may be written as an ellipsis.', used='<code>cp a b c dir/</code>, <code>rm f1 f2 f3</code>.',
         cmd='mkdir --help | head -1'),
    dict(key='upper', name='SOURCE DEST', sub='placeholders',
         why='The line cannot know your file names.',
         how='Capital words (or <i>underlined</i> words in man) are placeholders: replace them with real values.',
         impl='In man pages they are set in italics or underline by groff.', used='<code>cp notes.txt backup/</code>.',
         cmd='mv --help | head -2'),
    dict(key='dash', name='-T / --no-target-directory', sub='short and long options',
         why='Short options are quick to type; long ones are readable in scripts.',
         how='One dash + one letter (<code>-T</code>), or two dashes + a word (<code>--no-target-directory</code>). Short ones can be combined: <code>-rv</code>.',
         impl='Parsed by the program, usually with the getopt library (man 3 getopt).', used='Use long options in scripts for clarity.',
         cmd="cp --help | grep -- '-T,'"),
    dict(key='exit', name='Exit status', sub='0 = OK',
         why='Scripts need to know whether a command succeeded.',
         how='Many --help texts and man pages list the meaning of each exit code.',
         impl='The number the program returns to the shell, seen as <code>$?</code> (Lesson 5.4).', used='<code>if ls dir; then …</code>, monitoring, CI jobs.',
         cmd="ls --help | grep -A3 '^Exit status'", expect='any'),
], hint='Six symbols you will see in every manual. Click one.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Where does the help come from?</h2>
  <p>Left: Riya asks for help on cd and ls (outputs shortened; the man page view is typical output). Right: which help system answers, and where its text is stored.</p>
''' + two + '''
  <p>Three real-time scenarios: finding an unknown command, reading a usage line, and choosing the right manual section.</p>
''' + s1 + s2 + s3 + dx + qc('In <code>ls [OPTION]... [FILE]...</code>, is <code>ls</code> with nothing after it valid? Why?', 'Yes: both parts are in square brackets, so both are optional. With no FILE, ls lists the current folder.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Help systems at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ rsync --help', 'prompt'), ('| grep delete', 'acc')], title='server', size=6.4, step=12),
              '1. Offline servers', 'Production servers often have no browser or internet. <code>--help | grep</code> and <code>man</code> answer most questions in seconds.', ['Question', '*--help | grep', 'answer']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ man 5', 'prompt'), ('sshd_config', 'acc')], title='admin', size=6.4, step=12),
    '2. Editing configuration safely', 'Before changing a setting in <code>/etc</code>, admins read its section 5 page to check the exact name and allowed values.', ['Change config', '*man 5', 'no typos']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['--version', 'match docs'], 'amber', 8.6), '3. The right version',
    'Online answers may describe a different version. <code>--help</code> and the local man page always match what is installed; <code>cmd --version</code> confirms it.', ['Online tip', '*check locally', 'works here']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ apropos', 'prompt'), ('firewall', 'acc')], title='new job', size=6.4, step=12),
    '4. Learning an unfamiliar system', 'On a new distribution, <code>apropos</code> reveals which tools exist for a task (firewall, network, disk).', ['New distro', '*apropos', 'right tool']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['interview', 'man -k'], 'green', 8.6), '5. Interviews and exams',
    'Practical exams such as RHCSA and LFCS let you use only the system’s own documentation. Knowing man, apropos and --help is a real skill.', ['Exam room', '*local docs', 'pass']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Getting answers fast. All were really run on our Ubuntu build machine (a minimal image without man pages, so these use --help and help).', [
    dict(level='b', title='Find one option without scrolling', scenario='You remember that ls can sort by time, but not the letter.',
         cmd="ls --help | grep -i 'sort by'",
         explain='Help text is ordinary output: <code>grep -i</code> finds the lines you need, case-insensitively.'),
    dict(level='b', title='Is it a builtin or a program?', scenario='Decide whether to use help or man.',
         cmd='type cd ls echo',
         explain='builtin → <code>help</code>; a file in /usr/bin → <code>--help</code> and <code>man</code>. (echo is both: the builtin wins.)'),
    dict(level='i', title='One-line descriptions of builtins', scenario='A quick glossary of shell builtins.',
         cmd='help -d cd pwd export read',
         explain='<code>-d</code> prints only the short description of each builtin.'),
    dict(level='a', title='Where is the long manual?', scenario='--help ends with a pointer to the full documentation.',
         cmd="ls --help | tail -2; ls /usr/share/info | grep -m3 coreutils",
         explain='GNU tools point to their info manual; the files themselves live in <code>/usr/share/info</code>.'),
], extra=build_up('the option you need, from a long help text', '<code>date --help</code> prints about 100 lines. Riya needs the option that shows a date other than now.',
    '', [
    ('date --help | wc -l', 'Too many lines to read on screen.'),
    ('date --help | grep -i string', 'Lines that mention STRING: the date to display.'),
    ("date --help | grep -- '-d,'", 'Exactly the option: -d, --date=STRING.'),
    ("date -d 'tomorrow' +%A", 'Try it: the name of tomorrow’s day.'),
])) + which('Help situations.', [
    ('Quick list of options', 'cmd --help', 'Fast, matches your version.', 'Searching the web first.'),
    ('One option in a long list', 'cmd --help | grep word', 'No scrolling.', 'Reading 100 lines by eye.'),
    ('Every detail and examples', 'man cmd', 'Complete reference.', '--help (summary only).'),
    ('Do not know the command', 'apropos topic', 'Searches descriptions.', 'man random-guess'),
    ('A config file’s format', 'man 5 name', 'Section 5 = files.', 'man name (opens the command).'),
    ('Help for cd, export, read', 'help cd', 'Builtins live in bash.', 'man cd (often missing).'),
    ('apropos finds nothing', 'sudo mandb', 'Rebuilds the index.', 'Assuming no such command.'),
    ('Exit inside man', 'q', 'Quits the pager.', 'Ctrl+C or closing the terminal.'),
]) + puzzle_answer('cd is a <b>shell builtin</b> (Lesson 2.2): it is part of bash, not a separate program. Man pages are installed for programs and files, so there is no separate page for cd (some systems open the big bash builtins page instead). Bash documents its builtins itself: <code>help cd</code> (modern bash also accepts <code>cd --help</code>). Use <code>type name</code> first to know which help system applies.') + qc('How do you find the man pages related to “compress” if you do not know any command name?', '<code>apropos compress</code> or <code>man -k compress</code>.') + '''
</section>
'''

body = (cmap + story.replace('  <div class="story">', before('<a href="../../01-start-here/06-terminal-console-shell-and-prompt-your-first-commands/">Lesson 1.6</a>: commands, options and arguments.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
