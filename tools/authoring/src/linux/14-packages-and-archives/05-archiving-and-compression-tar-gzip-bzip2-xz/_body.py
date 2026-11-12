import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# A real project folder with deterministic text data (python3 with a fixed seed), used by every command below.
AR = r"""rm -rf ~/proj ~/bk ~/x; mkdir -p ~/proj/logs ~/proj/src ~/proj/cache ~/bk ~/x; cd ~/proj
python3 - <<'EOF'
import random
random.seed(14)
lv = ['INFO'] * 7 + ['WARN', 'ERROR']
for d in range(1, 4):
    with open(f'logs/app-2026-11-0{d}.log', 'w') as f:
        for i in range(4000):
            f.write(f'2026-11-0{d} {i//167:02d}:{i%60:02d}:{(i*7)%60:02d} {random.choice(lv)} order={random.randint(1000,9999)} user=u{random.randint(1,300)} ms={random.randint(5,900)}\n')
with open('src/app.py', 'w') as f:
    f.write('def main():\n    print("orders service")\n\nif __name__ == "__main__":\n    main()\n')
with open('README.md', 'w') as f:
    f.write('# orders service\nRun: python3 src/app.py\n')
with open('cache/blob.bin', 'wb') as f:
    f.write(random.randbytes(200000))
EOF
touch -d '2026-11-01 10:00' logs/* src/* README.md cache/*"""

HOOK = hook('Riya has to send the <code>orders</code> project (code, three days of logs, a cache) to a colleague, keep a nightly backup of it, and free disk space on a server whose <code>/var/log</code> is full of old logs. All three are the same two jobs: <b>archiving</b> (many files into one, with names, folders and permissions: <code>tar</code>, <code>zip</code>) and <b>compression</b> (making data smaller: <code>gzip</code>, <code>bzip2</code>, <code>xz</code>, <code>zstd</code>). This lesson measures, on real files, how much each tool saves and how fast it is.',
    ['create, list and extract tar archives (c, t, x, v, f, -C) and compress them with z, j and J',
     'compress single files with gzip, bzip2 and xz, read them without unpacking (zcat, zless, zgrep), and pick a level',
     'use zip and unzip for Windows-friendly archives, and exclude, append and extract single files',
     'make dated, verified backups and know when compression helps (text) and when it does not (already compressed data)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'send, back up, free space'),
    ('decide', 'Which tool?', 2, 'the quick chart'),
    ('definition', 'Archive vs compress', 5, 'simple meaning + 4 depths'),
    ('types', 'gzip vs bzip2 vs xz vs zip', 5, 'real measurements'),
    ('commands', 'By field', 15, 'tar, gzip, xz, zip'),
    ('animation', 'See it happen', 4, 'tar + gzip'),
    ('run', 'Run on your PC', 4, 'zstd and Windows'),
    ('lab', 'Practice lab', 7, 'a verified backup'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I want to… → use', [
    ('bundle a folder (Linux to Linux)', 'tar -czf name.tar.gz DIR', 'the standard'),
    ('smallest file, time does not matter', 'tar -cJf name.tar.xz DIR', 'releases'),
    ('send to Windows users', 'zip -r name.zip DIR', 'opens everywhere'),
    ('compress one big log', 'gzip FILE (or xz)', 'replaces the file'),
    ('look inside without extracting', 'tar -tzf · unzip -l · zcat · zgrep', 'read-only'),
    ('get one file back', 'tar -xzf A.tar.gz path/in/archive', 'not everything'),
])

cmap = concept_map(
    [('14.4', 'Source builds', 'tarballs'), ('3.2', 'cp and rsync', 'copying'), ('9.1', 'Permissions', 'what tar keeps')],
    ['archive vs compression', 'tar c t x, f, v, -C', 'z j J: gzip bzip2 xz', 'gzip, gunzip, zcat, zgrep', 'zip and unzip', 'exclude, append, single files', 'dated, verified backups'],
    [('18.2', 'logrotate', 'compresses old logs'), ('19.4', 'Checksums', 'verify archives'), ('17.4', 'cron', 'nightly backups'), ('16.6', 'scp/rsync', 'moving archives')],
    'tar puts many files into one; gzip, bzip2 and xz make it smaller; zip does both for Windows.')

sc = (term(20, 14, 316, 156, ['$ tar -czf proj.tar.gz proj', '$ ls -lh proj.tar.gz', ('-rw-r--r-- … 318K proj.tar.gz', 'out'), '$ tar -tzf proj.tar.gz | head -3', ('proj/ proj/logs/ …', 'out'), '$ gzip -l app.log.gz', ('ratio 80.3%', 'acc')], title='riya@laptop: ~', prompt='$', size=6.6, step=17)
      + t(352, 36, 'Two jobs:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['archive: tar, zip', '  many → one', 'compress: gzip,', '  bzip2, xz, zstd', '  big → small'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Send it, back it up, free the disk</h2>
  <div class="story">
''' + puzzle('Riya’s <code>tar -czf backup.tar.gz ~/proj</code> prints “Removing leading `/’ from member names”. Is the backup broken? Then she gzips <code>cache/blob.bin</code> and the result is <i>bigger</i> than the original. And her colleague on Windows double-clicks <code>proj.tar.xz</code> and gets “cannot open file”. Three surprises, one lesson.') + '''
    <p class="narration">On Riya’s laptop (every size in this lesson was measured on our build machine).</p>
''' + scene('A terminal: tar -czf creates proj.tar.gz, ls -lh shows its size, tar -tzf lists the contents and gzip -l shows the compression ratio.', sc,
            '<tspan font-weight="700" class="s-acc">tar</tspan> bundles, <tspan font-weight="700" class="s-acc">gzip</tspan> shrinks.') + '''
K> Why two tools? Windows does both with zip.
A> Unix style: one tool per job. <code>tar</code> (tape archive) only joins files, keeping names, folders, owners, permissions and times. <code>gzip</code>, <code>bzip2</code> and <code>xz</code> only compress one stream. Together: <code>.tar.gz</code>, <code>.tar.bz2</code>, <code>.tar.xz</code>. tar’s <code>z</code>, <code>j</code> and <code>J</code> options call them for you.
R> And which one is best?
A> Let’s measure it on Riya’s real files.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Many files go into tar which makes one archive file, then gzip makes it smaller: proj/ becomes proj.tar becomes proj.tar.gz.">'
       + ''.join(label_box(14, 26 + i * 30, 120, 24, [n], 'card', 8.2) for i, n in enumerate(['logs/app-1.log', 'logs/app-2.log', 'src/app.py', 'README.md', 'cache/blob.bin']))
       + arrow(140, 100, 200, 100) + label_box(206, 70, 140, 60, ['tar', 'proj.tar (one file)'], 'blue', 9)
       + arrow(352, 100, 412, 100) + label_box(418, 70, 140, 60, ['gzip', 'proj.tar.gz (smaller)'], 'green', 9)
       + t(320, 192, 'archive = many → one     compression = big → small', 9, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Archiving and compression at four depths', [
    ('v', 'No jargon: a suitcase and vacuum bag', '      <p>tar packs the suitcase; gzip squeezes the air out.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>tar -czf proj.tar.gz proj</code>: create (c), gzip (z), file name (f).</li>
        <li><code>tar -tzf proj.tar.gz</code>: list (t). <code>tar -xzf proj.tar.gz</code>: extract (x).</li>
        <li><code>gzip big.log</code> → big.log.gz; <code>gunzip big.log.gz</code> back.</li>
        <li><code>zip -r proj.zip proj</code>, <code>unzip proj.zip</code>.</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>z</code> gzip (fast, everywhere), <code>j</code> bzip2 (smaller, slow), <code>J</code> xz (usually smallest, slowest to compress, fast to decompress); modern tar also guesses from the name with <code>-a</code>, and extraction auto-detects.</li>
        <li>Levels <code>-1</code> (fast) to <code>-9</code> (small): <code>gzip -9</code>, <code>xz -6</code> default; <code>XZ_OPT=-9 tar -cJf …</code>.</li>
        <li>gzip, bzip2 and xz <b>replace</b> the original file; <code>-k</code> keeps it, <code>-c</code> writes to stdout.</li>
        <li>tar strips the leading <code>/</code> so extracting never overwrites system paths by surprise; use <code>-C DIR</code> to choose where to extract.</li>
      </ul>'''),
    ('a', 'Behind the screen: blocks, dictionaries and entropy', '''      <ul>
        <li>A tar file is a sequence of 512-byte headers (name, mode, owner, size, mtime) each followed by the file’s data, ending with two zero blocks: no index, so listing reads the whole archive.</li>
        <li>gzip uses DEFLATE (LZ77 + Huffman) with a 32 KB window; bzip2 the Burrows–Wheeler transform; xz LZMA2 with windows up to 64 MB+, which is why it finds more repetition.</li>
        <li>Random or already-compressed data (JPEG, MP4, .gz, encrypted files) has high <b>entropy</b>: nothing to squeeze, and headers make it slightly larger.</li>
        <li>zip compresses each file separately and keeps a central directory at the end: fast single-file extraction, worse ratio than .tar.xz.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Archiving and compression</h2>
''' + def_block(
    '<b>Archiving</b> combines many files and directories into a single file while keeping their names, structure and metadata; on Linux the standard tool is <b>tar</b>. <b>Compression</b> encodes data so it takes fewer bytes; <b>gzip</b>, <b>bzip2</b> and <b>xz</b> each compress one file or stream. A compressed archive (<code>.tar.gz</code>, <code>.tgz</code>, <code>.tar.xz</code>) uses both; <b>zip</b> archives and compresses in one format.',
    'tar joins, gzip/bzip2/xz shrink, zip does both.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Archive', 'Many files in one.'),
    ('Tarball', 'A .tar(.gz) archive.'),
    ('Compression ratio', 'How much smaller.'),
    ('Level', '-1 fast … -9 small.'),
    ('Lossless', 'Exact original comes back.'),
    ('Entropy', 'How random data is.'),
    ('Member', 'A file inside an archive.'),
    ('-C DIR', 'Change to DIR first.'),
]) + '\n' + names('Where the names come from.', [
    ('tar', 'tape archive', '1979, for tape drives.'),
    ('gzip', 'GNU zip', '1992.'),
    ('bzip2', 'block-sorting zip, v2', '1996.'),
    ('xz', 'the LZMA “xz” format', '2009.'),
    ('zstd', 'Zstandard', 'Facebook, 2016.'),
    ('zip', 'fast (“zip along”)', 'PKZIP, 1989.'),
    ('.tgz', '.tar.gz short form', 'Old DOS 8.3 names.'),
    ('cpio', 'copy in/out', 'Used inside .rpm and initramfs.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Create', '<code>tar -czf A.tar.gz DIR</code>'),
    ('List', '<code>tar -tzf A.tar.gz</code>'),
    ('Extract', '<code>tar -xzf A.tar.gz -C DIR</code>'),
    ('One file', '<code>gzip -k FILE</code>'),
    ('Read compressed', '<code>zcat · zless · zgrep</code>'),
    ('For Windows', '<code>zip -r A.zip DIR</code>'),
]) + '\n' + lv + didyou('The letters in <code>tar -czvf</code> do not need a dash at all (<code>tar czvf</code>, the old style), but <code>f</code> must come last because the next word is its file name: <code>tar -cfz x.tar</code> creates an archive called <code>z</code>.') + '''
EXAM> “What is the difference between tar and gzip?” → tar archives (joins many files into one, keeping metadata) without compressing; gzip compresses a single file. tar -z runs gzip on the archive.
''' + qc('Which option letters create a bzip2-compressed tar archive?', 'tar -cjf name.tar.bz2 DIR (j = bzip2).') + mistake('tar -czf ~/proj proj.tar.gz   (arguments swapped)',
    'tar -czf proj.tar.gz ~/proj   (archive name right after f)',
    'With the order swapped, tar tries to write an archive named after your folder and fails, or worse, overwrites a file.') + mistake('extracting an unknown archive straight into your home',
    'tar -tzf A.tar.gz | head first; then tar -xzf A.tar.gz -C ~/x',
    'Some archives have no top folder and spill hundreds of files, or overwrite files with the same names.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>gzip vs bzip2 vs xz vs zip, measured</h2>
  <p>Measured on our build machine on the 3 log files (631,464 bytes of text) of Riya’s project; see the commands card for the run.</p>
''' + table(['Tool', 'Extension', 'tar option', 'Ratio on text', 'Speed', 'Best for'], [
    ['gzip', '.gz', '<code>z</code>', 'good (19% here)', 'fast', 'everyday, logs, web'],
    ['bzip2', '.bz2', '<code>j</code>', 'best on these logs (12%)', 'slow', 'older releases'],
    ['xz', '.xz', '<code>J</code>', 'usually best (14% here)', 'slowest to compress', 'software releases, kernels'],
    ['zstd', '.zst', '<code>--zstd</code>', 'like xz at high levels', 'very fast', 'modern distros, backups'],
    ['zip', '.zip', '(separate tool)', 'like gzip', 'fast', 'Windows / macOS users'],
], minw=640) + table(['tar letter', 'Meaning'], [
    ['<code>c</code>', 'create'], ['<code>t</code>', 'list (table of contents)'], ['<code>x</code>', 'extract'],
    ['<code>r</code> / <code>u</code>', 'append / update (uncompressed only)'], ['<code>f NAME</code>', 'archive file'],
    ['<code>v</code>', 'verbose'], ['<code>z j J</code>', 'gzip, bzip2, xz'], ['<code>-C DIR</code>', 'change directory'],
    ['<code>--exclude=PAT</code>', 'skip matching'], ['<code>-p</code>', 'keep permissions (default as root)'],
], minw=420) + qc('On Riya’s logs, which compressor won?', 'bzip2 (12%), ahead of xz (14%) and gzip (19%): log lines full of random numbers suit bzip2’s block sorting. On most source code and mixed data xz wins. Measure your own data.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>tar, gzip, bzip2, xz and zip, then used in every field</h2>
  <p id="commands">Every command below really runs on our build machine on Riya’s project in <code>~/proj</code>: three log files (4,000 lines each, generated with a fixed seed so numbers repeat), a little code, and a 200 KB random cache file.</p>
''' + cmdcard_u(['bundling folders', 'backups', 'moving projects'],
               ['archiving a folder into itself'])(
    'tar', 'tar -czf · -tzf · -xzf · -C · -v', 'tar: create, list, extract',
    '<code>c</code> creates, <code>t</code> lists, <code>x</code> extracts; <code>f NAME</code> names the archive; <code>z</code> gzips it; <code>v</code> prints each member; <code>-C DIR</code> runs in DIR (extract into it, or archive relative to it).',
    'tar -czf A.tar.gz DIR   ·   tar -tzf A.tar.gz   ·   tar -xzf A.tar.gz -C DEST', 'change',
    [('-c -f NAME', 'create', 'archive'),
     ('-t', 'list', 'check'),
     ('-x', 'extract', 'restore'),
     ('-z', 'gzip', '.tar.gz'),
     ('-v', 'verbose', 'see members'),
     ('-C DIR', 'change dir', 'where to'),
     ('-tvf', 'long list', 'permissions, sizes')],
    dict(setup=AR, cmd="cd ~\ntar -czf bk/proj.tar.gz proj\ntar -tzf bk/proj.tar.gz | sort\ntar -xzf bk/proj.tar.gz -C ~/x && diff -r proj x/proj && echo 'extracted copy is identical'", note='diff -r prints nothing when the trees are the same.'),
    [('sys', [
        dict(situation='Absolute path: tar strips the leading /.', setup=AR, cmd="tar -czf ~/bk/abs.tar.gz $HOME/proj/README.md 2>&1 | sed \"s|$HOME|~|\"; tar -tzf ~/bk/abs.tar.gz", why='The puzzle: not an error; members are stored relative so extraction cannot overwrite system paths.')]),
     ('devops', [
        dict(situation='Archive relative to a directory with -C.', setup=AR, cmd="tar -czf ~/bk/logs.tar.gz -C ~/proj logs; tar -tzf ~/bk/logs.tar.gz | head -2", why='No home path inside the archive.')]),
    ],
    anat=anatomy([('tar', 'cmd', 'archiver'), ('-czf', 'opt', 'create, gzip, file'), ('proj.tar.gz', 'arg', 'archive name (after f)'), ('proj', 'arg', 'what to put in')], 'Archive name first, contents after.')
) + cmdcard_u(['comparing ratio and time'],
               ['xz -9 on huge data when a quick result is needed'])(
    'compare', 'tar -czf / -cjf / -cJf · ls -l · time', 'gzip vs bzip2 vs xz',
    'The same folder with three compressors: z (gzip), j (bzip2) and J (xz). We compare sizes in bytes and the CPU time each takes.',
    'tar -cJf proj.tar.xz proj   ·   ls -l proj.tar.*', 'safe',
    [('z', 'gzip', 'balance'),
     ('j', 'bzip2', 'old'),
     ('J', 'xz', 'smallest'),
     ('-a', 'by extension', 'auto'),
     ('XZ_OPT=-9', 'level for xz', 'max'),
     ('GZIP=-9', 'old env for gzip', 'deprecated')],
    dict(setup=AR, cmd="cd ~/proj\nraw=$(cat logs/*.log | wc -c); echo \"logs uncompressed: $raw bytes\"\nfor c in gzip bzip2 xz; do s=$(cat logs/*.log | $c -c | wc -c); echo \"$c: $s bytes ($(( s * 100 / raw ))% of original)\"; done", note='A surprise: on these logs bzip2 beats xz (random numbers in every line suit block sorting). On most other data xz is smallest. gzip is the biggest but by far the fastest. Always measure on your own data.'),
    [('data', [
        dict(situation='Lossless: every compressor gives back the exact bytes.', setup=AR, cmd="cd ~/proj; for c in gzip bzip2 xz; do cat logs/*.log | $c -c | $c -dc | cmp -s - <(cat logs/*.log) && echo \"$c: round trip identical\"; done", why='Speed differs (gzip is usually several times faster than xz on big files; time it with the time keyword on your own data), but the result is always exact.')]),
    ]
) + cmdcard_u(['single big files, old logs'],
               ['gzip on already compressed files'])(
    'gzip', 'gzip · gunzip · -k · -l · zcat · zgrep · zless', 'compress single files',
    '<code>gzip FILE</code> replaces FILE with FILE.gz (<code>-k</code> keeps it); <code>gunzip</code> or <code>gzip -d</code> reverses it; <code>gzip -l</code> shows the ratio. <code>zcat</code>, <code>zless</code> and <code>zgrep</code> read .gz files without unpacking. bzip2/bunzip2/bzcat and xz/unxz/xzcat work the same way.',
    'gzip -k app.log   ·   zgrep ERROR app.log.gz   ·   gunzip app.log.gz', 'change',
    [('gzip F', 'compress, replace', 'old logs'),
     ('-k', 'keep original', 'safe'),
     ('-d / gunzip', 'decompress', 'back'),
     ('-l', 'ratio', 'check'),
     ('-1 … -9', 'speed vs size', 'tune'),
     ('zcat / zgrep / zless', 'read without unpacking', 'logs')],
    dict(setup=AR, cmd="cd ~/proj/logs\ngzip -k app-2026-11-01.log\ngzip -l app-2026-11-01.log.gz | awk 'NR==2{print \"compressed\", $1, \"uncompressed\", $2, \"ratio\", $3}'\nzgrep -c ERROR app-2026-11-01.log.gz\nzcat app-2026-11-01.log.gz | head -1", note='zgrep searches inside the .gz directly.'),
    [('sys', [
        dict(situation='Random data does not compress (the puzzle).', setup=AR, cmd="cd ~/proj/cache; gzip -k blob.bin; ls -l blob.bin blob.bin.gz | awk '{print $9, $5}'", why='200,000 random bytes grow slightly: headers plus nothing to squeeze.'),
        dict(situation='Compress old logs, keep today’s.', setup=AR, cmd="cd ~/proj/logs; ls *.log | grep -v 11-03 | xargs gzip; ls", why='What logrotate does (Lesson 18.2).')]),
    ]
) + cmdcard_u(['sharing with Windows/macOS users'],
               ['Linux backups (zip loses owners)'])(
    'zip', 'zip -r · unzip -l · unzip -d · -x', 'zip and unzip',
    '<code>zip -r A.zip DIR</code> archives and compresses in one step; <code>unzip -l</code> lists; <code>unzip A.zip -d DEST</code> extracts; <code>-x PATTERN</code> excludes; <code>unzip A.zip FILE</code> extracts one member. Every OS opens .zip without extra software.',
    'zip -r proj.zip proj -x "proj/cache/*"   ·   unzip -l proj.zip', 'change',
    [('zip -r A.zip DIR', 'recursive', 'folders'),
     ('-x PAT', 'exclude', 'caches'),
     ('-q', 'quiet', 'scripts'),
     ('-e', 'password (weak)', 'casual only'),
     ('unzip -l', 'list', 'check'),
     ('unzip -d DIR', 'extract into', 'tidy')],
    dict(setup=AR, cmd="cd ~\nzip -qr bk/proj.zip proj -x 'proj/cache/*'\nunzip -l bk/proj.zip | tail -1\nunzip -q bk/proj.zip 'proj/src/*' -d ~/x && find ~/x -type f | sed \"s|$HOME|~|\"", note='The puzzle: send Windows users a .zip, not a .tar.xz.'),
    [('dev', [
        dict(situation='Same folder, zip vs tar.gz size.', setup=AR, cmd="cd ~; zip -qr bk/p.zip proj; tar -czf bk/p.tar.gz proj; ls -l bk/p.zip bk/p.tar.gz | awk '{print $9, $5}' | sed \"s|bk/||\"", why='zip compresses each file separately, so it is a little bigger.')]),
    ]
) + cmdcard_u(['backups that skip junk', 'getting one file back'],
               ['restoring a whole archive for one file'])(
    'select', '--exclude · single member · -r append · tar -d', 'choose what goes in and out',
    '<code>--exclude=PATTERN</code> skips files (caches, .git, node_modules); naming a member after the archive extracts only it; <code>-r</code> appends to an <b>uncompressed</b> tar; <code>tar -dzf</code> (diff) compares an archive with the files on disk.',
    "tar -czf A.tar.gz --exclude='*/cache' proj   ·   tar -xzf A.tar.gz proj/README.md", 'change',
    [('--exclude=PAT', 'skip', 'junk'),
     ('--exclude-vcs', 'skip .git etc.', 'code'),
     ('MEMBER after archive', 'just that file', 'restore one'),
     ('--wildcards', 'patterns in members', '*.log'),
     ('-r', 'append (no z)', 'add later'),
     ('-d', 'compare with disk', 'verify')],
    dict(setup=AR, cmd="cd ~\ntar -czf bk/slim.tar.gz --exclude='proj/cache' proj\ntar -tzf bk/slim.tar.gz | grep -c cache || echo 'no cache inside'\ntar -xzf bk/slim.tar.gz -C ~/x proj/README.md && cat ~/x/proj/README.md", note='Exclude patterns are matched against member names.'),
    [('sec', [
        dict(situation='Did anything change since the backup?', setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; echo extra >> proj/README.md; tar -dzf bk/p.tar.gz; echo \"exit $?\"", why='tar -d reports the changed file and returns 1.', expect='any')]),
    ]
) + undo('Archives are safe; the dangers are overwriting and replacing.', [
    ('gzip replaced the original:', '<code>gunzip FILE.gz</code> gives it back exactly (lossless); use <code>-k</code> next time.'),
    ('Extracted into the wrong place:', 'list the members (<code>tar -tzf A | xargs …</code>) to delete exactly what was extracted.'),
    ('Overwrote newer files on extract:', 'restore from another copy; next time <code>--keep-newer-files</code> or <code>-k</code> (keep existing).'),
    ('Wrong archive name order:', 'check with <code>ls -l</code>; delete the bad archive and rerun.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=AR, cmd="cd ~ && tar -xzf proj.tar", meaning='No such archive here.', fix='Check the name and path with ls.'),
    dict(setup=AR, cmd="cd ~/proj && tar -xzf README.md", meaning='Not a gzip file: the file is plain text (or you used z on a non-gz archive).', fix='Check with file NAME; drop z or use the right letter.'),
    dict(setup=AR, cmd="cd ~ && tar -czf", meaning='Option f needs a file name.', fix='tar -czf NAME.tar.gz DIR.'),
    dict(setup=AR, cmd="cd ~ && tar -cf bk/a.tar proj && gzip bk/a.tar && tar -rf bk/a.tar.gz README.md", meaning='You cannot append to a compressed archive.', fix='Append to the .tar first, then compress.'),
]) + qc('How do you extract only proj/README.md from proj.tar.gz?', 'tar -xzf proj.tar.gz proj/README.md') + '''
'''
cards = cards + '</section>\n'

ST = [('tar c', 'read files, write 512-byte headers + data', 'blue'), ('| gzip', 'find repeats, encode shorter', 'green'), ('> .tar.gz', 'one small file', 'amber'), ('tar x', 'gunzip, then recreate files', 'violet')]
def tstep(k):
    return ''.join(label_box(14, 12 + i * 40, 330, 32, [f'{a}: {b}'], c if i <= k else 'card', 8.2) for i, (a, b, c) in enumerate(ST))
see_cmds = [['$ tar -czf proj.tar.gz proj', ('reading proj/…', 'out')], ['(gzip runs inside tar)', ('compressing the stream', 'out')], ['$ ls -l proj.tar.gz', ('one file', 'out')], ['$ tar -xzf proj.tar.gz -C x', ('x/proj/… recreated', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Archive.', 'Compress.', 'Result.', 'Extract.'])]
two = anim_two('tar + gzip', 'Behind the screen: a pipeline',
               'A terminal: tar -czf creates the archive, gzip compresses it, then tar -xzf recreates the files.',
               'Four stacked boxes: tar writes headers and data, gzip compresses, one file results, tar x recreates.', see, [tstep(k) for k in range(4)],
               ['archive.', 'compress.', 'result.', 'extract.'],
               ['tar', 'gzip', 'file', 'extract'])

def ent(k):
    rows = [('logs (text)', 'green', 'shrinks a lot'), ('code', 'green', 'shrinks'), ('random cache', 'red', 'grows a little'), ('.gz again', 'red', 'no gain')]
    o = t(180, 18, 'What compresses?', 9.6, 'ink2', bold=True)
    for i in range(k + 1):
        a, c, b = rows[i]
        o += label_box(14, 32 + i * 30, 330, 24, [f'{a}: {b}'], c, 8.2)
    return o
s1 = anim_one('Animated example', 'Entropy: what compresses',
              'Repetition is what compressors remove.', 'text vs random', 'Boxes: text shrinks, random data does not.', [ent(k) for k in range(4)],
              ['text.', 'code.', 'random.', 'twice.'], hid='scenario-entropy')

dx = dissect('Layer by layer: inside a .tar.gz',
    'Each layer has a real command from our build machine.', [
    dict(key='gz', name='gzip wrapper', sub='magic 1f 8b', why='Compressed.', how='DEFLATE.', impl='10-byte header.', used='file, zcat.',
         setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; od -An -tx1 -N2 bk/p.tar.gz; file bk/p.tar.gz | cut -d: -f2 | cut -d, -f1"),
    dict(key='tar', name='tar stream', sub='512-byte blocks', why='Many files.', how='header + data.', impl='ustar format.', used='tar t.',
         setup=AR, cmd="cd ~; tar -cf bk/p.tar proj; echo \"size: $(stat -c %s bk/p.tar) bytes = $(( $(stat -c %s bk/p.tar) / 512 )) blocks of 512\"; head -c 100 bk/p.tar | tr -d '\\0'; echo"),
    dict(key='meta', name='Metadata', sub='mode, owner, time', why='Faithful restore.', how='In each header.', impl='tar -tv.', used='Backups.',
         setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; tar -tvzf bk/p.tar.gz proj/README.md | awk '{print $1, $2, $3, $4, $5, $6}'"),
], hint='Wrapper → stream → metadata. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>tar + gzip, and what compresses</h2>
''' + two + s1 + dx + qc('Why does compressing a .jpg barely help?', 'JPEG is already compressed: its data looks random, so there is no repetition left.') + '''
</section>
'''

VAR = variations('Sixteen more archive and compression commands. All were really run on our build machine on ~/proj.', [
    ('tar forms', [
        dict(title='Verbose create', setup=AR, cmd="cd ~; tar -cvzf bk/p.tar.gz proj/src proj/README.md", why='v prints each member.'),
        dict(title='xz archive', setup=AR, cmd="cd ~; tar -cJf bk/p.tar.xz proj && file bk/p.tar.xz | cut -d: -f2 | cut -d, -f1", why='J = xz.'),
        dict(title='Auto-compress by name (-a)', setup=AR, cmd="cd ~; tar -caf bk/p.tar.bz2 proj/src && file bk/p.tar.bz2 | cut -d: -f2 | cut -d, -f1", why='-a picks bzip2 from .bz2.'),
        dict(title='Extraction auto-detects', setup=AR, cmd="cd ~; tar -cJf bk/p.tar.xz proj/src; tar -xf bk/p.tar.xz -C ~/x && ls ~/x/proj/src", why='No J needed to extract.'),
        dict(title='Only *.log members', setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; tar -xzf bk/p.tar.gz -C ~/x --wildcards '*.log'; find ~/x -type f | wc -l", why='--wildcards for patterns.'),
        dict(title='Strip the top folder', setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; tar -xzf bk/p.tar.gz -C ~/x --strip-components=1; ls ~/x", why='Contents without proj/.'),
    ]),
    ('Pipes', [
        dict(title='tar to stdout and back (copy a tree)', setup=AR, cmd="cd ~; tar -cf - proj/src | tar -xf - -C ~/x; ls ~/x/proj/src", why='- means stdin/stdout; works over ssh too.'),
        dict(title='Count lines in all compressed logs', setup=AR, cmd="cd ~/proj/logs; gzip *.log; zcat *.gz | wc -l", why='zcat joins them.'),
        dict(title='Errors per day without unpacking', setup=AR, cmd="cd ~/proj/logs; gzip *.log; for f in *.gz; do echo \"$f $(zgrep -c ERROR $f)\"; done", why='zgrep per file.'),
        dict(title='Split a big archive into parts', setup=AR, cmd="cd ~; tar -czf - proj | split -b 300k - bk/p.tar.gz.part-; ls bk | wc -l; cat bk/p.tar.gz.part-* | tar -tzf - | wc -l", why='For size-limited uploads.'),
    ]),
    ('Levels and checks', [
        dict(title='gzip -1 vs -9', setup=AR, cmd="cd ~/proj/logs; for l in 1 9; do echo \"-$l: $(gzip -$l -c app-2026-11-01.log | wc -c) bytes\"; done", why='Small difference, big time difference on large data.'),
        dict(title='Test an archive’s integrity', setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; gzip -t bk/p.tar.gz && echo 'gzip OK'; tar -tzf bk/p.tar.gz > /dev/null && echo 'tar OK'", why='-t tests without extracting.'),
        dict(title='A corrupted archive', setup=AR, cmd="cd ~; tar -czf bk/p.tar.gz proj; head -c 20000 bk/p.tar.gz > bk/cut.tar.gz; gzip -t bk/cut.tar.gz; echo \"exit $?\"", why='Truncated downloads are detected.', expect='any'),
        dict(title='Checksum the backup', setup=AR, cmd="cd ~/bk; tar -cf p.tar -C ~ proj/README.md; sha256sum p.tar > p.sha256; sha256sum -c p.sha256", why='Store it next to the backup.'),
    ]),
    ('Dated backups', [
        dict(title='Name with the date', setup=AR, cmd="cd ~; f=bk/proj-$(date -d 2026-11-12 +%F).tar.gz; tar -czf $f proj; ls bk", why='%F = YYYY-MM-DD, sorts correctly.'),
        dict(title='Keep only the newest 3', setup=AR, cmd="cd ~/bk; for d in 08 09 10 11 12; do touch proj-2026-11-$d.tar.gz; done; ls proj-*.tar.gz | sort | head -n -3 | xargs rm; ls", why='Rotation in one line.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Archives and compression at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['backup', 'nightly'], 'blue', 8.6), '1. Nightly backups',
              'cron runs tar -czf /backup/app-$(date +%F).tar.gz with excludes, then checks it and deletes old ones.', ['cron', '*tar + date', 'rotate']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['logs', 'disk'], 'green', 8.6), '2. Log rotation',
    'logrotate gzips old logs: 1 GB of text becomes about 100–300 MB; zgrep still searches them.', ['Old logs', '*gzip', 'zgrep']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['release', '.tar.xz'], 'amber', 8.6), '3. Software releases',
    'The Linux kernel and GNU projects publish .tar.xz tarballs with checksums and signatures.', ['Build', '*tar -cJf', 'publish']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['big data', 'formats'], 'violet', 8.6), '4. Data engineering',
    'Hadoop and Spark prefer splittable formats (bzip2, or Parquet with Snappy/zstd); a single .gz cannot be split between workers.', ['Raw CSV', '*compress', 'Spark']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['containers', 'layers'], 'red', 8.6), '5. Container images',
    'Each Docker image layer is a tar archive, usually gzip- or zstd-compressed.', ['Dockerfile', '*layer = tar', 'registry']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Back up a folder', scenario='Before a change.', setup=AR, cmd="cd ~ && tar -czf bk/proj.tar.gz proj && ls bk", explain='c z f.'),
    dict(level='b', title='Look inside', scenario='What is in it?', setup=AR, cmd="cd ~ && tar -czf bk/p.tgz proj && tar -tzf bk/p.tgz | wc -l", explain='t lists.'),
    dict(level='i', title='Search compressed logs', scenario='Incident.', setup=AR, cmd="cd ~/proj/logs && gzip -k *.log && zgrep -h ERROR *.gz | wc -l", explain='zgrep.'),
    dict(level='i', title='Biggest member', scenario='Why so big?', setup=AR, cmd="cd ~ && tar -czf bk/p.tgz proj && tar -tvzf bk/p.tgz | sort -k3 -n | tail -1 | awk '{print $3, $6}'", explain='Size is field 3.'),
    dict(level='a', title='Copy a tree with a pipe', scenario='Keep permissions.', setup=AR, cmd="cd ~ && tar -cf - proj | (cd ~/x && tar -xf -) && du -s ~/x/proj | cut -f1", explain='Classic tar pipe.'),
], extra=build_up('a verified, dated backup', 'Riya builds the nightly backup step by step.', AR, [
    ("cd ~; f=bk/proj-2026-11-12.tar.gz; tar -czf $f --exclude=proj/cache proj && ls -l $f | awk '{print $9}'", '1. Create, without the cache.'),
    ("cd ~/bk; gzip -t proj-2026-11-12.tar.gz && tar -tzf proj-2026-11-12.tar.gz | wc -l | sed 's/^/members: /'", '2. Test it.'),
    ("cd ~/bk; sha256sum proj-2026-11-12.tar.gz > proj-2026-11-12.sha256 && sha256sum -c proj-2026-11-12.sha256", '3. Record and check a checksum.'),
    ("cd ~/x; tar -xzf ~/bk/proj-2026-11-12.tar.gz && diff -r --exclude=cache ~/proj proj && echo 'restore test passed'", '4. A real restore test.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Linux backup', 'tar -czf', 'Keeps owners, modes.', 'zip.'),
    ('Smallest release', 'tar -cJf', 'Usually best ratio.', 'gzip.'),
    ('Windows users', 'zip -r', 'Opens anywhere.', '.tar.xz.'),
    ('One big log', 'gzip / xz', 'Replace in place.', 'tar for one file.'),
    ('Read compressed', 'zcat / zgrep', 'No temp files.', 'gunzip first.'),
    ('Fast modern', 'zstd', 'Speed + ratio.', 'bzip2.'),
]) + keys('Handy forms.', [
    ('tar -czf A.tar.gz DIR', 'create', 'gzip'),
    ('tar -tzf A.tar.gz', 'list', 'check'),
    ('tar -xzf A.tar.gz -C D', 'extract', 'into D'),
    ("--exclude='*/cache'", 'skip', 'junk'),
    ('gzip -k F · zgrep P F.gz', 'compress / search', 'logs'),
    ('zip -r A.zip DIR', 'Windows', 'share'),
]) + scriptit('backup.sh', 'A nightly backup: dated tar.gz of the project without the cache, tested, checksummed, and only the newest three kept.',
'''set -e
src=~/proj; dest=~/bk; day=2026-11-12
f=$dest/proj-$day.tar.gz
tar -czf "$f" --exclude=proj/cache -C "$(dirname "$src")" "$(basename "$src")"
gzip -t "$f"
sha256sum "$f" > "$f.sha256"
for d in 09 10 11; do touch "$dest/proj-2026-11-$d.tar.gz"; done
ls "$dest"/proj-*.tar.gz | sort | head -n -3 | xargs -r rm
echo "backup $(basename "$f"): $(tar -tzf "$f" | wc -l) members, $(stat -c %s "$f") bytes"
ls "$dest" | grep -c 'tar.gz$' | sed 's/^/archives kept: /' ''',
'<p>The touch line only simulates older backups for the demo.</p>', expect='any') + puzzle_answer('<b>1.</b> “Removing leading `/’ from member names” is a notice, not an error: tar stores <code>home/riya/proj/…</code> so extracting can never overwrite absolute system paths. Use <code>-C ~ proj</code> to avoid the message. <b>2.</b> <code>cache/blob.bin</code> is random data with no repetition, so gzip cannot shrink it and its header makes it slightly bigger: compress text, not already compressed or random data. <b>3.</b> Windows opens .zip natively but not .tar.xz without extra software (7-Zip): send <code>zip -r proj.zip proj</code>.') + qc('Which command lists a .tar.gz without extracting it?', 'tar -tzf archive.tar.gz') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-snap-flatpak-and-building-from-source/">Lesson 14.4</a> (tarballs) and <a href="../../03-files-and-directories/02-copying-moving-and-syncing-cp-mv-and-rsync/">Lesson 3.2</a> (copying).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
