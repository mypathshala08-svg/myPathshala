import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

FX = r"""rm -rf ~/fx; mkdir -p ~/fx/photos ~/fx/logs ~/fx/site/conf ~/fx/site/pages; cd ~/fx
for n in 1 2 3; do touch "photos/IMG_000$n.JPG"; done; touch 'photos/Beach Day.JPG' 'photos/notes.txt'
for d in 40 35 10 2; do f=logs/app-$d.log; echo "log from $d days ago" > $f; touch -d "$d days ago" $f; done
head -c 300000 /dev/zero > logs/big.dump
for f in a b c; do echo "db_host=old-db01.local" > site/conf/$f.conf; done
echo "<p>contact: old-db01.local</p>" > site/pages/index.html; echo 'port=80' > site/conf/web.conf"""

HOOK = hook('Riya has three jobs before lunch: rename 2,000 camera photos from <code>IMG_0001.JPG</code> to <code>trip_0001.jpg</code>, delete log files older than 30 days on twelve servers, and replace the old database name <code>old-db01.local</code> in 400 config files. By hand, it is a day of work and a hundred chances to make a mistake. With <b>find</b> to choose the files and <b>-exec</b> or <b>xargs</b> to act on them, each job is one line. This lesson teaches the safe way: always <b>preview</b> what will happen, handle names with spaces, and only then run the real action.',
    ['select files with find (name, type, size, age) and act on them with -exec … \\; and -exec … +',
     'feed file lists into xargs safely with -print0 / -0, and use -n, -I, -P and -r',
     'do bulk renames, clean-ups and search-and-replace across many files, with a preview first',
     'know when to use -delete, -ok, -execdir and when a plain loop is clearer'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three jobs before lunch'),
    ('decide', 'Which form when?', 2, 'the quick chart'),
    ('definition', 'find, -exec and xargs', 6, 'simple meaning + 4 depths'),
    ('types', 'All the action forms', 5, 'one table'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, '\\; versus + versus xargs'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'clean up a project'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which form? (decide in 5 seconds)', [
    ('See what matches (always first)', 'find … -print   or   -ls', 'preview'),
    ('Delete what matches', 'find … -delete', 'built in'),
    ('Run a command once per file', "find … -exec cmd {} \\;", 'one at a time'),
    ('Run a command with many files at once', 'find … -exec cmd {} +', 'fast'),
    ('Names may contain spaces', 'find … -print0 | xargs -0 cmd', 'safe xargs'),
    ('Run in parallel', 'xargs -0 -P 4 -n 1 cmd', 'parallel'),
    ('Ask before each file', 'find … -ok rm {} \\;', 'interactive'),
    ('Replace text in many files', "find … -exec sed -i 's/a/b/g' {} +", 'bulk edit'),
])

cmap = concept_map(
    [('7.1', 'find', 'select files and -exec'), ('5.4', 'xargs', 'first look'), ('6.4', 'sed', 's/old/new/')],
    ['find tests: -name -type -size -mtime', '-exec {} \\; vs {} +', 'xargs -0 -n -I -P -r', 'preview, then act', 'bulk rename, clean-up, replace'],
    [('13.4', 'Admin one-liners', 'biggest files'), ('17.4', 'cron', 'scheduled clean-ups'), ('18.2', 'logrotate', 'the proper log tool'), ('13.7', '100 one-liners', 'cheat sheet')],
    'find chooses, -exec or xargs acts. Look first, act second, and let NUL characters carry the names.')

sc = (term(20, 14, 316, 156, ['$ find logs -name "*.log" -mtime +30', ('logs/app-35.log', 'out'), ('logs/app-40.log', 'out'), '$ find logs -name "*.log" -mtime +30 -delete', '$ ls logs', ('app-10.log  app-2.log  big.dump', 'acc')], title='riya@web01: ~/fx', prompt='riya@web01:~/fx$', size=6.8, step=17)
      + t(352, 36, 'Safe pattern:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['1 find … (look)', '2 check the list', '3 add the action', '-delete, -exec,', 'or | xargs'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three jobs before lunch</h2>
  <div class="story">
''' + puzzle('Riya runs <code>find photos -name "*.JPG" | xargs rm</code> and gets “rm: cannot remove \'photos/Beach\': No such file or directory”. Her colleague writes <code>find logs -delete -name "*.log"</code> and empties the whole logs folder, including big.dump. And <code>find . -name *.conf</code> works in one folder but says “paths must precede expression” in another. What went wrong each time?') + '''
    <p class="narration">Riya looks at the old logs first, then deletes exactly those.</p>
''' + scene('A terminal: find lists two log files older than 30 days, the same find with -delete removes them, and ls shows the rest are still there.', sc,
            'The same expression twice: <tspan font-weight="700" class="s-acc">first look, then act</tspan>.') + '''
K> Why run it twice?
A> Because find with an action does exactly what you asked, to every match, with no undo. The first run without an action shows the list. If the list is right, add the action to the same command.
R> And the puzzle?
A> Spaces in names, the order of find’s expression, and the shell expanding <code>*.conf</code> before find sees it. Today: -exec, xargs, and the safe habits for bulk work.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A warehouse: a picker (find) walks the shelves and puts matching boxes on a cart. A worker (-exec or xargs) then processes them: one at a time (\\;), a whole cart at once (+), or several workers in parallel (xargs -P).">'
       + label_box(14, 24, 160, 110, ['PICKER (find)', 'walks every shelf', 'takes boxes that', 'match the list'], 'blue', 9)
       + arrow(174, 79, 200, 79)
       + label_box(200, 24, 130, 110, ['-exec cmd {} \\;', 'one box', 'per trip'], 'amber', 9)
       + label_box(345, 24, 130, 110, ['-exec cmd {} +', 'xargs cmd', 'a full cart'], 'green', 9)
       + label_box(490, 24, 136, 110, ['xargs -P 4', 'four workers', 'in parallel'], 'violet', 9)
       + t(320, 166, 'Always check the cart before anyone works on it.', 10, 'acc', bold=True)
       + t(320, 188, 'Names with spaces travel safely only with -print0 / -0.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Bulk actions at four depths', [
    ('v', 'No jargon: a warehouse', '      <p>One person picks, another processes.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>find logs -name "*.log" -mtime +30</code>: look.</li>
        <li><code>find logs -name "*.log" -mtime +30 -delete</code>: delete those.</li>
        <li><code>find . -name "*.conf" -exec grep -l old {} +</code>: which configs mention old.</li>
        <li>Always quote the pattern: <code>"*.log"</code>.</li>
      </ul>'''),
    ('i', '-exec forms and xargs', '''      <ul>
        <li><code>-exec cmd {} \\;</code> runs cmd once per file; <code>{}</code> is the file name, <code>\\;</code> ends the command.</li>
        <li><code>-exec cmd {} +</code> runs cmd with as many file names as fit: far fewer processes.</li>
        <li><code>xargs</code> reads names from standard input and builds command lines; <code>find -print0 | xargs -0</code> separates names with NUL bytes, so spaces and newlines are safe.</li>
        <li><code>xargs -n 1</code> one name per command, <code>-I{}</code> put the name anywhere, <code>-P 4</code> four at a time, <code>-r</code> do nothing if there is no input.</li>
        <li>find evaluates its expression left to right: <code>-delete</code> before <code>-name</code> deletes everything (the second puzzle).</li>
      </ul>'''),
    ('a', 'Behind the screen: argument limits and NUL', '''      <ul>
        <li>The kernel limits the size of one command line (<code>getconf ARG_MAX</code>, 2 MiB here); <code>rm *</code> on 500,000 files fails with “Argument list too long”. <code>-exec +</code> and xargs split the list into chunks under the limit.</li>
        <li>NUL (byte 0) is the only character that cannot appear in a Linux file name, so it is the only fully safe separator.</li>
        <li><code>-execdir</code> runs the command inside the file’s folder with <code>./name</code>, avoiding races with renamed parent folders.</li>
        <li><code>-delete</code> implies <code>-depth</code> (children before parents) and does not follow symlinks.</li>
        <li>xargs without -0 also treats quotes and backslashes specially, another reason to use -0.</li>
        <li><code>sed -i</code> writes a new file and renames it over the old one: the inode changes and hard links break (Lesson 10.2).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>find actions, -exec and xargs</h2>
''' + def_block(
    '<code>find</code> walks a directory tree and evaluates an <b>expression</b> of tests and <b>actions</b> for each file. The action <code>-exec cmd {} ;</code> runs a command for each match, <code>-exec cmd {} +</code> runs it with many matches at once, and <code>-delete</code> removes matches. <code>xargs</code> reads items from standard input and runs a command with them as arguments, in batches, optionally in parallel; with <code>-0</code> it reads NUL-separated items produced by <code>find -print0</code>.',
    'find picks the files; -exec or xargs does the work.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Expression', 'find’s tests and actions, read left to right.'),
    ('Test', '-name, -type, -size, -mtime…'),
    ('Action', '-print, -delete, -exec, -ok…'),
    ('{}', 'Placeholder for the file name.'),
    ('\\; / +', 'End of -exec: one file / many files.'),
    ('xargs', 'Turns input lines into arguments.'),
    ('NUL separator', 'Byte 0: -print0 | xargs -0.'),
    ('ARG_MAX', 'Maximum size of one command line.'),
]) + '\n' + names('Where the names come from.', [
    ('find', 'find files', 'Unix V5, 1974.'),
    ('-exec', 'execute', 'Run a command.'),
    ('{}', 'braces', 'Filled in by find.'),
    ('xargs', 'extended arguments', 'PWB Unix, 1977.'),
    ('-print0', 'print with NUL', 'GNU find.'),
    ('-P', 'parallel', 'GNU xargs.'),
    ('-ok', 'OK to run?', 'Asks first.'),
    ('mtime', 'modification time', 'In days.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Preview', '<code>find … -print</code>'),
    ('Delete', '<code>find … -delete</code>'),
    ('Per file', '<code>-exec cmd {} \\;</code>'),
    ('Batched', '<code>-exec cmd {} +</code>'),
    ('Safe xargs', '<code>-print0 | xargs -0</code>'),
    ('Parallel', '<code>xargs -P 4</code>'),
]) + '\n' + lv + didyou('<code>find / -name core -exec rm {} \\;</code> used to be a classic nightly cron job to remove crash dump files. On a system with a program called <code>core</code> it deleted that too: one reason modern advice adds <code>-type f</code> and a more exact test to every bulk delete.') + '''
EXAM> “What is the difference between -exec {} \\; and -exec {} +?” → \\; runs the command once per file; + passes many files to one command, like xargs, which is much faster.
''' + qc('Why put the pattern in quotes: <code>find . -name "*.conf"</code>?', 'Without quotes the shell expands *.conf in the current folder first; find then receives file names, or several of them, instead of the pattern.') + mistake('find photos -name "*.JPG" | xargs rm',
    'find photos -name "*.JPG" -print0 | xargs -0 rm   ·   or   find photos -name "*.JPG" -delete',
    'xargs splits on spaces: “Beach Day.JPG” became “Beach” and “Day.JPG” (real run).') + mistake('find logs -delete -name "*.log"',
    'find logs -name "*.log" -delete   (tests first, action last)',
    'The expression is read left to right: -delete ran for every file before -name was checked.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Every way to act on found files</h2>
''' + table(['Form', 'Runs', 'Example', 'Use'], [
    ['<code>-print</code> / <code>-ls</code>', 'nothing: lists', '<code>find . -name "*.tmp" -ls</code>', 'preview'],
    ['<code>-delete</code>', 'built-in delete', '<code>find /tmp -mtime +7 -delete</code>', 'clean-ups'],
    ['<code>-exec cmd {} \\;</code>', 'once per file', '<code>-exec gzip {} \\;</code>', 'commands that take one file'],
    ['<code>-exec cmd {} +</code>', 'once per batch', '<code>-exec grep -l x {} +</code>', 'speed'],
    ['<code>-execdir cmd {} \\;</code>', 'in the file’s folder', '<code>-execdir mv {} new_{} \\;</code>', 'renames'],
    ['<code>-ok cmd {} \\;</code>', 'asks y/n each time', '<code>-ok rm {} \\;</code>', 'careful deletes'],
    ['<code>| xargs cmd</code>', 'batches', '<code>… | xargs wc -l</code>', 'simple names only'],
    ['<code>-print0 | xargs -0 cmd</code>', 'batches, safe names', '<code>… | xargs -0 rm</code>', 'any names'],
    ['<code>xargs -I{} cmd {} x</code>', 'one per item, name anywhere', '<code>xargs -I{} cp {} /bk/</code>', 'name in the middle'],
    ['<code>xargs -P 4 -n 1</code>', '4 in parallel', '<code>xargs -P4 -n1 gzip</code>', 'CPU-heavy work'],
    ['<code>while read -r -d \'\'</code>', 'your own loop', 'see examples', 'complex per-file logic'],
], minw=560) + table(['Test', 'Matches', 'Example'], [
    ['<code>-name / -iname</code>', 'name pattern (case-insensitive)', '<code>-iname "*.jpg"</code>'],
    ['<code>-type f / d / l</code>', 'file / folder / link', '<code>-type f</code>'],
    ['<code>-size +100M</code>', 'bigger than 100 MiB', '<code>-size -1k</code> smaller'],
    ['<code>-mtime +30</code>', 'changed more than 30 days ago', '<code>-mmin -60</code> last hour'],
    ['<code>-newer f</code>', 'changed after file f', 'since a deploy'],
    ['<code>-empty</code>', 'empty files/folders', 'clean-up'],
    ['<code>-user / -perm</code>', 'owner / permissions', '<code>-perm -o+w</code>'],
    ['<code>-maxdepth 1</code>', 'do not go deeper', 'one folder only'],
    ['<code>! -name</code>, <code>-o</code>, <code>\\( \\)</code>', 'not / or / grouping', '<code>\\( -name a -o -name b \\)</code>'],
], minw=480) + qc('Which form starts fewer processes for 1,000 files: <code>{} \\;</code> or <code>{} +</code>?', '{} + (a handful of commands instead of 1,000).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Clean-ups, -exec, xargs and bulk edits, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (GNU findutils 4.9) as riya, in <code>~/fx</code>: <code>photos/</code> (IMG_0001–0003.JPG, “Beach Day.JPG”, notes.txt), <code>logs/</code> (app logs dated 40, 35, 10 and 2 days ago, a 300 KB big.dump) and <code>site/</code> (four .conf files and a page, three mentioning <code>old-db01.local</code>).</p>
''' + cmdcard_u(['old logs, temp files, empty folders, caches'],
               ['-delete before the tests', 'running as root on / without a preview'])(
    'clean', 'find PATH tests -print · then -delete', 'clean-ups',
    'Write the tests, run with <code>-print</code> (the default) and check the list. Then add <code>-delete</code> at the <b>end</b>. Add <code>-type f</code> so folders are not touched, and a <code>-maxdepth</code> if you do not want to go deep.',
    'find DIR -type f -name "*.log" -mtime +30 [-delete]', 'danger',
    [('-mtime +30', 'older than 30 days', 'logs'),
     ('-size +100M', 'big files', 'disk full'),
     ('-empty -type d', 'empty folders', 'tidy'),
     ('-name "*.tmp"', 'temp files', 'caches'),
     ('-maxdepth 1', 'this folder only', 'limit'),
     ('-delete', 'remove (last!)', 'action'),
     ('-print | wc -l', 'count first', 'preview')],
    dict(setup=FX, cmd="cd ~/fx\nfind logs -type f -name '*.log' -mtime +30 | sort\nfind logs -type f -name '*.log' -mtime +30 -delete\nls logs\nmkdir -p tmp/a/b; find tmp -type d -empty -delete; ls -d tmp 2>&1", expect='any', note='Preview, delete, check. -delete also removed the nested empty folders (children first).'),
    [('sys', [
        dict(situation='The puzzle: action before the test.', setup=FX, cmd="cd ~/fx; cp -r logs logs_copy\nfind logs_copy -delete -name '*.log'; ls logs_copy 2>&1", expect='any', why='Everything, including big.dump and the folder itself, was deleted: -delete was evaluated first for every file.')]),
     ('devops', [
        dict(situation='How much space would a clean-up free?', setup=FX, cmd="cd ~/fx; find logs -type f -size +100k -print0 | du -ch --files0-from=- | tail -1", why='Measure before deleting.')]),
    ],
    anat=anatomy([('find logs', 'cmd', 'where'), ('-type f -name "*.log" -mtime +30', 'opt', 'tests (all must match)'), ('-delete', 'arg', 'action, last')], 'Tests are joined by an implicit AND and read left to right.')
) + cmdcard_u(['compress, checksum, change permissions, grep many files'],
               ['commands that need special per-file logic (use a loop)'])(
    'exec', "-exec cmd {} \\; · -exec cmd {} + · -execdir · -ok", '-exec',
    'Everything after <code>-exec</code> up to <code>\\;</code> or <code>+</code> is the command; <code>{}</code> is replaced by the path. With <code>\\;</code> one command runs per file; with <code>+</code> the names are collected and passed together (the <code>{}</code> must be last). <code>-ok</code> asks before each one.',
    "find … -exec gzip {} \\;   ·   find … -exec grep -l x {} +", 'change',
    [('-exec cmd {} \\;', 'per file', 'one-file commands'),
     ('-exec cmd {} +', 'batched', 'speed'),
     ('-exec sh -c \'…\' _ {} \\;', 'a small script per file', 'complex'),
     ('-execdir', 'run in the file’s folder', 'renames'),
     ('-ok', 'ask y/n', 'careful'),
     ('-exec … \\; -print', 'print only if cmd succeeded', 'filters')],
    dict(setup=FX, cmd="cd ~/fx\nfind site -name '*.conf' -exec grep -l old-db01 {} +\nfind site -name '*.conf' -exec echo 'one call:' {} \\;\nfind site -name '*.conf' -exec echo 'one call:' {} +", note='{} + gave one echo with all four names; {} \\; one echo per file.'),
    [('sec', [
        dict(situation='Fix permissions in bulk.', setup=FX, cmd="cd ~/fx; chmod 666 site/conf/*.conf\nfind site -type f -perm -o+w | wc -l\nfind site -type f -perm -o+w -exec chmod o-w {} +\nfind site -type f -perm -o+w | wc -l", why='World-writable files found and fixed in one line.')]),
     ('dev', [
        dict(situation='A small script per file with sh -c.', setup=FX, cmd="cd ~/fx; find site -name '*.conf' -exec sh -c 'echo \"$(basename \"$1\"): $(wc -c < \"$1\") bytes\"' _ {} \\;", why='sh -c gets the name as $1 (the _ is $0); quoting stays safe.')]),
    ]
) + cmdcard_u(['any list of names: find, grep -l, a file', 'parallel work'],
               ['xargs without -0 on arbitrary names', 'commands that read stdin themselves'])(
    'xargs', 'xargs [-0] [-n N] [-I{}] [-P N] [-r] cmd', 'xargs',
    'xargs reads items from standard input and appends them to the command. <code>-0</code> reads NUL-separated items (from <code>-print0</code>, <code>grep -lZ</code>, <code>sort -z</code>). <code>-n 1</code> one item per command; <code>-I{}</code> one item per command, placed where {} is; <code>-P N</code> runs N commands at once; <code>-r</code> runs nothing on empty input; <code>-t</code> prints each command before running it.',
    'find … -print0 | xargs -0 cmd   ·   … | xargs -0 -P4 -n1 cmd', 'change',
    [('xargs -0', 'NUL-separated input', 'always with find'),
     ('-n 1', 'one per command', 'simple tools'),
     ('-I{}', 'name anywhere', 'cp {} dest'),
     ('-P 4', 'parallel', 'speed'),
     ('-r', 'nothing if empty', 'safety'),
     ('-t', 'print each command', 'debug'),
     ('-p', 'ask first', 'careful')],
    dict(setup=FX, cmd="cd ~/fx\nfind photos -name '*.JPG' | xargs ls 2>&1 | head -3\nfind photos -name '*.JPG' -print0 | xargs -0 ls | sort\nprintf '%s\\n' a b c | xargs -t -n 1 echo item 2>&1", expect='any', note='Without -0, “Beach Day.JPG” broke into two names (the puzzle). -t shows each command xargs ran.'),
    [('data', [
        dict(situation='Parallel compression.', setup=FX, cmd="cd ~/fx; for i in 1 2 3 4; do head -c 200000 /dev/urandom > logs/part$i.dat; done\ns=$(date +%s%N); find logs -name 'part*.dat' -print0 | xargs -0 -P 4 -n 1 gzip; e=$(date +%s%N)\nls logs/*.gz | wc -l; echo \"4 files compressed by up to 4 parallel gzips\"", why='-P 4 runs four gzip processes at the same time.')]),
     ('sys', [
        dict(situation='-r: nothing to do, do nothing.', setup=FX, cmd="cd ~/fx/site; find . -name 'no-such-*' -print0 | xargs -0 -r ls; echo \"with -r: status $?, nothing listed\"\nfind . -name 'no-such-*' -print0 | xargs -0 ls", why='Without -r, ls ran with no arguments and listed the current folder (conf pages).')]),
    ]
) + cmdcard_u(['renaming many files', 'search and replace across a project'],
               ['bulk edits without a backup or git', 'sed -i on binary files'])(
    'bulk', 'loops with ${f%.*} · sed -i · grep -rl | xargs', 'bulk rename and replace',
    'For renames, a loop over <code>find -print0</code> with parameter expansion (Lesson 12.14) is the clearest; print the mv commands first. For text replacement, find the files that contain the old text (<code>grep -rlZ</code>), preview the lines, then <code>sed -i</code> them. Keep a backup (<code>sed -i.bak</code>) or work in git.',
    "grep -rlZ old DIR | xargs -0 sed -i 's/old/new/g'", 'danger',
    [('grep -rl old .', 'which files', 'preview'),
     ('grep -rn old .', 'which lines', 'preview'),
     ("sed -i.bak 's/a/b/g'", 'edit with backup', 'safe edit'),
     ('grep -rlZ … | xargs -0 sed -i', 'only files that match', 'efficient'),
     ('echo mv "$f" "$new"', 'preview renames', 'always first'),
     ('mv -n', 'never overwrite', 'renames')],
    dict(setup=FX, cmd="cd ~/fx\ngrep -rn 'old-db01.local' site\ngrep -rlZ 'old-db01.local' site | xargs -0 sed -i.bak 's/old-db01\\.local/db01.prod/g'\ngrep -rc 'db01.prod' site | grep -v ':0' | sort\nls site/conf/*.bak | wc -l", note='Preview the lines, replace only in matching files (with .bak backups), then verify.'),
    [('design', [
        dict(situation='Rename photos: preview, then run.', setup=FX, cmd="cd ~/fx/photos\nn=0; find . -maxdepth 1 -iname '*.jpg' -print0 | sort -z | while IFS= read -r -d '' f; do n=$((n+1)); printf 'mv -n %q trip_%04d.jpg\\n' \"${f#./}\" $n; done\nn=0; find . -maxdepth 1 -iname '*.jpg' -print0 | sort -z | while IFS= read -r -d '' f; do n=$((n+1)); mv -n -- \"$f\" \"$(printf 'trip_%04d.jpg' $n)\"; done; ls", why='The first loop only prints (with %q so spaces are visible); the second renames. read -d \"\" reads NUL-separated names.')]),
    ]
) + undo('Bulk actions multiply mistakes; previews and backups are the undo.', [
    ('Deleted the wrong files:', 'restore from backup or snapshot; there is no undelete on ext4.'),
    ('sed -i changed too much:', 'restore the .bak files: <code>for f in *.bak; do mv "$f" "${f%.bak}"; done</code>, or git checkout.'),
    ('Renames collided:', 'use <code>mv -n</code>; keep the printed preview as a map back.'),
    ('Habit:', 'find … (look) → add <code>echo</code> before the action → remove echo.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(setup=FX, cmd="cd ~/fx/site/conf; find . -name *.conf", meaning='The shell expanded *.conf to several names before find ran.', fix='Quote it: -name "*.conf".'),
    dict(setup=FX, cmd="cd ~/fx; find . -name '*.conf' -exec ls {}", meaning='-exec needs \\; or + at the end.', fix="-exec ls {} \\;"),
    dict(setup=FX, cmd="cd ~/fx; find . -name '*.conf' -exec echo {} x +", meaning='With +, {} must be the last argument.', fix='Use \\; or xargs -I{}.'),
    dict(setup=FX, cmd="cd ~/fx/photos; find . -name '*.JPG' | xargs ls", meaning='xargs split “Beach Day.JPG” at the space.', fix='-print0 | xargs -0.'),
    dict(cmd="find /root -name x", meaning='No permission to read a folder.', fix='2>/dev/null, or sudo if you must.'),
]) + qc('Which find option puts NUL bytes between names for xargs -0?', '-print0.') + '''
'''
cards = cards + '</section>\n'

FILES = ['a.conf', 'b.conf', 'c.conf']
def calls(k):
    o = ''
    for i, f in enumerate(FILES):
        o += label_box(10, 14 + i * 34, 90, 28, [f], 'blue', 8.4)
    if k == 0:
        o += ''.join(label_box(140, 14 + i * 34, 210, 28, [f'grep old {f}'], 'amber', 8) + arrow(100, 28 + i * 34, 140, 28 + i * 34) for i, f in enumerate(FILES))
        o += t(180, 140, '\\; → 3 processes', 9.6, 'amber', bold=True)
    elif k == 1:
        o += label_box(140, 40, 210, 40, ['grep old a.conf b.conf c.conf'], 'green', 8) + ''.join(arrow(100, 28 + i * 34, 140, 60) for i in range(3))
        o += t(180, 140, '+ → 1 process', 9.6, 'green', bold=True)
    else:
        o += label_box(140, 14, 100, 28, ['gzip a'], 'violet', 8) + label_box(250, 14, 100, 28, ['gzip b'], 'violet', 8) + label_box(140, 48, 100, 28, ['gzip c'], 'violet', 8)
        o += t(180, 140, 'xargs -P 2 -n 1 → 2 at a time', 9.6, 'violet', bold=True)
    return o
see_cmds = [["$ find . -name '*.conf' \\", "   -exec grep -l old {} \\;"], ["$ find . -name '*.conf' \\", "   -exec grep -l old {} +"], ["$ find . -print0 \\", "   | xargs -0 -P2 -n1 gzip"]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/fx', prompt='$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['One per file.', 'One batch.', 'Parallel.'])]
behind = [calls(k) for k in range(3)]
two = anim_two('How many commands run?', 'Behind the screen: processes started',
               'Three terminals: -exec with \\;, -exec with +, and xargs -P 2.',
               'Three files: with \\; three grep processes, with + one grep with all names, with xargs -P 2 gzip runs two at a time.', see, behind,
               ['\\;', '+', '-P'],
               ['per file', 'batch', 'parallel'])

def split(k):
    o = t(180, 20, 'find prints: photos/Beach Day.JPG', 8.6, 'ink2')
    if k == 0:
        o += label_box(40, 40, 280, 34, ['xargs (spaces split)'], 'red', 9)
        o += label_box(40, 90, 130, 30, ['photos/Beach'], 'red', 8.4) + label_box(190, 90, 130, 30, ['Day.JPG'], 'red', 8.4)
        o += t(180, 150, 'two wrong names → “No such file”', 9.4, 'red', bold=True)
    else:
        o += label_box(40, 40, 280, 34, ['-print0 | xargs -0 (NUL)'], 'green', 9)
        o += label_box(80, 90, 200, 30, ['photos/Beach Day.JPG'], 'green', 8.4)
        o += t(180, 150, 'one correct name', 9.4, 'green', bold=True)
    return o
s1 = anim_one('Animated example', 'Why -print0 and -0',
              'The same name, split two ways.',
              'find … -print0 | xargs -0', 'A file name with a space: plain xargs splits it into two wrong names; NUL separation keeps it whole.', [split(0), split(1)],
              ['spaces', 'NUL'], hid='scenario-nul')

dx = dissect('Layer by layer: what find and xargs do',
    'Each layer has a real command and output from our build machine.', [
    dict(key='order', name='Expression order', sub='left to right', why='Actions depend on tests.', how='Short-circuit AND.', impl='Like &&.', used='-delete last.',
         setup=FX, cmd="cd ~/fx; find site -name '*.html' -print -o -name 'web.conf' -print | sort"),
    dict(key='max', name='ARG_MAX', sub='command-line limit', why='Huge lists.', how='Kernel limit.', impl='getconf.', used='xargs batches.',
         cmd="echo \"ARG_MAX: $(getconf ARG_MAX) bytes\"; seq 1 200000 | xargs echo | wc -l | sed 's/^/xargs split 200000 numbers into /; s/$/ command(s)/'"),
    dict(key='nul', name='NUL bytes', sub='-print0', why='Any name.', how='Byte 0 between names.', impl='od shows \\0.', used='Safety.',
         setup=FX, cmd="cd ~/fx/photos; find . -name 'B*' -print0 | od -c | head -2"),
    dict(key='inode', name='sed -i', sub='new file', why='Breaks hard links.', how='Write temp, rename.', impl='Inode changes.', used='Bulk edits.',
         setup=FX, cmd="cd ~/fx/site/conf; a=$(stat -c %i web.conf); sed -i 's/80/8080/' web.conf; b=$(stat -c %i web.conf); [ \"$a\" != \"$b\" ] && echo \"inode changed after sed -i ($(cat web.conf))\""),
], hint='From the expression to the bytes. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How many commands run, and why NUL</h2>
''' + two + s1 + dx + qc('Why can NUL separate any two file names?', 'Byte 0 is the only character that can never appear in a Linux file name.') + '''
</section>
'''

VAR = variations('Twenty more find/xargs one-liners. All were really run on our build machine on the sample tree.', [
    ('Selecting', [
        dict(title='Case-insensitive extension', setup=FX, cmd="find ~/fx/photos -iname '*.jpg' | wc -l", why='-iname matches .JPG and .jpg.'),
        dict(title='Files changed in the last hour', setup=FX, cmd="find ~/fx -type f -mmin -60 | wc -l", why='-mmin in minutes.'),
        dict(title='Bigger than 100 KB', setup=FX, cmd="find ~/fx -type f -size +100k -exec ls -lh {} + | awk '{print $5, $NF}' | sed 's|/home/riya|~|'", why='-size with k, M, G.'),
        dict(title='Two patterns at once', setup=FX, cmd="find ~/fx \\( -name '*.html' -o -name 'web.conf' \\) | sed 's|/home/riya|~|' | sort", why='\\( … -o … \\) groups an OR.'),
        dict(title='Everything except .conf', setup=FX, cmd="find ~/fx/site -type f ! -name '*.conf' | sed 's|/home/riya|~|'", why='! negates a test.'),
        dict(title='Newer than a reference file', setup=FX, cmd="cd ~/fx; touch -d '5 days ago' ref; find logs -newer ref -name '*.log'", why='Since a deploy or a backup.'),
        dict(title='Only this folder', setup=FX, cmd="find ~/fx -maxdepth 1 -type d | sed 's|/home/riya|~|' | sort", why='-maxdepth 1 stops recursion.'),
    ]),
    ('Acting', [
        dict(title='Count lines in every .conf', setup=FX, cmd="cd ~/fx; find site -name '*.conf' -exec wc -l {} + | tail -1", why='One wc with all files gives a total.'),
        dict(title='Copy matches into one folder', setup=FX, cmd="cd ~/fx; mkdir -p bk; find site -name '*.conf' -print0 | xargs -0 -I{} cp {} bk/; ls bk", why='-I{} puts the name before the destination.'),
        dict(title='cp -t avoids -I', setup=FX, cmd="cd ~/fx; mkdir -p bk2; find site -name '*.conf' -print0 | xargs -0 cp -t bk2/; ls bk2 | wc -l", why='cp -t DEST takes the files last: batched.'),
        dict(title='Checksums of all photos', setup=FX, cmd="cd ~/fx; find photos -type f -print0 | sort -z | xargs -0 sha256sum | cut -c1-12,65- | head -3", why='Sorted for a stable list; identical hashes reveal identical files (here all are empty). Lesson 19.4.'),
        dict(title='Compress old logs instead of deleting', setup=FX, cmd="cd ~/fx; find logs -name '*.log' -mtime +7 -exec gzip {} +; ls logs", why='gzip old logs, keep recent ones.'),
        dict(title='Ask before each delete', setup=FX, cmd="cd ~/fx; yes n | find photos -name '*.txt' -ok rm {} \\; 2>&1; ls photos/notes.txt", why='-ok asked; we answered n (yes n), so nothing was removed.'),
        dict(title='Print and run with -t', setup=FX, cmd="cd ~/fx; find site/conf -name 'a*' -print0 | xargs -0 -t wc -c 2>&1", why='-t echoes the exact command line.'),
    ]),
    ('Bulk edits and renames', [
        dict(title='Change an extension for many files', setup=FX, cmd="cd ~/fx/photos; for f in *.JPG; do mv -n -- \"$f\" \"${f%.JPG}.jpg\"; done; ls", why='A loop with ${f%.JPG} (Lesson 12.14).'),
        dict(title='Spaces to underscores', setup=FX, cmd="cd ~/fx/photos; find . -maxdepth 1 -name '* *' -print0 | while IFS= read -r -d '' f; do mv -n -- \"$f\" \"${f// /_}\"; done; echo \"names with spaces left: $(ls | grep -c ' ')\"; ls | head -2", why='The loop renamed every name that had a space.'),
        dict(title='Lower-case all names', setup=FX, cmd="cd ~/fx/photos; for f in *; do l=${f,,}; [ \"$f\" = \"$l\" ] || mv -n -- \"$f\" \"$l\"; done; ls", why='${f,,} lower-cases.'),
        dict(title='Preview a replacement with diff', setup=FX, cmd="cd ~/fx; diff <(cat site/pages/index.html) <(sed 's/old-db01\\.local/db01.prod/' site/pages/index.html)", expect='any', why='See the change before sed -i.'),
        dict(title='Undo with the .bak files', setup=FX, cmd="cd ~/fx; find site -name '*.conf' -exec sed -i.bak 's/old/new/' {} +; find site -name '*.bak' -print0 | while IFS= read -r -d '' b; do mv -- \"$b\" \"${b%.bak}\"; done; grep -c old site/conf/a.conf", why='Restoring the backups put the old text back.'),
        dict(title='Add a header to many files', setup=FX, cmd="cd ~/fx; find site -name '*.conf' -exec sed -i '1i # managed by ops' {} +; head -1 site/conf/b.conf", why='sed 1i inserts a first line.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Bulk actions at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['-mtime', 'disk'], 'blue', 8.6), '1. Disk-full clean-ups',
              'find /var/app/tmp -type f -mtime +7 -delete in a nightly cron job keeps temp folders small.', ['Disk 95%', '*find -delete', 'space back']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['sed -i', 'migrations'], 'green', 8.6), '2. Server or domain migrations',
    'Replace an old host name in hundreds of configs: grep -rlZ old | xargs -0 sed -i.bak, then test, then remove the .bak files.', ['Old name', '*grep | sed', 'new name']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-perm', 'security'], 'red', 8.6), '3. Security audits',
    'find / -xdev -perm -4000 lists setuid programs; find -perm -o+w finds world-writable files to fix.', ['Audit', '*find -perm', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-P 8', 'media'], 'amber', 8.6), '4. Media processing',
    'Convert thousands of images or videos with xargs -P to use every core.', ['Files', '*xargs -P', 'converted']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['sha256', 'integrity'], 'violet', 8.6), '5. Integrity checks',
    'find … -print0 | xargs -0 sha256sum > manifest; later sha256sum -c manifest detects changes.', ['Files', '*sha256sum', 'manifest']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Count matching files', scenario='How many?', setup=FX, cmd="find ~/fx -name '*.conf' | wc -l", explain='wc -l.'),
    dict(level='b', title='Delete empty files', scenario='Tidy.', setup=FX, cmd="cd ~/fx; touch e1 e2; find . -maxdepth 1 -type f -empty -delete; ls e* 2>&1 | head -1", expect='any', explain='-empty.'),
    dict(level='i', title='Which files mention X?', scenario='Before a change.', setup=FX, cmd="grep -rl old-db01 ~/fx/site | sed 's|/home/riya|~|' | sort", explain='grep -rl.'),
    dict(level='i', title='Biggest 2 files', scenario='Disk.', setup=FX, cmd="find ~/fx -type f -printf '%s %p\\n' | sort -rn | head -2 | sed 's|/home/riya|~|'", explain='-printf %s = size.'),
    dict(level='a', title='Safe bulk replace', scenario='Migration.', setup=FX, cmd="cd ~/fx; grep -rlZ old-db01 site | xargs -0 -r sed -i 's/old-db01\\.local/db01.prod/g'; echo \"files still mentioning it: $(grep -rl old-db01 site | wc -l)\"", explain='0 files still mention it.'),
], extra=build_up('the old-logs clean-up', 'Riya builds the nightly clean-up safely, one step at a time.', FX, [
    ("cd ~/fx; find logs -type f", '1. What is there?'),
    ("cd ~/fx; find logs -type f -name '*.log' -mtime +30", '2. Narrow it down: only old .log files.'),
    ("cd ~/fx; find logs -type f -name '*.log' -mtime +30 -exec ls -l --time-style=+%F {} + | awk '{print $6, $7}'", '3. Check the dates.'),
    ("cd ~/fx; find logs -type f -name '*.log' -mtime +30 -print -delete | sed 's/^/deleted: /'; ls logs", '4. Delete and log what was deleted.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Delete matches', 'find -delete', 'Built in, safe with spaces.', 'xargs rm without -0.'),
    ('Same command on each file', '-exec {} +', 'Fast.', '{} \\; for 10,000 files.'),
    ('Names from another command', 'xargs -0', 'Batches.', 'for f in $(…).'),
    ('Per-file logic', 'while read -r -d ""', 'Readable.', 'A huge -exec sh -c.'),
    ('CPU-heavy per file', 'xargs -P N', 'Uses all cores.', 'One at a time.'),
    ('Text replace', 'grep -rlZ | xargs -0 sed -i.bak', 'Only matching files, backup.', 'sed -i on everything.'),
]) + keys('Handy forms.', [
    ('find … -print', 'preview', 'always first'),
    ('… -delete', 'remove', 'last in the expression'),
    ('-exec cmd {} +', 'batched', 'speed'),
    ('-print0 | xargs -0', 'safe names', 'any name'),
    ('xargs -P4 -n1', 'parallel', 'heavy work'),
    ("sed -i.bak 's/a/b/g'", 'edit with backup', 'replace'),
]) + scriptit('cleanup.sh', 'Clean a folder safely: show what would be deleted (old .log and .tmp files, empty folders) with the space it would free, and delete only when called with --yes.',
'''dir=${1:-$HOME/fx}; days=${DAYS:-30}; go=${2:-}
mapfile -d '' files < <(find "$dir" -type f \\( -name '*.log' -o -name '*.tmp' \\) -mtime +"$days" -print0)
echo "${#files[@]} file(s) older than $days days in ${dir/#$HOME/~}:"
for f in "${files[@]}"; do printf '  %s\\n' "${f/#$HOME/~}"; done
[ ${#files[@]} -gt 0 ] && echo "space: $(du -ch "${files[@]}" | tail -1 | cut -f1)"
if [ "$go" = --yes ]; then
  [ ${#files[@]} -gt 0 ] && rm -f -- "${files[@]}"
  find "$dir" -mindepth 1 -type d -empty -delete
  echo "deleted."
else
  echo "dry run: add --yes to delete"
fi''',
'<p>Run without --yes, so it only shows what it would do.</p>', expect='any') + puzzle_answer('<b>1.</b> xargs splits its input at spaces, so “photos/Beach Day.JPG” became two wrong names. Use <code>find … -print0 | xargs -0 rm</code>, or simply <code>find … -delete</code>. <b>2.</b> find reads its expression left to right; <code>-delete</code> came before <code>-name</code>, so it ran for every file (and returned true) before the name was ever checked. Tests first, action last. <b>3.</b> Unquoted, <code>*.conf</code> is expanded by the shell: in a folder with one .conf file find got that one name; with several, find got extra words and complained “paths must precede expression”. Quote patterns: <code>-name "*.conf"</code>.') + qc('Where does -delete belong in a find command?', 'At the end, after all the tests.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/fx', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../07-finding-files/">Module 7</a> (find) and <a href="../01-combining-commands-pipes-subshells-substitution/">Lesson 13.1</a> (combining commands).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
