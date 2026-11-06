import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 1. story
sc = (laptop(30, 30, 110, screen=term(36, 36, 98, 56, ['$ ssh riya@app-01', ('Permission denied?', 'err')], title='terminal', size=6.4, step=10))
      + t(85, 120, 'Riya’s laptop', 9, 'ink2')
      + '<rect x="190" y="26" width="200" height="74" rx="10" class="s-card2" style="stroke:var(--line)"/>'
      + t(204, 44, 'Message from Neha (team lead)', 8.6, 'acc', anchor='start', bold=True)
      + t(204, 62, '“Please SSH into app-01 and', 8.6, anchor='start')
      + t(204, 76, ' check today’s error log.”', 8.6, anchor='start')
      + t(204, 92, '10:05 AM · first day', 7.6, 'ink3', anchor='start')
      + arrow(146, 60, 186, 60, 'ink3', 1.8, dash=True)
      + server(440, 24, 50, 70, 'app-01 (Linux)', 'blue')
      + server(500, 24, 50, 70, 'db-01 (Linux)', 'green')
      + t(520, 120, 'No screen, no mouse.', 8.4, 'ink3') + t(520, 133, 'Only a command line.', 8.4, 'ink3'))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>First day, first server</h2>
  <div class="story">
''' + puzzle('Riya will type <code>tail app.log</code> on her own laptop after logging in to the server. Which computer actually reads the file from its disk, her laptop or the server? And what travels over the network: the whole log file, or something else?') + '''
    <p class="narration">Riya has just joined a fintech start-up in Navi Mumbai as an intern. At 10:05 her team lead sends a message: “Please SSH into app-01 and check today’s error log.” Riya opens her laptop and looks for app-01’s window. There isn’t one. The server is in a data centre; it has no screen and no mouse. It only understands typed commands.</p>
''' + scene('Riya’s laptop with a terminal, a message from her team lead asking her to check a log on a server, and two Linux servers with no screen.', sc,
            'Most servers have no screen. You talk to them by <tspan font-weight="700" class="s-acc">typing commands</tspan>.') + '''
R> Sir, I can use Windows, Excel, even a bit of Python. But this server has no desktop at all. Where do I click?
A> Nowhere. That is the first big idea of this course. Servers that run websites, UPI payments and databases are usually managed by typing commands into a <b>terminal</b>, and most of them run <b>Linux</b>.
K> I felt the same in my first week. I kept looking for the folder icon. Then I learnt about ten commands and suddenly the server felt like my own laptop.
R> But before commands I need to be sure of the basics. What exactly is a file? What is a server? Is it different from my laptop?
A> Very good instinct. In this lesson we fix the foundation: what a computer is made of, how files and folders are organised, what makes a computer a <b>server</b>, why we use a command line, and how to use this course. Twenty minutes now saves you weeks later.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
lv = levels4('A computer, its files and servers at four depths', [
    ('v', 'No jargon: a computer is a person at a desk', '''      <p>A computer is a machine that follows instructions. Picture a person working at a desk:</p>''' + '''<div class="scene"><svg viewBox="0 0 640 190" role="img" aria-label="A computer drawn as a person at a desk: the CPU is the brain doing the work, RAM is the desk holding today&#39;s work, the disk is a cupboard with labelled boxes (files) on shelves (folders).">''' + label_box(20, 20, 170, 70, ['CPU = the brain', 'does the work, very fast'], 'acc', 9.4) + label_box(235, 20, 170, 70, ['RAM = the desk', 'work in progress, wiped at power-off'], 'blue', 9.4) + label_box(450, 20, 170, 70, ['Disk = the cupboard', 'keeps things after power-off'], 'green', 9.4) + arrow(192, 55, 232, 55, 'ink3', 1.8) + arrow(407, 55, 447, 55, 'ink3', 1.8) + ''.join(f'<path d="M{x} {y}h22l6 6v22h-28z" class="s-card2" style="stroke:var(--line)"/>' for x, y in [(462, 104), (500, 104), (538, 104), (576, 104)]) + t(535, 152, 'labelled boxes = files', 8.8, 'ink2') + t(535, 167, 'shelves = folders', 8.8, 'ink2') + t(105, 118, 'one task at a time,', 8.8, 'ink2') + t(105, 132, 'billions per second', 8.8, 'ink2') + t(320, 118, 'more desk = more apps', 8.8, 'ink2') + t(320, 132, 'open at once', 8.8, 'ink2') + '''<text x="632" y="184" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>''' + '''
      <ul>
        <li>The <b>brain</b> (CPU) does the thinking and the work.</li>
        <li>The <b>desk</b> (RAM) holds whatever is being worked on right now. When the power goes, the desk is cleared.</li>
        <li>The <b>cupboard</b> (disk) keeps everything safely, even when the power is off. Each thing in it is in a labelled box: a <b>file</b>. Boxes sit on shelves: <b>folders</b>.</li>
        <li>A <b>server</b> is simply a computer whose whole job is to help other computers, all day and all night, like the kitchen behind a big restaurant serving thousands of orders.</li>
      </ul>'''),
    ('b', 'A kitchen', '''      <ul>
        <li>The <b>CPU</b> is the cook: it does the actual work, one small step at a time, very fast.</li>
        <li><b>RAM</b> (memory) is the kitchen counter: whatever the cook is working on right now sits here. It is fast but small, and it is wiped clean when the power goes.</li>
        <li>The <b>disk</b> (SSD/HDD) is the store room: big, slower, and things stay there after power-off. Your <b>files</b> live here.</li>
        <li>A <b>file</b> is a labelled container in the store room (<code>notes.txt</code>). A <b>folder</b> (Linux says <b>directory</b>) is a shelf that holds files and other shelves.</li>
        <li>The <b>operating system</b> is the kitchen manager: it decides which order the cook works on, where things are kept and who may open which box.</li>
      </ul>'''),
    ('i', 'Files, folders, paths, clients and servers', '''      <ul>
        <li>Folders form a <b>tree</b>. The full address of a file is its <b>path</b>: on Windows <code>C:\\Users\\Riya\\notes.txt</code>, on Linux <code>/home/riya/notes.txt</code>. Linux uses forward slashes <code>/</code> and has one tree that starts at <code>/</code>.</li>
        <li>Linux names are <b>case-sensitive</b>: <code>Notes.txt</code> and <code>notes.txt</code> are two different files. Spaces in names are allowed but make typing harder, so people use <code>daily_report.txt</code>.</li>
        <li>A file is just bytes. A <b>text file</b> holds readable characters (configs, logs, scripts, CSV). A <b>binary file</b> holds bytes meant for programs (images, videos, programs). On Linux the extension (<code>.txt</code>) is only a hint for humans.</li>
        <li>A <b>client</b> asks for something; a <b>server</b> provides it. Your UPI app is a client; the bank’s computers that move the money are servers. The same machine can be both.</li>
      </ul>'''),
    ('a', 'What a server really is, and why it runs Linux', '''      <ul>
        <li>“Server” describes a <b>role</b>, not special hardware: a computer that runs services continuously and answers requests over the network. Data-centre servers are built for it (redundant power, ECC memory, remote management) and usually run <b>headless</b> (no monitor).</li>
        <li>Most servers today are <b>virtual machines</b> or <b>containers</b> sharing big physical machines, rented from clouds such as AWS, Azure or Google Cloud.</li>
        <li>Admins reach them with <b>SSH</b>, an encrypted remote terminal (Lesson 15.6). One person can manage hundreds of servers because commands can be <b>scripted</b> and repeated exactly, which clicks cannot.</li>
        <li>Why Linux: free to run on thousands of machines, stable for years without reboots, every setting is a text file, and the whole cloud, container and big-data ecosystem (Docker, Kubernetes, Hadoop, Spark) is built on it.</li>
      </ul>'''),
])

definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Files, folders and servers: the words you must be sure of</h2>
''' + def_block(
    'A <b>server</b> is a computer, physical or virtual, that runs continuously to provide a <b>service</b> (a website, a database, payments, file storage) to other computers called <b>clients</b> over a network. Servers are usually managed remotely through a <b>command-line interface (CLI)</b>, a text interface in which the user types commands and the system replies with text. Data on any computer is stored as <b>files</b>, organised into <b>directories (folders)</b> that form a tree; the location of a file in that tree is its <b>path</b>.',
    'A server is a computer whose job is to serve other computers, all day and all night. Nobody sits in front of it; you talk to it by typing commands. Everything on it, including programs, settings and logs, is a file inside some folder, and every file has an address called its path.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('CPU', 'The processor. Runs instructions. Has several cores that can work at the same time.'),
    ('RAM (memory)', 'Fast working space for programs that are running. Emptied when the computer turns off.'),
    ('Disk (storage)', 'SSD or hard disk. Keeps files permanently, even after power-off.'),
    ('Operating system (OS)', f'The software that manages the hardware and runs programs: Windows, macOS, Linux. {gl("operating-system-os", "Glossary →")}'),
    ('File', 'A named piece of data on disk: <code>notes.txt</code>, <code>photo.jpg</code>, <code>app.log</code>.'),
    ('Directory (folder)', 'A container for files and other directories. Linux people say “directory”.'),
    ('Path', f'The address of a file in the folder tree: <code>/home/riya/notes.txt</code>. {gl("path-absolute-and-relative", "Glossary →")}'),
    ('Client / server', 'The one who asks (client) and the one who answers (server).'),
    ('CLI', 'Command-line interface: you type a command, the computer replies in text.'),
    ('GUI', 'Graphical user interface: windows, icons, mouse clicks.'),
    ('Terminal', f'The window where you type commands. {gl("terminal-terminal-emulator", "Glossary →")}'),
    ('Headless', 'A computer with no monitor, keyboard or mouse attached. Most servers are headless.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Linux was first released', '1991, by Linus Torvalds, then a student in Helsinki'),
    ('World’s 500 fastest supercomputers', 'All run Linux (every TOP500 list since November 2017)'),
    ('Android phones', 'Run on the Linux kernel'),
    ('Path separator', 'Linux and macOS: <code>/</code> · Windows: <code>\\</code>'),
    ('File names', 'Case-sensitive on Linux: <code>Report.txt</code> ≠ <code>report.txt</code>'),
    ('How servers are reached', 'Over the network, usually with SSH (port 22)'),
]) + '\n' + names('Linux command names are short forms. Knowing the full form makes them easy to remember. These are the ones in this lesson.', [
    ('echo', 'echo back', 'Repeats your words, like an echo in a valley.'),
    ('whoami', '“who am I?”', 'Literally the question, as one word.'),
    ('pwd', 'print working directory', 'Where am I working right now?'),
    ('mkdir', 'make directory', 'Directory = folder.'),
    ('cd', 'change directory', 'Walk into another folder.'),
    ('ls', 'list', 'List what is on this shelf.'),
    ('cat', 'concatenate', 'Joins files end to end; with one file it simply shows it.'),
    ('wc', 'word count', 'Counts words, and with -l lines.'),
    ('ssh', 'secure shell', 'A shell on another computer, over an encrypted line.'),
    ('tail', 'the tail (end) of a file', 'The last lines, where the newest log entries are.'),
]) + '\n' + lv + scene('A client-server flow: a phone and a laptop (clients) send requests over the internet to a server, which reads a database and sends replies back.',
    phone(30, 30, 34, 60, 'client: phone', '₹20') + laptop(96, 40, 70, 'client: laptop')
    + label_box(220, 44, 90, 40, ['Internet'], 'card', 9) + arrow(170, 64, 216, 64, 'acc', 2) + arrow(66, 56, 216, 58, 'acc', 2)
    + server(352, 22, 52, 74, 'server (Linux)', 'blue') + arrow(312, 64, 348, 60, 'acc', 2)
    + server(452, 22, 52, 74, 'database', 'green') + arrow(406, 60, 448, 60, 'green', 2)
    + t(560, 46, 'request →', 9, 'acc', anchor='start', bold=True) + t(560, 64, '← reply', 9, 'green', anchor='start', bold=True) + t(560, 82, 'many clients,', 8.6, 'ink2', anchor='start') + t(560, 96, 'one server', 8.6, 'ink2', anchor='start'),
    'Clients <tspan font-weight="700" class="s-acc">ask</tspan>; the server <tspan font-weight="700" class="s-green">answers</tspan>, for thousands of clients at once.') + '''
''' + didyou('“Server” is a job, not a kind of machine. The moment your laptop shares a folder or runs <code>python3 -m http.server</code>, it is a server for anyone who connects to it.') + '''
EXAM> For “What is a server? Differentiate client and server” write: definition (computer providing services over a network), one example pair (browser → web server, UPI app → bank server), three properties of servers (always on, many simultaneous clients, managed remotely) and one line on why servers mostly run Linux (stable, free, scriptable).
''' + qc('You switch off your laptop in the middle of writing an unsaved document. Which part lost the document: the disk or RAM? Why?', 'RAM. Unsaved work lives only in RAM (the desk), which is cleared when the power goes. Saving copies it to the disk (the cupboard), which keeps it.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Four ways to talk to a computer</h2>
''' + cards([
    ('GUI (graphical)', 'Windows, icons and a mouse. Easiest to start with; hard to repeat exactly or do 500 times.', 'Desktops, phones'),
    ('CLI (command line)', 'Type a command, read the reply. Precise, fast, works over a slow network, easy to save as a script.', 'Servers, developers'),
    ('TUI (text UI)', 'Full-screen text programs inside a terminal, controlled by keys: <code>nano</code>, <code>htop</code>, <code>vim</code>.', 'Editing and monitoring on servers'),
    ('Scripts and APIs', 'Commands saved in a file (a shell script) or programs calling each other. The computer runs them without you.', 'Automation, cloud, DevOps'),
]) + '''

  <h3>GUI or CLI? An honest comparison</h3>
''' + table(['', 'GUI (click)', 'CLI (type)'], [
    ['Learning curve', 'Easy: you can explore by clicking', 'Needs a few commands first'],
    ['Repeat a task 100 times', 'Click 100 times', 'One loop or one script'],
    ['Over a slow or remote link', 'Heavy (screen images)', 'Light (only text)'],
    ['Record exactly what you did', 'Hard', 'Command history and scripts'],
    ['Discover options', 'Menus show them', '<code>man</code> and <code>--help</code> show them'],
    ['Where it is used', 'Laptops, phones, design tools', 'Servers, cloud, data pipelines, DevOps'],
]) + '''

  <h3>Kinds of computers you will run Linux on</h3>
''' + table(['Kind', 'What it is', 'How you will meet it in this course'], [
    ['Your laptop + WSL', 'Real Linux running inside Windows', 'Lesson 1.5 sets it up in 10 minutes'],
    ['Virtual machine (VM)', 'A whole computer simulated in software (VirtualBox)', 'Safe place to break things'],
    ['Cloud server', 'A VM rented by the hour from AWS, Azure or GCP', 'What companies actually use'],
    ['Container', 'An isolated set of processes sharing one Linux kernel (Docker)', 'Module 20 explains how it works'],
    ['This website’s runner', 'A real Bash shell on OneCompiler’s Linux machines', 'Every “Run the code” box'],
], minw=600) + '''
''' + didyou('The first computer terminals were teleprinters: electric typewriters connected to a computer. That is why Linux still calls terminal devices <code>tty</code>, short for <b>teletypewriter</b>. Run <code>tty</code> in your terminal (Lesson 1.6).') + qc('Your team must change one setting on 200 cloud servers. GUI or CLI, and why?', 'CLI. You write the change once as commands (or a script), test it on one server and run the same commands on all 200: identical, fast, and recorded. Clicking 200 times is slow and error-prone.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. step by step: how to use this course
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>How to learn with this course: the 7-step loop</h2>
  <p>Every lesson uses the same loop. Each step says what really happens behind it, so you always know whether you are reading, watching a recording or running something for real.</p>
''' + stepper([
    ('1. Read the story and the definition', '<p>Riya, Kabir and Arjun Sir meet a real problem first. Then the definition box gives you the exam-ready wording, and the tabs take it from Beginner to Advanced.</p>',
     'Behind the screen: nothing runs. Start at Beginner; open Intermediate and Advanced when you are ready.'),
    ('2. Watch the two-view animation', '<p>Left: what you see in the terminal. Right: what happens behind the screen (shell, kernel, disk). Play it, or step with Next.</p>',
     'Behind the screen: these are drawings of real behaviour. The facts in them were checked on a real Linux machine.'),
    ('3. Run the code in your browser', '<p>Press <b>Open the live editor</b> in “Run the code”. Edit the commands and press Run.</p>',
     'Behind the screen: your script is sent to OneCompiler, which runs it in real Bash on a Linux machine and sends back the output. Nothing runs on our server.'),
    ('4. Run it on your own Linux', '<p>“Run on your PC” panels show commands for your own WSL, VM or cloud server, including ones that need <code>sudo</code>.</p>',
     'Behind the screen: the outputs shown were recorded on a real Ubuntu machine. Yours will differ in names, sizes and dates.'),
    ('5. Step through “Line by line”', '<p>Press Next to run one line at a time and watch the variables, the current folder, the exit status and the files change.</p>',
     'Behind the screen: recorded from a real Bash run using Bash’s own DEBUG trap, line by line.'),
    ('6. Test yourself', '<p>Quiz, practice problems (Easy → Business), interview scenarios. Try before opening the solution.</p>',
     'Behind the screen: every expected output in a solution was produced by actually running the solution.'),
    ('7. Keep the glossary open', f'<p>Every Linux term, with what happens behind it, is in the {gl("everything-is-a-file", "Linux glossary")}. Dotted links in lessons open it.</p>',
     'Behind the screen: one searchable page with 170+ terms, grouped by topic.'),
]) + '''
  <div class="callout callout--warn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18v.5"/></svg><p><b>A safety habit from day one:</b> practise on your own laptop, a VM or the browser runner, never on a company server. Commands like <code>rm</code> do not ask “Are you sure?” and there is no Recycle Bin on the command line.</p></div>
''' + qc('In which step does your code actually run on a real Linux machine without you installing anything?', 'Step 3, the browser runner: OneCompiler runs your script in real Bash on its Linux machines and sends back the output. Step 4 (“Run on your PC”) runs on your own Linux.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def fileicon(x, y, name, tone='card'):
    return (f'<path d="M{x} {y}h22l8 8v28h-30z" class="s-card2" style="stroke:var(--line)"/>'
            f'<path d="M{x+22} {y}v8h8" style="fill:none;stroke:var(--line)"/>' + t(x + 15, y + 50, name, 7.6, 'ink2', mono=True))

T0 = ['$ cat notes.txt']
T1 = ['$ cat notes.txt', 'chai at 4:30 with Kabir', 'learn 10 commands']
see = [
    term(20, 24, 320, 120, ['$ '], cursor=True) + t(180, 170, 'An empty prompt: the shell is waiting for you.', 9, 'ink2'),
    term(20, 24, 320, 120, T0) + t(180, 170, 'Riya types a command and presses Enter.', 9, 'ink2'),
    term(20, 24, 320, 120, T0) + t(180, 170, 'A few milliseconds pass…', 9, 'ink2'),
    term(20, 24, 320, 120, T0 + ['chai at 4:30 with Kabir']) + t(180, 170, 'The file’s text appears.', 9, 'ink2'),
    term(20, 24, 320, 120, T1 + ['$ '], cursor=True) + t(180, 170, 'Done. The prompt is back for the next command.', 9, 'green', bold=True),
]
def stack(hl):
    rows = [('You (keyboard)', 'card'), ('Terminal window', 'card'), ('Shell (bash)', 'acc'), ('Program: cat', 'card'), ('Kernel (Linux)', 'blue'), ('Disk', 'green')]
    o = ''
    for k, (name, tone) in enumerate(rows):
        on = k in hl
        o += box(20, 14 + k * 30, 150, 24, tone if on else 'card') + t(95, 30 + k * 30, name, 8.8, 'ink' if on else 'ink3', bold=on)
    return o
behind = [
    stack([0, 1]) + t(265, 40, 'Keys go to the terminal,', 8.8, 'ink2') + t(265, 54, 'which passes them to the shell.', 8.8, 'ink2'),
    stack([2]) + t(265, 40, 'The shell splits the line:', 8.8, 'ink2') + t(265, 56, 'command = cat', 8.8, 'acc', mono=True) + t(265, 70, 'argument = notes.txt', 8.8, 'acc', mono=True),
    stack([2, 3, 5]) + t(265, 40, 'It finds the program file', 8.8, 'ink2') + t(265, 56, '/usr/bin/cat on the disk', 8.8, 'acc', mono=True) + t(265, 72, 'and starts it as a process in RAM.', 8.8, 'ink2'),
    stack([3, 4, 5]) + t(265, 40, 'cat asks the kernel:', 8.8, 'ink2') + t(265, 56, '“open notes.txt, read it”', 8.8, 'blue', bold=True) + t(265, 72, 'Kernel finds it on disk,', 8.8, 'ink2') + t(265, 86, 'copies the bytes to RAM.', 8.8, 'ink2'),
    stack([1, 3]) + t(265, 40, 'cat writes the bytes to its', 8.8, 'ink2') + t(265, 54, 'output; the terminal draws them.', 8.8, 'ink2') + t(265, 74, 'cat exits; the shell shows', 8.8, 'ink2') + t(265, 88, 'the prompt again.', 8.8, 'green', bold=True),
]
two = anim_two('cat notes.txt', 'One command, six layers', 'A terminal where Riya types cat notes.txt and the file contents appear.',
               'The layers involved: keyboard, terminal, shell, the cat program, the Linux kernel and the disk.', see, behind,
               ['The terminal shows a prompt. Nothing happens until you type.',
                'Riya types <code>cat notes.txt</code> (cat = “show the contents”) and presses Enter.',
                'For a tiny moment nothing visible happens. A lot is happening behind.',
                'The text of the file appears in the terminal.',
                'The command has finished and the prompt returns. Total time: a few milliseconds.'],
               ['Every key press travels from the keyboard to the terminal app, and the terminal hands the finished line to the <b>shell</b>.',
                'The shell reads the line and splits it into words: the first word is the command, the rest are its arguments.',
                'The shell looks for a program called <code>cat</code> in its list of folders (PATH), finds <code>/usr/bin/cat</code> and starts it. A running program is called a <b>process</b>.',
                'Programs never touch the disk directly. <code>cat</code> asks the <b>kernel</b>, the core of Linux, to open and read the file. The kernel finds it on the disk and copies the bytes into memory.',
                'cat writes those bytes to its output, which is connected to the terminal. Then cat exits and the shell is ready again. You will meet every one of these layers in this course.'])

# scenario 1: UPI payment
def flow_frame(k):
    o = phone(20, 40, 36, 64, 'Riya’s phone', '₹20' if k >= 0 else None)
    o += label_box(110, 46, 70, 40, ['Internet'], 'card', 8.6)
    o += server(220, 30, 46, 64, 'payment app', 'blue') + server(292, 30, 46, 64, 'database', 'green')
    o += t(279, 122, 'all Linux, in a data centre', 7.8, 'ink3')
    return o
pa = flow_frame(0) + cap('Riya scans the stall’s QR code and pays ₹20.', 'Her phone is the client.', 'card', y=150, h=44)
pb = flow_frame(1) + arrow(58, 66, 108, 66, 'acc', 2.2) + arrow(182, 66, 218, 62, 'acc', 2.2) + cap('The request travels over the internet', 'to the payment company’s servers.', 'blue', y=150, h=44)
pc_ = flow_frame(2) + fill(226, 44, 34, 6, 'acc') + arrow(268, 62, 290, 62, 'green', 2) + cap('A program on a Linux server checks the PIN and balance,', 'and records the payment in a database.', 'blue', y=150, h=44)
pd = flow_frame(3) + arrow(218, 74, 182, 76, 'green', 2.2) + arrow(108, 76, 58, 76, 'green', 2.2) + cap('The reply goes back: “₹20 sent”.', 'Another server tells the stall’s speaker.', 'green', y=150, h=44)
pe = (t(180, 30, 'What you just saw', 10.5, 'acc', bold=True)
      + ''.join(t(30, 56 + k * 20, s, 8.8, anchor='start') for k, s in enumerate(['• Client: the phone. It only asks.', '• Servers: always on, serving millions of phones.', '• Nobody clicks on those servers; they run programs', '   started and watched with commands.']))
      + cap('This course teaches you to work on those servers.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', '₹20 by UPI: who is the client, who is the server?',
              'A payment at a chai stall, slowed down. The flow is simplified, but the idea is exact: a client asks, Linux servers do the work.',
              'One payment, many computers', 'A phone sends a UPI payment over the internet to payment servers and a database, and gets a confirmation back.', [pa, pb, pc_, pd, pe],
              ['Riya pays ₹20. Her phone runs an app, but the app does not move money itself. It is a <b>client</b>.',
               'The app sends a request over the internet to the payment company’s computers in a data centre.',
               'Programs running on Linux <b>servers</b> check the request and store the payment in a database (also on a server).',
               'The answer travels back to Riya’s phone, and a message goes to the stall owner’s speaker: “₹20 received.”',
               'The phone is the client; the always-on computers are the servers. Real payment systems involve many more servers and checks; this is the core idea.'],
              hid='scenario-upi')

# scenario 2: remote log
ra = laptop(20, 30, 120, screen=term(26, 36, 108, 58, ['$ '], title='terminal', size=6.6, step=11, cursor=True)) + server(260, 30, 54, 70, 'app-01', 'blue') + cap('Riya opens a terminal on her laptop.', 'app-01 is 1,000 km away, in a data centre.', 'card', y=150, h=44)
rb = laptop(20, 30, 120, screen=term(26, 36, 108, 58, ['$ ssh riya@app-01'], title='terminal', size=6.6, step=11)) + server(260, 30, 54, 70, 'app-01', 'blue') + arrow(146, 60, 254, 60, 'acc', 2.2, dash=True) + t(200, 52, 'encrypted', 7.6, 'acc') + cap('ssh opens an encrypted connection to the server.', '(SSH is taught in Lesson 15.6.)', 'blue', y=150, h=44)
rc = laptop(20, 30, 120, screen=term(26, 36, 108, 58, ['riya@app-01:~$ tail -3 app.log'], title='riya@app-01', size=6, step=11)) + server(260, 30, 54, 70, 'app-01', 'acc') + arrow(146, 60, 254, 60, 'acc', 2.2) + cap('Now every command she types runs on app-01.', 'tail -3 shows the last 3 lines of a file.', 'acc', y=150, h=44)
rd = laptop(20, 30, 120, screen=term(26, 36, 108, 58, ['riya@app-01:~$ tail -3 app.log', ('10:02 INFO payment ok', 'out'), ('10:03 ERROR db timeout', 'err'), ('10:04 INFO payment ok', 'out')], title='riya@app-01', size=5.8, step=10)) + server(260, 30, 54, 70, 'app-01', 'blue') + arrow(254, 74, 146, 74, 'green', 2.2) + cap('Only text comes back, so it is fast even on phone data.', 'She spots the ERROR line at 10:03.', 'green', y=150, h=44)
re_ = (t(180, 30, 'Riya’s first task, done', 10.5, 'green', bold=True) + ''.join(t(30, 56 + k * 20, s, 8.8, anchor='start') for k, s in enumerate(['• No screen on the server was needed.', '• Two commands: ssh, then tail.', '• The same skills work on 1 server or 1,000.'])) + cap('By Module 13 she will count errors per hour in one line.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The intern’s first task: read a log on a far-away server',
              'This is the exact situation from the story. You do not need to understand ssh or tail yet; watch how little is needed to work on a server you will never see.',
              'Working on a remote Linux server', 'A laptop terminal connects with ssh to a remote server and shows the last lines of a log file.', [ra, rb, rc, rd, re_],
              ['Riya’s laptop is the client. app-01 is a Linux server with no screen, far away.',
               'The <code>ssh</code> command opens a secure, encrypted connection and logs her in.',
               'Her prompt now shows <code>riya@app-01</code>: commands typed here run <b>on the server</b>.',
               '<code>tail -3 app.log</code> prints the last three lines of the log. One line says ERROR. Only a few bytes of text travelled.',
               'This is daily work for developers, testers, data engineers and DevOps engineers. By the end of the course you will do much more than read one log.'],
              hid='scenario-ssh')

# scenario 3: rush
def lb(n_servers, load, note_cls='ink2'):
    o = ''.join(phone(10 + k * 22, 20 + (k % 2) * 6, 18, 32) for k in range(5))
    o += t(60, 70, 'thousands of users', 7.6, 'ink3')
    o += label_box(130, 30, 70, 36, ['Load', 'balancer'], 'acc', 8.4)
    o += arrow(112, 48, 128, 48, 'acc', 2)
    for k in range(n_servers):
        y = 12 + k * 38
        o += server(240, y, 40, 30, None, 'blue', leds=2)
        o += arrow(202, 48, 238, y + 15, 'ink3', 1.4)
        lw = min(60, load[k]) if k < len(load) else 0
        o += f'<rect x="290" y="{y+10}" width="60" height="10" rx="3" class="s-card2"/>' + fill(290, y + 10, lw, 10, 'red' if lw > 50 else 'green', rx=3)
    return o
la = lb(1, [30]) + cap('9:55 AM. A ticket-booking site runs on one Linux server.', 'CPU at half. All fine.', 'card', y=164, h=44)
lb_ = lb(1, [60]) + cap('10:00 AM: booking opens. Load jumps.', 'One server at 100% CPU: pages time out.', 'red', y=164, h=44)
lc = lb(3, [60, 0, 0]) + cap('Engineers start two more identical Linux servers', 'from a script, in minutes. No clicking.', 'blue', y=164, h=44)
ld = lb(3, [26, 24, 25]) + cap('The load balancer spreads users over all three.', 'Each server is comfortable again.', 'green', y=164, h=44)
le = (t(180, 30, 'Why commands matter here', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 20, s, 8.6, anchor='start') for k, s in enumerate(['• The same setup must be repeated exactly on each server.', '• Scripts and commands can be repeated; clicks cannot.', '• Cloud servers are created, checked and removed by commands.', '• This is the world of DevOps (Modules 16–20).'])) + cap('Linux + the command line = servers at scale.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The 10 o’clock rush: why one server is never enough',
              'A simplified picture of what happens when a booking window opens and thousands of people click at once.',
              'Scaling out with identical Linux servers', 'Many phones hit a load balancer in front of one, then three, Linux servers; load bars drop as servers are added.', [la, lb_, lc, ld, le],
              ['Before the rush, one server handles the traffic easily.',
               'At 10:00 thousands of users arrive together. One server cannot keep up and requests start failing.',
               'The team runs a script that creates two more servers with exactly the same software and settings.',
               'A <b>load balancer</b> sends each new user to the least busy server. The bars show CPU load (illustrative).',
               'Doing this by clicking on three, thirty or three hundred servers would be slow and error-prone. Commands and scripts make it repeatable.'],
              hid='scenario-rush')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What happens when you type one command</h2>
  <p>Left: what Riya sees. Right: the six layers that work together, in order. Every later module zooms into one of these layers.</p>
''' + two + '''
  <p>Three real-time scenarios follow: a UPI payment, the intern’s first remote task, and a traffic rush that needs more servers.</p>
''' + s1 + s2 + s3 + dissect('Layer by layer: dissect <code>cat notes.txt</code>',
    'The animation showed six layers working together. Now open each one: why it exists, how it works, where it really lives on a Linux machine, and where you will meet it at work. Where possible, run a command that shows that layer for real.', [
    dict(key='you', name='You', sub='keyboard and eyes',
         why='A computer only does what it is told. Someone has to decide the command: you, or a script you wrote.',
         how='You type a line of text and press Enter. Nothing happens until Enter.',
         impl='Your fingers and the keyboard. The keyboard sends key codes to the computer over USB or Bluetooth.',
         used='Every job that touches Linux: developers, testers, data engineers, DevOps, support.'),
    dict(key='term', name='Terminal', sub='the window',
         why='You need somewhere to type and read text. The terminal is that window; it does not understand commands itself.',
         how='It draws the characters you type and passes them to the shell through a pseudo-terminal device; it draws whatever text comes back.',
         impl='An app: GNOME Terminal, Windows Terminal (for WSL), macOS Terminal, or a web terminal. The connection is a device such as <code>/dev/pts/0</code>.',
         used='On every laptop that manages servers; through SSH the same terminal controls a machine far away.'),
    dict(key='shell', name='Shell (bash)', sub='understands your command',
         why='Someone must read “cat notes.txt” and know that <i>cat</i> is a program and <i>notes.txt</i> its input.',
         how='bash splits the line into words, finds the program in the folders listed in PATH, starts it and waits for it to finish.',
         impl='A program file, <code>/usr/bin/bash</code> (about 1.4 MB on Ubuntu 24.04). It is just a program, which is why you can swap it for zsh or fish.',
         used='Interactive work and almost every automation script (Module 12 and the Shell Scripting course).',
         cmd='ps -p $$ -o comm='),
    dict(key='prog', name='Program: cat', sub='does the actual job',
         why='The shell does not read files itself. Each job is done by a small, specialised program.',
         how='cat opens the file, reads its bytes and writes them to its output, which is connected to your terminal.',
         impl='A program file from GNU coreutils: <code>/usr/bin/cat</code>, about 39 KB.',
         used='Everywhere: viewing configs and logs, joining files, feeding data into pipelines.',
         cmd='type cat; ls -l /usr/bin/cat'),
    dict(key='kernel', name='Kernel (Linux)', sub='the boss of the hardware',
         why='Programs must not touch the disk directly, or they could read each other’s files or crash the machine. One trusted program controls the hardware: the kernel.',
         how='cat asks the kernel “open notes.txt, read it” through system calls. The kernel checks permissions, finds the file and copies the bytes to cat.',
         impl='The file <code>/boot/vmlinuz-…</code>, loaded into RAM at start-up. It is the “Linux” in “Linux”.',
         used='Under every Linux server, Android phone, router and supercomputer (Lesson 1.2).',
         cmd='uname -sr'),
    dict(key='disk', name='Disk', sub='where the file really is',
         why='RAM forgets everything at power-off. Files must be kept on a device that remembers.',
         how='The file’s bytes sit in blocks on the SSD. A record called an inode says where those blocks are; the name notes.txt points to that inode.',
         impl='An SSD or hard disk (often a virtual disk in the cloud), formatted with a file system such as ext4.',
         used='Every saved file, database and log. Running out of disk space is one of the most common server problems.',
         setup='echo "chai at 4:30" > notes.txt', cmd='stat -c "%n: %s bytes, inode %i" notes.txt'),
]) + qc('When you run <code>cat notes.txt</code>, which layer is the <b>only</b> one allowed to read the disk directly?', 'The kernel. cat and bash are ordinary programs; they must ask the kernel through system calls.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Linux is already all around you</h2>
''' + usecase(phone(44, 14, 32, 60, text='₹'), '1. Payments and banking apps',
              'When you pay by UPI or check a bank balance, your phone talks to servers in data centres. Server software in banking and payments very commonly runs on Linux.',
              ['Phone app', '*Linux servers', 'Database', 'Reply']) + '\n' + usecase(
    phone(44, 14, 32, 60, text='OS'), '2. Android phones',
    'Android is built on the Linux kernel. Every Android phone in your class is, underneath, running Linux.',
    ['Apps', 'Android', '*Linux kernel', 'Hardware']) + '\n' + usecase(
    '<rect x="20" y="28" width="80" height="36" rx="6" class="s-card2" style="stroke:var(--line)"/>' + ''.join(f'<circle cx="{34+k*12}" cy="46" r="3" style="fill:#2F7D5B"/>' for k in range(5)) + '<path d="M40 28l-8-16M80 28l8-16" style="stroke:var(--ink-3);stroke-width:2"/>',
    '3. Wi-Fi routers, smart TVs and set-top boxes',
    'Many home routers, smart TVs and streaming boxes run a small Linux inside. You use it without ever seeing a terminal.',
    ['Router', '*Embedded Linux', 'Internet']) + '\n' + usecase(
    ''.join(server(10 + k * 36, 16, 30, 50, None, 'blue', leds=3) for k in range(3)),
    '4. Cloud servers',
    'Most virtual servers rented on AWS, Azure and Google Cloud run Linux. Companies create them, configure them and remove them with commands.',
    ['Command / script', '*Linux VM', 'Website or API']) + '\n' + usecase(
    ''.join(f'<rect x="{12+k*20}" y="16" width="16" height="58" rx="2" class="s-board"/>' for k in range(5)) + ''.join(f'<circle cx="{20+k*20}" cy="{26+(k%3)*12}" r="2" style="fill:#9FD3B8"/>' for k in range(5)),
    '5. Supercomputers and research',
    'Every one of the world’s 500 fastest supercomputers runs Linux, including those used for weather forecasting and science.',
    ['Scientists’ jobs', '*Linux cluster', 'Results']) + '\n' + usecase(
    '<ellipse cx="60" cy="24" rx="34" ry="8" class="s-soft-green" style="stroke:var(--green)"/><path d="M26 24v40c0 4 15 8 34 8s34-4 34-8V24" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 54, 'Hadoop · Spark', 8.4, 'green', bold=True),
    '6. Data engineering and AI',
    'Hadoop, Spark, Kafka and most AI training run on clusters of Linux machines. Data engineers and ML engineers use the terminal every day.',
    ['Data files', '*Linux cluster', 'Reports / models']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Short commands you can already understand after this lesson. Each was really run in a fresh Linux folder; the output shown is the real output. You will learn every command properly in later modules.', [
    dict(level='b', title='Who am I and where am I?', scenario='You have just logged in to a machine and want to confirm which user you are and which folder you are in, in one go.',
         cmd='echo "I am $(whoami), working in $(pwd)"',
         explain='<code>$( … )</code> runs a command and puts its answer inside the sentence. <code>whoami</code> prints your user name, <code>pwd</code> the current folder (Lesson 2.2).'),
    dict(level='b', title='How many things are in this folder?', scenario='A colleague asks how many files are in the reports folder. Counting by eye is slow and error-prone.',
         setup='mkdir -p reports && touch reports/jan.csv reports/feb.csv reports/mar.csv reports/notes.txt reports/summary.pdf',
         cmd='ls reports | wc -l', files_note='a folder <code>reports/</code> with 5 files.',
         explain='<code>ls</code> lists the names, one per line when its output goes to another program; <code>|</code> (a pipe) hands that list to <code>wc -l</code>, which counts lines.'),
    dict(level='i', title='Create a whole project structure in one line', scenario='First day of the internship: you want folders for logs, scripts and notes, without typing mkdir five times.',
         cmd='mkdir -p internship/{logs,scripts,notes} && ls internship',
         explain='<code>{logs,scripts,notes}</code> expands into three names (brace expansion, Lesson 3.4). <code>-p</code> creates parent folders as needed. <code>&&</code> runs <code>ls</code> only if mkdir succeeded.'),
    dict(level='a', title='Which file is taking the most space?', scenario='Your laptop says the disk is almost full. Find the biggest files in a folder, largest first.',
         setup='mkdir -p downloads && head -c 52000 /dev/zero > downloads/movie.mp4 && head -c 9000 /dev/zero > downloads/photo.jpg && head -c 1200 /dev/zero > downloads/notes.txt && head -c 300000 /dev/zero > downloads/setup.iso',
         cmd='ls -S downloads | head -2', files_note='a <code>downloads/</code> folder with 4 files of different sizes.',
         explain='<code>ls -S</code> sorts by size, largest first; <code>head -2</code> keeps only the first two lines. Module 13 shows the <code>du | sort</code> version for whole folder trees.'),
], extra=build_up('how many CSV reports are there?', 'Neha asks: “How many CSV reports do we have, and which ones?” Build the answer one small step at a time, checking the output after every step. This is how professionals write long commands.',
    'mkdir -p reports && touch reports/jan.csv reports/feb.csv reports/mar.csv reports/notes.txt reports/summary.pdf', [
    ('ls reports', 'Start by just looking: what is in the folder?'),
    ('ls reports | wc -l', 'Count everything: <code>|</code> sends the list to <code>wc -l</code>, which counts lines. 5, but that includes non-CSV files.'),
    ('ls reports/*.csv', 'Narrow down with a wildcard: only names ending in .csv.'),
    ('echo "CSV reports: $(ls reports/*.csv | wc -l)"', 'Combine and label it: a finished one-line answer you can paste into a chat or a script.'),
])) + which('A preview of the everyday commands you will master in Modules 1–3. Bookmark this table.', [
    ('Check which folder you are in', 'pwd', 'Prints the full path of the current folder.', 'Guessing, then creating files in the wrong place.'),
    ('See what is in a folder', 'ls -l', 'Names plus size, owner and date.', 'Forgetting <code>-a</code> and missing hidden files like <code>.bashrc</code>.'),
    ('Read a short text file', 'cat notes.txt', 'Prints the whole file at once.', 'Using cat on a 2 GB log: your screen floods for minutes.'),
    ('Read a long file or log', 'less app.log', 'Scroll with arrows, search with <code>/</code>, quit with <code>q</code>.', 'Opening huge logs in an editor on the server.'),
    ('Make a folder (and its parents)', 'mkdir -p a/b/c', 'Creates every missing level; no error if it exists.', 'Plain <code>mkdir a/b/c</code> fails when <code>a</code> does not exist.'),
    ('Know which user you are', 'whoami', 'Prints your user name.', 'Assuming you are root (admin) when you are not, or the reverse.'),
    ('Check free disk space', 'df -h', 'Size, used and free space of each disk, in human units.', 'Confusing it with <code>du</code>, which adds up files in a folder.'),
    ('Get help for a command', 'man ls', 'The full manual; <code>ls --help</code> gives a short summary.', 'Copying random commands from the internet without reading what they do.'),
]) + '''
''' + puzzle_answer('The <b>server</b> reads the file. After <code>ssh</code>, every command Riya types is sent to the server and run there, by the server’s shell, programs and kernel, on the server’s disk. Only her keystrokes go one way and the <b>text output</b> (a few hundred bytes) comes back, encrypted. The log file itself never travels. That is why SSH works well even on a slow mobile connection.') + qc('A command printed exactly what you needed, but it was long. How do you make it reusable tomorrow?', 'Save it in a script file (Lesson 12.5), or find it again from your history with the Up arrow or Ctrl+R (Lesson 1.6).') + '''
</section>
'''

cmap = concept_map(
    [(None, 'Using a computer', 'opening files and folders, typing'), (None, 'Curiosity', 'no programming needed')],
    ['CPU, RAM and disk', 'files, folders and paths', 'client and server', 'GUI vs CLI', 'how to use this course'],
    [('1.2', 'Kernel and shell', 'who actually runs your commands'), ('1.5', 'Install Linux', 'get your own Ubuntu safely'), ('2.1', 'The Linux folder tree', 'paths in depth'), ('16.6', 'SSH to a server', 'Riya’s real first task')],
    'Every Linux topic builds on the four words from this lesson: file, folder, path and server. Click any card to jump there.')
body = cmap + (story.replace('  <div class="story">', before('nothing. This lesson is the starting point of the Linux course. If you already know what files, folders and servers are, skim it in 5 minutes and jump to <a href="../02-what-is-an-operating-system-kernel-shell/">Lesson 1.2</a>.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
