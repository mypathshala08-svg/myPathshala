import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='14-string-manipulation-and-printf', n='12.14',
    module_label='Module 12 · The shell environment and shell programming',
    title='Bash string manipulation and printf: length, substrings, # ## % %%, replace, case',
    desc='Bash string manipulation with parameter expansion: ${#s}, ${s:off:len}, negative offsets, # ## % %% prefix/suffix removal for extensions, paths, emails and versions, ${s/a/b} ${s//a/b} /# /%, case ^ ^^ , ,, ~~, defaults :- := :? :+; printf %s %d %f %x %o %q %b %(fmt)T, widths, alignment, padding and -v; real outputs, animations and 35+ examples.',
    og_desc='Bash string operations and printf explained with real runs: substrings, # % cuts, replacements, case and formatted tables.',
    minutes=40, level='Beginner → Advanced',
    lead='Cut, trim, replace and change the case of text inside bash, without sed or awk, then print it in exact columns with printf. The # / % trick, every form in one table, and the traps.',
    chips=['# ## % %% animated', 'printf tables', 'Photo renamer build-up', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Strings inside bash
f="report.final.v2.pdf"
echo "length:  ${#f}"
echo "name:    ${f%.*}"
echo "ext:     ${f##*.}"
e="Riya.Sharma@Example.com"
echo "user:    ${e%@*}"
echo "domain:  ${e#*@}"
echo "lower:   ${e,,}"
printf '%-8s|%6.2f|%05d\\n' price 9.5 42
"""

RUN = dict(
    heading='Cut, replace and print',
    intro='<p>Take a file name and an email apart, then print a formatted line.</p>',
    code=MAIN,
    anno=[('${f%.*}', 'Shortest suffix from the last dot.'), ("printf '%-8s|%6.2f|%05d\\n'", 'Left 8, 6 wide with 2 decimals, 5 digits zero-padded.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Change f to archive.tar.gz.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the four cuts print?',
             code="p=/var/log/nginx/access.log\necho ${p#*/}\necho ${p##*/}\necho ${p%/*}\necho ${p%%/*}\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> should print the last 3 characters. Add one space.',
             code="s=abcdef\necho ${s:-3}\n"),
        dict(label='4 · Your turn', hint='Replace every space with an underscore and make it lower case.',
             code="t='My Holiday Photo.JPG'\nt=${t// /_}\necho \"${t,,}\"\n"),
        dict(label='5 · Challenge', hint='Print a two-column table of these items with printf.',
             code="printf '%-10s %8s\\n' ITEM PRICE\nprintf '%-10s %8.2f\\n' pen 10 book 245.5 bag 999\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: locale and bash version',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Your locale', cmd='locale | head -2', output=pc('locale | head -2'), note='Recorded. UTF-8 counts characters, not bytes.'),
        dict(title='2 · Case operators on old bash', cmd="/bin/bash -c 's=hi; echo ${s^^}'", output='/bin/bash: ${s^^}: bad substitution', note='Typical on macOS bash 3.2. Use tr a-z A-Z.'),
        dict(title='3 · printf as a program', cmd="/usr/bin/printf '%s\\n' hello", output=pc("/usr/bin/printf '%s\\n' hello"), note='Recorded. A separate printf program also exists; the built-in is used in bash.'),
        dict(title='4 · Is printf built in?', cmd='type -a printf', output=pc('type -a printf'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Taking a path apart, line by line',
    intro='<p>Step through: each line removes a different part.</p>',
    code='''p='/home/riya/photos/Trip 2026.JPEG'
name=${p##*/}
dir=${p%/*}
stem=${name%.*}
ext=${name##*.}
clean=${stem// /_}
printf '%s | %s | %s.%s\\n' "$dir" "$name" "${clean,,}" "${ext,,}"
''',
    notes={1: 'Quotes: the path has a space.', 2: 'File name.', 3: 'Folder.', 4: 'Without extension.', 5: 'Extension.', 6: 'Spaces → _.'},
)

WORKED_INTRO = 'Three string tasks from real jobs: a username generator, a masked log and a fixed-width export.'
EXAMPLES = [
    dict(level='b', tag='HR', title='Usernames from full names',
         problem='<p>Make a login from a full name: first letter of the first name plus the last name, lower case.</p>',
         inp='names', approach=['%% * and ##* .', '${x:0:1}, ,,.'],
         code='''for n in 'Riya Sharma' 'Aman Kumar Verma' 'Zoya Khan'; do
  first=${n%% *}; last=${n##* }
  u="${first:0:1}${last}"
  echo "$n -> ${u,,}"
done
''', notes={2: 'First and last words.', 3: 'One letter + last name.'}, tryit='Add a number if the username is longer than 8 characters.'),
    dict(level='i', tag='Security', title='Mask card numbers',
         problem='<p>Show only the last 4 digits of card numbers in a log.</p>',
         inp='numbers', approach=['${#s}, ${s: -4}.', 'printf %*s for the mask.'],
         code='''for c in 4111111111111111 5500005555555559; do
  printf -v mask '%*s' $(( ${#c} - 4 )) ''
  echo "${mask// /*}${c: -4}"
done
''', notes={2: 'A string of spaces as long as the hidden part.', 3: 'Spaces → *.'}, tryit='Group the result in blocks of 4.'),
    dict(level='a', tag='Banking', title='Fixed-width export',
         problem='<p>Write records as: account (10, zero-padded), name (15, left), amount (12, 2 decimals, right).</p>',
         inp='CSV lines', approach=['IFS=, read.', 'printf widths.'],
         code='''printf '%s\\n' '1234,Riya Sharma,1500.5' '98,Aman,20000' '7,Zoya Khan Mirza,99.99' > tx.csv
while IFS=, read -r acct name amt; do
  printf '%010d%-15.15s%12.2f\\n' "$acct" "$name" "$amt"
done < tx.csv | cat -A | sed 's/\\$$//'
''', notes={3: '%-15.15s pads and also cuts to 15.', 4: 'cat -A shows the exact width.'}, tryit='Add a trailer line with the record count.'),
]

QUIZ = mix([
    dict(q='Length of the string in s?', options=['${s#}', '${#s}', 'len $s', '${s:#}'], answer=1, why='${#s}.'),
    dict(q='f=a.b.c — ${f%.*} is…', options=['a', 'a.b', 'c', 'b.c'], answer=1, why='Shortest suffix.'),
    dict(q='f=a.b.c — ${f##*.} is…', options=['a', 'c', 'b.c', 'a.b'], answer=1, why='Longest prefix.'),
    dict(q='Replace every x with y?', options=['${s/x/y}', '${s//x/y}', '${s#x/y}', '${s%x/y}'], answer=1, why='Two slashes.'),
    dict(q='Last 3 characters?', options=['${s:-3}', '${s: -3}', '${s:3}', '${s%3}'], answer=1, why='Space needed.'),
    dict(q='Upper case in bash 4+?', options=['${s^^}', '${s,,}', '${s~}', '${s^}'], answer=0, why='^^.'),
    dict(q="printf '%05d' 42 prints…", options=['42000', '00042', '   42', '42'], answer=1, why='Zero pad.'),
    dict(q="printf '%s\\n' a b prints…", options=['a', 'a b', 'two lines', 'error'], answer=2, why='Format reused.'),
])

REVISION = [
    '${#s} length; ${s:off:len} substring; ${s: -n} last n (space!).',
    '# prefix, % suffix; one sign shortest, two signs longest; patterns are globs.',
    '${f%.*} name, ${f##*.} ext, ${p##*/} basename, ${p%/*} dirname, ${e#*@} domain.',
    '${s/a/b} first, ${s//a/b} all, /# start, /% end; ^ ^^ , ,, ~~ case (bash 4+).',
    ':- default, := assign default, :? error, :+ alternative.',
    'printf: %s %d %f %x %o %q %b %%; widths %-10s %8.2f %05d; -v var; format repeats; no automatic newline.',
]

FAQ = [
    ('How do I get a substring in bash?', '${var:offset:length}, offsets from 0; ${var: -3} for the last three characters.'),
    ('How do I remove a file extension in bash?', '${file%.*}; ${file##*.} gives the extension.'),
    ('What is the difference between # and ## (or % and %%)?', 'One sign removes the shortest match, two the longest; # from the start, % from the end.'),
    ('How do I replace text in a variable?', '${var/old/new} for the first match, ${var//old/new} for all.'),
    ('How do I convert to upper or lower case?', '${var^^} and ${var,,} in bash 4+, or tr.'),
    ('Why use printf instead of echo?', 'printf behaves the same everywhere and formats widths, decimals and alignment.'),
    ('How do I store printf output in a variable?', 'printf -v var FORMAT args.'),
]

PRACTICE_INTRO = 'Small string tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Length', stmt='Print the length of “Pathshala”.', inp='a word', code="w=Pathshala; echo ${#w}\n", explain='9.'),
    dict(level='easy', title='First 4', stmt='Print the first 4 letters of “Linux2026”.', inp='a word', code="s=Linux2026; echo ${s:0:4}\n", explain='Linu.'),
    dict(level='easy', title='Extension', stmt='Print the extension of backup.tar.gz.', inp='a name', code="f=backup.tar.gz; echo ${f##*.}\n", explain='gz.'),
    dict(level='medium', title='Double extension', stmt='Print backup from backup.tar.gz.', inp='a name', code="f=backup.tar.gz; echo ${f%%.*}\n", explain='%%.'),
    dict(level='medium', title='Domain', stmt='Print the domain of riya@myphatshala.in.', inp='an email', code="e=riya@myphatshala.in; echo ${e#*@}\n", explain='#*@.'),
    dict(level='medium', title='Clean', stmt='Turn “Big Data Notes” into big_data_notes.', inp='a title', code="t='Big Data Notes'; t=${t// /_}; echo ${t,,}\n", explain='Replace then lower.'),
    dict(level='business', title='Invoice line', stmt='Print item “pen”, qty 3 and price 12.5 as: pen        x3      12.50', inp='values', code="printf '%-10s x%-3d %8.2f\\n' pen 3 12.5\n", explain='Widths.'),
    dict(level='business', title='Employee IDs', stmt='Print EMP001 to EMP003 with printf.', inp='numbers', code="printf 'EMP%03d\\n' 1 2 3\n", explain='Format reused.'),
]

SCN_INTRO = 'Interview questions about strings in bash, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Get the file name without extension”', 'Very common.', 'syntax?',
        '''<ul>
          <li><code>${f%.*}</code>; extension <code>${f##*.}</code>.</li>
          <li>basename f .txt also works but starts a process.</li>
          <li>Watch double extensions like .tar.gz.</li>
        </ul>''', 'cut -d. -f1 (breaks with dots in names).') +
    scn('Service company', 'Junior', 'Batch-convert 5,000 images', 'Slow script with basename and sed.', 'speed up?',
        '''<ol>
          <li>Replace $(basename …) with ${f##*/}.</li>
          <li>${f%.png}.webp for the new name.</li>
          <li>Run the converter with xargs -P for parallel.</li>
        </ol>''', 'more sed.') +
    scn('Bank / fintech', 'Mid-level', 'Produce a fixed-width file', 'Each field exact width.', 'printf?',
        '''<ul>
          <li>%010d numbers, %-20.20s text (pad and cut).</li>
          <li>%12.2f amounts.</li>
          <li>Verify with awk '{print length}'.</li>
        </ul>''', 'echo with manual spaces.') +
    scn('Platform', 'Senior', 'Script works on Linux, fails on Mac', '${x^^} bad substitution.', 'why?',
        '''<ul>
          <li>macOS bash 3.2 lacks ^^ ,, and negative offsets.</li>
          <li>Use tr, require bash 4 via BASH_VERSINFO, or brew bash.</li>
          <li>Test in CI on both.</li>
        </ul>''', 'blaming the Mac.')
) + interview([
    ('# vs ##?', 'Shortest vs longest prefix.'),
    ('How to replace all?', '${s//a/b}.'),
    ('How to get the last character?', '${s: -1}.'),
    ('printf vs echo?', 'printf is portable and formats.'),
    ('What does %q do?', 'Quotes a string for safe reuse as shell input.'),
    ('Default value if empty?', '${v:-default}.'),
    ('Are patterns regex?', 'No, globs.'),
], [
    ('RHCSA / LFCS', 'Variable manipulation in scripts.'),
    ('DevOps interviews', 'Parse versions, paths and URLs in bash.'),
    ('Coding rounds', 'String tasks in bash.'),
]) + distro('Parameter expansion is POSIX for # % :-; bash adds the rest.', [
    ('${#s} # ## % %% :-', 'all shells', 'all', 'all', 'all'),
    ('${s:o:l} ${s/a/b}', 'bash', 'bash', 'bash 3.2 ok', 'bash'),
    ('${s^^} ${s,,}', 'bash 4+', 'bash 4+', 'no (3.2)', 'bash 4+'),
    ('printf', 'built-in', 'built-in', 'built-in', 'built-in'),
    ('dash (/bin/sh)', 'no :o:l, no /', '-', '-', '-'),
]) + teaser('13.1', 'Module 12 is done: Riya can write real scripts. Module 13 is about doing big jobs in one line: pipes, subshells, command substitution and the art of combining small tools. Next: combining commands.')

CHEATSHEET = cheatsheet('Strings and printf', [
    ('Measure / cut', [('${#s}', 'length'), ('${s:2:3}', 'substring'), ('${s: -3}', 'last 3'), ('${s:i:1}', 'one char')]),
    ('Trim', [('${s#p} ${s##p}', 'prefix'), ('${s%p} ${s%%p}', 'suffix'), ('${f%.*}', 'no ext'), ('${p##*/}', 'basename'), ('${p%/*}', 'dirname')]),
    ('Change', [('${s/a/b}', 'first'), ('${s//a/b}', 'all'), ('${s^^} ${s,,}', 'case'), ('${s:-d}', 'default'), ('${s:?m}', 'required')]),
    ('printf', [('%s %d %f', 'types'), ('%-10s', 'left'), ('%8.2f', 'decimals'), ('%05d', 'pad'), ('-v var', 'store')]),
])

MINDMAP = mindmap('Strings', [
    ('Measure', 'blue', ['${#s}', '${s:o:l}', '${s: -n}']),
    ('Trim', 'green', ['# ##', '% %%', 'globs']),
    ('Replace', 'amber', ['/ //', '/# /%', 'delete']),
    ('Case', 'violet', ['^ ^^', ', ,,', '~~']),
    ('Defaults', 'red', [':-', ':=', ':? :+']),
    ('printf', 'acc', ['%s %d %f', 'widths', '-v %q']),
])

LAB = lab('rename photos', 'Build the lab, write <code>~/lab1214/rename.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab1214 && cd ~/lab1214 && rm -rf rename.sh in out.txt table.txt
mkdir in && touch 'in/Beach Day.JPG' 'in/city walk.jpeg' in/IMG_7.PNG in/notes.TXT''',
    tasks=['In <code>in/</code>, rename every file to lower case with spaces replaced by <code>_</code>, and <code>.jpeg</code> changed to <code>.jpg</code>.',
           'Write the extensions of the renamed files, sorted and unique, one per line, into <code>out.txt</code>.',
           'Write a table into <code>table.txt</code>: one line per renamed file, name left-aligned in 16 characters, then its name length right-aligned in 3 (<code>printf \'%-16s%3d\\n\'</code>), sorted by name.',
           'Use parameter expansion for the changes (no sed, tr or awk in rename.sh).'],
    solution='''cat > rename.sh <<'EOF'
cd in || exit 1
for f in *; do
  n=${f,,}; n=${n// /_}; n=${n/%.jpeg/.jpg}
  [ "$f" != "$n" ] && mv -- "$f" "$n"
done
for f in *; do echo "${f##*.}"; done | sort -u > ../out.txt
for f in *; do printf '%-16s%3d\\n' "$f" "${#f}"; done > ../table.txt
EOF''',
    check='''cd ~/lab1214; rm -rf in out.txt table.txt; mkdir in && touch 'in/Beach Day.JPG' 'in/city walk.jpeg' in/IMG_7.PNG in/notes.TXT
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f rename.sh ] && bash rename.sh 2>/dev/null
ok "1 names"  '[ "$(ls in | tr "\\n" " ")" = "beach_day.jpg city_walk.jpg img_7.png notes.txt " ]'
ok "2 exts"   '[ "$(cat out.txt 2>/dev/null)" = "$(printf "jpg\\npng\\ntxt")" ]'
ok "3 table"  '[ "$(sed -n 1p table.txt 2>/dev/null)" = "beach_day.jpg    13" ] && [ "$(wc -l < table.txt)" = 4 ]'
ok "4 no sed" '[ -f rename.sh ] && ! grep -qE "(^|[ |])(sed|tr|awk)( |$)" rename.sh' ''')
