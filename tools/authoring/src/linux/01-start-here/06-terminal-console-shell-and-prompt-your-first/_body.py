import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 1. story
sc = (term(20, 16, 300, 120, ['$ ls -l /etc', ('total 812 ...', 'dim'), '$ ping google.com', ('64 bytes from ...', 'dim'), ('64 bytes from ...', 'dim'), ('64 bytes from ...', 'dim')], title='riya@laptop: ~')
      + t(340, 40, 'Riya’s questions:', 9, 'acc', anchor='start', bold=True)
      + ''.join(t(340, 60 + k * 16, s, 8.6, 'ink2', anchor='start') for k, s in enumerate(['• Terminal, shell, console: same thing?', '• What does riya@laptop:~$ mean?', '• What are -l and /etc?', '• ping never stops. Close the window?', '• Do I retype long commands every time?'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The command that would not stop</h2>
  <div class="story">
''' + puzzle('When Riya presses <kbd>Ctrl</kbd>+<kbd>C</kbd>, the letter “C” is never typed into ping. So what does ping actually receive, who sends it, and why does ping still get time to print a summary before it stops?') + '''
    <p class="narration">Ubuntu is installed. Riya opens the terminal and tries a few commands from a tutorial. <code>ls -l /etc</code> prints a wall of text. Then <code>ping google.com</code> starts printing a line every second and does not stop. She is about to close the whole window when Kabir stops her.</p>
''' + scene('A terminal where ls -l and a never-ending ping are running, next to Riya’s list of questions about terminal, shell, prompt and options.', sc,
            'Before more commands: learn the <tspan font-weight="700" class="s-acc">tools you type them into</tspan>.') + '''
K> Don’t close it! Press <kbd>Ctrl</kbd>+<kbd>C</kbd>. That stops the running command and gives your prompt back.
R> It worked! But I’m confused. People say terminal, console, shell, command line, prompt… are these all the same?
A> They are different parts that work together, and once you see which is which, everything gets easier. The <b>terminal</b> is the window, the <b>shell</b> is the program inside it, the <b>prompt</b> is the shell saying “I’m ready”, and a <b>console</b> is the machine’s own text screen.
K> And the keyboard shortcuts. Tab and the up arrow save me hours every week.
A> Today: the anatomy of every command (command, options, arguments), how to read the prompt, your first fifteen commands, how to get help without Google, and the shortcuts professionals use without thinking.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
lv = levels4('The terminal and the shell at four depths', [
    ('v', 'No jargon: ordering at a chai stall', '''      <p>Using a terminal is like ordering at a busy chai stall.</p>''' + '''<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A chai stall: the counter window is the terminal, the chaiwala is the shell, his Haan, bolo? is the prompt, and the order ek chai, kam cheeni, table 4 maps to command, option and argument, like ls -l /etc.">''' + label_box(20, 16, 180, 56, ['Counter window', '= the terminal'], 'blue', 9.4) + label_box(230, 16, 180, 56, ['Chaiwala', '= the shell'], 'acc', 9.4) + label_box(440, 16, 180, 56, ['“Haan, bolo?”', '= the prompt ($)'], 'green', 9.4) + t(320, 98, 'Your order:', 9.4, 'ink2', bold=True) + label_box(60, 108, 150, 40, ['“ek chai”', 'what you want'], 'card', 9) + label_box(245, 108, 150, 40, ['“kam cheeni”', 'how you want it'], 'card', 9) + label_box(430, 108, 150, 40, ['“table 4 pe”', 'for which one'], 'card', 9) + label_box(60, 158, 150, 34, ['command: ls'], 'acc', 9) + label_box(245, 158, 150, 34, ['option: -l'], 'blue', 9) + label_box(430, 158, 150, 34, ['argument: /etc'], 'green', 9) + '''<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>''' + '''
      <ul>
        <li>The <b>terminal</b> is the counter window: you speak through it, but it does not make chai.</li>
        <li>The <b>shell</b> is the chaiwala who understands your order and gets it done.</li>
        <li>The <b>prompt</b> is him saying “Haan, bolo?”: your turn to order.</li>
        <li>A <b>command line</b> is your order: what you want (<code>ls</code>), how (<code>-l</code>, an option) and for which thing (<code>/etc</code>, an argument). Press <kbd>Enter</kbd> to place it.</li>
        <li><kbd>Ctrl</kbd>+<kbd>C</kbd> is shouting “cancel!” when an order takes too long.</li>
      </ul>'''),
    ('b', 'A phone call', '''      <ul>
        <li>The <b>terminal</b> is the phone handset: you speak into it and hear the reply. It does not understand anything itself.</li>
        <li>The <b>shell</b> is the person on the other end who listens, understands your request and gets it done.</li>
        <li>The <b>prompt</b> (<code>riya@laptop:~$</code>) is that person saying “Yes, go ahead”. You type only after it appears.</li>
        <li>A <b>command</b> is your request: <code>date</code> means “what is the date?”. Press <kbd>Enter</kbd> to send it.</li>
      </ul>'''),
    ('i', 'Reading any command line', '''      <ul>
        <li>Shape of a command: <code>command [options] [arguments]</code>. In <code>ls -l /etc</code>: <code>ls</code> = command, <code>-l</code> = option (long listing), <code>/etc</code> = argument (which folder).</li>
        <li>Short options start with one dash and can be combined: <code>ls -l -a</code> = <code>ls -la</code>. Long options use two dashes: <code>ls --all</code>.</li>
        <li>Spaces separate words. A name with a space needs quotes: <code>cat "my notes.txt"</code>.</li>
        <li>Prompt: <code>user@host:folder$</code>. <code>~</code> = your home folder. <code>$</code> = normal user; <code>#</code> = root (administrator): be careful.</li>
        <li>Help: <code>command --help</code> (short), <code>man command</code> (full manual, <kbd>q</kbd> to quit).</li>
      </ul>'''),
    ('a', 'What really connects your keys to the shell', '''      <ul>
        <li>A <b>terminal emulator</b> (GNOME Terminal, Windows Terminal, iTerm2) talks to the shell through a <b>pseudo-terminal</b> (pty) device such as <code>/dev/pts/0</code>; <code>tty</code> prints yours. A <b>virtual console</b> (<code>/dev/tty1</code>…) is the kernel’s own text screen.</li>
        <li>The pty’s line discipline handles special keys: <kbd>Ctrl</kbd>+<kbd>C</kbd> sends the <b>SIGINT</b> signal to the foreground program, <kbd>Ctrl</kbd>+<kbd>Z</kbd> sends SIGTSTP (pause), <kbd>Ctrl</kbd>+<kbd>D</kbd> means end of input.</li>
        <li>bash uses the <b>readline</b> library for editing (arrows, <kbd>Ctrl</kbd>+<kbd>A</kbd>/<kbd>E</kbd>, <kbd>Ctrl</kbd>+<kbd>R</kbd> history search) and builds the prompt from the <code>PS1</code> variable (<code>\\u@\\h:\\w\\$</code>).</li>
        <li>The program receives the words as an array, <code>argv</code>; each program decides what its own options mean, which is why options differ between commands.</li>
      </ul>'''),
])

definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Terminal, console, shell and prompt</h2>
''' + def_block(
    'A <b>terminal</b> (terminal emulator) is a program that provides a text window for entering commands and displaying output, connected to a shell through a pseudo-terminal device. A <b>console</b> is the system’s directly attached text terminal (physical or virtual). The <b>shell</b> is the command-line interpreter that reads commands, interprets them and runs programs. The <b>prompt</b> is the text the shell prints to show it is ready for the next command. A <b>command line</b> has the form <i>command [options] [arguments]</i>.',
    'The terminal is the window. The shell is the program inside it that understands you. The prompt is the shell saying “your turn”. You type a command, maybe with options (how) and arguments (on what), and press Enter.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Terminal', f'The window you type in. {gl("terminal-terminal-emulator", "Glossary →")}'),
    ('Console', f'The machine’s own text screen (tty1–tty6). {gl("console-virtual-console", "Glossary →")}'),
    ('Shell', f'The program that understands commands: bash. {gl("shell", "Glossary →")}'),
    ('Prompt', f'<code>riya@laptop:~$</code>; built from PS1. {gl("prompt", "Glossary →")}'),
    ('Command / option / argument', f'What to do / how / on what. {gl("command-option-and-argument", "Glossary →")}'),
    ('Tab completion', f'Press Tab to finish names. {gl("tab-completion", "Glossary →")}'),
    ('History', f'Commands you typed before; Up arrow, Ctrl+R. {gl("history", "Glossary →")}'),
    ('man page', f'The built-in manual for each command. {gl("man-page-and-sections", "Glossary →")}'),
    ('Ctrl+C', f'Stop the running command (sends SIGINT). {gl("sigint-and-sighup", "Glossary →")}'),
    ('Exit status', f'0 = success, other = failure; shown by <code>echo $?</code>. {gl("exit-status", "Glossary →")}'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Prompt symbols', '<code>$</code> normal user · <code>#</code> root'),
    ('Ubuntu’s default prompt (PS1)', '<code>\\u@\\h:\\w\\$</code> = user@host:folder$'),
    ('Stop a running command', '<kbd>Ctrl</kbd>+<kbd>C</kbd>'),
    ('Clear the screen', '<code>clear</code> or <kbd>Ctrl</kbd>+<kbd>L</kbd>'),
    ('Log out / close the shell', '<code>exit</code> or <kbd>Ctrl</kbd>+<kbd>D</kbd> on an empty line'),
    ('Command not found', 'Exit status 127: typo, or the program is not installed'),
]) + '\n' + names('Terminal words are full of history from teleprinters and early Unix.', [
    ('tty', 'teletypewriter', 'The first terminals were electric typewriters.'),
    ('pts', 'pseudo-terminal slave', 'The fake terminal device behind each window: /dev/pts/0.'),
    ('PS1', 'prompt string 1', 'The variable bash turns into your prompt.'),
    ('man', 'manual', 'The built-in manual pages.'),
    ('ping', 'sonar “ping”', 'Named after the sound of a submarine’s sonar pulse.'),
    ('^C', 'Ctrl+C', 'Shown by the terminal when you press it; means “interrupt”.'),
    ('~', 'tilde = home', 'A short way to write /home/&lt;you&gt;.'),
    ('cd', 'change directory', 'Move to another folder.'),
]) + '\n' + lv + didyou('<kbd>Ctrl</kbd>+<kbd>C</kbd> is a real character: byte number 3 (in old teleprinter codes, “end of text”). The terminal sends that byte, and the kernel’s terminal layer, seeing it, sends the <b>SIGINT</b> signal to the running program instead of passing the byte on.') + '''
EXAM> “Differentiate terminal and shell; explain the structure of a Linux command with an example” → terminal = interface window, shell = interpreter (bash, zsh); structure <i>command [options] [arguments]</i> with <code>ls -l /etc</code> labelled; mention prompt symbols $ and #.
''' + qc('In <code>ls -la /tmp</code>, which part is the option and which the argument?', '<code>-la</code> is the option (two short options joined: long format and all files); <code>/tmp</code> is the argument.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Your first fifteen commands</h2>
''' + table(['Command', 'What it does', 'Try'], [
    ['<code>echo</code>', 'Print text', '<code>echo "Hello"</code>'],
    ['<code>date</code>', 'Show date and time; format with <code>+</code>', '<code>date +%d-%m-%Y</code>'],
    ['<code>cal</code>', 'Show a calendar (install package <code>ncal</code> if missing)', '<code>cal 11 2026</code>'],
    ['<code>whoami</code>', 'Your user name', '<code>whoami</code>'],
    ['<code>hostname</code>', 'This computer’s name', '<code>hostname</code>'],
    ['<code>pwd</code>', 'Current folder', '<code>pwd</code>'],
    ['<code>ls</code>', 'List files (<code>-l</code> long, <code>-a</code> hidden)', '<code>ls -la</code>'],
    ['<code>cd</code>', 'Change folder', '<code>cd /tmp</code>, <code>cd ~</code>'],
    ['<code>uptime</code>', 'How long the system has run, and load', '<code>uptime</code>'],
    ['<code>clear</code>', 'Clear the screen', '<code>clear</code>'],
    ['<code>history</code>', 'Commands you typed before', '<code>history | tail</code>'],
    ['<code>man</code>', 'The manual', '<code>man ls</code> (q to quit)'],
    ['<code>--help</code>', 'Quick help built into most commands', '<code>ls --help</code>'],
    ['<code>type</code>', 'Builtin, alias or program?', '<code>type cd</code>'],
    ['<code>exit</code>', 'Close the shell (or an SSH session)', '<code>exit</code>'],
], minw=560) + '''

  <h3>Keyboard shortcuts professionals use without thinking</h3>
''' + table(['Keys', 'Action'], [
    ['<kbd>Tab</kbd>', 'Complete a command or file name; press twice to list choices'],
    ['<kbd>↑</kbd> / <kbd>↓</kbd>', 'Previous / next command from history'],
    ['<kbd>Ctrl</kbd>+<kbd>C</kbd>', 'Stop the running command (or discard the line you are typing)'],
    ['<kbd>Ctrl</kbd>+<kbd>L</kbd>', 'Clear the screen'],
    ['<kbd>Ctrl</kbd>+<kbd>A</kbd> / <kbd>Ctrl</kbd>+<kbd>E</kbd>', 'Jump to start / end of the line'],
    ['<kbd>Ctrl</kbd>+<kbd>R</kbd>', 'Search your history: type part of an old command'],
    ['<kbd>Ctrl</kbd>+<kbd>D</kbd>', 'End of input; on an empty line it logs you out'],
    ['<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>C</kbd> / <kbd>V</kbd>', 'Copy / paste in most Linux terminals (plain Ctrl+C means “stop”!)'],
], minw=480, cls='compare') + '''
  <h3>Kinds of terminals</h3>
''' + cards([
    ('Terminal emulator', 'A window app: GNOME Terminal, Konsole, Windows Terminal, macOS Terminal, iTerm2.', 'everyday'),
    ('Virtual console', 'The kernel’s full-screen text login: Ctrl+Alt+F3 on many desktops. Useful when the GUI is frozen.', 'rescue'),
    ('SSH session', 'A terminal on a remote machine, through an encrypted connection. Same commands.', 'servers'),
    ('Web terminal', 'A terminal inside a browser: cloud consoles, this website’s runner.', 'anywhere'),
]) + '''
''' + qc('You want to copy text from a Linux terminal and press Ctrl+C. What happens instead?', 'Ctrl+C means “interrupt”: it stops the running command. To copy, use Ctrl+Shift+C (and Ctrl+Shift+V to paste).') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Reading and running one command line</h2>
  <p>Take <code>ls -l --human-readable /etc</code> apart, then run it the professional way.</p>
''' + stepper([
    ('1. Wait for the prompt', '<p><code>riya@laptop:~$</code>: user riya, computer laptop, folder ~ (home), $ = normal user.</p>', 'Behind the screen: bash printed this from its PS1 variable and is now reading your keystrokes with readline.'),
    ('2. Type the command name', '<p><code>ls</code>, then press <kbd>Tab</kbd> twice to see every command starting with “ls”.</p>', 'Behind the screen: Tab completion searches the folders in PATH (and bash builtins) for matching names.'),
    ('3. Add options', '<p><code>-l</code> (long format) and <code>--human-readable</code> (sizes like 4.0K). Short options can be joined: <code>-lh</code>.</p>', 'Behind the screen: options are just words starting with a dash; ls reads them from its argument list.'),
    ('4. Add the argument', '<p><code>/etc</code>, the folder to list. Type <code>/e</code> and press <kbd>Tab</kbd>: it completes to <code>/etc/</code>.</p>', 'Behind the screen: Tab completion for file names reads the folder contents, so it never makes a typo.'),
    ('5. Press Enter and read', '<p>The output appears; if it is long, re-run with <code>| less</code> to scroll (q to quit).</p>', 'Behind the screen: the shell splits the line into words, finds /usr/bin/ls, starts it with those words, and waits.'),
    ('6. Check success, reuse, get help', '<p><code>echo $?</code> → 0 means success. Press <kbd>↑</kbd> to bring the command back and edit it. Unsure of an option? <code>ls --help</code> or <code>man ls</code>.</p>', 'Behind the screen: every program returns an exit status; bash keeps the last one in <code>$?</code> and keeps typed lines in history.'),
]) + '''
''' + qc('What does <code>echo $?</code> print right after a successful command?', '0. Any other number means the command failed; 127 means “command not found”.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
see = [term(20, 18, 320, 130, ['$ '], cursor=True) + t(180, 172, 'The prompt: the shell is waiting.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ls -l /e'], cursor=True) + t(180, 172, 'Riya types and presses Tab after /e.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ls -l /etc/'], cursor=True) + t(180, 172, 'Tab completes it to /etc/.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ls -l /etc/', ('total 812', 'out'), ('drwxr-xr-x 3 root root 4096 ... apt', 'out'), ('-rw-r--r-- 1 root root  2319 ... bash.bashrc', 'out')]) + t(180, 172, 'Enter: the listing appears.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ping google.com', ('64 bytes from ...: time=21 ms', 'out'), ('64 bytes from ...: time=20 ms', 'out'), ('^C', 'acc')]) + t(180, 172, 'A never-ending ping, stopped with Ctrl+C.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ping google.com', ('^C', 'acc'), ('--- google.com ping statistics ---', 'out'), ('3 packets transmitted, 3 received', 'out'), '$ '], cursor=True) + t(180, 172, 'ping prints a summary and the prompt returns.', 9, 'green', bold=True)]
def pipe(hl, words=None, extra=''):
    o = label_box(10, 14, 100, 34, ['Keyboard'], 'card' if 0 not in hl else 'blue', 8.8)
    o += label_box(130, 14, 100, 34, ['Terminal', '+ pty /dev/pts/0'], 'card' if 1 not in hl else 'blue', 8.4)
    o += label_box(250, 14, 100, 34, ['bash', '(readline)'], 'card' if 2 not in hl else 'acc', 8.4)
    o += arrow(110, 31, 128, 31, 'ink3', 1.4) + arrow(230, 31, 248, 31, 'ink3', 1.4)
    if words:
        o += ''.join(label_box(14 + k * 84, 70, 78, 26, [w], tone, 8.4) for k, (w, tone) in enumerate(words))
    return o + extra
behind = [pipe([2], extra=t(180, 130, 'bash printed PS1 and waits for a line.', 8.8, 'ink2')),
          pipe([0, 1, 2], extra=t(180, 130, 'Keys → terminal → pty → bash. Tab is handled by readline.', 8.8, 'ink2')),
          pipe([2], extra=t(180, 120, 'readline lists /, finds the only name starting with “e”…', 8.6, 'ink2') + t(180, 136, '“etc”, and inserts it. No guessing, no typos.', 8.6, 'green', bold=True)),
          pipe([2], [('argv[0]: ls', 'acc'), ('argv[1]: -l', 'blue'), ('argv[2]: /etc/', 'green')], t(180, 130, 'bash splits the line into words and starts /usr/bin/ls with them.', 8.6, 'ink2')),
          pipe([0, 1], extra=t(180, 120, 'Ctrl+C is not text: the pty turns it into', 8.6, 'ink2') + t(180, 136, 'the signal SIGINT for the running program.', 8.6, 'red', bold=True)),
          pipe([2], extra=t(180, 120, 'ping catches SIGINT, prints its statistics and exits.', 8.6, 'ink2') + t(180, 136, 'bash sees it ended and prints the prompt.', 8.6, 'green', bold=True))]
two = anim_two('Tab, Enter, Ctrl+C', 'From key press to program', 'A terminal where Riya uses Tab completion, runs ls -l /etc and stops ping with Ctrl+C.',
               'The path from keyboard to terminal to pseudo-terminal to bash, the argv words handed to ls, and Ctrl+C becoming a SIGINT signal.', see, behind,
               ['The prompt is visible, so the shell is ready.',
                'Riya types <code>ls -l /e</code> and presses <kbd>Tab</kbd>.',
                'The shell completes the folder name to <code>/etc/</code>.',
                'She presses Enter; ls prints the long listing (shortened here).',
                'She runs <code>ping</code>, which never stops by itself, and presses <kbd>Ctrl</kbd>+<kbd>C</kbd> (shown as <code>^C</code>).',
                'ping prints a summary and exits; the prompt returns. (Output shortened; times are examples.)'],
               ['bash shows the prompt from its <code>PS1</code> variable and waits.',
                'Each key travels from the keyboard to the terminal app, then through the pseudo-terminal to bash, where the readline library edits the line.',
                'On Tab, readline reads the folder <code>/</code>, sees only one name starting with “e” and inserts it.',
                'On Enter, bash splits the line into words, an array called argv, finds <code>/usr/bin/ls</code> and runs it with those words.',
                '<kbd>Ctrl</kbd>+<kbd>C</kbd> is not sent as a letter. The pseudo-terminal converts it into the SIGINT signal for the program in the foreground.',
                'ping handles SIGINT by printing statistics and exiting. bash, which was waiting, takes over again. Lesson 11.3 covers signals in depth.'])

# scenario 1: tab completion vs typos
ta = term(14, 16, 332, 110, ['$ cd Documnets', ('bash: cd: Documnets: No such file or directory', 'err')], title='riya@laptop: ~') + cap('Typing long names by hand: one typo, one error.', '', 'red', y=150, h=34)
tb = term(14, 16, 332, 110, ['$ cd Do'], cursor=True, title='riya@laptop: ~') + cap('Type only the first letters…', '', 'card', y=150, h=34)
tc = term(14, 16, 332, 110, ['$ cd Do', ('Documents/  Downloads/', 'acc'), '$ cd Doc'], title='riya@laptop: ~') + cap('Two matches? Tab twice lists them. Add one letter.', '', 'blue', y=150, h=34)
td = term(14, 16, 332, 110, ['$ cd Documents/', '$ pwd', ('/home/riya/Documents', 'out')], title='riya@laptop: ~/Documents') + cap('Tab completes the rest, exactly as spelled on disk.', '', 'green', y=150, h=34)
te = (t(180, 30, 'Tab everywhere', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Command names: sys + Tab → systemctl', '• File and folder names, even long log names', '• Many options, e.g. git che + Tab → checkout', '• If Tab does nothing, the name does not exist: a free check!'])) + cap('Faster and no typos.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Tab completion: never type a long name again',
              'Riya keeps mistyping folder names. Kabir shows her the habit every Linux professional has.',
              'Completing names with Tab', 'A typo gives No such file or directory; Tab completion lists Documents and Downloads and completes the right name.', [ta, tb, tc, td, te],
              ['A typo (“Documnets”) and bash cannot find the folder.',
               'Instead she types just <code>Do</code>…',
               '…and presses <kbd>Tab</kbd> twice: two names start with “Do”, so bash lists both. She adds a <code>c</code>.',
               'One more <kbd>Tab</kbd> completes <code>Documents/</code> exactly as it is spelled on disk.',
               'Tab works for commands, files and many options. When Tab completes nothing, that itself tells you the name does not exist.'],
              hid='scenario-tab')

# scenario 2: history
ha = term(14, 16, 332, 110, ['$ grep -i "error" /var/log/app/payments-2026-11-05.log | tail -20'], title='riya@app-01') + cap('A long command Riya ran yesterday.', '', 'card', y=150, h=34)
hb = term(14, 16, 332, 110, ['$ ', ('(reverse-i-search)`paym\': grep -i "error" /var/log/', 'acc')], title='riya@app-01') + cap('Today: Ctrl+R and type “paym”.', 'bash finds the latest matching command.', 'blue', y=150, h=44)
hc = term(14, 16, 332, 110, ['$ grep -i "error" /var/log/app/payments-2026-11-06.log | tail -20'], title='riya@app-01') + cap('Right arrow to edit: change 05 to 06, press Enter.', '', 'blue', y=150, h=34)
hd = term(14, 16, 332, 110, ['$ history | tail -3', ('  501  cd /var/log/app', 'out'), ('  502  grep -i "error" ...-05.log | tail -20', 'out'), ('  503  grep -i "error" ...-06.log | tail -20', 'out'), '$ !502'], title='riya@app-01', size=7.6) + cap('history numbers every command; !502 re-runs one.', '', 'green', y=150, h=34)
he = (t(180, 30, 'History habits', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• ↑ for the last few commands, Ctrl+R for older ones.', '• !! repeats the last command (sudo !! is popular).', '• History lives in ~/.bash_history (saved on exit).', '• Never type passwords as part of a command: they get saved.'])) + cap('Your history is your notebook.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Yesterday’s long command, back in two seconds',
              'On the server, Riya needs the same long log search she ran yesterday, for today’s file. History numbers and file names are examples.',
              'Searching and reusing history', 'Ctrl+R finds a previous grep command, the date is edited, and history shows numbered commands that can be re-run with !number.', [ha, hb, hc, hd, he],
              ['Yesterday Riya ran a long grep on the payments log.',
               'Today she presses <kbd>Ctrl</kbd>+<kbd>R</kbd> and types a few letters; bash shows the most recent matching command.',
               'She presses the right arrow to edit it, changes the date in the file name and presses Enter.',
               '<code>history</code> lists commands with numbers; <code>!502</code> would run number 502 again.',
               'History is saved to <code>~/.bash_history</code>. Because it is saved, never put passwords directly in a command line.'],
              hid='scenario-history')

# scenario 3: prompt on production
pa = term(14, 16, 332, 100, ['riya@laptop:~/test$ rm -r old-logs'], title='laptop') + cap('On her laptop, deleting a test folder is harmless.', '', 'card', y=140, h=34)
pb = term(14, 16, 332, 100, [('root@pay-prod-01:/var/lib# ', 'err')], title='ssh: pay-prod-01') + cap('Same habits, but look at the prompt:', 'root, a production host, a system folder.', 'red', y=134, h=44)
pc_ = term(14, 16, 332, 100, [('root@pay-prod-01:/var/lib# ', 'err'), ('# stop. whoami? hostname? pwd?', 'acc')], title='ssh: pay-prod-01') + cap('Pause and read: user (#), host, folder.', '', 'amber', y=140, h=34)
pd = term(14, 16, 332, 100, [('[PROD] riya@pay-prod-01:~$ ', 'err'), ('# team prompt: red PROD tag, no root login', 'dim')], title='ssh: pay-prod-01') + cap('Many teams colour production prompts red,', 'and use sudo instead of logging in as root.', 'green', y=134, h=44)
pe = (t(180, 30, 'The prompt is a safety device', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• $ = normal user, # = root: slow down on #.', '• Check host and folder before rm, mv or restarts.', '• Prefer sudo for single commands over root shells.', '• Customising PS1 is covered in Lesson 12.2.'])) + cap('Read the prompt before every risky command.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Read the prompt before you press Enter',
              'Many production incidents start with a command typed into the wrong window. The prompt tells you exactly where you are, if you read it. Host names are examples.',
              'The prompt as a safety check', 'A harmless command on a laptop, then a root prompt on a production server, and a team prompt with a red PROD tag.', [pa, pb, pc_, pd, pe],
              ['On her laptop, <code>rm -r old-logs</code> in a test folder is harmless.',
               'In another window she is logged in to a production payment server as <b>root</b> (<code>#</code>), inside <code>/var/lib</code>, where databases keep their files.',
               'The habit: before any delete, move or restart, read the prompt (user, host, folder) or run <code>whoami; hostname; pwd</code>.',
               'Many teams make production prompts unmistakable, for example a red <code>[PROD]</code> tag, and avoid root shells by using sudo.',
               'A two-second look at the prompt prevents some of the most expensive mistakes in operations.'],
              hid='scenario-prompt')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Tab, Enter and Ctrl+C: what each key really does</h2>
  <p>Left: Riya’s terminal (outputs shortened). Right: the path from the keyboard to bash and the program.</p>
''' + two + '''
  <p>Three real-time scenarios: Tab completion, reusing history, and reading the prompt on a production server.</p>
''' + s1 + s2 + s3 + '''
''' + dissect('Layer by layer: dissect <kbd>Ctrl</kbd>+<kbd>C</kbd>',
    'What really happens between pressing two keys and a running program stopping? Open each layer. The commands show each step for real (a timer plays your hand on the keyboard).', [
    dict(key='you', name='You', sub='Ctrl + C',
         why='Some commands never finish by themselves (ping, tail -f) or hang. You need a way to say “stop”.',
         how='Hold Ctrl and press C.',
         impl='Your keyboard sends the key codes for Ctrl and C.',
         used='Many times a day: stopping logs, pings, stuck commands.'),
    dict(key='term', name='Terminal', sub='sends byte 3',
         why='Ctrl+C is not a letter. The terminal turns the key combination into a special control character.',
         how='It sends the byte 0x03 to the shell side, just as it sends letters.',
         impl='The terminal app (GNOME Terminal, Windows Terminal, iTerm2).',
         used='All terminal apps follow this old convention, which is why Ctrl+C means “stop” everywhere.',
         cmd="printf '\\x03' | od -An -tx1"),
    dict(key='tty', name='Terminal layer in the kernel', sub='turns byte 3 into a signal',
         why='The byte must reach the <i>running program</i> as an order, not as text.',
         how='The pseudo-terminal’s line discipline is set to treat byte 3 as the INTR character. Instead of delivering it as input, it asks the kernel to send signal <b>SIGINT</b> (number 2) to the program in the foreground.',
         impl='Inside the kernel (the tty layer); settings visible with <code>stty -a</code> (“intr = ^C”).',
         used='Also turns Ctrl+Z into SIGTSTP (pause) and Ctrl+\\ into SIGQUIT.',
         cmd='kill -l 2'),
    dict(key='prog', name='The program', sub='handles SIGINT',
         why='A program may need to tidy up before stopping: save data, delete temp files, print a summary.',
         how='If the program set a handler (ping does), it runs: ping prints its statistics, then exits. Otherwise the default action ends the program at once.',
         impl='In the program’s own code (ping from iputils). Shell scripts set handlers with <code>trap</code> (Lesson 11.3).',
         used='Databases and servers use the same idea to shut down cleanly.'),
    dict(key='shell', name='Shell (bash)', sub='takes back control',
         why='After the program ends, you need your prompt back, and to know how it ended.',
         how='bash was waiting for the program; it collects the exit status (128 + 2 = 130 for a program killed by SIGINT) and prints the prompt.',
         impl='bash’s job control; the status is in <code>$?</code>.',
         used='Scripts check <code>$?</code> to see whether a step was interrupted.',
         cmd='timeout --preserve-status -s INT 1 sleep 30; echo "sleep was stopped by SIGINT: exit status $?"', expect='any'),
]) + qc('Who turns the Ctrl+C key press into the SIGINT signal: the terminal app, bash, or the kernel?', 'The kernel’s terminal (tty) layer. The terminal app sends byte 3; the kernel converts it into SIGINT for the foreground program.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The terminal in a working day</h2>
''' + usecase(term(8, 14, 104, 62, [('$ ssh app-01', 'prompt'), ('$ tail -f app.log', 'prompt')], title='ops', size=6.4, step=12),
              '1. Watching a live log during a release',
              'During a deployment engineers keep a terminal with <code>tail -f</code> on the app’s log and stop it with Ctrl+C when the release looks healthy.',
              ['Release', '*tail -f + Ctrl+C', 'Go / no-go']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ history | grep', 'prompt'), ('  docker run ...', 'out')], title='dev', size=6.4, step=12),
    '2. Re-running yesterday’s commands',
    'Developers search their history for the long docker, kubectl or git commands they used before, instead of searching the internet again.',
    ['Need old command', '*Ctrl+R / history', 'Run again']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ man rsync', 'prompt'), ('/--delete', 'acc')], title='admin', size=6.4, step=12),
    '3. Checking an option before a risky command',
    'Admins open <code>man</code> and search inside it (<code>/</code>) to confirm what an option does before running it on a server.',
    ['Unsure option', '*man / --help', 'Safe command']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['[PROD]', 'red prompt'], 'red', 8.6), '4. Making production obvious',
    'Teams configure prompts and terminal colours per environment, so nobody confuses a production server with a test one.',
    ['SSH to server', '*PS1 with host + colour', 'Fewer mistakes']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Ctrl+Alt+F3', 'text console'], 'card', 8.6), '5. Rescuing a frozen desktop',
    'When a Linux desktop freezes, switching to a virtual console lets you log in and stop the misbehaving program without rebooting.',
    ['Frozen GUI', '*virtual console', 'Fixed']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small command lines built only from this lesson’s commands. Each was really run; dates are fixed so outputs match.', [
    dict(level='b', title='A neatly formatted date', scenario='A report heading needs today’s date in words.',
         cmd='date -d 2026-11-05 +"%A, %d %B %Y"',
         explain='<code>+</code> starts a format: <code>%A</code> weekday, <code>%d</code> day, <code>%B</code> month name, <code>%Y</code> year. Drop <code>-d 2026-11-05</code> to use today.'),
    dict(level='b', title='Who, where and on which machine', scenario='Before running anything risky, confirm user, host and folder in one line.',
         cmd='echo "$(whoami)@$(hostname):$(pwd)"',
         explain='This rebuilds the information your prompt shows, using three commands. Handy inside scripts, where there is no prompt.'),
    dict(level='i', title='Is this a builtin or a program, and where?', scenario='You want to know every place a command name can come from.',
         cmd='type -a echo',
         explain='<code>type -a</code> lists all matches: the bash builtin (used first) and two program files. <code>/bin</code> is a link to <code>/usr/bin</code> on modern Ubuntu.'),
    dict(level='a', title='Read only the option you need from --help', scenario='You remember ls can sort by time but not the letter.',
         cmd="ls --help | grep -- ' -t'",
         explain='<code>--help</code> output is text, so grep can search it. The <code>--</code> tells grep “no more options”, so <code>\' -t\'</code> is searched for rather than read as an option.'),
], extra=build_up('find the right option without the internet', 'Kabir wants ls to sort by file size but does not remember the option, and the server has no browser. Narrow down the built-in help step by step.',
    'mkdir -p logs && head -c 300 /dev/zero > logs/small.log && head -c 9000 /dev/zero > logs/big.log && head -c 3000 /dev/zero > logs/mid.log', [
    ('ls --help | wc -l', 'The help text is long: count its lines.'),
    ('ls --help | grep -i size', 'Search it for the word “size” (any case).'),
    ("ls --help | grep -- ' -S'", 'Found a candidate: <code>-S</code>. Show just that line (<code>--</code> stops grep reading the pattern as an option).'),
    ('ls -lS logs', 'Use it: biggest first.'),
], level='i')) + which('Situations at the prompt and the right move.', [
    ('A command runs forever (ping, tail -f)', 'Ctrl+C', 'Sends SIGINT; most programs exit cleanly.', 'Closing the window, which can leave work half done on servers.'),
    ('Copy text in a Linux terminal', 'Ctrl+Shift+C', 'Plain Ctrl+C means stop.', 'Pressing Ctrl+C to copy and killing a running job.'),
    ('Finish a long file name', 'Tab', 'Completes exactly what exists.', 'Typing it by hand and making a typo.'),
    ('Run the previous command again', '↑ then Enter (or !!)', 'History recalls it.', 'Retyping and changing something by accident.'),
    ('Find an old command', 'Ctrl+R', 'Searches history as you type.', 'Pressing ↑ fifty times.'),
    ('Learn what an option does', 'man ls / ls --help', 'Built-in, matches your installed version.', 'Trusting a random blog post for a dangerous option.'),
    ('Check success of the last command', 'echo $?', '0 = success.', 'Assuming no message means success.'),
    ('Leave an SSH session or shell', 'exit', 'Ends the shell cleanly.', 'Closing the laptop and leaving sessions hanging.'),
]) + '''
''' + puzzle_answer('ping receives a <b>signal</b>, SIGINT, not a letter. The terminal sends byte 3 when you press Ctrl+C; the kernel’s terminal layer turns that byte into SIGINT for the program in the foreground. ping has a <b>handler</b> for SIGINT, so instead of dying immediately it prints its statistics and then exits. A program without a handler stops at once; SIGKILL (kill -9) cannot be handled at all (Lesson 11.3).') + qc('Read this prompt: <code>root@pay-prod-01:/var/lib#</code>. Name the three things it tells you.', 'User <b>root</b> (also shown by <code>#</code>), host <b>pay-prod-01</b> (looks like a production payment server), folder <code>/var/lib</code>. Slow down before any delete or restart.') + '''
</section>
'''

cmap = concept_map(
    [('1.2', 'Kernel and shell', 'who runs commands'), ('1.5', 'Linux installed', 'or the browser runner')],
    ['terminal vs console vs shell vs prompt', 'command, options, arguments', 'first 15 commands', 'help: man, --help', 'Tab, history, Ctrl+C'],
    [('2.1', 'The Linux folder tree', 'where everything lives'), ('2.5', 'Getting help', 'man, info, apropos'), ('11.3', 'Signals', 'what Ctrl+C really sends'), ('12.3', 'Aliases and history', 'work even faster')],
    'Every later lesson assumes you are comfortable at the prompt. Practise the shortcuts until you use them without thinking.')
body = cmap + (story.replace('  <div class="story">', before('Linux installed (<a href="../05-installing-linux-wsl-on-windows-virtualbox-dual/">Lesson 1.5</a>), or just use the browser runner below.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
