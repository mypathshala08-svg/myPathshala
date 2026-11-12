import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

TM = "env -u TMUX tmux -L inner -f /dev/null"
W = '""'
CLEAN = "tmux kill-server 2>/dev/null; tmux -L inner kill-server 2>/dev/null; pkill -u riya -x sleep; rm -rf ~/tm; mkdir -p ~/tm; cd ~/tm"
LOOP = "\"PS1='riya@web01:~$ '; clear; for i in \\$(seq 1000); do echo backup step \\$i; sleep 1; done\" Enter"

def live(title, intro, steps, h=12, hid=None):
    """Record a real terminal running tmux. steps: [(keys shown or None for a hidden pause, tmux keys, note)]."""
    keys = ["\"PS1='riya@web01:~$ '; alias tmux='" + TM + "'; cd ~; clear\" Enter"] + [s[1] for s in steps]
    for attempt in range(4):
        shots = tmux_screens(CLEAN + "; export PS1='$ '", 'bash --norc', keys, 64, h)
        if len(shots) > 2 and shots[1].strip().startswith('riya@web01') and not any('alias tmux' in x or 'bash-5' in x for x in shots[1:]):
            break
    else:
        raise SystemExit('live(): recording failed')
    shots = shots[2:]
    items = []
    for (show, _, note), shot in zip(steps, shots):
        if show is None:
            continue
        items.append(f'<li class="fv"><p class="fv__sit"><b>{"Press" if show.startswith(("Ctrl", "y", "q")) else "Type"}</b> <kbd>{E(show)}</kbd> {note}</p><div class="code scr" data-lang="text" data-file="terminal"><pre><code>{E(shot)}</code></pre></div></li>')
    return f'''  <h3{f' id="{hid}"' if hid else ''}>{title}</h3>
  <p>{intro} <span class="muted">Real screens: recorded in a terminal on Ubuntu 24.04 (tmux 3.4, default settings), captured after each key.</span></p>
  <ol class="fvs">{''.join(items)}</ol>
'''

HOOK = hook('Riya is restoring a 200 GB database over SSH from a café. The Wi-Fi drops after 20 minutes. With <code>nohup</code> (Lesson 11.4) the restore would survive, but she could not see its progress or answer its “Continue? [y/N]” question. A <b>terminal multiplexer</b> solves this: <b>tmux</b> (or the older <b>screen</b>) runs your shells inside a <b>session</b> on the server. You can <b>detach</b> from it, lose the connection, log in again from another computer and <b>attach</b> to find everything exactly as you left it, still running. tmux also gives you several windows and split panes in one terminal. This lesson shows real tmux screens step by step.',
    ['explain sessions, windows and panes, and why tmux sessions survive a dropped connection',
     'create, detach, list, attach and kill sessions (tmux new -s, Ctrl+b d, tmux ls, tmux attach -t)',
     'work with windows and split panes, and use the most important Ctrl+b keys',
     'script tmux (send-keys, capture-pane), know the screen equivalents, and pick tmux vs nohup vs systemd'])
ROAD = roadmap([
    ('story', 'The story', 3, 'Wi-Fi drops, work goes on'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What tmux is', 6, 'simple meaning + 4 depths'),
    ('types', 'Sessions, windows, panes', 5, 'keys and screen'),
    ('commands', 'By field', 15, 'real tmux screens'),
    ('animation', 'See it happen', 4, 'detach and attach'),
    ('run', 'Run on your PC', 4, 'tmux needs a real terminal'),
    ('lab', 'Practice lab', 7, 'a session for a job'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Start long interactive work over SSH', 'tmux new -s work', 'new session'),
    ('Step away, keep it running', 'Ctrl+b d', 'detach'),
    ('Come back (any computer)', 'tmux attach -t work', 'attach'),
    ('Which sessions exist?', 'tmux ls', 'list'),
    ('A second shell in the same session', 'Ctrl+b c   ·   Ctrl+b % / "', 'window / pane'),
    ('Finished', 'exit (in every shell)   ·   tmux kill-session -t work', 'end'),
    ('No interaction needed', 'nohup cmd > log 2>&1 &', 'Lesson 11.4'),
    ('Must always run, restart on failure', 'systemd service', 'Lesson 17.3'),
])

cmap = concept_map(
    [('11.4', 'Jobs and nohup', 'SIGHUP on logout'), ('11.3', 'Signals', 'HUP, TERM'), ('16.6', 'SSH', 'remote logins')],
    ['server, session, window, pane', 'new, detach, ls, attach, kill', 'prefix Ctrl+b and its keys', 'copy mode and scrolling', 'scripting: send-keys, capture-pane', 'screen equivalents'],
    [('16.6', 'SSH', 'ssh -t host tmux attach'), ('17.3', 'systemd', 'real services'), ('21.1', 'Capstone', 'long installs in tmux'), ('20.4', 'DevOps', 'pair work in one session')],
    'tmux is a terminal that lives on the server. Your SSH connection is only a window onto it; closing the window does not close the terminal.')

sc = (term(20, 14, 316, 156, ['$ tmux new -s restore', ('(restore runs… 41%)', 'out'), '   Ctrl+b d', ('[detached (from session restore)]', 'acc'), '$ exit   # Wi-Fi drops', '$ tmux attach -t restore', ('(restore runs… 77%)', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=17)
      + t(352, 36, 'tmux session:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['lives on the server', 'detach: Ctrl+b d', 'SSH may drop', 'attach: back again', 'still running'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Wi-Fi drops, work goes on</h2>
  <div class="story">
''' + puzzle('Riya starts <code>tmux</code>, runs her restore, and closes the laptop. Next morning she types <code>tmux</code> again and sees an empty new shell: “my restore is gone!” <code>tmux ls</code> shows two sessions, <code>0</code> and <code>1</code>. Later, inside tmux, she types <code>tmux new -s logs</code> and gets “sessions should be nested with care, unset $TMUX to force”. And when she types <code>exit</code> in her tmux shell, the session disappears for good. What went wrong in each case?') + '''
    <p class="narration">Riya detaches from a running restore, loses the connection, and attaches again.</p>
''' + scene('A terminal: tmux new starts a session with a restore running; Ctrl+b d detaches; after reconnecting, tmux attach shows the restore further along.', sc,
            'The connection is <tspan font-weight="700" class="s-acc">only a window</tspan>; the work lives in the session.') + '''
K> How can it survive if my SSH session died?
A> The tmux <b>server</b> is a separate process on the machine, not a child of your SSH shell. It owns the session and its shells. Your terminal is just a <b>client</b> attached to it. When the connection drops, only the client goes away.
R> And the puzzle?
A> <code>tmux</code> alone always creates a <b>new</b> session; you need <code>tmux attach</code>. Today: sessions, windows, panes, keys and scripting, on real screens.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A TV studio (tmux server) keeps recording the show (your shells) even when viewers (SSH clients) switch off their TVs. Viewers can tune in again later from any TV.">'
       + label_box(220, 20, 200, 120, ['STUDIO (tmux server)', 'session “restore”', 'window 0: restore', 'window 1: logs'], 'blue', 9)
       + label_box(20, 40, 160, 80, ['laptop TV', '(SSH client)', 'switched off ✗'], 'red', 9)
       + label_box(460, 40, 160, 80, ['office TV', '(new SSH)', 'tunes in again ✓'], 'green', 9)
       + arrow(180, 80, 220, 80) + arrow(420, 80, 460, 80)
       + t(320, 168, 'Switching off a TV does not stop the show.', 10, 'acc', bold=True)
       + t(320, 190, 'detach = switch off; attach = tune in again.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('tmux at four depths', [
    ('v', 'No jargon: a TV studio', '      <p>The show keeps running whether you watch or not.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>tmux new -s work</code>: start a named session.</li>
        <li><kbd>Ctrl+b</kbd> then <kbd>d</kbd>: detach (leave it running).</li>
        <li><code>tmux ls</code>: list sessions.</li>
        <li><code>tmux attach -t work</code> (or <code>tmux a</code>): go back in.</li>
      </ul>'''),
    ('i', 'Windows, panes and the prefix', '''      <ul>
        <li>Every tmux key starts with the <b>prefix</b> <kbd>Ctrl+b</kbd>, released, then one key.</li>
        <li>A session has <b>windows</b> (like tabs: <kbd>c</kbd> new, <kbd>n</kbd>/<kbd>p</kbd> next/previous, <kbd>0</kbd>–<kbd>9</kbd>), and a window can be split into <b>panes</b> (<kbd>%</kbd> side by side, <kbd>"</kbd> one above the other, arrows to move, <kbd>x</kbd> close).</li>
        <li><kbd>[</kbd> enters copy mode to scroll back (q to leave); <kbd>?</kbd> lists all keys.</li>
        <li><code>exit</code> in the last shell ends the session; detaching does not.</li>
        <li>Settings go in <code>~/.tmux.conf</code> (mouse on, prefix Ctrl+a, history size).</li>
      </ul>'''),
    ('a', 'Behind the screen: server, clients and sockets', '''      <ul>
        <li>The first tmux command starts a <b>server</b> process that daemonises (it is not in your SSH session, so it gets no SIGHUP).</li>
        <li>Clients talk to it through a Unix socket in <code>/tmp/tmux-UID/default</code> (<code>-L name</code> chooses another socket, <code>-S path</code> a full path).</li>
        <li>Each pane is a <b>pseudo-terminal</b> (/dev/pts/N) owned by the server; the shell inside thinks it has a real terminal.</li>
        <li>Inside tmux, <code>$TMUX</code> is set (socket,pid,session); tmux refuses to nest unless you unset it.</li>
        <li>If systemd-logind kills user processes at logout (KillUserProcesses=yes), the server dies too; then run it with <code>systemd-run --user --scope tmux</code> or enable lingering.</li>
        <li>Rebooting the machine ends all sessions; plugins (tmux-resurrect) can save layouts but not running programs.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Terminal multiplexers: tmux and screen</h2>
''' + def_block(
    'A <b>terminal multiplexer</b> runs several terminal sessions inside one terminal and keeps them on the server independent of your connection. <b>tmux</b> organises them into <b>sessions</b>, <b>windows</b> and <b>panes</b>; you can <b>detach</b> from a session and <b>attach</b> to it later, even from another computer, while its programs keep running. <b>GNU screen</b> is the older tool with the same idea.',
    'A terminal that lives on the server; your connection is only a view onto it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Server', 'The tmux process that owns everything.'),
    ('Client', 'Your terminal attached to the server.'),
    ('Session', 'A named set of windows (work, restore).'),
    ('Window', 'A full screen, like a browser tab.'),
    ('Pane', 'A part of a split window.'),
    ('Prefix', 'Ctrl+b, pressed before every tmux key.'),
    ('Detach / attach', 'Leave / come back.'),
    ('Copy mode', 'Scroll back and copy text.'),
]) + '\n' + names('Where the names come from.', [
    ('tmux', 'terminal multiplexer', 'Nicholas Marriott, 2007.'),
    ('screen', 'GNU screen', 'Oliver Laumann, 1987.'),
    ('multiplexer', 'many signals on one line', 'Telephone engineering.'),
    ('pane', 'a window pane', 'Glass panel.'),
    ('prefix', 'before', 'Ctrl+b in tmux, Ctrl+a in screen.'),
    ('detach', 'un-attach', 'Leave running.'),
    ('pts', 'pseudo-terminal slave', '/dev/pts/N.'),
    ('byobu', 'Japanese folding screen', 'Ubuntu’s wrapper around tmux.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('New', '<code>tmux new -s NAME</code>'),
    ('Detach', '<kbd>Ctrl+b</kbd> <kbd>d</kbd>'),
    ('List', '<code>tmux ls</code>'),
    ('Attach', '<code>tmux a -t NAME</code>'),
    ('Kill', '<code>tmux kill-session -t NAME</code>'),
    ('Install', '<code>sudo apt install tmux</code>'),
]) + '\n' + lv + didyou('Ubuntu Server ships with <code>tmux</code> and <code>screen</code>-style <b>byobu</b> preinstalled on many cloud images, precisely because so much admin work happens over SSH connections that can drop.') + '''
EXAM> “How do you keep a process running after closing SSH, and still interact with it?” → Run it in tmux or screen, detach (Ctrl+b d), and reattach later with tmux attach.
''' + qc('You typed <code>exit</code> in the only shell of a tmux session. What happened to the session?', 'It ended: a session lives as long as it has at least one shell (pane). Detach with Ctrl+b d instead.') + mistake('tmux   (to get back to yesterday’s session)',
    'tmux ls   then   tmux attach -t NAME   (or tmux a for the last one)',
    'tmux with no command always creates a new session; that is why her restore seemed gone (it was session 0, she was in 1).') + mistake('closing the laptop with work in a plain SSH shell',
    'start long work inside tmux; detach before leaving',
    'Without tmux the SSH shell gets SIGHUP and its jobs die (Lesson 11.4).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Sessions, windows, panes, and the keys</h2>
''' + table(['Level', 'Like', 'Create', 'Move', 'Close'], [
    ['Session', 'a desk', '<code>tmux new -s n</code>', '<code>tmux a -t n</code>; <kbd>Ctrl+b s</kbd>', '<code>tmux kill-session -t n</code>'],
    ['Window', 'a tab', '<kbd>Ctrl+b c</kbd>', '<kbd>Ctrl+b n</kbd> / <kbd>p</kbd> / <kbd>0</kbd>–<kbd>9</kbd> / <kbd>w</kbd>', '<code>exit</code>; <kbd>Ctrl+b &amp;</kbd>'],
    ['Pane', 'part of a tab', '<kbd>Ctrl+b %</kbd> (left|right), <kbd>"</kbd> (top/bottom)', '<kbd>Ctrl+b</kbd> arrows, <kbd>o</kbd>', '<code>exit</code>; <kbd>Ctrl+b x</kbd>'],
], minw=560) + table(['Ctrl+b then', 'Does'], [
    ['<kbd>d</kbd>', 'detach'],
    ['<kbd>c</kbd>', 'new window'],
    ['<kbd>,</kbd>', 'rename window'],
    ['<kbd>$</kbd>', 'rename session'],
    ['<kbd>w</kbd> / <kbd>s</kbd>', 'choose window / session from a list'],
    ['<kbd>%</kbd> / <kbd>"</kbd>', 'split left-right / top-bottom'],
    ['<kbd>z</kbd>', 'zoom a pane to full size and back'],
    ['<kbd>[</kbd>', 'copy mode: scroll with arrows/PgUp, q to quit'],
    ['<kbd>?</kbd>', 'list all key bindings'],
    ['<kbd>:</kbd>', 'tmux command prompt'],
], minw=360) + table(['Task', 'tmux', 'GNU screen'], [
    ['New named session', '<code>tmux new -s work</code>', '<code>screen -S work</code>'],
    ['Detach', '<kbd>Ctrl+b d</kbd>', '<kbd>Ctrl+a d</kbd>'],
    ['List', '<code>tmux ls</code>', '<code>screen -ls</code>'],
    ['Attach', '<code>tmux a -t work</code>', '<code>screen -r work</code>'],
    ['New window', '<kbd>Ctrl+b c</kbd>', '<kbd>Ctrl+a c</kbd>'],
    ['Split', '<kbd>Ctrl+b %</kbd> <kbd>"</kbd>', '<kbd>Ctrl+a |</kbd> <kbd>S</kbd>'],
    ['Scroll back', '<kbd>Ctrl+b [</kbd>', '<kbd>Ctrl+a [</kbd> or <kbd>Esc</kbd>'],
    ['Detached start', '<code>tmux new -d -s j "cmd"</code>', '<code>screen -dmS j cmd</code>'],
], minw=480) + table(['', 'nohup / setsid', 'tmux / screen', 'systemd service'], [
    ['Survives logout', 'yes', 'yes', 'yes'],
    ['Watch and type into it later', 'no (log only)', '<b>yes</b>', 'logs only'],
    ['Survives reboot', 'no', 'no', 'yes (enabled)'],
    ['Restarts on failure', 'no', 'no', 'yes'],
    ['Best for', 'fire-and-forget commands', 'interactive admin work', 'permanent services'],
], minw=480) + qc('Which key splits a window into left and right panes?', 'Ctrl+b %.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Sessions, windows, panes and scripting, then used in every field</h2>
  <p id="commands">The screens below are real: tmux 3.4 with default settings running in a terminal on our Ubuntu 24.04 build machine as riya, captured after each key. The bottom line is tmux’s status bar: session name, windows (* = current), host name and clock.</p>
''' + live('Detach and attach: the core of tmux', 'Start a session, run a long job, detach, check from outside, and come back.', [
    ('tmux new -s work', "'tmux new -s work' Enter", 'A new session named work: a fresh shell with a green status bar.'),
    ('(a long job)', LOOP, 'A loop prints one backup step per second.'),
    (None, W, ''), (None, W, ''),
    ('Ctrl+b d', 'C-b d', 'Detach: back in the plain shell; the job keeps running inside tmux.'),
    ('tmux ls', "'tmux ls' Enter", 'The session is still there.'),
    (None, W, ''), (None, W, ''), (None, W, ''), (None, W, ''),
    ('tmux attach -t work', "'tmux attach -t work' Enter", 'Back in: the counter has moved on while we were away.'),
], hid='live-detach') + cmdcard_u(['long installs, restores, migrations over SSH', 'anything you want to come back to'],
               ['permanent services (use systemd)', 'nesting tmux inside tmux'])(
    'sess', 'tmux new -s · Ctrl+b d · tmux ls · tmux a -t · kill-session', 'sessions',
    '<code>tmux new -s NAME</code> creates a session; <code>-d</code> creates it detached, optionally with a command. <code>tmux ls</code> lists sessions, <code>tmux a -t NAME</code> attaches (<code>tmux a</code> = the most recent), <code>tmux kill-session -t NAME</code> ends one, <code>tmux kill-server</code> ends all. <code>tmux has -t NAME</code> tests whether it exists (for scripts).',
    'tmux new -s NAME   ·   tmux a -t NAME   ·   tmux new -A -s NAME', 'change',
    [('tmux new -s n', 'create', 'start'),
     ('tmux new -d -s n "cmd"', 'create detached with a command', 'scripts'),
     ('tmux new -A -s n', 'attach if it exists, else create', 'one habit'),
     ('tmux ls', 'list', 'check'),
     ('tmux a -t n', 'attach', 'return'),
     ('tmux has -t n', 'exists?', 'scripts'),
     ('tmux kill-session -t n', 'end one', 'cleanup')],
    dict(setup=CLEAN, cmd="tmux new -d -s restore 'sleep 300'\ntmux new -d -s logs\ntmux ls | sed -E 's/\\(created .*\\)/(created …)/'\ntmux has -t restore && echo 'restore exists'\ntmux kill-session -t logs; tmux ls | cut -d: -f1\ntmux kill-server", note='Two detached sessions; one killed; has -t is a yes/no test.'),
    [('sys', [
        dict(situation='The puzzle: tmux alone makes a new session.', setup=CLEAN, cmd="tmux new -d 'sleep 300'\ntmux new -d 'sleep 300'\ntmux ls | cut -d: -f1 | tr '\\n' ' '; echo '<- unnamed sessions are numbered'\ntmux kill-server", why='Always name sessions (-s) and attach with -t; or use tmux new -A -s work.')]),
     ('dev', [
        dict(situation='Nesting is refused.', setup=CLEAN, cmd="tmux new -d -s outer\ntmux send-keys -t outer 'tmux new -s inner 2>&1 | head -1 > ~/tm/nest.txt' Enter; sleep 0.8\ncat ~/tm/nest.txt; tmux kill-server", why='Inside tmux, $TMUX is set; detach first, or use Ctrl+b s to switch sessions.')]),
    ],
    anat=anatomy([('tmux', 'cmd', 'the client'), ('new', 'opt', 'command: new-session'), ('-s work', 'arg', 'session name')], 'tmux COMMAND OPTIONS. Short forms: new, ls, a, kill-ses.')
) + live('Windows and panes', 'Inside a session: a new window, a split, closing a pane, and the window list.', [
    ('tmux new -s work', "'tmux new -s work' Enter", 'A session with window 0.'),
    ('Ctrl+b c', 'C-b c', 'Window 1 is created and becomes current (* in the status bar).'),
    ('Ctrl+b %', 'C-b %', 'Window 1 is split into two panes, left and right.'),
    ('Ctrl+b x  then  y', 'C-b x', 'tmux asks before killing the pane…'),
    ('y', 'y', '…and the window is whole again.'),
    ('Ctrl+b w', 'C-b w', 'The window chooser: arrows and Enter to pick, q to close.'),
], hid='live-panes') + cmdcard_u(['watching logs while you work', 'several servers or tasks in one view'],
               ['too many tiny panes on a small screen'])(
    'win', 'new-window · split-window -h/-v · select-pane · rename', 'windows and panes from the command line',
    'Every key has a command: <kbd>c</kbd> = <code>new-window</code>, <kbd>%</kbd> = <code>split-window -h</code>, <kbd>"</kbd> = <code>split-window -v</code>, <kbd>,</kbd> = <code>rename-window</code>. You can type them after <kbd>Ctrl+b :</kbd>, or run them from a shell with <code>-t session:window.pane</code> as the target.',
    'tmux new-window -t s -n logs   ·   tmux split-window -h -t s:0', 'change',
    [('new-window -n name', 'window', 'tabs'),
     ('split-window -h', 'left|right', 'side by side'),
     ('split-window -v', 'top/bottom', 'stacked'),
     ('select-layout tiled', 'even grid', 'many panes'),
     ('rename-window', 'name a window', 'clarity'),
     ('list-windows / list-panes', 'inspect', 'scripts'),
     ('-t s:1.0', 'target: session s, window 1, pane 0', 'addressing')],
    dict(setup=CLEAN, cmd="tmux new -d -s ops -n shell\ntmux new-window -t ops -n logs\ntmux split-window -h -t ops:logs\ntmux split-window -v -t ops:logs\ntmux list-windows -t ops -F '#{window_index}: #{window_name} (#{window_panes} panes)'\ntmux kill-server", note='-F prints only the fields you ask for: index, name, number of panes.'),
    [('sys', [
        dict(situation='A ready-made monitoring layout.', setup=CLEAN, cmd="tmux new -d -s mon -x 120 -y 30 'top'\ntmux split-window -h -t mon 'watch -n 2 df -h'\ntmux split-window -v -t mon 'tail -f /etc/hostname'\ntmux select-layout -t mon tiled > /dev/null\ntmux list-panes -t mon -F 'pane #{pane_index}: #{pane_current_command} #{pane_width}x#{pane_height}'\ntmux kill-server", why='One command builds a three-pane dashboard; attach to it with tmux a -t mon.')]),
    ]
) + cmdcard_u(['starting jobs remotely', 'checking output without attaching', 'automation and tests'],
               ['typing passwords with send-keys'])(
    'script', 'send-keys · capture-pane -p · new -d "cmd" · pipe-pane', 'scripting tmux',
    '<code>tmux send-keys -t s \'text\' Enter</code> types into a pane as if you pressed the keys. <code>tmux capture-pane -p -t s</code> prints what the pane shows. <code>pipe-pane -o \'cat &gt;&gt; file\'</code> logs everything a pane prints. Together they let scripts drive interactive programs and check them later.',
    "tmux send-keys -t s 'cmd' Enter   ·   tmux capture-pane -p -t s", 'change',
    [('send-keys \'text\' Enter', 'type into a pane', 'automation'),
     ('send-keys C-c', 'press Ctrl+C', 'stop it'),
     ('capture-pane -p', 'print the screen', 'check'),
     ('capture-pane -p -S -100', 'with 100 lines of history', 'logs'),
     ('pipe-pane -o "cat >> f"', 'log a pane to a file', 'audit'),
     ('display -p "#{…}"', 'print tmux variables', 'info')],
    dict(setup=CLEAN, cmd="tmux new -d -s job -x 60 -y 10\ntmux send-keys -t job 'cd ~/tm; for i in 1 2 3; do echo \"processing file $i\"; done' Enter; sleep 0.6\ntmux capture-pane -p -t job | grep -v '^$' | tail -3\ntmux send-keys -t job 'sleep 100' Enter; sleep 0.3; tmux send-keys -t job C-c; sleep 0.3\ntmux display -p -t job 'pane runs: #{pane_current_command}'\ntmux kill-server", note='A script typed commands into the session, read the screen, and pressed Ctrl+C.'),
    [('dev', [
        dict(situation='Log a pane to a file.', setup=CLEAN, cmd="tmux new -d -s rec\ntmux pipe-pane -t rec -o 'cat >> ~/tm/session.log'\ntmux send-keys -t rec 'echo deploy started; echo deploy finished' Enter; sleep 0.6\ngrep -c deploy ~/tm/session.log; tmux kill-server", why='Everything the pane printed is in session.log, useful for audits.')]),
    ]
) + undo('Detaching is harmless; killing a session ends its programs.', [
    ('Lost which session is which:', '<code>tmux ls</code>; rename with <kbd>Ctrl+b $</kbd>.'),
    ('Accidentally typed exit in the last pane:', 'the session is gone; start again (next time detach).'),
    ('Screen messed up after a resize:', '<kbd>Ctrl+b :</kbd> <code>refresh-client</code>, or detach and attach.'),
    ('Stuck in copy mode or a prompt:', 'press <kbd>q</kbd> or <kbd>Esc</kbd>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(setup=CLEAN, cmd='tmux attach -t nosuch', meaning='No session with that name.', fix='tmux ls.'),
    dict(setup=CLEAN, cmd='tmux ls', meaning='No server: no sessions at all.', fix='tmux new -s NAME.'),
    dict(setup=CLEAN + "; tmux new -d -s a", cmd='tmux new -d -s a', meaning='The name is taken.', fix='Another name, or tmux new -A -s a.'),
    dict(setup=CLEAN, cmd='tmux attach', meaning='Nothing to attach to.', fix='Create a session first.'),
]) + qc('How do you leave tmux without stopping what runs inside?', 'Detach: Ctrl+b then d.') + '''
'''
cards = cards + '</section>\n'

def arch(k):
    client = [('laptop (SSH client)', 'green'), ('laptop: connection lost', 'red'), ('—', 'card'), ('office PC (new SSH)', 'green')][k]
    o = label_box(200, 14, 160, 40, ['tmux server'], 'blue', 9)
    o += label_box(200, 70, 160, 60, ['session: restore', 'pane → bash → restore'], 'blue', 8.4)
    o += label_box(14, 150, 170, 34, [client[0]], client[1], 8.4)
    if k in (0, 3):
        o += arrow(184, 160, 230, 130)
    return o
see_cmds = [['$ tmux new -s restore', ('restore 41%…', 'out')], ['(Wi-Fi drops)', ('client gone', 'acc')], ['(nobody attached)', ('restore 63%…', 'out')], ['$ tmux a -t restore', ('restore 77%…', 'out')]]
see = [term(14, 16, 332, 116, c, title='terminal', prompt='$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Attached.', 'Connection lost.', 'Still running.', 'Attached again.'])]
behind = [arch(k) for k in range(4)]
two = anim_two('Detach and attach', 'Behind the screen: server and clients',
               'A terminal running a restore in tmux; the connection drops; later a new connection attaches and the restore is further along.',
               'A tmux server box with a session inside; client boxes connect and disconnect below it while the session keeps running.', see, behind,
               ['Attached.', 'Lost.', 'Running.', 'Back.'],
               ['attach', 'drop', 'alone', 'attach'])

def layout(k):
    o = ''
    if k == 0:
        o += label_box(20, 20, 320, 130, ['window 0: bash'], 'blue', 9)
    elif k == 1:
        o += label_box(20, 20, 320, 130, ['window 1: bash (new)'], 'green', 9)
    elif k == 2:
        o += label_box(20, 20, 156, 130, ['pane 0'], 'green', 9) + label_box(184, 20, 156, 130, ['pane 1'], 'amber', 9)
    else:
        o += label_box(20, 20, 156, 130, ['pane 0'], 'green', 9) + label_box(184, 20, 156, 61, ['pane 1'], 'amber', 9) + label_box(184, 89, 156, 61, ['pane 2'], 'violet', 9)
    o += t(180, 172, ['Ctrl+b c: new window', 'window 1 is current', 'Ctrl+b %: left | right', 'Ctrl+b ": top / bottom'][k], 9.4, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Windows and panes',
              'One session, a second window, then splits.',
              'Ctrl+b c · % · "', 'A window, then a new window, then split into two side-by-side panes, then the right pane split into top and bottom.', [layout(k) for k in range(4)],
              ['One window.', 'New window.', 'Split %.', 'Split ".'], hid='scenario-panes')

dx = dissect('Layer by layer: what tmux runs',
    'Each layer has a real command and output from our build machine.', [
    dict(key='srv', name='Server process', sub='daemon', why='Survives logout.', how='Forks on first use.', impl='Parent is init.', used='ps.',
         setup=CLEAN, cmd="tmux new -d -s s1; ps -o ppid=,comm= -p $(pgrep -o -u riya -f '^tmux new -d -s s1') | awk '{print \"tmux server parent PID:\", $1, \"(1 = init/systemd)\"}'; tmux kill-server"),
    dict(key='sock', name='Socket', sub='/tmp/tmux-UID', why='Clients find it.', how='Unix socket.', impl='-L / -S.', used='Sharing.',
         setup=CLEAN, cmd="tmux new -d -s s1; ls -l /tmp/tmux-$(id -u)/ | awk '$NF==\"default\"{print \"type\", substr($1,1,1), \"(s = socket):\", $NF}'; tmux kill-server"),
    dict(key='pty', name='Pseudo-terminals', sub='/dev/pts', why='Each pane is a terminal.', how='openpty().', impl='One per pane.', used='tty.',
         setup=CLEAN, cmd="tmux new -d -s s1 -x 80 -y 20; tmux split-window -t s1; tmux list-panes -t s1 -F 'pane #{pane_index} -> #{pane_tty}' | sed -E 's/[0-9]+$/N/'; tmux kill-server"),
    dict(key='env', name='$TMUX', sub='inside', why='Detect tmux.', how='Set by the server.', impl='socket,pid,session.', used='Prompts, scripts.',
         setup=CLEAN, cmd="tmux new -d -s s1; tmux send-keys -t s1 '[ -n \"$TMUX\" ] && echo inside-tmux > ~/tm/env.txt' Enter; sleep 0.6; cat ~/tm/env.txt; echo \"outside: TMUX='${TMUX}'\"; tmux kill-server"),
], hint='From the server to the variables. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Detach and attach, windows and panes</h2>
''' + two + s1 + dx + qc('Why does the tmux server survive when SSH drops?', 'It is a daemon whose parent is init, not a child of the SSH shell, so the hang-up never reaches it.') + '''
</section>
'''

VAR = variations('Fifteen more tmux experiments (all scripted, so they run without a keyboard). All were really run on our build machine.', [
    ('Sessions', [
        dict(title='Create only if missing (for scripts)', setup=CLEAN, cmd="for i in 1 2; do tmux has -t work 2>/dev/null || tmux new -d -s work; done; tmux ls | wc -l; tmux kill-server", why='Run twice, still one session. Interactively, tmux new -A -s work does the same and attaches.'),
        dict(title='Run a job in a detached session', setup=CLEAN, cmd="tmux new -d -s backup 'for i in 1 2 3; do echo step $i; sleep 0.2; done; sleep 30'; sleep 1; tmux capture-pane -p -t backup | grep step; tmux kill-server", why='The usual way to start long work remotely: ssh host tmux new -d -s backup "cmd".'),
        dict(title='Rename a session', setup=CLEAN, cmd="tmux new -d -s tmp; tmux rename-session -t tmp release-v2; tmux ls -F '#{session_name}'; tmux kill-server", why='Clear names help when you have many.'),
        dict(title='Ask tmux about a session', setup=CLEAN, cmd="tmux new -d -s s; tmux new-window -t s; tmux display -p -t s '#{session_name} has #{session_windows} windows, attached clients: #{session_attached}'; tmux kill-server", why='Format variables expose session details for scripts and status bars.'),
        dict(title='Is a session running? (for scripts)', setup=CLEAN, cmd="for s in backup web; do tmux has -t $s 2>/dev/null && echo \"$s: running\" || echo \"$s: not running\"; done", why='has-session returns 0 or 1.'),
    ]),
    ('Windows, panes and keys', [
        dict(title='Send a command to every pane', setup=CLEAN, cmd="tmux new -d -s m -x 100 -y 30; tmux split-window -t m; tmux split-window -t m; tmux set -w -t m synchronize-panes on; tmux send-keys -t m 'echo same in every pane > /dev/null' Enter; tmux list-panes -t m | wc -l; tmux kill-server", why='synchronize-panes types into all panes at once (handy for several servers).'),
        dict(title='List every key binding of the prefix table', setup=CLEAN, cmd="tmux new -d -s k; tmux list-keys -T prefix | wc -l; tmux list-keys -T prefix | awk '$4 ~ /^(d|c|%)$/ {print $4, \"->\", $5, $6}'; tmux kill-server", why='Ctrl+b ? shows the same list interactively.'),
        dict(title='Zoom a pane', setup=CLEAN, cmd="tmux new -d -s z -x 80 -y 20; tmux split-window -h -t z; tmux resize-pane -Z -t z; tmux display -p -t z 'zoomed: #{window_zoomed_flag}'; tmux kill-server", why='Ctrl+b z: one pane full-size, again to restore.'),
        dict(title='Name windows when you create them', setup=CLEAN, cmd="tmux new -d -s n -n editor; tmux new-window -t n -n build; tmux list-windows -t n -F '#{window_index}:#{window_name}'; tmux kill-server", why='-n names a window; Ctrl+b , renames it later.'),
        dict(title='Scrollback history size', setup=CLEAN, cmd="tmux new -d -s h; tmux show -g history-limit; tmux kill-server", why='2000 lines by default; raise it in ~/.tmux.conf.'),
    ]),
    ('Config and friends', [
        dict(title='A tiny ~/.tmux.conf', setup=CLEAN + "; printf 'set -g mouse on\\nset -g history-limit 50000\\nset -g base-index 1\\n' > ~/tm/my.conf", cmd="tmux -f ~/tm/my.conf new -d -s c; tmux show -g mouse; tmux show -g history-limit; tmux show -g base-index; tmux kill-server", why='Mouse scrolling, long history, windows numbered from 1.'),
        dict(title='Change the prefix to Ctrl+a (shown)', cmd="printf 'unbind C-b\\nset -g prefix C-a\\nbind C-a send-prefix\\n'", why='Many screen users prefer Ctrl+a.'),
        dict(title='Reload config without restarting', setup=CLEAN + "; printf 'set -g status-left \"[#S] \"\\n' > ~/tm/s.conf", cmd="tmux new -d -s r; tmux source-file ~/tm/s.conf; tmux show -g status-left; tmux kill-server", why='Ctrl+b : source-file ~/.tmux.conf.'),
        dict(title='tmux version and screen availability', cmd="tmux -V; command -v screen > /dev/null && screen --version | head -1 || echo 'screen: not installed here (sudo apt install screen)'", why='tmux 3.x on current distros; screen may need installing.'),
        dict(title='Over SSH in one go (shown)', cmd="echo 'ssh -t web01 tmux new -A -s main   # log in straight into your session'", why='-t gives ssh a terminal so tmux can draw.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>tmux at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['restore', 'DBA'], 'blue', 8.6), '1. Long database work',
              'DBAs run restores, migrations and index builds inside tmux; if the VPN drops, the work continues and they reattach.', ['Start in tmux', '*detach', 'reattach later']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['panes', 'on-call'], 'green', 8.6), '2. Incident response',
    'On-call engineers split one window: logs on the left, top on the right, a shell below.', ['Alert', '*split panes', 'see everything']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['shared', 'pairing'], 'amber', 8.6), '3. Pair work and teaching',
    'Two people attach to the same session and see the same screen, useful for mentoring and live debugging.', ['Session', '*two clients', 'same view']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-d', 'automation'], 'violet', 8.6), '4. Automation',
    'Scripts start interactive tools in detached sessions, send keys and capture output (test harnesses, lab recorders like this course).', ['Script', '*send-keys', 'capture-pane']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['byobu', 'cloud'], 'red', 8.6), '5. Cloud servers',
    'Cloud images ship tmux/byobu; many teams start every SSH session with tmux new -A -s main.', ['ssh', '*tmux new -A', 'never lose work']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='List sessions', scenario='Where is my work?', setup=CLEAN + "; tmux new -d -s work", cmd="tmux ls | cut -d: -f1; tmux kill-server", explain='tmux ls.'),
    dict(level='b', title='Start a job detached', scenario='Over SSH.', setup=CLEAN, cmd="tmux new -d -s dl 'sleep 60'; tmux has -t dl && echo 'dl running'; tmux kill-server", explain='new -d.'),
    dict(level='i', title='Peek without attaching', scenario='Quick check.', setup=CLEAN, cmd="tmux new -d -s p 'echo 42% done; sleep 30'; sleep 0.5; tmux capture-pane -p -t p | head -1; tmux kill-server", explain='capture-pane -p.'),
    dict(level='i', title='Stop a program inside', scenario='Ctrl+C from outside.', setup=CLEAN, cmd="tmux new -d -s q 'bash --norc'; tmux send-keys -t q 'sleep 100' Enter; sleep 0.3; tmux send-keys -t q C-c; sleep 0.3; tmux display -p -t q '#{pane_current_command}'; tmux kill-server", explain='send-keys C-c.'),
    dict(level='a', title='Kill every session but one', scenario='Cleanup.', setup=CLEAN + "; for s in a b keep; do tmux new -d -s $s; done", cmd="tmux kill-session -a -t keep; tmux ls | cut -d: -f1; tmux kill-server", explain='-a = all others.'),
], extra=build_up('a work session for a job', 'Riya builds a ready-to-use tmux workspace with one script.', CLEAN, [
    ("tmux new -d -s job -n run; tmux ls | cut -d: -f1", '1. A detached session with a named window.'),
    ("tmux new-window -t job -n logs; tmux list-windows -t job -F '#{window_name}' | tr '\\n' ' '", '2. A second window for logs.'),
    ("tmux send-keys -t job:run 'for i in 1 2 3; do echo run $i; done' Enter; sleep 0.6; tmux capture-pane -p -t job:run | grep -c '^run '", '3. Start the work in window run.'),
    ("tmux has -t job && echo 'attach with: tmux a -t job'; tmux kill-server", '4. Ready: attach when you want to watch.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Interactive work that must survive SSH drops', 'tmux / screen', 'Reattach.', 'A plain SSH shell.'),
    ('Fire-and-forget command', 'nohup … &', 'Simple.', 'tmux for one line you never watch.'),
    ('Permanent service', 'systemd', 'Restarts, boot.', 'A forgotten tmux session.'),
    ('Several views at once', 'tmux panes', 'One screen.', 'Five SSH windows.'),
    ('Old servers without tmux', 'screen', 'Often installed.', 'Giving up.'),
]) + keys('tmux keys (press Ctrl+b first).', [
    ('d', 'detach', 'leave running'),
    ('c / n / p', 'new / next / previous window', 'tabs'),
    ('% / "', 'split left-right / top-bottom', 'panes'),
    ('arrows / z', 'move / zoom pane', 'panes'),
    ('[ … q', 'scroll back', 'copy mode'),
    ('s / w / ?', 'sessions / windows / help', 'navigate'),
]) + scriptit('workspace.sh', 'Create (or reuse) a tmux workspace named after the argument with three windows: shell, logs (a tail of a log file) and monitor (split into two panes), then print a summary and how to attach.',
'''name=${1:-ops}
log=~/tm/app.log; mkdir -p ~/tm; echo "app started" > "$log"
if ! tmux has -t "$name" 2>/dev/null; then
  tmux new -d -s "$name" -n shell -x 120 -y 30
  tmux new-window -t "$name" -n logs "tail -f $log"
  tmux new-window -t "$name" -n monitor 'top'
  tmux split-window -v -t "$name:monitor" 'sleep 3600'
fi
tmux list-windows -t "$name" -F '#{window_index} #{window_name}: #{window_panes} pane(s)'
echo "attach with: tmux attach -t $name"
tmux kill-server   # cleanup for this demo''',
'<p>Run without a name, so it builds the ops workspace.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>tmux</code> with no arguments always creates a <b>new</b> session (numbered 0, 1, …); her restore was still running in session 0. Use <code>tmux ls</code> and <code>tmux attach -t 0</code>, or always <code>tmux new -A -s restore</code>. <b>2.</b> Inside tmux, $TMUX is set and tmux refuses to nest; detach first or switch with <kbd>Ctrl+b s</kbd>. <b>3.</b> <code>exit</code> ends the shell; when the last pane closes, the session closes. To leave it running, detach with <kbd>Ctrl+b d</kbd>.') + qc('Which command lists tmux sessions?', 'tmux ls.') + '''
</section>
'''

_sh.run_sh(CLEAN + '; rm -rf ~/tm', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-foreground-and-background-jobs-and-nohup/">Lesson 11.4</a> (jobs, SIGHUP and nohup).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
