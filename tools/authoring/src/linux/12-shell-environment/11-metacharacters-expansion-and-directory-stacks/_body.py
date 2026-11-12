import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

EX = r"""rm -rf ~/ex; mkdir -p ~/ex/proj/{src,docs,logs} ~/ex/backup; cd ~/ex
touch proj/src/{main,util}.py proj/docs/readme.md proj/logs/app{1,2,3}.log notes.txt 'my file.txt'"""

HOOK = hook('Riya types one line: <code>cp ~/proj/{src,docs}/*.{py,md} "$BACKUP/$(date +%F)"</code>. Before cp even starts, bash rewrites that line in seven steps: braces become several words, <code>~</code> becomes her home, <code>$BACKUP</code> and <code>$(date +%F)</code> are filled in, the result is split into words, <code>*</code> turns into real file names, and the quotes are removed. Knowing this order explains almost every “why did the shell do that?”. This lesson also covers the <b>metacharacters</b> that have special meaning (<code>; &amp; | &lt; &gt; ( ) $ ` \\ " \' * ? [ ] ~ { } #</code>), <code>eval</code> (run a string as a new command line, and why it is dangerous), and <b>directory stacks</b>: <code>pushd</code>, <code>popd</code> and <code>dirs</code> to jump between folders and come back.',
    ['name the shell metacharacters and what each one does, and protect them when you need them literally',
     'list the seven expansions in their real order and predict the result of any command line',
     'use brace expansion, tilde expansion, command and arithmetic substitution, and process substitution confidently',
     'use eval only when needed (and safely), and move between folders with pushd, popd, dirs and cd -'])
ROAD = roadmap([
    ('story', 'The story', 3, 'one line, seven steps'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'Metacharacters and expansion', 6, 'simple meaning + 4 depths'),
    ('types', 'The seven expansions', 5, 'in order'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'a line being expanded'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'predict the shell'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Several similar names in one word', 'mkdir -p proj/{src,docs,logs}', 'brace expansion'),
    ('Numbers or letters in a row', 'touch file{1..5}.txt  ·  {a..e}', 'braces'),
    ('Your home / previous folder', '~   ·   ~riya   ·   cd -', 'tilde'),
    ('Output of a command inside a line', '"$(date +%F)"', 'command substitution'),
    ('Treat a command’s output as a file', 'diff <(sort a) <(sort b)', 'process substitution'),
    ('Use a metacharacter literally', "'*'  \\;  \"|\"", 'quote it (12.4)'),
    ('Build a command in a variable and run it', 'an array: cmd=(ls -l); "${cmd[@]}"', 'eval only if needed'),
    ('Jump to a folder and come back', 'pushd /var/log … popd', 'directory stack'),
])

cmap = concept_map(
    [('12.4', 'Quoting', 'what quotes stop'), ('3.4', 'Globbing', '* ? [ ] { }'), ('5.2', 'Redirection', '< > |')],
    ['metacharacters: ; & | < > ( ) $ ` \\ " \' * ? [ ] ~ { } #', 'the seven expansions in order', 'brace, tilde, parameter, arithmetic, command, process substitution', 'eval and its dangers', 'pushd, popd, dirs, cd -'],
    [('12.13', 'Arrays', 'commands in arrays'), ('12.14', 'Strings', '${var} operations'), ('13.1', 'Combining commands', '<( ) and subshells'), ('12.12', 'make', 'targets and variables')],
    'bash rewrites every line in a fixed order before running it. Metacharacters trigger those rewrites; quotes switch them off.')

sc = (term(20, 14, 316, 156, ['$ echo proj/{src,docs}/*.{py,md}', ('proj/src/main.py proj/src/util.py', 'out'), ('proj/docs/readme.md', 'out'), '$ pushd /var/log; pushd /etc', ('/etc /var/log ~/ex', 'acc'), '$ popd', ('/var/log ~/ex', 'out')], title='riya@web01: ~/ex', prompt='riya@web01:~/ex$', size=6.8, step=15)
      + t(352, 36, 'Before running:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['1 {braces}', '2 ~ tilde', '3 $var $(…) $((…))', '4 split, 5 *glob', '6 quote removal'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One line, seven steps</h2>
  <div class="story">
''' + puzzle('Riya stores a command in a variable: <code>cmd="ls -l | grep txt"</code>, then runs <code>$cmd</code>. Instead of a filtered list she gets <code>ls: cannot access \'|\': No such file or directory</code> and <code>ls: cannot access \'grep\'</code>. A colleague says “use eval”. Why did the pipe not work, what does eval change, and what is the safer way to keep a command in a variable?') + '''
    <p class="narration">Riya watches bash turn one short line into a long list of real file names.</p>
''' + scene('A terminal: echo with braces and globs prints matching files; pushd builds a stack of folders and popd returns.', sc,
            'The shell rewrites the line <tspan font-weight="700" class="s-acc">before</tspan> the command sees it.') + '''
K> So echo never sees the braces or the star?
A> Exactly. echo receives the finished list of names. Every special character you type (a <b>metacharacter</b>) is an instruction to the shell, handled in a fixed order: braces first, then <code>~</code>, then <code>$</code> things, then splitting, then wildcards, then quotes are removed.
R> And the puzzle?
A> It is about <b>when</b> the shell looks for <code>|</code>: before expansion. A pipe that only appears after <code>$cmd</code> is expanded is just text. Today: every metacharacter, the expansion order, eval, and the directory stack.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A post office sorting line: first the envelope is split into copies (braces), then addresses are filled in (tilde, variables, commands), then pages are separated (word splitting), then wildcards are looked up (globbing), and the stamps (quotes) are removed before delivery.">'
       + label_box(14, 20, 140, 110, ['1. copies', '{a,b} → a b', '2. address', '~ → /home/riya'], 'blue', 8.2)
       + label_box(166, 20, 150, 110, ['3. fill in', '$v  $(cmd)', '$((1+2))', '(left to right)'], 'amber', 8.2)
       + label_box(328, 20, 140, 110, ['4. split', 'at spaces', '5. look up', '*.txt → names'], 'green', 8.2)
       + label_box(480, 20, 146, 110, ['6. remove', 'quotes', '7. deliver', 'to the command'], 'violet', 8.2)
       + t(320, 160, 'Pipes, ; and redirections are found BEFORE all of this.', 9.6, 'ink2')
       + t(320, 182, 'That is why $cmd cannot contain a working pipe.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Expansion at four depths', [
    ('v', 'No jargon: a sorting line', '      <p>Your line passes through stations before it is delivered.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>mkdir -p proj/{src,docs,logs}</code>: three folders in one go.</li>
        <li><code>cp report.txt{,.bak}</code>: copy to report.txt.bak.</li>
        <li><code>cd ~</code>, <code>cd -</code>: home, and back to where you were.</li>
        <li><code>pushd /var/log</code> … <code>popd</code>: visit a folder and return.</li>
      </ul>'''),
    ('i', 'The order', '''      <ol>
        <li><b>Brace expansion</b> <code>{a,b}</code>, <code>{1..5}</code> (no variables inside).</li>
        <li><b>Tilde expansion</b> <code>~</code>, <code>~user</code>, <code>~+</code>, <code>~-</code>.</li>
        <li><b>Parameter, arithmetic and command substitution, process substitution</b>, left to right: <code>$v</code>, <code>${v}</code>, <code>$((…))</code>, <code>$(…)</code>, <code>&lt;(…)</code>.</li>
        <li><b>Word splitting</b> of unquoted results (IFS).</li>
        <li><b>Pathname expansion</b> (globbing) <code>* ? [ ]</code> on unquoted words.</li>
        <li><b>Quote removal</b>.</li>
      </ol><p>Before all of it, bash splits the line into tokens at metacharacters (<code>| &amp; ; ( ) &lt; &gt;</code> space, tab, newline) and recognises keywords; history <code>!</code> and aliases come even earlier.</p>'''),
    ('a', 'Behind the screen: tokens, eval and the stack', '''      <ul>
        <li>Operators like <code>|</code>, <code>&amp;&amp;</code>, <code>&gt;</code> are recognised while the line is <b>tokenised</b>, before expansion; anything they produce later is ordinary text. That is the puzzle.</li>
        <li><code>eval STRING</code> joins its arguments and feeds the result through the whole parser <b>again</b>: expansions happen twice. If any part comes from a user or a file, that is code injection.</li>
        <li>Safer: store commands in <b>arrays</b> (<code>cmd=(ls -l "$dir")</code>, run <code>"${cmd[@]}"</code>), use functions, or <code>${!name}</code> for indirect variables.</li>
        <li>The directory stack is a bash array, <code>DIRSTACK</code>; <code>dirs -v</code> numbers it, <code>pushd +N</code> rotates it, <code>~N</code> refers to entry N.</li>
        <li><code>$( )</code> runs in a subshell and strips trailing newlines; <code>&lt;( )</code> gives a /dev/fd/N path to a pipe.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Metacharacters, expansion, eval and directory stacks</h2>
''' + def_block(
    '<b>Metacharacters</b> are characters with special meaning to the shell (separators, operators, quoting and expansion triggers). <b>Expansion</b> is the set of rewrites bash applies to every command line, in a fixed order: brace, tilde, parameter/arithmetic/command/process substitution, word splitting, pathname expansion and quote removal. <code>eval</code> re-parses its arguments as a new command line. The <b>directory stack</b> is a list of folders managed with <code>pushd</code>, <code>popd</code> and <code>dirs</code>.',
    'Special characters are instructions. The shell carries them out in order, then runs the command.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Metacharacter', 'A character the shell treats specially.'),
    ('Token', 'A word or operator after splitting the line.'),
    ('Brace expansion', '{a,b} {1..5}: generate words.'),
    ('Tilde expansion', '~ → a home folder.'),
    ('Command substitution', '$(cmd) → its output.'),
    ('Process substitution', '<(cmd) → a file name for its output.'),
    ('eval', 'Run a string as a command line.'),
    ('Directory stack', 'pushd/popd list of folders.'),
]) + '\n' + names('Where the names come from.', [
    ('meta-', 'beyond', 'Characters about characters.'),
    ('glob', 'global', '/etc/glob in Unix V1.'),
    ('~', 'tilde', 'Home, from the ADM-3A keyboard.'),
    ('eval', 'evaluate', 'Bourne shell.'),
    ('pushd', 'push directory', 'csh, 1979.'),
    ('popd', 'pop directory', 'csh.'),
    ('dirs', 'directories', 'Show the stack.'),
    ('$( )', 'command substitution', 'Replaces `…`.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Several names', '<code>{a,b,c}</code>'),
    ('Ranges', '<code>{1..10}</code> <code>{a..e}</code>'),
    ('Home', '<code>~</code> / <code>~user</code>'),
    ('Previous folder', '<code>cd -</code>'),
    ('Stack', '<code>pushd</code> <code>popd</code> <code>dirs -v</code>'),
    ('See expansions', '<code>set -x</code>'),
]) + '\n' + lv + didyou('Brace expansion is not globbing: <code>echo {x,y}.txt</code> prints x.txt y.txt even if those files do not exist, while <code>echo *.txt</code> prints only names that exist. That is why <code>mkdir -p proj/{src,docs}</code> works for folders that do not exist yet.') + '''
EXAM> “What is the difference between $( ) and backquotes?” → Both are command substitution; $( ) nests easily and is clearer; backquotes need escaping inside.
''' + qc('Why does <code>echo {1..$n}</code> print {1..3} when n=3?', 'Brace expansion is step 1 and happens before $n is filled in, so the braces are not a valid range yet; they stay as text.') + mistake('cmd="ls -l | grep txt"; $cmd',
    'cmd=(ls -l); "${cmd[@]}" | grep txt   ·   or a function   ·   eval "$cmd" only for trusted, fixed text',
    'The pipe is recognised before expansion, so after $cmd is expanded, | is just an argument to ls. Real run: ls: cannot access \'|\'.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The metacharacters, and the expansions in order</h2>
''' + table(['Character', 'Meaning', 'Example'], [
    ['<code>;</code>  newline', 'end of a command', '<code>cd /tmp; ls</code>'],
    ['<code>&amp;</code>', 'run in the background', '<code>sleep 60 &amp;</code>'],
    ['<code>&amp;&amp;</code>  <code>||</code>', 'run next if ok / if failed', '<code>make &amp;&amp; ./app</code>'],
    ['<code>|</code>', 'pipe', '<code>ls | wc -l</code>'],
    ['<code>&lt; &gt; &gt;&gt; 2&gt;</code>', 'redirection', '<code>sort &lt; in &gt; out</code>'],
    ['<code>( )</code>  <code>{ ;}</code>', 'subshell / group', '<code>(cd /; ls)</code>'],
    ['<code>$</code>', 'variable, $( ), $(( ))', '<code>$HOME</code>'],
    ['<code>` `</code>', 'old command substitution', '<code>`date`</code>'],
    ['<code>\\</code>  <code>" "</code>  <code>\' \'</code>', 'quoting', '<code>\\$5</code>'],
    ['<code>* ? [ ]</code>', 'wildcards', '<code>*.log</code>'],
    ['<code>{ }</code>', 'brace expansion', '<code>{a,b}</code>'],
    ['<code>~</code>', 'home folder', '<code>~/bin</code>'],
    ['<code>#</code>', 'comment (at word start)', '<code># note</code>'],
    ['<code>!</code>', 'history / not', '<code>!!</code>, <code>! cmd</code>'],
], minw=520) + table(['Step', 'Expansion', 'Example', 'Result'], [
    ['1', 'brace', '<code>f{1..3}</code>', 'f1 f2 f3'],
    ['2', 'tilde', '<code>~/bin</code>', '/home/riya/bin'],
    ['3', 'parameter', '<code>${USER}</code>', 'riya'],
    ['3', 'arithmetic', '<code>$((6*7))</code>', '42'],
    ['3', 'command', '<code>$(date +%Y)</code>', '2026'],
    ['3', 'process', '<code>&lt;(ls)</code>', '/dev/fd/63'],
    ['4', 'word splitting', '<code>$v</code> with spaces', 'several words'],
    ['5', 'pathname (glob)', '<code>*.py</code>', 'main.py util.py'],
    ['6', 'quote removal', '<code>"a b"</code>', 'a b (one word)'],
], minw=520) + table(['', 'pushd / popd', 'cd -', 'cd ~N'], [
    ['Remembers', 'a whole stack', 'one previous folder', 'entry N of the stack'],
    ['Go back', 'popd', 'cd - again', '—'],
    ['Show', 'dirs -v', 'echo $OLDPWD', 'dirs -v'],
], minw=420) + qc('Which happens first: <code>$(…)</code> or the <code>*</code> wildcard?', 'Command substitution (step 3) happens first; globbing (step 5) is applied to the result if it is unquoted.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Expansion, eval and directory stacks, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/ex</code> with a project <code>proj/</code> (src/main.py, src/util.py, docs/readme.md, logs/app1–3.log), <code>notes.txt</code> and <code>my file.txt</code>.</p>
''' + cmdcard_u(['creating several folders or files at once', 'backups (file{,.bak})', 'sequences of names'],
               ['matching existing files (use globs)', 'ranges from variables'])(
    'brace', '{a,b,c} · {1..10} · {a..e} · {01..10..2}', 'brace expansion',
    'Braces generate words: a comma list <code>{a,b,c}</code>, a range <code>{1..10}</code> or <code>{a..e}</code>, with an optional step <code>{0..20..5}</code> and zero padding <code>{01..10}</code>. A prefix and suffix are glued to each word; braces can be nested and combined.',
    'pre{a,b}post   ·   {1..N}   ·   {X..Y..STEP}', 'change',
    [('{a,b,c}', 'list', 'names'),
     ('{1..5}', 'numbers', 'files'),
     ('{a..e}', 'letters', 'folders'),
     ('{01..10}', 'zero-padded', 'sorting'),
     ('{0..20..5}', 'step', 'intervals'),
     ('file{,.bak}', 'empty + .bak', 'backups'),
     ('{a,b}{1,2}', 'combinations', 'matrix')],
    dict(setup=EX, cmd="cd ~/ex\necho {a,b}{1,2}\necho log{01..03}.txt\necho {0..20..5} {e..a}\nmkdir -p demo/{in,out,tmp} && ls demo", note='Braces created three folder names that did not exist before.'),
    [('sys', [
        dict(situation='Quick backup and a project skeleton.', setup=EX, cmd="cd ~/ex\ncp notes.txt{,.bak}; ls notes*\nmkdir -p site/{css,js,img} site/pages/{home,about}; find site -type d | sort", why='cp notes.txt{,.bak} = cp notes.txt notes.txt.bak.')]),
     ('qa', [
        dict(situation='Braces do not take variables.', cmd="n=3\necho {1..$n}\necho $(seq 1 $n)\neval echo {1..$n}", why='{1..$n} stays literal (step 1 runs before $n). seq works; eval also works but is risky (see eval card).')]),
    ],
    anat=anatomy([('mkdir -p', 'cmd', 'command'), ('proj/', 'arg', 'prefix'), ('{src,docs}', 'opt', 'braces'), ('/x', 'arg', 'suffix')], 'Each brace item gets the prefix and suffix.')
) + cmdcard_u(['home and user folders', 'quick returns to the previous folder'],
               ['~ inside quotes (it stays literal)'])(
    'tilde', '~ · ~user · ~+ · ~- · cd -', 'tilde expansion',
    'At the start of a word, <code>~</code> becomes your home, <code>~riya</code> riya’s home, <code>~+</code> the current folder ($PWD), <code>~-</code> the previous one ($OLDPWD). <code>cd -</code> goes back to the previous folder. Inside quotes, use <code>$HOME</code> instead.',
    'cd ~/bin   ·   ls ~riya   ·   cd -', 'safe',
    [('~', 'your home', 'paths'),
     ('~user', 'their home', 'admin'),
     ('~+ / ~-', 'current / previous', 'rare'),
     ('cd -', 'go back', 'daily'),
     ('"$HOME"', 'home inside quotes', 'scripts')],
    dict(cmd="echo ~ ~riya\necho \"~\" \"$HOME\"\ncd /tmp; cd /etc; cd - ; echo \"OLDPWD was $OLDPWD\"", note='cd - also prints the folder it went to.'),
    [('dev', [
        dict(situation='~ only at the start of a word.', cmd="echo ~/bin x~ a=~/data\nf=~/x; echo \"$f\"", why='~ expands at the start of a word and right after = (bash does this for anything that looks like an assignment), but not in the middle (x~).')]),
    ]
) + cmdcard_u(['values inside a command line: dates, counts, sums', 'comparing two outputs without temp files'],
               ['backticks in new scripts', 'unquoted $( ) with names containing spaces'])(
    'subst', '$(cmd) · $((expr)) · <(cmd)', 'command, arithmetic and process substitution',
    '<code>$(cmd)</code> is replaced by cmd’s output (trailing newlines removed). <code>$((expr))</code> by an integer result. <code>&lt;(cmd)</code> by a file name (/dev/fd/…) from which cmd’s output can be read, so commands that want files can read command output.',
    'x="$(cmd)"   ·   $(( a * b ))   ·   diff <(cmd1) <(cmd2)', 'safe',
    [('$(cmd)', 'output inline', 'dates, counts'),
     ('`cmd`', 'old form', 'legacy'),
     ('$(( ))', 'integer maths', '12.7'),
     ('<(cmd)', 'output as a file', 'diff, comm, join'),
     ('>(cmd)', 'write into a command', 'tee to two tools'),
     ('$(<file)', 'file contents (fast)', 'no cat')],
    dict(setup=EX, cmd="cd ~/ex\necho \"today $(date +%Y) has $(ls proj/logs | wc -l) logs and $((24 * 7)) hours a week\"\necho <(true)\ndiff <(ls proj/src) <(printf 'main.py\\ntests.py\\n')", expect='any', note='diff compared a folder listing with a typed list, no temp files.'),
    [('data', [
        dict(situation='Nested substitution and $(<file).', setup=EX, cmd="cd ~/ex; echo 'v2.4' > version.txt\necho \"release $(<version.txt) built in $(basename \"$(pwd)\")\"\necho \"outer `echo inner`\"", why='$( ) nests without escaping; $(<file) reads a file without starting cat.')]),
    ]
) + cmdcard_u(['indirect variable names (rare)', 'running a command line read from a trusted config'],
               ['anything containing user input or file names (code injection)', 'commands that could be arrays or functions'])(
    'eval', 'eval · ${!name} · command arrays', 'run a string as code',
    '<code>eval "string"</code> joins its arguments and runs the result as a new command line, so pipes, redirections and expansions inside it work, and everything is expanded a <b>second</b> time. Safer alternatives: <code>${!name}</code> for “the variable whose name is in name”, arrays for commands, functions for reusable lines.',
    'eval "$cmd"   ·   echo "${!name}"   ·   cmd=(ls -l "$d"); "${cmd[@]}"', 'danger',
    [('eval "$s"', 'run text as a command line', 'trusted text only'),
     ('${!name}', 'indirect variable', 'safe'),
     ('cmd=(…); "${cmd[@]}"', 'command in an array', 'safe'),
     ('declare -n ref=var', 'name reference', 'bash 4.3+'),
     ('printf %q', 'quote safely', 'build commands')],
    dict(setup=EX, cmd="cd ~/ex\ncmd='ls proj/src | wc -l'\n$cmd 2>&1 | head -2\neval \"$cmd\"\nname=USER; echo \"${!name}\"", expect='any', note='The puzzle: $cmd passes | and wc to ls as names; eval re-parses the text so the pipe works; ${!name} reads the variable called USER.'),
    [('sec', [
        dict(situation='Why eval is dangerous.', setup=EX, cmd="cd ~/ex; touch victim.txt\nuser_input='notes.txt; rm victim.txt'\neval \"ls $user_input\"\nls victim.txt 2>&1", expect='any', why='The “file name” contained a second command, and eval ran it. Never eval anything that comes from users, files or the network.')]),
     ('dev', [
        dict(situation='The safe way: a command in an array.', setup=EX, cmd="cd ~/ex\ncmd=(ls -l 'my file.txt')\n\"${cmd[@]}\" | cut -c1-10\nprintf '%q ' \"${cmd[@]}\"; echo", why='Each array item is one argument, spaces included; printf %q shows a safely quoted version.')]),
    ]
) + cmdcard_u(['working in several folders and coming back', 'scripts that must return to where they started'],
               ['scripts where a subshell (cd x; …) is simpler'])(
    'dirs', 'pushd · popd · dirs -v · cd -', 'directory stack',
    '<code>pushd DIR</code> goes to DIR and pushes the old folder on a stack; <code>popd</code> returns to the top folder of the stack and removes it; <code>dirs -v</code> shows the stack with numbers; <code>pushd +N</code> rotates to entry N; <code>cd -</code> just toggles with the previous folder.',
    'pushd DIR   ·   popd   ·   dirs -v   ·   pushd +2', 'safe',
    [('pushd DIR', 'go there, remember here', 'visits'),
     ('popd', 'come back', 'return'),
     ('dirs -v', 'numbered stack', 'see it'),
     ('pushd', 'swap top two', 'toggle'),
     ('pushd +N', 'rotate to N', 'jump'),
     ('dirs -c', 'clear stack', 'reset'),
     ('> /dev/null', 'hide the printed stack', 'scripts')],
    dict(setup=EX, cmd="cd ~/ex\npushd proj/logs > /dev/null\npushd /etc > /dev/null\ndirs -v\npopd > /dev/null; pwd\npopd > /dev/null; pwd", note='Two visits, then back step by step to ~/ex.'),
    [('sys', [
        dict(situation='A script that always returns.', setup=EX, cmd="cd ~/ex\npushd proj/src > /dev/null || exit 1\necho \"working in $(pwd | sed 's|.*/ex|~/ex|'): $(ls | wc -l) files\"\npopd > /dev/null\necho \"back in $(pwd | sed 's|.*/ex|~/ex|')\"", why='pushd/popd pair up like brackets; a subshell ( cd …; … ) is the other way.')]),
     ('dev', [
        dict(situation='Rotate the stack.', setup=EX, cmd="cd ~/ex; pushd /tmp >/dev/null; pushd /etc >/dev/null; pushd /var >/dev/null\ndirs -v | sed 's|/home/riya|~|'\npushd +2 > /dev/null; pwd", why='+2 brings entry 2 to the top (and changes to it).')]),
    ]
) + undo('Expansion happens before commands run; check it before running destructive commands.', [
    ('Not sure what a line will become:', 'put <code>echo</code> in front, or <code>set -x</code>.'),
    ('A brace or glob created/removed too much:', 'restore from backup; next time preview with echo.'),
    ('Lost in folders:', '<code>cd -</code>, <code>dirs -v</code>, <code>popd</code>, or simply <code>cd</code>.'),
    ('Used eval on input:', 'remove it; use arrays, ${!name} or case to choose commands.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='popd', meaning='The stack is empty.', fix='pushd first; dirs -v to check.'),
    dict(cmd='pushd /nope', meaning='No such folder.', fix='Check the path.'),
    dict(cmd='echo $(( 2 + ))', meaning='Incomplete arithmetic.', fix='Complete the expression.'),
    dict(cmd='echo a;; b', meaning=';; is only valid inside case.', fix='One ; separates commands.'),
]) + qc('What does <code>cp file{,.bak}</code> run?', 'cp file file.bak.') + '''
'''
cards = cards + '</section>\n'

def exp(k):
    steps = ['cp ~/p/{a,b}.txt "$D/$(date +%Y)"',
             'cp ~/p/a.txt ~/p/b.txt "$D/$(date +%Y)"',
             'cp /home/riya/p/a.txt /home/riya/p/b.txt "$D/$(date +%Y)"',
             'cp /home/riya/p/a.txt /home/riya/p/b.txt "/bk/2026"']
    o = ''
    for i in range(k + 1):
        o += label_box(10, 14 + i * 40, 340, 32, [steps[i]], ['blue', 'amber', 'green', 'violet'][i], 7.2)
    return o
see_cmds = [['$ cp ~/p/{a,b}.txt "$D/$(date +%Y)"']] * 4
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['The line you type.', 'Step 1: braces.', 'Step 2: tilde.', 'Step 3: $D and $(date).'])]
behind = [exp(k) + t(180, 190, n, 8.4, 'violet', bold=True) for k, n in enumerate(['As typed.', '{a,b} → two words.', '~ → /home/riya.', 'Variables and commands filled in; quotes go.'])]
two = anim_two('A line being expanded', 'Behind the screen: the same line, rewritten step by step',
               'A terminal with one cp command line using braces, a tilde, a variable and a command substitution.',
               'The command line rewritten four times: braces, tilde, variables and command substitution, giving the final cp command.', see, behind,
               ['Typed.', 'Braces.', 'Tilde.', 'Values.'],
               ['as typed', '{a,b}', '~', '$D $(…)'])

def stack(k):
    stacks = [['~/ex'], ['/var/log', '~/ex'], ['/etc', '/var/log', '~/ex'], ['/var/log', '~/ex']]
    o = ''
    for i, d in enumerate(stacks[k]):
        o += label_box(110, 20 + i * 36, 140, 30, [f'{i}: {d}'], 'green' if i == 0 else 'card', 8)
    return o
frames = [stack(0) + t(180, 180, 'Start in ~/ex.', 8.6, 'violet', bold=True),
          stack(1) + t(180, 180, 'pushd /var/log: ~/ex remembered.', 8.6, 'violet', bold=True),
          stack(2) + t(180, 180, 'pushd /etc: now three entries.', 8.6, 'violet', bold=True),
          stack(3) + t(180, 180, 'popd: back to /var/log.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'The directory stack',
              'pushd adds on top, popd removes the top.',
              'pushd / popd', 'A stack of folder names: pushd puts the new folder on top and keeps the old ones below; popd removes the top and changes to the next.', frames,
              ['Start.', 'pushd.', 'pushd.', 'popd.'], hid='scenario-stack')

dx = dissect('Layer by layer: from a typed line to arguments',
    'Each layer has a real command and output from our build machine.', [
    dict(key='tok', name='Tokens', sub='operators first', why='Find | ; > &.', how='Before expansion.', impl='The parser.', used='Every line.',
         cmd="v='a | b'; printf '[%s]\\n' $v"),
    dict(key='brace', name='Brace + tilde', sub='steps 1–2', why='Generate words.', how='Text only.', impl='No files needed.', used='mkdir -p.',
         cmd="set -x; : x{1,2} ~ 2>&1; set +x"),
    dict(key='subst', name='Substitutions', sub='step 3', why='Fill in values.', how='Left to right.', impl='$( ) = subshell.', used='Everywhere.',
         cmd="i=1; echo $((i++)) $((i++)) $i"),
    dict(key='glob', name='Split + glob', sub='steps 4–5', why='Real file names.', how='Unquoted only.', impl='Sorted.', used='*.log.',
         setup=EX, cmd="cd ~/ex/proj/logs; p='app*.log'; echo $p; echo \"$p\""),
], hint='From tokens to the final argument list. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A line being expanded, and the directory stack</h2>
''' + two + s1 + dx + qc('In <code>echo $((i++)) $((i++)) $i</code> with i=1, why is the output 1 2 3?', 'Step 3 runs left to right: the first prints 1 and makes i 2, the second prints 2 and makes i 3, then $i is 3.') + '''
</section>
'''

VAR = variations('Fifteen more one-line experiments with metacharacters, expansions, eval and the stack. All were really run on our build machine.', [
    ('Braces and tilde', [
        dict(title='Many files in one touch', cmd="touch day{1..7}.log; ls day*.log | wc -l", why='Seven names from one word.'),
        dict(title='Combinations', cmd="echo {dev,test,prod}-{web,db}", why='3 × 2 = 6 names.'),
        dict(title='Rename an extension with braces', cmd="touch data.csv; mv data.{csv,txt}; ls data.*", why='mv data.csv data.txt.'),
        dict(title='Zero-padded sequence for sorting', cmd="echo img{08..12}.png", why='Padding keeps names in order (img08 before img10).'),
        dict(title='Another user’s home', cmd="echo ~root ~riya ~nosuchuser", why='Unknown users stay literal.'),
    ]),
    ('Substitutions', [
        dict(title='A dated backup name', cmd="echo \"backup_$(date +%Y%m%d)_$(hostname).tar.gz\"", why='Several substitutions in one word.'),
        dict(title='Count and compute in one line', cmd="echo \"$(ls /etc | wc -l) entries, about $(( $(ls /etc | wc -l) / 10 )) tens\" | sed 's/^[0-9]*/N/; s/about [0-9]*/about M/'", why='$(( )) can contain $( ).'),
        dict(title='Compare two command outputs', cmd="comm -3 <(printf 'a\\nb\\nc\\n') <(printf 'b\\nc\\nd\\n')", why='Process substitution: two outputs as two files.'),
        dict(title='Write to two commands at once', cmd="printf 'b\\na\\n' | tee >(sort > sorted.txt) > copy.txt; sleep 0.2; cat sorted.txt copy.txt", why='>( ) is a file name that feeds a command.'),
    ]),
    ('Metacharacters, eval and the stack', [
        dict(title='Separators and operators', cmd="echo one; echo two && echo three || echo never; false || echo 'after false'", why='; always, && on success, || on failure.'),
        dict(title='Metacharacters as plain text', cmd="echo 'a;b|c>d&e' \"*\" \\$5 \\~", why='Quoting makes them ordinary characters.'),
        dict(title='Subshell vs group', cmd="cd /tmp; (cd /etc; pwd); pwd; { cd /usr; pwd; }; pwd", why='( ) runs in a child (cd forgotten); { } in this shell.'),
        dict(title='Indirect variables without eval', cmd="env_dev=10.0.0.5; env_prod=10.0.0.9; e=prod; v=env_$e; echo \"${!v}\"", why='${!v} reads the variable named in v.'),
        dict(title='eval to build a variable name (trusted)', cmd="for i in 1 2; do eval \"slot_$i=free\"; done; echo \"$slot_1 $slot_2\"", why='Acceptable with fixed, trusted text; an array is cleaner (12.13).'),
        dict(title='Two-folder toggle', cmd="cd /tmp; pushd /etc > /dev/null; pushd > /dev/null; pwd; pushd > /dev/null; pwd; dirs -c", why='pushd with no argument swaps the top two entries.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Expansion and the stack at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['{dev,prod}', 'setup'], 'blue', 8.6), '1. Project and environment setup',
              'mkdir -p app/{dev,test,prod}/{config,logs} creates a whole tree in one command.', ['Plan', '*braces', 'tree']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['$(date)', 'backups'], 'green', 8.6), '2. Dated backups',
    'Backup names embed $(date +%F) and $(hostname) so files never overwrite each other.', ['Run', '*$( )', 'archive']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['<( )', 'diffs'], 'amber', 8.6), '3. Comparing environments',
    'diff <(ssh web01 rpm -qa | sort) <(ssh web02 rpm -qa | sort) finds package differences between servers.', ['Two lists', '*<( )', 'diff']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['no eval', 'security'], 'red', 8.6), '4. Secure scripts',
    'Code reviews flag eval on input; arrays and case replace it.', ['Review', '*arrays', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['pushd', 'builds'], 'violet', 8.6), '5. Build scripts',
    'Builds pushd into each module folder, build, popd back; the stack keeps paths straight.', ['Enter', '*pushd/popd', 'return']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Ten folders at once', scenario='Course weeks.', cmd="mkdir -p week{01..10}; ls -d week* | wc -l", explain='Brace range with padding.'),
    dict(level='b', title='Back to the last folder', scenario='Toggle.', cmd="cd /tmp; cd /etc; cd - > /dev/null; pwd", explain='cd -.'),
    dict(level='i', title='Preview a glob before rm', scenario='Safety.', setup=EX, cmd="cd ~/ex/proj/logs; echo rm app*.log", explain='echo shows what would run.'),
    dict(level='i', title='Same folders in two places', scenario='Compare trees.', setup=EX, cmd="cd ~/ex; diff <(ls proj) <(ls -1 proj | sort)  && echo same", explain='Process substitution.'),
    dict(level='a', title='Trace the expansion', scenario='Learn the order.', setup=EX, cmd="cd ~/ex/proj; set -x; : {src,docs}/* ~ $((2+2)) 2>&1; set +x", explain='set -x shows the expanded line.'),
], extra=build_up('predicting the shell', 'Riya expands one line step by step with echo before running it for real.', EX, [
    ("cd ~/ex; echo proj/{src,docs}", '1. Braces only.'),
    ("cd ~/ex; echo proj/{src,docs}/*", '2. Then globbing finds the files.'),
    ('cd ~/ex; D=~/ex/backup; echo cp proj/{src,docs}/* "$D/$(date +%Y)"', '3. Add a target with ~, $D and $( ).'),
    ('cd ~/ex; D=~/ex/backup; mkdir -p "$D/$(date +%Y)"; cp proj/{src,docs}/* "$D/$(date +%Y)"; ls "$D/$(date +%Y)"', '4. Run it for real.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Generate names', '{a,b} {1..5}', 'No files needed.', 'Using * for names that do not exist.'),
    ('Match existing files', '* ? [ ]', 'Real files only.', 'Braces.'),
    ('Output inside a line', '"$(cmd)"', 'Clear, nests.', 'Backticks.'),
    ('Output as a file', '<(cmd)', 'No temp files.', 'Temp files you forget to delete.'),
    ('Command in a variable', 'array', 'Keeps arguments.', 'eval on input.'),
    ('Visit and return', 'pushd / popd', 'Remembers.', 'cd ../../.. by hand.'),
]) + keys('Handy forms.', [
    ('cp f{,.bak}', 'quick backup', 'braces'),
    ('mkdir -p a/{b,c}/{d,e}', 'tree', 'braces'),
    ('cd -', 'previous folder', 'tilde'),
    ('diff <(a) <(b)', 'compare outputs', 'process subst'),
    ('${!name}', 'indirect', 'no eval'),
    ('dirs -v', 'see the stack', 'stack'),
]) + scriptit('mkproject.sh', 'Create a standard project tree for any name, using braces, substitutions, a dated log and the directory stack to return to the start folder.',
'''name=${1:-demo_app}
start=$PWD
mkdir -p "$name"/{src,tests,docs,logs,config/{dev,prod}}
pushd "$name" > /dev/null || exit 1
touch src/main.py tests/test_main.py docs/README.md config/{dev,prod}/app.conf
echo "created $(date +%Y): $(find . -type f | wc -l) files, $(find . -type d | wc -l) folders" > logs/setup.log
cat logs/setup.log
popd > /dev/null
[ "$PWD" = "$start" ] && echo "back in the start folder"''',
'<p>Run without a name, so it uses demo_app.</p>', expect='any') + puzzle_answer('The pipe <code>|</code> is recognised when bash first splits the line into tokens, <b>before</b> <code>$cmd</code> is expanded. After expansion, <code>|</code>, <code>grep</code> and <code>txt</code> are just extra arguments to ls, hence “cannot access \'|\'”. <code>eval "$cmd"</code> feeds the text through the parser again, so the pipe works, but eval is dangerous with any input you do not control. Safer: <code>cmd=(ls -l); "${cmd[@]}" | grep txt</code>, or a function <code>listtxt(){ ls -l | grep txt; }</code>.') + qc('Which two expansions do NOT happen inside double quotes?', 'Brace expansion, tilde expansion, word splitting and globbing are all off inside double quotes; $, $( ) and $(( )) still work.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/ex', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-quoting-and-expansion-single-vs-double-quotes/">Lesson 12.4</a> (quoting and word splitting) and <a href="../../03-files-and-directories/04-wildcards-and-globbing/">Lesson 3.4</a> (wildcards).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
