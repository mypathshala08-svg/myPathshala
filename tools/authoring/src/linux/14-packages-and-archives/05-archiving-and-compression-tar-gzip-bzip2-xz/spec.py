import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('AR = r"""') + 9
AR = _s[_i:_s.index('"""', _i)]

META = dict(
    module='14-packages-and-archives', lesson='05-archiving-and-compression-tar-gzip-bzip2-xz', n='14.5',
    module_label='Module 14 · Software packages and archives',
    title='Archiving and compression: tar, gzip, bzip2, xz and zip',
    desc='tar create, list and extract (c t x f v -C), gzip, bzip2 and xz compared on real files (sizes and times measured), zcat, zgrep and zless, zip and unzip, --exclude, single-file restore, --strip-components, tar pipes, integrity tests, and verified dated backups with rotation, with 35+ real examples.',
    og_desc='tar, gzip, bzip2, xz and zip measured on real files, with verified dated backups and single-file restores.',
    minutes=35, level='Beginner → Advanced',
    lead='tar joins files, gzip, bzip2 and xz shrink them, zip does both for Windows. Every size here was measured, and the backup is verified by a real restore.',
    chips=['Compressors measured', 'tar + gzip animated', 'Verified backup build-up', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Run-length encoding: the simplest compression idea (repeats become counts)
rle(){ echo -n "$1" | fold -w1 | uniq -c | awk '{printf "%s%s", $1, $2} END{print ""}'; }
for s in aaaaaaaabbbbcc ERRORERRORERROR abcdefgh; do
  out=$(rle "$s"); echo "$s (${#s}) -> $out (${#out})"
done
"""

RUN = dict(
    heading='Why repetition compresses',
    intro='<p>gzip and xz are far smarter, but the idea is the same: repeats are written shorter. Random text gets longer.</p>',
    code=MAIN,
    anno=[('uniq -c', 'Counts runs of the same character.'), ('abcdefgh', 'No repeats: the “compressed” form is longer.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which input grows?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does this print?',
             code="f=backup.tar.gz; echo \"${f%%.*} / ${f#*.}\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> f must be followed by the archive name. Reorder the letters.',
             code="echo 'tar -cfz out.tar dir   creates an archive named:'; set -- -cfz out.tar; echo \"${2}? no: f takes the NEXT word -> z\"\n"),
        dict(label='4 · Your turn', hint='Map an extension to the tar letter.',
             code="for f in a.tar.gz b.tar.bz2 c.tar.xz; do case $f in *.gz) l=z;; *.bz2) l=j;; *.xz) l=J;; esac; echo \"$f -> tar -x${l}f\"; done\n"),
        dict(label='5 · Challenge', hint='Build a dated backup name.',
             code="echo \"proj-$(date -d 2026-11-12 +%F).tar.gz\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>zstd and Windows tools are not on our build machine; typical outputs.</p>',
    items=[
        dict(title='1 · zstd', cmd='tar --zstd -cf proj.tar.zst proj\nls -lh proj.tar.zst', output='-rw-r--r-- 1 riya riya 610K Nov 12 10:00 proj.tar.zst', note='Typical; needs the zstd package.'),
        dict(title='2 · Windows 10/11 tar', cmd='tar -xf proj.tar.gz   (in PowerShell)', output='(files extracted; Windows ships bsdtar since 2018)', note='Typical.'),
        dict(title='3 · 7-Zip', cmd='7z x proj.tar.xz', output='Everything is Ok', note='Typical.'),
        dict(title='4 · Parallel gzip', cmd='tar -I pigz -cf big.tar.gz bigdir', output='(uses all cores)', note='Needs pigz.'),
    ],
)

TRACE = dict(
    heading='Rotating backups, line by line',
    intro='<p>Keep the newest three dated archives.</p>',
    code='''set -- proj-2026-11-09 proj-2026-11-10 proj-2026-11-11 proj-2026-11-12
keep=3; n=$#
for f in "$@"; do
  if (( n > keep )); then echo "delete $f"; n=$((n-1)); else echo "keep $f"; fi
done
''',
    notes={1: 'Names sort by date thanks to %F.', 4: 'Oldest first are deleted.'},
)

WORKED_INTRO = 'Three real archive tasks.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Back up and restore one file',
         problem='<p>Archive a folder, then restore only one file from it.</p>',
         inp='a folder', approach=['tar -czf, then name the member.'],
         code='''mkdir -p site/css; echo body > site/css/a.css; echo hi > site/index.html
tar -czf site.tar.gz site; rm site/index.html
tar -xzf site.tar.gz site/index.html; cat site/index.html
''', notes={3: 'Only that member comes back.'}, tryit='Restore with -C /tmp.'),
    dict(level='i', tag='Logs', title='Errors in compressed logs',
         problem='<p>Count ERROR lines across .gz logs without unpacking.</p>',
         inp='compressed logs', approach=['zgrep -c.'],
         code='''printf 'INFO a\\nERROR b\\nERROR c\\n' > d1.log; printf 'ERROR x\\n' > d2.log
gzip d1.log d2.log
for f in *.gz; do echo "$f $(zgrep -c ERROR "$f")"; done
''', notes={3: 'One count per file.'}, tryit='Total them.'),
    dict(level='a', tag='Data', title='Which compressor for this data?',
         problem='<p>Compare gzip, bzip2 and xz on repetitive text.</p>',
         inp='generated text', approach=['-c | wc -c.'],
         code='''seq 1 20000 | sed 's/^/order /' > o.txt
for c in gzip bzip2 xz; do echo "$c $($c -c o.txt | wc -c)"; done
''', notes={2: 'Bytes after compression.'}, tryit='Add the raw size.'),
]

QUIZ = mix([
    dict(q='tar -czf a.tar.gz d: the z means…', options=['zip', 'gzip', 'zero', 'list'], answer=1, why='gzip.'),
    dict(q='List a .tar.gz:', options=['tar -lzf', 'tar -tzf', 'tar -czf', 'tar -xzf'], answer=1, why='t.'),
    dict(q='On Riya’s logs the smallest result came from…', options=['gzip', 'bzip2', 'zip', 'tar'], answer=1, why='12%; xz was 14%. Measure your data.'),
    dict(q='gzip file keeps the original if…', options=['-k', '-r', '-v', 'always'], answer=0, why='-k.'),
    dict(q='Search inside app.log.gz:', options=['grep -z', 'zgrep', 'tar -g', 'gzip -s'], answer=1, why='zgrep.'),
    dict(q='Extract into /tmp/x:', options=['-d /tmp/x', '-C /tmp/x', '-o /tmp/x', '> /tmp/x'], answer=1, why='-C.'),
    dict(q='Best for Windows users:', options=['.tar.xz', '.zip', '.tar.bz2', '.cpio'], answer=1, why='Native.'),
    dict(q='Random data compressed with gzip…', options=['halves', 'grows slightly', 'disappears', 'fails'], answer=1, why='No repetition.'),
])

REVISION = [
    'tar archives (c create, t list, x extract, f file, v verbose, -C dir); it does not compress by itself.',
    'z gzip (fast), j bzip2, J xz (usually smallest; measure); extraction auto-detects; -a picks by extension.',
    'gzip, bzip2, xz replace the file (-k keeps it); zcat, zless, zgrep read without unpacking.',
    'zip -r and unzip for Windows; zip compresses per file and loses Unix owners.',
    '--exclude, single members, --wildcards, --strip-components, tar -d to compare.',
    'Backups: dated name, test (gzip -t, tar -t), checksum, restore test, rotation.',
]

FAQ = [
    ('How do I extract a tar.gz file in Linux?', 'tar -xzf file.tar.gz (add -C DIR to choose where).'),
    ('What is the difference between tar and zip?', 'tar only archives (compression is added with gzip/xz) and keeps Unix permissions; zip archives and compresses per file and is native on Windows.'),
    ('Which is better, gzip or xz?', 'xz usually makes smaller files, gzip is much faster; use gzip for everyday and logs, xz for releases.'),
    ('How do I see what is inside an archive?', 'tar -tzf A.tar.gz, unzip -l A.zip.'),
    ('How do I extract one file from a tar?', 'Name it after the archive: tar -xzf A.tar.gz path/in/archive.'),
    ('Why does tar remove the leading slash?', 'So extraction never writes to absolute system paths by accident.'),
    ('What is a .tgz?', 'Same as .tar.gz.'),
]

PRACTICE_INTRO = 'Small archive tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Create', stmt='Archive a folder d into d.tar.gz and list it.', inp='nothing', code="mkdir -p d; touch d/a; tar -czf d.tar.gz d; tar -tzf d.tar.gz\n", explain='d/ and d/a.'),
    dict(level='easy', title='Keep', stmt='gzip a file but keep the original.', inp='nothing', code="echo hi > f; gzip -k f; ls f f.gz\n", explain='-k.'),
    dict(level='easy', title='Read', stmt='Print a .gz without unpacking.', inp='nothing', code="echo hello | gzip > h.gz; zcat h.gz\n", explain='zcat.'),
    dict(level='medium', title='Letter', stmt='Which tar letter for .tar.xz?', inp='nothing', code="echo J\n", explain='Capital J.'),
    dict(level='medium', title='One member', stmt='Restore only d/a from d.tar.gz.', inp='an archive', code="mkdir -p d; echo A > d/a; echo B > d/b; tar -czf d.tar.gz d; rm -r d; tar -xzf d.tar.gz d/a; ls d\n", explain='Only a.'),
    dict(level='medium', title='Test', stmt='Test a gzip file.', inp='nothing', code="echo x | gzip > t.gz; gzip -t t.gz && echo OK\n", explain='OK.'),
    dict(level='business', title='Dated', stmt='Print a backup name for 2026-11-12.', inp='a date', code="echo \"db-$(date -d 2026-11-12 +%F).tar.gz\"\n", explain='db-2026-11-12.tar.gz.'),
    dict(level='business', title='Exclude', stmt='Archive d without d/cache and count members.', inp='nothing', code="mkdir -p d/cache; touch d/a d/cache/x; tar -czf d.tar.gz --exclude=d/cache d; tar -tzf d.tar.gz | wc -l\n", explain='2 (d/ and d/a).'),
]

SCN_INTRO = 'Interview questions about archives, compression and backups.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Create and extract a tar.gz”', 'Very common.', 'commands?',
        '''<ul>
          <li>tar -czvf name.tar.gz dir</li>
          <li>tar -tzf name.tar.gz to check</li>
          <li>tar -xzvf name.tar.gz -C dest</li>
        </ul>''', 'mixing up c and x.') +
    scn('Service company', 'Junior', '/var/log is 95% full', 'Production.', 'quick win?',
        '''<ol>
          <li>gzip old rotated logs (text shrinks 70–90%).</li>
          <li>zgrep keeps them searchable.</li>
          <li>Fix logrotate so it compresses (Lesson 18.2).</li>
        </ol>''', 'deleting today’s log of a running service.') +
    scn('Product company', 'Mid-level', 'Backups exist but never restored', 'Audit.', 'what to add?',
        '''<ul>
          <li>gzip -t and tar -t after every backup.</li>
          <li>Checksums stored with the archive.</li>
          <li>Regular restore tests into a scratch directory.</li>
        </ul>''', 'trusting a 0-exit-code alone.') +
    scn('Data platform', 'Senior', '10 TB of CSV for Spark', 'Storage cost.', 'format?',
        '''<ul>
          <li>Not one big .gz: it cannot be split across workers.</li>
          <li>bzip2 (splittable) or better columnar Parquet with Snappy/zstd.</li>
          <li>Measure ratio vs CPU.</li>
        </ul>''', 'gzip -9 everything.')
) + interview([
    ('tar vs gzip?', 'Archive vs compress.'),
    ('Why .tar.gz and not just .gz?', 'gzip handles one file only.'),
    ('zcat vs cat?', 'zcat decompresses first.'),
    ('--strip-components?', 'Drop leading path parts on extract.'),
    ('tar -r on .tar.gz?', 'Not possible; compressed archives cannot be appended.'),
    ('Fastest modern compressor?', 'zstd (and lz4).'),
    ('How to copy a tree keeping permissions?', 'tar -cf - dir | (cd dest && tar -xpf -).'),
], [
    ('LFCS', 'Archive, back up, compress, unpack.'),
    ('RHCSA', 'Create and extract tar archives with gzip and bzip2.'),
    ('CompTIA Linux+', 'tar, gzip, xz, zip, cpio, dd.'),
]) + distro('Same tools everywhere; defaults differ slightly.', [
    ('tar', 'GNU tar', 'GNU tar', 'GNU tar', 'GNU tar'),
    ('zstd', 'install', 'installed', 'installed', 'installed'),
    ('zip/unzip', 'install', 'installed', 'install', 'install'),
    ('Log compression', 'logrotate gzip', 'logrotate gzip', 'logrotate xz', 'journal zstd'),
    ('Packages', '.deb = ar + tar.zst/xz', '.rpm = cpio + zstd', '.rpm', '.pkg.tar.zst'),
]) + teaser('15.1', 'Archives fill disks. Next module: what a disk actually is: partitions, lsblk, blkid, fdisk and parted.')

CHEATSHEET = cheatsheet('Archives', [
    ('tar', [('tar -czf A.tar.gz D', 'create'), ('tar -tzf A', 'list'), ('tar -xzf A -C D', 'extract'), ('--exclude=P', 'skip')]),
    ('Compressors', [('z', 'gzip'), ('j', 'bzip2'), ('J', 'xz'), ('-a', 'by name')]),
    ('Single files', [('gzip -k F', 'keep'), ('gunzip F.gz', 'back'), ('zgrep P F.gz', 'search'), ('gzip -t F.gz', 'test')]),
    ('zip', [('zip -r A.zip D', 'create'), ('unzip -l A.zip', 'list'), ('unzip A.zip -d D', 'extract'), ('-x P', 'exclude')]),
])

MINDMAP = mindmap('Archives', [
    ('tar', 'blue', ['c t x f', '-C', 'metadata']),
    ('Compress', 'green', ['gzip', 'bzip2', 'xz / zstd']),
    ('Read', 'amber', ['zcat', 'zgrep', 'zless']),
    ('zip', 'violet', ['Windows', 'per file', 'unzip -l']),
    ('Select', 'red', ['--exclude', 'one member', 'strip']),
    ('Backup', 'acc', ['dated', 'tested', 'rotated']),
])

LAB = lab('a verified backup', 'Build the lab (it creates <code>~/proj</code>), write <code>~/lab145/answers.sh</code>, then run the checker.',
    setup=AR + '''
mkdir -p ~/lab145 && cd ~/lab145 && rm -rf answers.sh *.txt *.tar.gz restore''',
    tasks=['Create <code>~/lab145/proj.tar.gz</code> of <code>~/proj</code> without the <code>cache</code> folder, with paths starting at <code>proj/</code>.',
           'Write the number of members in the archive into <code>members.txt</code>.',
           'Write the number of ERROR lines in all three logs, read from the archive without extracting to disk, into <code>errors.txt</code>.',
           'Restore only <code>proj/README.md</code> into <code>~/lab145/restore</code>.'],
    solution='''cat > answers.sh <<'EOF'
cd ~/lab145
tar -czf proj.tar.gz -C ~ --exclude=proj/cache proj
tar -tzf proj.tar.gz | wc -l > members.txt
tar -xzOf proj.tar.gz --wildcards 'proj/logs/*.log' | grep -c ERROR > errors.txt
mkdir -p restore && tar -xzf proj.tar.gz -C restore proj/README.md
EOF''',
    check='''cd ~/lab145; rm -rf members.txt errors.txt proj.tar.gz restore
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh > /dev/null 2>&1
ok "1 archive" 'tar -tzf proj.tar.gz 2>/dev/null | grep -q "^proj/README.md$" && ! tar -tzf proj.tar.gz | grep -q cache'
ok "2 members" '[ "$(cat members.txt 2>/dev/null)" = "$(tar -tzf proj.tar.gz 2>/dev/null | wc -l)" ] && [ -s members.txt ]'
ok "3 errors"  '[ "$(cat errors.txt 2>/dev/null)" = "$(cat ~/proj/logs/*.log | grep -c ERROR)" ]'
ok "4 restore" 'cmp -s restore/proj/README.md ~/proj/README.md && [ ! -e restore/proj/src ]' ''')
