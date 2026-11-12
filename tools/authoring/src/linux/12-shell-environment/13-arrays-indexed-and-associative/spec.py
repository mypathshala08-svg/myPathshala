import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='13-arrays-indexed-and-associative', n='12.13',
    module_label='Module 12 · The shell environment and shell programming',
    title='Bash arrays: indexed and associative arrays, mapfile and read -a',
    desc='Bash arrays from zero: create, read, change and append; "${a[@]}" vs ${a[*]}, ${#a[@]}, ${!a[@]}, slices, negative indices, unset and sparse arrays; associative arrays with declare -A as lookups and counters; mapfile/readarray, read -ra, arrays from globs and commands, arrays in functions with local -n; real outputs and 30+ examples.',
    og_desc='Bash indexed and associative arrays explained with real runs: every ${…} form, mapfile, counters and the common traps.',
    minutes=40, level='Beginner → Advanced',
    lead='One variable, many values: indexed arrays for lists and associative arrays for name → value lookups. Every form, the quoting rule that keeps file names whole, and how to fill arrays from files and commands.',
    chips=['Lockers and drawers animated', 'Every ${…} form', 'Counters and lookups', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Indexed and associative arrays
servers=(web01 web02 db01)
servers+=(app01)
echo "count: ${#servers[@]}, first: ${servers[0]}, last: ${servers[-1]}"
for s in "${servers[@]}"; do echo " - $s"; done

declare -A ip=([web01]=10.0.0.11 [db01]=10.0.0.21)
ip[app01]=10.0.0.31
echo "db01 is at ${ip[db01]}"
for h in "${!ip[@]}"; do echo "$h ${ip[$h]}"; done | sort
"""

RUN = dict(
    heading='Both kinds of arrays',
    intro='<p>Create a list and a lookup table, add to both, and loop over them.</p>',
    code=MAIN,
    anno=[('"${servers[@]}"', 'Quoted: each item stays one word.'), ('declare -A', 'Required for string keys.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Why is the ip loop piped to sort?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two echo lines print?',
             code="a=(apple 'big banana' cherry)\necho ${#a}\necho ${#a[@]}\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> should print 2 lines. Fix the quoting.',
             code="files=('my report.txt' 'notes.txt')\nfor f in ${files[@]}; do echo \"[$f]\"; done\n"),
        dict(label='4 · Your turn', hint='Count the colours with an associative array.',
             code="declare -A n\nfor c in red blue red green red; do ((n[$c]++)); done\nfor c in \"${!n[@]}\"; do echo \"$c ${n[$c]}\"; done | sort\n"),
        dict(label='5 · Challenge', hint='Read lines into an array with mapfile and print the last one.',
             code="printf 'one\\ntwo\\nthree\\n' > list.txt\nmapfile -t lines < list.txt\necho \"${#lines[@]} lines, last: ${lines[-1]}\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: check your bash',
    intro='<p>Associative arrays need bash 4+. Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · bash version', cmd='echo $BASH_VERSION', output=pc('echo $BASH_VERSION'), note='Recorded. 4.0 or newer for declare -A.'),
        dict(title='2 · macOS default bash', cmd='/bin/bash -c \'declare -A m\'', output='/bin/bash: line 0: declare: -A: invalid option', note='Typical on macOS (bash 3.2). Install bash 5 with Homebrew or use zsh.'),
        dict(title='3 · Your home folders into an array', cmd='mapfile -t d < <(ls ~); echo "${#d[@]} items: ${d[*]:0:3}"', output='12 items: Desktop Documents Downloads', note='Typical.'),
        dict(title='4 · Arrays are not exported', cmd='a=(1 2); export a; bash -c \'echo "[${a[@]}]"\'', output=pc("a=(1 2); export a; bash -c 'echo \"[${a[@]}]\"'"), note='Recorded: the child sees nothing.'),
    ],
)

TRACE = dict(
    heading='An array changing, line by line',
    intro='<p>Step through: create, append, change, delete and count.</p>',
    code='''a=(red green blue)
a+=(black)
a[1]=lime
unset 'a[0]'
n=${#a[@]}
keys="${!a[*]}"
echo "$n items at indices $keys: ${a[*]}"
''',
    notes={1: 'Indices 0 1 2.', 2: 'Index 3 added.', 3: 'Item 1 replaced.', 4: 'Index 0 gone; no renumbering.', 6: 'Indices 1 2 3.'},
)

WORKED_INTRO = 'Three tasks from real jobs: grades, an access list and a CSV lookup.'
EXAMPLES = [
    dict(level='b', tag='Education', title='Class results',
         problem='<p>From a list of marks, print the count, total, average and highest.</p>',
         inp='marks', approach=['Loop with ((s+=m)).', 'Track the max.'],
         code='''marks=(67 82 91 58 74)
total=0; max=0
for m in "${marks[@]}"; do ((total += m)); ((m > max)) && max=$m; done
echo "students=${#marks[@]} total=$total avg=$((total / ${#marks[@]})) max=$max"
''', notes={3: 'One pass for both.'}, tryit='Also print how many scored below 60.'),
    dict(level='i', tag='Security', title='Allow only known commands',
         problem='<p>Check user requests against an allow-list stored as associative keys.</p>',
         inp='requests', approach=['declare -A allowed.', '[[ -v ]] test.'],
         code='''declare -A allowed=([start]=1 [stop]=1 [status]=1)
for req in status restart stop 'rm -rf'; do
  if [[ -v allowed[$req] ]]; then echo "ok: $req"; else echo "denied: $req"; fi
done
''', notes={3: 'Lookup instead of a long if/elif chain.'}, tryit='Add restart to the list.'),
    dict(level='a', tag='Data', title='Join two CSVs by key',
         problem='<p>Load city → state from one file and attach it to each sale in another.</p>',
         inp='two CSVs', approach=['mapfile -s 1.', 'IFS=, read.'],
         code='''printf 'city,state\\npune,MH\\ndelhi,DL\\n' > cities.csv
printf 'id,city,amt\\n1,pune,100\\n2,delhi,250\\n3,goa,90\\n' > sales.csv
declare -A state
while IFS=, read -r c s; do state[$c]=$s; done < <(tail -n +2 cities.csv)
while IFS=, read -r id c amt; do echo "$id,$c,${state[$c]:-??},$amt"; done < <(tail -n +2 sales.csv)
''', notes={3: 'Lookup table.', 4: '?? for unknown cities.'}, tryit='Count the sales per state.'),
]

QUIZ = mix([
    dict(q='Bash indexed arrays start at…', options=['1', '0', '-1', 'any'], answer=1, why='0.'),
    dict(q='Number of items in a?', options=['${#a}', '${#a[@]}', '$#a', 'len(a)'], answer=1, why='${#a} is the length of item 0.'),
    dict(q='Safe loop over items with spaces?', options=['for x in ${a[@]}', 'for x in "${a[@]}"', 'for x in $a', 'for x in "${a[*]}"'], answer=1, why='Quoted [@].'),
    dict(q='Associative arrays need…', options=['declare -a', 'declare -A', 'export', 'nothing'], answer=1, why='-A.'),
    dict(q='${!m[@]} gives…', options=['values', 'keys', 'count', 'last item'], answer=1, why='Keys/indices.'),
    dict(q="After a=(x y z); unset 'a[1]', indices are…", options=['0 1', '0 2', '1 2', '0 1 2'], answer=1, why='No renumbering.'),
    dict(q='Lines of a file into an array?', options=['read -a', 'mapfile -t', 'cat |', 'split'], answer=1, why='mapfile.'),
    dict(q='Why is cmd | mapfile -t a empty afterwards?', options=['mapfile is broken', 'the pipe runs mapfile in a subshell', '-t removes all', 'needs sudo'], answer=1, why='Use < <(cmd).'),
])

REVISION = [
    'a=(x y z); ${a[0]}; ${a[-1]}; a+=(w); a[1]=v.',
    'Always "${a[@]}" in loops and arguments; "${a[*]}" joins into one word.',
    '${#a[@]} count, ${#a[i]} length of one item, ${!a[@]} indices or keys, ${a[@]:s:n} slice.',
    "unset 'a[i]' leaves a gap; a=(\"${a[@]}\") renumbers; declare -p shows everything.",
    'declare -A m; m[key]=v; [[ -v m[key] ]]; ((m[$k]++)); keys are unordered.',
    'mapfile -t a < file / < <(cmd); read -ra a <<< "$line"; local -n for functions.',
]

FAQ = [
    ('How do I create an array in bash?', 'arr=(one two three); read with ${arr[0]}, all with "${arr[@]}".'),
    ('How do I get the length of an array?', '${#arr[@]}.'),
    ('What is an associative array?', 'A bash 4+ array with string keys, declared with declare -A, used like a dictionary.'),
    ('What is the difference between ${arr[@]} and ${arr[*]}?', 'Quoted, [@] gives each item as a separate word and [*] joins them into one.'),
    ('How do I read a file into an array?', 'mapfile -t arr < file (also called readarray).'),
    ('How do I delete an item?', "unset 'arr[i]'; indices are not renumbered."),
    ('Does /bin/sh support arrays?', 'No. Only "$@" via set --; use bash.'),
]

PRACTICE_INTRO = 'Small array tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Third item', stmt='Print the third item of (a b c d).', inp='an array', code="x=(a b c d); echo \"${x[2]}\"\n", explain='Index 2.'),
    dict(level='easy', title='Count', stmt='Print how many items are in (10 20 30 40 50).', inp='an array', code="x=(10 20 30 40 50); echo ${#x[@]}\n", explain='5.'),
    dict(level='easy', title='Append', stmt='Add z to (x y) and print all.', inp='an array', code="a=(x y); a+=(z); echo \"${a[@]}\"\n", explain='+=.'),
    dict(level='medium', title='Slice', stmt='Print items 2 to 4 (indices 1–3) of (a b c d e).', inp='an array', code="a=(a b c d e); echo \"${a[@]:1:3}\"\n", explain='b c d.'),
    dict(level='medium', title='Lookup', stmt='Map in→India, jp→Japan and print the name for jp.', inp='codes', code="declare -A c=([in]=India [jp]=Japan); echo \"${c[jp]}\"\n", explain='Japan.'),
    dict(level='medium', title='Keys sorted', stmt='Print the keys of ([b]=2 [a]=1 [c]=3) sorted.', inp='a map', code="declare -A m=([b]=2 [a]=1 [c]=3); printf '%s\\n' \"${!m[@]}\" | sort\n", explain='a b c.'),
    dict(level='business', title='Count fruit', stmt='Count each word in: apple pear apple fig apple pear.', inp='words', code="declare -A n; for w in apple pear apple fig apple pear; do ((n[$w]++)); done; for w in \"${!n[@]}\"; do echo \"$w ${n[$w]}\"; done | sort\n", explain='apple 3, fig 1, pear 2.'),
    dict(level='business', title='Fields of a line', stmt='Split riya:x:1000:1000 on : and print the third field.', inp='a passwd line', code="IFS=: read -ra f <<< 'riya:x:1000:1000'; echo \"${f[2]}\"\n", explain='1000.'),
]

SCN_INTRO = 'Interview questions about bash arrays, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Loop over an array”', 'Very common.', 'syntax?',
        '''<ul>
          <li><code>for x in "${arr[@]}"; do echo "$x"; done</code></li>
          <li>Count: <code>${#arr[@]}</code>; indices: <code>${!arr[@]}</code>.</li>
          <li>Quotes keep items with spaces whole.</li>
        </ul>''', 'for x in $arr (only item 0).') +
    scn('Service company', 'Junior', 'A file list breaks on names with spaces', 'files=$(ls) used.', 'fix?',
        '''<ol>
          <li>Use files=(*) or mapfile -t files &lt; &lt;(find … ).</li>
          <li>Loop with "${files[@]}".</li>
          <li>For any name: find -print0 + mapfile -d \'\'.</li>
        </ol>''', 'changing IFS globally.') +
    scn('DevOps', 'Mid-level', 'Map environment names to hosts', 'dev/test/prod.', 'structure?',
        '''<ul>
          <li><code>declare -A host=([dev]=… [prod]=…)</code></li>
          <li>Validate with [[ -v host[$env] ]].</li>
          <li>Load from a file with while read.</li>
        </ul>''', 'nested if/elif.') +
    scn('Platform', 'Senior', 'Script must run on macOS and Linux', 'macOS bash 3.2.', 'what breaks?',
        '''<ul>
          <li>declare -A, mapfile, ${a[-1]}, local -n need bash 4+.</li>
          <li>Use #!/usr/bin/env bash and require bash 4, or rewrite with awk.</li>
          <li>Check $BASH_VERSINFO at the top.</li>
        </ul>''', 'assuming one bash everywhere.')
) + interview([
    ('${#a} vs ${#a[@]}?', 'Length of item 0 vs number of items.'),
    ('How to delete an item?', "unset 'a[i]'."),
    ('Are arrays exported?', 'No.'),
    ('How to test a key?', '[[ -v m[key] ]].'),
    ('Pass an array to a function?', '"${a[@]}" as arguments or local -n ref.'),
    ('Is the key order kept?', 'No for associative arrays.'),
    ('Negative index?', '${a[-1]} last item, bash 4.3+.'),
], [
    ('RHCSA / LFCS', 'Shell scripts with loops over lists.'),
    ('DevOps interviews', 'Bash arrays and dictionaries.'),
    ('Coding rounds', 'Count frequencies in bash or awk.'),
]) + distro('Arrays are a bash/zsh/ksh feature; sh (dash) has none.', [
    ('Indexed arrays', 'bash 5', 'bash 5', 'bash 3.2 / zsh', 'Git Bash'),
    ('declare -A', 'yes', 'yes', 'no (bash 3.2); zsh typeset -A', 'yes'),
    ('mapfile', 'yes', 'yes', 'no (3.2)', 'yes'),
    ('Index base', '0', '0', 'zsh: 1', '0'),
    ('/bin/sh', 'dash: no arrays', 'bash in sh mode', '-', '-'),
]) + teaser('12.14', 'Riya needs the extension of a file name, the domain of an email, a name in capitals and a neatly aligned table. Bash can do all of it without sed or awk: ${var#…}, ${var%…}, ${var/…/…}, ${var^^} and printf. Next: string manipulation and printf.')

CHEATSHEET = cheatsheet('Arrays', [
    ('Indexed', [('a=(x y)', 'create'), ('${a[0]}', 'item'), ('a+=(z)', 'append'), ('${a[-1]}', 'last'), ("unset 'a[1]'", 'delete')]),
    ('All / count', [('"${a[@]}"', 'each item'), ('"${a[*]}"', 'joined'), ('${#a[@]}', 'count'), ('${!a[@]}', 'indices'), ('${a[@]:1:2}', 'slice')]),
    ('Associative', [('declare -A m', 'create'), ('m[k]=v', 'set'), ('${m[k]}', 'get'), ('[[ -v m[k] ]]', 'exists'), ('((m[$k]++))', 'count')]),
    ('Fill', [('mapfile -t a < f', 'lines'), ('< <(cmd)', 'command'), ('read -ra a <<< "$l"', 'split'), ('a=(*.csv)', 'glob'), ('declare -p a', 'inspect')]),
])

MINDMAP = mindmap('Arrays', [
    ('Indexed', 'blue', ['a=(…)', '${a[i]}', 'from 0']),
    ('All items', 'green', ['"${a[@]}"', '${#a[@]}', '${!a[@]}']),
    ('Change', 'amber', ['a+=()', 'unset', 'slices']),
    ('Assoc', 'violet', ['declare -A', 'keys', 'counters']),
    ('Fill', 'acc', ['mapfile', 'read -a', 'globs']),
    ('Traps', 'red', ['unquoted', '${#a}', 'pipes']),
])

LAB = lab('a server inventory', 'Build the lab, write <code>~/lab1213/inv.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab1213 && cd ~/lab1213 && rm -f inv.sh out_*.txt
printf 'web01,10.0.0.11,web\\nweb02,10.0.0.12,web\\ndb01,10.0.0.21,db\\ncache01,10.0.0.31,cache\\n' > hosts.csv''',
    tasks=['Read <code>hosts.csv</code> into an indexed array <code>rows</code> with mapfile, and write the number of rows into <code>out_count.txt</code>.',
           'Build an associative array <code>ip</code> (host → IP) and write the IP of <code>db01</code> into <code>out_ip.txt</code>.',
           'Count hosts per role with an associative array and write lines <code>role count</code>, sorted by role, into <code>out_roles.txt</code>.',
           'Write all host names joined with commas (in file order) into <code>out_names.txt</code>.'],
    solution='''cat > inv.sh <<'EOF'
mapfile -t rows < hosts.csv
echo "${#rows[@]}" > out_count.txt
declare -A ip role_n
names=()
for r in "${rows[@]}"; do
  IFS=, read -r h a role <<< "$r"
  ip[$h]=$a; ((role_n[$role]++)); names+=("$h")
done
echo "${ip[db01]}" > out_ip.txt
for k in "${!role_n[@]}"; do echo "$k ${role_n[$k]}"; done | sort > out_roles.txt
(IFS=,; echo "${names[*]}") > out_names.txt
EOF''',
    check='''cd ~/lab1213; rm -f out_*.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f inv.sh ] && bash inv.sh 2>/dev/null
ok "1 count"  '[ "$(cat out_count.txt 2>/dev/null)" = 4 ] && grep -q mapfile inv.sh'
ok "2 ip"     '[ "$(cat out_ip.txt 2>/dev/null)" = 10.0.0.21 ] && grep -q "declare -A" inv.sh'
ok "3 roles"  '[ "$(cat out_roles.txt 2>/dev/null)" = "$(printf "cache 1\\ndb 1\\nweb 2")" ]'
ok "4 names"  '[ "$(cat out_names.txt 2>/dev/null)" = "web01,web02,db01,cache01" ]' ''')
