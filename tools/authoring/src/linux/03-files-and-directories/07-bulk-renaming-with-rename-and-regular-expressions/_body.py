import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# The build machine cannot install the 'rename' package. prename.sh evaluates the same Perl expression on every
# name, exactly like Ubuntu's file-rename does, so every result below is verified; the page labels them honestly.
PRE = open(os.path.join(HERE, 'prename.sh'), encoding='utf-8').read()
VER = 'Typical output on Ubuntu (rename package) · result verified with the same Perl expression'
def R(setup, cmd):
    out = shlesson.run_sh(PRE + '\n' + setup + '\n' + cmd, 'any').rstrip('\n')
    return (VER, out)
def V(situation, setup, cmd, why):
    return dict(situation=situation, cmd=(setup + '\n' if setup else '') + cmd, rec=R(setup, cmd), why=why)

HOOK = hook('Riya copied 300 photos from a phone: <code>IMG 0001.JPEG</code> … with spaces and capital letters. The website needs <code>img_0001.jpg</code>: lowercase, underscores, short extension. <code>mv</code> renames one file at a time: 300 commands. One <code>rename</code> line does all 300, and with <code>-n</code> she can see every new name before anything changes.',
    ['rename many files in one command with a Perl substitution (<code>rename \'s/old/new/\' files</code>)',
     'preview safely with <code>-n</code> and see what happened with <code>-v</code>',
     'build patterns from regex parts: <code>^ $ . * + ? {n}</code>, <code>[ ]</code>, <code>\\d \\w \\s \\b</code>, groups <code>( )</code> and <code>$1</code>',
     'change case with <code>y/A-Z/a-z/</code>, and know the difference from mv, globs and the other rename on Red Hat'])
ROAD = roadmap([
    ('story', 'The story', 3, '300 photos, one line'),
    ('decide', 'Which tool when?', 2, 'mv, rename or a loop?'),
    ('definition', 'What rename is', 5, 'simple meaning + 4 depths'),
    ('commands', 'rename and regex, by field', 15, 'patterns, verified results'),
    ('errors', 'Errors and traps', 4, 'quotes, $(date), \\D'),
    ('animation', 'See it happen', 4, 'how s/// changes a name'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('mv, rename or a loop? (decide in 5 seconds)', [
    ('Rename one file', 'mv old new', 'simplest'),
    ('Same change on many files', "rename 's/old/new/' files", 'one command'),
    ('See the result first', "rename -n 's/…/…/' files", 'changes nothing'),
    ('Change the extension', "rename 's/\\.txt$/.md/' *.txt", '$ = at the end'),
    ('Add a prefix', "rename 's/^/2026_/' *", '^ = at the start'),
    ('Spaces to underscores', "rename 's/\\s+/_/g' *", 'g = every match'),
    ('All lowercase', "rename 'y/A-Z/a-z/' *", 'y = translate letters'),
    ('Re-order parts of a name', "rename 's/(\\d+)-(\\d+)/$2-$1/' *", 'groups and $1 $2'),
    ('A date or variable in the new name', 'rename "s/…/…_$(date +%F)/" *', 'double quotes!'),
    ('On RHEL/Rocky (util-linux rename)', 'rename .jpeg .jpg *.jpeg', 'different syntax'),
])

cmap = concept_map(
    [('3.2', 'mv', 'renames one file'), ('3.4', 'Wildcards', 'choose which files'), ('3.6', 'date', 'dates in names')],
    ['rename with s///, flags g and i', 'preview -n, verbose -v, force -f', 'regex: anchors, classes, \\d \\w \\s \\b, quantifiers', 'groups ( ) and $1, transliteration y///', 'Perl rename vs util-linux rename'],
    [('6.4', 'sed', 'the same s/// on text'), ('6.6', 'Regular expressions', 'grep, sed, awk'), ('13.2', 'find + -exec', 'rename in sub-folders'), ('12.4', 'Quoting', 'single vs double quotes')],
    'Bulk renaming is a daily job for data, media and log files. Regular expressions learned here are used again in grep, sed, awk, Python and SQL.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ ls | head -2', ('IMG 0001.JPEG', 'out'), ('IMG 0002.JPEG', 'out'), "$ rename -n 'y/A-Z/a-z/; s/\\s+/_/g;", "  s/\\.jpeg$/.jpg/' *", ('rename(IMG 0001.JPEG, img_0001.jpg)', 'acc'), ('… 300 lines', 'dim')], title='riya@laptop: ~/photos', size=7.4, step=15)
      + t(352, 36, 'One line, 300 files:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• y/A-Z/a-z/: lowercase', '• s/\\s+/_/g: spaces → _', '• s/\\.jpeg$/.jpg/: extension', '• -n: preview first', '• then run without -n'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>300 photos, one line</h2>
  <div class="story">
''' + puzzle('Riya wants to add today’s date to every report: <code>rename \'s/\\.txt$/_$(date +%F).txt/\' *.txt</code>. Instead of <code>report_2026-11-06.txt</code> she gets a strange name with numbers and the text “date +%F)”. Why, and what is the one-character fix?') + '''
    <p class="narration">The marketing team sent 300 product photos for the shop website. The names have spaces, capital letters and the long extension .JPEG; the website wants lowercase names with underscores and .jpg.</p>
''' + scene('A terminal: rename -n with three Perl expressions shows how IMG 0001.JPEG would become img_0001.jpg, for all 300 files.', sc,
            'Preview with <tspan font-weight="700" class="s-acc">-n</tspan>, then rename all at once.') + '''
R> 300 mv commands?
A> One <code>rename</code>. You give it a <b>substitution</b>, like find-and-replace: <code>s/old/new/</code>. It applies it to every file name you list, and with <code>-n</code> it only shows what it would do.
K> And what are those backslashes, <code>\\s+</code>?
A> Regular expressions, a small language for describing text: <code>\\s+</code> means “one or more spaces”, <code>$</code> means “at the end”. Today you learn rename and the regex pieces you need, with verified results for each one, and how data, media, development, security and operations teams use it.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Find and replace in a word processor: find a pattern, replace it, apply to all. rename does this to file names: s/find/replace/ applied to each file, with a preview.">'
       + ''.join(label_box(16 + k * 156, 22, 144, 104, [a, b, c, d], tone, 9) for k, (a, b, c, d, tone) in enumerate([
           ('1 · Find', 'what to look for', 's/ IMG /', '(a pattern)', 'blue'),
           ('2 · Replace', 'with what', '/ img /', '(the new text)', 'green'),
           ('3 · Preview', '“Replace all?”', 'rename -n', 'nothing changes', 'amber'),
           ('4 · Apply', 'to every name', 'rename', 'all files at once', 'violet')]))
       + t(320, 158, 'Like Find and Replace in Word, but for file names,', 9.6, 'ink2')
       + t(320, 180, 'and the “find” part can be a smart pattern (a regex).', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Bulk renaming at four depths', [
    ('v', 'No jargon: find and replace for file names', '      <p>You know Find and Replace from Word or Excel.</p>' + pic + '''
      <ul>
        <li><code>rename</code> does the same with <b>file names</b>: find a piece of the name and replace it.</li>
        <li>It works on many files at once: all photos, all reports.</li>
        <li>The <code>-n</code> option is the preview: it shows the new names and changes nothing.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>rename -n 's/old/new/' files</code>: preview. Remove <code>-n</code> to do it; add <code>-v</code> to see each rename.</li>
        <li><code>s/draft/final/</code> replaces the first “draft” in each name; add <code>g</code> at the end for every match.</li>
        <li><code>^</code> = start of the name, <code>$</code> = end: <code>s/^/2026_/</code> adds a prefix, <code>s/\\.txt$/.md/</code> changes the extension.</li>
        <li><code>y/A-Z/a-z/</code> turns capitals into small letters.</li>
        <li>Install on Ubuntu/Debian: <code>sudo apt install rename</code>.</li>
      </ul>'''),
    ('i', 'Regular expression building blocks', '''      <ul>
        <li><code>.</code> any character, so a real dot is <code>\\.</code>.</li>
        <li>How many: <code>*</code> 0 or more, <code>+</code> 1 or more, <code>?</code> 0 or 1, <code>{2,4}</code> 2 to 4.</li>
        <li>Classes: <code>[abc]</code>, <code>[0-9]</code>, <code>[^a-z]</code> (not); shortcuts <code>\\d</code> digit, <code>\\w</code> letter/digit/_, <code>\\s</code> space; capitals mean “not”: <code>\\D \\W \\S</code>.</li>
        <li><code>\\b</code> word boundary, <code>\\B</code> not a boundary. Note: <code>_</code> counts as a word character.</li>
        <li>Groups <code>( )</code> remember text; use it in the replacement as <code>$1</code>, <code>$2</code>. Flags: <code>g</code> all, <code>i</code> ignore case.</li>
      </ul>'''),
    ('a', 'Behind the screen: Perl, quotes and two different renames', '''      <ul>
        <li>Ubuntu’s <code>rename</code> (package <code>rename</code>, also called <code>file-rename</code>/<code>prename</code>) is a Perl program: for each file it puts the name in Perl’s <code>$_</code>, runs your code, and calls <code>rename()</code> if the name changed. Any Perl works: <code>s///</code>, <code>y///</code>, <code>lc</code>, even <code>sprintf</code>.</li>
        <li>It does <b>not</b> overwrite an existing file unless you add <code>-f</code>; it prints “not renamed: … already exists”.</li>
        <li>Single quotes give the code to Perl unchanged (best). Inside single quotes <code>$(date)</code> is not run by bash; Perl reads <code>$(</code> as its own variable (your group IDs). For bash values use double quotes and escape Perl’s own <code>\\$1</code>.</li>
        <li>RHEL, Rocky and Fedora ship <b>util-linux</b> <code>rename</code> with a different syntax: <code>rename FROM TO files</code> (plain text, no regex). Check with <code>rename --version</code>.</li>
        <li>Non-ASCII names (é, हिन्दी) are bytes for Perl unless you add <code>-u</code> / utf8 handling: <code>\\w</code> may not match them.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>rename and regular expressions</h2>
''' + def_block(
    '<code>rename</code> (Perl rename, Debian and Ubuntu) renames the given files by applying a Perl expression, usually a substitution <code>s/REGEX/REPLACEMENT/FLAGS</code> or a transliteration <code>y/FROM/TO/</code>, to each file name. A <b>regular expression</b> (regex) is a pattern language that describes text by position (<code>^ $ \\b</code>), character sets (<code>[ ] \\d \\w \\s</code>), repetition (<code>* + ? {n,m}</code>) and groups (<code>( )</code>, referenced as <code>$1</code>).',
    '<code>rename</code> = find and replace in many file names at once; <code>-n</code> previews.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Regular expression', f'A pattern describing text. {gl("regular-expression-regex", "Glossary →")}'),
    ('Substitution s///', 's/find/replace/flags: the core of rename and sed.'),
    ('Flag', 'g = all matches, i = ignore case.'),
    ('Anchor', '^ start, $ end, \\b word boundary.'),
    ('Character class', '[0-9], \\d, \\w, \\s and their opposites.'),
    ('Quantifier', '* + ? {n,m}: how many times.'),
    ('Capture group', '( … ) remembers text for $1, $2.'),
    ('Globbing vs regex', f'*.txt (glob) is not .*\\.txt (regex). {gl("globbing-wildcards", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('rename', 'rename', 'Perl version by Larry Wall, the creator of Perl.'),
    ('s///', 'substitute', 'From the ed and sed editors.'),
    ('y///', 'yank / translate', 'Same as tr: letter for letter.'),
    ('regex', 'regular expression', 'From Stephen Kleene’s maths of the 1950s.'),
    ('\\d \\w \\s', 'digit, word, space', 'Capital = the opposite.'),
    ('\\b', 'boundary', 'Between a word character and a non-word character.'),
    ('$1', 'first group', 'What the first ( ) matched.'),
    ('-n', 'no action (nono)', 'Show, do not rename.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Preview', "<code>rename -n 's/a/b/' *</code>"),
    ('Do it, show each', "<code>rename -v 's/a/b/' *</code>"),
    ('Extension', "<code>rename 's/\\.txt$/.md/' *.txt</code>"),
    ('Prefix / suffix', "<code>s/^/new_/</code> · <code>s/\\.txt$/_bak.txt/</code>"),
    ('Spaces → _', "<code>rename 's/\\s+/_/g' *</code>"),
    ('Lowercase', "<code>rename 'y/A-Z/a-z/' *</code>"),
]) + '\n' + lv + didyou('Regular expressions were invented by the mathematician Stephen Kleene in 1951 to describe “regular events”. Ken Thompson put them into the Unix editor <code>ed</code> in 1968, and the command <code>g/re/p</code> (global, regular expression, print) became the name of <b>grep</b>.') + '''
EXAM> “Difference between mv and rename” → mv renames or moves one file (or moves many into a folder) and uses no patterns; rename changes many names at once with a Perl substitution, does not move files to other folders, previews with -n, and on RHEL uses a different util-linux syntax.
''' + qc('What does <code>rename \'s/^/2026_/\' *.csv</code> do?', 'Adds “2026_” at the start of every .csv name: ^ is the start, and replacing “the start” inserts text there.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The regex pieces you need for file names</h2>
''' + table(['Piece', 'Meaning', 'Example', 'Matches in a name'], [
    ['<code>abc</code>', 'the text itself', '<code>s/draft/final/</code>', 'draft'],
    ['<code>.</code> / <code>\\.</code>', 'any one character / a real dot', '<code>s/\\.jpeg$/.jpg/</code>', '.jpeg at the end'],
    ['<code>^</code> <code>$</code>', 'start / end of the name', '<code>s/^/new_/</code>', 'the start'],
    ['<code>*</code> <code>+</code> <code>?</code>', '0+, 1+, 0 or 1 of the previous item', '<code>s/\\.jpe?g$/.jpg/i</code>', '.jpg, .jpeg, .JPEG'],
    ['<code>{n}</code> <code>{n,m}</code>', 'exactly n / n to m times', '<code>s/\\d{4}//</code>', 'four digits'],
    ['<code>[ ]</code> <code>[^ ]</code>', 'one of / none of', '<code>s/[^a-z0-9._-]/_/g</code>', 'unsafe characters'],
    ['<code>\\d \\w \\s</code>', 'digit · letter/digit/_ · whitespace', '<code>s/\\s+/_/g</code>', 'runs of spaces'],
    ['<code>\\D \\W \\S</code>', 'not digit · not word · not space', '<code>s/\\W//g</code>', 'every non-word character'],
    ['<code>\\b \\B</code>', 'word boundary / not a boundary', '<code>s/\\breport\\b/x/</code>', '“report” as a whole word'],
    ['<code>( )</code> + <code>$1</code>', 'remember and reuse', '<code>s/(\\d+)/_$1/</code>', 'file123 → file_123'],
    ['<code>a|b</code>', 'a or b', '<code>s/(draft|tmp)_//</code>', 'draft_ or tmp_'],
    ['flags <code>g i</code>', 'all matches · ignore case', '<code>s/ /_/g</code>', 'every space'],
], minw=620) + mistake("rename 's/.txt/.md/' *     (dot not escaped, no anchor)", "rename 's/\\.txt$/.md/' *",
                       'An unescaped <code>.</code> matches any character, and without <code>$</code> the first “?txt” anywhere in the name is replaced, e.g. in <code>my_txt_notes.txt</code>.') + qc('Glob or regex? In a glob, <code>*.txt</code> means “anything ending in .txt”. What does <code>*</code> mean in a regex?', '“0 or more of the previous item”. The regex for “anything” is <code>.*</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>rename explained, then used in every field</h2>
  <p id="commands">Our build machine cannot install the <code>rename</code> package, so these results were produced by running <b>exactly the same Perl expression</b> on each name, the way rename does, and are labelled as verified typical output. On your Ubuntu machine: <code>sudo apt install rename</code>, and you will get the same names.</p>
''' + cmdcard_u(['the same change on many names: extension, prefix, spaces, case', 'cleaning names before upload, import or publishing', 'you want a preview of every change (<code>-n</code>)'],
               ['one file (mv is simpler)', 'moving files into other folders (mv, Lesson 3.2)', 'RHEL/Rocky without the Perl version (syntax differs)'])(
    'rename', 'rename', 'Perl rename',
    'Applies a Perl expression to each file name and renames the file if the name changed. Use <code>-n</code> first: it prints <code>rename(old, new)</code> for each file and changes nothing.',
    "rename [-n] [-v] [-f] 'PERLEXPR' FILE...", 'change',
    [('-n, --nono', 'show what would be renamed, change nothing', 'always first'),
     ('-v, --verbose', 'print “old renamed as new”', 'see and log'),
     ('-f, --force', 'overwrite existing files', 'rarely; risky'),
     ("'s/a/b/'", 'replace the first a with b', 'one change'),
     ("'s/a/b/g'", 'replace every a', 'spaces, dashes'),
     ("'s/a/b/i'", 'ignore case', '.JPEG, .jpeg'),
     ("'y/A-Z/a-z/'", 'translate letters one to one', 'lower / upper case'),
     ("'expr1; expr2'", 'several changes in order', 'complete clean-up')],
    dict(cmd="touch notes.txt data.txt\nrename -n 's/\\.txt$/.md/' *.txt", rec=R('touch notes.txt data.txt', "rename -n 's/\\.txt$/.md/' *.txt"), note='Only a preview: nothing is renamed until you run it again without <code>-n</code>.'),
    [('data', [
        V('Add the year in front of every CSV export.', 'touch sales.csv stock.csv', "rename -v 's/^/2026_/' *.csv\nls", '<code>^</code> = the start of the name; replacing it inserts text.'),
        V('Exports have dates as DD-MM-YYYY; make them sortable YYYY-MM-DD.', 'touch sales_06-11-2026.csv sales_31-10-2026.csv', "rename -v 's/(\\d{2})-(\\d{2})-(\\d{4})/$3-$2-$1/' *.csv\nls", 'Three groups are remembered and written back in a new order: $3-$2-$1. Now ls sorts them by date.')]),
     ('dev', [
        V('Change every .txt to .md (and nothing else).', 'touch notes.txt my_txt_notes.txt report.doc', "rename -v 's/\\.txt$/.md/' *\nls", '<code>\\.</code> is a real dot, <code>$</code> the end: my_txt_notes.txt keeps the “txt” in the middle.')]),
     ('sys', [
        V('Replace spaces with underscores (they break scripts).', "touch 'my file name.txt' 'test   data.csv' 'spaced out .log'", "rename -v 's/\\s+/_/g' *\nls", '<code>\\s+</code> = one or more spaces (so three spaces become one _), <code>g</code> = all of them.')]),
     ('ml', [
        V('Dataset images: lowercase, underscores and .jpg, all in one pass.', "touch 'IMG 0001.JPEG' 'IMG 0002.JPEG' 'Cat Photo.Jpeg'", "rename -v 'y/A-Z/a-z/; s/\\s+/_/g; s/\\.jpe?g$/.jpg/' *\nls", 'Three expressions run in order on each name. Consistent names avoid “file not found” on case-sensitive Linux training servers.')]),
     ('sec', [
        V('Make uploaded file names safe: keep only letters, digits, dot, dash and underscore.', "touch 'invoice (final).pdf' 'a;b.txt' 'ok_file.txt'", "rename -v 's/[^A-Za-z0-9._-]+/_/g' *\nls", 'Characters like <code>; ( ) space</code> can be abused in badly written scripts. An allow-list (<code>[^…]</code>) is safer than trying to block bad characters one by one.')]),
     ('qa', [
        V('A test: what happens if the new name already exists?', 'touch a.txt b.txt', "rename -v 's/a/b/' a.txt\nls", 'rename refuses to overwrite (unless -f). Both files are still there.')]),
     ('devops', [
        V('Versioned artefacts: add the build number before the extension.', 'touch app.jar worker.jar', "build=42\nrename -v \"s/\\\\.jar\\$/-b$build.jar/\" *.jar\nls", 'Double quotes let bash insert <code>$build</code>; Perl’s own <code>$</code> (end of name) must then be escaped as <code>\\$</code>.')]),
    ],
    anat=anatomy([('rename', 'cmd', 'command'), ('-n', 'opt', 'preview'), ("'s/\\.txt$/.md/'", 'arg', 'Perl expression'), ('*.txt', 'sep', 'files (a glob!)')], 'Two pattern languages in one line: the files are chosen by a <b>glob</b> (Lesson 3.4), the change is described by a <b>regex</b>.')
) + cmdcard_u(['you need a precise pattern: digits, words, positions', 'removing or extracting parts of a name', 'reordering parts with groups'],
               ['a fixed word is enough (plain text works too)', 'you are not sure: test on one name with <code>-n</code> first'])(
    'regex', 'regex', 'regular expressions in rename',
    'The left part of <code>s/…/…/</code> is a regular expression. These verified examples show what each building block really does to file names, including the surprising cases.',
    's/REGEX/REPLACEMENT/FLAGS', 'change',
    [('\\d / \\D', 'a digit / anything but a digit', 'numbers in names'),
     ('\\w / \\W', 'letter, digit or _ / anything else', 'clean characters'),
     ('\\s / \\S', 'whitespace / non-whitespace', 'spaces, tabs'),
     ('\\b / \\B', 'word boundary / no boundary', 'whole words only'),
     ('( ) and $1', 'remember and reuse', 'reorder, insert'),
     ('{n,m}', 'repeat n to m times', 'exact digit counts'),
     ('[^…]', 'any character not listed', 'allow-lists'),
     ('a|b', 'either a or b', 'several words')],
    dict(cmd="touch file123.txt\nrename -v 's/(\\d+)/_$1/' *.txt", rec=R('touch file123.txt', "rename -v 's/(\\d+)/_$1/' *.txt"), note='The group <code>(\\d+)</code> remembers “123”; the replacement writes “_” followed by it.'),
    [('data', [
        V('Remove all digits from names.', 'touch data123.csv v2_report.csv', "rename -v 's/\\d+//g' *\nls", '<code>\\d+</code> = a run of digits; <code>g</code> removes every run.'),
        V('Keep only the digits (careful!).', 'touch file123name.txt report_2024_version.txt log-07.txt', "rename -v 's/\\D+//g' *.txt\nls", '<code>\\D</code> also matches the dot and “txt”, so the extension disappears: 123, 2024, 07. A common classroom example shows “123.txt”; that is not what really happens.')]),
     ('dev', [
        V('Whole word only: prefix files that contain the word “report”.', 'touch report.txt weekly_report.txt finalreport.txt reporting_notes.txt', "rename -v 's/\\breport\\b/test_report/' *\nls", 'Only report.txt changes. weekly_report.txt is unchanged because <code>_</code> is a word character, so there is no boundary between “_” and “report”.'),
        V('Inside a word only: \\B (not a boundary).', 'touch word.txt sword.txt keyword_report.txt wording.txt', "rename -v 's/\\Bword/BLOCK/' *\nls", 'word.txt and wording.txt are <b>unchanged</b>: “word” is at the start of the name there, which is a boundary. Some notes show wording.txt → BLOCKing.txt; a real run proves otherwise.')]),
     ('sys', [
        V('Remove every non-word character (dots too!).', "touch 'hello-world@2024!.txt' Report_2024.txt 'my file.txt'", "rename -v 's/\\W//g' *\nls", 'The dot before the extension is a non-word character, so it is removed too, and capital letters are kept: Report_2024txt. To keep the extension, exclude the dot: <code>s/[^\\w.]//g</code>.')]),
     ('sec', [
        V('Names with accents or Indian scripts: \\w does not match them by default.', "touch 'Résumé (final).pdf'", "rename -v 's/[^\\w.-]+/_/g' *\nls", 'Perl sees é as two bytes that are not \\w, so “Résumé” becomes “R_sum”. Decide on purpose whether to keep Unicode names (Perl’s utf8 options) or transliterate them.')]),
    ]
) + mistake("rename 's/^(.*)\\.txt$/$1_$(date +%Y-%m-%d).txt/' *.txt", 'rename "s/\\\\.txt\\$/_$(date +%F).txt/" *.txt',
            'In single quotes bash never runs <code>$(date …)</code>; Perl reads <code>$(</code> as its own variable (the group IDs), so the name becomes something like <code>report_30033 30033date +%Y-%m-%d).txt</code> (verified). Use double quotes so bash inserts the date, and escape Perl’s <code>$</code> as <code>\\$</code>.') + cmdcard_u(['upper or lower case for all names', 'replacing several single characters at once', 'on RHEL/Rocky: the util-linux rename for simple text changes'],
               ['changing words (use s///)', 'Perl rename is not installed and patterns are needed (install it, or use a loop with mv)'])(
    'case', 'y/// · util-linux rename', 'case changes and the Red Hat rename',
    '<code>y/abc/xyz/</code> (or <code>tr</code>) replaces characters one for one: a→x, b→y, c→z. On RHEL, Rocky and Fedora, <code>rename</code> is a different program from util-linux: <code>rename FROM TO FILES</code>, plain text only.',
    "rename 'y/A-Z/a-z/' FILES   ·   (util-linux) rename FROM TO FILES", 'change',
    [("'y/A-Z/a-z/'", 'all capitals to small letters', 'web and Linux-friendly names'),
     ("'y/a-z/A-Z/'", 'all small letters to capitals', 'legacy systems'),
     ("'y/ /_/'", 'every space to _ (one for one)', 'simple cleanup'),
     ("'$_ = lc'", 'Perl lc(): lowercase (Unicode-aware with options)', 'alternative'),
     ('rename .jpeg .jpg *.jpeg', 'util-linux: replace first “.jpeg” with “.jpg”', 'RHEL/Rocky/Fedora'),
     ('rename -n / -v (util-linux)', 'no-act / verbose, same idea', 'preview there too'),
     ('rename --version', 'which rename do I have?', 'before using either syntax')],
    dict(cmd="touch Report.TXT IMAGE.PNG file.txt\nrename -v 'y/A-Z/a-z/' *", rec=R('touch Report.TXT IMAGE.PNG file.txt', "rename -v 'y/A-Z/a-z/' *"), note='file.txt was already lowercase, so it is skipped (no line printed).'),
    [('web', [
        V('A web server is case-sensitive: Logo.PNG ≠ logo.png. Make every asset lowercase.', 'touch Logo.PNG Banner.JPG style.css', "rename -v 'y/A-Z/a-z/' *\nls", 'Windows and macOS ignore case, Linux web servers do not: a link to logo.png gives 404 for Logo.PNG.')]),
     ('sys', [
        dict(situation='On Rocky Linux: change .jpeg to .jpg with util-linux rename.', cmd='rename -v .jpeg .jpg *.jpeg', typical="`a.jpeg' -> `a.jpg'\n`b.jpeg' -> `b.jpg'",
             why='Typical output of util-linux rename (RHEL/Rocky/Fedora). No regex: it replaces the first occurrence of the plain text.')]),
     ('devops', [
        dict(situation='A script must work on Ubuntu and on RHEL: check which rename exists.', cmd='rename --version', typical='/usr/bin/rename using File::Rename version 2.02, File::Rename::Options version 1.99\n(on RHEL: rename from util-linux 2.37.4)',
             why='Typical. Scripts that must run everywhere often avoid rename and use a loop with mv instead (see Script it).')]),
    ]
) + undo('If a bulk rename went wrong…', [
    ('Before:', 'always <code>-n</code> first, and read every line. Then the same command without -n.'),
    ('Reverse a simple change:', 'swap the parts: <code>s/\\.md$/.txt/</code> undoes <code>s/\\.txt$/.md/</code>.'),
    ('Log what you did:', 'run with <code>-v</code> and save it: <code>rename -v … | tee rename.log</code>; each line tells you the old name.'),
    ('Two names became one:', 'rename refuses (no overwrite) and reports it; never add <code>-f</code> unless you are sure.'),
    ('Big jobs:', 'copy the folder first (<code>cp -a photos photos.bak</code>), rename the copy, check, then swap.'),
]) + errors('The errors and traps students hit with rename. Messages from the rename program itself are typical; the name results were verified.', [
    dict(cmd="rename 's/a/b/' x.txt", setup='', meaning='On our build machine rename is not installed: the same message appears on minimal Ubuntu systems.', fix='<code>sudo apt install rename</code> (Ubuntu/Debian).'),
    dict(cmd="echo 'invoice(final).pdf' | perl -lpe 's/(/_/'", meaning='( starts a group in a regex; alone it is a syntax error. (Tested with perl -lpe, the same engine rename uses.)', fix='Escape special characters: <code>s/\\(/_/</code>. Special: <code>. * + ? ( ) [ ] { } ^ $ | \\ /</code>.'),
    dict(cmd="echo 'a.b.txt' | perl -lpe 's/./_/g'", meaning='Not an error message, but a classic mistake: an unescaped . matches every character.', fix='<code>s/\\./_/g</code> replaces only real dots.'),
]) + stepper([
    ('1. Look at the names', '<p><code>ls | head</code>: what is wrong with them?</p>', 'Behind the screen: just reading the folder.'),
    ('2. Choose the files', '<p>A glob: <code>*.JPEG</code>, <code>IMG*</code>, or <code>*</code>.</p>', 'Behind the screen: bash expands it to the file list.'),
    ('3. Write the expression', "<p><code>'y/A-Z/a-z/; s/\\s+/_/g; s/\\.jpeg$/.jpg/'</code></p>", 'Behind the screen: Perl code run once per name.'),
    ('4. Preview', "<p><code>rename -n '…' *</code>: read every line.</p>", 'Behind the screen: the code runs, but rename() is not called.'),
    ('5. Run and log', "<p><code>rename -v '…' * | tee rename.log</code></p>", 'Behind the screen: one rename() system call per changed name, like mv.'),
    ('6. Check', '<p><code>ls</code>: all names as expected?</p>', 'Behind the screen: the data is never touched, only names.'),
]) + qc('You must turn <code>2026-11-06_sales.csv</code> into <code>sales_2026-11-06.csv</code>. Which expression?', "<code>s/^(\\d{4}-\\d{2}-\\d{2})_(.*)\\.csv$/$2_$1.csv/</code>: two groups, swapped, extension kept.") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def nm(parts, hl, note, tone='blue'):
    o, x = '', 14
    for k, p in enumerate(parts):
        w = 18 + len(p) * 7.2
        o += label_box(round(x), 40, round(w), 34, [p], ('green' if k in hl else 'card'), 9.6)
        x += w + 4
    return o + t(180, 110, note, 9, tone, bold=True)
see = [nm(['IMG', ' ', '0001', '.', 'JPEG'], [], 'The original name.') + cap('IMG 0001.JPEG', '', 'card', y=150, h=34),
       nm(['img', ' ', '0001', '.', 'jpeg'], [0, 4], 'y/A-Z/a-z/: every capital → small.', 'green') + cap('img 0001.jpeg', '', 'blue', y=150, h=34),
       nm(['img', '_', '0001', '.', 'jpeg'], [1], 's/\\s+/_/g: spaces → _.', 'green') + cap('img_0001.jpeg', '', 'blue', y=150, h=34),
       nm(['img', '_', '0001', '.jpg'], [3], 's/\\.jpeg$/.jpg/: only at the end.', 'green') + cap('img_0001.jpg', '', 'green', y=150, h=34),
       (t(180, 30, 'Three steps, in order', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start', mono=True) for k, s in enumerate(['y/A-Z/a-z/', 's/\\s+/_/g', 's/\\.jpeg$/.jpg/', '→ one rename() per file'])) + cap('Order matters: lowercase before the .jpeg rule.', '', 'green', y=150, h=34))]
def eng(hl, note, tone='blue'):
    items = [('bash: expand * → 300 names', 'card'), ('rename: for each name → $_', 'acc'), ('Perl runs your code on $_', 'violet'), ('changed? → rename(old, new)', 'green'), ('-n? → only print rename(old, new)', 'amber')]
    o = ''.join(label_box(14, 10 + k * 31, 332, 26, [s], tn if k in hl else 'card', 8.6) for k, (s, tn) in enumerate(items))
    return o + t(180, 175, note, 8.8, tone, bold=True)
behind = [eng([0, 1], 'bash builds the list; rename takes one name at a time.'),
          eng([2], 'y/// translates letters in $_.', 'violet'),
          eng([2], 's/// replaces the first (or, with g, every) match.', 'violet'),
          eng([3], 'The name changed, so rename() is called.', 'green'),
          eng([4], 'With -n the last step only prints.', 'amber')]
two = anim_two('How one file name is transformed', 'Inside rename',
               'The name IMG 0001.JPEG changes step by step: lowercase, spaces to underscore, .jpeg to .jpg.',
               'bash expands the file list; rename puts each name in $_, runs the Perl code, and calls rename() if the name changed, or only prints with -n.', see, behind,
               ['The photo’s original name.',
                '<code>y/A-Z/a-z/</code> makes every capital letter small.',
                '<code>s/\\s+/_/g</code> turns the space into an underscore.',
                '<code>s/\\.jpeg$/.jpg/</code> shortens the extension, only at the end.',
                'All three run in order for every file.'],
               ['bash expands the glob; rename receives a plain list.',
                'Each name goes into Perl’s $_ variable.',
                'Your expressions change $_ step by step.',
                'If the result differs, rename() renames the file (like mv).',
                '-n prints the plan instead: the safe preview.'])

z1 = term(14, 14, 332, 100, ["$ rename 's/\\.txt$/_$(date +%F).txt/' *.txt", '$ ls', ('report_30033 30033date +%F).txt', 'err')], title='riya@laptop', size=7.2) + cap('Single quotes: a strange name!', '', 'red', y=150, h=34)
z2 = label_box(20, 20, 320, 70, ['bash: single quotes → passed unchanged', 'Perl: $( is a variable = your group IDs', 'so “$(date +%F)” becomes “30033 30033date +%F)”'], 'violet', 8.8) + cap('Perl saw $( and replaced it.', '', 'violet', y=150, h=34)
z3 = term(14, 14, 332, 100, ['$ rename -n "s/\\\\.txt\\$/_$(date +%F).txt/" *.txt', ('rename(report.txt, report_2026-11-06.txt)', 'acc')], title='riya@laptop', size=7.2) + cap('Double quotes: bash inserts the date first.', '', 'green', y=150, h=34)
z4 = label_box(20, 20, 320, 70, ['inside double quotes:', '\\$ → Perl’s end-of-name $', '\\\\. → Perl gets \\. (a real dot)'], 'amber', 8.8) + cap('Escape what belongs to Perl.', '', 'amber', y=150, h=34)
z5 = (t(180, 30, 'Quote rule for rename', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• normally: single quotes', '• need a bash value: double quotes', '• then escape Perl’s $ and \\', '• always preview with -n'])) + cap('Preview catches every quoting mistake.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario', 'The date that did not appear',
              'Riya adds today’s date to reports. The names below were verified with the same Perl expression.',
              'Quotes in rename', 'With single quotes $(date) is read by Perl as a variable and produces a broken name; with double quotes bash inserts the date and Perl’s symbols are escaped.', [z1, z2, z3, z4, z5],
              ['With single quotes, the new name is nonsense.',
               'bash did not run <code>$(date)</code>; Perl read <code>$(</code> (your group IDs, here 30033).',
               'With double quotes, bash runs date first and Perl receives the real date.',
               'Inside double quotes, Perl’s own <code>$</code> and <code>\\</code> must be escaped.',
               'The -n preview shows every such mistake before it happens.'],
              hid='scenario-quotes')

dx = dissect('Layer by layer: one rename command',
    "Take <code>rename -v 's/\\s+/_/g' *.txt</code>. Open each layer; the outputs are real runs on our build machine (bash and Perl are installed, the rename package is not).", [
    dict(key='glob', name='Glob *.txt', sub='bash chooses files',
         why='rename itself does not search the folder.',
         how='bash expands *.txt into the list of names.',
         impl='Pathname expansion (Lesson 3.4).', used='Every rename command.',
         cmd="touch 'my notes.txt' 'q1 data.txt'; printf '[%s]\\n' *.txt"),
    dict(key='perl', name='Perl $_', sub='the name as text',
         why='Perl is a text-processing language.',
         how='Each name is put into $_; your code changes $_.',
         impl='rename is a Perl script (File::Rename).', used='s///, y///, lc, sprintf…',
         cmd="perl -e '$_ = \"my notes.txt\"; s/\\s+/_/g; print \"$_\\n\"'"),
    dict(key='regex', name='Regex \\s+', sub='what to match',
         why='Describe “one or more spaces” in one token.',
         how='\\s = space or tab; + = one or more; g = all matches.',
         impl='Perl’s regex engine.', used='grep -P, sed -E, Python re.',
         cmd="echo 'test   data.csv' | perl -lpe 's/\\s+/_/g'"),
    dict(key='call', name='rename()', sub='the system call',
         why='Changing a name needs the kernel.',
         how='Same call as mv on one file system: instant, data untouched.',
         impl='renameat2() (Lesson 3.2).', used='mv, rename, every program.',
         cmd="touch 'a b.txt'; perl -e 'rename(\"a b.txt\", \"a_b.txt\") or die'; ls"),
], hint='From the file list to the system call. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How s/// and y/// change a name</h2>
  <p>Left: one photo name, changed step by step. Right: what rename does inside.</p>
''' + two + s1 + dx + qc('Why must <code>y/A-Z/a-z/</code> come before <code>s/\\.jpeg$/.jpg/</code> when the files end in .JPEG?', 'Because the second rule looks for lowercase “.jpeg”. After y/// the extension is lowercase, so it matches. (Or use the i flag: <code>s/\\.jpeg$/.jpg/i</code>.)') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Bulk renaming at work</h2>
''' + usecase(term(8, 14, 104, 62, [("$ rename 's/(..)-", 'prompt'), ("(..)-(....)/'", 'acc')], title='data', size=6.4, step=12),
              '1. Sortable data files', 'Data teams turn DD-MM-YYYY into YYYY-MM-DD so files sort by date and match partition naming.', ['Exports', '*rename groups', 'sorted']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['lowercase', 'no spaces'], 'green', 8.6), '2. Web and media assets',
    'Web developers and media teams normalise image names for case-sensitive Linux servers and CDNs.', ['Photos', '*y/// s///', 'no 404s']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ rename -n', 'prompt'), ('… | tee log', 'acc')], title='ops', size=6.4, step=12),
    '3. Log and archive housekeeping', 'Admins rename rotated or migrated files to a new scheme, with a preview and a log of every change.', ['Old scheme', '*rename -v', 'new scheme']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['[^A-Za-z0-9._-]', '→ _'], 'red', 8.6), '4. Safe upload names',
    'Security reviews require uploaded files to have safe names; an allow-list regex removes risky characters.', ['Upload', '*sanitise', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['img_0001.jpg', 'label_…'], 'violet', 8.6), '5. ML datasets',
    'ML engineers rename thousands of images into class_number.jpg form so training scripts can read labels from names.', ['Raw images', '*rename', 'clean dataset']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Renaming without the rename package: these use only bash and mv, so they work on every system, and were really run on our build machine.', [
    dict(level='b', title='Change extensions with a loop', scenario='.txt → .md without rename.',
         cmd='touch a.txt b.txt && for f in *.txt; do mv -- "$f" "${f%.txt}.md"; done && ls',
         explain='<code>${f%.txt}</code> removes “.txt” from the end of the variable (Lesson 12.4).'),
    dict(level='b', title='Add a prefix with a loop', scenario='Prefix every CSV with 2026_.',
         cmd='touch s.csv t.csv && for f in *.csv; do mv -- "$f" "2026_$f"; done && ls',
         explain='Plain text in front of "$f".'),
    dict(level='i', title='Spaces to underscores with bash', scenario='No rename installed.',
         cmd="touch 'my file.txt' 'q1 data.csv' && for f in *\\ *; do mv -- \"$f\" \"${f// /_}\"; done && ls",
         explain='<code>${f// /_}</code> replaces every space in the variable.'),
    dict(level='i', title='Lowercase with bash', scenario='Make all names lowercase.',
         cmd='touch Report.TXT IMAGE.PNG && for f in *; do mv -- "$f" "${f,,}"; done && ls',
         explain='<code>${f,,}</code> = lowercase (bash 4+).'),
    dict(level='a', title='Numbered names in a fixed order', scenario='Rename photos to photo_001.jpg … by sorted name.',
         cmd='touch c.jpg a.jpg b.jpg && n=1; for f in *.jpg; do mv -- "$f" "$(printf "photo_%03d.jpg" "$n")"; n=$((n+1)); done; ls',
         explain='printf builds padded numbers; the glob sorts names alphabetically.'),
], extra=build_up('a clean-up for phone photos, previewed', 'Riya builds the expression one step at a time and checks each with the same Perl code rename uses (perl -lpe).',
    "printf 'IMG 0001.JPEG\\nIMG 0002.JPEG\\nCat Photo.Jpeg\\n' > names.txt", [
    ("perl -lpe 'y/A-Z/a-z/' names.txt", '1. Lowercase.'),
    ("perl -lpe 'y/A-Z/a-z/; s/\\s+/_/g' names.txt", '2. Spaces to underscores.'),
    ("perl -lpe 'y/A-Z/a-z/; s/\\s+/_/g; s/\\.jpe?g$/.jpg/' names.txt", '3. Shorter extension (also catches .jpg already).'),
    ("perl -pe 's/^/rename(/; chomp; $_ .= \")\\n\"' names.txt | head -1; echo \"→ now run: rename 'y/A-Z/a-z/; s/\\\\s+/_/g; s/\\\\.jpe?g\\$/.jpg/' *\"", '4. Happy with the result: run it with rename on the real files.'),
])) + which('Choosing the right way.', [
    ('One file', 'mv old new', 'Simplest.', 'rename for a single file.'),
    ('Same change, many files', "rename 's/…/…/' *", 'One command.', '300 mv commands.'),
    ('Be sure first', 'rename -n …', 'Preview.', 'Running without -n first.'),
    ('Extension only', "s/\\.txt$/.md/", 'Anchored.', "s/.txt/.md/ (unescaped, unanchored)."),
    ('Case', "y/A-Z/a-z/", 'All letters.', 'Forgetting the order of steps.'),
    ('A bash value inside', 'rename "s/…$x/…/"', 'bash expands $x.', "Single quotes around $(date)."),
    ('No rename installed', 'for f in …; do mv …', 'Works everywhere.', 'Parsing ls output.'),
    ('RHEL / Rocky', 'rename FROM TO files', 'util-linux syntax.', 'Perl s/// there (fails).'),
]) + keys('Shortcuts and helpers for renaming.', [
    ("perl -lpe 's/…/…/'", 'test an expression on lines of text; -l keeps \\s from eating the newline', "echo 'IMG 1.JPEG' | perl -lpe 'y/A-Z/a-z/'"),
    ('${f%.txt}', 'remove a suffix from a variable', 'mv "$f" "${f%.txt}.md"'),
    ('${f// /_}', 'replace all spaces in a variable', 'mv "$f" "${f// /_}"'),
    ('${f,,} / ${f^^}', 'lowercase / uppercase a variable', 'mv "$f" "${f,,}"'),
    ('mv --', 'protect names that start with -', 'mv -- "$f" new'),
    ('| tee rename.log', 'keep a record of -v output', "rename -v '…' * | tee rename.log"),
]) + scriptit('clean-names.sh', 'A portable clean-up that works on Ubuntu and RHEL alike, because it uses only bash and mv: lowercase, spaces to underscores, unsafe characters removed, and a dry-run mode.',
'''#!/bin/bash
# clean-names.sh [-n]: lowercase, spaces -> _, only [a-z0-9._-]
dry=0; [ "$1" = "-n" ] && dry=1
touch 'IMG 0001.JPEG' 'Invoice (Final).PDF' 'ok_name.txt'   # demo files
for f in *; do
  [ -f "$f" ] || continue
  [ "$f" = "$(basename "$0")" ] && continue
  new=${f,,}                  # lowercase
  new=${new// /_}             # spaces to _
  new=${new//[^a-z0-9._-]/}   # drop anything else
  [ "$f" = "$new" ] && continue
  if [ -e "$new" ]; then echo "skip: $new exists"; continue; fi
  if [ $dry -eq 1 ]; then echo "would rename: $f -> $new"; else mv -- "$f" "$new" && echo "renamed: $f -> $new"; fi
done''',
'<p>Run it with <code>-n</code> first, exactly like rename. The <code>${var//pattern/}</code> forms use globs, not regex: <code>[^a-z0-9._-]</code> is a bracket expression (Lesson 3.4).</p>') + puzzle_answer('The expression was in <b>single quotes</b>, so bash did not run <code>$(date +%F)</code>; it was passed to Perl as text. In Perl, <code>$(</code> is a built-in variable holding your group IDs, so Perl inserted those numbers followed by “date +%F)”. Fix: use <b>double quotes</b> so bash inserts the date first, and escape Perl’s own symbols: <code>rename "s/\\\\.txt\\$/_$(date +%F).txt/" *.txt</code>. And always preview with <code>-n</code>.') + qc('Which command shows how <code>rename \'s/ /_/g\' *</code> would rename files, without renaming anything?', "<code>rename -n 's/ /_/g' *</code>") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-wildcards-and-globbing/">Lesson 3.4</a> (globs choose the files) and <a href="../02-copying-moving-and-syncing-cp-mv-and-rsync/">Lesson 3.2</a> (mv renames one file).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
