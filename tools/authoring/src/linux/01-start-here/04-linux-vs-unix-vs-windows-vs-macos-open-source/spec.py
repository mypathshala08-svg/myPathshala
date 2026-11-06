import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser
BODY = body(HERE)

META = dict(
    module='01-start-here', lesson='04-linux-vs-unix-vs-windows-vs-macos-open-source', n='1.4',
    module_label='Module 1 · Start here: what is Linux?',
    title='Linux vs Unix vs Windows vs macOS, open source and the GPL',
    desc='How Linux, Unix, Windows and macOS really differ (kernels, tools, paths, case sensitivity, line endings), what open source, copyleft and the GPL mean, and the cross-platform traps that break scripts and websites. With animations, real Bash and interview questions.',
    og_desc='Linux vs Windows vs macOS vs Unix, open source and the GPL, and the CRLF and case-sensitivity traps, explained with real commands.',
    minutes=25, level='Beginner → Advanced',
    lead='Riya’s Windows-made script refuses to run on the Linux server, Kabir’s Mac commands behave a little differently, and a friend says free software cannot be professional. This lesson compares Linux, Unix, Windows and macOS honestly, explains open source, copyleft and the GPL, and fixes the three traps that catch people moving between systems.',
    chips=['Story-based', '4 animations', 'Real Bash in your browser'],
)

MAIN = r'''# 1) A script saved on Windows (CRLF line endings)
printf '#!/bin/bash\r\necho "backup done"\r\n' > backup.sh
chmod +x backup.sh
./backup.sh
echo "exit status: $?"
cat -A backup.sh
# 2) Fix: remove the \r before each end of line
sed -i 's/\r$//' backup.sh
./backup.sh
# 3) Linux names are case-sensitive
touch Report.txt report.txt
ls
'''

RUN = dict(
    heading='Break a script the Windows way, then fix it',
    intro='<p>This script creates a file with Windows line endings, shows the error, reveals the hidden characters, fixes them and runs again. Then it proves that Linux keeps <code>Report.txt</code> and <code>report.txt</code> as two files. The output is from a real run with bash 5.2; older bash versions word the first error as “bad interpreter”.</p>',
    code=MAIN, expect='any',
    anno=[
        (r"printf '#!/bin/bash\r\n…'", r'<code>\r\n</code> writes CR + LF, exactly what Notepad on Windows saves at the end of each line.'),
        ('./backup.sh', 'Fails. The kernel looks for an interpreter called <code>/bin/bash</code> followed by an invisible CR.'),
        ('echo "exit status: $?"', '127 means “command not found”: the interpreter could not be found.'),
        ('cat -A backup.sh', 'Shows invisible characters: <code>^M</code> is the CR, <code>$</code> the end of line.'),
        (r"sed -i 's/\r$//' backup.sh", 'Deletes a CR found right before each end of line, editing the file in place.'),
        ('touch Report.txt report.txt', 'On Windows this would be one file. On Linux it creates two.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Find the line with <code>^M$</code>. What does the exit status 127 mean?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many lines will <code>ls</code> print? Remember case sensitivity.',
             code='touch notes.txt Notes.txt NOTES.txt notes.TXT\nls | wc -l\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the web page asks for <code>Logo.png</code>. Run it; why does the check fail, and what is the real file name?',
             code='touch logo.png\nif [ -f Logo.png ]; then echo "image found"; else echo "404: Logo.png not found"; fi\nls | grep -i logo\n'),
        dict(label='4 · Your turn', hint='Create a Windows-style CSV with <code>printf \'a,b\\r\\n1,2\\r\\n\'</code>, count its lines, show it with <code>cat -A</code>, then fix it.',
             code="printf 'a,b\\r\\n1,2\\r\\n' > data.csv\nwc -l < data.csv\ncat -A data.csv\nsed -i 's/\\r$//' data.csv\ncat -A data.csv\n"),
        dict(label='5 · Challenge', hint='Use the portable form <code>sed -i.bak</code> to change port 8080 to 9090, then show both the new file and the backup.',
             code="echo 'port=8080' > app.conf\nsed -i.bak 's/8080/9090/' app.conf\ncat app.conf app.conf.bak\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: licences and line endings on your own Linux',
    intro='<p>On Ubuntu and Debian every package ships its licence information. <b>Outputs were recorded on a real Ubuntu 24.04 cloud VM.</b></p>',
    items=[
        dict(title='1 · Licence texts installed on your system', cmd='ls /usr/share/common-licenses', output=pc('ls /usr/share/common-licenses'),
             note='Debian-family systems keep the full text of common licences here, so packages can refer to them.'),
        dict(title='2 · The GPL version 2, the Linux kernel’s licence', cmd='head -2 /usr/share/common-licenses/GPL-2', output=pc('head -2 /usr/share/common-licenses/GPL-2'),
             note='Read the whole licence with <code>less /usr/share/common-licenses/GPL-2</code> (press q to quit).'),
        dict(title='3 · Which licence does bash use?', cmd='grep -m1 "^License:" /usr/share/doc/bash/copyright', output=pc('grep -m1 "^License:" /usr/share/doc/bash/copyright'),
             note='<code>GPL-3+</code> means GPL version 3 or any later version. Try the same for other packages in <code>/usr/share/doc/</code>.'),
        dict(title='4 · Which sed do you have?', cmd='sed --version | head -1', output=pc('sed --version | head -1'),
             note='GNU sed on Linux. On a Mac, <code>sed --version</code> gives an error because BSD sed has no such option, a quick way to tell them apart.'),
    ],
)

TRACE = dict(
    heading='The CRLF bug and its fix, line by line',
    intro='<p>Watch the file size in the <b>Files</b> box: removing the two CR characters makes it 2 bytes smaller. Watch <code>$?</code> too: 127 when the script cannot start, 0 when it works.</p>',
    code=r'''printf '#!/bin/bash\r\necho hi\r\n' > win.sh
chmod +x win.sh
./win.sh
echo "status: $?"
sed -i 's/\r$//' win.sh
./win.sh
echo "status: $?"
''',
    notes={1: 'Windows-style :: Two lines, each ending with \\r\\n: 22 bytes.',
           3: 'Fails :: The kernel cannot find the interpreter "/bin/bash\\r".',
           5: 'Fix :: sed removes the CR at each line end: 2 bytes fewer.',
           6: 'Works :: The shebang now names a real file.'},
)

WORKED_INTRO = 'Three real tasks: catching case-sensitivity problems, cleaning a folder of Windows files, and a first-pass licence review of a project’s dependencies.'
EXAMPLES = [
    dict(level='b', tag='Web deployment', title='Will these image names break on Linux?',
         problem='<p>A website’s HTML refers to <code>Logo.png</code>, <code>banner.jpg</code> and <code>Team.PNG</code>. The images folder contains <code>logo.png</code>, <code>banner.jpg</code> and <code>team.png</code>. Which references will fail on a Linux server?</p>',
         inp='HTML refers to: Logo.png banner.jpg Team.PNG\nFolder has: logo.png banner.jpg team.png',
         approach=['Create the folder with the real file names.', 'For each name used in the HTML, test with <code>[ -f name ]</code>.', 'Print OK or MISSING.'],
         code='''mkdir -p images
touch images/logo.png images/banner.jpg images/team.png
for name in Logo.png banner.jpg Team.PNG; do
  if [ -f "images/$name" ]; then
    echo "OK      $name"
  else
    echo "MISSING $name"
  fi
done
''',
         notes={4: 'Test :: <code>-f</code> is true only if a file with exactly this name, letter case included, exists.'},
         tryit='Rename the references to match the real names and run again until all are OK.'),
    dict(level='i', tag='Data files', title='Find and fix every Windows file in a folder',
         problem='<p>Meera from the analytics team received a folder of CSV exports. Some were saved on Windows. Find the ones with CRLF endings, fix them, and confirm that none are left.</p>',
         inp='exports/jan.csv (CRLF), exports/feb.csv (LF), exports/mar.csv (CRLF)',
         approach=['Create the sample files with <code>printf</code> (\\r\\n for Windows files).', '<code>grep -l $\'\\r\'</code> lists files that contain a CR.', 'Fix each with <code>sed -i</code>, then search again.'],
         code=r'''mkdir -p exports
printf 'id,amt\r\n1,200\r\n' > exports/jan.csv
printf 'id,amt\n1,150\n' > exports/feb.csv
printf 'id,amt\r\n1,320\r\n' > exports/mar.csv
echo "Windows files:"
grep -l $'\r' exports/*.csv
sed -i 's/\r$//' $(grep -l $'\r' exports/*.csv)
echo "Left after fix: $(grep -l $'\r' exports/*.csv | wc -l)"
''',
         notes={6: 'Search :: Prints the names of files containing a carriage return.', 7: 'Fix :: <code>$( )</code> passes those file names to sed.'},
         tryit='Add a fourth Windows file and run again. What happens if no file needs fixing? (Hint: sed gets no file name.)'),
    dict(level='a', tag='Business problem', title='First-pass licence review of dependencies',
         problem='<p>Before a product release, the team exports its dependency list as <i>name licence</i>. Flag copyleft licences (GPL, AGPL, LGPL) for legal review and count the permissive ones.</p>',
         inp='requests Apache-2.0\nflask BSD-3-Clause\nreportlab BSD-3-Clause\nsome-pdf-lib AGPL-3.0\nlibfoo LGPL-2.1\nlodash MIT',
         approach=['Store the list in a file.', 'Use <code>awk</code> to check column 2 against a pattern of copyleft licences.', 'Print each flagged library and the counts.'],
         code='''cat > deps.txt <<'EOF'
requests Apache-2.0
flask BSD-3-Clause
reportlab BSD-3-Clause
some-pdf-lib AGPL-3.0
libfoo LGPL-2.1
lodash MIT
EOF
awk '$2 ~ /GPL/ { print "REVIEW: " $1 " (" $2 ")"; c++ }
     $2 !~ /GPL/ { p++ }
     END { print c " to review, " p " permissive" }' deps.txt
''',
         notes={9: 'awk :: <code>$2 ~ /GPL/</code> matches GPL, AGPL and LGPL in the licence column.'},
         tryit='Add “mysql-connector GPL-2.0” to the list. This check is only a first pass; real reviews involve the legal team.'),
]

QUIZ = mix([
    dict(q='In “free software”, the word free mainly means…', options=['free of cost only', 'freedom to use, study, change and share', 'free of bugs', 'free of licences'], answer=1,
         why='Free as in freedom. Many free programs also cost nothing, but companies still pay for support and services.'),
    dict(q='What is the key rule of a copyleft licence like the GPL?', options=['You may never sell the software', 'If you distribute it or a modified version, you must offer the source under the same licence', 'You must not modify the code', 'Only companies may use it'], answer=1,
         why='Distribution is the trigger. Using GPL software internally creates no duty to publish your own code.'),
    dict(q='Which licence is permissive?', options=['GPL-3.0', 'AGPL-3.0', 'MIT', 'GPL-2.0'], answer=2,
         why='MIT, BSD and Apache 2.0 are permissive: usable in closed products with attribution.'),
    dict(q='A script made in Notepad fails on Linux; cat -A shows ^M at line ends. What is the cause?', options=['Wrong permissions', 'Windows CRLF line endings', 'The script is too long', 'Linux cannot run scripts'], answer=1,
         why='^M is the carriage return (CR). Remove it with <code>sed -i \'s/\\r$//\'</code> or dos2unix.'),
    dict(q='On Linux, can Report.txt and report.txt exist in the same folder?', options=['No, never', 'Yes, they are different names', 'Only as root', 'Only on macOS'], answer=1,
         why='Linux file names are case-sensitive. Windows and macOS (by default) are not.'),
    dict(q='Which statement about macOS is correct?', options=['It is a Linux distribution', 'It is a certified UNIX with the XNU kernel', 'It uses the Windows NT kernel', 'It has no terminal'], answer=1,
         why='macOS is certified UNIX 03. Its tools are BSD-style, so some options differ from GNU tools on Linux.'),
    dict(q='Which licence does the Linux kernel use?', options=['MIT', 'Apache 2.0', 'GPL version 2', 'Proprietary'], answer=2,
         why='The kernel is GPL-2.0 (version 2 only).'),
])

REVISION = [
    '<b>Open source</b>: code published with the right to use, study, modify and share. Free = freedom.',
    '<b>Copyleft (GPL)</b>: distribute it or a modified version → offer source under the same licence. Linux kernel = GPL-2.0; bash = GPL-3.0+.',
    '<b>Permissive</b> (MIT, BSD, Apache 2.0): fine in closed products with attribution. <b>AGPL</b>: network use counts.',
    'Kernels: Linux (monolithic) · macOS XNU (hybrid, certified UNIX) · Windows NT (hybrid) · AIX/Solaris (commercial Unix).',
    'Tools: GNU on Linux, BSD-style on macOS (<code>sed -i</code> differs; <code>sed -i.bak</code> is portable).',
    'Paths <code>/</code> vs <code>\\</code>; Linux is <b>case-sensitive</b>.',
    'Line endings: LF on Linux/macOS, CRLF on Windows. Detect with <code>file</code> or <code>cat -A</code>; fix with <code>sed -i \'s/\\r$//\'</code>.',
    'Linux licence files on Ubuntu: <code>/usr/share/common-licenses</code>, <code>/usr/share/doc/&lt;pkg&gt;/copyright</code>.',
]

FAQ = [
    ('Differentiate Linux and Windows.', 'Linux: open source (GPL), free, monolithic Linux kernel, case-sensitive file names, / paths, bash and GNU tools, software via package managers, dominant on servers and cloud. Windows: proprietary, licensed, NT kernel, case-insensitive, drive letters and \\, PowerShell, installers/winget, dominant on office desktops.'),
    ('Is macOS based on Linux?', 'No. macOS uses Apple’s XNU kernel and BSD-derived user tools, and is a certified UNIX. It feels similar to Linux because both follow Unix design and POSIX.'),
    ('What is the difference between Unix and Linux?', 'Unix is the original family of operating systems from Bell Labs and its commercial descendants (AIX, Solaris, HP-UX); “UNIX” is a certified trademark. Linux is an independent, open-source Unix-like kernel written in 1991 that follows the same design.'),
    ('What is copyleft?', 'A licensing approach where the freedom to use, change and share must be kept in any distributed derivative. The GPL is the best-known copyleft licence.'),
    ('Can a company use GPL software without publishing its own code?', 'Yes, if it only uses it internally. Obligations under the GPL are triggered when the software, or a modified version, is distributed to others. (AGPL also covers offering software over a network.) This is general information, not legal advice.'),
    ('Why does a script written on Windows fail on Linux?', 'Usually CRLF line endings: the first line becomes <code>#!/bin/bash\\r</code>, so the kernel cannot find the interpreter. Convert to LF with <code>sed -i \'s/\\r$//\'</code> or dos2unix, and add execute permission.'),
]

PRACTICE_INTRO = 'Small cross-platform tasks. Expected outputs are from real runs on Ubuntu with GNU tools.'
PROBLEMS = [
    dict(level='easy', title='How many distinct files?', stmt='Create <code>data.csv</code>, <code>Data.csv</code> and <code>DATA.csv</code>, then print how many files exist.', inp='data.csv Data.csv DATA.csv',
         code='touch data.csv Data.csv DATA.csv\nls | wc -l\n', explain='Three names that differ only in case are three different files on Linux.'),
    dict(level='easy', title='Show the hidden CR', stmt='Create a one-line Windows-style file and show its invisible characters.', inp="printf 'hello\\r\\n'",
         code="printf 'hello\\r\\n' > w.txt\ncat -A w.txt\n", explain='<code>^M</code> is the CR byte and <code>$</code> marks where the line ends.'),
    dict(level='easy', title='LF or CRLF?', stmt='Use <code>file</code> to report on a Linux-style and a Windows-style file.', inp='unix.txt (LF), win.txt (CRLF)',
         code="printf 'a\\n' > unix.txt\nprintf 'a\\r\\n' > win.txt\nfile unix.txt win.txt\n", explain='<code>file</code> only mentions line terminators when they are unusual for Linux.'),
    dict(level='medium', title='Bytes before and after the fix', stmt='Create a 3-line Windows file, print its size in bytes, fix it, print the size again.', inp="printf 'a\\r\\nb\\r\\nc\\r\\n'",
         code="printf 'a\\r\\nb\\r\\nc\\r\\n' > f.txt\necho \"before: $(wc -c < f.txt) bytes\"\nsed -i 's/\\r$//' f.txt\necho \"after: $(wc -c < f.txt) bytes\"\n", explain='Each line loses one CR byte: 9 bytes become 6. <code>wc -c</code> counts bytes.'),
    dict(level='medium', title='Portable in-place edit', stmt='Change <code>debug=true</code> to <code>debug=false</code> with a command that works on Linux and macOS, and keep a backup.', inp='debug=true',
         code="echo 'debug=true' > settings.conf\nsed -i.bak 's/debug=true/debug=false/' settings.conf\necho \"new: $(cat settings.conf)\"\necho \"backup: $(cat settings.conf.bak)\"\n", explain='<code>-i.bak</code> (suffix attached to -i) is accepted by both GNU and BSD sed.'),
    dict(level='medium', title='Lower-case every file name', stmt='A folder has <code>Logo.PNG</code>, <code>Banner.JPG</code> and <code>team.png</code>. Rename every file to lower case.', inp='Logo.PNG Banner.JPG team.png',
         code="mkdir -p img && cd img\ntouch Logo.PNG Banner.JPG team.png\nfor f in *; do\n  lower=$(echo \"$f\" | tr 'A-Z' 'a-z')\n  [ \"$f\" != \"$lower\" ] && mv \"$f\" \"$lower\"\ndone\nls\n",
         explain='<code>tr \'A-Z\' \'a-z\'</code> converts letters to lower case; <code>mv</code> renames only when the name actually changes.'),
    dict(level='business', title='Licence counts for a release note', stmt='From the dependency list, print how many libraries use each licence, most common first.', inp='a MIT\nb Apache-2.0\nc MIT\nd GPL-3.0\ne MIT\nf Apache-2.0',
         code="printf 'a MIT\\nb Apache-2.0\\nc MIT\\nd GPL-3.0\\ne MIT\\nf Apache-2.0\\n' > deps.txt\ncut -d' ' -f2 deps.txt | sort | uniq -c | sort -nr\n",
         explain='The classic counting pipeline: take the column, sort it, count duplicates with <code>uniq -c</code>, sort by count. You will use it constantly (Module 6).'),
    dict(level='business', title='Stop Windows files at the gate', stmt='Before deploying, print FAIL with the file names if any <code>.sh</code> file in <code>deploy/</code> has CRLF endings, otherwise PASS.', inp='deploy/start.sh (LF), deploy/stop.sh (CRLF)',
         code="mkdir -p deploy\nprintf 'echo start\\n' > deploy/start.sh\nprintf 'echo stop\\r\\n' > deploy/stop.sh\nbad=$(grep -l $'\\r' deploy/*.sh)\nif [ -n \"$bad\" ]; then echo \"FAIL: $bad\"; else echo PASS; fi\n",
         explain='<code>-n</code> tests for a non-empty string. Checks like this run in CI pipelines so a broken script never reaches a server.'),
]

SCN_INTRO = 'Interview questions about operating systems, open source and cross-platform problems.'
SCENARIOS = (
    scn('Any company · concepts', 'Fresher', '“Linux is free, so how do companies earn from it?”',
        'The interviewer wants to see if you understand the open-source business model.',
        'do you understand free as in freedom and real business models?',
        '''<ul>
          <li>The code is free to use, but companies pay for subscriptions and support (Red Hat, Canonical, SUSE), certification, long-term maintenance and consulting.</li>
          <li>Cloud providers earn by renting Linux servers; hardware makers by selling devices that run Linux.</li>
          <li>Companies contribute to Linux because sharing the cost of one excellent kernel is cheaper than each building their own.</li>
        </ul>''', '“Nobody earns from Linux” or “it is free so it has no support”.') +
    scn('Product company · debugging', 'Fresher', '“The script works on my laptop”',
        'A teammate’s deploy script, written on Windows, fails on the Linux build server with “cannot execute: required file not found” (or “bad interpreter”).',
        'do you recognise the CRLF problem and fix it properly?',
        '''<ol>
          <li>Check the file: <code>file deploy.sh</code> or <code>cat -A deploy.sh | head -2</code>; ^M or “CRLF” confirms Windows line endings.</li>
          <li>Fix: <code>sed -i 's/\\r$//' deploy.sh</code> (or dos2unix), make sure it is executable.</li>
          <li>Prevent: set the editor to LF, add a <code>.gitattributes</code> rule such as <code>*.sh text eol=lf</code>, and add a CI check.</li>
        </ol>''', 'rewriting the script, or “just run it with bash deploy.sh” without explaining the cause.') +
    scn('Startup · compliance', 'Junior', 'A GPL library in the product',
        'Your company sells a desktop application. A developer added a GPL-licensed library. The product manager asks if that is a problem.',
        'do you know when copyleft obligations apply, and escalate correctly?',
        '''<ul>
          <li>Because the app is distributed to customers, including a GPL library can require releasing the combined work’s source under the GPL.</li>
          <li>Options: replace it with a permissively licensed alternative, use it in a way that legal confirms is acceptable, or accept GPL for that product.</li>
          <li>Raise it with the legal/compliance team before release; do not decide alone.</li>
        </ul>''', 'ignoring it because “open source is free”, or claiming any GPL use makes the whole company’s code public.') +
    scn('Web agency · deployment', 'Fresher', 'Images missing after deployment',
        'A site works perfectly on a Windows laptop. After deploying to the Linux server some images show as broken.',
        'do you think of case sensitivity?',
        '''<ul>
          <li>Check the browser’s network tab or the server log for 404s; compare requested names with <code>ls</code> on the server.</li>
          <li>Likely cause: names differing only in case (Logo.png vs logo.png). Windows ignores case, Linux does not.</li>
          <li>Fix the references or rename files, and adopt lower-case names as a team rule.</li>
        </ul>''', 'blaming the server or caching without checking the exact file names.')
) + teaser('1.5', 'Riya cannot risk wiping her only laptop. Which way of getting Linux gives her a real Ubuntu without touching her Windows files at all?')

from linuxkit import mindmap
MINDMAP = mindmap('Linux & others', [
    ('Four systems', 'blue', ['Linux: open, GPL v2', 'macOS: certified UNIX', 'Windows: NT, closed', 'AIX/Solaris: Unix']),
    ('Open source', 'green', ['use, study, change, share', 'free = freedom', 'pay for support']),
    ('Licences', 'violet', ['GPL: share source', 'MIT/BSD/Apache: permissive', 'AGPL: network use']),
    ('Line endings', 'red', ['Linux LF, Windows CRLF', 'see: cat -A, od -c', "fix: sed -i 's/\\r$//'"]),
    ('Case & paths', 'amber', ['A.txt ≠ a.txt', '/ vs \\', 'test on Linux first']),
    ('GNU vs BSD tools', 'acc', ['sed -i differs on Mac', 'portable: sed -i.bak', 'Homebrew GNU tools']),
])
