import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

CLEAN = "pkill -u riya -x sleep; pkill -u riya -x yes; tmux kill-server 2>/dev/null; rm -rf ~/jb; mkdir -p ~/jb; cd ~/jb"
PS1 = "\"PS1='riya@web01:~/jb$ '; cd ~/jb; clear\" Enter"

def live(title, intro, steps, h=11, hid=None):
    """Record a real interactive bash in tmux. steps: [(keys shown, tmux keys, note)]."""
    for attempt in range(4):
        shots = tmux_screens(CLEAN + "; export PS1='$ '", 'bash --norc', [PS1] + [s[1] for s in steps], 64, h)
        if len(shots) > 2 and shots[1].strip().startswith('riya@web01') and not any('PS1=' in x or 'bash-5' in x for x in shots[1:]):
            break
    else:
        raise SystemExit('live(): terminal recording kept failing')
    shots = shots[2:]
    items = []
    for (show, _, note), shot in zip(steps, shots):
        items.append(f'<li class="fv"><p class="fv__sit"><b>Type</b> <kbd>{E(show)}</kbd> {note}</p><div class="code scr" data-lang="text" data-file="terminal"><pre><code>{E(shot)}</code></pre></div></li>')
    return f'''  <h3{f' id="{hid}"' if hid else ''}>{title}</h3>
  <p>{intro} <span class="muted">Real screens: recorded in an interactive bash in a terminal on Ubuntu 24.04, captured after each key.</span></p>
  <ol class="fvs">{''.join(items)}</ol>
'''

HOOK = hook('Riya starts a 40-minute backup over SSH, then needs her terminal for something else. She presses Ctrl+Z by accident and the progress freezes. Later she closes the laptop lid, the SSH session drops and the backup dies with it. The shell has <b>job control</b> for exactly this: run a command in the <b>background</b> with <code>&amp;</code>, pause it with <b>Ctrl+Z</b>, list jobs with <code>jobs</code>, continue them with <code>bg</code> and <code>fg</code>. To survive logout she needs <code>nohup</code>, <code>disown</code> or <code>setsid</code> (or tmux, Lesson 11.6). This lesson shows each one on real terminal screens.',
    ['run commands in the background with &, and see them with jobs, jobs -l and $!',
     'pause with Ctrl+Z, continue with bg and fg, and refer to jobs with %1, %+, %- and %name',
     'explain why closing a terminal kills its jobs (SIGHUP), and keep work alive with nohup, disown and setsid',
     'handle background output, wait for jobs in scripts, and avoid the common traps'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the backup that died'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What a job is', 6, 'simple meaning + 4 depths'),
    ('types', 'Foreground, background, stopped', 5, 'states and commands'),
    ('commands', 'By field', 15, 'real terminal screens'),
    ('animation', 'See it happen', 4, 'logout and SIGHUP'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'jobs that survive'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Start something and keep the prompt', 'cmd &', 'background'),
    ('Pause what is in front of you', 'Ctrl+Z', 'stopped'),
    ('Let the paused job continue behind', 'bg', 'background'),
    ('Bring a job back to the front', 'fg  /  fg %2', 'foreground'),
    ('See my jobs', 'jobs -l', 'list'),
    ('Must survive logout (new command)', 'nohup cmd > log 2>&1 &', 'ignore HUP'),
    ('Already running, must survive', 'disown -h %1   or   disown', 'detach'),
    ('Long interactive work over SSH', 'tmux / screen', 'Lesson 11.6'),
])

cmap = concept_map(
    [('11.1', 'Processes', 'parent and child'), ('11.3', 'Signals', 'HUP, TSTP, CONT'), ('5.2', 'Redirection', '> log 2>&1')],
    ['foreground vs background', '& and $!', 'jobs, fg, bg, %n', 'Ctrl+Z = SIGTSTP', 'SIGHUP on logout', 'nohup, disown, setsid, wait'],
    [('11.5', 'nice', 'background jobs at low priority'), ('11.6', 'tmux and screen', 'sessions that survive'), ('17.2', 'systemd', 'real services'), ('17.4', 'cron', 'scheduled jobs')],
    'One terminal, many jobs: one in front that gets your keys, the rest behind. Logging out sends them all a hang-up.')

sc = (term(20, 14, 316, 156, ['$ ./backup.sh', ('copying… 12%', 'out'), '^Z', ('[1]+  Stopped   ./backup.sh', 'acc'), '$ bg', ('[1]+ ./backup.sh &', 'out'), '$ jobs', ('[1]+  Running   ./backup.sh &', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=16)
      + t(352, 36, 'Job control:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['Ctrl+Z pauses', 'bg continues behind', 'fg brings it back', 'logout → HUP', 'nohup survives'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The backup that died</h2>
  <div class="story">
''' + puzzle('Riya runs <code>./backup.sh &amp;</code> over SSH and logs out; the backup stops. Next time she runs <code>nohup ./backup.sh &amp;</code>; it survives, but a file called <code>nohup.out</code> keeps growing in her home folder. A colleague runs <code>./backup.sh &amp; disown</code>, which also survives. And in a script, <code>fg</code> answers “no job control”. What is happening in each case?') + '''
    <p class="narration">Riya pauses a running job, sends it to the background and checks on it.</p>
''' + scene('A terminal: backup.sh is running, Ctrl+Z stops it, bg continues it in the background and jobs shows it running.', sc,
            'The prompt is back, but the job <tspan font-weight="700" class="s-acc">still belongs</tspan> to this terminal.') + '''
K> So Ctrl+Z did not cancel it?
A> No. Ctrl+Z sends SIGTSTP: the job is <b>stopped</b> (paused), keeping all its memory and open files. <code>bg</code> sends SIGCONT so it continues in the background; <code>fg</code> brings it back to the front.
R> And why did logging out kill it?
A> When the terminal closes, the shell gets <b>SIGHUP</b> (hang-up) and passes it to all its jobs. Their default action is to terminate. <code>nohup</code> and <code>disown</code> are two ways to stop that from happening. Today: all of it, on real screens.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A kitchen with one chef at the counter (foreground) and pots simmering on the back burners (background). One pot is taken off the heat (stopped). When the chef goes home and turns off the kitchen power (hang-up), every pot stops, except the one on its own gas line (nohup).">'
       + label_box(20, 24, 180, 110, ['FRONT counter', 'one job gets', 'your keyboard', '(foreground)'], 'blue', 9)
       + label_box(220, 24, 180, 110, ['BACK burners', 'jobs keep cooking', 'with &, bg', '(background)'], 'green', 9)
       + label_box(420, 24, 200, 110, ['OFF the heat', 'Ctrl+Z: paused,', 'nothing lost', '(stopped)'], 'amber', 9)
       + t(320, 162, 'Leaving the kitchen (logout) cuts the power: HUP to every job.', 9.8, 'acc', bold=True)
       + t(320, 184, 'nohup / disown / setsid give a pot its own gas line.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Jobs at four depths', [
    ('v', 'No jargon: a kitchen', '      <p>One dish in front of you, others simmering behind.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sleep 100 &amp;</code>: start in the background; you get <code>[1] 4120</code> (job 1, PID 4120).</li>
        <li><code>jobs</code>: list jobs of this terminal.</li>
        <li><kbd>Ctrl+Z</kbd> then <code>bg</code>: continue a job in the background.</li>
        <li><code>fg</code>: bring the last job back to the front.</li>
      </ul>'''),
    ('i', 'Job numbers and logout', '''      <ul>
        <li>Refer to jobs as <code>%1</code>, <code>%2</code>, <code>%+</code> (current, also <code>%%</code>), <code>%-</code> (previous) or <code>%sle</code> (name starts with).</li>
        <li><code>$!</code> is the PID of the last background job; <code>wait</code> waits for jobs; <code>kill %1</code> signals a job.</li>
        <li>On logout or terminal close, bash sends SIGHUP to its jobs (and SIGCONT to stopped ones so they can die).</li>
        <li><code>nohup cmd</code> sets HUP to “ignore” and redirects output to <code>nohup.out</code> if it is a terminal.</li>
        <li><code>disown</code> removes a job from the shell’s table so it is not sent HUP; <code>disown -h</code> keeps it listed but skips the HUP.</li>
      </ul>'''),
    ('a', 'Behind the screen: sessions and process groups', '''      <ul>
        <li>Each pipeline you start is a <b>process group</b>. The terminal has one <b>foreground process group</b>: only it may read the keyboard, and Ctrl+C / Ctrl+Z go to the whole group.</li>
        <li>A background job that tries to read the terminal gets <b>SIGTTIN</b> and stops (“Stopped (tty input)”); writing is allowed unless <code>stty tostop</code>.</li>
        <li>The shell, its jobs and the terminal form a <b>session</b>; the shell is the session leader. When the terminal hangs up, the kernel sends SIGHUP to the leader, and bash forwards it to its jobs.</li>
        <li><code>setsid cmd</code> starts cmd in a <b>new session</b> with no terminal: it never receives the terminal’s HUP.</li>
        <li>Scripts run with job control <b>off</b> (<code>set +m</code>): no %job notifications, and <code>fg</code>/<code>bg</code> fail with “no job control”, but <code>&amp;</code>, <code>$!</code>, <code>jobs</code> and <code>wait</code> work.</li>
        <li>systemd-logind can also kill user processes at logout (<code>KillUserProcesses=</code>); on Ubuntu it is off by default.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Jobs, job control and nohup</h2>
''' + def_block(
    'A <b>job</b> is a command or pipeline started from an interactive shell, tracked by a job number. <b>Job control</b> lets the user run jobs in the <b>foreground</b> (attached to the keyboard) or the <b>background</b> (<code>&amp;</code>), stop them (<kbd>Ctrl+Z</kbd>) and move them with <code>bg</code>, <code>fg</code> and <code>jobs</code>. <code>nohup</code> runs a command immune to SIGHUP, and <code>disown</code> removes a job from the shell so it survives logout.',
    'Several jobs per terminal; one in front, the others behind; keep the ones that must outlive you away from the hang-up.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Job', 'A command started from the shell, with a number.'),
    ('Foreground', 'Gets your keyboard; you wait for it.'),
    ('Background', 'Runs while you keep typing (&).'),
    ('Stopped', 'Paused with Ctrl+Z (SIGTSTP).'),
    ('%1', 'Job number 1 (not PID 1).'),
    ('$!', 'PID of the last background job.'),
    ('SIGHUP', 'Hang-up, sent when the terminal closes.'),
    ('nohup / disown / setsid', 'Ways to survive logout.'),
]) + '\n' + names('Where the names come from.', [
    ('&', 'ampersand: “and also”', 'Run this and continue.'),
    ('fg / bg', 'foreground / background', 'csh, 1979.'),
    ('jobs', 'the job table', 'csh.'),
    ('nohup', 'no hang-up', 'Unix V7.'),
    ('disown', 'give up ownership', 'bash.'),
    ('setsid', 'set session ID', 'setsid(2).'),
    ('TSTP', 'terminal stop', 'Ctrl+Z.'),
    ('TTIN', 'terminal input', 'Background read.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Background', '<code>cmd &amp;</code>'),
    ('Pause', '<kbd>Ctrl+Z</kbd>'),
    ('Continue behind', '<code>bg</code>'),
    ('To the front', '<code>fg %1</code>'),
    ('Survive logout', '<code>nohup cmd &amp;</code>'),
    ('Wait in scripts', '<code>wait</code>'),
]) + '\n' + lv + didyou('“Hang-up” is a real telephone word: Unix terminals were connected by modems, and when the phone line dropped the modem signalled a hang-up. The signal kept the name for 50 years; today it fires when an SSH connection drops or a terminal window closes.') + '''
EXAM> “What is the difference between nohup and &?” → & runs a job in the background but it still receives SIGHUP on logout; nohup makes the command ignore SIGHUP (usually combined: nohup cmd &).
''' + qc('Does Ctrl+Z end a program?', 'No. It stops (pauses) it; fg or bg continues it. Ctrl+C is the one that interrupts.') + mistake('cmd &   then log out, expecting it to keep running',
    'nohup cmd > cmd.log 2>&1 &   ·   or cmd & disown   ·   or run it inside tmux',
    'A plain background job still gets SIGHUP when the terminal closes (real run: the sleep died).') + mistake('kill 1 to stop job 1',
    'kill %1',
    'Without %, 1 is PID 1 (systemd): “Operation not permitted” as a user, a disaster as root.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Job states and the commands that move them</h2>
''' + table(['State', 'What it means', 'How you get there', 'ps STAT'], [
    ['Foreground, running', 'you wait; keys go to it', 'type a command; fg', 'R or S, with +'],
    ['Background, running', 'runs; you keep typing', '<code>&amp;</code>; bg', 'R or S (no +)'],
    ['Stopped', 'paused, memory kept', 'Ctrl+Z; kill -STOP', 'T'],
    ['Stopped (tty input)', 'background job wanted the keyboard', 'reading while in background', 'T'],
    ['Done / Terminated', 'finished; shown once by jobs', 'exit; kill', 'gone'],
], minw=520) + table(['Command', 'Does'], [
    ['<code>cmd &amp;</code>', 'start in the background, print [job] PID'],
    ['<code>jobs</code> / <code>jobs -l</code> / <code>jobs -p</code>', 'list jobs / with PIDs / only PIDs'],
    ['<code>fg [%n]</code>', 'bring to the foreground (sends CONT if stopped)'],
    ['<code>bg [%n]</code>', 'continue a stopped job in the background'],
    ['<kbd>Ctrl+Z</kbd>', 'stop the foreground job (SIGTSTP)'],
    ['<code>kill %n</code>', 'signal a job'],
    ['<code>wait [%n|PID]</code>', 'wait until jobs finish; returns their status'],
    ['<code>disown [-h] [%n]</code>', 'remove from the job table / only skip HUP'],
], minw=440) + table(['Way to survive logout', 'Use for', 'Output', 'Can you come back to it?'], [
    ['<code>nohup cmd &amp;</code>', 'a new long command', 'nohup.out (or your redirect)', 'no (only its log)'],
    ['<code>cmd &amp; disown</code>', 'a job you already started', 'still tied to the dead terminal: redirect it', 'no'],
    ['<code>setsid cmd</code>', 'fully detached, new session', 'redirect it', 'no'],
    ['<code>tmux</code> / <code>screen</code>', 'interactive work', 'on screen', '<b>yes</b>, reattach (11.6)'],
    ['systemd service / timer', 'real long-running services', 'journal', 'yes, systemctl status (17.2)'],
], minw=520) + qc('What is the difference between %1 and 1 in kill?', '%1 is job number 1 of this shell; 1 is process ID 1 (systemd).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Background, Ctrl+Z, bg/fg, and surviving logout, then used in every field</h2>
  <p id="commands">The screens below are real: an interactive bash running in tmux on our Ubuntu 24.04 build machine as riya, captured after each key. Plain examples (not screens) were run as scripts, where job control is off.</p>
''' + live('Ctrl+Z, bg, fg: a real session', 'Start a long command, pause it, continue it behind, bring it back, then interrupt it.', [
    ('sleep 300', "'sleep 300' Enter", 'and wait: the prompt does not come back, the job is in the foreground.'),
    ('Ctrl+Z', 'C-z', 'The shell prints [1]+ Stopped: job 1 is paused.'),
    ('bg', "'bg' Enter", 'Job 1 continues in the background (note the &).'),
    ('sleep 200 &', "'sleep 200 &' Enter", 'A second job: [2] and its PID.'),
    ('jobs -l', "'jobs -l' Enter", '+ marks the current job, - the previous one.'),
    ('fg %1', "'fg %1' Enter", 'Job 1 is in front again; the prompt is gone.'),
    ('Ctrl+C', 'C-c', 'SIGINT ends it; job 2 is still running.'),
    ('kill %2; jobs', "'kill %2; sleep 0.3; jobs' Enter", 'Signal by job number; jobs reports Terminated once.'),
], h=14, hid='live-jobs') + cmdcard_u(['long commands you do not need to watch', 'starting several tasks at once'],
               ['commands that ask for input', 'forgetting where the output goes'])(
    'bg', 'cmd & · $! · jobs [-l|-p] · wait', 'background jobs',
    'A <code>&amp;</code> at the end runs the command in the background; the shell prints the job number and PID and returns the prompt. <code>$!</code> holds the PID. Background jobs still write to the terminal, so redirect their output. <code>wait</code> waits for all background jobs (or one PID) and returns its exit status.',
    'cmd > log 2>&1 &   ·   pid=$!   ·   wait $pid', 'safe',
    [('cmd &', 'run behind', 'long jobs'),
     ('$!', 'last background PID', 'scripts'),
     ('jobs -l', 'with PIDs', 'check'),
     ('jobs -p', 'PIDs only', 'kill $(jobs -p)'),
     ('wait', 'all jobs', 'scripts'),
     ('wait $pid', 'one job, its status', 'errors'),
     ('wait -n', 'the next to finish', 'pools')],
    dict(setup=CLEAN, cmd="cd ~/jb\n( sleep 1; echo 'report done' ) > report.log 2>&1 &\npid=$!\njobs -l | sed \"s/$pid/PID/\"\necho \"started PID $pid\" | sed 's/[0-9]\\+/N/'\nwait $pid; echo \"finished with status $?\"; cat report.log", note='In a script the job number still appears in jobs, and wait collects the status.'),
    [('data', [
        dict(situation='Run three tasks in parallel and wait for all.', setup=CLEAN, cmd="cd ~/jb; start=$SECONDS\nfor n in 1 2 3; do ( sleep 1; echo \"part $n ready\" > part$n.txt ) & done\nwait\necho \"3 one-second tasks took $((SECONDS - start)) s\"; cat part*.txt", why='Parallel jobs: the total is about 1 s, not 3 s.')]),
     ('dev', [
        dict(situation='Collect each job’s status.', cmd="( sleep 0.3; exit 0 ) & a=$!\n( sleep 0.2; exit 3 ) & b=$!\nwait $a; echo \"a: $?\"; wait $b; echo \"b: $?\"", why='wait PID returns that job’s exit code, so a script can detect a failed part.')]),
    ],
    anat=anatomy([('sleep 300', 'cmd', 'the command'), ('> log 2>&1', 'arg', 'keep output off the screen'), ('&', 'opt', 'run in the background')], 'The & comes last. Redirect output so it does not mix with your typing.')
) + cmdcard_u(['moving between tasks in one terminal', 'pausing something to free the terminal'],
               ['scripts (job control is off)', 'stopping jobs that hold locks for others'])(
    'fgbg', 'Ctrl+Z · bg [%n] · fg [%n] · %+ %- %name', 'stop, continue and switch',
    '<kbd>Ctrl+Z</kbd> stops the foreground job. <code>bg</code> continues it in the background, <code>fg</code> in the foreground. Without an argument they use the current job (<code>%+</code>); otherwise name it: <code>%2</code>, <code>%-</code>, <code>%vim</code> (name starts with), <code>%?log</code> (name contains). <code>%2</code> alone is the same as <code>fg %2</code>.',
    'Ctrl+Z   ·   bg   ·   fg %2   ·   %vim', 'safe',
    [('Ctrl+Z', 'stop', 'pause'),
     ('bg', 'continue behind', 'free the prompt'),
     ('fg', 'continue in front', 'interact again'),
     ('%2', 'job 2 (= fg %2)', 'switch'),
     ('%vim', 'name starts with vim', 'by name'),
     ('%-', 'previous job', 'toggle'),
     ('kill %1', 'signal a job', 'stop it')],
    dict(cmd="set -m\nsleep 30 & sleep 31 &\njobs\nkill -STOP %1; sleep 0.2; jobs\nbg %1 > /dev/null; sleep 0.2; jobs\nkill %1 %2; wait 2>/dev/null; true", note='set -m turns job control on in a script; kill -STOP here plays the role of Ctrl+Z.'),
    [('qa', [
        dict(situation='The puzzle: fg in a script.', cmd="sleep 5 &\nfg 2>&1\nkill %1", expect='any', why='Scripts run without job control, so fg and bg refuse. Use wait and kill instead.')]),
    ]
) + live('Logout and SIGHUP: which jobs survive?', 'A real terminal starts four sleeps in different ways; then the terminal is closed (we kill the tmux session, which is what happens when an SSH connection drops).', [
    ('sleep 300 &', "'sleep 300 &' Enter", 'A plain background job.'),
    ('nohup sleep 301 &', "'nohup sleep 301 &' Enter", 'nohup tells you where output will go.'),
    ('sleep 302 & disown', "'sleep 302 & disown' Enter", 'disown removes it from the job table.'),
    ('setsid sleep 303', "'setsid sleep 303' Enter", 'setsid starts a new session (and returns at once).'),
    ('jobs', "'jobs' Enter", 'Only 300 and 301 are still jobs of this shell.'),
], h=12, hid='live-hup') + cmdcard_u(['long downloads, builds, backups over SSH', 'a job you forgot to start with nohup'],
               ['services that should restart on failure (use systemd)', 'work you want to watch later (use tmux)'])(
    'nohup', 'nohup cmd & · disown [-h] [%n] · setsid cmd', 'surviving logout',
    '<code>nohup</code> makes the command ignore SIGHUP and, if output is a terminal, appends it to <code>nohup.out</code>. <code>disown</code> works on a job that is already running. <code>setsid</code> starts the command in a new session without a terminal. In all cases, redirect output to a log file yourself.',
    'nohup cmd > cmd.log 2>&1 &   ·   disown %1   ·   setsid cmd > log 2>&1 < /dev/null &', 'safe',
    [('nohup cmd &', 'ignore HUP', 'new commands'),
     ('> log 2>&1', 'your own log', 'not nohup.out'),
     ('disown', 'forget the current job', 'already running'),
     ('disown -h %1', 'keep listed, skip HUP', 'still see it in jobs'),
     ('disown -a', 'all jobs', 'leaving now'),
     ('setsid cmd', 'new session', 'fully detached'),
     ('shopt huponexit', 'HUP at login-shell exit', 'off by default')],
    dict(setup=CLEAN, cmd="cd ~/jb; tmux -f /dev/null new-session -d -s t 'bash --norc -i'; sleep 0.5\ntmux send-keys -t t 'sleep 300 &' Enter 'nohup sleep 301 > /dev/null 2>&1 &' Enter 'sleep 302 & disown' Enter 'setsid sleep 303 &' Enter; sleep 0.8\necho 'before closing:'; pgrep -a -u riya -x sleep | grep -v defunct | awk '{print \"  \"$2, $3}'\ntmux kill-session -t t; sleep 0.5\necho 'after closing the terminal:'; pgrep -a -u riya -x sleep | grep -v defunct | awk '{print \"  \"$2, $3}'\npkill -u riya -x sleep", note='The plain background job died with the terminal; nohup, disown and setsid survived.'),
    [('sys', [
        dict(situation='nohup without a redirect.', setup=CLEAN, cmd="cd ~/jb; script -qc 'nohup echo hello from nohup' /dev/null | tr -d '\\r'\ncat nohup.out", why='With a terminal, nohup appends to nohup.out (here in the current folder) and says so. That is the growing file from the puzzle; always redirect.')]),
     ('dev', [
        dict(situation='disown -h: still listed, but protected.', cmd="set -m; sleep 40 & disown -h %1; jobs; sleep 41 & disown %2 2>/dev/null || disown; jobs; pkill -P $$ -x sleep", expect='any', why='-h keeps the job in the table (you can still fg it) but HUP is not sent.')]),
    ]
) + undo('A job killed by logout is gone; rerun it properly.', [
    ('Stopped with Ctrl+Z by mistake:', '<code>fg</code> (or <code>bg</code>).'),
    ('Job died at logout:', 'restart with <code>nohup … &amp;</code>, or inside tmux.'),
    ('nohup.out is huge:', '<code>: &gt; nohup.out</code> empties it; next time redirect to a log you rotate.'),
    ('“There are stopped jobs” when exiting:', 'type <code>jobs</code>, then fg/kill them; exiting again kills them.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='fg', meaning='No job control in a script (or no jobs).', fix='Use an interactive shell; in scripts use wait.'),
    dict(cmd='set -m; fg %3', meaning='There is no job 3.', fix='jobs to see the numbers.'),
    dict(cmd='kill %1', meaning='No job 1 in this shell.', fix='jobs -l; or kill the PID.'),
    dict(cmd='wait 999999', meaning='Not a child of this shell.', fix='wait only for your own background jobs.'),
]) + qc('Which command continues a stopped job in the background?', 'bg.') + '''
'''
cards = cards + '</section>\n'

def sess(k):
    alive = [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 1, 1, 1], [0, 0, 1, 1, 1]][k]
    hup = k >= 1
    names_ = ['terminal', 'bash', 'sleep 300 (&)', 'nohup sleep 301', 'setsid sleep 303']
    o = ''
    pos = [(130, 10), (130, 52), (20, 100), (130, 100), (240, 136)]
    for i, (x, y) in enumerate(pos):
        col = ('red' if not alive[i] else ('green' if i >= 3 else ('amber' if hup and i < 3 and k == 1 else 'blue')))
        if i == 2 and k >= 2:
            col = 'red'
        o += label_box(x, y, 110, 30, [names_[i] + ('' if alive[i] or i == 2 else ' ✗')], col, 7.6)
    if k == 1:
        o += t(180, 190, 'SIGHUP!', 9, 'red', bold=True)
    return o
see_cmds = [['$ sleep 300 &', '$ nohup sleep 301 &', '$ setsid sleep 303'], ['(SSH connection drops)'], ['(terminal and bash are gone)'], ['$ pgrep -a sleep   # new login', ('301 sleep 301', 'out'), ('303 sleep 303', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Three jobs.', 'The line drops.', 'HUP delivered.', 'Who survived?'])]
behind = [sess(k) for k in range(4)]
two = anim_two('Logging out', 'Behind the screen: the session and SIGHUP',
               'A terminal starting three sleeps; the SSH connection drops; a new login shows which ones survived.',
               'Boxes for terminal, bash and three jobs: on hang-up, the terminal, bash and the plain background job turn red; nohup and setsid jobs stay green.', see, behind,
               ['Start.', 'Hang-up.', 'Dead.', 'Survivors.'],
               ['start', 'HUP', 'gone', 'left'])

def states(k):
    lab = ['Foreground (running)', 'Stopped (T)', 'Background (running)', 'Foreground again']
    keys = ['sleep 300', 'Ctrl+Z', 'bg', 'fg']
    col = ['blue', 'amber', 'green', 'blue']
    o = ''
    for i in range(4):
        o += label_box(10 + i * 86, 40, 80, 56, [keys[i], lab[i].split(' (')[0]], col[i] if i <= k else 'card', 7.4)
    o += t(180, 140, lab[k], 9.4, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'One job, four states',
              'Each key moves the job to a new state.',
              'Ctrl+Z · bg · fg', 'Four boxes in a row: foreground, stopped after Ctrl+Z, background after bg, foreground again after fg.', [states(k) for k in range(4)],
              ['Start.', 'Ctrl+Z.', 'bg.', 'fg.'], hid='scenario-states')

dx = dissect('Layer by layer: what makes a job',
    'Each layer has a real command and output from our build machine.', [
    dict(key='pg', name='Process group', sub='PGID', why='Signals go to the group.', how='One per pipeline.', impl='setpgid().', used='Ctrl+C.',
         cmd="set -m; sleep 30 | sleep 31 & sleep 0.2; n=$(ps -o pgid=,comm= --ppid $$ | awk '$2==\"sleep\"{print $1}' | sort -u | wc -l); echo \"2 sleeps in a pipeline, $n process group\"; [ \"$(ps -o pgid= -p $$)\" != \"$(ps -o pgid= -p $(pgrep -n -x sleep))\" ] && echo 'and it is not the shell’s group'; kill %1"),
    dict(key='sess', name='Session', sub='SID', why='Logout = session ends.', how='Shell leads it.', impl='setsid().', used='HUP.',
         cmd="ps -o sid= -p $$ >/dev/null; s1=$(ps -o sid= -p $$); setsid sleep 0.5 & sleep 0.1; s2=$(ps -o sid= -p $(pgrep -n -x sleep)); [ \"$s1\" != \"$s2\" ] && echo 'setsid: different session'"),
    dict(key='sig', name='HUP disposition', sub='/proc', why='nohup sets ignore.', how='SigIgn bit 1.', impl='signal(SIGHUP, SIG_IGN).', used='nohup.',
         cmd="nohup sleep 3 > /dev/null 2>&1 & p=$!; sleep 0.2; m=$(awk '/SigIgn/{print $2}' /proc/$p/status); (( 0x$m & 1 )) && echo 'HUP is ignored in the nohup process'; kill $p"),
    dict(key='tty', name='Background reads', sub='SIGTTIN', why='Only the front reads keys.', how='Kernel tty driver.', impl='stops the job.', used='Stopped (tty input).',
         cmd="echo 'a background job may write:'; ( echo '  hello from behind' ) & wait"),
], hint='From process groups to the terminal. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Logging out, and the four states of a job</h2>
''' + two + s1 + dx + qc('Why did the plain background job die but the nohup one survive?', 'Both got SIGHUP; the nohup process had HUP set to “ignore” (see its SigIgn bit), the plain one used the default action: terminate.') + '''
</section>
'''

VAR = variations('Sixteen more experiments with jobs, wait and nohup. All were really run on our build machine.', [
    ('Background and wait', [
        dict(title='Two downloads at once (simulated)', cmd="( sleep 0.4; echo 'a.iso done' ) & ( sleep 0.2; echo 'b.iso done' ) & wait; echo 'both finished'", why='Output appears in the order the jobs finish.'),
        dict(title='wait -n: react to the first finisher', cmd="( sleep 0.5; exit 1 ) & ( sleep 0.1; exit 0 ) & wait -n; echo \"first finished with $?\"; wait", why='Useful for a pool of workers.'),
        dict(title='Limit to N jobs at a time', cmd="for i in 1 2 3 4 5 6; do ( sleep 0.2; echo \"task $i\" ) & (( $(jobs -rp | wc -l) >= 2 )) && wait -n; done; wait", why='At most two jobs run at the same time.'),
        dict(title='A spinner while a job works', cmd="( sleep 1 ) & p=$!; n=0; while kill -0 $p 2>/dev/null; do n=$((n+1)); sleep 0.2; done; echo \"job done after about $n checks\"", why='kill -0 polls the job (Lesson 11.3).'),
        dict(title='Background output mixed with yours', cmd="( for i in 1 2 3; do echo \"  bg line $i\"; sleep 0.1; done ) & echo 'you keep typing...'; wait", why='The reason to redirect background output.'),
        dict(title='Kill all my jobs at the end', cmd="sleep 30 & sleep 31 & echo \"jobs: $(jobs -p | wc -l)\"; kill $(jobs -p); wait 2>/dev/null; echo \"left: $(jobs -rp | wc -l)\"", why='jobs -p gives PIDs for kill.'),
    ]),
    ('Job control (set -m)', [
        dict(title='Current and previous job', cmd="set -m; sleep 30 & sleep 31 & sleep 32 & jobs | cut -c1-4; kill %1 %2 %3", why='+ is the newest, - the one before.'),
        dict(title='Refer to a job by name', cmd="set -m; sleep 30 & yes > /dev/null & jobs %yes; kill %yes %sleep", why='%yes = job whose command starts with yes.'),
        dict(title='Stop and continue by job number', cmd="set -m; timeout 20 yes > /dev/null & sleep 0.2; kill -STOP %1; sleep 0.1; jobs; kill -CONT %1; sleep 0.1; jobs; kill %1", why='The script version of Ctrl+Z and bg.'),
        dict(title='A background job that reads the keyboard', setup="cd ~; cat > ask.sh <<'EOF'\nread -p 'name? ' n; echo \"hi $n\"\nEOF", cmd="tmux -f /dev/null new-session -d -s q 'bash --norc -i'; sleep 0.4; tmux send-keys -t q 'bash ~/ask.sh &' Enter; sleep 0.6; tmux send-keys -t q 'jobs' Enter; sleep 0.4; tmux capture-pane -t q -p | grep -E 'Stopped|Running|\\[1\\]' | sed -E 's/[0-9]{3,}/PID/'; tmux kill-server", expect='any', why='It wanted input while in the background, so the kernel stopped it (SIGTTIN).'),
    ]),
    ('Surviving logout', [
        dict(title='nohup with your own log', setup=CLEAN, cmd="cd ~/jb; nohup bash -c 'echo started; sleep 0.3; echo finished' > job.log 2>&1 & wait; cat job.log; ls nohup.out 2>&1", expect='any', why='With a redirect, no nohup.out is created.'),
        dict(title='nohup and its exit codes', cmd="nohup false > /dev/null 2>&1; echo \"false: $?\"; nohup nosuchcmd > /dev/null 2>&1; echo \"missing: $?\"", why='nohup returns the command’s status, or 127 if it cannot run it.'),
        dict(title='setsid has no terminal', cmd="setsid bash -c 'tty; ps -o tty= -p $$' 2>&1 | head -2; true", why='“not a tty” and ? : fully detached.'),
        dict(title='huponexit is off by default', cmd="shopt huponexit; true", why='bash sends HUP to jobs when a login shell exits only if this is on; the terminal hang-up still sends it.'),
        dict(title='timeout + nohup for a safe long job', setup=CLEAN, cmd="cd ~/jb; nohup timeout 1 sleep 5 > t.log 2>&1 & p=$!; wait $p; echo \"status $? (124 = stopped by timeout)\"", why='A limit so a forgotten job cannot run forever.'),
        dict(title='What runs without a terminal?', cmd="ps -u riya -o tty=,comm= | awk '$1==\"?\"' | sort | uniq -c | head -3 | sed -E 's/^ +//'", why='Processes with TTY ? have no terminal: daemons, nohup/setsid jobs.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Jobs at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['nohup', 'SSH'], 'blue', 8.6), '1. Long tasks over SSH',
              'nohup ./restore.sh > restore.log 2>&1 & then tail -f restore.log; the restore survives a dropped connection.', ['Start', '*nohup &', 'log out safely']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['& + wait', 'speed'], 'green', 8.6), '2. Parallel scripts',
    'Copy to three servers at once with & and wait; the script finishes when the slowest one does.', ['Start N', '*wait', 'all done']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Ctrl+Z', 'editing'], 'amber', 8.6), '3. Switching tasks in one terminal',
    'In vim press Ctrl+Z, run a command, fg back to the same cursor position.', ['Edit', '*Ctrl+Z / fg', 'continue']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['HUP', 'outages'], 'red', 8.6), '4. Avoiding “it stopped when I logged out”',
    'A classic incident: a migration started with & over VPN died when the VPN dropped. Teams now require tmux or nohup.', ['Incident', '*tmux / nohup', 'rule']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['systemd', 'services'], 'violet', 8.6), '5. Real services',
    'Anything that should always run (an API, a worker) becomes a systemd service, not a nohup job (Lesson 17.3).', ['Prototype nohup', '*systemd', 'production']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Start and remember the PID', scenario='Stop it later.', cmd="sleep 30 & echo $! > ~/job.pid; kill \"$(cat ~/job.pid)\"; rm ~/job.pid; echo stopped", explain='$! right after &.'),
    dict(level='b', title='How many jobs?', scenario='Before exit.', cmd="sleep 10 & sleep 11 & jobs | wc -l; kill $(jobs -p)", explain='2.'),
    dict(level='i', title='Safe long job', scenario='Over SSH.', setup=CLEAN, cmd="cd ~/jb; nohup bash -c 'sleep 0.2; echo ok' > long.log 2>&1 & wait; cat long.log", explain='nohup + log + &.'),
    dict(level='i', title='Fail if any part fails', scenario='CI.', cmd="pids=(); for c in true false true; do $c & pids+=($!); done; fail=0; for p in \"${pids[@]}\"; do wait $p || fail=$((fail+1)); done; echo \"$fail failed\"", explain='wait each PID.'),
    dict(level='a', title='Detach completely', scenario='Fire and forget.', cmd="setsid -f bash -c 'sleep 0.1' < /dev/null > /dev/null 2>&1; echo \"returned at once, status $?\"", explain='setsid -f forks into a new session.'),
], extra=build_up('a parallel backup', 'Riya turns a slow serial backup into a parallel, logout-safe one.', CLEAN + "; mkdir -p src/{a,b,c}; for d in a b c; do head -c 200000 /dev/urandom > src/$d/data.bin; done", [
    ("cd ~/jb; s=$SECONDS; for d in a b c; do tar czf $d.tgz -C src $d; sleep 1; done; echo \"serial: $((SECONDS-s)) s\"", '1. One after another (sleep stands in for a slow disk).'),
    ("cd ~/jb; s=$SECONDS; for d in a b c; do ( tar czf $d.tgz -C src $d; sleep 1 ) & done; wait; echo \"parallel: $((SECONDS-s)) s\"", '2. In parallel with & and wait.'),
    ("cd ~/jb; for d in a b c; do ( tar czf $d.tgz -C src $d && echo \"$d ok\" || echo \"$d FAILED\" ) >> backup.log 2>&1 & done; wait; sort backup.log", '3. A log of each part.'),
    ("cd ~/jb; rm -f backup.log; nohup bash -c 'for d in a b c; do tar czf $d.tgz -C src $d & done; wait; echo all done' > backup.log 2>&1 & wait; cat backup.log", '4. The whole thing under nohup: safe to log out.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Run something behind', 'cmd &', 'Simple.', 'Opening a second terminal.'),
    ('Paused by mistake', 'fg / bg', 'Nothing lost.', 'Killing and restarting.'),
    ('New long command over SSH', 'nohup … &', 'Ignores HUP.', 'A plain &.'),
    ('Already running, must survive', 'disown', 'No restart.', 'Hoping.'),
    ('Want to come back and watch', 'tmux / screen', 'Reattach.', 'nohup (only a log).'),
    ('Permanent service', 'systemd', 'Restarts, logs.', 'nohup in rc.local.'),
]) + keys('Keys and forms.', [
    ('Ctrl+Z', 'stop the front job', 'TSTP'),
    ('bg / fg', 'continue behind / in front', 'CONT'),
    ('%1 %+ %-', 'job numbers', 'jobs'),
    ('$!', 'last background PID', 'scripts'),
    ('jobs -l', 'list with PIDs', 'check'),
    ('wait', 'until all jobs end', 'scripts'),
]) + scriptit('runpool.sh', 'Run a list of tasks in the background with at most 3 at a time, log each result with its duration, and report how many failed. Safe to start with nohup.',
'''max=3; fail=0; log=~/pool.log; : > "$log"
tasks=("sleep 0.3" "sleep 0.1" false "sleep 0.2" "ls /nope" "sleep 0.1")
run(){ local s=$SECONDS; if bash -c "$1" > /dev/null 2>&1; then r=ok; else r=FAIL; fi; echo "$r  $1  ($((SECONDS-s))s)" >> "$log"; [ $r = ok ]; }
for t in "${tasks[@]}"; do
  while (( $(jobs -rp | wc -l) >= max )); do wait -n || fail=$((fail+1)); done
  run "$t" &
done
while (( $(jobs -rp | wc -l) > 0 )); do wait -n || fail=$((fail+1)); done
sort "$log"; echo "${#tasks[@]} tasks, $fail failed"''',
'<p>Six sample tasks, two of which fail.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>&amp;</code> only puts the job in the background; it is still a job of that shell, so when SSH dropped, bash got SIGHUP and passed it on. <b>2.</b> <code>nohup</code> ignores HUP, and because its output was still the terminal it appended everything to <code>nohup.out</code>: redirect it, <code>nohup ./backup.sh &gt; backup.log 2&gt;&amp;1 &amp;</code>. <b>3.</b> <code>disown</code> removes the job from the shell’s table, so bash does not send it HUP. <b>4.</b> Scripts run without job control; fg/bg only work in an interactive shell (or after <code>set -m</code>). In scripts, use <code>wait</code> and <code>kill</code>.') + qc('Which survives a dropped SSH connection: cmd &amp; or nohup cmd &amp;?', 'nohup cmd &amp; (or disown, setsid, tmux).') + '''
</section>
'''

_sh.run_sh(CLEAN + '; rm -rf ~/jb ~/ask.sh ~/pool.log', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../03-signals-kill-pkill-killall-sigterm-vs-sigkill/">Lesson 11.3</a> (signals: HUP, TSTP, CONT).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
