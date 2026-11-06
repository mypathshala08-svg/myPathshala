import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='07-bulk-renaming-with-rename-and-regular-expressions', n='3.7',
    module_label='Module 3 · Working with files and directories',
    title='Bulk renaming with rename and regular expressions',
    desc='Rename many files at once with Perl rename: s/// with g and i, y/// for case, -n preview, -v, -f; regex building blocks for file names (^ $ . * + ? {n,m}, [ ], \\d \\w \\s \\b and their opposites, groups and $1, a|b); quoting traps such as $(date) in single quotes; Perl rename vs util-linux rename on RHEL; portable alternatives with bash loops and mv. Verified results, used by data, web, ML, security and operations teams.',
    og_desc='300 photos, one line: rename with regular expressions, previewed with -n, with verified results and the traps nobody tells you.',
    minutes=40, level='Beginner → Advanced',
    lead='300 photo names with spaces and capitals must become clean lowercase names. This lesson teaches rename and the regular expressions behind it, the quoting traps, the Red Hat difference, and portable bash alternatives, with every result verified.',
    chips=['Patterns by field', 'Which tool when?', 'Errors and traps', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = r"""# Test rename expressions with perl -lpe (same engine as rename), then rename with bash + mv
printf 'IMG 0001.JPEG\nIMG 0002.JPEG\nCat Photo.Jpeg\n' > names.txt
perl -lpe 'y/A-Z/a-z/; s/\s+/_/g; s/\.jpe?g$/.jpg/' names.txt
touch 'IMG 0001.JPEG' 'Cat Photo.Jpeg'
for f in *.JPEG *.Jpeg; do
  new=${f,,}; new=${new// /_}; new=${new%.jpeg}.jpg
  mv -v -- "$f" "$new"
done
"""

RUN = dict(
    heading='Preview a rename, then do it',
    intro='<p>The online runner has no <code>rename</code> package, so the script tests the expression with <code>perl -lpe</code> (the engine rename uses), then renames real files with a portable bash loop. On your Ubuntu machine you would run the same expression with <code>rename</code>.</p>',
    code=MAIN,
    anno=[
        ("perl -lpe 'y/A-Z/a-z/; s/\\s+/_/g; s/\\.jpe?g$/.jpg/' names.txt", 'The exact rename expression, tested on text.'),
        ('new=${f,,}; new=${new// /_}; new=${new%.jpeg}.jpg', 'The same three steps with bash variable tricks.'),
        ('mv -v -- "$f" "$new"', 'Rename one file per loop round.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Compare the perl preview with the real renames.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each line become? Then run.',
             code="printf 'report.txt\\nmy_txt_notes.txt\\n' | perl -lpe 's/\\.txt$/.md/'\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the dot is not escaped, so the wrong part changes. Fix it.',
             code="echo 'atxt_notes.txt' | perl -lpe 's/.txt/.md/'\n"),
        dict(label='4 · Your turn', hint='Turn <code>06-11-2026_sales.csv</code> into <code>2026-11-06_sales.csv</code> with groups.',
             code="echo '06-11-2026_sales.csv' | perl -lpe 's/^(\\d{2})-(\\d{2})-(\\d{4})/$3-$2-$1/'\n"),
        dict(label='5 · Challenge', hint='Keep only letters, digits, dots, dashes and underscores (replace the rest with _).',
             code="echo 'Invoice (Final) #3.pdf' | perl -lpe 's/[^A-Za-z0-9._-]+/_/g'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the real rename',
    intro='<p>Install rename on Ubuntu and try the commands from this lesson. Outputs are <b>typical</b>.</p>',
    items=[
        dict(title='1 · Install and check the version', cmd='sudo apt install rename; rename --version', output='/usr/bin/rename using File::Rename version 2.02, File::Rename::Options version 1.99', note='Typical on Ubuntu 24.04 (version numbers may differ).'),
        dict(title='2 · Preview, then rename', cmd="rename -n 's/\\s+/_/g' *  &&  rename -v 's/\\s+/_/g' *", output='rename(my file.txt, my_file.txt)\nmy file.txt renamed as my_file.txt', note='Typical: -n prints the plan, -v reports what was done.'),
        dict(title='3 · Rocky / RHEL / Fedora', cmd='rename -v .jpeg .jpg *.jpeg', output="`a.jpeg' -> `a.jpg'", note='Typical util-linux rename: plain text FROM TO, no regex. For Perl rename there: install prename from EPEL, or use a bash loop.'),
        dict(title='4 · Recursive renames with find', cmd="find . -name '*.JPEG' -exec rename -v 's/\\.JPEG$/.jpg/' {} +", output='./2026/a.JPEG renamed as ./2026/a.jpg', note='Typical. find selects files in every sub-folder (Lesson 13.2); careful: the expression sees the whole path.'),
        dict(title='5 · Perl on our build machine', cmd='perl -v | sed -n 2p', output=pc('perl -v | sed -n 2p'), note='Recorded: Perl is installed everywhere, which is why perl -lpe is a good test bench.'),
    ],
)

TRACE = dict(
    heading='Renaming in a loop, step by step',
    intro='<p>Step through a portable rename loop. Watch the <b>Files</b> box: one name changes per round.</p>',
    code='''touch 'Jan Report.TXT' 'Feb Report.TXT'
for f in *.TXT; do
  new=${f,,}
  new=${new// /_}
  mv -- "$f" "$new"
done
ls
''',
    notes={1: 'Setup :: Two badly named files.', 3: 'Lowercase :: ${f,,}.', 4: 'Spaces :: ${new// /_}.', 5: 'Rename :: One file changes.', 7: 'Result :: Clean names.'},
)

WORKED_INTRO = 'Three tasks from real jobs, tested with perl -lpe (the same engine as rename) so they run anywhere.'
EXAMPLES = [
    dict(level='b', tag='Web', title='Web-safe image names',
         problem='<p>Turn names like <code>Logo Final.PNG</code> into <code>logo_final.png</code>.</p>',
         inp='Logo Final.PNG, Team Photo 2026.JPG',
         approach=['Lowercase with y///.', 'Spaces with s/\\s+/_/g.'],
         code='''printf 'Logo Final.PNG\\nTeam Photo 2026.JPG\\n' | perl -lpe 'y/A-Z/a-z/; s/\\s+/_/g'
''',
         notes={1: 'Test :: The same expression you would give rename.'},
         tryit='Add <code>s/\\.jpg$/.jpeg/</code> at the end. Does order matter?'),
    dict(level='i', tag='Data engineering', title='Sortable dates in file names',
         problem='<p>Exports are named <code>sales_DD-MM-YYYY.csv</code>. Rename to <code>sales_YYYY-MM-DD.csv</code> so they sort by date.</p>',
         inp='sales_06-11-2026.csv, sales_31-10-2026.csv',
         approach=['Three groups for day, month, year.', 'Write them back as $3-$2-$1.'],
         code='''printf 'sales_06-11-2026.csv\\nsales_31-10-2026.csv\\n' | perl -lpe 's/(\\d{2})-(\\d{2})-(\\d{4})/$3-$2-$1/' | sort
''',
         notes={1: 'Groups :: \\d{2} = exactly two digits; sort proves the order is now by date.'},
         tryit='What happens to a file that has no date in its name?'),
    dict(level='a', tag='ML / data', title='Class labels from folder-style names',
         problem='<p>Images are named <code>cat (12).jpg</code>, <code>dog (3).jpg</code>. A training script expects <code>cat_0012.jpg</code> (label, underscore, 4-digit number).</p>',
         inp='cat (12).jpg, dog (3).jpg',
         approach=['Capture the label and the number.', 'Format the number with sprintf inside the replacement (the e flag).'],
         code='''printf 'cat (12).jpg\\ndog (3).jpg\\n' | perl -lpe 's/^(\\w+) \\((\\d+)\\)\\.jpg$/sprintf("%s_%04d.jpg", $1, $2)/e'
''',
         notes={1: 'e flag :: The replacement is Perl code: sprintf pads the number to 4 digits.'},
         tryit='Change %04d to %05d.'),
]

QUIZ = mix([
    dict(q='Which option previews a rename without changing anything?', options=['-v', '-n', '-f', '-p'], answer=1,
         why='-n (nono) prints rename(old, new).'),
    dict(q="What does rename 's/^/2026_/' * do?", options=['Removes 2026_', 'Adds 2026_ at the start of every name', 'Renames to 2026_', 'Nothing'], answer=1,
         why='^ is the start of the name.'),
    dict(q='Why write \\. in s/\\.txt$/.md/?', options=['Style only', 'An unescaped . matches any character', 'To hide the file', 'For Windows'], answer=1,
         why='. is a regex wildcard; \\. is a real dot.'),
    dict(q='What does the g flag do?', options=['Global: replace every match', 'Group', 'Ignore case', 'Preview'], answer=0,
         why='Without g only the first match per name is replaced.'),
    dict(q="rename 's/\\D+//g' on file123name.txt gives…", options=['123.txt', '123', 'file123name', 'name.txt'], answer=1,
         why='\\D also matches the dot and txt, so they are removed too.'),
    dict(q='Which expression makes names lowercase?', options=["'s/A-Z/a-z/'", "'y/A-Z/a-z/'", "'lc/A-Z/'", "'s/[A-Z]/[a-z]/'"], answer=1,
         why='y/// translates character ranges one for one.'),
    dict(q='$(date +%F) inside single quotes in a rename expression…', options=['inserts the date', 'is not run by bash; Perl misreads $(', 'causes a bash error', 'is ignored'], answer=1,
         why='Single quotes stop bash; use double quotes and escape Perl’s $.'),
    dict(q='On Rocky Linux, rename .jpeg .jpg *.jpeg works but s/// does not. Why?', options=['Old Perl', 'It is util-linux rename with a different syntax', 'SELinux', 'Missing -n'], answer=1,
         why='Red Hat systems ship util-linux rename: FROM TO files.'),
])

REVISION = [
    "<code>rename -n 'EXPR' files</code> preview; <code>-v</code> report; no overwrite unless <code>-f</code>.",
    '<code>s/find/replace/</code>; flags <code>g</code> all, <code>i</code> ignore case; several: <code>\'expr1; expr2\'</code>.',
    'Anchors <code>^ $</code>, real dot <code>\\.</code>; <code>* + ? {n,m}</code> repeat the previous item.',
    '<code>\\d \\w \\s</code> and opposites <code>\\D \\W \\S</code>; <code>\\b</code> boundary (<code>_</code> is a word char).',
    'Groups <code>( )</code> → <code>$1 $2</code> in the replacement; <code>a|b</code> alternatives.',
    '<code>y/A-Z/a-z/</code> lowercase; order of expressions matters.',
    'Single quotes normally; double quotes only for bash values, then escape Perl’s <code>\\$</code>.',
    'RHEL/Rocky: util-linux <code>rename FROM TO files</code>. Portable: <code>for f in …; do mv -- "$f" "${f,,}"; done</code>.',
]

FAQ = [
    ('How do you rename multiple files at once in Linux?', "With rename and a Perl expression, e.g. rename 's/\\.txt$/.md/' *.txt, or with a bash loop and mv."),
    ('What is the difference between mv and rename?', 'mv renames or moves one file at a time without patterns; rename changes many names with a regex and does not move files between folders.'),
    ('How do you preview a rename?', 'rename -n prints the planned changes without renaming anything.'),
    ('How do you replace spaces in file names?', "rename 's/\\s+/_/g' * (or a loop with ${f// /_})."),
    ('How do you convert file names to lowercase?', "rename 'y/A-Z/a-z/' * (or a loop with ${f,,})."),
    ('Why does rename behave differently on CentOS/RHEL?', 'Those systems ship util-linux rename (rename FROM TO files), not the Perl version.'),
    ('Is a glob the same as a regex?', 'No. Globs choose files (*.txt); regex describes text inside the expression (.*\\.txt$).'),
]

PRACTICE_INTRO = 'Regex tasks for file names, tested with perl -lpe (the engine rename uses). Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Change the extension', stmt='Turn .txt into .md for each name.', inp='a.txt, b.txt',
         code="printf 'a.txt\\nb.txt\\n' | perl -lpe 's/\\.txt$/.md/'\n", explain='Escaped dot, anchored at the end.'),
    dict(level='easy', title='Add a prefix', stmt='Add “old_” in front of each name.', inp='x.csv, y.csv',
         code="printf 'x.csv\\ny.csv\\n' | perl -lpe 's/^/old_/'\n", explain='^ = start.'),
    dict(level='easy', title='Lowercase', stmt='Make the names lowercase.', inp='READ ME.TXT',
         code="echo 'READ ME.TXT' | perl -lpe 'y/A-Z/a-z/'\n", explain='y/// translates letters.'),
    dict(level='medium', title='Spaces to dashes', stmt='Replace every run of spaces with one dash.', inp='my   holiday  photo.jpg',
         code="echo 'my   holiday  photo.jpg' | perl -lpe 's/\\s+/-/g'\n", explain='\\s+ and g.'),
    dict(level='medium', title='Remove a version tag', stmt='Remove “_v1”, “_v2” … before the extension.', inp='report_v2.pdf, plan_v10.docx',
         code="printf 'report_v2.pdf\\nplan_v10.docx\\n' | perl -lpe 's/_v\\d+(\\.\\w+)$/$1/'\n", explain='Group keeps the extension.'),
    dict(level='medium', title='Pad numbers', stmt='Turn page1.png … page12.png into page001.png …', inp='page1.png, page12.png',
         code="printf 'page1.png\\npage12.png\\n' | perl -lpe 's/(\\d+)/sprintf(\"%03d\",$1)/e'\n", explain='The e flag runs sprintf.'),
    dict(level='business', title='Safe upload names', stmt='Replace anything that is not a letter, digit, dot, dash or underscore with _.', inp='Q1 report (final)#2.xlsx',
         code="echo 'Q1 report (final)#2.xlsx' | perl -lpe 's/[^A-Za-z0-9._-]+/_/g'\n", explain='Allow-list with [^…].'),
    dict(level='business', title='Rename for real, portably', stmt='Without rename: lowercase all .TXT files and change spaces to _.', inp="'Jan Sales.TXT'",
         code="touch 'Jan Sales.TXT'\nfor f in *.TXT; do n=${f,,}; mv -- \"$f\" \"${n// /_}\"; done\nls\n", explain='bash parameter expansion + mv.'),
]

SCN_INTRO = 'Interview questions about renaming files and regular expressions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Rename all .txt files to .log.”',
        'A folder has 50 .txt files.',
        'do you know bulk renaming?',
        '''<ul>
          <li>Perl rename: <code>rename -n 's/\\.txt$/.log/' *.txt</code>, then without -n.</li>
          <li>Portable: <code>for f in *.txt; do mv -- "$f" "${f%.txt}.log"; done</code>.</li>
          <li>Not <code>mv *.txt *.log</code>: mv cannot do pattern renames.</li>
        </ul>''', 'typing 50 mv commands, or mv *.txt *.log.') +
    scn('Web team · deploy', 'Junior', 'Images work on Windows, 404 on the server',
        'The site links to logo.png but the file is Logo.PNG.',
        'do you know case sensitivity?',
        '''<ol>
          <li>Linux file names are case-sensitive; Windows and macOS usually are not.</li>
          <li>Normalise: <code>rename -n 'y/A-Z/a-z/' *</code>, check, run, and fix references.</li>
          <li>Add a CI check that rejects uppercase asset names.</li>
        </ol>''', 'renaming one file by hand and moving on.') +
    scn('Data platform', 'Mid-level', 'Files from 20 sources, 20 naming styles',
        'Daily files arrive as sales_06-11-2026.csv, SALES 2026.11.06.CSV, sales-20261106.csv…',
        'can you design a regex normalisation?',
        '''<ul>
          <li>Pick one target: <code>sales_YYYY-MM-DD.csv</code>, lowercase.</li>
          <li>One rule per source pattern with groups (<code>(\\d{2})-(\\d{2})-(\\d{4})</code> → <code>$3-$2-$1</code>), tested with -n and perl -lpe on samples.</li>
          <li>Log every rename; files that match no rule go to a “quarantine” folder for review.</li>
        </ul>''', 'one huge regex nobody can read.') +
    scn('Security review', 'Senior', 'Uploaded file names in shell scripts',
        'A script processes uploads with <code>for f in $(ls uploads)</code>; one upload is named <code>x; rm -rf ~</code>.',
        'do you handle untrusted names safely?',
        '''<ul>
          <li>Never parse ls; use globs and quote variables (<code>"$f"</code>), use <code>--</code>.</li>
          <li>Sanitise names on upload with an allow-list (<code>[^A-Za-z0-9._-]</code> → _), or store files under generated IDs and keep the original name in a database.</li>
          <li>Treat names as data, never as code (no eval).</li>
        </ul>''', '“users will not do that”.')
) + interview([
    ('How do you rename many files with one command?', "rename 's/old/new/' files (Perl rename), after rename -n to preview."),
    ('What do ^ and $ mean in a regex?', 'Start and end of the text (here: of the file name).'),
    ('What is the difference between \\d and \\D?', '\\d matches one digit; \\D matches any character that is not a digit.'),
    ('What does the g flag do in s///g?', 'Replaces every match instead of only the first.'),
    ('How do you reuse matched text?', 'With groups ( ) in the pattern and $1, $2 in the replacement.'),
    ('Glob vs regex?', 'Globs (*, ?, [ ]) select file names in the shell; regex is a richer pattern language used inside rename, grep, sed.'),
    ('Why might rename not work on RHEL?', 'It is the util-linux version with syntax rename FROM TO files.'),
], [
    ('RHCSA (EX200)', 'Essential tools: “Use grep and regular expressions to analyze text”; the same regex skills apply to renaming.'),
    ('LFCS', 'Essential Commands: use regular expressions and shell tools to manage files.'),
    ('CompTIA Linux+', 'Regular expressions and bulk file operations in file management and scripting objectives.'),
]) + distro('This is the lesson where distributions differ the most.', [
    ('rename package', 'Perl rename (apt install rename)', 'util-linux rename (FROM TO files); Perl version via EPEL prename', 'no rename: brew install rename (Perl)', 'WSL: as Ubuntu; Git Bash: none'),
    ('Syntax', "rename 's/a/b/' files", 'rename a b files', "rename 's/a/b/' files (brew)", '—'),
    ('Preview', '-n', '-n (newer util-linux) / -v', '-n', '—'),
    ('Portable fallback', 'bash loop + mv', 'bash loop + mv', 'zsh: zmv; bash loop', 'bash loop + mv'),
    ('${f,,} lowercase', 'bash 4+: yes', 'yes', 'bash 3.2: no (zsh: ${f:l})', 'yes'),
    ('Case-insensitive file system', 'no', 'no', 'yes: a.txt → A.txt needs a temp name', '/mnt/c: yes'),
]) + teaser('4.1', 'Riya must change one setting in a server’s config file. There is no mouse and no Notepad. Which editor is always there, and how does she save and quit?')

CHEATSHEET = cheatsheet('rename and regex', [
    ('rename', [("rename -n 'E' *", 'preview'), ("rename -v 'E' *", 'do + report'), ("rename -f 'E' *", 'overwrite (risky)'), ("'E1; E2'", 'several steps'), ('rename --version', 'Perl or util-linux?')]),
    ('Common jobs', [("s/\\.txt$/.md/", 'extension'), ('s/^/new_/', 'prefix'), ('s/\\.txt$/_bak.txt/', 'suffix'), ('s/\\s+/_/g', 'spaces → _'), ('y/A-Z/a-z/', 'lowercase')]),
    ('Regex basics', [('^ $', 'start / end'), ('. \\.', 'any char / real dot'), ('* + ? {n,m}', 'how many'), ('[abc] [^abc]', 'set / not set'), ('a|b', 'either')]),
    ('Shortcuts', [('\\d \\D', 'digit / not'), ('\\w \\W', 'word char / not'), ('\\s \\S', 'space / not'), ('\\b \\B', 'boundary / not'), ('( ) $1', 'group, reuse')]),
    ('Portable (bash + mv)', [('${f%.txt}.md', 'extension'), ('${f// /_}', 'spaces'), ('${f,,}', 'lowercase'), ('mv -- "$f" "$new"', 'safe mv'), ("perl -lpe 'E'", 'test an expression')]),
])

MINDMAP = mindmap('Bulk renaming', [
    ('rename', 'blue', ["-n preview, -v", "s/find/replace/g", 'no overwrite']),
    ('Anchors', 'green', ['^ start, $ end', '\\. real dot', '\\b word boundary']),
    ('Classes', 'violet', ['[ ] [^ ]', '\\d \\w \\s', '\\D strips the dot!']),
    ('Groups', 'amber', ['( ) remember', '$1 $2 reuse', 'reorder dates']),
    ('Quotes', 'red', ["'single' normally", '"double" for $(date)', 'escape Perl’s \\$']),
    ('Elsewhere', 'acc', ['RHEL: rename FROM TO', 'bash loop + mv', 'y/// for case']),
])

LAB = lab('clean a photo folder (portable)', 'Build the lab and rename the files so the checker passes. Use rename if you have it, or a bash loop with mv (works everywhere).',
    setup='''mkdir -p ~/lab37 && cd ~/lab37 && rm -rf photos
mkdir photos && cd photos
touch 'IMG 0001.JPEG' 'IMG 0002.JPEG' 'Team Photo.Jpeg' notes.TXT''',
    tasks=['Every <code>.JPEG</code> / <code>.Jpeg</code> file must end in <code>.jpg</code>.',
           'All names must be lowercase.',
           'No name may contain a space (use _).',
           '<code>notes.TXT</code> must become <code>notes.txt</code>.'],
    solution='''for f in *; do
  n=${f,,}; n=${n// /_}; n=${n/%.jpeg/.jpg}
  [ "$f" = "$n" ] || mv -- "$f" "$n"
done''',
    check='''cd ~/lab37/photos
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 jpg extensions"  '[ "$(ls | grep -ci "\\.jpeg$")" -eq 0 ] && [ "$(ls *.jpg 2>/dev/null | wc -l)" -eq 3 ]'
ok "2 lowercase"       '! ls | grep -q "[A-Z]"'
ok "3 no spaces"       '! ls | grep -q " "'
ok "4 notes.txt"       '[ -f notes.txt ]' ''')
