import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap
BODY = body(HERE)

META = dict(
    module='02-file-system', lesson='03-absolute-and-relative-paths', n='2.3',
    module_label='Module 2 · The Linux file system',
    title='Absolute and relative paths, ~, . and .. and Tab completion',
    desc='Absolute vs relative paths in Linux explained from zero: /, ~, ~user, . and .., Tab and double-Tab completion, realpath, dirname and basename, why ./script.sh is needed, how the kernel walks a path one folder at a time, and how to write scripts that work from any folder. Animations, real Bash and interview questions.',
    og_desc='Why does the same script work in one folder and fail in another? Absolute vs relative paths, explained.',
    minutes=30, level='Beginner → Advanced',
    lead='Riya’s script works in its own folder and fails everywhere else, though the file never moved. This lesson explains the two kinds of path, the shortcuts ~, . and .., Tab completion, what the kernel does with every path you type, and the one habit that makes scripts work from any folder.',
    chips=['Story-based', '4 animations', 'Layer-by-layer', 'Real Bash in your browser'],
)

MAIN = '''# One file, many paths
mkdir -p reports data && echo "id,amt" > data/sales.csv
cat /home/riya/lab/data/sales.csv
cat ~/lab/data/sales.csv
cat data/sales.csv
cd reports
cat ../data/sales.csv
realpath ../data/./sales.csv
cd ~
cat ../data/sales.csv
echo "exit status: $?"
'''

RUN = dict(
    heading='One file, many paths',
    intro='<p>The script reads the same file four ways, then shows the relative path breaking once the current folder changes. The output was recorded on our Ubuntu build machine as user <code>riya</code>, starting in <code>~/lab</code>.</p>',
    code=MAIN, expect='any',
    anno=[
        ('cat /home/riya/lab/data/sales.csv', 'Absolute: works from anywhere.'),
        ('cat ~/lab/data/sales.csv', 'The shell turns <code>~</code> into <code>/home/riya</code> first.'),
        ('cat data/sales.csv', 'Relative to <code>~/lab</code>, where we are now.'),
        ('cat ../data/sales.csv', 'From reports: up to lab, then down to data.'),
        ('realpath ../data/./sales.csv', 'Prints the clean absolute path.'),
        ('cd ~', 'Now the current folder is home…'),
        ('echo "exit status: $?"', '…so the same relative path fails: status 1.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which <code>cat</code> fails, and why?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each line print? Then run.',
             code='cd /usr/bin\ncd ../share\npwd\ncd ../../etc/..\npwd\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> tilde inside quotes. Make it print your home folder’s notes path.',
             code='echo "~/notes.txt"\n'),
        dict(label='4 · Your turn', hint='Print the folder part, the file name and the name without extension of <code>/var/log/nginx/access.log</code>.',
             code='f=/var/log/nginx/access.log\ndirname "$f"\nbasename "$f"\nbasename "$f" .log\n'),
        dict(label='5 · Challenge', hint='Show that a name without a slash is searched in PATH but <code>./</code> runs the local file.',
             code="printf 'echo hello from the local script\\n' > hi.sh\nchmod +x hi.sh\nhi.sh 2>&1 || echo \"(not found in PATH)\"\n./hi.sh\n", expect='any'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: paths on your own Linux',
    intro='<p>Try these on your own Linux. <b>Outputs were recorded on our Ubuntu 24.04 build machine</b> unless marked typical.</p>',
    items=[
        dict(title='1 · Tilde forms', cmd='echo ~ ~root; cd /tmp; cd /etc; echo ~+ ~-', output=pc('echo ~ ~root; cd /tmp; cd /etc; echo ~+ ~-'),
             note='<code>~root</code> is root’s home; <code>~+</code> = current folder, <code>~-</code> = previous.'),
        dict(title='2 · The root is its own parent', cmd='ls -di / /.. ; cd /; cd ..; pwd', output=pc('ls -di / /.. ; cd /; cd ..; pwd'),
             note='Same inode number: at the top, <code>..</code> points back to <code>/</code>.'),
        dict(title='3 · Limits for names and paths', cmd='getconf NAME_MAX /; getconf PATH_MAX /', output=pc('getconf NAME_MAX /; getconf PATH_MAX /'),
             note='255 bytes per name, 4096 bytes per path on ext4.'),
        dict(title='4 · Watch the kernel resolve a path', cmd='strace -e trace=openat cat ../data/sales.csv 2>&1 | tail -3', output='openat(AT_FDCWD, "../data/sales.csv", O_RDONLY) = 3\nid,amt\n+++ exited with 0 +++',
             note='Typical output (strace is not installed in our build image; install it with <code>sudo apt install strace</code>). <code>AT_FDCWD</code> = “resolve from the current directory”.'),
        dict(title='5 · Tab completion candidates', cmd='compgen -d -- /var/l', output=pc('compgen -d -- /var/l'),
             note='What Tab Tab would list for folders starting with <code>/var/l</code>.'),
    ],
)

TRACE = dict(
    heading='Paths changing meaning, line by line',
    intro='<p>The same relative name points to different files as the current folder changes. Watch <code>PWD</code> in the <b>Shell</b> box.</p>',
    code='''mkdir -p a b
echo "I am a/note" > a/note
echo "I am b/note" > b/note
cd a
cat note
cd ../b
cat note
cat /home/riya/lab/a/note
''',
    notes={4: 'Into a :: The current folder is now ~/lab/a.', 5: 'Relative :: <code>note</code> means ~/lab/a/note.',
           6: 'Sideways :: <code>../b</code>: up to lab, into b.', 7: 'Same name :: Now <code>note</code> is a different file!', 8: 'Absolute :: Always the same file, wherever we are.'},
)

WORKED_INTRO = 'Three real tasks: a portable script, normalising messy paths from a config, and splitting paths in a file-processing job.'
EXAMPLES = [
    dict(level='b', tag='Scripts', title='Make a script find its own data',
         problem='<p>A script in <code>tools/</code> must read <code>tools/data/list.txt</code> no matter which folder it is started from.</p>',
         inp='tools/count.sh and tools/data/list.txt (3 lines)',
         approach=['Get the script’s folder with <code>cd "$(dirname "$0")" &amp;&amp; pwd</code>.', 'Build the data path from it; run the script from two different folders to prove it.'],
         code='''mkdir -p tools/data && printf 'a\\nb\\nc\\n' > tools/data/list.txt
cat > tools/count.sh <<'EOF'
here="$(cd "$(dirname "$0")" && pwd)"
echo "lines: $(wc -l < "$here/data/list.txt")"
EOF
bash tools/count.sh
cd / && bash /home/riya/lab/tools/count.sh
''',
         notes={2: 'Write the script :: Its first line finds the script’s own absolute folder, even if $0 was relative.', 6: 'From lab :: Works.', 7: 'From / :: Still works.'},
         tryit='Change the script to use <code>data/list.txt</code> directly and run it from <code>/</code>. What happens?'),
    dict(level='i', tag='Config check', title='Normalise messy paths from a config',
         problem='<p>A config file lists folders written by different people: some relative, some with <code>..</code> and <code>.</code>. Print each as a clean absolute path, and flag the ones that do not exist.</p>',
         inp='paths.txt: data/./raw, ./reports/../data, /tmp, missing/dir',
         approach=['Read the file line by line.', '<code>realpath -m</code> normalises even missing paths; <code>[ -e ]</code> tests existence.'],
         code='''mkdir -p data/raw reports
printf 'data/./raw\\n./reports/../data\\n/tmp\\nmissing/dir\\n' > paths.txt
while read -r p; do
  clean=$(realpath -m "$p")
  [ -e "$clean" ] && state=ok || state=MISSING
  printf "%-20s -> %-28s %s\\n" "$p" "$clean" "$state"
done < paths.txt
''',
         notes={4: 'Normalise :: <code>-m</code> = do not require the path to exist.', 5: 'Check :: <code>-e</code> = exists.'},
         tryit='Add the line <code>~/lab</code> to the file. Why is it MISSING? (Hint: who expands ~?)'),
    dict(level='a', tag='Business problem', title='Route incoming files by name and folder',
         problem='<p>An import job receives full paths of uploaded files. For each, print the customer (the folder name), the file name without extension and the extension, for a load log.</p>',
         inp='/upload/acme/orders_1105.csv, /upload/zenith/stock.json, /upload/acme/returns.csv',
         approach=['<code>dirname</code> then <code>basename</code> gives the customer folder.', 'Bash parameter expansion <code>${f##*.}</code> gives the extension; <code>basename "$f" ".$ext"</code> the name.'],
         code='''for f in /upload/acme/orders_1105.csv /upload/zenith/stock.json /upload/acme/returns.csv; do
  customer=$(basename "$(dirname "$f")")
  ext=${f##*.}
  name=$(basename "$f" ".$ext")
  echo "$customer | $name | $ext"
done
''',
         notes={2: 'Customer :: Folder of the file, then its last part.', 3: 'Extension :: <code>##*.</code> removes everything up to the last dot.'},
         tryit='Add <code>/upload/acme/archive.tar.gz</code>. What extension do you get? (Lesson 12.4 covers expansions in depth.)'),
]

QUIZ = mix([
    dict(q='Which is an absolute path?', options=['./data', '../etc', '/var/log', 'notes.txt'], answer=2,
         why='Only paths starting with / are absolute.'),
    dict(q='You are in /home/riya/lab. What does cd ../.. lead to?', options=['/home', '/home/riya', '/', '/lab'], answer=0,
         why='lab → riya → home.'),
    dict(q='Who expands ~ into /home/riya?', options=['The kernel', 'The shell', 'The ls command', 'The terminal emulator'], answer=1,
         why='Tilde expansion is done by the shell before the command runs.'),
    dict(q='Why does deploy.sh give “command not found” even though it is in the current folder?', options=['It is not executable', 'Names without a slash are searched only in PATH', 'Scripts need sudo', 'The file is hidden'], answer=1,
         why='Use ./deploy.sh: a slash tells the shell to run that exact file.'),
    dict(q='What does pressing Tab twice do when several names match?', options=['Deletes the line', 'Lists all matching choices', 'Runs the command', 'Nothing'], answer=1,
         why='The first Tab completes the common part; the second lists the candidates.'),
    dict(q='What is /..?', options=['An error', 'The same as /', 'The parent of the disk', 'Your home'], answer=1,
         why='At the root, .. points to the root itself.'),
    dict(q='Which path should a crontab line use for a script?', options=['run.sh', './run.sh', '../run.sh', '/opt/app/run.sh'], answer=3,
         why='Cron starts jobs in another folder with a minimal PATH, so absolute paths are safest.'),
])

REVISION = [
    'Absolute = starts with <code>/</code>, same from everywhere. Relative = from the current folder.',
    '<code>.</code> here · <code>..</code> parent · <code>~</code> home · <code>~user</code> their home · <code>~+</code>/<code>~-</code> current/previous.',
    '<code>~</code> is expanded by the shell, not inside quotes: use <code>"$HOME/..."</code> in quotes.',
    'Tab completes; Tab Tab lists choices; no completion = the name does not exist.',
    'Run a local script with <code>./script.sh</code>: names without a slash are searched in PATH only.',
    '<code>realpath</code> cleans a path; <code>dirname</code>/<code>basename</code> split it.',
    'The kernel walks a path component by component; each folder needs x permission; errors: ENOENT, EACCES.',
    'Scripts: build paths from <code>"$(cd "$(dirname "$0")" &amp;&amp; pwd)"</code>; cron and services: absolute paths.',
]

FAQ = [
    ('What is the difference between an absolute and a relative path?', 'An absolute path starts with / and is resolved from the root, so it means the same from any folder. A relative path does not start with / and is resolved from the current working directory.'),
    ('What do . and .. mean?', '. is the current directory and .. is its parent. Both are real entries in every directory.'),
    ('Why do I have to type ./ to run a script?', 'A command name without a slash is searched only in the directories listed in PATH, and the current directory is not in PATH for safety. ./script.sh is a path, so the shell runs that exact file.'),
    ('What does ~ mean?', 'The home directory of the current user (the value of $HOME). ~name is the home directory of user name. The shell expands it; it is not expanded inside quotes.'),
    ('How do I get the absolute path of a file?', 'realpath file (or readlink -f file). Both remove ., .. and symbolic links.'),
    ('Why does my script work in one folder and fail in another?', 'It uses relative paths, which depend on the current working directory. Build paths from the script’s own location (dirname "$0") or use absolute paths.'),
]

PRACTICE_INTRO = 'Tasks about paths. Expected outputs come from real runs on Ubuntu 24.04 (start folder: ~/lab).'
PROBLEMS = [
    dict(level='easy', title='Absolute or relative?', stmt='For each of <code>/etc</code>, <code>notes</code>, <code>../x</code> and <code>./run.sh</code>, print whether it is absolute or relative.', inp='/etc notes ../x ./run.sh',
         code='for p in /etc notes ../x ./run.sh; do\n  case $p in /*) echo "$p: absolute" ;; *) echo "$p: relative" ;; esac\ndone\n', explain='The pattern <code>/*</code> matches anything that starts with a slash.'),
    dict(level='easy', title='Clean path', stmt='Print the clean absolute form of <code>/usr/./bin/../lib</code>.', inp='/usr/./bin/../lib',
         code='realpath /usr/./bin/../lib\n', explain='. disappears, bin/.. cancels out: /usr/lib.'),
    dict(level='easy', title='Home in quotes', stmt='Print the path of <code>notes.txt</code> in your home folder from inside double quotes, correctly expanded.', inp='(none)',
         code='echo "$HOME/notes.txt"\n', explain='$HOME expands inside double quotes; ~ would not.'),
    dict(level='medium', title='Relative route', stmt='Create <code>web/css</code> and <code>web/img</code>. Print the relative path from <code>web/css</code> to <code>web/img/logo.png</code>.', inp='web/css, web/img/logo.png',
         code='mkdir -p web/css web/img && touch web/img/logo.png\nrealpath --relative-to=web/css web/img/logo.png\n', explain='The route is ../img/logo.png: exactly what a stylesheet would write.'),
    dict(level='medium', title='Folder and name', stmt='Given <code>/srv/backups/2026-11-05/db.sql.gz</code>, print the date folder and the file name.', inp='/srv/backups/2026-11-05/db.sql.gz',
         code='f=/srv/backups/2026-11-05/db.sql.gz\necho "date: $(basename "$(dirname "$f")")"\necho "file: $(basename "$f")"\n', explain='dirname, then basename of that, gives the folder’s own name.'),
    dict(level='medium', title='Same name, two files', stmt='Create <code>x/cfg</code> and <code>y/cfg</code> with different text. From inside <code>x</code>, print <code>cfg</code> and <code>../y/cfg</code>.', inp='x/cfg = "dev", y/cfg = "prod"',
         code='mkdir x y && echo dev > x/cfg && echo prod > y/cfg\ncd x\ncat cfg ../y/cfg\n', explain='A relative name always depends on where you are.'),
    dict(level='business', title='Check paths before a cron job', stmt='A job will use the paths <code>/etc/hostname</code>, <code>/no/such/file</code> and <code>/usr/bin/env</code>. Print OK or MISSING for each, so the job is not scheduled with broken paths.', inp='three absolute paths',
         code='for p in /etc/hostname /no/such/file /usr/bin/env; do\n  if [ -e "$p" ]; then echo "OK      $p"; else echo "MISSING $p"; fi\ndone\n', explain='A pre-flight check like this catches typos before a job fails at 2 a.m.'),
    dict(level='business', title='Portable project paths', stmt='A project keeps <code>config/app.conf</code>. Print the config’s absolute path from inside <code>project/bin</code> using only relative navigation and realpath.', inp='project/bin, project/config/app.conf',
         code='mkdir -p project/bin project/config && echo "port=80" > project/config/app.conf\ncd project/bin\nrealpath ../config/app.conf\ncat ../config/app.conf\n', explain='Inside a repository, relative paths keep the project portable; realpath shows where they lead on this machine.'),
]

SCN_INTRO = 'Interview questions about paths, as asked for support, DevOps and developer roles.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Absolute vs relative path?”',
        'The interviewer asks for the difference and an example of each for the same file.',
        'can you explain it with one clear example?',
        '''<ul>
          <li>Absolute starts at <code>/</code>: <code>/home/riya/notes.txt</code>; same meaning from anywhere.</li>
          <li>Relative starts at the current folder: from <code>/home/riya</code> just <code>notes.txt</code>; from <code>/home/riya/docs</code> it is <code>../notes.txt</code>.</li>
          <li>Mention <code>.</code>, <code>..</code> and <code>~</code>, and that <code>~</code> is expanded by the shell.</li>
        </ul>''', 'saying relative paths are “shorter absolute paths”.') +
    scn('Operations · cron', 'Junior', '“My script works by hand but fails in cron.”',
        'A backup script runs fine from the terminal but the cron job fails every night.',
        'do you know how cron’s environment differs?',
        '''<ol>
          <li>Cron starts jobs in the user’s home with a minimal PATH and no interactive startup files.</li>
          <li>So relative paths and commands found only in your custom PATH break. Use absolute paths, or <code>cd /opt/backup || exit 1</code> at the start.</li>
          <li>Log output: <code>... &gt;&gt; /var/log/backup.log 2&gt;&amp;1</code>, and test with <code>env -i</code> to simulate a bare environment (Lesson 17.4).</li>
        </ol>''', '“cron is broken, run it with sudo”.') +
    scn('Security · concepts', 'Mid-level', '“Why isn’t . in PATH?”',
        'The interviewer asks why you must type <code>./tool</code> instead of <code>tool</code> for a program in the current folder.',
        'do you see the security reason?',
        '''<ul>
          <li>Names without a slash are searched in PATH; with <code>.</code> in PATH, a malicious <code>ls</code> placed in a shared folder like <code>/tmp</code> would run when you type <code>ls</code> there.</li>
          <li>Even at the end of PATH it catches typos (<code>sl</code>). Explicit <code>./</code> means you always know what runs.</li>
        </ul>''', '“Linux is just strict”.') +
    scn('Kernel · internals', 'Senior', '“What happens when you open a relative path?”',
        'Explain what the kernel does for <code>open("../data/x.csv")</code>.',
        'do you understand path resolution?',
        '''<ul>
          <li>The syscall (openat with AT_FDCWD) starts from the process’s current directory; an absolute path would start at the process’s root directory.</li>
          <li>The path is split on <code>/</code>; each component is looked up in the directory reached so far (dentry cache first, then the file system), checking x permission on each directory and following symbolic links (limit 40).</li>
          <li>Failure modes: ENOENT, ENOTDIR, EACCES, ELOOP, ENAMETOOLONG. At the end, the final inode’s permissions are checked and a file descriptor is returned.</li>
        </ul>''', 'not knowing that . and .. are real directory entries.')
) + teaser('2.4', 'Riya renames <code>photo.jpg</code> to <code>photo.txt</code>. Windows would now call it a text file. What does Linux think it is, and how can she ask?')

MINDMAP = mindmap('Paths', [
    ('Absolute', 'acc', ['starts with /', 'same from everywhere', 'cron, configs, docs']),
    ('Relative', 'blue', ['from the current folder', '.. parent, . here', 'short, for typing']),
    ('Shortcuts', 'green', ['~ = $HOME (shell)', '~user, ~+, ~-', 'not inside quotes']),
    ('Tab', 'amber', ['Tab completes', 'Tab Tab lists', 'no match = wrong path']),
    ('Tools', 'violet', ['realpath', 'dirname, basename', './script.sh']),
    ('Behind the screen', 'red', ['walk one name at a time', 'x permission on folders', 'ENOENT, EACCES']),
])
