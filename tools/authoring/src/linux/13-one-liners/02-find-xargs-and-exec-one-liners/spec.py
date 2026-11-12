import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='02-find-xargs-and-exec-one-liners', n='13.2',
    module_label='Module 13 · Power one-liners and command combos',
    title='find + xargs + -exec: bulk rename, clean up and replace across files',
    desc='Bulk actions on many files: find tests (-name -iname -type -size -mtime -mmin -newer -empty -perm -maxdepth, ! -o), actions -print -delete -exec {} ; and {} + -execdir -ok, xargs -0 -n -I -P -r -t with -print0, ARG_MAX, safe bulk renames with read -d "", search and replace with grep -rlZ | xargs -0 sed -i.bak, previews and undo; real outputs and 35+ examples.',
    og_desc='find -exec and xargs explained with real runs: safe clean-ups, bulk renames, search and replace, -print0 and parallel xargs.',
    minutes=40, level='Beginner → Advanced',
    lead='Choose files with find, act on them with -exec or xargs: clean-ups, renames and replacements across hundreds of files, always with a preview first and safe handling of spaces.',
    chips=['\\; vs + vs xargs animated', 'Why -print0 and -0', 'Preview-then-act habit', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A small project to tidy
mkdir -p proj/logs proj/conf
touch proj/logs/a.log proj/logs/b.log proj/logs/keep.txt 'proj/conf/my app.conf' proj/conf/db.conf
echo 'host=old-server' > proj/conf/db.conf

# 1. look
find proj -name '*.log'
# 2. act
find proj -name '*.log' -delete
ls proj/logs

# names with spaces: -print0 | xargs -0
find proj -name '*.conf' -print0 | xargs -0 ls -1

# replace text in the files that contain it
grep -rlZ old-server proj | xargs -0 sed -i 's/old-server/new-server/'
cat proj/conf/db.conf
"""

RUN = dict(
    heading='Look, act, replace',
    intro='<p>Preview with find, delete the matches, handle a name with a space, and replace text only where it appears.</p>',
    code=MAIN,
    anno=[("find proj -name '*.log' -delete", 'Same expression as the preview, plus the action at the end.'), ('-print0 | xargs -0', 'Keeps “my app.conf” as one name.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file in logs survived?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many echo commands run in each line?',
             code="touch x1 x2 x3\nfind . -name 'x*' -exec echo run {} \\; | wc -l\nfind . -name 'x*' -exec echo run {} + | wc -l\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the file name has a space. Add -print0 and -0.',
             code="touch 'my file.txt'\nfind . -name 'my*' | xargs ls 2>&1\n", expect='any'),
        dict(label='4 · Your turn', hint='Delete only empty files in this folder (not folders).',
             code="touch empty1 empty2; echo data > full\nfind . -maxdepth 1 -type f -empty -delete\nls\n"),
        dict(label='5 · Challenge', hint='Rename every .txt to .md with a loop and parameter expansion.',
             code="touch a.txt b.txt\nfor f in *.txt; do mv -n -- \"$f\" \"${f%.txt}.md\"; done\nls *.md\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real clean-ups',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical. Always run the preview line first.</p>',
    items=[
        dict(title='1 · Big files in your home', cmd='find ~ -type f -size +500M -printf "%s\\t%p\\n" 2>/dev/null | sort -rn | head', output='4294967296\t/home/you/VMs/ubuntu.vdi\n…', note='Typical.'),
        dict(title='2 · Old downloads (preview)', cmd='find ~/Downloads -type f -mtime +90 | wc -l', output='212', note='Typical. Add -delete only after checking.'),
        dict(title='3 · Thumbnails cache size', cmd='du -sh ~/.cache/thumbnails 2>/dev/null', output='384M\t/home/you/.cache/thumbnails', note='Typical: safe to clean.'),
        dict(title='4 · findutils version', cmd='find --version | head -1', output=pc('find --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A safe rename loop, line by line',
    intro='<p>Step through: read NUL-separated names, build the new name, rename.</p>',
    code='''touch 'Old File.TXT' second.TXT
count=0
while IFS= read -r -d '' f; do
  new=${f#./}; new=${new// /_}; new=${new%.TXT}.txt
  mv -n -- "$f" "$new"; count=$((count+1))
done < <(find . -maxdepth 1 -name '*.TXT' -print0)
echo "renamed $count files"
''',
    notes={3: 'One NUL-separated name at a time.', 4: 'Strip ./, spaces to _, new extension.', 6: 'find feeds the loop without a subshell.'},
)

WORKED_INTRO = 'Three bulk jobs from real work, each with a preview step.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Clean a temp folder',
         problem='<p>Remove .tmp files older than one day from a cache folder, but list them first.</p>',
         inp='a cache folder', approach=['-mtime +1.', 'preview then -delete.'],
         code='''mkdir -p cache; touch cache/a.tmp cache/b.tmp cache/keep.dat
touch -d '3 days ago' cache/a.tmp
echo "would delete:"; find cache -name '*.tmp' -mtime +1
find cache -name '*.tmp' -mtime +1 -delete
ls cache
''', notes={3: 'Preview.', 4: 'Same expression + action.'}, tryit='Also delete empty subfolders.'),
    dict(level='i', tag='Developer', title='Rename to a numbered series',
         problem='<p>Rename all .JPG files to photo_001.jpg, photo_002.jpg… in name order.</p>',
         inp='photos', approach=['sort -z.', 'printf -v.'],
         code='''touch IMG_9.JPG IMG_10.JPG 'IMG 2.JPG'
n=0
while IFS= read -r -d '' f; do
  n=$((n+1)); printf -v new 'photo_%03d.jpg' "$n"
  echo "$f -> $new"; mv -n -- "$f" "$new"
done < <(find . -maxdepth 1 -name '*.JPG' -print0 | sort -z)
''', notes={6: 'sort -z sorts NUL-separated names.'}, tryit='Use sort -zV for natural number order.'),
    dict(level='a', tag='DevOps', title='Migrate a host name',
         problem='<p>Replace db-old with db-new in every .conf that contains it, keep backups, then verify.</p>',
         inp='configs', approach=['grep -rlZ.', 'sed -i.bak.', 'verify with grep -c.'],
         code='''mkdir -p etc; echo 'db=db-old' > etc/a.conf; echo 'db=db-old' > etc/b.conf; echo 'x=1' > etc/c.conf
grep -rlZ db-old etc | xargs -0 -r sed -i.bak 's/db-old/db-new/g'
echo "changed: $(ls etc/*.bak | wc -l) files"
echo "still old: $(grep -rl db-old etc --include='*.conf' | wc -l)"
''', notes={2: 'Only files that match are edited.', 4: 'Ignore the .bak copies.'}, tryit='Restore from the .bak files.'),
]

QUIZ = mix([
    dict(q='-exec cmd {} \\; runs cmd…', options=['once in total', 'once per file', 'in parallel', 'never'], answer=1, why='Per file.'),
    dict(q='-exec cmd {} + …', options=['once per file', 'with many files at once', 'only on folders', 'asks first'], answer=1, why='Batched.'),
    dict(q='Safe pipe from find to xargs:', options=['find | xargs', 'find -print0 | xargs -0', 'find -0 | xargs', 'find | xargs -n1'], answer=1, why='NUL.'),
    dict(q='Where does -delete go?', options=['first', 'last, after the tests', 'anywhere', 'before -type'], answer=1, why='Left to right.'),
    dict(q='Why quote "*.log" in find?', options=['style', 'so the shell does not expand it first', 'find needs quotes', 'for speed'], answer=1, why='Shell globbing.'),
    dict(q='xargs -P 4 …', options=['4 files per command', '4 commands at once', '4 retries', 'prints 4 lines'], answer=1, why='Parallel.'),
    dict(q='Which asks before each file?', options=['-exec', '-ok', '-delete', '-print'], answer=1, why='-ok.'),
    dict(q='sed -i.bak …', options=['deletes .bak files', 'edits and keeps a backup', 'previews only', 'edits .bak files'], answer=1, why='Backup suffix.'),
])

REVISION = [
    'Habit: find … (preview) → same find + action; add -type f; quote patterns.',
    '-delete last; -exec cmd {} \\; per file; -exec cmd {} + batched; -execdir in the folder; -ok asks.',
    'find -print0 | xargs -0 for any name; -n 1, -I{}, -P N, -r, -t.',
    'Tests: -name -iname -type -size -mtime/-mmin -newer -empty -perm -maxdepth, ! -o \\( \\).',
    'Renames: while IFS= read -r -d "" f; do …; done < <(find … -print0); preview with echo / printf %q; mv -n.',
    'Replace: grep -rlZ old | xargs -0 -r sed -i.bak "s/old/new/g"; verify; restore from .bak if needed.',
]

FAQ = [
    ('What is the difference between find -exec and xargs?', 'Both run commands on found files; -exec is built into find, xargs reads names from a pipe and can run in parallel. Use -print0 | xargs -0 for safety.'),
    ('What do {} and \\; mean in find -exec?', '{} is replaced by the file name; \\; ends the command. With + instead of \\; many names are passed at once.'),
    ('How do I delete files older than 30 days?', 'find DIR -type f -mtime +30 -delete (run it without -delete first).'),
    ('How do I handle file names with spaces in xargs?', 'Use find -print0 | xargs -0.'),
    ('How do I replace text in many files?', "grep -rlZ old DIR | xargs -0 sed -i.bak 's/old/new/g'."),
    ('How do I rename many files?', 'A loop with parameter expansion, e.g. for f in *.JPG; do mv -n "$f" "${f%.JPG}.jpg"; done; or the rename tool.'),
    ('Why "Argument list too long"?', 'The command line exceeded ARG_MAX; use find -exec {} + or xargs.'),
]

PRACTICE_INTRO = 'Small bulk tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Count .txt', stmt='Create 3 .txt files and count them with find.', inp='nothing', code="touch a.txt b.txt c.txt; find . -maxdepth 1 -name '*.txt' | wc -l\n", explain='3.'),
    dict(level='easy', title='Folders only', stmt='Create two folders and list only folders below ., not . itself.', inp='nothing', code="mkdir -p d1 d2; find . -mindepth 1 -maxdepth 1 -type d | sort\n", explain='-type d.'),
    dict(level='easy', title='Delete', stmt='Create x.tmp and delete it with find.', inp='nothing', code="touch x.tmp; find . -name '*.tmp' -delete; ls x.tmp 2>/dev/null || echo gone\n", explain='gone.'),
    dict(level='medium', title='Batch', stmt='With 4 files, show how many echo commands {} + runs.', inp='files', code="touch f1 f2 f3 f4; find . -name 'f*' -exec echo {} + | wc -l\n", explain='1.'),
    dict(level='medium', title='Spaces', stmt='List “a b.txt” safely with xargs.', inp='a name with a space', code="touch 'a b.txt'; find . -name 'a b*' -print0 | xargs -0 ls\n", explain='-0.'),
    dict(level='medium', title='Old', stmt='Make old.log 10 days old and new.log today; find files older than 5 days.', inp='two files', code="touch new.log; touch -d '10 days ago' old.log; find . -name '*.log' -mtime +5\n", explain='./old.log.'),
    dict(level='business', title='Replace', stmt='Replace v1 with v2 in all .cfg files that contain v1, then count files with v2.', inp='configs', code="echo v1 > a.cfg; echo v1 > b.cfg; echo x > c.cfg; grep -lZ v1 *.cfg | xargs -0 sed -i 's/v1/v2/'; grep -l v2 *.cfg | wc -l\n", explain='2.'),
    dict(level='business', title='Rename', stmt='Rename every .JPEG to .jpg.', inp='files', code="touch p.JPEG q.JPEG; for f in *.JPEG; do mv -- \"$f\" \"${f%.JPEG}.jpg\"; done; ls *.jpg\n", explain='p.jpg q.jpg.'),
]

SCN_INTRO = 'Interview questions about bulk file actions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Delete .log files older than 7 days”', 'Very common.', 'command?',
        '''<ul>
          <li>find /var/log/app -type f -name "*.log" -mtime +7 -delete</li>
          <li>Run without -delete first.</li>
          <li>Or put it in cron / use logrotate.</li>
        </ul>''', 'rm *.log (deletes new ones too).') +
    scn('Service company', 'Junior', '“rm: Argument list too long”', '500,000 files.', 'fix?',
        '''<ol>
          <li>The expanded * exceeded ARG_MAX.</li>
          <li>find . -name "*.tmp" -delete, or -exec rm {} +.</li>
          <li>Or xargs -0 in batches.</li>
        </ol>''', 'a for loop over $(ls).') +
    scn('Product company', 'Mid-level', 'Replace a URL in 400 files', 'Some names have spaces.', 'safe one-liner?',
        '''<ul>
          <li>grep -rlZ old . | xargs -0 sed -i.bak "s#old#new#g"</li>
          <li># as sed separator because URLs contain /.</li>
          <li>Verify with grep -rc, then delete the .bak files or commit to git.</li>
        </ul>''', 'sed on every file blindly.') +
    scn('Platform', 'Senior', 'Convert 50,000 images fast', '16 cores.', 'how?',
        '''<ul>
          <li>find … -print0 | xargs -0 -P 16 -n 50 convert-script</li>
          <li>Batches of 50 reduce process start-up cost.</li>
          <li>Or GNU parallel with a progress bar and logs.</li>
        </ul>''', 'one process at a time.')
) + interview([
    ('What does -print0 do?', 'Separates names with NUL bytes.'),
    ('-exec vs -execdir?', '-execdir runs in the file’s directory.'),
    ('What does xargs -I{} do?', 'Runs one command per item, replacing {} with it.'),
    ('What does xargs -r do?', 'Does not run the command if there is no input.'),
    ('How to find files changed in the last hour?', 'find -mmin -60.'),
    ('How to find setuid files?', 'find / -xdev -perm -4000.'),
    ('Why does sed -i break hard links?', 'It writes a new file and renames it.'),
], [
    ('RHCSA (EX200)', 'Locate files with find and act on them.'),
    ('LFCS', 'find with -exec and xargs.'),
    ('CompTIA Linux+', 'find, xargs, -exec.'),
]) + distro('GNU find and xargs are standard on Linux; macOS ships BSD versions.', [
    ('find -delete -print0', 'GNU findutils', 'GNU findutils', 'BSD find (yes)', 'Git Bash'),
    ('-printf', 'yes', 'yes', 'no (use stat)', '-'),
    ('xargs -P -r', 'yes', 'yes', '-P yes, -r is default', '-'),
    ('sed -i', 'sed -i', 'sed -i', "sed -i '' (BSD)", '-'),
    ('rename tool', 'apt install rename', 'prename / rename', 'brew install rename', '-'),
]) + teaser('13.3', 'The website was slow at 10 a.m. Riya has a 2-million-line access log and ten minutes. Who hit the site the most, which URLs failed, and when did the errors start? Next: log analysis one-liners.')

CHEATSHEET = cheatsheet('find + xargs', [
    ('Select', [('-name "*.x"', 'pattern'), ('-type f/d', 'kind'), ('-size +100M', 'size'), ('-mtime +30', 'age'), ('-maxdepth 1', 'depth')]),
    ('Act', [('-print', 'preview'), ('-delete', 'remove (last)'), ('-exec c {} \\;', 'per file'), ('-exec c {} +', 'batched'), ('-ok c {} \\;', 'ask')]),
    ('xargs', [('-print0 | xargs -0', 'safe'), ('-n 1', 'one each'), ('-I{}', 'placeholder'), ('-P 4', 'parallel'), ('-r', 'no empty run')]),
    ('Bulk', [('grep -rlZ x | xargs -0 sed -i.bak', 'replace'), ('mv -n "$f" "${f%.a}.b"', 'rename'), ('echo first', 'preview'), ('*.bak', 'undo')]),
])

MINDMAP = mindmap('find + xargs', [
    ('Select', 'blue', ['-name -type', '-size -mtime', '! -o ( )']),
    ('Preview', 'green', ['-print', '-ls', 'wc -l']),
    ('-exec', 'amber', ['{} \\;', '{} +', '-execdir -ok']),
    ('xargs', 'violet', ['-0', '-n -I', '-P -r']),
    ('Bulk', 'acc', ['rename', 'sed -i.bak', 'clean-up']),
    ('Traps', 'red', ['spaces', '-delete first', 'unquoted *']),
])

LAB = lab('clean up a project', 'Build the lab, write <code>~/lab132/tidy.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab132 && cd ~/lab132 && rm -rf proj tidy.sh
mkdir -p proj/build proj/src proj/empty1 proj/empty2/deeper
touch proj/build/a.o proj/build/b.o 'proj/src/main file.c' proj/src/util.c proj/src/notes.TXT
echo 'server=old.example.com' > proj/src/util.c; echo 'see old.example.com' > proj/src/notes.TXT
touch -d '20 days ago' proj/build/a.o''',
    tasks=['Delete every <code>.o</code> file older than 7 days under <code>proj</code> (only a.o is that old).',
           'Delete all empty folders under <code>proj</code> (empty1, empty2 and deeper).',
           'Replace <code>old.example.com</code> with <code>new.example.com</code> in every file that contains it, without backup files.',
           'Rename every <code>.TXT</code> file to lower-case <code>.txt</code>, and every name with a space to use <code>_</code> instead.'],
    solution='''cat > tidy.sh <<'EOF'
cd ~/lab132
find proj -type f -name '*.o' -mtime +7 -delete
find proj -mindepth 1 -type d -empty -delete
grep -rlZ old.example.com proj | xargs -0 -r sed -i 's/old\\.example\\.com/new.example.com/g'
while IFS= read -r -d '' f; do mv -n -- "$f" "${f%.TXT}.txt"; done < <(find proj -name '*.TXT' -print0)
while IFS= read -r -d '' f; do d=${f%/*}; b=${f##*/}; mv -n -- "$f" "$d/${b// /_}"; done < <(find proj -name '* *' -print0)
EOF''',
    check='''cd ~/lab132; rm -rf proj
mkdir -p proj/build proj/src proj/empty1 proj/empty2/deeper
touch proj/build/a.o proj/build/b.o 'proj/src/main file.c' proj/src/util.c proj/src/notes.TXT
echo 'server=old.example.com' > proj/src/util.c; echo 'see old.example.com' > proj/src/notes.TXT
touch -d '20 days ago' proj/build/a.o
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f tidy.sh ] && bash tidy.sh 2>/dev/null
ok "1 old .o"  '[ ! -e proj/build/a.o ] && [ -e proj/build/b.o ]'
ok "2 empty"   '[ ! -e proj/empty1 ] && [ ! -e proj/empty2 ] && [ -d proj/src ]'
ok "3 replace" '! grep -rq old.example.com proj && [ "$(grep -rl new.example.com proj | wc -l)" = 2 ] && [ -z "$(find proj -name "*.bak")" ]'
ok "4 rename"  '[ -e proj/src/notes.txt ] && [ -e proj/src/main_file.c ] && [ -z "$(find proj -name "* *" -o -name "*.TXT")" ]' ''')
