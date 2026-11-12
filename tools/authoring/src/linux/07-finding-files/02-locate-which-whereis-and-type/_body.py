import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# A user-level PATH demo: two "python" programs and an alias, to show which wins.
PATHDEMO = r"""mkdir -p ~/bin ~/venv/bin
printf '#!/bin/sh\necho "python from ~/bin"\n' > ~/bin/mytool; chmod +x ~/bin/mytool
printf '#!/bin/sh\necho "python from venv"\n' > ~/venv/bin/mytool; chmod +x ~/venv/bin/mytool"""

LOC_REC = 'Typical output on Ubuntu (plocate). Our build machine has no locate; options checked against the plocate manual.'

HOOK = hook('Two puzzles from one morning. First: <code>find / -name nginx.conf</code> takes 40 seconds on a big server, but a colleague types <code>locate nginx.conf</code> and gets the answer before her finger leaves Enter. Second: Riya types <code>python3 app.py</code> and gets an error about a missing library, although she installed it. Which <code>python3</code> actually ran? <code>locate</code> searches a ready-made index of file names; <code>which</code>, <code>type</code> and <code>whereis</code> tell you exactly what a command name means.',
    ['find files by name in an instant with <code>locate</code> (<code>-i -b -c -l -e -r --regex</code>), and know when its index is out of date (<code>updatedb</code>)',
     'find out which program runs when you type a command: <code>which</code>, <code>which -a</code>, <code>command -v</code>',
     'tell aliases, functions, builtins, keywords and programs apart with <code>type</code> and <code>type -a</code>',
     'find a command’s binary, source and manual with <code>whereis</code>, and fix “command not found” and wrong-version problems'])
ROAD = roadmap([
    ('story', 'The story', 3, '40 seconds vs 0.1'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What the four tools are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each tool, by field', 16, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'how the shell finds a command'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Where is a file named X? (anywhere, fast)', 'locate X', 'index; may be up to a day old'),
    ('…and only files that still exist', 'locate -e X', 'skips deleted files'),
    ('…a file I created a minute ago', 'sudo updatedb; locate X  or  find', 'the index is not live'),
    ('Which program runs when I type X?', 'which X  /  command -v X', 'first match in $PATH'),
    ('All programs named X on my PATH', 'which -a X  /  type -a X', 'version conflicts'),
    ('Is X an alias, function, builtin or file?', 'type X', 'what the shell will really do'),
    ('Binary, source and manual of X', 'whereis X', 'is the man page installed?'),
    ('In a script: is X installed?', 'command -v X > /dev/null', 'POSIX, reliable'),
    ('Files by size, age, owner', 'find (Lesson 7.1)', 'locate only knows names'),
])

cmap = concept_map(
    [('7.1', 'find', 'live search by any property'), ('12.1', 'PATH', 'where the shell looks for programs'), ('1.6', 'Shell and prompt', 'typing commands')],
    ['locate and updatedb: an index of every file name', 'locate options: -i -b -c -l -e -r --regex -0', 'which and command -v: the program behind a name', 'type: alias, keyword, function, builtin or file', 'whereis: binary, source and manual paths; hash'],
    [('12.3', 'Aliases and history', 'why ll works'), ('14.2', 'apt and dpkg', 'dpkg -S: which package owns a file'), ('12.5', 'Shell scripts', 'command -v checks'), ('17.4', 'cron', 'updatedb runs on a timer')],
    'find is the thorough detective; locate is the phone book; which, type and whereis answer “what exactly is this command?”. Knowing which to use saves minutes every day.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ time find / -name nginx.conf 2>/dev/null', ('/etc/nginx/nginx.conf', 'out'), ('real 0m41.2s', 'err'), '$ time locate nginx.conf', ('/etc/nginx/nginx.conf', 'acc'), ('real 0m0.06s', 'acc'), '$ type python3', ('python3 is /home/riya/venv/bin/python3', 'acc')], title='riya@web01: ~', size=7.0, step=15)
      + t(352, 36, 'Four quick answers:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• locate: where is it?', '• which: which program?', '• type: what kind?', '• whereis: binary + manual', '• updatedb: refresh index'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>40 seconds versus 0.1</h2>
  <div class="story">
''' + puzzle('Riya creates <code>report_final.pdf</code> and immediately runs <code>locate report_final.pdf</code>. Nothing is printed. Then she deletes an old file and <code>locate</code> still lists it. Is locate broken? And a note says “locate is able to find files even after they are deleted”: is that a feature?') + '''
    <p class="narration">A production server, a missing config file, and a Python program that refuses to see its library.</p>
''' + scene('A terminal: find takes 41 seconds to find nginx.conf; locate finds it in 0.06 seconds; type python3 shows a virtual-environment path.', sc,
            'locate reads an <tspan font-weight="700" class="s-acc">index</tspan>; find walks the disk.') + '''
A> locate does not search the disk at all. Once a day a job called <code>updatedb</code> writes every file name into a database; locate just looks in that list. That is why it is instant, and why it can be out of date.
R> And the Python problem?
K> Ask the shell what <code>python3</code> means: <code>type -a python3</code>. There may be two of them, and the first one in your PATH wins.
A> Today: locate and updatedb, then which, type and whereis, each explained, then used by admins, developers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A city: a detective walking every street to find a house (find), a phone directory printed last night (locate), and a receptionist who knows which office a name belongs to (which and type).">'
       + label_box(14, 20, 190, 110, ['find', 'a detective who', 'walks every street', 'slow, always current'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['locate', 'yesterday’s phone book', 'instant lookup', 'new houses missing'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['which / type / whereis', 'the receptionist:', '“that name means', 'office 3, floor 2”'], 'green', 8.6)
       + t(320, 160, 'Three ways to find something: search everything now,', 9.6, 'ink2')
       + t(320, 182, 'look it up in a list, or ask who a name refers to.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('locate, which, whereis and type at four depths', [
    ('v', 'No jargon: a detective, a phone book and a receptionist', '      <p>Think of finding someone in a city.</p>' + pic + '''
      <ul>
        <li><code>find</code> is a detective who walks every street: slow but always right.</li>
        <li><code>locate</code> is a phone book printed last night: instant, but people who moved in today are missing.</li>
        <li><code>which</code>, <code>type</code> and <code>whereis</code> are the receptionist who knows exactly which office a name refers to.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>locate nginx.conf</code>: every path containing that name.</li>
        <li><code>locate -i report</code>: any case; <code>locate -c '*.pdf'</code>: just count.</li>
        <li><code>which python3</code>: the program that runs when you type python3.</li>
        <li><code>type ll</code>: “ll is aliased to ls -alF”.</li>
        <li><code>whereis ls</code>: the ls program and its manual page.</li>
      </ul>'''),
    ('i', 'Indexes, PATH and command types', '''      <ul>
        <li>The index is rebuilt by <code>updatedb</code>, normally once a day by a systemd timer or cron. Files created since are missing; deleted files are still listed (use <code>locate -e</code> to check they exist).</li>
        <li>locate only shows files you are allowed to see, even though the index was built as root.</li>
        <li>When you type a command, the shell checks in order: <b>alias → keyword → function → builtin → a program in $PATH</b> (searched left to right). <code>type</code> shows that order; <code>which</code> only searches $PATH.</li>
        <li><code>which -a</code> and <code>type -a</code> list every match: the answer to “wrong version” problems.</li>
        <li>In scripts use <code>command -v</code> (POSIX, built in) to test whether a command exists.</li>
      </ul>'''),
    ('a', 'Behind the screen: plocate, hashing and PATH order', '''      <ul>
        <li>Ubuntu 22.10+ and Debian 12 use <b>plocate</b> (database <code>/var/lib/plocate/plocate.db</code>, built by <code>updatedb</code> from <code>/etc/updatedb.conf</code>, which skips /tmp, /proc and network mounts). It is a compressed trigram index: a search reads a few kilobytes, not the disk. Older systems use mlocate.</li>
        <li><code>-r</code>/<code>--regex</code> forces a full scan of the database (still much faster than find).</li>
        <li>bash remembers where it found each program (<code>hash</code>). If you install a new version in another folder, bash may keep running the old one until <code>hash -r</code> or a new shell.</li>
        <li><code>which</code> is an external program that knows nothing about aliases or functions; <code>type</code> and <code>command -v</code> are shell builtins and see everything the shell sees.</li>
        <li>Security: a writable folder early in $PATH (like <code>.</code> or <code>~/bin</code> before /usr/bin) lets someone plant a fake <code>ls</code> or <code>sudo</code>. Keep system folders first for root.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>locate, which, whereis and type</h2>
''' + def_block(
    '<code>locate</code> searches a database of file names, built periodically by <code>updatedb</code>, for names matching a pattern. <code>which</code> prints the full path of the executable that would run for a command name, by searching the directories in <code>$PATH</code>. <code>type</code> (a shell builtin) tells how the shell would interpret a name: alias, keyword, function, builtin or file. <code>whereis</code> finds the binary, source and manual-page files of a command in standard locations.',
    'Find a file name instantly, and find out exactly what a command name refers to.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Index / database', 'A prepared list of every file name, used by locate.'),
    ('updatedb', 'The job that rebuilds locate’s database.'),
    ('$PATH', 'The list of folders the shell searches for programs.'),
    ('Alias', 'A short name for a longer command: ll = ls -alF.'),
    ('Builtin', f'A command inside the shell itself: cd, echo, type. {gl("builtin-vs-external-command", "Glossary →")}'),
    ('Keyword', 'Shell syntax words: if, for, [[ .'),
    ('Hash table', 'bash’s memory of where it found each program.'),
    ('Man page', 'The manual: man ls (installed under /usr/share/man).'),
]) + '\n' + names('Where the names come from.', [
    ('locate', 'locate', 'From GNU findutils (1980s); now mlocate and plocate.'),
    ('plocate', 'posting-list locate', 'Uses an index like a search engine.'),
    ('updatedb', 'update database', 'Rebuilds the index.'),
    ('which', '“which one?”', 'Which file runs.'),
    ('whereis', '“where is it?”', 'From 3BSD (1979).'),
    ('type', 'type of command', 'A bash builtin.'),
    ('command -v', 'command, verbose', 'POSIX way to look a name up.'),
    ('hash', 'hash table', 'The shell’s path cache.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Find a file fast', '<code>locate nginx.conf</code>'),
    ('Refresh the index', '<code>sudo updatedb</code>'),
    ('Which program?', '<code>which python3</code>'),
    ('All of them', '<code>type -a python3</code>'),
    ('Alias or program?', '<code>type ll</code>'),
    ('Exists? (scripts)', '<code>command -v git &gt;/dev/null</code>'),
]) + '\n' + lv + didyou('On Ubuntu the locate index is refreshed by a systemd timer called <code>plocate-updatedb.timer</code>, normally once a day. You can see when it will run next with <code>systemctl list-timers | grep updatedb</code> (Lesson 17.3).') + '''
EXAM> “What is the difference between find and locate?” → locate searches a database built by updatedb (fast, may be stale, names only); find searches the file system live (slower, always current, can test size, time, owner and run actions).
''' + qc('Why can <code>locate</code> miss a file you created five minutes ago?', 'Its database was built earlier by updatedb. Run <code>sudo updatedb</code> first, or use find.') + mistake('“Locate is able to find the files even after they are deleted” (listed as an advantage)  ·  “locate -u username: files owned by a user”  ·  “locate -n 10: limit results”',
    'Listing deleted files is a drawback of the stale index: use locate -e to show only files that still exist · locate has no owner option (use find -user) · on plocate the limit option is -l 10 (-n belonged to older mlocate)',
    'Checked against the plocate manual (Ubuntu’s locate since 22.10). The comparison table in the notes is otherwise right: locate is faster, find is current.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>find vs locate, and the five kinds of command names</h2>
''' + table(['', 'find', 'locate'], [
    ['Searches', 'the file system, live', 'a database built by updatedb'],
    ['Speed', 'seconds to minutes', 'milliseconds'],
    ['New files', 'found', 'missing until the next updatedb'],
    ['Deleted files', 'not listed', '<b>still listed</b> (use -e)'],
    ['Tests', 'name, size, time, owner, permission…', 'name / path only'],
    ['Actions', '-exec, -delete', 'none (pipe to xargs)'],
    ['Permissions', 'errors for unreadable folders', 'silently shows only what you may see'],
    ['Installed by default', 'always', 'Ubuntu desktop yes; servers: apt install plocate'],
], minw=560) + table(['Kind', 'Example', 'type says', 'which says'], [
    ['alias', '<code>ll</code>', 'll is aliased to `ls -alF\'', 'nothing (not a file)'],
    ['keyword', '<code>if</code>, <code>[[</code>', 'if is a shell keyword', 'nothing'],
    ['function', '<code>mkcd</code> (yours)', 'mkcd is a function', 'nothing'],
    ['builtin', '<code>cd</code>, <code>echo</code>', 'cd is a shell builtin', 'nothing for cd; /usr/bin/echo for echo'],
    ['file (program)', '<code>ls</code>, <code>python3</code>', 'ls is /usr/bin/ls', '/usr/bin/ls'],
], minw=560) + qc('Why does <code>which cd</code> print nothing?', 'cd is a shell builtin, not a program file in $PATH. Use <code>type cd</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each tool explained, then used in every field</h2>
  <p id="commands">which, type, whereis, command -v and hash were recorded on Ubuntu 24.04. Our build machine has no locate (it is not installed on minimal servers), so locate outputs are <b>typical</b> outputs from Ubuntu with plocate, and every option was checked against the plocate manual.</p>
''' + cmdcard_u(['“where is that file?” when you know (part of) the name', 'searching the whole system in milliseconds', 'counting files of a kind across the disk'],
               ['files created or deleted since the last updatedb', 'searching by size, age or owner (use find)', 'servers where plocate is not installed (find works everywhere)'])(
    'locate', 'locate', 'find file names in an index',
    'Prints every path in the database that contains the pattern (or matches it, if it has * ? [ ]). Shows only files you are allowed to see.',
    'locate [-i] [-b] [-c] [-l N] [-e] [-0] [-r REGEX | --regex ERE] PATTERN...   ·   sudo updatedb', 'safe',
    [('locate nginx.conf', 'paths containing the text', 'find a config'),
     ('-i', 'ignore case', 'Report / report'),
     ('-b', 'match only the file name, not folders', 'fewer false hits'),
     ('-c', 'only count', 'how many?'),
     ('-l 10', 'at most 10 results (plocate)', 'long lists'),
     ('-e', 'only files that still exist', 'stale index'),
     ("--regex '\\.log$'", 'extended regex (scans whole DB)', 'precise patterns'),
     ('-0', 'NUL-separated for xargs -0', 'safe pipelines'),
     ('sudo updatedb', 'rebuild the database now', 'after big changes')],
    dict(cmd='locate nginx.conf', rec=(LOC_REC, '/etc/nginx/nginx.conf\n/usr/share/doc/nginx/examples/nginx.conf'), note='Every path that contains “nginx.conf” anywhere, from the index.'),
    [('sys', [
        dict(situation='Where are all the sshd config files?', cmd="locate -b 'sshd_config'", rec=(LOC_REC, '/etc/ssh/sshd_config\n/usr/share/openssh/sshd_config'),
             why='-b matches the file name only, so folders called sshd_config.d do not produce extra noise.'),
        dict(situation='A file just created is missing: refresh the index.', cmd="touch ~/report_final.pdf\nlocate report_final.pdf; echo \"exit $?\"\nsudo updatedb\nlocate report_final.pdf",
             rec=(LOC_REC, 'exit 1\n/home/riya/report_final.pdf'), why='The first locate finds nothing (exit 1); after updatedb the new file is in the index. That is the first part of the puzzle.')]),
     ('dev', [
        dict(situation='How many Python files are on this machine?', cmd="locate -c '*.py'", rec=(LOC_REC, '18342'),
             why='-c counts without printing 18,000 lines. With * the pattern must match the whole path.')]),
     ('devops', [
        dict(situation='Only results that still exist (after a clean-up).', cmd="rm ~/old_report.pdf\nlocate old_report.pdf\nlocate -e old_report.pdf; echo \"exit $?\"",
             rec=(LOC_REC, '/home/riya/old_report.pdf\nexit 1'), why='The index still lists the deleted file; -e checks the disk. That is the second part of the puzzle: a drawback, not a feature.')]),
     ('sec', [
        dict(situation='Private keys lying around (only those you can read are shown).', cmd="locate --regex '\\.(pem|key)$' | grep -v ssl/certs | head", rec=(LOC_REC, '/home/riya/projects/api/server.key\n/home/riya/Downloads/aws-dev.pem'),
             why='A quick audit of your own files. Run as root to see everything; never leave keys in Downloads.')]),
    ],
    anat=anatomy([('locate', 'cmd', 'command'), ('-i', 'opt', 'ignore case'), ('-b', 'opt', 'name only'), ("'report'", 'arg', 'text or glob to look for')], 'A pattern without * ? [ ] matches anywhere in the path; with them it must match the whole path.')
) + cmdcard_u(['which program runs for a command name', 'debugging “wrong version” problems', 'getting a full path for scripts and cron'],
               ['aliases, functions and builtins (which cannot see them: use type)'])(
    'which', 'which · command -v', 'the program behind a name',
    '<code>which</code> searches each folder of <code>$PATH</code> in order and prints the first executable with that name; <code>-a</code> prints all. <code>command -v</code> is the POSIX builtin equivalent and also knows aliases, functions and builtins.',
    'which [-a] NAME...   ·   command -v NAME', 'safe',
    [('which python3', 'first match in PATH', 'which version runs'),
     ('which -a python3', 'all matches in PATH order', 'conflicts'),
     ('echo $PATH', 'the search order', 'understand the result'),
     ('command -v git', 'POSIX lookup (builtin)', 'scripts'),
     ('command -v git >/dev/null || …', 'is it installed?', 'checks'),
     ('readlink -f $(which python3)', 'follow symlinks to the real file', 'real version')],
    dict(setup=PATHDEMO, cmd="echo \"$PATH\" | tr ':' '\\n' | head -4\nwhich ls python3\nwhich -a ls", note='ls exists twice (in /usr/bin and /bin, the same file on Ubuntu, where /bin is a link to /usr/bin); the first one in PATH wins.'),
    [('dev', [
        dict(situation='Two versions of a tool: which one wins depends on PATH order.', setup=PATHDEMO, cmd="PATH=\"$HOME/bin:$HOME/venv/bin:$PATH\"; which -a mytool; mytool\nPATH=\"$HOME/venv/bin:$HOME/bin:$PATH\"; which mytool; mytool",
             why='Activating a Python virtual environment puts its bin folder first: that is all “activate” really does.'),
        dict(situation='Follow a symlink to the real program.', cmd="readlink -f \"$(which python3)\"",
             why='/usr/bin/python3 is often a link to python3.12 (or similar): the real version.')]),
     ('devops', [
        dict(situation='A deploy script checks its tools first.', cmd="for t in git curl docker; do if command -v \"$t\" > /dev/null; then echo \"$t: $(command -v \"$t\")\"; else echo \"$t: MISSING\"; fi; done",
             why='command -v exits 1 when the name is unknown; fail early with a clear message. (docker is not installed on our build machine.)')]),
     ('sys', [
        dict(situation='Full paths for crontab entries (cron has a short PATH).', cmd="echo \"0 2 * * * $(which tar) czf /backup/etc.tgz /etc\"",
             why='cron runs with PATH=/usr/bin:/bin; full paths avoid “command not found” at 2 a.m. (Lesson 17.4).')]),
    ]
) + mistake('which cd  ·  which ll   (expecting an answer)', 'type cd  ·  type ll   ·   command -v ll',
            'which only searches $PATH for program files. Builtins, aliases and functions are invisible to it, so it prints nothing and exits 1.') + cmdcard_u(['what the shell will really do when you type a name', 'aliases that hide the real command', 'all definitions in order (type -a)'],
               ['shells without type (rare): use command -v'])(
    'type', 'type', 'what kind of command?',
    'A shell builtin that says how a name would be interpreted: alias, keyword, function, builtin or file (with its path). <code>-a</code> lists every definition in the order the shell would try them; <code>-t</code> prints just the kind.',
    'type [-a] [-t] [-p] NAME...', 'safe',
    [('type ls', 'what ls is', 'quick check'),
     ('type -a echo', 'every definition, in order', 'builtin vs /usr/bin/echo'),
     ('type -t NAME', 'one word: alias, keyword, function, builtin, file', 'scripts'),
     ('type -p NAME', 'path only, if it is a file', 'like which'),
     ('type ll', 'shows the alias text', 'what an alias does')],
    dict(cmd="type cd ls if\ntype -a echo\ntype -t cd ls if", note='cd is part of the shell, ls a program, if a keyword. echo exists as a builtin and as programs; the builtin wins.'),
    [('sys', [
        dict(situation='Why does ls show colours, or rm ask before deleting? Check for aliases.', cmd="shopt -s expand_aliases; alias ls='ls --color=auto'; alias rm='rm -i'\ntype ls rm",
             why='Many distributions define aliases in ~/.bashrc. type reveals them; \\rm or command rm skips an alias (Lesson 12.3).')]),
     ('dev', [
        dict(situation='Is my function overriding a real command?', cmd="grep() { echo 'my grep function'; }\ntype -a grep\ncommand grep -c root /etc/passwd",
             why='A function named like a program wins; type -a shows both; command runs the real program.')]),
     ('qa', [
        dict(situation='A script behaves differently for two testers: same command, different kind.', cmd="shopt -s expand_aliases; alias python3='echo using an alias'\ntype -t python3\nunalias python3; type -t python3",
             why='Aliases are not inherited by scripts, so a test that passes in your terminal can fail in CI. Check with type.')]),
    ]
) + cmdcard_u(['finding a program together with its manual page and source', 'checking whether documentation is installed', 'quick look at standard locations'],
               ['which version runs (whereis ignores $PATH order: use which/type)'])(
    'whereis', 'whereis · hash', 'binary, source and manual',
    '<code>whereis</code> searches standard system folders (not $PATH) for a command’s binary (<code>-b</code>), manual pages (<code>-m</code>) and source (<code>-s</code>). <code>hash</code> shows bash’s cache of program paths; <code>hash -r</code> clears it.',
    'whereis [-b|-m|-s] NAME...   ·   hash   ·   hash -r', 'safe',
    [('whereis ls', 'binary + manual + source', 'overview'),
     ('-b', 'binaries only', 'paths'),
     ('-m', 'manual pages only', 'is man installed?'),
     ('-s', 'source only', 'rare today'),
     ('hash', 'remembered program paths and hit counts', 'what bash cached'),
     ('hash -r', 'forget all cached paths', 'after moving programs')],
    dict(cmd="whereis bash ls\nwhereis -b python3", note='On our minimal build machine no manual pages are installed, so only binaries are listed. A desktop Ubuntu shows e.g. <code>ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz</code>.'),
    [('sys', [
        dict(situation='Is the manual for a command installed? (typical desktop output)', cmd='whereis -m tar', rec=('Typical output on Ubuntu desktop (man pages installed)', 'tar: /usr/share/man/man1/tar.1.gz'),
             why='No path after the colon = no man page (minimal images often remove them; run unminimize or install the -doc package).')]),
     ('devops', [
        dict(situation='Installed a new version but the old one still runs: the hash cache.', setup=PATHDEMO, cmd="PATH=\"$HOME/bin:$PATH\"; mytool; hash | grep mytool\ncp ~/venv/bin/mytool /tmp/mytool_new; mkdir -p ~/bin2; mv /tmp/mytool_new ~/bin2/mytool; mv ~/bin/mytool ~/bin/mytool.off\nPATH=\"$HOME/bin2:$PATH\"; hash -r; mytool",
             why='bash remembers the first location; after moving programs, hash -r (or a new terminal) makes it search again.')]),
    ]
) + undo('These tools only read, but they can mislead you.', [
    ('locate shows a file that is gone:', 'use <code>locate -e</code>, or run <code>sudo updatedb</code>.'),
    ('locate misses a new file:', '<code>sudo updatedb</code>, or use find (Lesson 7.1).'),
    ('which shows a program, but something else runs:', 'an alias or function wins: use <code>type -a</code>.'),
    ('Old version keeps running after an upgrade:', '<code>hash -r</code> or open a new terminal; check <code>which -a</code> and PATH order.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='locate nginx.conf', meaning='locate is not installed on this machine (minimal servers, containers).', fix='<code>sudo apt install plocate</code> (then <code>sudo updatedb</code>), or use find.'),
    dict(cmd='which nosuchtool', meaning='Not found in any $PATH folder: which prints nothing and exits 1.', fix='Install it, or add its folder to PATH (Lesson 12.1).'),
    dict(cmd='type nosuchtool', meaning='Not an alias, keyword, function, builtin or file.', fix='Check the spelling; install the package.'),
    dict(cmd='nosuchtool --version', meaning='command not found (127): the shell searched every PATH folder.', fix='Ubuntu often suggests the package to install (command-not-found).'),
]) + qc('A script must stop if <code>jq</code> is not installed. Which line?', "<code>command -v jq &gt;/dev/null || { echo 'jq missing' &gt;&amp;2; exit 1; }</code>") + '''
'''

SCREENS = screens_block('Real terminal screens: type tells the truth', 'In an interactive shell Ubuntu defines aliases like ll. which cannot see them; type can.',
    "printf '%s\\n' 'PS1=\"riya@laptop:~$ \"' \"alias ll='ls -alF'\" > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'which ll; echo \"exit $?\"' Enter", ' after <code>which ll</code>: nothing, exit 1.'),
    ('Enter', "'type ll' Enter", ' after <code>type ll</code>: the alias and what it runs.'),
], 72, 8, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

# ---------------------------------------------------------------- 5. animations
def look(k, note, tone):
    steps = ['alias?', 'keyword?', 'function?', 'builtin?', '$PATH: ~/venv/bin', '$PATH: /usr/bin']
    o = ''
    for i, st in enumerate(steps):
        tn = 'card'
        if i < k:
            tn = 'red'
        if i == k:
            tn = 'green' if k == 4 else 'amber'
        o += label_box(14 + (i % 3) * 112, 14 + (i // 3) * 46, 104, 38, [st], tn, 8)
    return o + t(180, 130, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ python3 app.py'], title='riya@laptop', size=8)] * 5
see = [s + cap(c, '', 'card', y=150, h=34) for s, c in zip(see, ['You type python3…', '…not a keyword…', '…not a function…', '…not a builtin…', '…found in the venv first: that one runs.'])]
behind = [look(0, 'Is python3 an alias? No.', 'violet'), look(1, 'A keyword? No.', 'violet'), look(2, 'A function? No.', 'violet'),
          look(3, 'A builtin? No.', 'violet'), look(4, 'Search PATH left to right: found in ~/venv/bin.', 'green')]
two = anim_two('How the shell finds a command', 'Behind the screen: the lookup order',
               'A terminal where python3 app.py is typed.',
               'Six boxes: alias, keyword, function, builtin, then PATH folders; each is checked in turn until the venv folder matches.', see, behind,
               ['You press Enter.', 'The shell checks its own lists first.', 'Still nothing…', '…and nothing.', 'PATH order decides which python3 runs.'],
               ['1. aliases', '2. keywords', '3. functions', '4. builtins', '5. $PATH folders, first match wins (and is remembered in hash).'])

def idx(k, note, tone):
    o = label_box(14, 14, 150, 110, ['disk (files)', 'report.pdf', 'nginx.conf', 'new_file.txt  (new!)'], 'card', 8)
    o += label_box(196, 14, 150, 110, ['plocate.db', 'report.pdf', 'nginx.conf', ('new_file.txt' if k >= 2 else '— missing —')], 'amber' if k in (1, 2) else 'card', 8)
    o += arrow(166, 70, 192, 70)
    return o + t(180, 150, note, 8.6, tone, bold=True)
frames = [idx(0, 'A new file appears on the disk.', 'violet'), idx(1, 'locate looks only in the database: not found.', 'red'),
          idx(2, 'sudo updatedb copies every name into the database.', 'amber'), idx(3, 'Now locate finds it instantly.', 'green')]
s1 = anim_one('Animated example', 'Why locate can be out of date',
              'The disk and the locate database are two different things.',
              'disk vs index', 'A disk box with three files including a new one, and a database box that is missing the new file until updatedb runs.', frames,
              ['New files are not in the index yet.', 'locate does not look at the disk.', 'updatedb rebuilds the index (daily by default).', 'Then the search is instant again.'], hid='scenario-index')

dx = dissect('Layer by layer: type -a python3',
    'How a command name becomes a program. Each layer has a real command and output from our build machine.', [
    dict(key='alias', name='Aliases', sub='alias',
         why='Shortcuts typed by people.',
         how='Checked first (interactive shells).',
         impl='alias / unalias.', used='ll, la.',
         cmd="shopt -s expand_aliases; alias hi='echo hello'; type -t hi"),
    dict(key='func', name='Functions', sub='name() { … }',
         why='Small reusable code.',
         how='Defined in the shell or ~/.bashrc.',
         impl='Override programs with the same name.', used='Scripts.',
         cmd="greet() { echo hi; }; type -t greet"),
    dict(key='builtin', name='Builtins', sub='inside bash',
         why='Must change the shell itself (cd) or are faster (echo).',
         how='No new process is started.',
         impl='enable -a lists them.', used='cd, echo, type.',
         cmd='type -t cd echo'),
    dict(key='path', name='PATH search', sub='left to right',
         why='Find program files.',
         how='Each folder in $PATH is tried; first executable wins.',
         impl='Result cached in hash.', used='All programs.',
         cmd="echo \"$PATH\" | tr ':' '\\n' | head -3; type -p python3"),
], hint='From the name you type to what runs. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How the shell finds a command, and why locate can be stale</h2>
''' + two + s1 + dx + qc('You installed a new <code>node</code> in /usr/local/bin, but <code>node -v</code> still shows the old version. Two checks?', '<code>type -a node</code> (which one comes first in PATH) and <code>hash -r</code> (bash may have cached the old path).') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>locate, which, type and whereis at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ locate', 'prompt'), ('nginx.conf', 'acc')], title='ops', size=6.4, step=12),
              '1. Finding configs and logs', 'Admins locate configuration files and logs on unfamiliar servers in seconds.', ['Question', '*locate', 'path']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['type -a', 'python3'], 'blue', 8.6), '2. Version conflicts',
    'Developers debug “wrong Python/Node/Java” problems with type -a, which -a and PATH.', ['Bug', '*type -a', 'fix PATH']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['command -v', '|| exit'], 'green', 8.6), '3. Script preconditions',
    'Installers and CI scripts check that every tool exists before starting.', ['Start', '*command -v', 'go / stop']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['which sudo', 'PATH order'], 'red', 8.6), '4. Security',
    'Auditors check that system commands resolve to system folders, not planted copies.', ['Audit', '*which -a', 'clean PATH']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['whereis -m', 'docs'], 'violet', 8.6), '5. Documentation',
    'whereis shows whether manual pages are installed on a minimal image.', ['Need help', '*whereis -m', 'man page']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='What is ls?', scenario='Program, alias or builtin?',
         cmd='type ls cd', explain='type answers for each name.'),
    dict(level='b', title='Where is python3?', scenario='The full path.',
         cmd='which python3', explain='First match in PATH.'),
    dict(level='i', title='Missing tools', scenario='Which of these are not installed?',
         cmd="for t in git curl jq tree; do command -v \"$t\" > /dev/null || echo \"missing: $t\"; done", explain='Exit status of command -v.'),
    dict(level='i', title='PATH, one folder per line', scenario='Read the search order.',
         cmd="echo \"$PATH\" | tr ':' '\\n' | nl | head -4", explain='tr splits; nl numbers (Lesson 6.2).'),
    dict(level='a', title='Programs with the same name twice', scenario='Find duplicates across PATH folders (conflicts).',
         cmd="for d in $(echo \"$PATH\" | tr ':' ' '); do ls \"$d\" 2>/dev/null; done | sort | uniq -d | head -3", explain='List every PATH folder, then uniq -d (Lesson 6.2).'),
], extra=build_up('the wrong-python investigation', 'Riya finds out why her program cannot see its library.', PATHDEMO, [
    ("type -a mytool 2>&1 || echo 'not on PATH yet'", '1. Is mytool on PATH at all?'),
    ("PATH=\"$HOME/bin:$HOME/venv/bin:$PATH\"; type -a mytool", '2. After adding both folders: two copies.'),
    ("PATH=\"$HOME/bin:$HOME/venv/bin:$PATH\"; mytool", '3. The ~/bin one runs: the wrong one.'),
    ("PATH=\"$HOME/venv/bin:$HOME/bin:$PATH\"; hash -r; mytool", '4. Put the venv first (what “activate” does): fixed.'),
])) + which('Choosing the right tool.', [
    ('File by name, fast', 'locate', 'Instant.', 'find / every time.'),
    ('File just created', 'find (or updatedb first)', 'Live.', 'locate alone.'),
    ('Size / age / owner', 'find', 'Tests.', 'locate.'),
    ('Which program runs', 'type -a / which -a', 'Exact order.', 'Guessing.'),
    ('Alias or builtin?', 'type', 'Sees everything.', 'which.'),
    ('Scripts: is it installed?', 'command -v', 'POSIX, builtin.', 'which (not always installed).'),
    ('Manual installed?', 'whereis -m / man -w', 'Paths.', 'Searching by hand.'),
    ('Old version still runs', 'hash -r', 'Clears cache.', 'Rebooting.'),
]) + keys('Shortcuts and handy forms.', [
    ('\\ls  or  command ls', 'skip an alias for one call', '\\rm file'),
    ('type -a NAME', 'everything the name can mean', 'type -a python3'),
    ('hash -r', 'forget cached program paths', 'after installs'),
    ('sudo updatedb', 'refresh the locate index', 'then locate'),
    ('locate -c', 'count only', "locate -c '*.jpg'"),
    ('Alt + .', 'reuse the last argument', 'locate x; vim Alt+.'),
]) + scriptit('need-tools.sh', 'The start of every serious script: check required tools, print where each one is, and stop with a clear message if one is missing.',
'''need() {
  for t in "$@"; do
    if p=$(command -v "$t"); then printf '%-8s %s\\n' "$t" "$p"
    else echo "error: $t is not installed" >&2; return 1; fi
  done
}
need bash grep sed awk && echo "all tools present"
need git jq || echo "stopping: install the missing tool first"''',
'<p>jq is not installed on our build machine, so the second check fails as it should.</p>') + puzzle_answer('locate is not broken: it searches a <b>database</b> built by <code>updatedb</code>, usually once a day. A file created after the last update is not in it (run <code>sudo updatedb</code>), and a deleted file is still in it until the next update. That is a <b>limitation</b>, not a feature: <code>locate -e</code> hides entries whose files no longer exist.') + qc('Which command shows every definition of <code>echo</code> in the order the shell would use them?', '<code>type -a echo</code>') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-find-search-by-name-type-size-time-and-run-exec/">Lesson 7.1</a> (find).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
