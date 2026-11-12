import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('SS = r"""') + 9
SS = _s[_i:_s.index('"""', _i)]

META = dict(
    module='02-working-with-data', lesson='03-temporary-files-trap-and-clean-up', n='2.3',
    module_label='Module 2 · Working with data',
    title='Temporary files, trap and clean-up',
    desc='Safe scratch space in Bash: mktemp files and folders, templates and TMPDIR, trap on EXIT, INT and TERM with exit codes 130 and 143, keeping the exit status in the clean-up function, atomic writes with mv, what kill -9 leaves behind, and sweeping old leftovers, with every run real.',
    og_desc='mktemp, trap EXIT/INT/TERM, atomic mv and leftover sweeps for Bash scripts, with real runs.',
    minutes=35, level='Intermediate',
    lead='Unique scratch space that is always removed, and results that appear all at once or not at all.',
    chips=['Every ending cleans up', 'Atomic mv animated', 'kill -9 tested', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """work=$(mktemp -d)
cleanup() {
  local rc=$?
  rm -rf -- "${work:?}"
  echo "cleaned $work (exit $rc)"
}
trap cleanup EXIT

seq 1 5 > "$work/numbers"
echo "sum: $(paste -sd+ "$work/numbers" | bc)"
ls "$work"
# the trap runs when this program ends
"""

RUN = dict(
    heading='mktemp and trap in your browser',
    intro='<p>The temp folder exists while the script runs and is removed when it ends.</p>',
    code=MAIN,
    anno=[('mktemp -d', 'Unique private folder.'), ('local rc=$?', 'Keep the exit status.'), ('trap cleanup EXIT', 'Runs at the very end.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. When is “cleaned” printed?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> does the trap run when the script fails?',
             code="( trap 'echo trap ran' EXIT; false; exit 1 ); echo \"exit $?\"\n", expect='any'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> double quotes expand $w too early (it is empty). Use single quotes.',
             code="trap \"echo would remove [$w]\" EXIT\nw=$(mktemp -d)\n"),
        dict(label='4 · Your turn', hint='Write a result atomically.',
             code="t=$(mktemp ./.out.XXXXXX)\necho 'final report' > \"$t\"\nmv -- \"$t\" report.txt\ncat report.txt\n"),
        dict(label='5 · Challenge', hint='Two names from mktemp: are they different?',
             code="a=$(mktemp); b=$(mktemp)\n[[ $a != \"$b\" ]] && echo 'different names'\nrm -f -- \"$a\" \"$b\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Press Ctrl+C yourself. Outputs below are from our build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Run the job', cmd="./report.sh; echo $?", output='report.sh: report written\nreport.sh: cleaned report.QDLRlL (exit 0)\n0', note='Real output (random name differs).'),
        dict(title='2 · Press Ctrl+C', cmd="SLOW=10 ./report.sh\n^C", output='^Creport.sh: interrupted\nreport.sh: cleaned report.xMgvuj (exit 130)', note='Real behaviour.'),
        dict(title='3 · Where is TMPDIR?', cmd="echo ${TMPDIR:-/tmp}; df -h /tmp | tail -1", output='/tmp\ntmpfs  3.9G  12M  3.9G  1% /tmp', note='Typical: /tmp in RAM on many systems.'),
        dict(title='4 · OS clean-up rules', cmd="systemd-tmpfiles --cat-config | grep -E '^[dq] /(var/)?tmp'", output='q /tmp 1777 root root 10d\nq /var/tmp 1777 root root 30d', note='Typical.'),
    ],
)

TRACE = dict(
    heading='Clean-up that keeps the status, line by line',
    intro='<p>The handler runs last and passes the status on.</p>',
    code='''work=$(mktemp -d)
cleanup() { local rc=$?; rm -rf -- "$work"; echo "removed, status $rc"; }
touch "$work/a" "$work/b"
ls "$work" | wc -l
cleanup
[[ -d $work ]] || echo "folder gone"
''',
    notes={2: 'rc is saved before rm can change $?.', 5: 'Called by hand here; trap EXIT calls it at the end.'},
)

WORKED_INTRO = 'Three jobs that never leave a mess.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Sort a big file through scratch space',
         problem='<p>Sort and de-duplicate a list through a temp file, cleaning up on any ending.</p>',
         inp='a list', approach=['mktemp + trap.'],
         code='''printf 'b\\na\\nb\\nc\\n' > list.txt
( t=$(mktemp); trap 'rm -f -- "$t"' EXIT
  sort -u list.txt > "$t" && mv -- "$t" list.txt )
cat list.txt
''', notes={2: 'Trap right after mktemp.', 3: 'Atomic replace of the input.'}, tryit='Make the sort fail and check the original.'),
    dict(level='i', tag='Security', title='A secret that never stays on disk',
         problem='<p>Write a token to a private temp file for a command, then remove it.</p>',
         inp='a token', approach=['0600 file, EXIT trap.'],
         code='''( t=$(mktemp); trap 'rm -f -- "$t"; echo "token file removed"' EXIT
  printf '%s' 'ghp_demo_token' > "$t"
  stat -c 'mode %a, %s bytes' "$t"
  wc -c < "$t" > /dev/null )
''', notes={1: 'Removed however the block ends.', 3: 'Only the owner can read it.'}, tryit='Add an INT trap.'),
    dict(level='a', tag='SRE', title='Prove no leftovers after 20 failures',
         problem='<p>Run a failing job 20 times and count temp folders left.</p>',
         inp='nothing', approach=['Own TMPDIR, count.'],
         code='''mkdir -p scratch; export TMPDIR=$PWD/scratch
for i in $(seq 20); do bash -c 'set -e; w=$(mktemp -d); trap "rm -rf -- \\"\\$w\\"" EXIT; false' || true; done
echo "leftovers after 20 failed runs: $(ls scratch | wc -l)"
''', notes={2: 'Every run fails on false.'}, tryit='Remove the trap and rerun.'),
]

QUIZ = mix([
    dict(q='Why not /tmp/job.tmp?', options=['too long', 'parallel runs collide and it is predictable', 'not allowed', 'slow'], answer=1, why='Unique names.'),
    dict(q='mktemp -d creates…', options=['a file', 'a private folder', 'a link', 'nothing'], answer=1, why='0700 folder.'),
    dict(q='trap cleanup EXIT runs…', options=['only on success', 'on every normal or error exit', 'only on kill -9', 'at start'], answer=1, why='Any exit.'),
    dict(q='Exit code after Ctrl+C with trap … exit 130:', options=['2', '130', '143', '0'], answer=1, why='128+2.'),
    dict(q='Which signal can no trap catch?', options=['INT', 'TERM', 'KILL', 'HUP'], answer=2, why='SIGKILL.'),
    dict(q='First line of a clean-up function:', options=['rm -rf', 'local rc=$?', 'exit 0', 'echo'], answer=1, why='Keep status.'),
    dict(q='mv is atomic when…', options=['always', 'source and target are on the same file system', 'with -f', 'as root'], answer=1, why='rename().'),
    dict(q='Template for mktemp needs at least…', options=['1 X', '3 X', '6 X', '10 X'], answer=1, why='Too few X otherwise.'),
])

REVISION = [
    'Never fixed temp names: mktemp (file, 0600) or mktemp -d (folder, 0700); TMPDIR chooses the place.',
    "Register trap 'cleanup' EXIT right after mktemp; single quotes so variables expand at run time.",
    'cleanup(){ local rc=$?; rm -rf -- "${work:?}"; } keeps the exit status and refuses empty paths.',
    "Add trap 'exit 130' INT and trap 'exit 143' TERM; kill -9 cannot be trapped.",
    'Publish results atomically: build in a temp file on the same file system, then mv.',
    'Sweep crash leftovers by template name and age (find -name job.* -mmin +60), dry run first.',
]

FAQ = [
    ('How do I create a temporary file in Bash?', 'tmp=$(mktemp) for a file, mktemp -d for a folder; they get unique names and private permissions.'),
    ('How do I delete temp files when a script exits?', "trap 'rm -rf -- \"$tmp\"' EXIT right after creating them."),
    ('Does trap EXIT run when the script is killed?', 'On Ctrl+C in Bash yes; for kill (TERM) add a TERM trap that exits; kill -9 never runs any trap.'),
    ('What is the exit code after Ctrl+C?', '130 (128 + signal 2).'),
    ('Why use single quotes in trap?', 'So variables expand when the trap runs, not when it is set.'),
    ('How do I write a file atomically?', 'Write to a temp file in the same folder, then mv it over the target.'),
    ('Where should big temp files go?', 'Set TMPDIR to a disk-backed folder such as /var/tmp; /tmp may be RAM (tmpfs).'),
]

PRACTICE_INTRO = 'Small temp-file and trap tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Private file', stmt='Show the mode of a new mktemp file.', inp='nothing', code="f=$(mktemp); stat -c %a \"$f\"; rm -f -- \"$f\"\n", explain='600.'),
    dict(level='easy', title='Trap', stmt='Print bye when a subshell ends.', inp='nothing', code="( trap 'echo bye' EXIT; echo hi )\n", explain='hi, bye.'),
    dict(level='easy', title='Signal code', stmt='Compute the code for SIGTERM (15).', inp='nothing', code="echo $((128 + 15))\n", explain='143.'),
    dict(level='medium', title='Status kept', stmt='Exit 5 through a trap that runs rm.', inp='nothing', code="bash -c 'c(){ local r=$?; rm -f /nope 2>/dev/null; exit $r; }; trap c EXIT; exit 5'; echo $?\n", explain='5.'),
    dict(level='medium', title='Empty guard', stmt='Show that ${w:?} refuses an empty w.', inp='nothing', code="w=''; ( : \"${w:?empty}\" ) 2>/dev/null || echo refused\n", explain='refused.'),
    dict(level='medium', title='Atomic', stmt='Replace v1 with v2 via a temp file.', inp='nothing', code="echo v1 > f; t=$(mktemp ./.f.XXXXXX); echo v2 > \"$t\"; mv -- \"$t\" f; cat f\n", explain='v2.'),
    dict(level='business', title='Leftover count', stmt='Count folders in a scratch dir after one trapped run.', inp='nothing', code="mkdir -p s; TMPDIR=$PWD/s bash -c 'w=$(mktemp -d); trap \"rm -rf -- \\\"\\$w\\\"\" EXIT'; ls s | wc -l\n", explain='0.'),
    dict(level='business', title='Old only', stmt='Find folders older than 60 min named job.*.', inp='nothing', code="mkdir -p job.a job.b; touch -d '2 hours ago' job.a; find . -maxdepth 1 -name 'job.*' -mmin +60\n", explain='./job.a.'),
]

SCN_INTRO = 'Interview questions about temp files and traps.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you create a temp file safely?”', 'Common.', 'and remove it?',
        '''<ul>
          <li>tmp=$(mktemp).</li>
          <li>trap 'rm -f -- "$tmp"' EXIT.</li>
          <li>Never fixed names in /tmp.</li>
        </ul>''', 'echo > /tmp/x.tmp.') +
    scn('Service company', 'Junior', '/tmp full of old job files', 'Server alert.', 'fix?',
        '''<ol>
          <li>Sweep by name and age.</li>
          <li>Add trap EXIT (+INT/TERM) to the job.</li>
          <li>Use mktemp templates to recognise files.</li>
        </ol>''', 'rm -rf /tmp/*.') +
    scn('Product company', 'Mid-level', 'Users saw half-written price lists', 'Website.', 'cause + fix?',
        '''<ul>
          <li>The job wrote straight into the live file.</li>
          <li>Write aside, then mv (same file system).</li>
          <li>A failed run then keeps the old list.</li>
        </ul>''', 'adding sleep.') +
    scn('Platform', 'Senior', 'Flaky CI builds on shared runners', 'Random failures.', 'investigate?',
        '''<ul>
          <li>Look for fixed temp paths shared by parallel jobs.</li>
          <li>Replace with mktemp / per-job TMPDIR.</li>
          <li>Clean with traps; isolate workspaces.</li>
        </ul>''', 'retrying until green.')
) + interview([
    ('mktemp permissions?', '0600 file, 0700 folder.'),
    ('What is trap EXIT?', 'Runs when the shell exits.'),
    ('Codes for INT and TERM?', '130 and 143.'),
    ('Why local rc=$??', 'Keep the real exit status.'),
    ('Can kill -9 be trapped?', 'No.'),
    ('Atomic file replace?', 'Temp file + mv on the same file system.'),
    ('TMPDIR?', 'Where mktemp creates files.'),
], [
    ('LFCS', 'Scripts that handle signals and files safely.'),
    ('RHCSA', 'Shell scripts; process signals.'),
    ('CompTIA Linux+', 'trap, signals, temp files.'),
]) + distro('/tmp per distribution.', [
    ('/tmp type', 'disk (tmpfs on newer)', 'tmpfs', 'tmpfs', 'tmpfs'),
    ('Cleared at boot', 'yes', 'yes', 'yes', 'yes'),
    ('Age rules', 'tmpfiles.d', 'tmpfiles.d', 'tmpfiles.d', 'tmpfiles.d'),
    ('mktemp', 'coreutils', 'coreutils', 'coreutils', 'coreutils'),
    ('macOS', '-', '-', '-', 'BSD mktemp: -t differs'),
]) + teaser('2.4', 'Inside those temp folders, the heavy lifting is done by sed, awk and jq. Next: calling them correctly from scripts, passing variables in safely, and parsing JSON.')

CHEATSHEET = cheatsheet('Temp files and trap', [
    ('mktemp', [('t=$(mktemp)', 'file'), ('-d', 'folder'), ('name.XXXXXX', 'template'), ('TMPDIR=…', 'location')]),
    ('trap', [("trap 'f' EXIT", 'any exit'), ("trap 'exit 130' INT", 'Ctrl+C'), ("trap 'exit 143' TERM", 'kill'), ('trap -p', 'show')]),
    ('Clean-up', [('local rc=$?', 'keep status'), ('rm -rf -- "${w:?}"', 'safe'), ('KEEP=1', 'debug'), ('kill -9', 'no trap')]),
    ('Results', [('temp + mv', 'atomic'), ('same file system', 'required'), ('chmod 644', 'readers'), ('find -mmin +60', 'sweep')]),
])

MINDMAP = mindmap('Temp + trap', [
    ('mktemp', 'blue', ['unique', '0600/0700', 'TMPDIR']),
    ('trap', 'green', ['EXIT', 'INT 130', 'TERM 143']),
    ('Handler', 'amber', ['local rc=$?', '${w:?}', 'rm -rf --']),
    ('Atomic', 'violet', ['temp file', 'mv', 'same FS']),
    ('Limits', 'red', ['kill -9', 'power loss', 'tmpfs']),
    ('Sweep', 'acc', ['by name', 'by age', 'dry run']),
])

LAB = lab('a job that never leaks', 'Build the lab (it creates <code>~/lab23/data.txt</code> and a private <code>~/lab23/scratch</code> TMPDIR), write <code>~/lab23/job.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab23; mkdir -p ~/lab23/scratch ~/lab23/out && cd ~/lab23
seq 1 100 > data.txt; echo 'old result' > out/result.txt''',
    tasks=['<code>job.sh</code> creates its scratch space with <code>mktemp</code> (it will run with <code>TMPDIR=~/lab23/scratch</code>) and writes <code>sum 5050</code> to <code>out/result.txt</code> by building it in a temp file and moving it into place.',
           'After a successful run <code>~/lab23/scratch</code> must be empty and the exit code 0.',
           'With <code>FAIL=1</code> set, the job must fail with exit <b>1</b> before replacing the result: <code>out/result.txt</code> keeps its previous content and scratch is empty.',
           'When stopped with <code>kill</code> (SIGTERM) while running with <code>SLOW=3</code>, it must exit <b>143</b> and leave scratch empty.'],
    solution='''cat > job.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd ~/lab23
work=$(mktemp -d)
cleanup() { local rc=$?; rm -rf -- "${work:?}"; exit "$rc"; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
awk '{s += $1} END {print "sum", s}' data.txt > "$work/result"
sleep "${SLOW:-0}"
[[ ${FAIL:-} == 1 ]] && exit 1
tmp=$(mktemp out/.result.XXXXXX)
cp -- "$work/result" "$tmp"
mv -- "$tmp" out/result.txt
EOF
chmod +x job.sh''',
    check='''cd ~/lab23; export TMPDIR=$HOME/lab23/scratch; echo 'old result' > out/result.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 result"  './job.sh 2>/dev/null; [ "$(cat out/result.txt)" = "sum 5050" ] && grep -q mktemp job.sh'
ok "2 clean"   './job.sh 2>/dev/null; r=$?; [ $r -eq 0 ] && [ -z "$(ls -A scratch)" ] && [ -z "$(ls -A out | grep -v result.txt)" ]'
ok "3 failure" 'echo keep > out/result.txt; FAIL=1 ./job.sh 2>/dev/null; r=$?; [ $r -eq 1 ] && [ "$(cat out/result.txt)" = keep ] && [ -z "$(ls -A scratch)" ]'
ok "4 TERM"    'SLOW=3 ./job.sh 2>/dev/null & p=$!; sleep 1; kill $p; wait $p; r=$?; sleep 0.5; [ $r -eq 143 ] && [ -z "$(ls -A scratch)" ]' ''')
