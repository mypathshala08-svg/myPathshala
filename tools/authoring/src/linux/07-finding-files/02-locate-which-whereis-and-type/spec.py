import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='07-finding-files', lesson='02-locate-which-whereis-and-type', n='7.2',
    module_label='Module 7 · Finding files and commands',
    title='locate, which, whereis and type',
    desc='locate and updatedb explained (plocate options -i -b -c -l -e -r --regex -0, why the index is stale), then which, which -a, command -v, type and type -a (alias, keyword, function, builtin, file), whereis -b -m -s and hash -r, with the shell lookup order animated and real outputs. Common note mistakes (locate -u user, -n, deleted files as a feature) corrected.',
    og_desc='Find files instantly with locate, and find out exactly which program a command name runs with which, type and whereis.',
    minutes=34, level='Beginner → Advanced',
    lead='locate finds file names in milliseconds from an index; which, type and whereis tell you exactly what a command name means. This lesson explains each, the shell’s lookup order, and how admins, developers, DevOps, security and testers use them.',
    chips=['find vs locate', 'Shell lookup order animated', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# What does each name mean?
type cd ls if
type -a echo
which ls python3
command -v grep
whereis bash
shopt -s expand_aliases; alias ll='ls -alF'; type ll
"""

RUN = dict(
    heading='Ask the shell what a name means',
    intro='<p>Compare type, which, command -v and whereis on builtins, keywords, programs and an alias.</p>',
    code=MAIN,
    anno=[
        ('type -a echo', 'A builtin and programs: the builtin wins.'),
        ("shopt -s expand_aliases; alias ll='ls -alF'; type ll", 'type shows the alias text.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which names are not programs?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each line print? Then run.',
             code="which cd; echo \"which exit=$?\"\ntype -t cd\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the check says git is missing even if it is installed. Fix it.',
             code="if command -v gti > /dev/null; then echo found; else echo missing; fi\n"),
        dict(label='4 · Your turn', hint='Print the folders of $PATH, one per line, numbered.',
             code="echo \"$PATH\" | tr ':' '\\n' | nl\n"),
        dict(label='5 · Challenge', hint='Make a function named ls that prints a message, show type -a ls, then run the real ls with command.',
             code="ls() { echo 'fake ls'; }\ntype -a ls\nls\ncommand ls -d /etc\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: locate and the index',
    intro='<p>locate needs the plocate package and sudo for updatedb. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Install plocate (if locate is missing)', cmd='sudo apt install plocate', output='Setting up plocate (1.1.19-2) ...', note='Typical; the database is built right after install.'),
        dict(title='2 · Database and last update', cmd='ls -l /var/lib/plocate/plocate.db', output='-rw-r----- 1 root plocate 4.2M Nov 11 06:25 /var/lib/plocate/plocate.db', note='Typical. Group plocate lets locate read it.'),
        dict(title='3 · When does updatedb run?', cmd='systemctl list-timers | grep -i updatedb', output='Thu 2026-11-12 01:13 ... plocate-updatedb.timer plocate-updatedb.service', note='Typical: daily.'),
        dict(title='4 · Count, limit, case', cmd="locate -c '*.conf'; locate -i -l 3 readme", output='612\n/usr/share/doc/bash/README\n/usr/share/doc/git/README.md\n/usr/share/doc/tar/README', note='Typical.'),
        dict(title='5 · What is excluded from the index', cmd='grep PRUNE /etc/updatedb.conf', output='PRUNE_BIND_MOUNTS="yes"\nPRUNENAMES=".git .bzr .hg .svn"\nPRUNEPATHS="/tmp /var/spool /media /var/lib/os-prober /var/lib/ceph /home/.ecryptfs /var/lib/schroot"', note='Typical Ubuntu.'),
        dict(title='6 · Which package owns a program?', cmd='dpkg -S "$(readlink -f "$(which ls)")"', output=pc('dpkg -S "$(readlink -f "$(which ls)")" 2>&1 || true'), note='Recorded (Lesson 14.2).'),
    ],
)

TRACE = dict(
    heading='Checking tools in a script',
    intro='<p>Step through a script that resolves names and checks what exists.</p>',
    code='''p=$(command -v bash)
k=$(type -t cd)
if command -v nosuchtool > /dev/null; then m=found; else m=missing; fi
echo "bash=$p cd=$k nosuchtool=$m"
''',
    notes={1: 'Path :: command -v prints where bash is.', 2: 'Kind :: cd is a builtin.', 3: 'Exit status :: not found, so the else branch runs.', 4: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s version clash, a DevOps preflight check and a security PATH audit.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Which tool runs?',
         problem='<p>Two copies of a tool exist. Show both and which one wins.</p>',
         inp='two folders, each with mytool',
         approach=['Put both on PATH.', 'type -a, then run.'],
         code='''mkdir -p a b; printf '#!/bin/sh\\necho A\\n' > a/mytool; printf '#!/bin/sh\\necho B\\n' > b/mytool; chmod +x a/mytool b/mytool
PATH="$PWD/a:$PWD/b:$PATH"
type -a mytool
mytool
''',
         notes={1: 'Two tools.', 2: 'a first.', 3: 'Both listed :: in PATH order.', 4: 'A runs.'},
         tryit='Swap a and b in PATH (and run hash -r).'),
    dict(level='i', tag='DevOps', title='Preflight check',
         problem='<p>Report each required tool, and fail if any is missing.</p>',
         inp='bash, sed and a missing tool',
         approach=['command -v in a loop.', 'Count missing.'],
         code='''miss=0
for t in bash sed nosuchtool; do
  if command -v "$t" > /dev/null; then echo "ok      $t"; else echo "MISSING $t"; miss=$((miss+1)); fi
done
echo "missing: $miss"
''',
         notes={2: 'Loop.', 3: 'Check each.', 5: 'Total :: 1 missing.'},
         tryit='Exit 1 when miss is not 0.'),
    dict(level='a', tag='Security', title='Writable folders in PATH',
         problem='<p>Warn about any PATH folder that others can write to (a planted program could run).</p>',
         inp='PATH with a deliberately unsafe folder',
         approach=['Split PATH.', 'Test with find -perm.'],
         code='''mkdir -p unsafe; chmod 777 unsafe
PATH="$PWD/unsafe:$PATH"
for d in $(echo "$PATH" | tr ':' ' '); do
  [ -d "$d" ] && [ -n "$(find "$d" -maxdepth 0 -perm -o+w)" ] && echo "WARNING: $d is world-writable"
done
echo done
''',
         notes={1: 'Unsafe folder.', 2: 'Put first (bad idea).', 3: 'Each PATH folder.', 4: 'Warn :: only unsafe.', 6: 'End.'},
         tryit='chmod 755 unsafe and run again.'),
]

QUIZ = mix([
    dict(q='Why is locate so much faster than find?', options=['it uses more CPUs', 'it searches a prebuilt database of names', 'it only searches /home', 'it caches the disk'], answer=1,
         why='updatedb builds the index.'),
    dict(q='You created a file a minute ago and locate cannot find it. Fix?', options=['locate -f', 'sudo updatedb, then locate', 'reboot', 'locate -u'], answer=1,
         why='The index is not live.'),
    dict(q='Which option shows only files that still exist?', options=['-e', '-n', '-u', '-x'], answer=0,
         why='-e checks each result on disk.'),
    dict(q='Which prints nothing for cd?', options=['type cd', 'command -v cd', 'which cd', 'type -t cd'], answer=2,
         why='cd is a builtin; which only searches PATH.'),
    dict(q='type ll prints “ll is aliased to `ls -alF\'”. What does that mean?', options=['ll is a program', 'll is a shortcut the shell expands', 'll is broken', 'll is a keyword'], answer=1,
         why='An alias.'),
    dict(q='The best way for a script to test that git is installed?', options=['which git', 'command -v git > /dev/null', 'ls /usr/bin/git', 'locate git'], answer=1,
         why='POSIX, builtin, works for any location.'),
    dict(q='An old version still runs after you installed a new one elsewhere in PATH. First try?', options=['hash -r', 'updatedb', 'whereis -r', 'reboot'], answer=0,
         why='bash cached the old path.'),
    dict(q='Which shows a command’s manual page path?', options=['which', 'whereis', 'type', 'locate -b'], answer=1,
         why='whereis -m.'),
])

REVISION = [
    '<code>locate PATTERN</code> searches the index built by <code>updatedb</code> (daily). New files are missing; deleted ones remain.',
    'locate options: <code>-i</code> case, <code>-b</code> name only, <code>-c</code> count, <code>-l N</code> limit, <code>-e</code> existing, <code>-r / --regex</code>, <code>-0</code>.',
    'locate has no owner, size or time tests: that is find’s job.',
    '<code>which [-a] NAME</code>: the program(s) in $PATH; blind to aliases, functions and builtins.',
    '<code>type [-a|-t] NAME</code>: alias, keyword, function, builtin or file; shows everything the shell will try.',
    'Lookup order: alias → keyword → function → builtin → $PATH left to right (cached in <code>hash</code>; <code>hash -r</code>).',
    '<code>command -v</code> for scripts; <code>command NAME</code> or <code>\\NAME</code> skips aliases/functions.',
    '<code>whereis [-b -m -s]</code>: binary, manual and source in standard folders.',
]

FAQ = [
    ('What is the difference between find and locate?', 'locate searches a database built by updatedb (fast, may be out of date, names only); find searches live (slower, current, many tests).'),
    ('Why does locate not find my new file?', 'The database is updated about once a day. Run sudo updatedb, or use find.'),
    ('locate: command not found?', 'Install it: sudo apt install plocate (Ubuntu/Debian) or sudo dnf install plocate / mlocate (Fedora/RHEL).'),
    ('What is the difference between which and type?', 'which is a program that only searches $PATH; type is a shell builtin that also knows aliases, functions, keywords and builtins.'),
    ('How do I see all versions of a command on my PATH?', 'type -a NAME or which -a NAME.'),
    ('How do I check in a script whether a command exists?', 'if command -v NAME > /dev/null; then … fi.'),
    ('What does whereis do?', 'It lists a command’s binary, manual page and source files from standard locations.'),
]

PRACTICE_INTRO = 'Small lookup tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='What kind?', stmt='Print the kind of cd, ls and for, one word each.', inp='three names',
         code="type -t cd ls for\n", explain='-t.'),
    dict(level='easy', title='Path of a program', stmt='Show the full path of bash.', inp='bash',
         code="command -v bash\n", explain='Or which bash.'),
    dict(level='easy', title='All echoes', stmt='Show every definition of echo.', inp='echo',
         code="type -a echo\n", explain='Builtin first.'),
    dict(level='medium', title='Exists?', stmt='Print yes or no for sed and nosuchtool.', inp='two names',
         code="for t in sed nosuchtool; do command -v \"$t\" > /dev/null && echo \"$t yes\" || echo \"$t no\"; done\n", explain='Exit status.'),
    dict(level='medium', title='PATH folders', stmt='How many folders are in PATH?', inp='$PATH',
         code="echo \"$PATH\" | tr ':' '\\n' | wc -l\n", explain='tr + wc.'),
    dict(level='medium', title='Alias revealed', stmt='Define alias la=\'ls -A\' and show what it is.', inp='an alias',
         code="shopt -s expand_aliases; alias la='ls -A'\ntype la\n", explain='type shows the text.'),
    dict(level='business', title='Function vs program', stmt='A function named date hides the program. Show both, then run the real one with a fixed format.', inp='a function',
         code="date() { echo 'not the real date'; }\ntype -t date\ncommand date -d 2026-01-01 +%A\n", explain='command skips the function.'),
    dict(level='business', title='Binary paths', stmt='Show only the binary paths of bash and ls with whereis.', inp='two commands',
         code="whereis -b bash ls\n", explain='-b.'),
]

SCN_INTRO = 'Interview questions about locate, which, type and whereis, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Find and locate: what is the difference?”',
        'Asked in almost every Linux interview.',
        'do you understand the index?',
        '''<ul>
          <li>locate: database from updatedb, very fast, may be stale, names only.</li>
          <li>find: live walk, slower, current, tests size/time/owner and runs actions.</li>
          <li>Fix stale results: <code>sudo updatedb</code>; hide deleted ones: <code>locate -e</code>.</li>
        </ul>''', '“locate is newer and better, find is old.”') +
    scn('Product team', 'Junior', '“My library is installed but Python cannot import it”',
        'pip install worked; python3 app.py says ModuleNotFoundError.',
        'can you find which interpreter is running?',
        '''<ol>
          <li><code>type -a python3</code> and <code>which -a pip</code>: are they from the same place?</li>
          <li>Activate the virtual environment, or use <code>python3 -m pip install …</code>.</li>
          <li><code>hash -r</code> if paths changed.</li>
        </ol>''', 'reinstalling again and again.') +
    scn('Operations', 'Mid-level', 'A cron job fails with “command not found”',
        'The script works in your terminal but fails at 2 a.m.',
        'do you know cron’s environment?',
        '''<ul>
          <li>cron uses a minimal PATH (/usr/bin:/bin) and no aliases.</li>
          <li>Use full paths (<code>command -v tool</code> to find them) or set PATH at the top of the crontab.</li>
          <li>Never rely on aliases in scripts.</li>
        </ul>''', 'adding sleep or rerunning.') +
    scn('Security team', 'Senior', 'A fake sudo in PATH',
        'A user reports sudo asking for the password twice.',
        'can you spot PATH hijacking?',
        '''<ul>
          <li><code>type -a sudo</code>: is there a copy in ~/bin, /tmp or . before /usr/bin?</li>
          <li>Check for writable PATH folders and aliases/functions in ~/.bashrc.</li>
          <li>Remove it, rotate the password, review how it got there.</li>
        </ul>''', 'trusting which alone (it misses aliases and functions).')
) + interview([
    ('How do you update the locate database?', 'sudo updatedb.'),
    ('How do you search case-insensitively with locate?', 'locate -i name.'),
    ('How do you find which program runs for a command?', 'which NAME, or better type NAME.'),
    ('Is cd a program?', 'No, a shell builtin (type cd).'),
    ('What does whereis show?', 'Binary, man page and source locations.'),
    ('How do you run a command ignoring an alias?', '\\cmd or command cmd.'),
    ('What is $PATH?', 'Colon-separated folders searched left to right for programs.'),
], [
    ('RHCSA (EX200)', 'Locating files and documentation; locate and which appear in basic tasks.'),
    ('LFCS', 'Essential commands: search for files; understand PATH.'),
    ('CompTIA Linux+', 'locate/updatedb, which, whereis, type in file and command searching.'),
]) + distro('Same ideas everywhere; packages differ.', [
    ('locate', 'plocate (Ubuntu 22.10+, Debian 12)', 'plocate or mlocate (Fedora/RHEL)', 'locate; database via /usr/libexec/locate.updatedb', 'not in Git Bash'),
    ('updatedb', 'daily systemd timer', 'daily timer/cron', 'weekly periodic job', '-'),
    ('which', 'debianutils', 'GNU which (shows aliases with flags)', 'BSD which', 'Git Bash: yes'),
    ('type, command -v', 'bash builtin', 'bash builtin', 'zsh builtin (type, whence)', 'bash builtin'),
    ('whereis', 'util-linux', 'util-linux', 'BSD whereis', '-'),
    ('Windows names', '-', '-', '-', 'cmd.exe: where.exe'),
]) + teaser('8.1', 'Riya can find any file now, but who is allowed to read it? Why can she open notes.txt but not /etc/shadow? Next: users, groups and the passwd file.')

CHEATSHEET = cheatsheet('locate · which · type · whereis', [
    ('locate', [('locate NAME', 'search index'), ('-i / -b', 'case / name only'), ('-c / -l N', 'count / limit'), ('-e', 'still exists'), ('sudo updatedb', 'refresh')]),
    ('which', [('which NAME', 'first in PATH'), ('which -a NAME', 'all in PATH'), ('readlink -f $(which x)', 'real file'), ('echo $PATH', 'order'), ('command -v NAME', 'scripts')]),
    ('type', [('type NAME', 'what it is'), ('type -a NAME', 'all, in order'), ('type -t NAME', 'one word'), ('command NAME', 'skip alias/function'), ('\\NAME', 'skip alias')]),
    ('whereis & hash', [('whereis NAME', 'bin + man'), ('-b / -m / -s', 'bin / man / src'), ('hash', 'cached paths'), ('hash -r', 'forget'), ('man -w NAME', 'man page path')]),
])

MINDMAP = mindmap('Finding files and commands', [
    ('locate', 'amber', ['index from updatedb', '-i -b -c -l', '-e -r --regex']),
    ('Index', 'red', ['daily timer', 'new files missing', 'deleted still listed']),
    ('which', 'blue', ['first in PATH', '-a all', 'blind to aliases']),
    ('type', 'green', ['alias keyword', 'function builtin file', '-a -t']),
    ('whereis', 'violet', ['-b -m -s', 'man installed?', 'standard dirs']),
    ('PATH', 'acc', ['left to right', 'hash -r', 'command -v']),
])

LAB = lab('investigate command names', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab72/bin1 ~/lab72/bin2 && cd ~/lab72 && rm -f *.txt
printf '#!/bin/sh\\necho one\\n' > bin1/tool; printf '#!/bin/sh\\necho two\\n' > bin2/tool; chmod +x bin1/tool bin2/tool''',
    tasks=['Write the one-word kind (<code>type -t</code>) of <code>cd</code>, <code>ls</code> and <code>if</code>, one per line, into <code>kinds.txt</code>.',
           'Write the full path of bash (from <code>command -v</code>) into <code>bash.txt</code>.',
           'With <code>PATH="$HOME/lab72/bin2:$HOME/lab72/bin1:$PATH"</code>, write the output of running <code>tool</code> into <code>run.txt</code>.',
           'Write <code>yes</code> or <code>no</code> for whether <code>nosuchtool</code> exists into <code>exists.txt</code>.'],
    solution='''type -t cd ls if > kinds.txt
command -v bash > bash.txt
PATH="$HOME/lab72/bin2:$HOME/lab72/bin1:$PATH"; tool > run.txt
command -v nosuchtool > /dev/null && echo yes > exists.txt || echo no > exists.txt''',
    check='''cd ~/lab72
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 kinds"   '[ "$(cat kinds.txt 2>/dev/null)" = "$(printf "builtin\\nfile\\nkeyword")" ]'
ok "2 bash"    '[ -x "$(cat bash.txt 2>/dev/null)" ]'
ok "3 PATH"    '[ "$(cat run.txt 2>/dev/null)" = two ]'
ok "4 exists"  '[ "$(cat exists.txt 2>/dev/null)" = no ]' ''')
