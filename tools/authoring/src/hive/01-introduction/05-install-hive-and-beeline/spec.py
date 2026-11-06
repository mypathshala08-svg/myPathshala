import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='01-introduction', lesson='05-install-hive-and-beeline', n='1.5',
    module_label='Module 1 · Start here: why Hive?',
    title='Install Hive 4 with Docker and connect with Beeline',
    desc='Run Apache Hive 4.2.1 on your laptop with Docker Compose: PostgreSQL metastore database, Hive Metastore and HiveServer2. Connect with Beeline and a JDBC URL, create your first external table over 50,002 orders, read the metastore row in Postgres, fix Connection refused and use Beeline in scripts. Real recorded outputs.',
    og_desc='Three containers, one command, your first Hive query on 50,002 real rows. Every output in this lesson was recorded from Hive 4.2.1.',
    minutes=32, level='Beginner → Intermediate',
    lead='Time to stop reading about Hive and run it. With Docker you start the same three services a company runs (a Postgres database, the Hive Metastore and HiveServer2) on one laptop. You connect with Beeline, create a table over 50,002 TiffinGo orders, run a query and then look inside Postgres to see the row Hive wrote about your table. <b>All outputs in this lesson are real</b>, recorded from Hive 4.2.1.',
    chips=['Hive 4.2.1', 'Docker Compose lab', 'Real recorded outputs', 'Runs in your browser (Python)'],
)

MAIN = '''# Read a Hive JDBC URL the way Beeline does
url = "jdbc:hive2://localhost:10000/tiffingo;ssl=false;transportMode=binary"

prefix, rest = url.split("://", 1)
hostport, _, path = rest.partition("/")
host, _, port = hostport.partition(":")
db, *opts = path.split(";")
options = dict(o.split("=", 1) for o in opts)

print("driver  :", prefix)
print("host    :", host)
print("port    :", int(port))
print("database:", db or "default")
print("options :", options)
'''
RUN = dict(
    heading='Run the code: JDBC URLs, ports and Beeline output',
    intro='<p>Beeline itself needs Java and a server, so the browser exercises practise the skills around it: reading a JDBC URL, checking which port is which, turning Beeline’s CSV output into numbers and planning memory for the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('prefix, rest = url.split("://", 1)', '<code>jdbc:hive2</code> selects the Hive JDBC driver. <code>hive2</code> means HiveServer2 (the old HiveServer1 is long gone).'),
        ('host, _, port = hostport.partition(":")', 'Host and port: where HiveServer2 is listening. 10000 is the default for binary (Thrift) mode.'),
        ('db, *opts = path.split(";")', 'Settings come after semicolons, for example <code>ssl=true</code> or <code>transportMode=http;httpPath=cliservice</code>.'),
    ],
    tasks=[
        dict(label='1 · Read a URL', hint='Press <b>Run</b>. Then change the URL to <code>jdbc:hive2://hs2.tiffingo.in:10000/</code> (no database) and see the default.', code=None),
        dict(label='2 · Which service is this port?', hint='<b>Predict first:</b> what does each port in <code>checks</code> belong to? Then add 8080 and see the fallback message.',
             code='''ports = {10000: "HiveServer2 (JDBC/Thrift)", 10002: "HiveServer2 web UI",
         9083: "Hive Metastore (Thrift)", 5432: "PostgreSQL (metastore DB)"}
checks = [10000, 9083, 10002, 5432]
for p in checks:
    print(p, "->", ports.get(p, "not a Hive lab port"))
'''),
        dict(label='3 · Use Beeline CSV output', hint='This is real <code>--outputformat=csv2</code> output from the lab. Compute the total and each city’s share. Add a third city line and run again.',
             code='''out = """city,orders
Pune,7931
Thane,4820"""
lines = out.splitlines()
header, rows = lines[0].split(","), [l.split(",") for l in lines[1:]]
total = sum(int(r[1]) for r in rows)
for city, n in rows:
    print(f"{city:6} {int(n):6}  {int(n) / total:.1%}")
print("total ", total)
'''),
        dict(label='4 · Memory budget', hint='Our idle containers used 1,173 + 348 + 102 MB. Docker Desktop has 4,096 MB. How much is left for queries? Try a 3,072 MB limit.',
             code='''used_mb = {"hiveserver2": 1173, "metastore": 348, "hms-db": 102}
limit_mb = 4096
total = sum(used_mb.values())
print("idle total:", total, "MB")
print("headroom  :", limit_mb - total, "MB")
print("ok" if limit_mb - total > 1024 else "too tight: give Docker more RAM")
'''),
        dict(label='5 · Spot the error', hint='This URL points Beeline at the web UI port. The check fails. Fix the port so the assertion passes.', expect='error',
             code='''url = "jdbc:hive2://localhost:10002/default"
port = int(url.split("://")[1].split("/")[0].split(":")[1])
assert port == 10000, f"port {port} is the web UI, not the JDBC port"
print("URL looks right")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the real lab',
    intro='<p>Follow these with the compose file from Step 2. <b>Every output below was recorded from a real run of Hive 4.2.1</b> (26 October 2026). Times, ids and container ages will differ on your machine; INFO lines are trimmed with “…”.</p>',
    items=[
        dict(title='1 · Start and check the containers', cmd='docker compose -p hivelab up -d\ndocker compose -p hivelab ps\ndocker stats --no-stream --format "table {{.Name}}\\t{{.MemUsage}}"', file='Terminal',
             output=open(CAP + 'compose_ps.txt').read().rstrip() + '\n\nNAME          MEM USAGE / LIMIT\nhiveserver2   1.173GiB / 7.839GiB\nmetastore     347.6MiB / 7.839GiB\nhms-db        102.1MiB / 7.839GiB',
             note='Three containers. Only HiveServer2 (10000, 10002) and the metastore (9083) publish ports to your PC; Postgres is reachable only inside the Docker network.'),
        dict(title='2 · Run a query and read the Tez progress table', cmd='docker exec -it hiveserver2 beeline -u jdbc:hive2://localhost:10000/ -n hive \\\n  -e "SELECT city, COUNT(*) AS orders FROM orders_raw WHERE city IN (\'Pune\',\'Thane\') GROUP BY city ORDER BY city;"', file='Terminal',
             output='''Connected to: Apache Hive (version 4.2.1)
INFO  : Compiling command(queryId=hive_20261026101909_…): SELECT city, COUNT(*) …
INFO  : No Stats for default@orders_raw, Columns: city
INFO  : Completed compiling command(…); Time taken: 0.249 seconds
INFO  : Tez session hasn't been created yet. Opening session
----------------------------------------------------------------------------------------------
        VERTICES      MODE        STATUS  TOTAL  COMPLETED  RUNNING  PENDING  FAILED  KILLED
----------------------------------------------------------------------------------------------
Map 1 .......... container     SUCCEEDED      1          1        0        0       0       0
Reducer 2 ...... container     SUCCEEDED      1          1        0        0       0       0
Reducer 3 ...... container     SUCCEEDED      1          1        0        0       0       0
----------------------------------------------------------------------------------------------
VERTICES: 03/03  [==========================>>] 100%  ELAPSED TIME: 1.02 s
…
INFO  :   VERTICES      DURATION(ms)   CPU_TIME(ms)    GC_TIME(ms)   INPUT_RECORDS   OUTPUT_RECORDS
INFO  :      Map 1              0.00              0              0          50,002                2
…
+--------+---------+
|  city  | orders  |
+--------+---------+
| Pune   | 7931    |
| Thane  | 4820    |
+--------+---------+
2 rows selected (1.573 seconds)''',
             note='The same three vertices as in Lesson 1.4: Map 1 reads all 50,002 rows and outputs 2 (one partial count per city), Reducer 2 merges, Reducer 3 sorts. One task each, because the file is small. “No Stats” means <code>ANALYZE TABLE</code> has not been run yet (Module 8).'),
        dict(title='3 · Common mistakes, real messages', cmd='beeline -u jdbc:hive2://localhost:10001/ -n hive -e "show tables"\nhive -e "select 1"', file='Terminal',
             output=open(CAP + 'refused.txt').read().rstrip() + '\n\nCannot run commands specified using -e. No current connection',
             note='First: wrong port, nobody is listening. Second: in Hive 4 the <code>hive</code> command starts Beeline, which has no URL to connect to. Use <code>beeline -u jdbc:hive2://…</code>.'),
    ],
)

TRACE = dict(
    heading='Parsing a JDBC URL, one line at a time',
    intro='<p>Watch the URL being cut into pieces. The variables show exactly what Beeline needs to open a connection: host, port, database and options.</p>',
    code='''url = "jdbc:hive2://localhost:10000/tiffingo;ssl=false"
scheme, rest = url.split("://", 1)
hostport, path = rest.split("/", 1)
host, port = hostport.split(":")
db, opt = path.split(";")
key, value = opt.split("=")
conn = {"host": host, "port": int(port), "db": db, key: value}
print(conn)
''',
    notes={2: 'Driver :: <code>jdbc:hive2</code> selects the HiveServer2 JDBC driver.', 7: 'Ready :: Everything Beeline needs to open a session.'},
)

WORKED_INTRO = 'Three small jobs that come up on the first day with a Hive environment: building connection strings from a config, turning Beeline output into a report, and working out from the logs when a server became ready.'
EXAMPLES = [
    dict(level='b', tag='Connections · config', title='Build JDBC URLs for three environments',
         problem='<p>TiffinGo has a laptop lab, a test cluster and production. Each has a host, a port and a database; production also needs <code>ssl=true</code>. Print the Beeline command for each environment.</p>',
         inp='lab: localhost:10000/default · test: hs2-test.tiffingo.in:10000/tiffingo · prod: hs2.tiffingo.in:10000/tiffingo + ssl',
         approach=['Keep the environments in a dictionary.', 'Build <code>jdbc:hive2://host:port/db</code>.', 'Append <code>;ssl=true</code> when needed and print the command.'],
         code='''envs = {
    "lab":  ("localhost", 10000, "default", False),
    "test": ("hs2-test.tiffingo.in", 10000, "tiffingo", False),
    "prod": ("hs2.tiffingo.in", 10000, "tiffingo", True),
}
for name, (host, port, db, ssl) in envs.items():
    url = f"jdbc:hive2://{host}:{port}/{db}"
    if ssl:
        url += ";ssl=true"
    print(f"{name:4} beeline -u '{url}'")
''', notes={6: 'Build :: Same format everywhere; only the values change.'},
         tryit='Add an environment “dr” on hs2-dr.tiffingo.in with ssl. Notice that no code changes, only data: this is how teams avoid hard-coded URLs.'),
    dict(level='i', tag='Beeline output · report', title='Turn csv2 output into a revenue report',
         problem='<p>A scheduler runs <code>beeline --silent=true --outputformat=csv2</code> and saves this real output. Print each city’s revenue in lakh rupees and its share of the total, largest first.</p>',
         inp='city,orders,revenue\\nMumbai,10015,2941330\\nBengaluru,9298,2724070\\nPune,7931,2344660',
         approach=['Split the text into lines; the first line is the header.', 'Convert numbers with <code>int()</code>.', 'Sort by revenue and print lakhs (÷ 100,000) and percentages.'],
         code='''out = """city,orders,revenue
Mumbai,10015,2941330
Bengaluru,9298,2724070
Pune,7931,2344660"""
rows = [line.split(",") for line in out.splitlines()[1:]]
rows = [(c, int(o), int(r)) for c, o, r in rows]
total = sum(r for _, _, r in rows)
for city, orders, rev in sorted(rows, key=lambda x: -x[2]):
    print(f"{city:10} Rs {rev / 100000:5.2f} lakh  {rev / total:.1%}")
''', notes={6: 'Convert :: Beeline prints text; numbers must be converted before maths.'},
         tryit='These three rows are the top cities from the real lab query. Add “Hyderabad,5979,1763190” and check the shares still add up to 100%.'),
    dict(level='a', tag='Operations · start-up', title='When was HiveServer2 ready?',
         problem='<p>Log lines from a start-up are given (format <code>HH:MM:SS message</code>, taken from the real quick-start container). Find how many seconds passed between the schema tool starting and the web UI starting, and the first moment a client could connect.</p>',
         inp='10:12:46 schematool start · 10:12:56 Starting HiveServer2 · 10:13:02 Starting Web UI on port 10002 · 10:13:03 Started HttpServer',
         approach=['Convert each time to seconds since midnight.', 'Find the lines by keyword.', 'Print the differences.'],
         code='''log = ["10:12:46 schematool -initOrUpgradeSchema",
       "10:12:56 Starting HiveServer2. PID is: 1",
       "10:13:02 Starting Web UI on port 10002",
       "10:13:03 Started HttpServer[hiveserver2] on port 10002"]
def secs(line):
    h, m, s = map(int, line[:8].split(":"))
    return h * 3600 + m * 60 + s
start = secs(log[0])
for line in log[1:]:
    print(f"+{secs(line) - start:2d} s  {line[9:]}")
''', notes={5: 'Parse :: Turn a clock time into one number so we can subtract.'},
         tryit='In our measurement port 10000 accepted connections 20 s after docker run. Add a line “10:13:06 port 10000 open” and see where it falls. Scripts that start Hive should wait for the port, not a fixed sleep.'),
]

QUIZ = mix([
    dict(q='Beginner: Which port does Beeline connect to by default for HiveServer2?', options=['9083', '10000', '10002', '5432'], answer=1,
         why='10000 is HiveServer2’s Thrift/JDBC port. 10002 is its web UI, 9083 the metastore and 5432 Postgres.'),
    dict(q='Beginner: What does the metastore store?', options=['The rows of every table', 'Table definitions: names, columns, types, locations, partitions', 'Query results', 'Docker images'], answer=1,
         why='The metastore holds metadata only. In our lab CREATE TABLE added a row to TBLS in Postgres while the CSV file stayed where it was.'),
    dict(q='Beginner: In Hive 4, what happens when you type the hive command?', options=['The old Hive CLI starts and reads the metastore directly', 'Beeline starts', 'HiveServer2 starts', 'Nothing, the command was removed'], answer=1,
         why='The old CLI is gone. hive launches Beeline, so hive -e without a URL fails with “No current connection”.'),
    dict(q='Intermediate: Why is the embedded Derby metastore unsuitable for a team?', options=['Derby cannot store table names', 'Only the one process that embeds it can use it, and it lives inside that container', 'It is slower than Postgres for SELECT queries on data', 'It needs Kerberos'], answer=1,
         why='Embedded Derby has no network service; Spark or a second HiveServer2 cannot share it, and removing the container deletes it.'),
    dict(q='Intermediate: Beeline prints “Connection refused (state=08S01)”. What is the most likely cause?', options=['A syntax error in the SQL', 'Nothing is listening on that host and port yet (wrong port, container down or still starting)', 'The table has no statistics', 'The user lacks SELECT permission'], answer=1,
         why='Refused is a network-level answer: no listener. Check the port, docker compose ps and the HiveServer2 log.'),
    dict(q='Intermediate: Which switch gives clean comma-separated output for a script?', options=['--outputformat=table', '--outputformat=csv2', '--verbose=true', '-n csv'], answer=1,
         why='csv2 (or tsv2) prints plain delimited rows; add --silent=true to hide INFO lines.'),
    dict(q='Advanced: Inside the Docker network, how does HiveServer2 reach the metastore in our compose lab?', options=['thrift://localhost:9083', 'thrift://metastore:9083', 'jdbc:hive2://metastore:10000', 'postgres://metastore:5432'], answer=1,
         why='Containers resolve each other by service name. localhost inside the hiveserver2 container would mean the hiveserver2 container itself.'),
    dict(q='Advanced: What does schematool do the first time the metastore starts?', options=['Loads CSV data into tables', 'Creates the metastore’s own tables and version record in the database', 'Compiles HiveQL', 'Starts YARN'], answer=1,
         why='schematool -initOrUpgradeSchema created 84 tables in Postgres in our run and recorded schema version 4.2.0.'),
])

REVISION = [
    'A Hive deployment = <b>HiveServer2</b> (10000, web UI 10002) + <b>Metastore</b> (9083) + its <b>RDBMS</b> + <b>storage</b> + <b>engine</b> (Tez).',
    'Lab: <code>docker compose up -d</code> starts <b>Postgres</b>, <b>metastore</b>, <b>hiveserver2</b> from image <code>apache/hive:4.2.1</code>; <code>SERVICE_NAME</code> picks the role.',
    'Connect: <code>beeline -u jdbc:hive2://localhost:10000/ -n hive</code>. URL = driver · host · port · database · ;options.',
    'Metastore modes: <b>embedded</b> (Derby, one process) · <b>local</b> · <b>remote</b> (service on 9083, shared by many engines).',
    '<code>CREATE EXTERNAL TABLE … LOCATION</code> writes metadata only (rows in TBLS, SDS, COLUMNS_V2); data files are not copied.',
    'Beeline: <code>-e</code> one statement, <code>-f</code> script, <code>--silent=true</code>, <code>--outputformat=csv2|tsv2|vertical|json</code>, <code>--hivevar</code>, <code>!tables</code>, <code>!quit</code>.',
    '“Connection refused” → wrong port, container down, or not ready yet. Inside Docker use service names, from your PC use localhost.',
    'In Hive 4 the old CLI is removed: <code>hive</code> starts Beeline.',
]
FAQ = [
    ('Do I need Hadoop installed to practise Hive?', 'Not for this course. The apache/hive image includes the Hadoop and Tez libraries it needs and runs Tez in local mode with the local file system as storage. You learn the same HiveQL, metastore and plans. On a real cluster the SQL is the same; only the storage paths (hdfs:// or s3a://) and the place where tasks run (YARN) differ.'),
    ('Why Postgres for the metastore and not the built-in Derby?', 'Derby in embedded mode can be used by only the one process that embeds it and disappears with its container. A separate database such as PostgreSQL or MySQL can be shared by a metastore service that HiveServer2, Spark and Trino all use, and can be backed up. Production deployments always use an external database.'),
    ('What is the difference between Beeline and the old Hive CLI?', 'Beeline is a JDBC client: it connects to HiveServer2, which applies security, sessions and resource management. The old CLI ran the compiler inside the user’s own process and talked to the metastore directly, bypassing HiveServer2 and its security. The old CLI is deprecated and removed in Hive 4; the hive command now starts Beeline.'),
    ('My first query took longer than the next ones. Why?', 'The first query in a session opens a Tez session (“Tez session hasn’t been created yet. Opening session”), which starts the Tez application master. Later queries in the same session reuse it. Each new beeline -e command opens a new session, so scripts that run many statements should use -f with one file.'),
    ('How do I stop and restart the lab without losing my tables?', 'Use docker compose -p hivelab stop and docker compose -p hivelab start (or up -d). The metastore lives in the Postgres volume hms-db and managed table data in the warehouse volume, so both survive. docker compose down -v deletes the volumes, and with them every table definition and managed table.'),
]

PRACTICE_INTRO = 'Short programs about ports, URLs, Beeline output and lab resources: the everyday arithmetic of running Hive.'
PROBLEMS = [
    dict(level='easy', title='Name that port', stmt='Print the service for ports 10000, 10002, 9083 and 5432 from a dictionary.', inp='[10000, 10002, 9083, 5432]',
         code='''svc = {10000: "HiveServer2", 10002: "HS2 web UI", 9083: "Metastore", 5432: "Postgres"}
for p in [10000, 10002, 9083, 5432]:
    print(p, svc[p])
''', explain='Memorise these four. Most connection problems are a wrong port.'),
    dict(level='easy', title='Build a URL', stmt='Given host hs2.tiffingo.in, port 10000 and database tiffingo, print the JDBC URL.', inp='hs2.tiffingo.in · 10000 · tiffingo',
         code='''host, port, db = "hs2.tiffingo.in", 10000, "tiffingo"
print(f"jdbc:hive2://{host}:{port}/{db}")
''', explain='jdbc:hive2://hs2.tiffingo.in:10000/tiffingo. If the database is left out, Hive uses default.'),
    dict(level='easy', title='Count Beeline result rows', stmt='Beeline printed the table below. Count the data rows (lines that start with “| ” and are not the header).', inp='+--------+\n| city   |\n+--------+\n| Pune   |\n| Thane  |\n+--------+',
         code='''out = """+--------+
| city   |
+--------+
| Pune   |
| Thane  |
+--------+"""
rows = [l for l in out.splitlines() if l.startswith("| ")][1:]
print(len(rows), "rows")
''', explain='2 rows. The first “| ” line is the header. Beeline also prints “2 rows selected” at the end, but scripts should use csv2 instead of parsing the table format.'),
    dict(level='medium', title='Options to a dictionary', stmt='Parse the options of <code>jdbc:hive2://hs2:10001/sales;transportMode=http;httpPath=cliservice;ssl=true</code> into a dictionary.', inp='transportMode=http;httpPath=cliservice;ssl=true',
         code='''url = "jdbc:hive2://hs2:10001/sales;transportMode=http;httpPath=cliservice;ssl=true"
opts = dict(p.split("=") for p in url.split(";")[1:])
print(opts)
''', explain='HTTP transport mode is used behind load balancers and gateways; it uses port 10001 and an httpPath by default.'),
    dict(level='medium', title='Seconds until ready', stmt='A script polls the port every 2 seconds. It failed 9 times and then succeeded. How long did HiveServer2 take, and how many polls would a 60-second timeout allow?', inp='9 failures · 2 s interval · 60 s timeout',
         code='''fails, every, timeout = 9, 2, 60
print("ready after about", (fails + 1) * every, "s")
print("polls allowed:", timeout // every)
''', explain='About 20 s, which matches our measurement. Use a timeout well above the normal start time so slow laptops do not fail.'),
    dict(level='medium', title='CSV to totals', stmt='Sum the orders column from real csv2 output “city,orders / Pune,7931 / Thane,4820”.', inp='city,orders\nPune,7931\nThane,4820',
         code='''out = "city,orders\\nPune,7931\\nThane,4820"
print(sum(int(l.split(",")[1]) for l in out.splitlines()[1:]))
''', explain='12,751. Skip the header line and convert the text to integers before adding.'),
    dict(level='business', title='Laptop or cloud for a training batch?', stmt='A batch of 40 students each needs about 2 GB RAM for the lab. Laptops have 8 GB. A cloud VM with 16 GB costs Rs 12 per hour and fits 6 students. For 30 hours of practice, what does the cloud cost if laptops are not used?', inp='40 students · 6 per VM · Rs 12/hour · 30 hours',
         code='''import math
students, per_vm, rate, hours = 40, 6, 12, 30
vms = math.ceil(students / per_vm)
print("VMs:", vms, "| cost: Rs", vms * rate * hours)
''', explain='7 VMs for 30 hours = Rs 2,520. With 8 GB laptops each student can run the lab locally, so the batch can avoid most of that cost.'),
    dict(level='business', title='Backup check', stmt='The metastore database is 180 MB and grows 12 MB per month; table data is 3 TB. A backup job copies only the metastore. How big is it after 12 months, and why is backing it up so important compared with its size?', inp='180 MB + 12 MB/month · 12 months',
         code='''size = 180 + 12 * 12
print("metastore after 12 months:", size, "MB")
print("share of total data:", f"{size / (3 * 1024 * 1024):.4%}")
''', explain='324 MB, about 0.01% of the data, yet without it nobody knows which files form which table, partition or column. Small, critical, back it up.'),
]

SCN_INTRO = 'Setting up and connecting are the first things a new data engineer does. Interviewers use them to check practical experience.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How would you set up Hive to practise?”',
        'The interviewer asks how you practised Hive without a company cluster.',
        'have you actually run Hive, and do you know its parts?',
        '''<ol>
          <li>I used Docker Compose with the official <code>apache/hive</code> image: one container for PostgreSQL, one for the Hive Metastore on 9083 and one for HiveServer2 on 10000.</li>
          <li>I connected with Beeline using <code>jdbc:hive2://localhost:10000/</code>, created external tables over CSV files and ran queries on Tez in local mode.</li>
          <li>I checked the metastore tables in Postgres to see how a CREATE TABLE is stored.</li>
        </ol>''', 'saying “I only watched videos”; describe the components and one thing you ran.') +
    scn('Support · connectivity', 'Fresher', 'Beeline says Connection refused',
        'A new analyst cannot connect: “Could not open client transport … Connection refused”.',
        'can you troubleshoot from network to service?',
        '''<ul>
          <li>Confirm the URL: host, port 10000 (not the web UI port 10002), correct transport mode.</li>
          <li>Check the service is running and listening (container status, <code>ss -ltn</code> or the HiveServer2 log); it may still be starting.</li>
          <li>Check firewalls or security groups between the analyst and the server; then retry with <code>--verbose=true</code>.</li>
        </ul>''', 'blaming the SQL; Connection refused happens before any SQL is sent.') +
    scn('Platform · design', 'Mid-level', 'Why not use embedded Derby in our team setup?',
        'A colleague proposes running HiveServer2 with the default embedded Derby metastore to save time.',
        'do you understand metastore modes and their limits?',
        '''<ul>
          <li>Embedded Derby can be opened by only one process; a second HiveServer2, Spark or Trino cannot share the catalogue.</li>
          <li>Metadata would live inside one machine or container: no backups, no high availability.</li>
          <li>Use a remote metastore backed by PostgreSQL or MySQL, back up that database, and run more than one metastore instance for availability.</li>
        </ul>''', '“Derby is fine because it is the default”: defaults are for testing.') +
    scn('Data engineering · automation', 'Mid-level', 'Running Hive from a scheduler',
        'You must run a nightly HiveQL report from Airflow and save the result as CSV.',
        'do you know Beeline’s scripting switches and failure handling?',
        '''<ol>
          <li>Put the SQL in a file and run <code>beeline -u &lt;url&gt; --silent=true --outputformat=csv2 --hivevar run_date={{ ds }} -f report.hql &gt; report.csv</code>.</li>
          <li>Rely on Beeline’s exit code: a failed statement returns non-zero, so the task fails and retries or alerts.</li>
          <li>Keep credentials out of the command line (use the scheduler’s connection store), and write large results to a table or files instead of streaming them through Beeline.</li>
        </ol>''', 'parsing the default table output with string tricks; use csv2.')
)
