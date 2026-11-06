import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap
BODY = body(HERE)

META = dict(
    module='02-file-system', lesson='05-getting-help-man-help-info-whatis-and-apropos', n='2.5',
    module_label='Module 2 · The Linux file system',
    title='Getting help: man, --help, info, whatis and apropos',
    desc='How to find help on any Linux system without the internet: --help, man pages and their sections (1–8), moving and searching inside man, reading SYNOPSIS notation ([ ], ..., UPPERCASE), whatis, apropos and man -k, help for bash builtins, info manuals, mandb and where documentation is stored. Animations, real Bash and interview questions.',
    og_desc='Nobody remembers every option. Find any Linux option in ten seconds, offline: --help, man, apropos and help.',
    minutes=25, level='Beginner → Advanced',
    lead='Riya is on a server with no internet and cannot remember an option. This lesson shows the help systems every Linux machine already has: --help for a quick summary, man for the full manual and its sections, whatis and apropos to find the right command, help for bash builtins, and how to read the brackets and dots in every usage line.',
    chips=['Story-based', '4 animations', 'Layer-by-layer', 'Real Bash in your browser'],
)

MAIN = '''# Asking the system for help
type cd ls
help -d cd
ls --help | head -1
ls --help | grep -- '-S '
cp --help | grep -- '-r,'
date --version | head -1
'''

RUN = dict(
    heading='Ask the system',
    intro='<p>The script checks what kind of command each name is, then asks the right help system. Recorded on our Ubuntu build machine.</p>',
    code=MAIN,
    anno=[
        ('type cd ls', 'Builtin or program? It decides which help to use.'),
        ('help -d cd', 'One-line help for a builtin.'),
        ('ls --help | head -1', 'The usage line of a program.'),
        ("ls --help | grep -- '-S '", '<code>--</code> tells grep that <code>-S</code> is a pattern, not a grep option.'),
        ("cp --help | grep -- '-r,'", 'How to copy folders.'),
        ('date --version | head -1', 'Which version is installed, so you know which docs apply.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which line tells you how to copy a folder?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> is <code>echo</code> a builtin, a program, or both? Then run.',
             code='type -a echo\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> grep thinks <code>-h</code> is its own option. Fix it so it searches for “-h”.',
             code="ls --help | grep '-h'\n", expect='any'),
        dict(label='4 · Your turn', hint='Find the option of <code>wc</code> that counts only lines.',
             code="wc --help | grep -i line\n"),
        dict(label='5 · Challenge', hint='Print the one-line description of every builtin whose name starts with “e”.',
             code="help -d 'e*'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the manual on your own Linux',
    intro='<p>Man pages are removed from our minimal build image, so the man outputs below are <b>typical output on Ubuntu 24.04 desktop or server</b> (shortened). The last item was recorded on our build machine.</p>',
    items=[
        dict(title='1 · Open a manual page', cmd='man ls', output='LS(1)                            User Commands                           LS(1)\n\nNAME\n       ls - list directory contents\n\nSYNOPSIS\n       ls [OPTION]... [FILE]...\n\nDESCRIPTION\n       List  information  about  the FILEs (the current directory by default).\n       Sort entries alphabetically if none of -cftuvSUX nor --sort  is  speci‐\n       fied.\n...\n Manual page ls(1) line 1 (press h for help or q to quit)',
             note='Space = next page, b = back, /word = search, n = next match, g / G = top / bottom, q = quit.'),
        dict(title='2 · One name, several sections', cmd='whatis passwd; man -f printf', output='passwd (1ssl)         - OpenSSL application commands\npasswd (1)            - change user password\npasswd (5)            - the password file\nprintf (1)            - format and print data\nprintf (3)            - formatted output conversion',
             note='Typical. <code>man -f</code> = whatis. The (1ssl) page comes from OpenSSL. Section 3 pages need the manpages-dev package.'),
        dict(title='3 · Search by keyword', cmd='apropos -s 1 "copy files"', output='cp (1)               - copy files and directories\ncpio (1)             - copy files to and from archives\ninstall (1)          - copy files and set attributes\nscp (1)              - OpenSSH secure file copy',
             note='Typical. <code>-s 1</code> limits to section 1. Your list depends on the packages installed.'),
        dict(title='4 · Where is that page stored?', cmd='man -w ls; man -w 5 passwd', output='/usr/share/man/man1/ls.1.gz\n/usr/share/man/man5/passwd.5.gz',
             note='Typical. <code>-w</code> prints the file instead of showing it: compressed roff source, one folder per section.'),
        dict(title='5 · Bring the manuals back on a minimal system', cmd='sudo apt install man-db manpages && sudo unminimize', output='(Ubuntu asks for confirmation, then reinstalls the documentation removed from the minimal image)',
             note='Only needed on minimal images (cloud and container images). A normal Ubuntu install already has man pages.'),
        dict(title='6 · Builtins have their own help', cmd='help pwd', output=pc('help pwd'),
             note='Recorded on our build machine. <code>help</code> works even where man pages are missing.'),
    ],
)

TRACE = dict(
    heading='Letting a script check its tools',
    intro='<p>A setup script checks that the tools it needs exist and what kind they are before using them. Watch the <b>Shell</b> box.</p>',
    code='''for tool in cd tar gzip nosuchtool; do
  kind=$(type -t "$tool")
  echo "$tool: ${kind:-missing}"
done
tar --version | head -1
''',
    notes={1: 'Loop :: One tool per round.', 2: 'Kind :: <code>type -t</code> prints builtin, file, alias, function, or nothing.',
           3: 'Report :: <code>${kind:-missing}</code> = the value, or “missing” if it is empty.', 5: 'Version :: The docs you read should match this.'},
)

WORKED_INTRO = 'Three real tasks: building your own cheat sheet, finding an option for a real job, and checking which help a list of commands needs.'
EXAMPLES = [
    dict(level='b', tag='Learning', title='A personal cheat sheet from --help',
         problem='<p>Build a small cheat sheet of the sorting options of <code>ls</code> and save it to a file for later.</p>',
         inp='ls --help',
         approach=['<code>grep</code> the lines that mention “sort”.', 'Save with <code>&gt;</code> and show the file.'],
         code='''ls --help | grep -i 'sort' > ls-sorting.txt
wc -l ls-sorting.txt
head -4 ls-sorting.txt
''',
         notes={1: 'Filter and save :: Only lines about sorting go into the file.', 3: 'Check :: The first few lines.'},
         tryit='Do the same for <code>cp --help</code> and the word “preserve”.'),
    dict(level='i', tag='Operations', title='Find the option for a real job',
         problem='<p>Kabir needs to create a <code>tar</code> archive and <b>exclude</b> log files. Find the option in the help text, then use it.</p>',
         inp='app/ with main.py, app.log and debug.log',
         approach=['<code>tar --help | grep -- --exclude</code> shows the option.', 'Use it and list the archive with <code>tar -tf</code>.'],
         code='''mkdir app && touch app/main.py app/app.log app/debug.log
tar --help | grep -m1 -- '--exclude='
tar -czf app.tgz --exclude='*.log' app
tar -tzf app.tgz
''',
         notes={2: 'Look it up :: <code>-m1</code> = first match only.', 3: 'Use it :: Quotes stop the shell from expanding *.log itself.', 4: 'Verify :: The logs are not in the archive.'},
         tryit='Find the option that makes tar print each file while it works (hint: verbose).'),
    dict(level='a', tag='Automation', title='Which help does each command need?',
         problem='<p>For a training sheet, print for each command whether to use <code>help</code> (builtin), <code>--help</code>/<code>man</code> (program) or whether it is missing.</p>',
         inp='cd export grep tar read nosuch',
         approach=['<code>type -t</code> returns builtin, file or nothing.', '<code>case</code> maps it to the help tool.'],
         code='''for c in cd export grep tar read nosuch; do
  case $(type -t "$c") in
    builtin) echo "$c -> help $c" ;;
    file)    echo "$c -> $c --help / man $c" ;;
    *)       echo "$c -> not installed" ;;
  esac
done
''',
         notes={2: 'Classify :: The shell itself tells us the kind.', 5: 'Missing :: Nothing printed by type -t.'},
         tryit='Add an alias <code>alias ll="ls -l"</code> before the loop and <code>ll</code> to the list. What does type -t say? (In a script, aliases need <code>shopt -s expand_aliases</code>.)'),
]

QUIZ = mix([
    dict(q='Which command shows the full manual page of ls?', options=['help ls', 'man ls', 'info -k ls', 'whatis -f ls'], answer=1,
         why='man shows manual pages; --help gives a shorter summary.'),
    dict(q='You do not know the name of a command for partitions. What do you use?', options=['man partition', 'apropos partition', 'help partition', 'partition --help'], answer=1,
         why='apropos (man -k) searches the one-line descriptions of all pages.'),
    dict(q='Which manual section contains file formats such as /etc/passwd?', options=['1', '3', '5', '8'], answer=2,
         why='Section 5: file formats and configuration files. man 5 passwd.'),
    dict(q='How do you get help for the builtin cd?', options=['man cd', 'help cd', 'info cd', 'apropos cd'], answer=1,
         why='Builtins are documented inside bash: help cd.'),
    dict(q='In a usage line, what does [FILE]... mean?', options=['Exactly one file', 'Zero or more files', 'A file named FILE', 'A required list'], answer=1,
         why='[ ] = optional, ... = may repeat: zero or more.'),
    dict(q='How do you quit a man page?', options=['Ctrl+Q', 'Esc', 'q', ':exit'], answer=2,
         why='man uses the pager less; q quits.'),
    dict(q='apropos prints “nothing appropriate” for everything. What may help?', options=['Reboot', 'sudo mandb', 'chmod 777 /usr/share/man', 'Reinstall bash'], answer=1,
         why='apropos searches the mandb index; rebuild it (and install man pages on minimal images).'),
])

REVISION = [
    '<code>cmd --help</code>: quick options; filter with <code>| grep</code>.',
    '<code>man cmd</code>: full manual. Space, b, <code>/word</code>, n, q.',
    'Sections: 1 commands, 2 system calls, 3 library, 4 devices, 5 file formats, 7 overviews, 8 admin. <code>man 5 passwd</code>.',
    'SYNOPSIS: <code>[ ]</code> optional, <code>...</code> repeat, UPPERCASE = your value, <code>a|b</code> one of them, “or:” = another form.',
    '<code>whatis</code> (= <code>man -f</code>) one line; <code>apropos</code> (= <code>man -k</code>) keyword search; index built by <code>mandb</code>.',
    'Builtins (cd, export, read): <code>help name</code>; check the kind with <code>type name</code>.',
    '<code>info</code> for long GNU manuals; files in /usr/share/man, /usr/share/info, /usr/share/doc.',
    'Docs on the machine match the installed version; check with <code>--version</code>.',
]

FAQ = [
    ('What is the difference between man and --help?', 'man shows the complete manual page from /usr/share/man, formatted in a pager. --help is a short summary printed by the program itself.'),
    ('What are the sections of the Linux manual?', '1 user commands, 2 system calls, 3 library functions, 4 special files, 5 file formats, 6 games, 7 miscellaneous and conventions, 8 system administration commands.'),
    ('What is the difference between whatis and apropos?', 'whatis shows the one-line description of an exact page name; apropos searches all descriptions for a keyword. They are the same as man -f and man -k.'),
    ('Why is there no man page for cd?', 'cd is a bash builtin. Builtins are documented by bash itself: use help cd (or man bash).'),
    ('How do you search inside a man page?', 'Type / followed by the word and press Enter; n goes to the next match, N to the previous.'),
    ('What is the info command?', 'A reader for Texinfo manuals, used mainly by GNU projects. They are longer than man pages and organised in linked nodes.'),
]

PRACTICE_INTRO = 'Tasks about finding help. Expected outputs come from real runs on Ubuntu 24.04 (a minimal image, so these use --help, help and type).'
PROBLEMS = [
    dict(level='easy', title='Builtin or program?', stmt='Print the kind of <code>pwd</code>, <code>grep</code> and <code>read</code>.', inp='pwd grep read',
         code='type -t pwd grep read\n', explain='builtin, file, builtin.'),
    dict(level='easy', title='The usage line', stmt='Print only the first line of <code>mkdir --help</code>.', inp='mkdir --help',
         code='mkdir --help | head -1\n', explain='DIRECTORY... = one or more folder names are required.'),
    dict(level='easy', title='Help for a builtin', stmt='Show the short description of the builtin <code>export</code>.', inp='export',
         code='help -d export\n', explain='-d prints only the one-line description.'),
    dict(level='medium', title='Find an option', stmt='Find the option of <code>sort</code> that sorts numbers correctly.', inp='sort --help',
         code="sort --help | grep -- '-n,'\n", explain='-n compares as numbers, so 10 comes after 9.'),
    dict(level='medium', title='Count the options', stmt='How many lines of <code>ls --help</code> start with spaces and a dash (one per option)?', inp='ls --help',
         code="ls --help | grep -c '^ *-'\n", explain='A rough count of the options ls offers.'),
    dict(level='medium', title='Version check', stmt='Print the version line of <code>grep</code> and <code>bash</code>.', inp='grep, bash',
         code='grep --version | head -1\nbash --version | head -1\n', explain='Always compare with the version an online answer was written for.'),
    dict(level='business', title='Look it up, then use it', stmt='A report needs the date 30 days ago in YYYY-MM-DD form. Find the date option and use it.', inp='date --help',
         code="date --help | grep -m1 -- '--date='\ndate -d '2026-11-05 -30 days' +%F\n", explain='-d accepts expressions like “-30 days”; +%F prints YYYY-MM-DD. (A fixed start date keeps the output stable.)'),
    dict(level='business', title='Onboarding check', stmt='A new laptop must have <code>git</code>, <code>curl</code> and <code>tar</code>. Print “ok” or “missing” for each.', inp='git curl tar',
         code='for t in git curl tar; do\n  if type -P "$t" > /dev/null; then echo "ok      $t"; else echo "missing $t"; fi\ndone\n', explain='<code>type -P</code> looks only for program files in PATH.'),
]

SCN_INTRO = 'Interview questions about documentation, as asked for support, admin and certification-style practical rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you find out what a command does?”',
        'The interviewer names a command you have never seen, for example <code>nl</code>.',
        'do you know how to help yourself?',
        '''<ul>
          <li><code>whatis nl</code> for one line, <code>nl --help</code> for the options, <code>man nl</code> for the details and examples.</li>
          <li>If it is a builtin (<code>type nl</code>), use <code>help</code>.</li>
          <li>Then test it on a sample file.</li>
        </ul>''', '“I would search on Google” as the only answer.') +
    scn('Operations · no internet', 'Junior', 'Find a command for a task',
        'On a server with no internet you must find how to see which process uses a port.',
        'can you search the local documentation by topic?',
        '''<ol>
          <li><code>apropos port</code> or <code>apropos socket</code> → ss, lsof, netstat, fuser.</li>
          <li><code>whatis ss</code>; then <code>ss --help</code> or <code>man ss</code> and search <code>/listening</code>.</li>
          <li>Result: <code>sudo ss -ltnp</code> (Lesson 16.4).</li>
        </ol>''', 'giving up because there is no browser.') +
    scn('Certification · practical', 'Mid-level', '“The exam allows only local docs.”',
        'In RHCSA- or LFCS-style exams you may only use the system’s documentation. How do you prepare?',
        'are you fluent with man sections and searching?',
        '''<ul>
          <li>Know sections 1, 5 and 8 and use <code>man 5 fstab</code>, <code>man 5 crontab</code>, <code>man 8 mount</code>.</li>
          <li>Use <code>man -k</code> with section filters, and jump to EXAMPLES with <code>/EXAMPLES</code>.</li>
          <li>Look in <code>/usr/share/doc/&lt;package&gt;</code> for sample configs.</li>
        </ul>''', 'only memorising options.') +
    scn('Platform team · internals', 'Senior', '“Why did apropos return nothing?”',
        'On a fresh cloud VM, <code>apropos</code> and <code>man</code> return nothing useful.',
        'do you understand how the man system is built?',
        '''<ul>
          <li>Minimal images remove man pages (dpkg excludes /usr/share/man) and may skip the mandb index.</li>
          <li>Fix: <code>sudo unminimize</code> (Ubuntu) or reinstall the man-db and manpages packages, then <code>sudo mandb</code>.</li>
          <li>Meanwhile <code>--help</code> and <code>help</code> still work, because their text is inside the programs and bash.</li>
        </ul>''', '“the commands are broken”.')
) + teaser('3.1', 'Riya needs 12 empty monthly report files and a folder tree three levels deep. Can she do it all with two short commands?')

MINDMAP = mindmap('Getting help', [
    ('--help', 'acc', ['quick option list', 'inside the program', '| grep word']),
    ('man', 'blue', ['full manual page', 'Space, /word, n, q', 'NAME, SYNOPSIS, …']),
    ('Sections', 'violet', ['1 cmds · 8 admin', '5 file formats', 'man 5 passwd']),
    ('Find commands', 'green', ['apropos = man -k', 'whatis = man -f', 'index: mandb']),
    ('Builtins', 'amber', ['type name first', 'help cd', 'man bash covers all']),
    ('Read a SYNOPSIS', 'red', ['[ ] optional', '... repeat', 'UPPER = your value']),
])
