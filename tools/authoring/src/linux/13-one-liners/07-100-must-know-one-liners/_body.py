import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

H = r"""rm -rf ~/h; mkdir -p ~/h/{docs,logs,src,photos,old}; cd ~/h
printf 'alpha\nbeta\ngamma\nbeta\ndelta\n' > words.txt
printf 'name,dept,salary\nRiya,IT,72000\nAman,HR,51000\nZoya,IT,88000\nNeha,Sales,64000\nRavi,HR,47000\n' > staff.csv
printf '%s\n' '10.0.0.5 GET /home 200' '10.0.0.7 GET /login 401' '10.0.0.5 POST /login 200' '10.0.0.9 GET /admin 403' '10.0.0.5 GET /home 200' '10.0.0.7 GET /api 500' > logs/access.log
printf '2026-11-11 10:00 INFO start\n2026-11-11 10:01 ERROR db down\n2026-11-11 10:02 WARN retry\n2026-11-11 10:03 ERROR db down\n' > logs/app.log
printf 'port=8080\nhost=localhost\n# comment\n\ndebug=false\n' > docs/app.conf
for f in main util test; do printf 'def %s():\n    return 1  # TODO tidy\n' $f > src/$f.py; done
touch photos/IMG_1.JPG photos/IMG_2.JPG 'photos/my trip.JPG'; head -c 2M /dev/zero > old/big.iso; touch -d '60 days ago' old/big.iso
printf 'line one\r\nline two\r\n' > docs/windows.txt"""

def g(title, items):
    return (title, [dict(title=t_, cmd=c, setup=H, why=w, **({'expect': 'any'} if any else {})) for t_, c, w, *any in items])

VAR = variations('The 100: grouped by job, each one really run on our build machine on a small sample folder <code>~/h</code> (words.txt, staff.csv, logs/, docs/, src/, photos/, old/). Read the one-line explanation, then try a variation of your own.', [
    g('1–10 · Files and folders', [
        ('1. Make a folder tree in one go', "cd ~/h; mkdir -p proj/{src,docs,tests}; ls proj", 'Brace expansion (12.11).'),
        ('2. Go back to the previous folder', "cd /tmp; cd ~/h; cd - > /dev/null; pwd", 'cd - toggles.'),
        ('3. Newest files first', "cd ~/h; ls -t | head -3", 'ls -t sorts by time.'),
        ('4. Biggest files first, human sizes', "cd ~/h; ls -lhS old/* logs/* | head -2 | awk '{print $5, $NF}'", 'ls -S by size.'),
        ('5. Tree without the tree command', "cd ~/h; find src docs -print | sort | sed 's|[^/]*/|  |g'", 'A quick indented view.'),
        ('6. Copy with a backup of the target', "cd ~/h; cp docs/app.conf /tmp/a.conf; cp --backup=numbered docs/app.conf /tmp/a.conf; ls /tmp/a.conf* | wc -l; rm -f /tmp/a.conf*", 'Never lose the old version.'),
        ('7. Move without overwriting', "cd ~/h; touch x y; mv -n x y; ls x y", 'mv -n.'),
        ('8. Rename all .JPG to .jpg', "cd ~/h/photos; for f in *.JPG; do mv -n -- \"$f\" \"${f%.JPG}.jpg\"; done; ls", 'Parameter expansion.'),
        ('9. Delete files older than 30 days (preview)', "cd ~/h; find old -type f -mtime +30", 'Add -delete only after checking (13.2).'),
        ('10. Empty folders', "cd ~/h; mkdir -p e1 e2/e3; find . -type d -empty | sort", 'Clean-up candidates.'),
    ]),
    g('11–20 · Viewing and searching text', [
        ('11. First and last lines', "cd ~/h; head -2 words.txt; tail -1 words.txt", 'head / tail.'),
        ('12. Lines 2 to 4', "cd ~/h; sed -n '2,4p' words.txt", 'A slice.'),
        ('13. Number the lines', "cd ~/h; nl -ba words.txt | head -2", 'nl -ba numbers blank lines too.'),
        ('14. Case-insensitive search', "cd ~/h; grep -i error logs/app.log | wc -l", 'grep -i.'),
        ('15. Search recursively with line numbers', "cd ~/h; grep -rn TODO src | head -2", 'grep -rn.'),
        ('16. Only file names that match', "cd ~/h; grep -rl TODO src | sort", 'grep -l.'),
        ('17. Lines around a match', "cd ~/h; grep -A1 ERROR logs/app.log | head -3", '-A after, -B before, -C both.'),
        ('18. Lines that do NOT match', "cd ~/h; grep -v '^#' docs/app.conf | grep -v '^$'", 'Config without comments and blanks.'),
        ('19. Several patterns', "cd ~/h; grep -E 'ERROR|WARN' logs/app.log | wc -l", 'grep -E with |.'),
        ('20. Whole words only', "cd ~/h; printf 'cat\\ncatalog\\n' | grep -w cat", '-w matches whole words.'),
    ]),
    g('21–30 · Transforming text', [
        ('21. Replace all occurrences', "cd ~/h; sed 's/beta/BETA/g' words.txt | paste -sd' '", 'sed s///g.'),
        ('22. Edit a file in place with a backup', "cd ~/h; sed -i.bak 's/8080/9090/' docs/app.conf; head -1 docs/app.conf; ls docs/app.conf.bak", 'sed -i.bak.'),
        ('23. Delete blank lines', "cd ~/h; sed '/^$/d' docs/app.conf | wc -l", 'Pattern /^$/.'),
        ('24. Upper case', "echo 'hello world' | tr a-z A-Z", 'tr ranges.'),
        ('25. Squeeze spaces', "echo 'a    b     c' | tr -s ' '", 'tr -s.'),
        ('26. Remove Windows line endings', "cd ~/h; tr -d '\\r' < docs/windows.txt | cat -A", 'No more ^M.'),
        ('27. Print a column', "cd ~/h; cut -d, -f1 staff.csv | tail -n +2 | paste -sd' '", 'cut -d -f.'),
        ('28. Swap two columns', "cd ~/h; awk -F, -v OFS=, '{print $2, $1}' staff.csv | head -2", 'awk with OFS.'),
        ('29. Add line numbers to the start', "cd ~/h; awk '{print NR\": \"$0}' words.txt | head -2", 'NR is the line number.'),
        ('30. Reverse lines', "cd ~/h; tac words.txt | head -2", 'tac is cat backwards.'),
    ]),
    g('31–40 · Counting and statistics', [
        ('31. Lines, words, characters', "cd ~/h; wc words.txt", 'wc.'),
        ('32. Count unique values', "cd ~/h; sort -u words.txt | wc -l", 'sort -u.'),
        ('33. Count each value, most first', "cd ~/h; sort words.txt | uniq -c | sort -rn | head -2", 'The classic.'),
        ('34. Duplicated lines only', "cd ~/h; sort words.txt | uniq -d", 'uniq -d.'),
        ('35. Sum a column', "cd ~/h; awk -F, 'NR>1{s+=$3} END{print s}' staff.csv", 'awk sum.'),
        ('36. Average', "cd ~/h; awk -F, 'NR>1{s+=$3; n++} END{printf \"%.0f\\n\", s/n}' staff.csv", 'Sum / count.'),
        ('37. Max with the name', "cd ~/h; tail -n +2 staff.csv | sort -t, -k3 -rn | head -1 | cut -d, -f1,3", 'Sort numerically by column 3.'),
        ('38. Total per group', "cd ~/h; awk -F, 'NR>1{t[$2]+=$3} END{for(d in t) print d, t[d]}' staff.csv | sort", 'awk array group-by.'),
        ('39. Top IPs in a log', "cd ~/h; awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn | head -1", '13.3.'),
        ('40. Status code counts', "cd ~/h; awk '{print $4}' logs/access.log | sort | uniq -c", 'Field of interest.'),
    ]),
    g('41–50 · Processes', [
        ('41. My processes', "ps -u riya -o pid=,comm= | wc -l | sed 's/^/processes: /'", 'ps -u.'),
        ('42. Top CPU users', "timeout 3 yes > /dev/null & sleep 1; ps -u riya -o %cpu=,comm= --sort=-%cpu | head -1 | awk '{print $2}'; kill %1", '--sort=-%cpu.'),
        ('43. Top memory users', "ps -u riya -o rss=,comm= --sort=-rss | head -1 | awk '{print $2}'", '--sort=-rss.'),
        ('44. Find a process by name', "sleep 30 & pgrep -a -x sleep -P $$ | awk '{print $2, $3}'; kill %1", 'pgrep -a.'),
        ('45. Stop by name', "sleep 31 & pkill -x -P $$ sleep; wait 2>/dev/null; pgrep -c -x sleep -P $$", 'pkill -x.', 1),
        ('46. Process tree of this shell', "sleep 5 & pstree -p $$ | sed -E 's/[0-9]+/N/g'; kill %1", 'pstree.'),
        ('47. Run in the background, survive logout', "nohup sleep 1 > /dev/null 2>&1 & echo \"started $!\" | sed 's/[0-9]*$/PID/'", 'nohup … & (11.4).'),
        ('48. Time limit for a command', "timeout 1 sleep 5; echo \"status $?\"", 'timeout → 124.'),
        ('49. Low priority', "nice -n 19 bash -c 'echo nice=$(nice)'", 'nice (11.5).'),
        ('50. How long has the system run?', "uptime -p | sed -E 's/[0-9]+/N/g'", 'uptime -p.'),
    ]),
    g('51–60 · Disk and memory', [
        ('51. Disk usage overview', "df -h ~ | awk 'NR==2{print $5, \"used\"}'", 'df -h.'),
        ('52. Biggest folders here', "cd ~/h; du -sh * | sort -rh | head -2", 'du | sort -rh.'),
        ('53. Files bigger than 1 MB', "cd ~/h; find . -type f -size +1M", 'find -size.'),
        ('54. Inode usage', "df -i ~ | awk 'NR==2{print $5, \"inodes used\"}'", 'df -i.'),
        ('55. Memory available', "free -m | awk 'NR==2{print ($7>0 ? \"available: yes\" : \"no\")}'", 'free (column available).'),
        ('56. Folder size in bytes', "cd ~/h; du -sb old | cut -f1", 'du -sb.'),
        ('57. Count files in a tree', "cd ~/h; find . -type f | wc -l", 'find | wc -l.'),
        ('58. Disk use of one file type', "cd ~/h; find . -name '*.py' -print0 | du -ch --files0-from=- | tail -1", 'du on a list.'),
        ('59. Deleted but open files (yours)', "lsof -a +L1 -u riya 2>/dev/null | wc -l | sed 's/^/lines: /'", 'lsof +L1 (13.4).'),
        ('60. Make a 10 MB test file', "cd ~/h; truncate -s 10M test.img; ls -lh test.img | awk '{print $5}'; du -h test.img | cut -f1", 'truncate makes a sparse file: 10M logical, 0 on disk.'),
    ]),
    g('61–70 · Users, permissions and identity', [
        ('61. Who am I, in which groups', "id -un; id -Gn | wc -w | sed 's/^/groups: /'", 'id.'),
        ('62. Make a script executable', "cd ~/h; echo 'echo hi' > hi.sh; chmod +x hi.sh; ./hi.sh", 'chmod +x.'),
        ('63. Permissions in octal', "cd ~/h; stat -c '%a %n' words.txt", 'stat -c %a.'),
        ('64. Private file', "cd ~/h; chmod 600 docs/app.conf; ls -l docs/app.conf | cut -c1-10", 'Owner only.'),
        ('65. Files writable by everyone', "cd ~/h; chmod o+w words.txt; find . -type f -perm -o+w; chmod o-w words.txt", 'Security audit (9.x).'),
        ('66. Default permissions for new files', "umask; (umask 077; touch secret; stat -c %a secret)", 'umask.'),
        ('67. Accounts with a real shell', "grep -vE 'nologin|false$' /etc/passwd | cut -d: -f1 | wc -l | sed 's/^/accounts: /'", '/etc/passwd.'),
        ('68. My home folder from passwd', "getent passwd riya | cut -d: -f6", 'getent.'),
        ('69. Owner and group of a file', "cd ~/h; stat -c '%U:%G' words.txt", 'stat %U %G.'),
        ('70. Change only folders’ permissions', "cd ~/h; find src -type d -exec chmod 755 {} +; stat -c %a src", 'Folders vs files.'),
    ]),
    g('71–80 · Archives, compression and checksums', [
        ('71. Make a tar.gz', "cd ~/h; tar czf src.tgz src; tar tzf src.tgz | wc -l", 'tar czf.'),
        ('72. List without extracting', "cd ~/h; tar czf src.tgz src; tar tzf src.tgz | head -2", 'tar t.'),
        ('73. Extract into another folder', "cd ~/h; tar czf src.tgz src; mkdir -p x; tar xzf src.tgz -C x; ls x/src | wc -l", '-C.'),
        ('74. Exclude files', "cd ~/h; tar czf s.tgz --exclude='*.py' src docs; tar tzf s.tgz | grep -c py", '--exclude.', 1),
        ('75. Compress one file, keep the original', "cd ~/h; gzip -k words.txt; ls words.txt*", 'gzip -k.'),
        ('76. Read a .gz without extracting', "cd ~/h; gzip -k words.txt; zcat words.txt.gz | head -1", 'zcat / zgrep.'),
        ('77. Zip for Windows users', "cd ~/h; zip -qr docs.zip docs; unzip -l docs.zip | tail -1 | awk '{print $2, \"files\"}'", 'zip -r.'),
        ('78. Checksum', "cd ~/h; sha256sum words.txt | cut -c1-16", 'sha256sum (19.4).'),
        ('79. Verify checksums later', "cd ~/h; sha256sum *.txt *.csv > SUMS; sha256sum -c SUMS", '-c checks a list.'),
        ('80. Split and join a big file', "cd ~/h; split -b 512K old/big.iso part_; ls part_* | wc -l; cat part_* | cmp - old/big.iso && echo identical", 'split / cat.'),
    ]),
    g('81–90 · System and network information', [
        ('81. Kernel and OS', "uname -sr | sed -E 's/[0-9][0-9.]*[^ ]*/VERSION/'; grep -m1 PRETTY /etc/os-release | cut -d= -f2", 'uname, os-release.'),
        ('82. CPU count', "nproc", 'nproc.'),
        ('83. Host name', "hostname", 'hostname.'),
        ('84. Current date in ISO format', "date +%F | sed 's/[0-9]/N/g'", 'date +FORMAT.'),
        ('85. Date in another time zone', "TZ=UTC date +%Z", 'TZ= for one command.'),
        ('86. Seconds since 1970 and back', "s=$(date -d '2026-01-01 00:00 UTC' +%s); echo $s; date -u -d @$s +%F", 'Epoch time.'),
        ('87. Is a local port open?', "(exec 3<>/dev/tcp/127.0.0.1/1) 2>/dev/null && echo open || echo closed", 'bash /dev/tcp (16.4).'),
        ('88. My IP addresses', "hostname -I 2>/dev/null | wc -w | sed 's/^/addresses: /'", 'hostname -I (ip addr on full systems).'),
        ('89. DNS servers configured', "grep -c ^nameserver /etc/resolv.conf | sed 's/^/nameservers: /'", '/etc/resolv.conf.'),
        ('90. Environment variable list (sorted)', "env | cut -d= -f1 | sort | head -3", 'env.'),
    ]),
    g('91–100 · Shell and scripting tricks', [
        ('91. Repeat the last command’s argument', "echo one two three; echo \"last argument was: $_\"", '$_ is the last argument.'),
        ('92. Run only if the previous worked', "cd ~/h && echo 'in ~/h' || echo 'cd failed'", '&& and ||.'),
        ('93. Loop over files safely', "cd ~/h/photos; for f in *; do printf '[%s]\\n' \"$f\"; done", 'Quotes keep spaces.'),
        ('94. Read a file line by line', "cd ~/h; while IFS= read -r l; do echo \"> $l\"; done < words.txt | head -2", 'while read.'),
        ('95. Compare two command outputs', "diff <(printf 'a\\nb\\n') <(printf 'a\\nc\\n') | grep '^[<>]'", 'Process substitution.'),
        ('96. Save output and see it', "cd ~/h; ls | tee listing.txt | wc -l", 'tee.'),
        ('97. Sequence of numbers', "seq -s ' ' 1 2 9", 'seq START STEP END.'),
        ('98. Random number and password', "echo $((RANDOM % 100)) | sed 's/[0-9]*/N/'; tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 12 | wc -c", '$RANDOM, /dev/urandom.'),
        ('99. Calculator', "echo $((7 * 6)); echo 'scale=2; 10/3' | bc", '$(( )) integers, bc decimals.'),
        ('100. Explain any command', "type -a printf | head -1; help -d echo | tail -1", 'type, help, man, --help.'),
    ]),
], hid='the-100')

HOOK = hook('This is the lesson to bookmark. Over 13 modules you have met hundreds of commands; in daily work you reach for the same hundred one-liners again and again. Here they are, grouped by job (files, text, counting, processes, disk, users, archives, system, scripting), each <b>really run</b> on a small sample folder with its real output and a one-line explanation. Then come the patterns behind them, a timed challenge and a lab that asks you to solve tasks with one line each.',
    ['recall 100 everyday one-liners by job, and know what each part does',
     'recognise the few patterns behind most of them (filter | field | sort | uniq -c, find … -exec, loops over files, $( ) and <( ))',
     'adapt a one-liner to a new task instead of memorising it',
     'check yourself with the challenge and the lab'])
ROAD = roadmap([
    ('story', 'The story', 2, 'a cheat sheet that runs'),
    ('decide', 'Find the right group', 2, 'the quick chart'),
    ('definition', 'The patterns behind them', 5, 'six shapes'),
    ('types', 'Map of the 100', 3, 'groups and lessons'),
    ('commands', 'The 100', 20, 'every one really run'),
    ('animation', 'See it happen', 3, 'one pattern, many uses'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'The challenge lab', 8, 'ten tasks, one line each'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which group of the 100? (decide in 5 seconds)', [
    ('Create, copy, rename, delete files', '1–10 · Files and folders', 'files'),
    ('Look inside files, search', '11–20 · Viewing and searching', 'text'),
    ('Change text, columns, line endings', '21–30 · Transforming', 'edit'),
    ('How many? Totals, top N', '31–40 · Counting and statistics', 'count'),
    ('What is running?', '41–50 · Processes', 'ps'),
    ('Disk full? Memory?', '51–60 · Disk and memory', 'df du'),
    ('Who? Permissions?', '61–70 · Users and permissions', 'id chmod'),
    ('Pack, compress, verify', '71–80 · Archives and checksums', 'tar sha256'),
    ('About the machine', '81–90 · System and network', 'uname date'),
    ('Shell tricks', '91–100 · Scripting', 'loops tee'),
])

cmap = concept_map(
    [('13.1', 'Combining', '| && ; $( ) <( )'), ('13.2', 'find + xargs', 'bulk actions'), ('13.6', 'Which command', 'choosing')],
    ['100 one-liners by job', 'six patterns behind them', 'adapting instead of memorising', 'a self-check challenge'],
    [('14.1', 'Packages', 'installing missing tools'), ('17.4', 'cron', 'running one-liners on a schedule'), ('21.2', 'Final cheat sheet', 'whole course'), ('21.3', 'Interview questions', 'practice')],
    'A hundred one-liners are really six patterns used on different data. Learn the patterns and you can write the hundred-and-first.')

sc = (term(20, 14, 316, 156, ['$ sort words.txt | uniq -c | sort -rn | head -2', ('      2 beta', 'out'), ('      1 gamma', 'out'), "$ awk -F, 'NR>1{t[$2]+=$3} END…' staff.csv", ('HR 98000', 'out'), ('IT 160000', 'acc')], title='riya@web01: ~/h', prompt='riya@web01:~/h$', size=6.6, step=17)
      + t(352, 36, 'Patterns:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['filter | count', 'group with awk', 'find … -exec', 'loop over files', 'compare <( )'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A cheat sheet that runs</h2>
  <div class="story">
''' + puzzle('Riya prints a famous “100 Linux one-liners” page from the internet. Within a week three of them fail on her server: one uses <code>netstat</code> (not installed), one counts duplicates with <code>uniq -c</code> on an unsorted file, and one deletes old files with <code>find … -delete -mtime +30</code>. Which three habits would have caught these before running them?') + '''
    <p class="narration">Riya keeps two one-liners that she uses every day.</p>
''' + scene('A terminal: counting duplicate words with sort, uniq -c and sort -rn, and totalling salaries per department with an awk array.', sc,
            'Most one-liners are the same <tspan font-weight="700" class="s-acc">few patterns</tspan> on different data.') + '''
K> Should I learn all hundred by heart?
A> No. Learn the six patterns in the next section and keep this page as a reference. When you need something, find the group, copy the closest one-liner, and change the file name, the column number or the pattern.
R> And the puzzle?
A> Every one-liner here was run on a real machine first. Before trusting one from anywhere: check the tool exists, read it part by part, and run the read-only version first.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Six recipe cards: FILTER-COUNT (grep | sort | uniq -c), GROUP (awk arrays), BULK (find … -exec), LOOP (for f in …), COMPARE (diff &lt;( ) &lt;( )), CHAIN (&& ||).">'
       + ''.join(label_box(14 + (i % 3) * 206, 20 + (i // 3) * 78, 198, 68, [a, b], c, 8.4) for i, (a, b, c) in enumerate([
           ('FILTER → COUNT', 'grep | cut | sort | uniq -c', 'blue'), ('GROUP', "awk '{t[$k]+=$v} END…'", 'green'), ('BULK', 'find … -exec cmd {} +', 'amber'),
           ('LOOP', 'for f in *; do …"$f"…; done', 'violet'), ('COMPARE', 'diff <(a) <(b)', 'red'), ('CHAIN', 'a && b || c', 'acc')]))
       + t(320, 192, 'Change the file, the column or the pattern; keep the shape.', 9.6, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('The 100 at four depths', [
    ('v', 'No jargon: six recipe cards', '      <p>A hundred dishes from six recipes.</p>' + pic),
    ('b', 'How to use this page', '''      <ul>
        <li>Find the group for your job in the chart above.</li>
        <li>Copy the closest one-liner and change file names and numbers.</li>
        <li>Run read-only parts first (no -delete, -i or rm until you are sure).</li>
        <li>Try the variation idea under each one.</li>
      </ul>'''),
    ('i', 'The six patterns', '''      <ol>
        <li><b>Filter → field → count:</b> <code>grep X | cut -dD -fN | sort | uniq -c | sort -rn | head</code>.</li>
        <li><b>Group in awk:</b> <code>awk -F, '{t[$k]+=$v} END{for(x in t) print x, t[x]}'</code>.</li>
        <li><b>Bulk on files:</b> <code>find DIR tests -exec cmd {} +</code> or <code>-print0 | xargs -0</code>.</li>
        <li><b>Loop over files:</b> <code>for f in *.x; do cmd "$f"; done</code>, or <code>while read -r</code> for lines.</li>
        <li><b>Compare:</b> <code>diff/comm &lt;(cmd1) &lt;(cmd2)</code>.</li>
        <li><b>Chain safely:</b> <code>step1 &amp;&amp; step2 || alert</code>.</li>
      </ol>'''),
    ('a', 'Behind the screen: portability and safety', '''      <ul>
        <li>GNU-specific options (<code>sed -i</code> without a suffix, <code>find -printf</code>, <code>ls --sort</code>, <code>date -d</code>) differ on macOS/BSD; check <code>--version</code> on a new system.</li>
        <li>Tools may be missing (<code>ss</code>, <code>rsync</code>, <code>locate</code> on minimal images): <code>command -v tool</code> before relying on one in scripts.</li>
        <li>Locale affects sort order and character classes: <code>LC_ALL=C</code> makes results reproducible and faster.</li>
        <li>Quote every variable and file name (<code>"$f"</code>) and use <code>--</code> before file names that may start with a dash.</li>
        <li>For scripts, add <code>set -euo pipefail</code> so a failing part stops the script (Lesson 12.6).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What a one-liner is, and the patterns behind the 100</h2>
''' + def_block(
    'A <b>one-liner</b> is a complete solution to a task written as a single command line, usually by combining small tools with pipes, lists, substitutions and loops. Good one-liners are short, read-only by default, quote their file names, and follow a small set of reusable <b>patterns</b>: filter-and-count, group with awk, bulk actions with find, loops over files, comparing outputs, and safe chains.',
    'One line, one task: a few patterns applied to different data.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('One-liner', 'A task solved in one command line.'),
    ('Pattern', 'A reusable shape of one-liner.'),
    ('Read-only first', 'Run without -delete, -i or rm to check.'),
    ('Portability', 'Works on other systems too.'),
    ('GNU', 'The tools on most Linux systems.'),
    ('BSD', 'The tools on macOS, FreeBSD.'),
    ('Sample data', 'A small file to test on first.'),
    ('Challenge', 'Solving a task without looking.'),
]) + '\n' + names('Where the names come from.', [
    ('one-liner', 'one line', 'From Perl and awk culture.'),
    ('cheat sheet', 'a crib note', 'Allowed here.'),
    ('tac', 'cat reversed', 'GNU coreutils.'),
    ('nl', 'number lines', 'Unix.'),
    ('seq', 'sequence', 'Plan 9 / GNU.'),
    ('bc', 'basic calculator', 'Unix 1975.'),
    ('truncate', 'set file size', 'GNU.'),
    ('getent', 'get entries', 'Name service lookups.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Count values', '<code>sort | uniq -c | sort -rn</code>'),
    ('Group', '<code>t[$k]+=$v</code>'),
    ('Bulk', '<code>find -exec {} +</code>'),
    ('Loop', '<code>for f in *; do …</code>'),
    ('Compare', '<code>diff &lt;( ) &lt;( )</code>'),
    ('Chain', '<code>a &amp;&amp; b || c</code>'),
]) + '\n' + lv + didyou('Many classic one-liner collections (“sed one-liners”, “awk one-liners”) date from the 1990s Usenet era. They still work because the tools kept their interfaces for 30 years: a one-liner learned today will likely still work when you retire.') + '''
EXAM> “Write a one-liner to find the 5 most frequent words in a file.” → tr -s ' ' '\\n' &lt; file | sort | uniq -c | sort -rn | head -5.
''' + qc('Which one pattern answers “top 3 X by count” for almost any X?', 'extract X | sort | uniq -c | sort -rn | head -3.') + mistake('copying one-liners from the internet and running them as root',
    'read every part, check the tools exist (command -v), run on sample data, read-only first',
    'Three of the printed one-liners in the puzzle failed or were dangerous; all three habits would have caught them.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Map of the 100</h2>
''' + table(['Group', 'Numbers', 'Main tools', 'Learned in'], [
    ['Files and folders', '1–10', 'mkdir, cd, ls, cp, mv, find', 'Modules 2, 3, 7'],
    ['Viewing and searching', '11–20', 'head, tail, sed -n, nl, grep', 'Modules 3, 6'],
    ['Transforming text', '21–30', 'sed, tr, cut, awk, tac', 'Module 6'],
    ['Counting and statistics', '31–40', 'wc, sort, uniq, awk', 'Modules 6, 13'],
    ['Processes', '41–50', 'ps, pgrep, pkill, nohup, timeout, nice', 'Module 11'],
    ['Disk and memory', '51–60', 'df, du, find, free, lsof, truncate', 'Modules 13, 15'],
    ['Users and permissions', '61–70', 'id, chmod, stat, umask, getent', 'Modules 8, 9'],
    ['Archives and checksums', '71–80', 'tar, gzip, zip, sha256sum, split', 'Modules 14, 19'],
    ['System and network', '81–90', 'uname, nproc, date, /dev/tcp, env', 'Modules 12, 16, 18'],
    ['Shell and scripting', '91–100', '$_, &&, for, while read, tee, seq, bc', 'Module 12'],
], minw=520) + table(['Pattern', 'Shape', 'Examples in the 100'], [
    ['Filter → field → count', '<code>… | sort | uniq -c | sort -rn</code>', '33, 39, 40'],
    ['Group in awk', '<code>t[$k]+=$v</code>', '35–38'],
    ['Bulk on files', '<code>find … -exec</code>', '9, 10, 53, 65, 70'],
    ['Loop over files / lines', '<code>for f in *</code>, <code>while read</code>', '8, 93, 94'],
    ['Compare', '<code>diff &lt;( ) &lt;( )</code>, <code>cmp</code>, <code>sha256sum -c</code>', '79, 80, 95'],
    ['Chain', '<code>&amp;&amp; ||</code>', '92'],
], minw=480) + qc('Which group would you open to find a one-liner for “sum a column”?', '31–40 · Counting and statistics (35).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> The 100</span>
  <h2>100 must-know one-liners, each really run</h2>
  <p id="commands">Every one-liner below starts from the same fresh sample folder <code>~/h</code> on our Ubuntu 24.04 build machine, user riya. Outputs that depend on the machine (process counts, dates, versions) are shown as N where the exact number does not matter.</p>
''' + VAR + '''
</section>
'''

def pattern(k):
    uses = [("awk '{print $1}' access.log", 'top IPs'), ("cut -d, -f2 staff.csv", 'staff per department'), ("grep -o '[A-Z]*' app.log", 'log levels'), ("tr -s ' ' '\\n' < text", 'top words')]
    o = label_box(60, 14, 240, 34, ['… | sort | uniq -c | sort -rn | head'], 'blue', 8.4)
    for i in range(k + 1):
        o += label_box(10, 64 + i * 26, 220, 22, [uses[i][0]], 'green' if i == k else 'card', 7.2) + t(300, 79 + i * 26, uses[i][1], 8, 'violet', bold=(i == k))
    return o
see_cmds = [["$ awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -1", ('3 10.0.0.5', 'out')],
            ["$ cut -d, -f2 staff.csv | tail -n +2 | sort | uniq -c | sort -rn | head -1", ('2 IT', 'out')],
            ["$ grep -oE 'INFO|WARN|ERROR' app.log | sort | uniq -c | sort -rn | head -1", ('2 ERROR', 'out')],
            ["$ tr -s ' ' '\\n' < notes.txt | sort | uniq -c | sort -rn | head -1", ('5 the', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/h', prompt='$', size=6.8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['IPs.', 'Departments.', 'Levels.', 'Words.'])]
behind = [pattern(k) for k in range(4)]
two = anim_two('One pattern, four questions', 'Behind the screen: only the first part changes',
               'Four terminals using sort | uniq -c | sort -rn | head on IPs, departments, log levels and words.',
               'One fixed pattern box at the top; below it four different first stages for different questions.', see, behind,
               ['IPs.', 'Depts.', 'Levels.', 'Words.'],
               ['IP', 'dept', 'level', 'word'])

def safety(k):
    steps = [('1. Does the tool exist?', 'command -v netstat || echo missing'), ('2. Read it part by part', 'run each stage alone'), ('3. Sample data first', '~/h, a copy, a VM'), ('4. Read-only first', 'no -delete, -i, rm'), ('5. Then the real run', 'and check the result')]
    return ''.join(label_box(14, 10 + i * 34, 330, 28, [f'{a}: {b}'], 'green' if i <= k else 'card', 7.6) for i, (a, b) in enumerate(steps))
s1 = anim_one('Animated example', 'Five checks before running any one-liner',
              'The habits that catch broken or dangerous one-liners.',
              'check → read → sample → read-only → run', 'Five steps light up one after another: tool exists, read each part, test on sample data, run read-only, then the real run.', [safety(k) for k in range(5)],
              ['Exists?', 'Read.', 'Sample.', 'Read-only.', 'Run.'], hid='scenario-safety')

dx = dissect('Layer by layer: checking a one-liner before you trust it',
    'Each layer has a real command and output from our build machine.', [
    dict(key='exists', name='Tool exists', sub='command -v', why='Missing tools.', how='Exit status.', impl='PATH lookup.', used='Scripts.',
         cmd="for t in awk netstat ss lsof; do command -v $t > /dev/null && echo \"$t: yes\" || echo \"$t: missing\"; done"),
    dict(key='stage', name='Stage by stage', sub='read it', why='Understand.', how='Cut the pipe.', impl='One stage at a time.', used='Debugging.',
         setup=H, cmd="cd ~/h; awk '{print $1}' logs/access.log | head -2; echo '--- + sort | uniq -c'; awk '{print $1}' logs/access.log | sort | uniq -c"),
    dict(key='dry', name='Read-only version', sub='preview', why='Safety.', how='Remove the action.', impl='echo / -print.', used='Deletes, edits.',
         setup=H, cmd="cd ~/h; find old -type f -mtime +30; sed 's/8080/9090/' docs/app.conf | head -1; echo 'rm would remove:' old/*.iso"),
    dict(key='ver', name='GNU or BSD?', sub='--version', why='Options differ.', how='Ask the tool.', impl='coreutils.', used='New systems.',
         cmd="sed --version | head -1; date --version | head -1"),
], hint='From “does it exist” to “which version”. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One pattern, many uses, and five checks</h2>
''' + two + s1 + dx + qc('What is the read-only version of <code>find old -mtime +30 -delete</code>?', 'find old -mtime +30 (the same without -delete).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The 100 at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['runbooks', 'ops'], 'blue', 8.6), '1. Team runbooks',
              'Operations teams keep their own tested one-liner lists for incidents: disk full, top IPs, stuck processes.', ['Incident', '*runbook line', 'answer']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['aliases', 'speed'], 'green', 8.6), '2. Personal aliases and functions',
    'The one-liners you use weekly become aliases or functions in ~/.bashrc (Lesson 12.3).', ['Repeat', '*alias', 'one word']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cron', 'automation'], 'amber', 8.6), '3. Small automations',
    'A one-liner in cron cleans temp files or mails a daily count; when it grows, it becomes a script.', ['Daily', '*cron', 'done']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['interviews', 'careers'], 'violet', 8.6), '4. Interviews',
    'Linux and DevOps interviews ask for exactly these: top 5 words, sum a column, find big files, count status codes.', ['Question', '*pattern', 'one line']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['data', 'analysis'], 'red', 8.6), '5. Quick data checks',
    'Analysts check a CSV with head, wc, uniq -c and an awk sum before loading it anywhere.', ['File', '*one-liners', 'trust']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Five favourites to start with. All really run on our build machine.', [
    dict(level='b', title='Top words', scenario='Any text.', setup=H, cmd="cd ~/h; sort words.txt | uniq -c | sort -rn | head -1", explain='The count pattern.'),
    dict(level='b', title='Biggest here', scenario='Disk.', setup=H, cmd="cd ~/h; du -sh * | sort -rh | head -1", explain='du | sort -rh.'),
    dict(level='i', title='Search code', scenario='Developers.', setup=H, cmd="cd ~/h; grep -rn TODO src | wc -l", explain='grep -rn.'),
    dict(level='i', title='Sum a column', scenario='Data.', setup=H, cmd="cd ~/h; awk -F, 'NR>1{s+=$3} END{print s}' staff.csv", explain='awk sum.'),
    dict(level='a', title='Compare outputs', scenario='Audits.', setup=H, cmd="cd ~/h; diff <(cut -d, -f2 staff.csv | sort -u) <(printf 'HR\\nIT\\nSales\\ndept\\n') && echo 'same departments'", explain='diff <( ).'),
], extra=build_up('adapting a one-liner', 'Riya turns one known one-liner into answers for three new questions.', H, [
    ("cd ~/h; awk '{print $1}' logs/access.log | sort | uniq -c | sort -rn | head -1", '1. Known: the top IP.'),
    ("cd ~/h; awk '{print $3}' logs/access.log | sort | uniq -c | sort -rn | head -1", '2. Change the column: the top URL.'),
    ("cd ~/h; awk '$4>=400{print $1}' logs/access.log | sort | uniq -c | sort -rn | head -1", '3. Add a condition: the IP with most errors.'),
    ("cd ~/h; awk -F, 'NR>1{print $2}' staff.csv | sort | uniq -c | sort -rn | head -1", '4. Change the file and separator: the biggest department.'),
], cumulative=False)) + which('Choosing the right group.', [
    ('Files', '1–10', 'Create, copy, rename, clean.', '-'),
    ('Search', '11–20', 'grep and friends.', '-'),
    ('Change', '21–30', 'sed, tr, awk.', '-'),
    ('Numbers', '31–40', 'Counts, sums, groups.', '-'),
    ('Running things', '41–50', 'ps, kill, nohup.', '-'),
    ('Space', '51–60', 'df, du, find -size.', '-'),
]) + keys('The six patterns.', [
    ('| sort | uniq -c | sort -rn', 'count and rank', 'any field'),
    ("awk '{t[$k]+=$v}'", 'group', 'totals'),
    ('find … -exec {} +', 'bulk', 'files'),
    ('for f in *; do …; done', 'loop', 'files'),
    ('diff <(a) <(b)', 'compare', 'outputs'),
    ('a && b || c', 'chain', 'safety'),
])
uc = uc + scriptit('oneliner-quiz.sh', 'A tiny self-test: five tasks on the sample data, each solved two different ways; the script checks that both answers agree.',
'''mkdir -p ~/h/logs ~/h/src && cd ~/h || exit 1
[ -f words.txt ] || printf 'alpha\\nbeta\\ngamma\\nbeta\\ndelta\\n' > words.txt
[ -f staff.csv ] || printf 'name,dept,salary\\nRiya,IT,72000\\nAman,HR,51000\\n' > staff.csv
[ -f logs/app.log ] || printf 'INFO a\\nERROR b\\nERROR c\\n' > logs/app.log
touch src/a.py src/b.py
check(){ local want got; want=$(bash -c "$2" 2>/dev/null); got=$(bash -c "$3" 2>/dev/null); [ "$want" = "$got" ] && echo "PASS  $1 ($got)" || echo "FAIL  $1 (want: $want, got: $got)"; }
check 'unique words'     "sort -u words.txt | wc -l"                       "sort words.txt | uniq | wc -l"
check 'sum of salaries'  "awk -F, 'NR>1{s+=\\$3} END{print s}' staff.csv"   "tail -n +2 staff.csv | cut -d, -f3 | paste -sd+ | bc"
check 'python files'     "find src -name '*.py' | wc -l"                  "ls src/*.py | wc -l"
check 'ERROR lines'      "grep -c ERROR logs/app.log"                     "awk '/ERROR/{n++} END{print n}' logs/app.log"
check 'biggest word'     "awk '{print length, \\$0}' words.txt | sort -rn | head -1 | cut -d' ' -f2" "while read -r w; do echo \\"\\${#w} \\$w\\"; done < words.txt | sort -rn | head -1 | cut -d' ' -f2"''',
'<p>Each task is solved two ways; if both agree, it passes.</p>', expect='any') + puzzle_answer('<b>1. Check the tool exists:</b> <code>command -v netstat</code> would have shown it is missing (use <code>ss</code> or <code>lsof -i</code>). <b>2. Read it part by part:</b> running <code>uniq -c</code> on its own shows repeated values split up; the fix is <code>sort | uniq -c</code>. <b>3. Run the read-only version first:</b> without <code>-delete</code>, the find would have listed every file, revealing that the order was wrong; tests come first, the action last (<code>find … -mtime +30 -delete</code>).') + qc('Which three habits make internet one-liners safe?', 'Check the tools exist, read/run it stage by stage, and run a read-only version on sample data first.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/h /tmp/a.conf*', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('the earlier lessons of <a href="../01-combining-commands-pipes-subshells-substitution/">Module 13</a>; this lesson is a reference and challenge.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
