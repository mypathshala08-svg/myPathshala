import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

AR = r"""rm -rf ~/ar; mkdir -p ~/ar; cd ~/ar
printf 'web01 10.0.0.11 up\nweb02 10.0.0.12 down\ndb01 10.0.0.21 up\n' > servers.txt
touch 'report jan.csv' 'report feb.csv' notes.txt"""

HOOK = hook('Riya keeps server names in <code>server1</code>, <code>server2</code>, <code>server3</code> and loops over them with <code>eval</code>. When a fourth server arrives she edits five places. Bash has <b>arrays</b>: one variable holding a list (<code>servers=(web01 web02 db01)</code>), and <b>associative arrays</b> that map a name to a value (<code>ip[web01]=10.0.0.11</code>). Arrays are also the only safe way to keep a list of file names that contain spaces, and to build a command with arguments. This lesson covers both kinds, every <code>${…}</code> form that works on them, <code>mapfile</code> to read files into arrays, and the mistakes that silently break scripts.',
    ['create indexed arrays, read and change items, and loop over them safely with "${arr[@]}"',
     'use the length, indices, slicing, appending and deleting forms, and know $@ vs $* for arrays',
     'create associative arrays with declare -A and use them as lookup tables and counters',
     'fill arrays from commands and files with mapfile/readarray and read -a, and pass them to functions'])
ROAD = roadmap([
    ('story', 'The story', 3, 'one variable, many values'),
    ('decide', 'Which form when?', 2, 'the quick chart'),
    ('definition', 'What an array is', 6, 'simple meaning + 4 depths'),
    ('types', 'Indexed vs associative', 5, 'every ${…} form'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'boxes and keys'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a server inventory'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which form? (decide in 5 seconds)', [
    ('A list in order', 'servers=(web01 web02 db01)', 'indexed array'),
    ('Name → value lookup', 'declare -A ip; ip[web01]=10.0.0.11', 'associative'),
    ('Every item, safely', 'for s in "${servers[@]}"', 'quoted [@]'),
    ('How many items', '${#servers[@]}', 'length'),
    ('Add to the end', 'servers+=(app01)', 'append'),
    ('Lines of a file', 'mapfile -t lines < file', 'readarray'),
    ('Split one line', 'read -ra parts <<< "$line"', 'read -a'),
    ('Count things', 'declare -A n; ((n[$k]++))', 'counter'),
])

cmap = concept_map(
    [('12.1', 'Variables', 'one value'), ('12.9', 'Loops', 'for and while'), ('12.11', 'Expansion', 'eval and ${!name}')],
    ['indexed arrays (0, 1, 2…)', 'associative arrays (keys)', '"${a[@]}" vs ${a[*]}', 'length, indices, slices, append, unset', 'mapfile, read -a, arrays in functions'],
    [('12.14', 'Strings', '${var} operations on items'), ('13.5', 'Data one-liners', 'awk arrays'), ('17.4', 'cron scripts', 'lists of jobs'), ('21.1', 'Capstone', 'server inventories')],
    'An array is a numbered row of boxes; an associative array is a row of labelled boxes. Quote "${a[@]}" and each box stays one item.')

sc = (term(20, 14, 316, 156, ['$ servers=(web01 web02 db01)', '$ echo ${#servers[@]} ${servers[1]}', ('3 web02', 'out'), '$ declare -A ip=([web01]=10.0.0.11)', '$ echo ${ip[web01]}', ('10.0.0.11', 'acc')], title='riya@web01: ~/ar', prompt='riya@web01:~/ar$', size=6.8, step=17)
      + t(352, 36, 'One variable:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['[0] web01', '[1] web02', '[2] db01', 'ip[web01]', '  = 10.0.0.11'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One variable, many values</h2>
  <div class="story">
''' + puzzle('Riya puts two file names in an array: <code>files=("report jan.csv" "report feb.csv")</code>. She runs <code>for f in ${files[@]}; do echo "[$f]"; done</code> and gets four lines: <code>[report]</code> <code>[jan.csv]</code> <code>[report]</code> <code>[feb.csv]</code>. Then <code>echo ${#files}</code> prints 14, not 2. And <code>declare -A</code> is missing, so <code>ip[web01]=1; ip[db01]=2; echo ${ip[web01]}</code> prints 2. Explain all three.') + '''
    <p class="narration">Riya replaces three variables with one array.</p>
''' + scene('A terminal: an array of three servers, its length and second item, and an associative array lookup.', sc,
            'Index from <tspan font-weight="700" class="s-acc">0</tspan>; keys are labels.') + '''
K> Why does web02 come out for index 1?
A> Indexed arrays count from 0. <code>${servers[0]}</code> is web01. <code>${#servers[@]}</code> is the number of items.
R> And the ip one?
A> That is an <b>associative</b> array, declared with <code>declare -A</code>. Keys are strings, so it works like a phone book: name in, value out. Today: both kinds, every form, and the three traps in the puzzle.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Left: a row of numbered lockers 0, 1, 2 holding web01, web02, db01. Right: a cabinet of labelled drawers web01, web02, db01 holding IP addresses.">'
       + ''.join(label_box(20 + i * 92, 40, 84, 60, [f'[{i}]', v], 'blue', 9) for i, v in enumerate(['web01', 'web02', 'db01']))
       + t(150, 130, 'Indexed: numbered lockers', 10, 'blue', bold=True)
       + ''.join(label_box(330 + i * 100, 40, 92, 60, [k, v], 'green', 8.4) for i, (k, v) in enumerate([('web01', '10.0.0.11'), ('web02', '10.0.0.12'), ('db01', '10.0.0.21')]))
       + t(480, 130, 'Associative: labelled drawers', 10, 'green', bold=True)
       + t(320, 175, 'Same box idea, different way of finding a box.', 9.6, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Arrays at four depths', [
    ('v', 'No jargon: lockers and drawers', '      <p>A row of numbered lockers, or a cabinet with labelled drawers.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>fruits=(apple banana cherry)</code>: create.</li>
        <li><code>echo "${fruits[0]}"</code>: first item.</li>
        <li><code>echo "${#fruits[@]}"</code>: how many.</li>
        <li><code>for f in "${fruits[@]}"; do …; done</code>: every item.</li>
      </ul>'''),
    ('i', 'All the forms', '''      <ul>
        <li><code>"${a[@]}"</code> each item as one word; <code>"${a[*]}"</code> all items joined into one word (first char of IFS).</li>
        <li><code>${!a[@]}</code> the indices or keys; <code>${a[@]:1:2}</code> a slice.</li>
        <li><code>a+=(x y)</code> append; <code>unset 'a[1]'</code> delete one (indices are not renumbered); <code>unset a</code> delete all.</li>
        <li><code>declare -A m</code> associative; <code>${m[key]}</code>; <code>[[ -v m[key] ]]</code> exists?</li>
      </ul>'''),
    ('a', 'Behind the screen: sparse arrays and references', '''      <ul>
        <li>Indexed arrays are <b>sparse</b>: after <code>unset 'a[1]'</code> the indices are 0 2; <code>a[100]=x</code> does not create 98 empty items. Loop over <code>"${!a[@]}"</code>, not 0..length-1.</li>
        <li><code>$a</code> alone means <code>${a[0]}</code>; <code>${#a}</code> is the <b>length of item 0</b> (the puzzle’s 14).</li>
        <li>Without <code>declare -A</code>, <code>ip[web01]</code> is an indexed array and the key is evaluated as arithmetic: web01 is an unset variable = 0, so every key lands on index 0.</li>
        <li>Arrays cannot be exported to child processes; functions get them by name with <code>local -n ref=$1</code> (bash 4.3+) or as "$@".</li>
        <li>Associative arrays need bash 4+ (macOS ships bash 3.2); key order is not guaranteed, so pipe through sort.</li>
        <li>POSIX sh (dash) has no arrays at all; only "$@".</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Indexed and associative arrays in bash</h2>
''' + def_block(
    'An <b>array</b> is a variable that holds many values. An <b>indexed array</b> numbers its items from 0; an <b>associative array</b> (<code>declare -A</code>, bash 4+) uses string <b>keys</b>. Items are read with <code>${name[index]}</code>, all items with <code>"${name[@]}"</code>, and the count with <code>${#name[@]}</code>.',
    'One name, many boxes: numbered or labelled.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Array', 'One variable, many values.'),
    ('Element / item', 'One value in the array.'),
    ('Index', 'Position number, from 0.'),
    ('Key', 'A label in an associative array.'),
    ('Associative array', 'declare -A: key → value.'),
    ('Sparse', 'Indices may have gaps.'),
    ('Slice', '${a[@]:start:count}.'),
    ('mapfile / readarray', 'Read lines into an array.'),
]) + '\n' + names('Where the names come from.', [
    ('array', 'arranged row', 'From Latin ad + ready.'),
    ('declare -a', 'array', 'indexed.'),
    ('declare -A', 'Associative', 'bash 4.0, 2009.'),
    ('mapfile', 'map a file', 'bash 4.0.'),
    ('readarray', 'same as mapfile', 'Alias name.'),
    ('@', 'all, separately', 'Like "$@".'),
    ('*', 'all, joined', 'Like "$*".'),
    ('hash / dict', 'other languages’ name', 'Python dict, Perl hash.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Create', '<code>a=(x y z)</code>'),
    ('One item', '<code>${a[0]}</code>'),
    ('All items', '<code>"${a[@]}"</code>'),
    ('Count', '<code>${#a[@]}</code>'),
    ('Map', '<code>declare -A m</code>'),
    ('From file', '<code>mapfile -t a &lt; f</code>'),
]) + '\n' + lv + didyou('Bash arrays start at 0, zsh arrays start at 1. The same script <code>a=(x y); echo $a[1]</code> prints different things in the two shells, one reason scripts start with <code>#!/bin/bash</code>.') + '''
EXAM> “How do you find the number of elements in an array?” → ${#arr[@]}. (${#arr} is the length of the first element.)
''' + qc('With <code>a=(red green blue)</code>, what is <code>${a[2]}</code>?', 'blue (counting from 0).') + mistake('for f in ${files[@]}',
    'for f in "${files[@]}"',
    'Unquoted, every item is split at spaces and globbed; "report jan.csv" becomes two items (real run). Quoted "${a[@]}" keeps each item whole.') + mistake('ip[web01]=1 without declare -A',
    'declare -A ip; ip[web01]=1',
    'Without -A the key is arithmetic: web01 → 0, db01 → 0, so both write index 0 (real run prints 2).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Indexed vs associative, and every ${…} form</h2>
''' + table(['', 'Indexed', 'Associative'], [
    ['Declare', '<code>a=(…)</code> or <code>declare -a a</code>', '<code>declare -A m</code> (required)'],
    ['Lookup by', 'number 0, 1, 2…', 'string key'],
    ['Order', 'by index', 'not guaranteed'],
    ['Create with values', '<code>a=(x y)</code>', '<code>m=([k1]=v1 [k2]=v2)</code>'],
    ['bash version', 'all', '4.0+'],
    ['Use', 'lists, files, arguments', 'lookups, counters, configs'],
], minw=420) + table(['Form', 'Gives', 'With a=(x "y z" w)'], [
    ['<code>${a[0]}</code>', 'one item', 'x'],
    ['<code>"${a[@]}"</code>', 'all, each one word', '3 words: x | y z | w'],
    ['<code>"${a[*]}"</code>', 'all, joined into one word', '1 word: x y z w'],
    ['<code>${#a[@]}</code>', 'number of items', '3'],
    ['<code>${#a[1]}</code>', 'length of item 1', '3'],
    ['<code>${!a[@]}</code>', 'indices / keys', '0 1 2'],
    ['<code>${a[@]:1:2}</code>', 'slice: from 1, 2 items', 'y z w'],
    ['<code>${a[-1]}</code>', 'last item (bash 4.3+)', 'w'],
    ['<code>a+=(v)</code>', 'append', '4 items'],
    ['<code>unset \'a[1]\'</code>', 'delete item 1', 'indices 0 2'],
    ['<code>${a[@]/x/X}</code>', 'replace in every item', 'X y z w'],
], minw=520) + table(['Fill from', 'Command', 'Notes'], [
    ['a list', '<code>a=(one two)</code>', 'quotes for spaces'],
    ['a glob', '<code>files=(*.csv)</code>', 'safe with spaces'],
    ['lines of a file', '<code>mapfile -t a &lt; file</code>', '-t drops newlines'],
    ['a command', '<code>mapfile -t a &lt; &lt;(cmd)</code>', 'not cmd | mapfile'],
    ['one line', '<code>read -ra a &lt;&lt;&lt; "$line"</code>', 'split by IFS'],
    ['a CSV line', '<code>IFS=, read -ra a &lt;&lt;&lt; "$line"</code>', 'comma'],
], minw=480) + qc('Why <code>mapfile -t a &lt; &lt;(cmd)</code> and not <code>cmd | mapfile -t a</code>?', 'In a pipe, mapfile runs in a subshell, so the array disappears when the pipe ends.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Indexed arrays, associative arrays and filling them, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (bash 5.2) as riya, in <code>~/ar</code> with <code>servers.txt</code> (three lines: name, IP, status), two files with spaces (<code>report jan.csv</code>, <code>report feb.csv</code>) and <code>notes.txt</code>.</p>
''' + cmdcard_u(['lists: servers, files, users, arguments', 'anything with spaces in it'],
               ['2-D tables (use awk or a key like "row,col")'])(
    'idx', 'a=(…) · ${a[i]} · "${a[@]}" · ${#a[@]} · a+=()', 'indexed arrays',
    'Create with parentheses, separated by spaces. Read one item by index (from 0, negative counts from the end). Use <code>"${a[@]}"</code> in loops and as arguments. Append with <code>+=</code>; change with <code>a[i]=value</code>.',
    'a=(v1 v2)   ·   ${a[i]}   ·   for x in "${a[@]}"', 'safe',
    [('a=(x y z)', 'create', 'lists'),
     ('a[3]=w', 'set one', 'change'),
     ('${a[-1]}', 'last item', 'bash 4.3+'),
     ('"${a[@]}"', 'every item', 'loops'),
     ('${#a[@]}', 'count', 'checks'),
     ('a+=(v)', 'append', 'collect'),
     ('${!a[@]}', 'indices', 'sparse loops')],
    dict(setup=AR, cmd="servers=(web01 web02 db01)\necho \"first=${servers[0]} last=${servers[-1]} count=${#servers[@]}\"\nservers+=(app01)\nservers[1]=web02-new\nfor i in \"${!servers[@]}\"; do echo \"$i: ${servers[$i]}\"; done", note='Index 1 was replaced; app01 was appended as index 3.'),
    [('sys', [
        dict(situation='The puzzle, part 1 and 2: spaces and ${#a}.', setup=AR, cmd="cd ~/ar; files=(\"report jan.csv\" \"report feb.csv\")\nfor f in ${files[@]}; do echo \"[$f]\"; done\nfor f in \"${files[@]}\"; do echo \"[$f]\"; done\necho \"${#files} vs ${#files[@]}\"", why='Unquoted: 4 words. Quoted: 2 items. ${#files} is the length of item 0 ("report jan.csv" = 14).')]),
     ('dev', [
        dict(situation='Files from a glob, safely.', setup=AR, cmd="cd ~/ar; csv=(*.csv)\necho \"${#csv[@]} csv files\"\nprintf '<%s>\\n' \"${csv[@]}\"", why='A glob into an array keeps spaces; printf repeats its format for every item.')]),
    ],
    anat=anatomy([('servers', 'cmd', 'name'), ('=(', 'opt', 'start'), ('web01 web02', 'arg', 'items'), (')', 'opt', 'end')], 'No spaces around =. Items separated by spaces; quote items that contain spaces.')
) + cmdcard_u(['slices, deletes, search-and-replace on all items', 'joining with a separator'],
               ['assuming indices are 0..n-1 after unset'])(
    'ops', '${a[@]:s:n} · unset · ${a[*]} · ${a[@]/x/y}', 'slicing, deleting and joining',
    'A slice <code>${a[@]:start:count}</code> returns part of the array. <code>unset \'a[i]\'</code> removes one item but does <b>not</b> renumber (quote it so [i] is not a glob). <code>"${a[*]}"</code> joins with the first character of IFS. String operations like <code>/old/new</code> and <code>#prefix</code> apply to every item.',
    '${a[@]:1:2}   ·   unset \'a[1]\'   ·   (IFS=,; echo "${a[*]}")', 'safe',
    [('${a[@]:1}', 'from item 1', 'skip first'),
     ('${a[@]:0:2}', 'first two', 'top N'),
     ('unset \'a[i]\'', 'delete one', 'remove'),
     ('a=("${a[@]}")', 'renumber', 'after unset'),
     ('"${a[*]}"', 'join', 'CSV lines'),
     ('${a[@]/#/pre-}', 'prefix all', 'paths'),
     ('${a[@]%.csv}', 'strip suffix all', 'names')],
    dict(cmd="a=(mon tue wed thu fri)\necho \"slice: ${a[@]:1:3}\"\nunset 'a[1]'\necho \"after unset: ${a[*]}  indices: ${!a[*]}\"\na=(\"${a[@]}\"); echo \"renumbered: ${!a[*]}\"\n(IFS=,; echo \"joined: ${a[*]}\")", note='After unset the indices were 0 2 3 4 until the array was rebuilt.'),
    [('data', [
        dict(situation='Change every item at once.', setup=AR, cmd="cd ~/ar; files=(*.csv)\nprintf '%s\\n' \"${files[@]%.csv}\"\nprintf '%s\\n' \"${files[@]/#/backup/}\"\nprintf '%s\\n' \"${files[@]// /_}\"", why='%.csv strips the suffix, /#/ adds a prefix, // replaces every space.')]),
    ]
) + cmdcard_u(['lookups: name → IP, user → shell', 'counting things', 'config key = value'],
               ['ordered output without sort', 'bash 3 (macOS default)'])(
    'assoc', 'declare -A m · m[key]=v · ${m[key]} · ${!m[@]} · [[ -v m[k] ]]', 'associative arrays',
    'Declare with <code>declare -A</code> first. Keys are strings (quote keys with spaces). <code>${!m[@]}</code> gives the keys, <code>${m[@]}</code> the values. Check a key with <code>[[ -v m[key] ]]</code>. Count with <code>((m[$k]++))</code>.',
    'declare -A m=([k]=v)   ·   ${m[k]}   ·   for k in "${!m[@]}"', 'safe',
    [('declare -A m', 'create', 'required'),
     ('m[key]=val', 'set', 'add/change'),
     ('${m[key]}', 'get', 'lookup'),
     ('${!m[@]}', 'all keys', 'loops'),
     ('[[ -v m[k] ]]', 'key exists?', 'checks'),
     ('unset \'m[k]\'', 'delete', 'remove'),
     ('((m[$k]++))', 'count', 'tallies')],
    dict(setup=AR, cmd="cd ~/ar; declare -A ip status\nwhile read -r name addr st; do ip[$name]=$addr; status[$name]=$st; done < servers.txt\necho \"db01 is ${ip[db01]} (${status[db01]})\"\nfor n in \"${!ip[@]}\"; do echo \"$n ${ip[$n]}\"; done | sort\n[[ -v ip[app99] ]] || echo 'app99 not in inventory'", note='Keys came out in random order, so we sorted.'),
    [('qa', [
        dict(situation='The puzzle, part 3: forgetting declare -A.', cmd="ip[web01]=1; ip[db01]=2\necho \"web01=${ip[web01]} keys=${!ip[*]}\"\nunset ip; declare -A ip; ip[web01]=1; ip[db01]=2\necho \"web01=${ip[web01]} keys=$(printf '%s ' \"${!ip[@]}\" | tr ' ' '\\n' | sort | tr '\\n' ' ')\"", why='Indexed: both keys became index 0. Associative: two real keys.')]),
     ('sys', [
        dict(situation='Count HTTP status codes.', cmd="declare -A n\nfor code in 200 404 200 500 200 404; do ((n[$code]++)); done\nfor c in \"${!n[@]}\"; do echo \"$c ${n[$c]}\"; done | sort", why='A counter per key, the shell version of uniq -c.')]),
    ]
) + cmdcard_u(['reading files and command output into arrays', 'splitting a line into fields'],
               ['cmd | mapfile (subshell loses the array)', 'a=($(cmd)) with spaces or * in output'])(
    'fill', 'mapfile -t · readarray · read -ra · a=($(cmd))', 'filling arrays from files and commands',
    '<code>mapfile -t arr &lt; file</code> puts each line into one item (-t removes the newline). For commands use process substitution <code>&lt; &lt;(cmd)</code>. <code>read -ra arr &lt;&lt;&lt; "$line"</code> splits one line by IFS. <code>a=($(cmd))</code> splits at any space and expands wildcards, so avoid it for names.',
    'mapfile -t a < file   ·   mapfile -t a < <(cmd)   ·   IFS=, read -ra f <<< "$line"', 'safe',
    [('mapfile -t a < f', 'lines → items', 'files'),
     ('readarray', 'same command', 'alias'),
     ('< <(cmd)', 'from a command', 'no subshell'),
     ('read -ra a', 'split a line', 'fields'),
     ('IFS=, read -ra', 'split on commas', 'CSV'),
     ('mapfile -n 5', 'first 5 lines', 'top N'),
     ('mapfile -s 1', 'skip header', 'CSV')],
    dict(setup=AR, cmd="cd ~/ar; mapfile -t lines < servers.txt\necho \"${#lines[@]} lines; second: ${lines[1]}\"\nread -ra f <<< \"${lines[1]}\"; echo \"name=${f[0]} ip=${f[1]} state=${f[2]}\"\nIFS=, read -ra c <<< 'riya,pune,42'; echo \"${c[1]}\"", note='One line per item, then one field per item.'),
    [('dev', [
        dict(situation='Why not cmd | mapfile?', setup=AR, cmd="cd ~/ar\nls | mapfile -t a; echo \"pipe: ${#a[@]}\"\nmapfile -t a < <(ls); echo \"process substitution: ${#a[@]}\"\nb=($(ls)); echo \"a=(\\$(ls)): ${#b[@]} (split at spaces)\"", why='The pipe version filled an array in a subshell (0 here); $(ls) split the two names with spaces into four.')]),
    ]
) + undo('Arrays live only in the current shell.', [
    ('Deleted the wrong item:', 'rebuild from the source (file, command) or re-run the assignment.'),
    ('Array empty after a pipe:', 'use <code>&lt; &lt;(cmd)</code> instead of <code>cmd |</code>.'),
    ('Wrong type (indexed vs associative):', '<code>unset name</code>, then <code>declare -A name</code>.'),
    ('Inspect any array:', '<code>declare -p name</code> prints it exactly.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='declare -A m; m[]=1', meaning='An empty key is not allowed.', fix='Use a non-empty key; quote variables: m["$k"].'),
    dict(cmd='a=(1 2); echo ${a[5]:?missing}', meaning='Item 5 is unset; :? turned it into an error.', fix='Check ${#a[@]} or [[ -v a[5] ]].'),
    dict(cmd='a=(1 2); declare -A a', meaning='Cannot change an indexed array into an associative one.', fix='unset a first.'),
    dict(cmd='a=(1 2); echo ${a[-5]}', meaning='Negative index beyond the start.', fix='Use a valid index.'),
]) + qc('How do you print the keys of <code>declare -A m</code>?', '<code>"${!m[@]}"</code>.') + '''
'''
cards = cards + '</section>\n'

def lockers(k):
    items = [['web01', 'web02', 'db01'], ['web01', 'web02', 'db01', 'app01'], ['web01', None, 'db01', 'app01'], ['web01', 'db01', 'app01']][k]
    o = ''
    for i, v in enumerate(items):
        o += label_box(10 + i * 84, 50, 78, 54, [f'[{i}]', v or '(gone)'], 'card' if v is None else ('green' if (k == 1 and i == 3) else 'blue'), 8.6)
    return o
see_cmds = [['$ s=(web01 web02 db01)', '$ echo ${#s[@]}', ('3', 'out')],
            ['$ s+=(app01)', '$ echo ${#s[@]}', ('4', 'out')],
            ["$ unset 's[1]'", '$ echo ${!s[@]}', ('0 2 3', 'acc')],
            ['$ s=("${s[@]}")', '$ echo ${!s[@]}', ('0 1 2', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/ar', prompt='riya@web01:~/ar$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Create.', 'Append.', 'Delete one.', 'Renumber.'])]
behind = [lockers(k) + t(180, 150, n, 8.4, 'violet', bold=True) for k, n in enumerate(['Three lockers, 0 to 2.', 'A fourth at index 3.', 'Index 1 is empty; no shifting.', 'Rebuilt: 0 1 2 again.'])]
two = anim_two('Changing an array', 'Behind the screen: numbered lockers',
               'A terminal creating an array, appending, unsetting an item and rebuilding it.',
               'Lockers numbered from 0: append adds locker 3, unset empties locker 1 without moving the others, rebuilding renumbers.', see, behind,
               ['Create.', 'Append.', 'Unset.', 'Renumber.'],
               ['create', 'append', 'unset', 'renumber'])

def drawers(k):
    keys = [('200', 0), ('404', 0), ('500', 0)]
    counts = [[0, 0, 0], [1, 0, 0], [2, 1, 0], [3, 2, 1]][k]
    return ''.join(label_box(30 + i * 104, 50, 96, 56, [f'n[{c}]', str(counts[i])], 'green' if counts[i] else 'card', 9) for i, (c, _) in enumerate(keys))
frames = [drawers(0) + t(180, 150, 'declare -A n: empty drawers.', 8.6, 'violet', bold=True),
          drawers(1) + t(180, 150, '200 seen: ((n[200]++)).', 8.6, 'violet', bold=True),
          drawers(2) + t(180, 150, '200 again, 404 once.', 8.6, 'violet', bold=True),
          drawers(3) + t(180, 150, 'Final tally: 3, 2, 1.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'An associative array as a counter',
              'Each status code is a labelled drawer; ++ adds one.',
              '((n[$code]++))', 'Three labelled drawers 200, 404, 500 with counts that grow as codes are read.', frames,
              ['Empty.', '200.', 'More.', 'Total.'], hid='scenario-counter')

dx = dissect('Layer by layer: what bash stores',
    'Each layer has a real command and output from our build machine.', [
    dict(key='decl', name='declare -p', sub='exact contents', why='See the truth.', how='Prints a re-usable definition.', impl='Shows -a or -A.', used='Debugging.',
         cmd="a=(x 'y z'); declare -A m=([k]=v); declare -p a m"),
    dict(key='sparse', name='Sparse indices', sub='gaps allowed', why='No shifting.', how='Only set items exist.', impl='A linked list in bash.', used='unset.',
         cmd="a[0]=x; a[10]=y; echo \"count=${#a[@]} indices=${!a[*]}\""),
    dict(key='words', name='@ vs *', sub='word boundaries', why='Arguments.', how='[@] keeps items.', impl='Like $@ $*.', used='Passing on.',
         cmd="a=(one 'two three'); printf '[%s]' \"${a[@]}\"; echo; printf '[%s]' \"${a[*]}\"; echo"),
    dict(key='fn', name='Into functions', sub='nameref', why='Reuse.', how='local -n.', impl='bash 4.3+.', used='Libraries.',
         cmd="total(){ local -n arr=$1; local s=0; for v in \"${arr[@]}\"; do ((s+=v)); done; echo $s; }\nprices=(10 20 30); total prices"),
], hint='From storage to passing arrays around. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Lockers and drawers</h2>
''' + two + s1 + dx + qc('After <code>a[0]=x; a[10]=y</code>, what is <code>${#a[@]}</code>?', '2. Arrays are sparse; indices 1–9 do not exist.') + '''
</section>
'''

VAR = variations('Sixteen more array experiments, from simple lists to small tools. All were really run on our build machine.', [
    ('Indexed arrays', [
        dict(title='Days of the week by number', cmd="days=(Sun Mon Tue Wed Thu Fri Sat); echo \"day 3 is ${days[3]}, today is ${days[$(date -d 2026-11-11 +%w)]}\"", why='date +%w gives 0–6, a perfect index.'),
        dict(title='Sum and average', cmd="marks=(78 92 65 88); s=0; for m in \"${marks[@]}\"; do ((s+=m)); done; echo \"sum=$s avg=$((s / ${#marks[@]}))\"", why='Loop items; integer average.'),
        dict(title='Largest value', cmd="v=(42 7 99 15); max=${v[0]}; for x in \"${v[@]}\"; do ((x > max)) && max=$x; done; echo \"max=$max\"", why='Classic loop pattern.'),
        dict(title='Reverse an array', cmd="a=(1 2 3 4); r=(); for ((i=${#a[@]}-1; i>=0; i--)); do r+=(\"${a[i]}\"); done; echo \"${r[*]}\"", why='C-style loop from the end.'),
        dict(title='Sort an array', cmd="names=(zoya Aman riya bob); mapfile -t sorted < <(printf '%s\\n' \"${names[@]}\" | sort -f); echo \"${sorted[*]}\"", why='Bash has no sort; printf + sort + mapfile.'),
        dict(title='Remove duplicates', cmd="a=(b a c a b); mapfile -t u < <(printf '%s\\n' \"${a[@]}\" | sort -u); echo \"${u[*]} (${#u[@]} unique)\"", why='sort -u then back into an array.'),
        dict(title='Is it in the list?', cmd="allowed=(start stop status); want=stop; [[ \" ${allowed[*]} \" == *\" $want \"* ]] && echo \"$want allowed\"", why='Pad with spaces so sto does not match stop.'),
    ]),
    ('Associative arrays', [
        dict(title='A config table', cmd="declare -A cfg=([host]=db01 [port]=5432 [user]=app); echo \"psql -h ${cfg[host]} -p ${cfg[port]} -U ${cfg[user]}\"", why='Named settings instead of positional ones.'),
        dict(title='Default for a missing key', cmd="declare -A shell=([riya]=bash [aman]=zsh); for u in riya neha; do echo \"$u: ${shell[$u]:-sh (default)}\"; done", why=':- works on items too.'),
        dict(title='Word frequency', cmd="declare -A w; for x in the cat and the hat and the bat; do ((w[$x]++)); done; for k in \"${!w[@]}\"; do echo \"${w[$k]} $k\"; done | sort -rn | head -3", why='Counter, then sort by count.'),
        dict(title='Group by a field', setup=AR, cmd="cd ~/ar; declare -A by; while read -r n _ st; do by[$st]+=\"$n \"; done < servers.txt; for s in up down; do echo \"$s: ${by[$s]}\"; done", why='+= appends text to a value.'),
        dict(title='Delete a key', cmd="declare -A m=([a]=1 [b]=2 [c]=3); unset 'm[b]'; echo \"${#m[@]} keys left\"; [[ -v m[b] ]] || echo 'b gone'", why='unset with quotes.'),
    ]),
    ('Filling and passing', [
        dict(title='Skip a CSV header', cmd="printf 'name,age\\nriya,24\\naman,31\\n' > p.csv; mapfile -t -s 1 rows < p.csv; for r in \"${rows[@]}\"; do IFS=, read -r n a <<< \"$r\"; echo \"$n is $a\"; done", why='-s 1 skips the first line.'),
        dict(title='A command with arguments in an array', setup=AR, cmd="cd ~/ar; opts=(-c); target='report jan.csv'; cmd=(wc \"${opts[@]}\" \"$target\"); \"${cmd[@]}\"; declare -p cmd", why='Arguments with spaces stay whole; no eval.'),
        dict(title='Return an array from a function', cmd="get_ports(){ printf '%s\\n' 22 80 443; }; mapfile -t ports < <(get_ports); echo \"${#ports[@]} ports, last ${ports[-1]}\"", why='Functions print lines; the caller collects them.'),
        dict(title='Script arguments are an array too', setup="cd ~; cat > args.sh <<'EOF'\nargs=(\"$@\")\necho \"count=${#args[@]} first=${args[0]} rest=${args[*]:1}\"\nEOF", cmd="bash ~/args.sh one 'two words' three", why='"$@" copied into an array keeps each argument.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Arrays at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['servers', 'loops'], 'blue', 8.6), '1. Running a task on many servers',
              'hosts=(web01 web02 db01); for h in "${hosts[@]}"; do ssh "$h" uptime; done.', ['List', '*array', 'each host']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ip[host]', 'inventory'], 'green', 8.6), '2. Inventories and lookups',
    'An associative array maps host to IP, role or owner, loaded from a CSV.', ['CSV', '*declare -A', 'lookup']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['n[code]++', 'reports'], 'amber', 8.6), '3. Log counting',
    'Count HTTP codes, users or errors in pure bash when awk is not wanted.', ['Log', '*counter', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cmd=( )', 'safe'], 'red', 8.6), '4. Building commands safely',
    'rsync, curl and docker options collected in arrays instead of strings + eval.', ['Options', '*array', 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['mapfile', 'batches'], 'violet', 8.6), '5. Batch jobs',
    'mapfile the list of files to process, check the count, then loop or split into chunks.', ['List', '*mapfile', 'process']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Print each item on a line', scenario='Readable lists.', cmd="a=(apple 'big banana' cherry); printf '%s\\n' \"${a[@]}\"", explain='printf repeats per item.'),
    dict(level='b', title='Count items', scenario='Validation.', cmd="a=(x y z); echo \"${#a[@]}\"", explain='[@] for the count.'),
    dict(level='i', title='Show an array exactly', scenario='Debugging.', cmd="a=(x 'y z'); declare -p a", explain='declare -p.'),
    dict(level='i', title='Join with commas', scenario='CSV output.', cmd="a=(riya pune 24); (IFS=,; echo \"${a[*]}\")", explain='IFS first char + [*].'),
    dict(level='a', title='Lines of a command, safely', scenario='Names with spaces.', setup=AR, cmd="cd ~/ar; mapfile -t f < <(ls *.csv); echo \"${#f[@]}: ${f[1]}\"", explain='< <( ).'),
], extra=build_up('a server status report', 'Riya turns servers.txt into a summary with arrays.', AR, [
    ("cd ~/ar; mapfile -t rows < servers.txt; echo \"${#rows[@]} servers\"", '1. Read the file.'),
    ("cd ~/ar; mapfile -t rows < servers.txt; declare -A st; for r in \"${rows[@]}\"; do read -r n _ s <<< \"$r\"; st[$n]=$s; done; declare -p st | tr ' ' '\\n' | grep -c '\\['", '2. Map name → status.'),
    ("cd ~/ar; mapfile -t rows < servers.txt; declare -A st; for r in \"${rows[@]}\"; do read -r n _ s <<< \"$r\"; st[$n]=$s; done; down=(); for n in \"${!st[@]}\"; do [ \"${st[$n]}\" = down ] && down+=(\"$n\"); done; echo \"down: ${down[*]:-none}\"", '3. Collect the ones that are down.'),
    ("cd ~/ar; mapfile -t rows < servers.txt; declare -A st; for r in \"${rows[@]}\"; do read -r n _ s <<< \"$r\"; st[$n]=$s; done; down=(); for n in \"${!st[@]}\"; do [ \"${st[$n]}\" = down ] && down+=(\"$n\"); done; echo \"${#down[@]} of ${#st[@]} down: ${down[*]:-none}\"", '4. A one-line summary.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Ordered list', 'indexed array', 'Simple.', 'server1, server2 variables.'),
    ('Lookup by name', 'declare -A', 'Direct.', 'grep in a loop.'),
    ('Big data files', 'awk', 'Fast, has arrays too.', 'bash loops over 1M lines.'),
    ('Names with spaces', '"${a[@]}"', 'Stays whole.', 'a string of names.'),
    ('Portable /bin/sh', 'set -- a b c; "$@"', 'Works in dash.', 'bash arrays in sh scripts.'),
]) + keys('Handy forms.', [
    ('"${a[@]}"', 'every item', 'loops'),
    ('${#a[@]}', 'count', 'checks'),
    ('${!a[@]}', 'indices/keys', 'loops'),
    ('a+=(x)', 'append', 'collect'),
    ('declare -p a', 'inspect', 'debug'),
    ('mapfile -t a < <(cmd)', 'fill', 'commands'),
]) + scriptit('inventory.sh', 'Read servers.txt into associative arrays, then print a sorted table, the number of servers that are up, and the IP of a host given as an argument.',
'''mkdir -p ~/ar && cd ~/ar || exit 1
[ -f servers.txt ] || printf 'web01 10.0.0.11 up\\nweb02 10.0.0.12 down\\ndb01 10.0.0.21 up\\n' > servers.txt
declare -A ip status
while read -r name addr st; do ip[$name]=$addr; status[$name]=$st; done < servers.txt
printf '%-8s %-12s %s\\n' HOST IP STATE
for h in $(printf '%s\\n' "${!ip[@]}" | sort); do printf '%-8s %-12s %s\\n' "$h" "${ip[$h]}" "${status[$h]}"; done
up=0; for h in "${!status[@]}"; do [ "${status[$h]}" = up ] && ((up++)); done
echo "up: $up of ${#ip[@]}"
want=${1:-db01}
[[ -v ip[$want] ]] && echo "$want -> ${ip[$want]}" || echo "$want not found"''',
'<p>Run without an argument, so it looks up db01.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>${files[@]}</code> without quotes splits every item at spaces, so two names became four words. Use <code>"${files[@]}"</code>. <b>2.</b> <code>${#files}</code> means the length of <code>${files[0]}</code> (“report jan.csv” has 14 characters); the count is <code>${#files[@]}</code>. <b>3.</b> Without <code>declare -A</code>, <code>ip</code> is an indexed array and the keys are arithmetic: web01 and db01 are unset variables = 0, so both assignments wrote index 0 and the last one (2) won.') + qc('What does <code>"${a[*]}"</code> give with IFS=,?', 'All items joined into one word with commas.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/ar ~/args.sh ~/p.csv', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-shell-variables-and-environment-variables-env/">Lesson 12.1</a> (variables) and <a href="../09-loops-for-while-until-break-continue/">Lesson 12.9</a> (loops).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
