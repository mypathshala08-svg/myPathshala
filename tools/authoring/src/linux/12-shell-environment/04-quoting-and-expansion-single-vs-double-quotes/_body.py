import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

QF = r"""rm -rf ~/qt; mkdir -p ~/qt/in; cd ~/qt
touch 'in/my report.txt' in/a.txt in/b.txt 'in/-n'"""

HOOK = hook('Riya’s backup script works for months. Then a colleague saves a file called <code>Q3 report.xlsx</code>, with a space, and the script fails with “No such file: Q3” and “No such file: report.xlsx”. Another script prints a price as <code>Price: 5</code> instead of <code>Price: $5</code>. A third one, meant to delete <code>$dir/*</code>, nearly deletes <code>/*</code> because <code>$dir</code> was empty. All three are <b>quoting</b> bugs. Before running any command, the shell rewrites your line: it expands <code>$variables</code>, <code>$(commands)</code>, <code>*</code> wildcards and <code>~</code>, then splits the result into words. Quotes decide which of those steps happen.',
    ['explain exactly what single quotes, double quotes, backslash and $\'…\' protect, and what they do not',
     'avoid word splitting and globbing bugs by quoting variables: <code>"$var"</code>, <code>"$@"</code>, <code>"$(cmd)"</code>',
     'know the difference between <code>$*</code>, <code>"$*"</code>, <code>$@</code> and <code>"$@"</code>, checked with real runs',
     'combine quotes, print quotes inside quotes, and debug with <code>printf \'[%s]\\n\'</code> and <code>set -x</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the file with a space'),
    ('decide', 'Which quote when?', 2, 'the quick chart'),
    ('definition', 'Quoting', 6, 'simple meaning + 4 depths'),
    ('types', 'Four kinds of quoting', 5, 'side by side'),
    ('commands', 'Quoting by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'word splitting'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'fix a script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which quote? (decide in 5 seconds)', [
    ('A variable or $(command)', '"$var"   "$(cmd)"', 'almost always double quotes'),
    ('Text exactly as typed ($ * ! \\ stay)', "'text'", 'single quotes'),
    ('All script arguments, unchanged', '"$@"', 'never $* or $@ alone'),
    ('One special character only', '\\$   \\"   \\ (space)', 'backslash'),
    ('A single quote inside text', "\"it's\"   or   'it'\\''s'", 'switch quote type'),
    ('Tab, newline, escape codes', "$'a\\tb\\n'", 'ANSI-C quoting'),
    ('Let the wildcard work', '*.txt   (no quotes)', 'quotes stop globbing'),
    ('See what the shell made of it', "printf '[%s]\\n' $x", 'one line per word'),
])

cmap = concept_map(
    [('12.1', 'Variables', '$name'), ('3.4', 'Wildcards', '* ? [ ]'), ('5.4', '$( )', 'command substitution')],
    ['what the shell expands before running', 'single quotes: nothing expands', 'double quotes: only $, `, \\ expand', 'backslash and $\'…\'', 'word splitting, globbing, "$@" vs $*'],
    [('12.7', 'Script input', '$1, $#, read'), ('12.11', 'Expansion order', 'all seven steps'), ('6.4', 'sed', 'quoting patterns'), ('12.6', 'set -x', 'see expansions')],
    'The shell rewrites every line before running it. Single quotes stop everything, double quotes stop everything except $, ` and \\. Quote every variable.')

sc = (term(20, 14, 316, 156, ['$ f="Q3 report.xlsx"', '$ cp $f backup/', ("cp: cannot stat 'Q3'", 'err'), ("cp: cannot stat 'report.xlsx'", 'err'), '$ cp "$f" backup/', '$ echo \'$HOME\' "$HOME"', ('$HOME /home/riya', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Quotes decide:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• \'…\' = exactly this', '• "…" = expand $ only', '• no quotes =', '  split + wildcards', '• quote every $var'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The file with a space</h2>
  <div class="story">
''' + puzzle('A clean-up script contains <code>rm -rf $dir/*</code>. Someone runs it before setting <code>dir</code>. What command does the shell actually run, and which two small changes make the line safe?') + '''
    <p class="narration">A file name with a space breaks a copy command, until Riya adds two quote marks.</p>
''' + scene('A terminal: cp $f fails because the name with a space was split into two words; cp "$f" works; single quotes print $HOME literally, double quotes expand it.', sc,
            'Without quotes, a value with a space becomes <tspan font-weight="700" class="s-acc">two words</tspan>.') + '''
K> But the variable had the full name in it!
A> Yes. The problem is what happens after the shell puts the value in: without quotes, it <b>splits</b> the result at spaces into separate words and treats any <code>*</code> as a wildcard. So <code>cp $f backup/</code> became <code>cp Q3 report.xlsx backup/</code>: three arguments.
R> And with double quotes?
A> <code>"$f"</code> still gets the value, but the result stays <b>one word</b>. That is the rule you will repeat for the rest of your Linux life: quote your variables. Today you will see exactly what each kind of quote protects.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Three envelopes: a sealed envelope (single quotes) arrives exactly as written; a window envelope (double quotes) lets the post office fill in the address ($var) but keeps it one letter; no envelope at all lets the pages be split and shuffled.">'
       + label_box(14, 20, 190, 110, ["'single quotes'", 'a sealed envelope:', 'nothing is changed', "'$HOME' → $HOME"], 'green', 8.6)
       + label_box(224, 20, 190, 110, ['"double quotes"', 'window envelope:', '$var filled in,', 'still ONE item'], 'blue', 8.6)
       + label_box(434, 20, 192, 110, ['no quotes', 'loose pages:', 'split at spaces,', '* becomes file names'], 'red', 8.6)
       + t(320, 160, 'Most bugs come from loose pages: quote your variables.', 9.6, 'ink2')
       + t(320, 182, 'Need $ literally? Single quotes or \\$.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Quoting at four depths', [
    ('v', 'No jargon: envelopes', '      <p>How your text travels to the command.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>echo "Hello $USER"</code>: double quotes, the variable is filled in.</li>
        <li><code>echo 'Cost: $5'</code>: single quotes, printed exactly.</li>
        <li><code>cp "$file" "$dest"</code>: quote every variable that holds a name.</li>
        <li><code>echo "She said \\"hi\\""</code>: backslash before a quote inside the same kind of quotes.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li><b>Single quotes</b>: everything literal; a single quote cannot appear inside, not even as <code>\\'</code>.</li>
        <li><b>Double quotes</b>: <code>$var</code>, <code>${…}</code>, <code>$(…)</code>, <code>`…`</code>, <code>$((…))</code> and <code>\\</code> before <code>$ ` " \\</code> still work; no word splitting, no wildcards, no <code>~</code>.</li>
        <li><b>Backslash</b> outside quotes protects the next character (a space, <code>*</code>, <code>$</code>).</li>
        <li><code>$'…'</code> (ANSI-C) understands <code>\\n \\t \\e \\'</code>.</li>
        <li><code>"$@"</code> gives each argument as its own word; <code>"$*"</code> joins them into one; unquoted <code>$@</code>/<code>$*</code> are split again at spaces.</li>
      </ul>'''),
    ('a', 'Behind the screen: the order of expansions', '''      <ul>
        <li>For each line bash does: brace expansion → tilde → parameter, arithmetic and command substitution (left to right) → <b>word splitting</b> → <b>pathname expansion (globbing)</b> → quote removal. Full order in Lesson 12.11.</li>
        <li>Word splitting uses <code>IFS</code> (space, tab, newline by default) and happens only on the <b>results of unquoted expansions</b>, never on text you typed.</li>
        <li>Quote removal is last: the program never sees your quotes. <code>echo "a"</code> and <code>echo a</code> pass the same argument.</li>
        <li>History expansion (<code>!</code>) runs before all of this in interactive shells, even inside double quotes (Lesson 12.3).</li>
        <li><code>[[ … ]]</code> does no word splitting or globbing on variables; <code>[ … ]</code> is an ordinary command, so it does (Lesson 12.8).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Quoting and expansion</h2>
''' + def_block(
    '<b>Quoting</b> removes the special meaning of characters to the shell. <b>Single quotes</b> preserve every character literally. <b>Double quotes</b> preserve everything except <code>$</code>, <code>`</code> and <code>\\</code> (so variable, command and arithmetic substitution still happen) and prevent word splitting and pathname expansion. A <b>backslash</b> quotes the single next character. <b>Expansion</b> is the rewriting the shell does to an unquoted line before running it.',
    'Single quotes: exactly as typed. Double quotes: fill in $, keep it one piece.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Expansion', 'The shell rewriting your line.'),
    ('Word splitting', 'Cutting results at spaces into words.'),
    ('Globbing', 'Turning * ? [ ] into file names.'),
    ('Command substitution', '$(cmd) replaced by its output.'),
    ('IFS', 'Characters used to split words.'),
    ('Escape', 'A backslash protecting one character.'),
    ('Literal', 'Taken exactly as written.'),
    ('Quote removal', 'Quotes vanish before the command runs.'),
]) + '\n' + names('Where the names come from.', [
    ("' '", 'strong quotes', 'Nothing inside expands.'),
    ('" "', 'weak quotes', '$ ` \\ still work.'),
    ('\\', 'escape', 'Protects one character.'),
    ("$' '", 'ANSI-C quoting', 'Escapes like C.'),
    ('$( )', 'command substitution', 'Newer form of ` `.'),
    ('IFS', 'internal field separator', 'Space, tab, newline.'),
    ('glob', 'global', 'Unix V1 /etc/glob.'),
    ('"$@"', 'all arguments', 'Each kept whole.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Literal', "<code>'$HOME'</code>"),
    ('Expanded', '<code>"$HOME"</code>'),
    ('One char', '<code>\\$</code>'),
    ('Tab', "<code>$'\\t'</code>"),
    ('All args', '<code>"$@"</code>'),
    ('See words', "<code>printf '[%s]\\n'</code>"),
]) + '\n' + lv + didyou('Quotes are for the shell, not for the program. When you type <code>grep "error" log.txt</code>, grep receives <code>error</code> without quotes. That is why <code>grep "my error"</code> works: the quotes only told the shell to keep the two words together.') + '''
EXAM> “Difference between single and double quotes in shell?” → Single quotes preserve the literal value of every character; double quotes allow $, ` and \\ (variable, command and arithmetic substitution) but still prevent word splitting and globbing.
''' + qc('What does <code>echo "Today is $(date +%A)"</code> print, and what does the same with single quotes print?', 'Double: Today is Wednesday (the command runs). Single: Today is $(date +%A), literally.') + mistake('echo "Using \\"\\$@\\": \\"$@\\""   →   claimed output:  "arg1" "arg2"',
    'Real output: Using "$@": "arg1 arg2"',
    'Inside one double-quoted string, $@ is joined with spaces like $*. The difference between "$@" and "$*" only shows when they are used as separate arguments (a for loop, a command): see the $@ card below. Checked on our build machine.') + mistake('“Without double quotes, $* expands to a single string”',
    'Unquoted $* and $@ are split again at spaces into separate words; only "$*" is one string',
    'Real run with the arguments "a b" and c: for x in $* gives three words a, b, c; for x in "$*" gives one: a b c; for x in "$@" gives two: a b and c.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Four kinds of quoting, and what each one stops</h2>
''' + table(['Inside…', 'no quotes', '"double"', "'single'", '\\ backslash'], [
    ['$var, ${var}', 'expanded, then split', 'expanded, one word', 'literal', '\\$ = literal $'],
    ['$(cmd), `cmd`', 'run, then split', 'run, one word', 'literal', '—'],
    ['$((1+2))', '3', '3', 'literal', '—'],
    ['* ? [ ]', 'file names', 'literal', 'literal', '\\* = literal'],
    ['~', 'home folder', 'literal', 'literal', '—'],
    ['space', 'separates words', 'kept', 'kept', '\\ = kept'],
    ['! (interactive)', 'history', 'history!', 'literal', '\\! = literal'],
    ['" inside', 'starts quoting', '\\" needed', 'literal', '\\"'],
    ["' inside", 'starts quoting', 'literal', 'impossible', "\\'"],
], minw=600) + table(['Form', 'With arguments "a b" and c', 'Words'], [
    ['<code>$*</code>', 'a | b | c', '3'],
    ['<code>$@</code>', 'a | b | c', '3'],
    ['<code>"$*"</code>', 'a b c', '1'],
    ['<code>"$@"</code>', 'a b | c', '2 (correct)'],
], minw=380) + table(['', '<code>$( )</code>', '<code>` `</code> (backticks)'], [
    ['Nesting', 'easy: <code>$(dirname $(pwd))</code>', 'needs escaping'],
    ['Readability', 'clear', 'looks like quotes'],
    ['Use', 'always', 'old scripts only'],
], minw=380) + qc('How do you print <code>It\'s $5</code> exactly?', "<code>echo \"It's \\$5\"</code> or <code>echo 'It'\\''s $5'</code>.") + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Quoting explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/qt</code>, with a folder <code>in/</code> holding <code>my report.txt</code> (a space), <code>a.txt</code>, <code>b.txt</code> and a nasty file called <code>-n</code>. We use <code>printf '[%s]\\n' …</code> often: it prints each word it receives in brackets, one per line, so you can see what the shell made of a line.</p>
''' + cmdcard_u(['any variable that holds a file name, path or user input', 'command substitution results'],
               ['when you really want splitting or globbing (rare; use arrays instead)'])(
    'double', '"double quotes"', 'expand, keep one word',
    'Inside double quotes, <code>$var</code>, <code>${var}</code>, <code>$(cmd)</code>, <code>$((…))</code> and backticks are expanded; spaces, <code>*</code>, <code>?</code>, <code>~</code> and single quotes are kept literally. Use <code>\\$</code>, <code>\\"</code>, <code>\\\\</code> and <code>\\`</code> for the four special characters.',
    'cmd "$var"   ·   "$(cmd)"   ·   "text with \\"quotes\\" and \\$"', 'safe',
    [('"$f"', 'value as ONE word', 'file names'),
     ('"${f}_old"', 'name ends at }', 'joining'),
     ('"$(date +%F)"', 'command output', 'dates'),
     ('"$((a+b))"', 'arithmetic', 'numbers'),
     ('\\"  \\$', 'literal " and $', 'inside "…"'),
     ('"~"', 'NOT your home', 'use $HOME')],
    dict(setup=QF, cmd="cd ~/qt; f='in/my report.txt'\nprintf '[%s]\\n' $f\nprintf '[%s]\\n' \"$f\"\nls -l \"$f\" | cut -c1-10", note='Unquoted: two words. Quoted: one. That is the whole story bug.'),
    [('dev', [
        dict(situation='Messages with variables, commands and real quotes.', cmd="user=Riya; n=3\necho \"Hello $user, you have $n new files ($(date +%Y)).\"\necho \"She said \\\"ok\\\" and paid \\$5\"",
             why='Double quotes let $ work, and \\ protects the characters that would otherwise be special inside them.')]),
     ('sys', [
        dict(situation='A value with * inside.', setup=QF, cmd="cd ~/qt/in; pattern='*.txt'\necho $pattern\necho \"$pattern\"",
             why='Unquoted, the * in the value became file names. Quoted, it stays the pattern. Important for grep and find arguments.')]),
    ],
    anat=anatomy([('cp', 'cmd', 'copy'), ('"$f"', 'arg', 'one word'), ('"$dest/"', 'arg', 'one word')], 'Rule: if it starts with $, put it in double quotes.')
) + cmdcard_u(['text that must not change: prices, regex, awk and sed programs', 'commands to run later (ssh, cron)'],
               ['when you need a variable inside (use double quotes)'])(
    'single', "'single quotes'", 'exactly as typed',
    'Everything between single quotes is literal: <code>$</code>, <code>*</code>, <code>\\</code>, <code>!</code>, <code>"</code>. There is no way to put a single quote inside; close, add <code>\\\'</code>, and reopen: <code>\'it\'\\\'\'s\'</code>.',
    "echo 'text'   ·   awk '{print $1}'   ·   'it'\\''s'", 'safe',
    [("'$HOME'", 'prints $HOME', 'literal'),
     ("awk '{print $2}'", 'awk sees $2', 'programs'),
     ("grep 'a.*b'", 'regex untouched', 'patterns'),
     ("'it'\\''s'", "it's", 'quote inside'),
     ("ssh h 'echo $HOME'", 'expands on the server', 'remote')],
    dict(cmd="echo 'Cost: $5 * 2 = $10, path ~/x, not $(date)'\necho 'it'\\''s' \"it's\"\nawk 'BEGIN { x = 7; print \"x is\", x }'", note='Nothing inside single quotes changed.'),
    [('devops', [
        dict(situation='Expand here or on the other side?', cmd="bash -c \"echo here: $USER\"\nbash -c 'echo inside: $USER'\nUSER=other bash -c 'echo inside with another value: $USER'",
             why='Double quotes expand in YOUR shell before the inner shell runs; single quotes pass $USER through to be expanded by the inner shell (or remote server, with ssh).')]),
    ]
) + mistake("rm -rf $dir/*", 'rm -rf "${dir:?dir is empty}"/*   (and set -u)',
            'If dir is empty, the line becomes rm -rf /*. ${dir:?msg} stops with an error when dir is empty or unset; quotes keep names with spaces safe. Lesson 12.6 adds set -u.') + cmdcard_u(['one special character', 'file names with spaces typed by hand', 'tabs and newlines in text'],
               ['long strings full of backslashes (use single quotes)'])(
    'escape', "\\ backslash · $'…'", 'escape one character',
    'Outside quotes a backslash protects the next character: <code>my\\ file.txt</code>, <code>\\*</code>, <code>\\$</code>. At the end of a line it joins the next line. <code>$\'…\'</code> understands C escapes: <code>\\n</code>, <code>\\t</code>, <code>\\\'</code>, <code>\\\\</code>, <code>\\e</code>.',
    "cat my\\ file.txt   ·   echo \\$HOME   ·   printf %s $'a\\tb'", 'safe',
    [('\\ (space)', 'keep the space', 'names'),
     ('\\$  \\*  \\!', 'literal character', 'one-offs'),
     ('\\ at line end', 'continue the line', 'long commands'),
     ("$'\\t'  $'\\n'", 'tab, newline', 'IFS, printf'),
     ("$'it\\'s'", 'quote inside', 'ANSI-C')],
    dict(setup=QF, cmd="cd ~/qt\nls in/my\\ report.txt\necho \\$HOME \\* \"\\$HOME\"\necho $'col1\\tcol2' | cat -A\nls -l \\\n   in/a.txt | cut -c1-10", note='cat -A shows the tab as ^I. The \\ at the end of a line continues the command.'),
    [('qa', [
        dict(situation='A file called -n: quotes do not help, -- does.', setup=QF, cmd="cd ~/qt/in\nls \"-n\" 2>&1 | head -1\nls -- -n\nls ./-n",
             why='Quotes are removed before ls sees the word, so "-n" is still an option. Use -- (end of options) or ./-n.')]),
    ]
) + cmdcard_u(['passing all of a script’s arguments on', 'loops over arguments'],
               ['$* and unquoted $@ (they break arguments with spaces)'])(
    'args', '"$@" vs "$*" vs $@', 'all the arguments',
    '<code>"$@"</code> expands to each positional parameter as a separate word, exactly as given. <code>"$*"</code> joins them into one word separated by the first character of IFS. Unquoted <code>$@</code> and <code>$*</code> are split again at every space.',
    'for a in "$@"; do …; done   ·   other_cmd "$@"', 'safe',
    [('"$@"', 'each argument whole', 'almost always'),
     ('"$*"', 'all in one string', 'messages, logs'),
     ('$@ / $*', 'split again', 'avoid'),
     ('$#', 'how many', 'Lesson 12.7'),
     ('IFS=,; echo "$*"', 'join with commas', 'CSV')],
    dict(cmd="set -- 'Q3 report.xlsx' notes.txt\necho \"count: $#\"\nprintf '[%s] ' $@; echo '  <- $@'\nprintf '[%s] ' \"$@\"; echo '  <- \"$@\"'\nprintf '[%s] ' \"$*\"; echo '  <- \"$*\"'", note='set -- sets $1, $2 as if a script was called with these two arguments. Only "$@" keeps exactly two.'),
    [('devops', [
        dict(situation='A wrapper script that passes everything on.', cmd="printf 'printf \"[%%s]\\\\n\" \"$@\"\\n' > inner.sh\nprintf 'echo \"wrapper got $# args\"\\nbash inner.sh \"$@\"\\n' > wrap.sh\nbash wrap.sh 'two words' one",
             why='"$@" is the only form that forwards arguments with spaces intact. Every wrapper, alias replacement and Docker entrypoint uses it.')]),
     ('dev', [
        dict(situation='Join arguments with commas.', cmd="set -- apple banana 'dragon fruit'\n( IFS=,; echo \"$*\" )",
             why='"$*" joins with the first character of IFS; the ( ) keeps the IFS change local.')]),
    ]
) + undo('Quoting mistakes are fixed by quoting; the damage is in what the command did.', [
    ('A loop split a name with spaces:', 'quote the variable; for lists of names use arrays or <code>find -print0 | xargs -0</code>.'),
    ('An empty variable widened a command (rm, chmod):', 'use <code>${var:?}</code> and <code>set -u</code>; test with <code>echo</code> first.'),
    ('The prompt shows <code>&gt;</code> and waits:', 'an unclosed quote; press <kbd>Ctrl</kbd>+<kbd>C</kbd> and retype.'),
    ('Not sure what the shell made of a line:', "<code>printf '[%s]\\n' …</code> or <code>set -x</code> (Lesson 12.6)."),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='f="my report.txt"; cat $f', setup=QF + '; cd ~/qt/in', meaning='Unquoted: split into my and report.txt.', fix='<code>cat "$f"</code>.'),
    dict(cmd="echo 'it's'", meaning='The quote in it\'s closed the string; the next one opens a new one that never ends.', fix="<code>\"it's\"</code> or <code>'it'\\''s'</code>."),
    dict(cmd='[ $name = Riya ]', meaning='Empty $name leaves [ = Riya ]: too few words.', fix='<code>[ "$name" = Riya ]</code>.'),
    dict(cmd='echo "${HOME"', meaning='Missing } in a ${ } expansion.', fix='<code>"${HOME}"</code>.'),
]) + qc('Why does <code>[ $name = Riya ]</code> fail when name is empty, but <code>[ "$name" = Riya ]</code> works?', 'Unquoted, the empty value disappears and [ sees “= Riya”. Quoted, it sees an empty string "" as the first word.') + '''
'''
cards = cards + '</section>\n'

def ws(k):
    o = label_box(14, 20, 332, 30, ['cp $f backup/      f = “Q3 report.xlsx”'], 'blue', 8)
    if k >= 1:
        o += label_box(14, 58, 332, 30, ['after $ expansion:  cp Q3 report.xlsx backup/'], 'amber', 8)
    if k >= 2:
        o += ''.join(label_box(14 + i * 84, 100, 78, 30, [w], 'red' if i in (1, 2) else 'card', 8) for i, w in enumerate(['cp', 'Q3', 'report.xlsx', 'backup/']))
    if k == 3:
        o += ''.join(label_box(14 + i * 112, 142, 104, 30, [w], 'green' if i == 1 else 'card', 8) for i, w in enumerate(['cp', 'Q3 report.xlsx', 'backup/']))
    return o
see_cmds = [['$ cp $f backup/'], ['$ cp $f backup/'], ['$ cp $f backup/', ("cp: cannot stat 'Q3'", 'err'), ("cp: cannot stat 'report.xlsx'", 'err')], ['$ cp "$f" backup/', ('(copied)', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Looks fine…', 'the value goes in…', '…and it is split: 4 words.', 'Quoted: 3 words.'])]
behind = [ws(k) + t(180, 196, n, 8.4, 'violet', bold=True) for k, n in enumerate(['The line as typed.', 'Step 1: $f replaced by its value.', 'Step 2: unquoted result split at the space.', 'With "$f": the value stays one word.'])]
two = anim_two('Word splitting', 'Behind the screen: from one line to words',
               'A terminal: cp $f fails with two cannot-stat errors; cp "$f" works.',
               'The line is expanded, then split into words; unquoted, the file name becomes two words; quoted, it stays one.', see, behind,
               ['Typed.', 'Expanded.', 'Split.', 'Quoted.'],
               ['one line', '$f → value', '4 words', '3 words'])

def quo(k):
    rows = [("'$HOME *'", '$HOME *', 'green'), ('"$HOME *"', '/home/riya *', 'blue'), ('$HOME *', '/home/riya a.txt b.txt', 'red'), ('\\$HOME \\*', '$HOME *', 'violet')]
    o = ''
    for i, (a, b, tn) in enumerate(rows[:k + 1]):
        o += label_box(14, 18 + i * 40, 150, 32, [a], tn, 8) + arrow(164, 34 + i * 40, 190, 34 + i * 40) + label_box(190, 18 + i * 40, 160, 32, [b], 'card', 8)
    return o
frames = [quo(0) + t(180, 190, 'Single: nothing changes.', 8.6, 'green', bold=True),
          quo(1) + t(180, 190, 'Double: $ works, * stays.', 8.6, 'blue', bold=True),
          quo(2) + t(180, 190, 'None: $ works and * becomes files.', 8.6, 'red', bold=True),
          quo(3) + t(180, 190, 'Backslash: one character at a time.', 8.6, 'violet', bold=True)]
s1 = anim_one('Animated example', 'One text, four kinds of quoting',
              'The same characters, four results.',
              'quoting', 'The text $HOME * with single quotes, double quotes, no quotes and backslashes, and what echo prints for each.', frames,
              ['Single.', 'Double.', 'None.', 'Backslash.'], hid='scenario-quotes')

dx = dissect('Layer by layer: what happens to one line',
    'Each layer has a real command and output from our build machine.', [
    dict(key='typed', name='What you type', sub='with quotes', why='Your intention.', how='Characters.', impl='Read by bash.', used='Every line.',
         setup=QF, cmd="cd ~/qt/in; f='my report.txt'; printf '[%s]\\n' \"$f\" '$f' *.txt"),
    dict(key='expand', name='Expansion', sub='$, $( ), $(( ))', why='Fill in values.', how='Left to right.', impl='Not inside \' \'.', used='Variables.',
         cmd="n=4; printf '[%s]\\n' \"$n\" \"$((n*2))\" \"$(echo hi)\""),
    dict(key='split', name='Word splitting', sub='IFS', why='Turn results into words.', how='Unquoted results only.', impl='IFS=space tab newline.', used='The bug source.',
         cmd="v='a b  c'; printf '[%s]\\n' $v; IFS=,; w='x,y'; printf '[%s]\\n' $w"),
    dict(key='glob', name='Globbing', sub='* ? [ ]', why='File names.', how='Unquoted only.', impl='Sorted matches.', used='ls *.txt.',
         setup=QF, cmd="cd ~/qt/in; printf '[%s]\\n' *.txt '*.txt' nomatch*"),
    dict(key='removal', name='Quote removal', sub='last step', why='Program never sees quotes.', how='Removed.', impl='Arguments.', used='Always.',
         cmd="printf '[%s]\\n' \"a\" 'b' c\\ d"),
], hint='From your line to the words the program receives. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Word splitting, and four kinds of quoting</h2>
''' + two + s1 + dx + qc('A pattern that matches no file, like <code>nomatch*</code>, unquoted: what does the program receive?', 'The text nomatch* itself (bash default). With shopt -s nullglob it would vanish; with failglob it is an error.') + '''
</section>
'''

VAR = variations('Variations on quoting, each with printf \x27[%s]\\n\x27 so you can count the words the program receives.', [
    ('Same text, different quotes', [
        dict(title='Five ways to write one line', cmd="who=Riya\nprintf '[%s]\\n' \"Hi $who\" 'Hi $who' Hi\\ $who \"Hi \"$who \"Hi \\$who\"", why='Count the brackets: all one word, but $who is expanded in only three.'),
        dict(title='Quotes can be glued', cmd="a=one\nprintf '[%s]\\n' 'single'\"double $a\"plain", why='Pieces next to each other with no space form one word.'),
        dict(title='Nested command in quotes', cmd="printf '[%s]\\n' \"Folder: $(basename \"$(pwd)\")\"", why='Inside $( ) you can use quotes again; they start fresh.'),
    ]),
    ('Splitting and globbing', [
        dict(title='A list in a variable vs an array', cmd="list='a.txt b c.txt'\nprintf '[%s]\\n' $list\narr=('a.txt' 'b c.txt')\nprintf '<%s>\\n' \"${arr[@]}\"", why='A string can only be split at spaces; an array keeps items with spaces intact.'),
        dict(title='Changing IFS for one read', cmd="line='riya:x:1000:1000:Riya Sharma:/home/riya:/bin/bash'\nIFS=: read -r user _ uid _ name _ <<< \"$line\"\necho \"$user ($uid) is $name\"", why='IFS=: for read only: the /etc/passwd fields split at colons.'),
        dict(title='Glob with no match', cmd="shopt -s nullglob\nfiles=(*.nomatch); echo \"${#files[@]} files\"\nshopt -u nullglob\nfiles=(*.nomatch); echo \"${files[0]}\"", why='Default: the pattern stays as text; nullglob: it disappears.'),
    ]),
    ('$@ and $* in action', [
        dict(title='Count arguments three ways', cmd="set -- 'a b' c\nn1=$(printf '%s\\n' $@ | wc -l)\nn2=$(printf '%s\\n' \"$@\" | wc -l)\nn3=$(printf '%s\\n' \"$*\" | wc -l)\necho \"\\$@=$n1  \\\"\\$@\\\"=$n2  \\\"\\$*\\\"=$n3\"", why='3, 2 and 1 lines: only "$@" matches the real number of arguments.'),
        dict(title='Your notes’ example, run for real', cmd="printf 'echo \"Using \\\\$*: $*\"\\necho \"Using \\\\\"\\\\$@\\\\\": \\\\\"$@\\\\\"\"\\n' > notes.sh\ncat notes.sh; bash notes.sh arg1 arg2", why='Inside one double-quoted echo string both are joined with spaces: the output is "arg1 arg2", not "arg1" "arg2".'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Quoting at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['"$file"', 'backups'], 'blue', 8.6), '1. Backup and file scripts',
              'Every path variable is quoted, because users create file names with spaces, brackets and dashes.', ['Name', '*"$f"', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ["awk '…'", 'data'], 'green', 8.6), '2. Data pipelines',
    "awk, sed and jq programs go in single quotes so $1 and $field reach the tool, not the shell.", ['Program', "*'...'", 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['"$@"', 'wrappers'], 'amber', 8.6), '3. Wrappers and entrypoints',
    'Docker entrypoints and tool wrappers end with exec "$@" to pass every argument unchanged.', ['Wrap', '*"$@"', 'exec']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['${dir:?}', 'safety'], 'red', 8.6), '4. Safety in production',
    'Famous outages were caused by rm -rf $DIR/ with an empty DIR. Quoting plus ${VAR:?} stops it.', ['Check', '*${v:?}', 'stop']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ["ssh h '…'", 'remote'], 'violet', 8.6), '5. Remote commands',
    'Single quotes send the command to the server unexpanded; double quotes expand locally first.', ['Local', "*'...'", 'remote']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='See the words', scenario='What did the shell make of it?', cmd="x='one two'; printf '[%s]\\n' $x \"$x\"", explain="printf '[%s]'."),
    dict(level='b', title='Literal dollar', scenario='Prices.', cmd="echo \"Total: \\$5\"; echo 'Total: $5'", explain='\\$ or single quotes.'),
    dict(level='i', title='Loop over names with spaces', scenario='Files safely.', setup=QF, cmd="cd ~/qt/in; for f in *.txt; do echo \"<$f>\"; done", explain='Glob, then "$f".'),
    dict(level='i', title='Newline in a string', scenario='Multi-line message.', cmd="msg=$'line1\\nline2'; echo \"$msg\"", explain="$'…'."),
    dict(level='a', title='Guard an empty variable', scenario='Before rm.', cmd="dir=''; ( : \"${dir:?is empty, refusing}\" ) 2>&1 | sed 's/.*line [0-9]*: //'", explain='${var:?}.'),
], extra=build_up('fixing a fragile script', 'Riya fixes three quoting bugs in a copy script, one at a time.', QF + "; mkdir -p ~/qt/out", [
    ("cd ~/qt; for f in $(ls in); do echo \"word: $f\"; done | head -3", '1. The bug: $(ls) is split at spaces.'),
    ('cd ~/qt; for f in in/*; do echo "file: $f"; done | head -3', '2. Fix: let the glob produce the names.'),
    ('cd ~/qt; for f in in/*.txt; do cp -- "$f" out/; done; ls out', '3. Quote "$f" and use -- for names like -n.'),
], cumulative=True)) + VAR + which('Choosing the right quoting.', [
    ('A variable', '"$var"', 'One word, value filled in.', '$var unquoted.'),
    ('Text with $ * !', "'text'", 'Nothing changes.', '"text" (still expands $).'),
    ('All arguments', '"$@"', 'Each kept whole.', '$* or $@.'),
    ('One character', '\\x', 'Short.', 'Quoting a whole line for it.'),
    ('Tab or newline', "$'\\t'", 'Real control characters.', '"\\t" (two characters).'),
    ('Wildcards should work', 'no quotes', 'Globbing.', '"*.txt".'),
]) + keys('Handy forms.', [
    ('"$var"', 'safe value', 'always'),
    ('"${var:?msg}"', 'fail if empty', 'rm, chmod'),
    ('"${var:-default}"', 'default value', 'options'),
    ("'it'\\''s'", 'quote in single', 'tricky'),
    ("printf '[%s]\\n' …", 'see words', 'debug'),
    ('cmd -- "$f"', 'name starting with -', 'safety'),
]) + scriptit('safe-copy.sh', 'A copy tool that survives any file name: spaces, leading dashes, asterisks. It refuses an empty destination and passes all names with "$@".',
'''dest=${DEST:?set DEST to a folder}
mkdir -p -- "$dest"
for f in "$@"; do
  if [ -f "$f" ]; then cp -- "$f" "$dest/" && echo "copied: $f"; else echo "skipped: $f" >&2; fi
done''',
'<p>Run with DEST=~/qt/out2 and three awkward names.</p>', expect='any') + puzzle_answer('With <code>dir</code> empty, <code>rm -rf $dir/*</code> becomes <code>rm -rf /*</code>: an attempt to delete everything the user can reach. Make it safe with <code>"${dir:?}"</code> (stop if empty or unset) and quotes: <code>rm -rf -- "${dir:?}"/*</code>, and add <code>set -u</code> at the top of the script (Lesson 12.6).') + qc('Inside double quotes, which four characters are still special?', '<code>$</code>, <code>`</code>, <code>\\</code> and <code>"</code> (and ! in interactive shells).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/qt ~/inner.sh ~/wrap.sh', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-shell-variables-and-environment-variables-env/">Lesson 12.1</a> (variables) and <a href="../../03-files-and-directories/04-wildcards-and-globbing/">Lesson 3.4</a> (wildcards).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
