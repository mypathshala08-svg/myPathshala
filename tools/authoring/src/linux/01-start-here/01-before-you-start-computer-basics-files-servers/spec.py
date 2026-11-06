import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser
BODY = body(HERE)

META = dict(
    module='01-start-here', lesson='01-before-you-start-computer-basics-files-servers', n='1.1',
    module_label='Module 1 · Start here: what is Linux?',
    title='Before you start: computer basics, files, servers and how to use this course',
    desc='The foundation for learning Linux: CPU, RAM and disk, files, folders and paths, clients and servers, GUI vs command line, why servers run Linux, and how to use this course. With animations, real-time scenarios, real Bash you can run in the browser, and interview questions.',
    og_desc='Files, folders, paths, servers and the command line: the basics every Linux learner needs, explained with stories and animations.',
    minutes=20, level='Beginner',
    lead='Riya’s first internship task is to “check a log on the server”, and the server has no screen. Before learning Linux commands, this lesson makes sure the basics are solid: what a computer is made of, how files and folders are organised, what a server is, why we type commands, and how to get the most out of this course.',
    chips=['Story-based', '4 animations', 'Real Bash in your browser'],
)

FIRST = '''# Your first Linux commands. They run on a real Linux machine.
echo "Hello from Linux!"
whoami
pwd
mkdir -p internship/notes
cd internship/notes
cat > day1.txt <<'EOF'
Day 1: learnt what a server is
Day 1: ran my first commands
EOF
ls
cat day1.txt
wc -l day1.txt
'''

RUN = dict(
    heading='Your first eleven commands',
    intro='<p>Read the script, then open the live editor and press <b>Run</b>. Each line is one command. Lines starting with <code>#</code> are comments and are ignored. The output below is from a real run; the user name and folder will be different on OneCompiler and on your own machine.</p>',
    code=FIRST,
    anno=[
        ('echo "Hello from Linux!"', '<code>echo</code> prints its text. The simplest way to see that the shell is listening.'),
        ('whoami', 'Prints the user you are logged in as. On a server this tells you whether you are a normal user or <code>root</code> (the admin).'),
        ('pwd', '“Print working directory”: the folder you are in right now. Every relative file name is looked up from here.'),
        ('mkdir -p internship/notes', 'Makes the folder <code>internship</code> and, inside it, <code>notes</code>. <code>-p</code> means “create parents too, and do not complain if it exists”.'),
        ('cd internship/notes', '“Change directory”: move into that folder. Your prompt’s folder changes.'),
        ("cat > day1.txt <<'EOF'", 'Writes the lines up to <code>EOF</code> into a new file <code>day1.txt</code>. A quick way to create a small text file without an editor (Lesson 5.2).'),
        ('ls', 'Lists the files in the current folder.'),
        ('wc -l day1.txt', 'Counts lines in the file: 2. <code>wc</code> = word count; <code>-l</code> = lines only.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Compare the output with the box above. Which lines differ, and why? (Hint: user name and folder.)', code=FIRST),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what will each <code>pwd</code> print? Write your guesses, then run.',
             code='mkdir -p a/b\ncd a/b\npwd\ncd ..\npwd\ncd ..\npwd\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this script has a typo. Run it, read the error message, fix it. What number does <code>echo $?</code> print, and what does it mean?',
             code='ecoh "Good morning"\necho "exit status: $?"\n', expect='any'),
        dict(label='4 · Your turn', hint='Make a folder named after you, create a file <code>about.txt</code> with two lines about yourself, then show it with <code>cat</code>.',
             code="mkdir -p riya\ncd riya\ncat > about.txt <<'EOF'\nName: Riya\nCity: Kharghar\nEOF\ncat about.txt\n"),
        dict(label='5 · Challenge', hint='Create three files in one command with <code>touch</code>, then count them with <code>ls | wc -l</code>. Can you make it print “3 files”?',
             code='mkdir -p reports\ncd reports\ntouch jan.csv feb.csv mar.csv\necho "$(ls | wc -l) files"\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: meet your own Linux',
    intro='<p>If you already have Linux (WSL, a VM, a Mac terminal for most commands, or a cloud server), run these to see what your machine is made of. No Linux yet? <a href="../05-installing-linux-wsl-on-windows-virtualbox-dual/">Lesson 1.5</a> sets it up. <b>The outputs below were recorded on a real Ubuntu 24.04 cloud VM</b>; your numbers will be different.</p>',
    items=[
        dict(title='1 · Which Linux is this?', cmd='cat /etc/os-release | head -4', output=pc('cat /etc/os-release | head -4'),
             note='Every distribution describes itself in <code>/etc/os-release</code>. Lesson 1.3 explains distributions.'),
        dict(title='2 · How many CPU cores?', cmd='nproc', output=pc('nproc'),
             note='The number of CPU cores this machine can use. A big server may show 64 or more.'),
        dict(title='3 · How much memory (RAM)?', cmd='free -h', output=pc('free -h'),
             note='<code>-h</code> means human units (Gi = gibibytes). Look at <b>total</b> and <b>available</b>. Lesson 15.4 explains every column.'),
        dict(title='4 · How big is the disk, how much is free?', cmd='df -h ~', output=pc('df -h ~'),
             note='Size, used and available space of the disk that holds your home folder (<code>~</code>).'),
    ],
)

TRACE = dict(
    heading='Watch the folder and files change, line by line',
    intro='<p>This short script creates a folder, a file inside it, and then tries to remove the folder. Press <b>Next</b> and watch the <b>Shell</b> box (current folder, exit status) and the <b>Files</b> box. One command fails on purpose: notice the exit status.</p>',
    code='''course="Linux"
echo "Starting $course"
mkdir -p practice
cd practice
echo "first note" > note.txt
ls
cd ..
rmdir practice
echo "exit status was $?"
''',
    notes={1: 'Variable :: A shell variable stores text. No spaces around <code>=</code>.',
           3: 'mkdir :: Creates a folder inside the current folder (~/lab).',
           4: 'cd :: Moves into the new folder. Watch “folder (PWD)”.',
           5: 'Redirect :: <code>></code> sends echo’s text into a file instead of the screen.',
           8: 'rmdir :: rmdir only removes <b>empty</b> folders. practice still has note.txt, so it refuses and prints an error.',
           9: 'Exit status :: <code>$?</code> holds the exit status of the previous command: 0 means success, anything else means failure.'},
)

WORKED_INTRO = 'Three small real tasks: setting up a work folder, counting files by type, and adding up a day’s sales from a text file. Each one runs live and is traced step by step.'
EXAMPLES = [
    dict(level='b', tag='Internship', title='Set up your internship workspace',
         problem='<p>On day one Riya wants a tidy place for her work: a folder <code>internship</code> with <code>logs</code> and <code>notes</code> inside, and a README in notes that records her start date (5 November 2026). Finally she wants to see what she made.</p>',
         inp='(nothing: start from an empty folder)',
         approach=['Create both sub-folders in one <code>mkdir -p</code>.', 'Write the README with <code>echo … ></code>, using <code>date</code> to format the date.', 'List the folder and print the README to check.'],
         code='''mkdir -p internship/logs internship/notes
start=$(date -d 2026-11-05 +"%d %B %Y")
echo "Internship started on $start" > internship/notes/README.txt
ls internship
cat internship/notes/README.txt
''',
         notes={2: 'Command substitution :: <code>$( )</code> runs <code>date</code> and stores its answer in the variable <code>start</code>.'},
         tryit='Change the date to your own start date. Add a third folder <code>scripts</code> in the same mkdir.'),
    dict(level='i', tag='Everyday', title='How many PDFs and images are in Downloads?',
         problem='<p>Kabir’s Downloads folder is a mess. Before cleaning it, he wants a quick count: how many PDF files and how many JPG images are there?</p>',
         inp='Downloads: bill.pdf, marksheet.pdf, ticket.pdf, photo1.jpg, photo2.jpg, notes.txt',
         approach=['Create the sample files with <code>touch</code>.', 'Use a wildcard: <code>*.pdf</code> means “every name ending in .pdf”.', 'Pipe the list into <code>wc -l</code> to count it, and print a sentence.'],
         code='''mkdir -p Downloads
cd Downloads
touch bill.pdf marksheet.pdf ticket.pdf photo1.jpg photo2.jpg notes.txt
pdfs=$(ls *.pdf | wc -l)
jpgs=$(ls *.jpg | wc -l)
echo "PDF files: $pdfs"
echo "JPG files: $jpgs"
''',
         notes={4: 'Wildcard :: The shell replaces <code>*.pdf</code> with the three matching names before ls runs (Lesson 3.4).'},
         tryit='Add two more PDFs to the touch line and run again. Then count .txt files too.'),
    dict(level='a', tag='Business problem', title='The chai stall’s total for the day',
         problem='<p>Raju’s chai stall records every sale as one line: <i>item amount</i>. At closing time he wants the number of sales and the total amount, without a calculator.</p>',
         inp='chai 20\nsamosa 15\nchai 20\nvada-pav 25\nchai 20',
         approach=['Store the sales in a text file (one sale per line).', '<code>wc -l</code> counts the lines, so it counts the sales.', '<code>awk</code> adds up column 2 and prints the total (awk is taught in Lesson 6.5; here just see its power).'],
         code='''cat > sales.txt <<'EOF'
chai 20
samosa 15
chai 20
vada-pav 25
chai 20
EOF
count=$(wc -l < sales.txt)
echo "Sales today: $count"
awk '{ total += $2 } END { print "Total: Rs", total }' sales.txt
''',
         notes={8: 'Count :: <code>wc -l &lt; sales.txt</code> reads the file through input redirection, so only the number is printed (no file name).',
                10: 'awk :: For every line awk adds field 2 to <code>total</code>; at the END it prints it.'},
         tryit='Add “tea 10” as a new sale and run again. How would you count only chai sales? (Try <code>grep -c chai sales.txt</code>.)'),
]

QUIZ = mix([
    dict(q='Which part of a computer keeps your files after the power is switched off?', options=['RAM', 'The disk (SSD or hard disk)', 'The CPU', 'The terminal'], answer=1,
         why='RAM is emptied at power-off. Files are stored on the disk. The CPU only executes instructions.'),
    dict(q='On Linux, are “Report.txt” and “report.txt” the same file?', options=['Yes, names are not case-sensitive', 'No, they are two different files', 'Only inside /home', 'Only if they have the same size'], answer=1,
         why='Linux file names are case-sensitive, so both can exist side by side in the same folder.'),
    dict(q='Which statement about a server is correct?', options=['It must be a special, expensive machine', 'It is a role: a computer that provides services to clients over a network', 'It is always a physical machine in your office', 'It always has a monitor and mouse'], answer=1,
         why='“Server” is a role. A laptop, a VM in the cloud or a huge rack machine can all be servers. Most are headless, many are virtual.'),
    dict(q='Your UPI app sends a payment request to the bank’s computers. In this exchange, your phone is the…', options=['server', 'client', 'kernel', 'database'], answer=1,
         why='The phone asks; the bank’s servers answer. The asking side is the client.'),
    dict(q='Why are servers usually managed through a command line rather than a GUI?', options=['GUIs are illegal on servers', 'Commands are light over the network and can be scripted and repeated exactly', 'The command line is always faster for beginners', 'Servers cannot display text'], answer=1,
         why='Text is tiny to send, and a script can repeat the same steps on one or a thousand servers with no mistakes.'),
    dict(q='What does pwd print?', options=['Your password', 'The current working directory (folder)', 'The power status', 'The list of files'], answer=1,
         why='pwd = print working directory. It never shows passwords.'),
    dict(q='Which path is written in Linux style?', options=['C:\\Users\\riya\\notes.txt', '/home/riya/notes.txt', 'home>riya>notes.txt', '\\\\home\\riya'], answer=1,
         why='Linux uses forward slashes and one tree that starts at /. Drive letters and backslashes are Windows style.'),
])

REVISION = [
    'CPU runs instructions, RAM holds running programs (temporary), disk stores files (permanent).',
    'A <b>file</b> is named data; a <b>directory</b> (folder) holds files and directories; together they form a tree.',
    'A <b>path</b> is a file’s address. Linux: <code>/home/riya/notes.txt</code>, forward slashes, one tree starting at <code>/</code>.',
    'Linux names are case-sensitive; extensions are only hints.',
    'A <b>client</b> asks, a <b>server</b> serves. Server is a role, not a machine type. Most servers are headless and many are virtual.',
    'Servers are managed with a <b>CLI</b> over SSH: light, precise, scriptable.',
    'Four ways to talk to a computer: GUI, CLI, TUI, scripts/APIs.',
    'Course loop: story → animation → run in browser → run on PC → trace → test → glossary.',
]

FAQ = [
    ('Do I need to know programming before learning Linux?', 'No. Linux commands are not programming. You will write small shell scripts later (Module 12), but they start from zero. Basic computer use is enough.'),
    ('Is Linux an operating system or just a kernel?', 'Strictly, Linux is the kernel, the core program. In everyday speech “Linux” means a whole operating system built on that kernel, like Ubuntu or Red Hat Enterprise Linux. Lesson 1.2 explains the difference.'),
    ('What is the difference between a client and a server? Give an example.', 'A client requests a service; a server provides it, usually to many clients at once. Example: a web browser (client) requests a page from a web server; a UPI app (client) sends a payment to a bank’s servers.'),
    ('Why do most servers run Linux?', 'It is free to run on any number of machines, very stable, configurable through text files, easy to automate with scripts, and the tools of the cloud, containers and big data are built for it.'),
    ('What is a headless server?', 'A server with no monitor, keyboard or mouse. It is managed remotely over the network, usually with SSH and the command line.'),
    ('Is the command line harder than a GUI?', 'Only for the first week. After that it is usually faster, and it can do things a GUI cannot: repeat steps exactly, work over slow links and run unattended as scripts.'),
]

PRACTICE_INTRO = 'Small tasks that use only the commands from this lesson. Run each in the browser runner. Expected outputs come from real runs.'
PROBLEMS = [
    dict(level='easy', title='Say hello with a variable', stmt='Store your name in a variable <code>name</code> and print “Welcome to Linux, &lt;name&gt;!”.', inp='name=Asha',
         code='name="Asha"\necho "Welcome to Linux, $name!"\n', explain='A variable is set with <code>name="Asha"</code> (no spaces around =) and read with <code>$name</code>. Double quotes let the variable expand.'),
    dict(level='easy', title='Make a folder and a file, then list it', stmt='Create a folder <code>college</code>, inside it an empty file <code>timetable.txt</code>, then list the folder.', inp='(nothing)',
         code='mkdir college\ntouch college/timetable.txt\nls college\n', explain='<code>touch</code> creates an empty file if it does not exist. You can give a path to touch without cd-ing into the folder.'),
    dict(level='easy', title='User and folder in one line', stmt='Print one line in the form “user: &lt;user&gt; | folder: &lt;folder&gt;”.', inp='(nothing)',
         code='echo "user: $(whoami) | folder: $(pwd)"\n', explain='Two command substitutions inside one echo. Each <code>$( )</code> is replaced by the command’s output.'),
    dict(level='medium', title='Count lines in a to-do list', stmt='Create <code>todo.txt</code> with four tasks (one per line) and print “4 tasks to do”.', inp='buy notebook\nsubmit assignment\ncall home\nrevise Linux 1.1',
         code="cat > todo.txt <<'EOF'\nbuy notebook\nsubmit assignment\ncall home\nrevise Linux 1.1\nEOF\necho \"$(wc -l < todo.txt) tasks to do\"\n",
         explain='<code>wc -l &lt; todo.txt</code> prints only the number. With <code>wc -l todo.txt</code> you would also get the file name.'),
    dict(level='medium', title='A folder for every weekday', stmt='Create folders <code>mon</code> to <code>fri</code> inside <code>week</code> in one command and list them.', inp='(nothing)',
         code='mkdir -p week/{mon,tue,wed,thu,fri}\nls week\n', explain='Brace expansion turns one word into five. <code>ls</code> prints names in alphabetical order, which is why fri comes first.'),
    dict(level='medium', title='Go in, come back', stmt='Make <code>a/b/c</code>, go into <code>c</code>, print the folder, then go back up two levels with one cd and print again.', inp='(nothing)',
         code='mkdir -p a/b/c\ncd a/b/c\npwd\ncd ../..\npwd\n', explain='<code>..</code> means the parent folder; <code>../..</code> goes up two levels. Lesson 2.3 covers paths in depth.'),
    dict(level='business', title='Canteen menu: how many items?', stmt='The college canteen menu is a text file with one item per line. Print how many items are on the menu and show the last two items added.', inp='tea 10\ncoffee 15\nsamosa 15\nidli 30\nupma 25',
         code="cat > menu.txt <<'EOF'\ntea 10\ncoffee 15\nsamosa 15\nidli 30\nupma 25\nEOF\necho \"Items on menu: $(wc -l < menu.txt)\"\ntail -2 menu.txt\n",
         explain='<code>tail -2</code> prints the last two lines of a file. New items are usually appended at the end, so tail shows the newest ones.'),
    dict(level='business', title='Visitor log at the gate', stmt='A security guard logs one line per visitor. Print the total number of visitors and how many came for the “placement” drive.', inp='Asha placement\nVikram library\nNeha placement\nArjun placement\nSara canteen',
         code="cat > visitors.txt <<'EOF'\nAsha placement\nVikram library\nNeha placement\nArjun placement\nSara canteen\nEOF\necho \"Total visitors: $(wc -l < visitors.txt)\"\necho \"For placement: $(grep -c placement visitors.txt)\"\n",
         explain='<code>grep -c word file</code> counts the lines that contain the word (Lesson 6.1). With wc and grep you can already answer simple business questions from text files.'),
]

SCN_INTRO = 'Fresher-level questions that interviewers ask to check you understand where Linux fits, before any commands.'
SCENARIOS = (
    scn('IT services · fresher', 'Fresher', '“Why do companies run servers on Linux?”',
        'In an HR + technical round you are asked why your project should be deployed on Linux and not on Windows desktops.',
        'do you understand servers, cost and automation, not just “Linux is free”?',
        '''<ul>
          <li>Servers are long-running, headless machines; Linux is stable for months without reboots and needs fewer resources because it does not need a desktop.</li>
          <li>No licence cost per machine, which matters when you run tens or hundreds of servers.</li>
          <li>Everything is configurable through text files and commands, so setups can be scripted and repeated exactly (automation, DevOps, cloud).</li>
          <li>The tools we deploy with (Docker, Kubernetes, web servers, databases, Hadoop/Spark) are built for and tested mainly on Linux.</li>
        </ul>''', 'saying only “because it is free” or “because it is more secure” without explaining.') +
    scn('Product company · fresher', 'Fresher', 'Client and server in a real app',
        'The interviewer says: “Explain what happens, in terms of client and server, when you book a cab in an app.”',
        'can you identify clients, servers and the network in a familiar system?',
        '''<ol>
          <li>The phone app is the client: it sends my location and request over the internet.</li>
          <li>The company’s servers (in a data centre or cloud) receive it, find nearby drivers from a database, and send offers to drivers’ phones (also clients).</li>
          <li>When a driver accepts, the server updates the database and notifies my app.</li>
          <li>The servers run continuously and serve many thousands of clients at the same time.</li>
        </ol>''', 'describing only the screens of the app.') +
    scn('Any company · first week', 'Intern', '“SSH into the server and check the log”',
        'Your lead asks you to check a log on a Linux server. You have never used a terminal. What do you do?',
        'are you honest, safe and resourceful?',
        '''<ul>
          <li>Ask for the exact server name, my user name and how access works (password or SSH key), and which log file to check.</li>
          <li>Connect with <code>ssh user@server</code>, confirm with <code>whoami</code> and <code>pwd</code>, and only <b>read</b> the log with <code>less</code> or <code>tail</code>. Never run delete or restart commands I do not understand.</li>
          <li>Copy the relevant error lines and the time into my reply.</li>
        </ul>''', 'pretending to know, or trying random commands from the internet on a company server.') +
    scn('Operations · scenario', 'Fresher', 'GUI or CLI for 50 servers?',
        'Your company has 50 Linux servers and needs the same setting changed on all of them. A teammate wants to log into each one with a remote desktop.',
        'do you see why the command line scales?',
        '''<ul>
          <li>Clicking through 50 desktops is slow and someone will miss a step on one server.</li>
          <li>Write the change once as commands, test on one server, then run the same commands on all 50 (with a loop over SSH, or a tool such as Ansible).</li>
          <li>The script also documents exactly what was changed, which helps reviews and rollbacks.</li>
        </ul>''', '“GUI is easier, so let us just do it manually.”')
) + teaser('1.2', 'Riya’s laptop runs Windows and Kabir’s phone runs Android. One of them secretly runs the same core software as the office’s Ubuntu servers. Which one, and what is that core called?')

from linuxkit import mindmap
MINDMAP = mindmap('Before you start', [
    ('Computer parts', 'acc', ['CPU = does the work', 'RAM = temporary desk', 'Disk = permanent cupboard']),
    ('Files & folders', 'green', ['file = named data', 'folder = directory', 'path = /home/riya/a.txt', 'case-sensitive names']),
    ('Client & server', 'blue', ['client asks, server answers', 'server = a role', 'headless, often virtual']),
    ('GUI vs CLI', 'violet', ['CLI: light, scriptable', 'repeat on 1 or 1000 servers', 'SSH = remote terminal']),
    ('Why Linux', 'amber', ['free, stable, scriptable', 'all TOP500 supercomputers', 'cloud, Android, big data']),
    ('How to learn here', 'red', ['story → animation → run', 'browser runner + PC panels', 'glossary always open']),
])
