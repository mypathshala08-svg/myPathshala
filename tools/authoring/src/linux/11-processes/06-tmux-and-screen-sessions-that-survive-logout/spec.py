import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='06-tmux-and-screen-sessions-that-survive-logout', n='11.6',
    module_label='Module 11 · Processes',
    title='tmux and screen: terminal sessions that survive logout',
    desc='tmux from zero with real terminal screens: server, sessions, windows and panes; tmux new -s, Ctrl+b d, tmux ls, tmux attach -t, new -A, kill-session; Ctrl+b c % " z [ w s ?; scripting with send-keys, capture-pane, pipe-pane and format strings; ~/.tmux.conf; GNU screen equivalents; tmux vs nohup vs systemd; 30+ examples.',
    og_desc='tmux explained with real recorded screens: detach and attach, windows, panes, keys, scripting and screen equivalents.',
    minutes=35, level='Beginner → Advanced',
    lead='Keep your terminal on the server: start work in tmux, detach, lose the connection, and attach again from anywhere. Sessions, windows, panes, the key bindings and scripting, on real screens.',
    chips=['Real tmux screens', 'Detach / attach animated', 'Scripting tmux', 'Practice lab with checker', 'tmux vs screen table'],
)

MAIN = """# tmux needs a real terminal, so the browser shows the idea with a log file:
# the "session" keeps writing even when nobody is watching.
( for i in 1 2 3 4 5; do echo "restore step $i"; sleep 0.3; done ) > session.log &
echo "detached: the job keeps running"
sleep 0.7
echo "peek 1: $(tail -1 session.log)"
sleep 1
echo "peek 2: $(tail -1 session.log)"
wait
echo "attach: full history"; cat session.log
"""

RUN = dict(
    heading='The idea behind detach and attach',
    intro='<p>The browser cannot run tmux (it needs a real terminal), so this simulates a session with a background job and a log. The real tmux screens are above; the real commands are in <b>Run on your PC</b>.</p>',
    code=MAIN,
    anno=[('tail -1 session.log', 'Like tmux capture-pane: look without attaching.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Does the job wait for you?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many lines are in the log at the end?',
             code="( for i in 1 2 3; do echo line $i; sleep 0.2; done ) > s.log &\nwait\nwc -l < s.log\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the peek happens too early. Add sleep 0.5 before it.',
             code="( sleep 0.3; echo done ) > s.log &\necho \"peek: [$(cat s.log)]\"\nwait\n"),
        dict(label='4 · Your turn', hint='Write the tmux command that would create a detached session called backup running ./backup.sh.',
             code="echo \"tmux new -d -s backup './backup.sh'\"\n"),
        dict(label='5 · Challenge', hint='Print a tmux cheat line for each key.',
             code="for k in 'd:detach' 'c:new window' '%:split left|right' '\"\":split top/bottom'; do echo \"Ctrl+b ${k%%:*}  ->  ${k#*:}\"; done\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real tmux',
    intro='<p>Install with <code>sudo apt install tmux</code> (Ubuntu) or <code>sudo dnf install tmux</code>. Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Version', cmd='tmux -V', output=pc('tmux -V'), note='Recorded.'),
        dict(title='2 · Start, detach, list', cmd='tmux new -s work   # then Ctrl+b d\ntmux ls', output='[detached (from session work)]\nwork: 1 windows (created Thu Nov 12 10:15:02 2026)', note='Recorded format (see the live screens).'),
        dict(title='3 · Real disconnect test', cmd='ssh you@server\ntmux new -s t\nping -i 1 localhost   # now close the terminal window\nssh you@server\ntmux a -t t', output='64 bytes from localhost: icmp_seq=212 ttl=64 time=0.040 ms', note='Typical: the ping counter kept going while you were away.'),
        dict(title='4 · GNU screen', cmd='screen -S work   # Ctrl+a d to detach\nscreen -ls\nscreen -r work', output='There is a screen on:\n\t4120.work\t(Detached)\n1 Socket in /run/screen/S-you.', note='Typical (install with sudo apt install screen).'),
    ],
)

TRACE = dict(
    heading='A session in a script, line by line',
    intro='<p>Step through the simulation: start, peek, finish.</p>',
    code='''( echo "step 1"; sleep 0.4; echo "step 2" ) > s.log &
pid=$!
first=$(head -1 s.log)
wait $pid
lines=$(wc -l < s.log)
echo "first peek: $first, lines at the end: $lines"
''',
    notes={1: 'Like tmux new -d.', 3: 'Like capture-pane.', 4: 'The work ends by itself.', 5: 'Full history.'},
)

WORKED_INTRO = 'Three tmux habits from real jobs, as commands you can paste into a terminal.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='One session per server habit',
         problem='<p>Print the command an admin types to always land in the same session after login.</p>',
         inp='nothing', approach=['tmux new -A -s main.'],
         code='''echo 'ssh -t web01 "tmux new -A -s main"'
echo '# -A: attach if main exists, otherwise create it'
''', notes={1: '-t gives ssh a terminal.'}, tryit='Add it as an alias in ~/.bashrc.'),
    dict(level='i', tag='DBA', title='Start a restore safely',
         problem='<p>Build the command line that starts a restore in a detached, logged tmux session.</p>',
         inp='a dump file name', approach=['tmux new -d', 'pipe-pane log.'],
         code='''dump=sales_2026-11-11.sql.gz
s="restore-${dump%%.*}"
echo "tmux new -d -s $s"
echo "tmux pipe-pane -t $s -o 'cat >> ~/$s.log'"
echo "tmux send-keys -t $s 'zcat $dump | psql sales' Enter"
''', notes={2: 'Session name from the file name.'}, tryit='Add a has-session check so it does not start twice.'),
    dict(level='a', tag='SRE', title='Generate a pane layout for N servers',
         problem='<p>Print tmux commands that open one pane per server and synchronise typing.</p>',
         inp='server list', approach=['split-window per host', 'synchronize-panes.'],
         code='''hosts=(web01 web02 db01)
echo "tmux new -d -s fleet 'ssh ${hosts[0]}'"
for h in "${hosts[@]:1}"; do echo "tmux split-window -t fleet 'ssh $h'"; done
echo "tmux select-layout -t fleet tiled"
echo "tmux set -w -t fleet synchronize-panes on"
''', notes={3: 'One pane per remaining host.'}, tryit='Add a fourth host.'),
]

QUIZ = mix([
    dict(q='Detach from tmux:', options=['Ctrl+d', 'Ctrl+b d', 'exit', 'Ctrl+c'], answer=1, why='Ctrl+b d.'),
    dict(q='List sessions:', options=['tmux list', 'tmux ls', 'tmux ps', 'tmux show'], answer=1, why='tmux ls.'),
    dict(q='Attach to session work:', options=['tmux new work', 'tmux attach -t work', 'tmux open work', 'tmux -r work'], answer=1, why='attach -t.'),
    dict(q='Plain tmux (no arguments)…', options=['attaches to the last session', 'creates a new session', 'lists sessions', 'errors'], answer=1, why='New session.'),
    dict(q='Split left and right:', options=['Ctrl+b "', 'Ctrl+b %', 'Ctrl+b c', 'Ctrl+b s'], answer=1, why='%.'),
    dict(q='Why does tmux survive SSH drops?', options=['it ignores TERM', 'its server is not a child of the SSH shell', 'it uses nohup', 'SSH keeps it'], answer=1, why='Daemon.'),
    dict(q='screen’s prefix is…', options=['Ctrl+b', 'Ctrl+a', 'Alt', 'Esc'], answer=1, why='Ctrl+a.'),
    dict(q='Print what a pane shows from a script:', options=['tmux cat', 'tmux capture-pane -p', 'tmux log', 'tmux read'], answer=1, why='capture-pane.'),
])

REVISION = [
    'tmux server → sessions → windows → panes; your terminal is a client.',
    'tmux new -s NAME, Ctrl+b d, tmux ls, tmux a -t NAME, tmux new -A -s NAME, tmux kill-session -t NAME.',
    'Ctrl+b c new window, n/p/0-9 move, % and " split, arrows move, z zoom, x close, [ scroll, ? help.',
    'exit in the last pane ends the session; detaching does not.',
    'Scripting: new -d "cmd", send-keys … Enter, capture-pane -p, pipe-pane, has -t, display -p "#{…}".',
    'screen: screen -S, Ctrl+a d, screen -ls, screen -r. Survives logout, not reboot.',
]

FAQ = [
    ('What is tmux used for?', 'Running terminal sessions on a server that survive disconnection, with windows and split panes.'),
    ('How do I detach and reattach in tmux?', 'Ctrl+b then d to detach; tmux attach -t NAME (or tmux a) to reattach.'),
    ('How do I list tmux sessions?', 'tmux ls.'),
    ('What is the difference between tmux and screen?', 'Same idea; tmux is newer with panes, scripting and easier configuration; screen is older and often preinstalled.'),
    ('How do I scroll in tmux?', 'Ctrl+b [ for copy mode, then arrows/PgUp; q to exit. Or set -g mouse on.'),
    ('Does tmux survive a reboot?', 'No. Sessions live in memory; use systemd for services.'),
    ('tmux vs nohup?', 'nohup survives logout but you cannot interact; tmux lets you reattach and type.'),
]

PRACTICE_INTRO = 'Small tasks that build tmux commands. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Detach key', stmt='Print the key sequence to detach from tmux.', inp='nothing', code="echo 'Ctrl+b d'\n", explain='Prefix, then d.'),
    dict(level='easy', title='New session', stmt='Print the command to create a session named db.', inp='nothing', code="echo 'tmux new -s db'\n", explain='-s name.'),
    dict(level='easy', title='Attach', stmt='Print the command to attach to db.', inp='nothing', code="echo 'tmux attach -t db'\n", explain='-t target.'),
    dict(level='medium', title='Attach or create', stmt='Print one command that attaches to main or creates it.', inp='nothing', code="echo 'tmux new -A -s main'\n", explain='-A.'),
    dict(level='medium', title='Detached job', stmt='Print a command that starts ./sync.sh in a detached session sync.', inp='nothing', code="echo \"tmux new -d -s sync './sync.sh'\"\n", explain='-d plus command.'),
    dict(level='medium', title='screen', stmt='Print the screen command that lists sessions.', inp='nothing', code="echo 'screen -ls'\n", explain='-ls.'),
    dict(level='business', title='Target', stmt='Print the target for session ops, window 2, pane 1.', inp='numbers', code="s=ops w=2 p=1; echo \"$s:$w.$p\"\n", explain='session:window.pane.'),
    dict(level='business', title='Kill others', stmt='Print the command that kills every session except keep.', inp='nothing', code="echo 'tmux kill-session -a -t keep'\n", explain='-a.'),
]

SCN_INTRO = 'Interview questions about tmux and screen, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you keep a long command running after SSH disconnects?”', 'Very common.', 'two ways?',
        '''<ul>
          <li>tmux/screen: run inside, detach, reattach later.</li>
          <li>nohup cmd &gt; log 2&gt;&amp;1 &amp; when no interaction is needed.</li>
          <li>For permanent services: systemd.</li>
        </ul>''', 'keeping the laptop on.') +
    scn('Service company', 'Junior', '“My tmux session is gone”', 'tmux shows an empty shell.', 'what happened?',
        '''<ol>
          <li>tmux alone created a new session.</li>
          <li>tmux ls; tmux a -t &lt;old&gt;.</li>
          <li>If not listed: the server died (reboot, logind) or exit was typed.</li>
        </ol>''', 'assuming the work is lost.') +
    scn('DevOps', 'Mid-level', 'Run the same command on 6 servers live', 'Watch all outputs.', 'tmux?',
        '''<ul>
          <li>One pane per ssh, select-layout tiled.</li>
          <li>synchronize-panes on to type once.</li>
          <li>For automation prefer Ansible/pssh.</li>
        </ul>''', 'six terminal windows.') +
    scn('Platform', 'Senior', 'tmux sessions die at logout on new servers', 'Used to work.', 'why?',
        '''<ul>
          <li>systemd-logind KillUserProcesses=yes kills the user scope.</li>
          <li>loginctl enable-linger user or systemd-run --user --scope tmux.</li>
          <li>Check distro defaults.</li>
        </ul>''', 'reinstalling tmux.')
) + interview([
    ('Session vs window vs pane?', 'Desk, tab, part of a tab.'),
    ('How to rename a window?', 'Ctrl+b , (comma).'),
    ('How to scroll back?', 'Ctrl+b [ (copy mode).'),
    ('Where is the socket?', '/tmp/tmux-UID/default.'),
    ('Can two people share a session?', 'Yes, both attach (same user, or a shared socket with -S).'),
    ('How to send keys from a script?', 'tmux send-keys -t s "cmd" Enter.'),
    ('Does tmux survive reboot?', 'No.'),
], [
    ('RHCSA / LFCS', 'Not required, but expected in practice for remote work.'),
    ('DevOps / SRE interviews', 'tmux, nohup, systemd choices.'),
    ('CompTIA Linux+', 'screen and tmux basics.'),
]) + distro('tmux and screen are packages on every distribution.', [
    ('tmux', 'apt install tmux (often preinstalled)', 'dnf install tmux', 'brew install tmux', 'WSL'),
    ('screen', 'apt install screen', 'dnf install screen (RHEL 8+: EPEL)', 'preinstalled (old)', '-'),
    ('byobu', 'preinstalled on Ubuntu Server', 'EPEL', 'brew', '-'),
    ('Default prefix', 'Ctrl+b', 'Ctrl+b', 'Ctrl+b', '-'),
    ('Windows', '-', '-', '-', 'Windows Terminal panes (no detach)'),
]) + teaser('12.1', 'Module 11 is done: Riya can start, watch, signal, prioritise and protect processes. Module 12 opened the shell itself; if you have not read it yet, start with shell variables. Otherwise go on to Module 13: one-liners that combine commands.')

CHEATSHEET = cheatsheet('tmux', [
    ('Sessions', [('tmux new -s n', 'new'), ('Ctrl+b d', 'detach'), ('tmux ls', 'list'), ('tmux a -t n', 'attach'), ('tmux kill-ses -t n', 'kill')]),
    ('Windows', [('Ctrl+b c', 'new'), ('Ctrl+b n / p', 'next / prev'), ('Ctrl+b 0-9', 'jump'), ('Ctrl+b ,', 'rename'), ('Ctrl+b w', 'choose')]),
    ('Panes', [('Ctrl+b %', 'left|right'), ('Ctrl+b "', 'top/bottom'), ('Ctrl+b arrows', 'move'), ('Ctrl+b z', 'zoom'), ('Ctrl+b x', 'close')]),
    ('Scripting / screen', [('send-keys … Enter', 'type'), ('capture-pane -p', 'read'), ('new -d "cmd"', 'detached'), ('screen -S / -r / -ls', 'screen'), ('Ctrl+a d', 'screen detach')]),
])

MINDMAP = mindmap('tmux', [
    ('Idea', 'blue', ['server', 'client', 'survives SSH']),
    ('Sessions', 'green', ['new -s', 'ls / a -t', 'kill-session']),
    ('Windows', 'amber', ['Ctrl+b c', 'n p 0-9', 'rename']),
    ('Panes', 'violet', ['% "', 'arrows z', 'x']),
    ('Scripting', 'acc', ['send-keys', 'capture-pane', 'has -t']),
    ('Others', 'red', ['screen', 'nohup', 'systemd']),
])

LAB = lab('a session for a job', 'Build the lab, do the four tasks with tmux commands in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab116 && cd ~/lab116 && rm -f *.txt
tmux kill-session -t lab116 2>/dev/null; tmux kill-session -t lab116-old 2>/dev/null
tmux new -d -s lab116-old 'sleep 600'; true''',
    tasks=['Create a detached session named <code>lab116</code> whose first window is named <code>work</code>.',
           'Add a second window named <code>logs</code> to it, and split the <code>logs</code> window into two panes.',
           'Use send-keys to run <code>echo hello-from-tmux &gt; ~/lab116/out.txt</code> in the <code>work</code> window.',
           'Kill the session <code>lab116-old</code> without touching <code>lab116</code>.'],
    solution='''tmux new -d -s lab116 -n work
tmux new-window -t lab116 -n logs
tmux split-window -t lab116:logs
tmux send-keys -t lab116:work 'echo hello-from-tmux > ~/lab116/out.txt' Enter
tmux kill-session -t lab116-old''',
    check='''cd ~/lab116; sleep 0.8
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 session" 'tmux has -t lab116 2>/dev/null && [ "$(tmux list-windows -t lab116 -F "#{window_index}:#{window_name}" | head -1)" = "0:work" ]'
ok "2 logs"    '[ "$(tmux list-panes -t lab116:logs 2>/dev/null | wc -l)" = 2 ]'
ok "3 keys"    '[ "$(cat out.txt 2>/dev/null)" = hello-from-tmux ]'
ok "4 old"     '! tmux has -t lab116-old 2>/dev/null && tmux has -t lab116 2>/dev/null' ''')
