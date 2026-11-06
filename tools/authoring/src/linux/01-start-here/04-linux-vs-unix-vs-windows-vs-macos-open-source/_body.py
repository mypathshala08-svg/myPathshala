import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 1. story
sc = (label_box(20, 22, 130, 46, ['Windows laptop', 'Sara: “free = not serious”'], 'blue', 8.4)
      + label_box(170, 22, 130, 46, ['MacBook', 'Kabir: “same terminal!”'], 'card', 8.4)
      + label_box(320, 22, 130, 46, ['Ubuntu server', 'runs the app'], 'acc', 8.4)
      + label_box(470, 22, 150, 46, ['Bank’s AIX box', 'a real Unix'], 'violet', 8.4)
      + t(320, 98, 'Four systems in one project. Riya’s script works on two of them and fails on two.', 9, 'ink2')
      + t(320, 116, 'Why? Kernels, tools, licences, and two invisible characters at the end of each line.', 9, 'acc', bold=True))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Free software can’t be serious”</h2>
  <div class="story">
''' + puzzle('Riya’s script looks exactly the same in Notepad on Windows and in a Linux editor. Yet Linux refuses to run it. What invisible thing is different, and which command can make it visible?') + '''
    <p class="narration">Riya writes a small backup script on her Windows laptop and copies it to the Ubuntu server. It refuses to run. Her college friend Sara, an intern at another company, says: “Linux is free, so it can’t be that professional anyway.” Kabir, on his MacBook, says his terminal “looks exactly like Linux”. And the bank they work with still runs some old Unix machines. Riya decides she needs to understand how these systems really differ.</p>
''' + scene('A Windows laptop, a MacBook, an Ubuntu server and a bank’s AIX Unix machine in one project; a script works on some and fails on others.', sc,
            'Same ideas, different <tspan font-weight="700" class="s-acc">kernels, tools and licences</tspan>.') + '''
R> Sir, Sara says free software is not serious. But you told me banks and supercomputers run Linux. Who is right?
A> You are. In “free software”, free means <b>freedom</b>, not only price. You may read, change and share the code. Companies like Red Hat, Google and IBM pay thousands of engineers to work on Linux precisely because that freedom is useful to them.
K> And my Mac? The terminal looks the same. Is macOS Linux?
A> No. macOS is a <b>Unix</b>, certified as one, with a different kernel. It feels similar because both follow the same Unix ideas. But some tools behave differently, as you will see with <code>sed</code>.
R> And my script? It is just text. Why does Linux reject it?
A> Because Windows ends every line with two invisible characters and Linux expects one. Today: how Linux, Unix, Windows and macOS really differ, what “open source” and the GPL mean, and three traps that catch people moving between systems.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
lv = levels4('Open source and the four systems at four depths', [
    ('v', 'No jargon: a sealed dabba vs a recipe you may change', '''      <p>Imagine two ways of getting lunch.</p>''' + '''<div class="scene"><svg viewBox="0 0 640 200" role="img" aria-label="Left: a sealed lunch box you may only eat (closed software). Right: the dish together with its recipe, which you may read, change and share (open-source software).">''' + label_box(20, 18, 270, 54, ['Sealed dabba', 'eat it, but no recipe'], 'card', 10) + ''.join(t(40, 100 + k * 20, s, 9, 'ink2', anchor='start') for k, s in enumerate(['✓ use it', '✗ see how it is made', '✗ change it', '✗ share it'])) + t(155, 186, 'closed (proprietary): Windows, macOS', 9, 'blue', bold=True) + label_box(350, 18, 270, 54, ['Dish + its recipe', 'printed on the box'], 'green', 10) + ''.join(t(370, 100 + k * 20, s, 9, 'ink2', anchor='start') for k, s in enumerate(['✓ use it', '✓ read the recipe', '✓ change it', '✓ share it with friends'])) + t(485, 186, 'open source: Linux', 9, 'green', bold=True) + '''<text x="632" y="196" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>''' + '''
      <ul>
        <li><b>Windows</b> and <b>macOS</b> are like the sealed dabba: you use them, but their makers keep the recipe (source code).</li>
        <li><b>Linux</b> comes with its recipe. Anyone may read it, improve it and share it. That is <b>open source</b>.</li>
        <li>Open does not mean careless: banks, phones and supercomputers run Linux. Companies pay for <b>support</b>, not for the recipe.</li>
        <li>The four systems (Linux, Unix, Windows, macOS) are like four houses: same kinds of rooms (files, users, programs), different builders and different house rules.</li>
      </ul>'''),
    ('b', 'An open recipe', '''      <ul>
        <li><b>Closed (proprietary) software</b> is like a restaurant’s secret recipe: you can eat the dish (use the program) but not see or change the recipe (source code).</li>
        <li><b>Open-source software</b> publishes the recipe. Anyone may cook it, improve it and share it. Linux is open source.</li>
        <li>“Free software” means <b>free as in freedom</b>. Many open-source programs are also free of cost, but companies still pay for support, certification and services.</li>
        <li>Windows and macOS are mostly closed; Linux is open; classic Unix systems (AIX, Solaris, HP-UX) are commercial.</li>
      </ul>'''),
    ('i', 'How the four systems differ in daily use', '''      <ul>
        <li><b>Paths</b>: Linux/macOS <code>/home/riya</code> with <code>/</code>; Windows <code>C:\\Users\\Riya</code> with <code>\\</code> and drive letters.</li>
        <li><b>Case</b>: Linux treats <code>Logo.png</code> and <code>logo.png</code> as different files. Windows and (by default) macOS do not.</li>
        <li><b>Line endings</b> in text files: Linux and macOS use LF (<code>\\n</code>); Windows uses CRLF (<code>\\r\\n</code>). A script saved on Windows can fail on Linux.</li>
        <li><b>Shells and tools</b>: Linux uses GNU tools and bash; macOS uses BSD-style tools and zsh; Windows uses PowerShell and cmd. Many commands exist everywhere but options can differ (for example <code>sed -i</code>).</li>
        <li><b>Installing software</b>: apt/dnf on Linux, Homebrew on macOS, installers or winget on Windows.</li>
      </ul>'''),
    ('a', 'Licences, kernels and the Unix trademark', '''      <ul>
        <li>The Linux kernel is licensed under <b>GPL version 2 only</b>. GPL is <b>copyleft</b>: if you distribute the kernel or a modified version, you must offer the source under the same licence. That is why phone makers publish their kernel sources.</li>
        <li><b>Permissive</b> licences (MIT, BSD, Apache 2.0) allow use in closed products with only attribution (Apache 2.0 adds a patent grant). <b>AGPL</b> extends copyleft to software offered over a network.</li>
        <li>Using GPL software inside a company, without distributing it, creates no obligation to publish your code. Distribution is the trigger. Legal teams still review licences before shipping products.</li>
        <li><b>“UNIX”</b> is a trademark certified by The Open Group. macOS has been certified UNIX 03 since version 10.5; AIX is certified too. Linux distributions are “Unix-like”: compatible in behaviour, not certified.</li>
        <li>Kernels: Linux (monolithic, Linux), macOS (XNU, hybrid), Windows (NT, hybrid). WSL 2 runs a real Linux kernel in a lightweight VM on Windows.</li>
      </ul>'''),
])

definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Open-source software and the GPL</h2>
''' + def_block(
    '<b>Open-source software</b> is software whose source code is published under a licence that grants everyone the rights to <b>use, study, modify and redistribute</b> it, for any purpose. The <b>GNU General Public License (GPL)</b> is a <b>copyleft</b> open-source licence: anyone who distributes the software or a work based on it must make the corresponding source code available under the same licence terms. The Linux kernel is distributed under GPL version 2.',
    'Open source means the code is public and you are allowed to change and share it. The GPL adds one rule: if you give the software (or your modified version) to others, you must give them the code too, under the same freedom.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Source code', 'The human-readable program text that is compiled into the program you run.'),
    ('Open source', f'Code is published and may be used, changed and shared. {gl("open-source-and-the-gpl", "Glossary →")}'),
    ('Proprietary', 'Closed software: the owner keeps the code and sets strict usage terms.'),
    ('Copyleft', 'A licence rule: modified versions you distribute must keep the same freedom (GPL).'),
    ('Permissive licence', 'MIT, BSD, Apache 2.0: may be used in closed products with attribution.'),
    ('Unix-like', f'Behaves like Unix (POSIX) without the certified trademark: Linux, FreeBSD. {gl("unix", "Glossary →")}'),
    ('LF / CRLF', 'Line endings: Linux uses LF (\\n); Windows uses CR+LF (\\r\\n).'),
    ('Case-sensitive', 'Upper and lower case letters count as different: A.txt ≠ a.txt.'),
    ('GNU vs BSD tools', 'Two families of the same commands (sed, ls, date) with some different options.'),
    ('WSL', f'Windows Subsystem for Linux: real Linux inside Windows. {gl("wsl-windows-subsystem-for-linux", "Glossary →")}'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Linux kernel licence', 'GPL-2.0 (version 2 only)'),
    ('bash licence', 'GPL-3.0 or later'),
    ('macOS', 'Certified UNIX 03; XNU kernel; default shell zsh since 2019'),
    ('Windows', 'NT kernel; PowerShell; runs Linux through WSL 2'),
    ('Commercial Unix still in use', 'IBM AIX, Oracle Solaris, HPE HP-UX (mainly in older enterprise systems)'),
    ('Open Source Definition', 'Published by the Open Source Initiative (OSI), which also approves licences'),
]) + '\n' + names('Several names in this lesson are short forms. Some are jokes, some come from old machines.', [
    ('GPL', 'GNU General Public License', 'The copyleft licence of Linux and bash.'),
    ('MIT', 'Massachusetts Institute of Technology', 'The university where this short, permissive licence came from.'),
    ('BSD', 'Berkeley Software Distribution', 'The Unix from the University of California, Berkeley; also a licence.'),
    ('POSIX', 'Portable Operating System Interface', 'The standard that keeps Unix-like systems compatible; the name was suggested by Richard Stallman.'),
    ('XNU', '“X is Not Unix”', 'macOS’s kernel. Another recursive joke.'),
    ('AIX', 'Advanced Interactive eXecutive', 'IBM’s Unix, still found in banks.'),
    ('CR LF', 'Carriage Return, Line Feed', 'Typewriter moves: back to the left, then down one line.'),
    ('sed', 'stream editor', 'Edits text as it flows past, line by line.'),
]) + '\n' + lv + didyou('CR and LF come from typewriters and teleprinters: “carriage return” moved the print head back to the left edge, “line feed” moved the paper up one line. Windows kept both characters at the end of each line; Unix decided one (LF) was enough. That 50-year-old choice is why Riya’s script fails.') + '''
EXAM> “Differentiate between Linux and Windows” → compare in a table: licence and cost, source availability, kernel, file system paths and case sensitivity, default shell, software installation, security model (users and permissions), and typical use (servers vs desktops). Add one line on GPL and copyleft.
''' + qc('A company runs a GPL-licensed tool on its internal servers and never gives it to anyone outside. Must it publish its own source code?', 'No. GPL obligations start when you <b>distribute</b> the software (or a modified version) to others. Internal use alone does not trigger them. (AGPL is different for network services.)') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Four systems side by side</h2>
''' + table(['', 'Linux', 'Unix (AIX, Solaris)', 'macOS', 'Windows'], [
    ['Kernel', 'Linux (monolithic)', 'Vendor kernels', 'XNU (hybrid)', 'NT (hybrid)'],
    ['Source code', 'Open (GPL v2)', 'Mostly closed', 'Kernel partly open, OS closed', 'Closed'],
    ['Cost', 'Free; paid support optional', 'Licensed with hardware', 'With Apple hardware', 'Licensed'],
    ['Default shell', 'bash', 'ksh / bash', 'zsh', 'PowerShell / cmd'],
    ['Core tools', 'GNU', 'Vendor / POSIX', 'BSD-style', 'Windows tools'],
    ['Paths', '<code>/home/riya</code>', '<code>/home/riya</code>', '<code>/Users/riya</code>', '<code>C:\\Users\\Riya</code>'],
    ['File names', 'Case-sensitive', 'Case-sensitive', 'Case-insensitive by default', 'Case-insensitive'],
    ['Line endings', 'LF', 'LF', 'LF', 'CRLF'],
    ['Install software', 'apt / dnf', 'Vendor tools', 'Homebrew, App Store', 'winget, installers'],
    ['Typical use', 'Servers, cloud, Android, embedded', 'Legacy enterprise', 'Developer and creative laptops', 'Office desktops, some servers'],
], minw=720) + '''

  <h3>Open-source licence families</h3>
''' + table(['Licence', 'Type', 'Main rule', 'Examples'], [
    ['GPL v2 / v3', 'Strong copyleft', 'Distribute → share source under GPL', 'Linux kernel (v2), bash (v3), GCC'],
    ['LGPL', 'Weak copyleft', 'Libraries can be linked from closed programs', 'glibc'],
    ['AGPL v3', 'Network copyleft', 'Offering it as a network service also counts', 'Some databases and web apps'],
    ['MIT', 'Permissive', 'Keep the copyright notice', 'Many JavaScript libraries'],
    ['Apache 2.0', 'Permissive', 'Notice + explicit patent grant', 'Kubernetes, Spark, Kafka, Hadoop'],
    ['BSD 2/3-clause', 'Permissive', 'Keep the notice', 'FreeBSD, many tools'],
    ['Proprietary', 'Closed', 'Use only as the licence allows', 'Windows, Microsoft Office'],
], minw=620) + '''
  <div class="callout callout--warn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18v.5"/></svg><p>This is general information for learners, not legal advice. Companies have legal teams that review licences before shipping software.</p></div>
''' + qc('Which licence family lets you use code inside a closed product with only an attribution notice?', 'Permissive licences: MIT, BSD, Apache 2.0.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps: Windows script to Linux
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Moving a script from Windows to Linux without surprises</h2>
  <p>The most common cross-platform trap, fixed in six steps. You will run the same steps yourself in “Run the code”.</p>
''' + stepper([
    ('1. Copy the script to the server', '<p>Riya copies <code>backup.sh</code>, written in Notepad on Windows, to the Ubuntu server.</p>', 'Behind the screen: the file is copied byte for byte, including Windows line endings (CR LF).'),
    ('2. Run it and read the error', '<p><code>./backup.sh</code> fails with “cannot execute: required file not found” (older bash says “/bin/bash^M: bad interpreter”).</p>',
     'Behind the screen: the kernel reads the first line <code>#!/bin/bash\\r</code> and looks for a program called <code>/bin/bash\\r</code>, with an invisible carriage return at the end. It does not exist.'),
    ('3. Look at the invisible characters', '<p><code>cat -A backup.sh</code> shows <code>^M$</code> at line ends; <code>file backup.sh</code> says “with CRLF line terminators”.</p>', 'Behind the screen: <code>^M</code> is how cat displays the CR byte (decimal 13); <code>$</code> marks the end of the line.'),
    ('4. Remove the CR characters', '<p><code>sed -i \'s/\\r$//\' backup.sh</code> (or <code>dos2unix backup.sh</code> if installed).</p>', 'Behind the screen: sed deletes a CR found just before each end of line, then writes a new file in place of the old one.'),
    ('5. Make it executable', '<p><code>chmod +x backup.sh</code>.</p>', 'Behind the screen: Windows has no execute bit; Linux needs it before <code>./backup.sh</code> may run (Lesson 9.2).'),
    ('6. Prevent it next time', '<p>Set your editor (VS Code, Notepad++) to save with LF, or set Git’s <code>core.autocrlf</code> for the project.</p>', 'Behind the screen: VS Code shows “CRLF” or “LF” in its status bar; one click switches it.'),
]) + '''
''' + qc('Which command shows ^M at the end of each line of a Windows file?', '<code>cat -A file</code>. <code>file</code> also reports “CRLF line terminators” for scripts and text files.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
see = [term(20, 22, 320, 130, ['$ ./backup.sh', ('bash: ./backup.sh: cannot execute:', 'err'), ('required file not found', 'err')]) + t(180, 178, 'The script written on Windows refuses to run.', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ cat -A backup.sh', ('#!/bin/bash^M$', 'acc'), ('echo "backup done"^M$', 'acc')]) + t(180, 178, 'cat -A reveals ^M at the end of every line.', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ file backup.sh', ('... with CRLF line terminators', 'acc')]) + t(180, 178, 'file confirms Windows line endings.', 9, 'ink2'),
       term(20, 22, 320, 130, ["$ sed -i 's/\\r$//' backup.sh", '$ file backup.sh', ('Bourne-Again shell script, ASCII text', 'out')]) + t(180, 178, 'One sed command removes them.', 9, 'ink2'),
       term(20, 22, 320, 130, ['$ ./backup.sh', ('backup done', 'out'), '$ '], cursor=True) + t(180, 178, 'Now it runs.', 9, 'green', bold=True)]
def bytes_(cells, hl=None, note=''):
    o = ''
    for k, (c, kind) in enumerate(cells):
        x = 10 + k * 26
        tone = {'n': 'card', 'cr': 'red', 'lf': 'green'}[kind]
        if hl is not None and k in hl:
            tone = 'acc'
        o += box(x, 40, 24, 30, tone, rx=4) + t(x + 12, 60, c, 8.4, 'ink', bold=(kind != 'n'), mono=True)
    return o + t(180, 100, note, 8.8, 'ink2')
B = [('#', 'n'), ('!', 'n'), ('/', 'n'), ('b', 'n'), ('i', 'n'), ('n', 'n'), ('/', 'n'), ('b', 'n'), ('a', 'n'), ('s', 'n'), ('h', 'n'), ('\\r', 'cr'), ('\\n', 'lf')]
B2 = B[:11] + [('\\n', 'lf')]
behind = [bytes_(B, note='The first line on disk, byte by byte (13 bytes).') + t(180, 124, 'The kernel reads #! and takes the rest as the program path.', 8.6, 'ink2'),
          bytes_(B, hl=[11], note='There is an extra byte: \\r (carriage return), shown by cat as ^M.') + t(180, 124, 'So the path asked for is "/bin/bash\\r". No such file.', 8.6, 'red', bold=True),
          bytes_(B, note='Windows ends lines with \\r\\n; Linux with \\n only.') + t(180, 124, 'Every line of the script has the extra \\r.', 8.6, 'ink2'),
          bytes_(B2, note='sed removes \\r before each end of line.') + t(180, 124, 'Now the first line is exactly #!/bin/bash.', 8.6, 'green', bold=True),
          bytes_(B2, note='The kernel finds /bin/bash and gives it the script to run.') + t(180, 124, 'Lesson: text files carry invisible characters.', 8.6, 'ink2')]
two = anim_two('CRLF', 'Two invisible characters', 'A terminal where a Windows-made script fails, cat -A shows ^M, sed fixes it, and the script runs.',
               'The bytes of the script’s first line, showing the extra carriage-return byte that breaks the shebang path.', see, behind,
               ['Riya runs the script she wrote in Notepad. Bash 5.2 says “cannot execute: required file not found”; older versions say “bad interpreter”.',
                '<code>cat -A</code> shows hidden characters: <code>^M</code> before every <code>$</code> (end of line).',
                '<code>file</code> says the text has CRLF line terminators, the Windows style.',
                'A <code>sed</code> command deletes the CR at the end of every line.',
                'The same script now runs normally.'],
               ['On disk, the first line is the bytes <code>#!/bin/bash</code> followed by an end-of-line. When you run the script, the kernel reads this “shebang” line to find the interpreter.',
                'But there is a hidden carriage-return byte (<code>\\r</code>) before the newline. The kernel looks for a program literally named <code>/bin/bash\\r</code>, which does not exist.',
                'Windows ends text lines with two bytes (CR LF); Linux and macOS with one (LF). Every line of this script carries the extra CR.',
                'After the fix, each line ends with LF only, and the shebang names a real file.',
                'The kernel starts <code>/bin/bash</code> and passes it the script. The same problem breaks CSV imports and config files, so remember <code>cat -A</code> and <code>file</code>.'])

# scenario 1: GNU vs BSD sed
sa = term(6, 20, 170, 104, ["$ sed -i 's/8080/9090/' app.conf", '$ grep port app.conf', ('port=9090', 'out')], title='Ubuntu (GNU sed)', size=7, step=12) + term(184, 20, 170, 104, ['$ '], title='MacBook (BSD sed)', size=7, step=12) + cap('Kabir’s script changes a port on Linux. It works.', '', 'card', y=150, h=34)
sb = term(6, 20, 170, 104, ["$ sed -i 's/8080/9090/' app.conf", ('port=9090', 'out')], title='Ubuntu (GNU sed)', size=7, step=12) + term(184, 20, 170, 104, ["$ sed -i 's/8080/9090/' app.conf", ('sed: ... error', 'err')], title='MacBook (BSD sed)', size=7, step=12) + cap('Same line on his Mac: error.', 'BSD sed needs a backup suffix after -i.', 'red', y=150, h=44)
sc_ = term(6, 20, 170, 104, ["$ sed -i 's/8080/9090/' app.conf"], title='Ubuntu (GNU sed)', size=7, step=12) + term(184, 20, 170, 104, ["$ sed -i '' 's/8080/9090/' app.conf", ('(works)', 'dim')], title='MacBook (BSD sed)', size=7, step=12) + cap('On macOS: sed -i \'\' … (empty suffix).', 'On Linux that form would fail instead.', 'blue', y=150, h=44)
sd = term(6, 20, 348, 104, ["$ sed -i.bak 's/8080/9090/' app.conf", ('works on both, keeps app.conf.bak', 'out')], title='portable', size=7.4, step=13) + cap('Portable form: -i.bak works with GNU and BSD sed.', '', 'green', y=150, h=34)
se = (t(180, 30, 'The lesson', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• macOS commands come from BSD, Linux’s from GNU.', '• Most options match; some (sed -i, date -d, ls --color) do not.', '• Test scripts on the system they will run on.', '• Or install GNU tools on the Mac (Homebrew: gsed, coreutils).'])) + cap('“Looks the same” is not “is the same”.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Same command, Mac vs Linux: the sed -i surprise',
              'Kabir’s script edits a config file in place. It works on the Ubuntu server and fails on his MacBook. A real, very common difference between GNU and BSD tools.',
              'GNU tools vs BSD tools', 'Two terminals: GNU sed on Ubuntu edits a file with sed -i; BSD sed on macOS reports an error until a suffix is given.', [sa, sb, sc_, sd, se],
              ['On Linux, <code>sed -i \'s/8080/9090/\' app.conf</code> edits the file in place.',
               'On macOS the same line fails, because BSD sed expects a backup-file suffix right after <code>-i</code> and treats the next word as that suffix.',
               'On macOS you write <code>sed -i \'\'</code> (an empty suffix). That form, in turn, does not work with GNU sed on Linux.',
               '<code>sed -i.bak</code> works on both and leaves a backup copy you can delete.',
               'macOS and Linux share Unix ideas, but their tools come from different projects. Test scripts where they will run.'],
              hid='scenario-sed')

# scenario 2: case sensitivity deployment
ca = label_box(14, 26, 150, 52, ['Developer on Windows', '&lt;img src="Logo.png"&gt;'], 'blue', 8.4) + label_box(196, 26, 150, 52, ['Folder contains', 'logo.png'], 'card', 8.4) + cap('The page asks for Logo.png; the file is logo.png.', '', 'card', y=150, h=34)
cb = label_box(14, 26, 150, 52, ['Windows laptop test', 'logo shows ✓'], 'green', 8.4) + label_box(196, 26, 150, 52, ['Windows ignores case', 'Logo.png = logo.png'], 'green', 8.4) + cap('On the laptop everything looks perfect.', '', 'green', y=150, h=34)
cc = label_box(14, 26, 150, 52, ['Linux web server', 'logo missing ✗'], 'red', 8.4) + label_box(196, 26, 150, 52, ['GET /Logo.png', '404 Not Found'], 'red', 8.4) + cap('Deployed to Linux: broken image, 404 error.', 'Linux file names are case-sensitive.', 'red', y=150, h=44)
cd_ = term(14, 20, 332, 100, ['$ ls | grep -i logo', ('logo.png', 'out'), "$ grep -o 'src=\"[^\"]*\"' index.html", ('src="Logo.png"', 'acc')], title='riya@web-01', size=7.6, step=13) + cap('ls | grep -i finds the real name; the HTML uses another.', '', 'blue', y=150, h=34)
ce = (t(180, 30, 'Fix and prevent', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Use lower-case file names everywhere: logo.png.', '• Make the code match the exact name.', '• Test on Linux (WSL or a container) before deploying.'])) + cap('Works on Windows ≠ works on Linux.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'It works on my laptop: the case-sensitive file name',
              'A website looks perfect on a Windows laptop and loses its logo on the Linux server. One of the most common deployment bugs for beginners.',
              'Case sensitivity in production', 'A page referencing Logo.png works on Windows but gives 404 on a Linux server where the file is logo.png.', [ca, cb, cc, cd_, ce],
              ['The HTML refers to <code>Logo.png</code>, but the file was saved as <code>logo.png</code>.',
               'On Windows the file system ignores case, so the logo appears and nobody notices.',
               'On the Linux server <code>Logo.png</code> and <code>logo.png</code> are different names; the server finds no <code>Logo.png</code> and returns 404.',
               '<code>ls | grep -i logo</code> (case-insensitive search) shows the real name; the HTML shows the wrong one.',
               'Habit: lower-case names, exact matches, and testing on Linux before release.'],
              hid='scenario-case')

# scenario 3: licence check
def lic(rows, k):
    o = t(180, 22, 'Libraries in the product', 10, 'acc', bold=True)
    for i, (name, l, verdict, tone) in enumerate(rows):
        y = 34 + i * 28
        o += t(14, y + 16, name, 8.6, anchor='start', bold=True) + t(130, y + 16, l, 8.4, 'ink2', anchor='start', mono=True)
        if i < k:
            o += label_box(210, y + 2, 140, 22, [verdict], tone, 8)
    return o
R = [('json-parser', 'MIT', 'OK: keep notice', 'green'), ('http-client', 'Apache-2.0', 'OK: notice + NOTICE file', 'green'), ('pdf-engine', 'AGPL-3.0', 'Review: network use', 'red'), ('kernel (device)', 'GPL-2.0', 'Ship source with device', 'amber')]
la = [lic(R, 0) + cap('Before release: list every library and its licence.', '', 'card', y=150, h=34),
      lic(R, 1) + cap('MIT: fine in a closed product. Keep the copyright notice.', '', 'green', y=150, h=34),
      lic(R, 2) + cap('Apache 2.0: also fine; include the licence and NOTICE.', '', 'green', y=150, h=34),
      lic(R, 3) + cap('AGPL in a web service: legal must review before use.', '', 'red', y=150, h=34),
      lic(R, 4) + cap('A device shipping Linux must offer the kernel source.', 'That is why phone makers publish kernel code.', 'amber', y=150, h=44)]
s3 = anim_one('Real-time scenario 3 · advanced', 'The licence check before a product ships',
              'Companies routinely check the licences of every open-source component before releasing a product. Simplified; real reviews are done with legal teams and scanning tools.',
              'Permissive vs copyleft in practice', 'A list of libraries with MIT, Apache 2.0, AGPL and GPL licences and what each requires before shipping.', la,
              ['A release checklist includes a software bill of materials: every library and its licence.',
               'MIT is permissive: the code may be used in a closed product as long as the copyright notice is kept.',
               'Apache 2.0 is also permissive and adds a patent grant; keep the licence text and any NOTICE file.',
               'AGPL extends copyleft to software used over a network, so using it inside a web service needs legal review.',
               'A device that ships the Linux kernel (GPL-2.0) must offer the kernel source, including the maker’s changes. This is not legal advice; it shows why licences matter in engineering.'],
              hid='scenario-licence')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Why a Windows script fails on Linux</h2>
  <p>Left: Riya’s terminal. Right: the actual bytes of the first line of her script.</p>
''' + two + '''
  <p>Three real-time scenarios: GNU vs BSD tools on Mac and Linux, a case-sensitive file name breaking a website, and a licence check before shipping.</p>
''' + s1 + s2 + s3 + '''
''' + dissect('Layer by layer: dissect the CRLF failure',
    'Follow Riya’s script from the moment Notepad saves it to the moment Linux refuses it. Each layer has a real command that shows exactly what that layer sees.', [
    dict(key='editor', name='Editor on Windows', sub='saves the file',
         why='Text editors must mark where each line ends. Windows tradition marks it with two characters.',
         how='Notepad writes CR (byte 13) and LF (byte 10) after every line.',
         impl='Windows apps by default; modern editors (VS Code, Notepad++) let you choose LF or CRLF in the status bar.',
         used='Every script, CSV and config file written on Windows and copied to a Linux server.'),
    dict(key='bytes', name='File on disk', sub='just bytes',
         why='Files store bytes, not “lines”. A line ending is simply one or two more bytes.',
         how='The extra <code>\\r</code> sits right before every <code>\\n</code>. You cannot see it in most editors.',
         impl='The file’s data blocks; <code>od -c</code> prints every byte as a character.',
         used='Debugging broken CSV imports, configs and scripts.',
         setup="printf '#!/bin/bash\\r\\necho hi\\r\\n' > b.sh", cmd='od -c b.sh | head -2'),
    dict(key='shell', name='Shell (bash)', sub='asks the kernel to run it',
         why='bash does not open scripts itself when you type <code>./b.sh</code>; it asks the kernel to execute the file.',
         how='bash calls <code>execve("./b.sh")</code> and reports whatever error the kernel returns.',
         impl='<code>/usr/bin/bash</code>; the message wording depends on the bash version.',
         used='Every time you run <code>./script.sh</code>.',
         setup="printf '#!/bin/bash\\r\\necho hi\\r\\n' > b.sh && chmod +x b.sh", cmd='./b.sh; echo "exit status: $?"', expect='any'),
    dict(key='kernel', name='Kernel', sub='reads the #! line',
         why='The kernel must know which program should interpret a script.',
         how='It reads the first line after <code>#!</code> up to the newline and tries to start that program. With CRLF the name is <code>/bin/bash\\r</code>, which does not exist.',
         impl='The kernel’s script loader (binfmt_script), part of <code>execve</code>.',
         used='Every script with a shebang: bash, Python, Perl.',
         setup="printf '#!/bin/bash\\r\\necho hi\\r\\n' > b.sh", cmd='head -1 b.sh | od -c'),
    dict(key='fix', name='The fix', sub='sed removes the CR',
         why='Linux tools expect LF only. Removing the CRs makes the file a normal Linux text file.',
         how='<code>sed -i \'s/\\r$//\'</code> deletes a CR at the end of each line and rewrites the file.',
         impl='GNU sed (<code>/usr/bin/sed</code>); or <code>dos2unix</code> if installed; or Git’s line-ending settings.',
         used='Release pipelines often check for CRLF automatically and fail the build.',
         setup="printf '#!/bin/bash\\r\\necho hi\\r\\n' > b.sh && chmod +x b.sh", cmd="sed -i 's/\\r$//' b.sh && ./b.sh && file b.sh"),
]) + qc('What did <code>echo $?</code> print after the failed run, and what does that number mean?', '127: the command (here the interpreter <code>/bin/bash\\r</code>) could not be found.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where these differences matter at work</h2>
''' + usecase(phone(44, 14, 32, 60, text='GPL'), '1. Android phones and kernel source',
              'Because the Linux kernel is GPL, phone and TV makers publish the kernel source for their devices. Developers use it to build custom ROMs and fix drivers.',
              ['Device ships Linux', '*GPL v2', 'Kernel source published']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Windows laptop', '+ WSL Ubuntu'], 'blue', 8.4), '2. Windows desktops, Linux servers',
    'Many companies give staff Windows laptops while their servers run Linux. Developers use WSL, keep LF line endings and lower-case names to avoid surprises.',
    ['Code on Windows', '*WSL / LF / lowercase', 'Linux server']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['MacBook', 'zsh + Homebrew'], 'card', 8.4), '3. Mac developers',
    'Developers on macOS use the Unix terminal daily but deploy to Linux. They install GNU tools or test in Docker containers to catch BSD/GNU differences.',
    ['Mac terminal', '*Docker / GNU tools', 'Linux deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['AIX', 'core banking'], 'violet', 8.4), '4. Unix in banks and telecom',
    'Some long-running core systems still run on commercial Unix such as AIX. Linux skills transfer to them: same shell ideas, permissions and processes.',
    ['Old Unix system', '*shell skills', 'Maintain / migrate']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['SBOM', 'licence scan'], 'green', 8.4), '5. Open-source compliance',
    'Release pipelines often generate a software bill of materials and scan licences automatically, flagging copyleft components for review.',
    ['Build', '*licence scanner', 'Approved release']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company, and are not legal advice.</p>
''' + oneliners('Commands for exactly these cross-platform problems. All were really run on Ubuntu; the sample files are created first.', [
    dict(level='b', title='Does this file have Windows line endings?', scenario='A script or CSV from a Windows colleague behaves strangely.',
         setup="printf 'name,city\\r\\nRiya,Kharghar\\r\\n' > data.csv", cmd='cat -A data.csv', files_note='a CSV saved on Windows.',
         explain='<code>cat -A</code> shows invisible characters: <code>^M</code> is the carriage return, <code>$</code> the end of the line. (For scripts and plain text, <code>file</code> also reports “CRLF line terminators”; for CSV files it may not.)'),
    dict(level='b', title='Find a file when you are not sure of its case', scenario='Is it Logo.png, logo.png or LOGO.PNG?',
         setup='touch logo.png Banner.JPG index.html', cmd='ls | grep -i logo', files_note='three files with mixed-case names.',
         explain='<code>grep -i</code> ignores case while searching the list of names, so you see the exact spelling on disk.'),
    dict(level='i', title='Fix Windows line endings in place', scenario='Convert the CSV so Linux tools see clean lines.',
         setup="printf 'name,city\\r\\nRiya,Kharghar\\r\\n' > data.csv", cmd="sed -i 's/\\r$//' data.csv && cat -A data.csv",
         explain='<code>\\r$</code> matches a carriage return at the end of a line; replacing it with nothing removes it. <code>dos2unix</code> does the same if installed.'),
    dict(level='a', title='List every file in a project that still has CRLF endings', scenario='Before a release, make sure no script or config in the repository has Windows line endings.',
         setup="mkdir -p proj/scripts && printf 'echo ok\\r\\n' > proj/scripts/deploy.sh && printf 'echo ok\\n' > proj/scripts/build.sh && printf 'port=80\\r\\n' > proj/app.conf",
         cmd="grep -rlI $'\\r' proj", files_note='a small project with three files.',
         explain='<code>$\'\\r\'</code> is bash’s way of writing a real carriage-return character. <code>-r</code> searches folders, <code>-l</code> prints only file names, <code>-I</code> skips binary files.'),
], extra=build_up('find and fix every Windows-style file in a project', 'Before a release, make sure no file in the project has Windows line endings, and fix the ones that do.',
    "mkdir -p proj/scripts && printf 'echo ok\\r\\n' > proj/scripts/deploy.sh && printf 'echo ok\\n' > proj/scripts/build.sh && printf 'port=80\\r\\n' > proj/app.conf", [
    ("grep -rlI $'\\r' proj", 'List files that contain a carriage return (<code>-r</code> recursive, <code>-l</code> names only, <code>-I</code> skip binaries).'),
    ("grep -rlI $'\\r' proj | wc -l", 'How many?'),
    ("grep -rlI $'\\r' proj | xargs sed -i 's/\\r$//' && echo fixed", '<code>xargs</code> hands the list of names to sed, which fixes them all (Lesson 13.2).'),
    ("grep -rlI $'\\r' proj | xargs sed -i 's/\\r$//'; echo \"Files still with CRLF: $(grep -rlI $'\\r' proj | wc -l)\"", 'Fix and verify in one line: 0 means the project is clean.'),
], level='a')) + which('Cross-platform situations and the right tool.', [
    ('Check for Windows line endings', 'cat -A notes.txt | head', 'Lines ending in ^M$ have CRLF.', 'Assuming the file is fine because it looks fine in an editor.'),
    ('See invisible characters', 'cat -A notes.txt', 'Shows ^M (CR), tabs as ^I and $ at line ends.', 'Using plain cat, which hides them.'),
    ('Convert CRLF to LF', "sed -i 's/\\r$//' f", 'Works everywhere GNU sed exists.', 'Copy-pasting the file content by hand.'),
    ('Edit a file in place portably (Linux and Mac)', "sed -i.bak 's/a/b/' f", 'GNU and BSD sed both accept a suffix.', '<code>sed -i \'\'</code> on Linux, or <code>sed -i</code> alone on Mac.'),
    ('Search names ignoring case', 'ls | grep -i logo', 'Shows the real spelling.', 'Guessing the case and getting “No such file”.'),
    ('Find a package’s licence (Debian/Ubuntu)', 'less /usr/share/doc/bash/copyright', 'Each package ships its copyright and licence file.', 'Assuming “open source” means “no conditions”.'),
]) + '''
''' + puzzle_answer('An invisible <b>carriage-return character</b> (CR, byte 13) at the end of every line, added by Windows. Linux expects only LF. <code>cat -A</code> shows it as <code>^M</code>, and <code>od -c</code> shows it as <code>\\r</code>. Because the first line becomes <code>#!/bin/bash\\r</code>, the kernel looks for an interpreter that does not exist.') + qc('A website works on a Windows laptop but loses its images on the Linux server. What is the first thing to check?', 'The exact spelling and letter case of the image file names versus the names used in the HTML: Linux file names are case-sensitive.') + '''
</section>
'''

cmap = concept_map(
    [('1.2', 'Kernel and shell', 'what makes an OS'), ('1.3', 'Distributions', 'what Linux “is” in practice')],
    ['Linux vs Unix vs Windows vs macOS', 'open source, copyleft, GPL', 'permissive vs copyleft licences', 'the CRLF and case-sensitivity traps'],
    [('1.5', 'Install Linux', 'WSL on Windows, a VM, or a Mac'), ('6.4', 'sed', 'editing text like the CRLF fix'), ('9.2', 'chmod', 'why scripts need +x'), ('course:shell-scripting', 'Shell Scripting', 'scripts that work everywhere')],
    'Cross-platform habits from this lesson (LF line endings, lower-case names, testing on Linux) save hours in every later module.')
body = cmap + (story.replace('  <div class="story">', before('<a href="../02-what-is-an-operating-system-kernel-shell/">Lesson 1.2</a> (kernel and shell) and <a href="../03-linux-distributions-explained-ubuntu-debian/">Lesson 1.3</a> (distributions).') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
