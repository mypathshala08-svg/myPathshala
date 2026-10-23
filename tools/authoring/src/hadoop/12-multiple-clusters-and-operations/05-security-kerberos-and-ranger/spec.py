import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='05-security-kerberos-and-ranger', n='12.5',
    module_label='Module 12 · Multiple clusters and operations',
    title='Security: Kerberos and Ranger',
    desc='Hadoop security on a real lab: on an unsecured cluster HADOOP_USER_NAME=hadoop deletes a protected folder; then a real MIT Kerberos KDC and a Kerberos-secured NameNode: "Client cannot authenticate via:[TOKEN, KERBEROS]" without a ticket, kinit, klist, keytabs, the KDC log of AS_REQ and TGS_REQ, impersonation that no longer works, and an HDFS ACL. Apache Ranger policies, masking, tag policies and audit, wire and at-rest encryption, KMS, Knox and AD explained. Architecture diagram, two animations, Python Kerberos simulation, quiz and interview scenarios.',
    og_desc='One environment variable deleted a protected folder. Then we built a real Kerberos KDC, and it stopped working.',
    minutes=30, level='Intermediate',
    lead='A Hadoop cluster without Kerberos believes any user name a client claims. This lesson shows that on our lab, then builds a real Kerberos KDC and a secured NameNode, logs in with tickets, reads what the KDC recorded and adds an HDFS ACL. Apache Ranger, encryption and audit complete the picture of how companies protect payroll, patient and payment data.',
    chips=['Real KDC + secured NameNode', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a Kerberos login',
    intro='<p>A toy Kerberos with real ideas and fake cryptography: each principal has a secret key, tickets are “sealed” with the key of whoever must read them, and every ticket has an expiry time. Watch how riya gets into the NameNode and why an impostor cannot.</p>',
    code='''import hashlib
def key(secret):                                  # a "key" derived from a password or keytab
    return hashlib.sha256(secret.encode()).hexdigest()[:8]
def seal(k, data):  return {"sealed_with": k, "data": data}
def open_(k, box):
    if box["sealed_with"] != k:
        raise PermissionError("cannot decrypt: wrong key")
    return box["data"]

KDC = {"riya@LAB": key("riya123"), "krbtgt@LAB": key("kdc-secret"), "nn/nn-secure@LAB": key("from-keytab")}

def as_req(user, now):                           # 1. AS: password -> TGT
    tgt = seal(KDC["krbtgt@LAB"], {"user": user, "expires": now + 10})
    return seal(KDC[user], {"tgt": tgt})          # only the user's key opens the reply

def tgs_req(tgt, service, now):                   # 2. TGS: TGT -> service ticket
    t = open_(KDC["krbtgt@LAB"], tgt)
    if now > t["expires"]:
        raise PermissionError("TGT expired")
    return seal(KDC[service], {"user": t["user"], "expires": t["expires"]})

def namenode(ticket, claimed_name=None):          # 3. service: reads the user from the ticket
    t = open_(KDC["nn/nn-secure@LAB"], ticket)
    return f"NameNode sees user={t['user'].split('@')[0]} (claimed {claimed_name})"

reply = as_req("riya@LAB", now=0)
tgt = open_(key("riya123"), reply)["tgt"]         # riya types the right password
ticket = tgs_req(tgt, "nn/nn-secure@LAB", now=1)
print(namenode(ticket, claimed_name="nn"))
try:
    open_(key("wrongpass"), reply)
except PermissionError as e:
    print("wrong password:", e)
''',
    anno=[
        ('    return seal(KDC[user], {"tgt": tgt})          # only the user\'s key opens the reply', 'The KDC answers anyone, but the answer is sealed with the user\'s key. That is why a wrong password gave "Password incorrect" without the password crossing the network.'),
        ('    return seal(KDC[service], {"user": t["user"], "expires": t["expires"]})', 'A service ticket is sealed with the service\'s key, which the NameNode has in its keytab.'),
        ('    t = open_(KDC["nn/nn-secure@LAB"], ticket)', 'The NameNode takes the user from the ticket. The claimed name is ignored, as HADOOP_USER_NAME was in our lab.'),
    ],
    tasks=[
        dict(label='1 · A full login', hint='Press <b>Run</b>. Which key opens which box at each step?', code=None),
        dict(label='2 · Expired ticket', hint='<b>Predict first:</b> the TGT lasts 10 time units. Ask for a service ticket at time 12. What happens, and what does a real user do?',
             code='''def tgs(tgt_expires, now):
    if now > tgt_expires:
        return "TGT expired: run kinit again (or kinit -R if renewable)"
    return "service ticket issued"
for now in [1, 9, 12]:
    print(now, tgs(10, now))
'''),
        dict(label='3 · Map principals to users', hint='Apply simple auth_to_local rules: strip the realm for users, map nn/* to the user nn, and anything from another realm to nobody.',
             code='''def short_name(p, realm="LAB.MYPHATSHALA"):
    name, _, r = p.partition("@")
    if r != realm:
        return "nobody"
    return name.split("/")[0]                    # nn/nn-secure -> nn, riya -> riya
for p in ["riya@LAB.MYPHATSHALA", "nn/nn-secure@LAB.MYPHATSHALA", "kabir@OTHER.REALM"]:
    print(f"{p:32} -> {short_name(p)}")
'''),
        dict(label='4 · A Ranger-style policy check', hint='Evaluate allow and deny policies for users and groups on paths. Deny wins over allow; no matching policy means deny (our cluster then falls back to HDFS permissions, which we ignore here).',
             code='''policies = [
    {"path": "/finance", "groups": {"finance"}, "users": {"kabir"}, "access": {"read"}, "type": "allow"},
    {"path": "/finance/salaries", "groups": {"interns"}, "users": set(), "access": {"read"}, "type": "deny"},
]
groups = {"kabir": {"analysts"}, "riya": {"interns", "finance"}, "meera": {"finance"}}
def allowed(user, path, access):
    match = [p for p in policies if path.startswith(p["path"]) and access in p["access"]
             and (user in p["users"] or groups[user] & p["groups"])]
    if any(p["type"] == "deny" for p in match):
        return "DENIED (deny policy)"
    return "allowed" if match else "DENIED (no policy)"
for u, path in [("kabir", "/finance/q3.csv"), ("riya", "/finance/salaries"), ("meera", "/finance/salaries"), ("riya", "/hr/x")]:
    print(f"{u:6} {path:20} {allowed(u, path, 'read')}")
'''),
        dict(label='5 · Spot the error', hint='This NameNode trusts the name the client sends, like simple auth. Make it raise an error unless a valid ticket is given.',
             code='''def namenode(request):
    user = request.get("ticket_user") or request["claimed"]
    if user != "nn":
        raise PermissionError(f"Permission denied: user={user}")
    return "payroll contents"
print(namenode({"claimed": "nn"}))           # an impostor gets in!
print(namenode({"claimed": "riya"}))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

KER = 'lab/kerberos/'
PCRUN = dict(
    heading='Run it on your PC: a KDC, a secured NameNode and an ACL',
    intro='<p>Part 1 and Part 3 use the Module 8 lab. Part 2 needs the three containers in the <code>kerberos</code> folder: an Ubuntu KDC (it installs MIT Kerberos with apt the first time, so it needs internet), a NameNode with Kerberos switched on, and a client. Put the five files below in a folder called <code>kerberos</code>, with an empty <code>keytabs</code> subfolder, then run <code>docker compose -p lab12k up -d</code>, wait about two minutes and run <code>bash kerberos_lab.sh</code>. Our secure NameNode has no DataNodes, so the demo only creates empty files.</p>',
    items=[
        dict(title='The three containers', file='docker-compose.yaml',
             cmd=rd(KER + 'docker-compose.yaml') + '\n# ---- krb5.conf (same folder) ----\n' + '\n'.join('# ' + l for l in rd(KER + 'krb5.conf').strip().split('\n'))
                 + '\n# ---- config (same folder) ----\n' + '\n'.join('# ' + l for l in rd(KER + 'config').strip().split('\n')),
             output='$ docker compose -p lab12k up -d\n Container lab12k-nn-secure-1 Started\n$ docker logs lab12k-nn-secure-1 | grep -E "Login successful|listener on 8020"\nINFO  UserGroupInformation:1143 - Login successful for user nn/nn-secure@LAB.MYPHATSHALA using keytab file nn.keytab. Keytab auto renewal enabled : false\nINFO  Server:1618 - IPC Server listener on 8020: starting',
             note='Real lines (timestamps removed). The NameNode command waits until kinit with the keytab works, then formats and starts. Our first version let the image format at container start, before the keytab existed, and failed with "KerberosAuthException: failure to login … Unable to obtain password from user".'),
        dict(title='The KDC: realm, principals, keytab', file='kdc.sh',
             cmd=rd(KER + 'kdc.sh'),
             output='HTTP/nn-secure@LAB.MYPHATSHALA\nK/M@LAB.MYPHATSHALA\nkabir@LAB.MYPHATSHALA\nkadmin/admin@LAB.MYPHATSHALA\nkadmin/changepw@LAB.MYPHATSHALA\nkrbtgt/LAB.MYPHATSHALA@LAB.MYPHATSHALA\nnn/nn-secure@LAB.MYPHATSHALA\nriya@LAB.MYPHATSHALA\nKDC ready\nkrb5kdc: starting...',
             note='Real output of docker logs lab12k-kdc-1. krbtgt is the KDC\'s own principal (it seals every TGT); K/M is the master key.'),
        dict(title='Unsecured vs Kerberos vs ACL', file='kerberos_lab.sh',
             cmd=rd(KER + 'kerberos_lab.sh') + '\n# Run on your PC:  bash kerberos_lab.sh',
             output=rd('tx125.txt').strip(),
             note='Real output. The KDC log section shows the last 8 groups of requests, so it includes earlier runs of the script. Ranger is not part of this lab.'),
    ],
)

TRACE = dict(
    heading='Which key opens which ticket',
    intro='<p>Follow riya\'s login with three keys: hers, the KDC\'s and the NameNode\'s. Each step can only be opened by one of them.</p>',
    code='''keys = {"riya": "k_riya", "krbtgt": "k_kdc", "nn": "k_nn"}
reply = ("k_riya", ("k_kdc", "TGT for riya"))
tgt = reply[1] if reply[0] == keys["riya"] else None
service = ("k_nn", "riya") if tgt[0] == keys["krbtgt"] else None
user = service[1] if service[0] == keys["nn"] else None
print("NameNode accepts:", user)
''',
    notes={3: 'AS reply :: Opened with riya\'s key: only the right password gets the TGT.',
           4: 'TGS :: The KDC opens the TGT with its own key and issues a ticket sealed for the NameNode.',
           5: 'Service :: The NameNode opens it with the key in its keytab and reads the user name.'},
)

WORKED_INTRO = 'Four security design problems from different organisations: naming, mapping, policies and long jobs.'
EXAMPLES = [
    dict(level='b', tag='Naming · telecom', title='Name the principals for a new cluster',
         problem='<p>A telecom company adds a cluster with a NameNode on <code>nn1.blr.telco.in</code>, 2 workers (<code>w1</code>, <code>w2</code>, each a DataNode and a NodeManager) and a ResourceManager on <code>rm1</code>. Realm: <code>TELCO.IN</code>. List the service principals they need (ignore HTTP).</p>',
         inp='nn1, rm1, w1, w2 · realm TELCO.IN',
         approach=['One principal per service per host: service/host@REALM.',
                   'Workers run two services each.',
                   'Count them.'],
         code='''realm, dom = "TELCO.IN", "blr.telco.in"
services = {"nn1": ["nn"], "rm1": ["rm"], "w1": ["dn", "nm"], "w2": ["dn", "nm"]}
ps = [f"{s}/{h}.{dom}@{realm}" for h, ss in services.items() for s in ss]
print(len(ps), "principals"); print("\\n".join(ps))
''', notes={3: 'Pattern :: service/fully-qualified-host@REALM, one keytab per host.'},
         tryit='Add HTTP/host@REALM for every host that serves a web UI with SPNEGO. How many now?'),
    dict(level='i', tag='Mapping · university', title='Map principals to short names',
         problem='<p>A university\'s users log in as <code>roll123@STUDENTS.UNI.AC.IN</code> and staff as <code>name@STAFF.UNI.AC.IN</code>; the cluster realm is STAFF. HDFS home folders are <code>/user/&lt;short name&gt;</code>. Which short names do these principals get with “strip the realm for both realms, deny others”?</p>',
         inp='3 principals · 2 trusted realms',
         approach=['Split name and realm.',
                   'Accept the two trusted realms, strip the realm.',
                   'Everything else maps to nobody.'],
         code='''trusted = {"STUDENTS.UNI.AC.IN", "STAFF.UNI.AC.IN"}
for p in ["roll123@STUDENTS.UNI.AC.IN", "meera@STAFF.UNI.AC.IN", "eve@EVIL.ORG"]:
    name, realm = p.split("@")
    print(f"{p:30} -> {name if realm in trusted else 'nobody'}")
''', notes={3: 'auth_to_local :: Real rules look like RULE:[1:$1@$0](.*@STUDENTS\\.UNI\\.AC\\.IN)s/@.*//'},
         tryit='What goes wrong if a student and a staff member are both called meera? (One home folder, two people.)'),
    dict(level='i', tag='Policy design · hospital', title='ACLs or Ranger policies?',
         problem='<p>A hospital has 40 departments, each with a folder under /records, and 6 roles that need read access across several departments. Count the ACL entries needed if each role is added to each folder it needs (average 25 folders per role), versus Ranger policies written per role.</p>',
         inp='6 roles · 25 folders each',
         approach=['ACL: one entry per role per folder.',
                   'Ranger: one policy per role listing its folders.',
                   'Compare what must be reviewed.'],
         code='''roles, folders_per_role = 6, 25
print("ACL entries to manage   :", roles * folders_per_role)
print("Ranger policies to manage:", roles, "(each with a list of paths, audited centrally)")
''', notes={2: 'ACLs :: Each entry lives on a different folder, so nobody sees the whole picture.'},
         tryit='Now add the rule “only de-identified data for researchers”: ACLs cannot do column masking at all; Ranger can (in Hive).'),
    dict(level='a', tag='Long jobs · bank', title='A 30-hour job and 10-hour tickets',
         problem='<p>A bank\'s year-end reconciliation runs 30 hours. Tickets last 10 hours and are renewable for 7 days. HDFS delegation tokens last 24 hours unless renewed (renew interval) and at most 7 days. Which credentials expire during the job, and what keeps it alive?</p>',
         inp='job 30 h · TGT 10 h · token 24 h renew, max 7 d',
         approach=['The client TGT is only needed at submission.',
                   'Tasks use delegation tokens; the ResourceManager renews them.',
                   'Check the hard 7-day maximum.'],
         code='''job, tgt, token_renew, token_max = 30, 10, 24, 7 * 24
print("TGT expires during job:", job > tgt, "- harmless after submission")
renewals = job // token_renew
print(f"delegation token renewed {renewals} time(s) by the RM; max life OK: {job <= token_max}")
''', notes={3: 'Tokens :: Jobs carry delegation tokens, so tasks never need a Kerberos ticket.'},
         tryit='A streaming job that runs for 3 weeks breaks the 7-day maximum: such services log in from a keytab instead.'),
]

QUIZ = mix([
    dict(q='What does Hadoop do with the user name on a cluster without Kerberos?', options=['Checks it against LDAP', 'Trusts whatever the client sends, e.g. HADOOP_USER_NAME', 'Rejects unknown names', 'Asks for a password'], answer=1,
         why='In our lab HADOOP_USER_NAME=hadoop deleted /secure_demo.'),
    dict(q='What did the secured NameNode answer to a client without a ticket?', options=['Permission denied: user=dr.who', 'Client cannot authenticate via:[TOKEN, KERBEROS]', 'Safe mode is ON', 'File not found'], answer=1,
         why='The handshake needs a Kerberos ticket or a delegation token.'),
    dict(q='What does kinit obtain?', options=['A service ticket for every service', 'A ticket-granting ticket (TGT) from the KDC', 'A keytab', 'An HDFS delegation token'], answer=1,
         why='klist showed krbtgt/LAB.MYPHATSHALA, valid 10 hours.'),
    dict(q='Why did the KDC log show 4 TGS_REQ for riya?', options=['She typed 4 passwords', 'Each hdfs command asked for a NameNode service ticket', 'The KDC retried 4 times', 'One per DataNode'], answer=1,
         why='Each command is a new JVM, which keeps its service ticket only in memory.'),
    dict(q='What is a keytab?', options=['A list of ACLs', 'A file holding a principal\'s keys so a service can log in without a password', 'The KDC database', 'A Ranger policy'], answer=1,
         why='The NameNode logged in from /keytabs/nn.keytab.'),
    dict(q='What does the + in drwxr-x---+ mean?', options=['Sticky bit', 'The folder has an ACL', 'Encrypted', 'Snapshottable'], answer=1,
         why='We added user:kabir:r-x with setfacl.'),
    dict(q='Which component enforces a Ranger policy?', options=['Ranger Admin on every request', 'A plugin inside the service (NameNode, HiveServer2…)', 'The KDC', 'The client'], answer=1,
         why='Plugins cache policies and decide locally, then send audit events.'),
    dict(q='Which feature protects HDFS data on a stolen disk?', options=['Kerberos', 'Ranger', 'Encryption zones with a KMS', 'ACLs'], answer=2,
         why='Encryption at rest; the others control access through Hadoop.'),
])

REVISION = [
    'Four pillars: <b>authentication</b> (Kerberos), <b>authorization</b> (permissions, ACLs, Ranger), <b>audit</b>, <b>encryption</b> (wire and at rest).',
    'Simple auth trusts the client\'s user name: in our lab <code>HADOOP_USER_NAME=hadoop</code> deleted a 700 folder.',
    'Kerberos: AS_REQ → TGT (kinit), TGS_REQ → service ticket (<code>nn/host@REALM</code>), service decrypts with its <b>keytab</b>.',
    'Lab: no ticket → “Client cannot authenticate via:[TOKEN, KERBEROS]”; riya\'s ticket → files owned by riya; pretending does nothing.',
    '<b>auth_to_local</b> maps principals to short names; jobs use <b>delegation tokens</b>, renewed by the RM.',
    'ACL: <code>hdfs dfs -setfacl -m user:kabir:r-x</code>; Ranger: central resource/tag policies, masking, row filters, audit.',
    'Production: AD as KDC, keytabs locked down, clocks synced (5 min skew), RPC privacy, encryption zones + KMS, Knox.',
]
FAQ = [
    ('Why is Kerberos needed in Hadoop?', 'Without it Hadoop uses simple authentication: the client\'s user name (from the OS or HADOOP_USER_NAME) is trusted, so anyone with network access can act as any user, including the HDFS superuser. Kerberos makes every user and service prove its identity with tickets from a KDC, so permissions, ACLs and Ranger policies apply to the real person.'),
    ('How does Kerberos authentication work in Hadoop?', 'The user runs kinit and the KDC\'s Authentication Service returns a ticket-granting ticket sealed with a key derived from the password. The client then asks the Ticket-Granting Service for a service ticket for a Hadoop service such as nn/host@REALM, and presents it to that service, which decrypts it with the key in its keytab. Jobs then use Hadoop delegation tokens so tasks do not contact the KDC.'),
    ('What is Apache Ranger?', 'A central authorization and audit framework for the Hadoop ecosystem. Administrators define policies in Ranger Admin (by user, group, resource or Atlas tag); plugins inside HDFS, Hive, HBase, YARN, Kafka and others download the policies, enforce them locally and send audit events to Solr or HDFS. Ranger also supports column masking and row filtering for Hive.'),
    ('What is the difference between HDFS ACLs and Ranger?', 'ACLs are stored on each file or directory in the NameNode and only cover HDFS. Ranger policies are defined centrally, can cover many paths and services with one policy, support groups from LDAP/AD, tags, masking and row filters, and keep a searchable audit of every decision.'),
    ('What is a keytab and why is it sensitive?', 'A keytab stores a principal\'s long-term keys so a service (or a scheduled job) can log in to Kerberos without typing a password. Anyone who can read it can act as that principal until the keys are changed, so keytabs must be readable only by the service user, kept out of source control and rotated.'),
]

PRACTICE_INTRO = 'Security exercises built on the real messages and settings from our lab.'
PROBLEMS = [
    dict(level='easy', title='Read a principal', stmt='Split nn/nn-secure@LAB.MYPHATSHALA into service, host and realm.', inp='one principal',
         code='''p = "nn/nn-secure@LAB.MYPHATSHALA"
name, realm = p.split("@"); service, host = name.split("/")
print(service, host, realm)
''', explain='nn (the NameNode service), host nn-secure, realm LAB.MYPHATSHALA.'),
    dict(level='easy', title='Ticket expiry', stmt='riya\'s TGT was valid from 10:08:23 for 10 hours. When does it expire?', inp='10:08:23 + 10 h',
         code='''from datetime import datetime, timedelta
print((datetime(2026, 10, 22, 10, 8, 23) + timedelta(hours=10)).time())
''', explain='20:08:23, exactly what klist showed.'),
    dict(level='easy', title='Read the permission bits', stmt='/payroll is drwx------ owned by nn. Which of owner, group and others may enter it?', inp='drwx------',
         code='''bits = "rwx------"
for who, part in zip(["owner", "group", "others"], [bits[0:3], bits[3:6], bits[6:9]]):
    print(who, "can enter" if part[2] == "x" else "cannot enter")
''', explain='Only the owner nn; riya needed EXECUTE on the folder, hence access=EXECUTE in the error.'),
    dict(level='medium', title='Effective ACL rights with a mask', stmt='The mask limits named users and groups. With user:kabir:rwx but mask::r-x, what can kabir do?', inp='rwx AND r-x',
         code='''def eff(entry, mask):
    return "".join(e if (e != "-" and m != "-") else "-" for e, m in zip(entry, mask))
print("kabir effective:", eff("rwx", "r-x"))
''', explain='r-x: the mask removes write, which is why getfacl shows the mask line.'),
    dict(level='medium', title='Count KDC traffic', stmt='Each hdfs command is a new JVM that asks for a service ticket. 500 analysts each run 40 commands a day. How many TGS requests? How many AS requests if each logs in twice?', inp='500 × 40 · 500 × 2',
         code='''print("TGS:", 500 * 40, "AS:", 500 * 2)
''', explain='20,000 TGS and 1,000 AS requests a day: why big companies run several KDCs (or AD domain controllers).'),
    dict(level='medium', title='Clock skew', stmt='Kerberos rejects tickets if clocks differ by more than 5 minutes. Which servers fail?', inp='offsets in seconds',
         code='''offsets = {"nn1": 12, "w1": -40, "w2": 410, "edge1": -305}
print([h for h, s in offsets.items() if abs(s) > 300])
''', explain='w2 and edge1: “Clock skew too great”. Run NTP or chrony everywhere.'),
    dict(level='business', title='Cost of not securing', stmt='One accidental or malicious delete of a 40 TB folder takes 3 engineers 5 days to restore from DR (₹8,000 per engineer-day) plus a day of lost analytics for 200 users (₹2,000 each). Compare with a 2-week Kerberos + Ranger project for 2 engineers.', inp='illustrative costs',
         code='''incident = 3 * 5 * 8000 + 200 * 2000
project = 2 * 10 * 8000
print(f"one incident Rs {incident:,} vs project Rs {project:,}")
''', explain='₹5.2 lakh for one incident vs ₹1.6 lakh (illustrative), before counting audit findings or leaked data.'),
    dict(level='advanced', title='Simulate impersonation attempts', stmt='For each request, decide what a simple-auth and a Kerberos cluster believe the user is.', inp='3 requests',
         code='''reqs = [{"claimed": "hadoop", "ticket": None}, {"claimed": "nn", "ticket": "riya"}, {"claimed": None, "ticket": "kabir"}]
for r in reqs:
    simple = r["claimed"] or "os-user"
    kerberos = r["ticket"] or "REJECTED"
    print(f"claimed={r['claimed']!s:6} ticket={r['ticket']!s:5} simple->{simple:7} kerberos->{kerberos}")
''', explain='Simple auth believes the claim; Kerberos only the ticket, and rejects requests without one.'),
]

SCN_INTRO = 'Security questions come up in Hadoop admin, data engineering and platform interviews, usually with a story.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · Kerberos</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Explain Kerberos in Hadoop in two minutes”</h4>
      <p class="scn__situation">A standard opening question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the three exchanges and why Hadoop needs it.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Without Kerberos, Hadoop trusts the user name the client sends; anyone can be the superuser.</li>
          <li>kinit → TGT from the AS; TGT → service ticket for nn/host@REALM from the TGS; the NameNode decrypts it with its keytab.</li>
          <li>Jobs get delegation tokens at submission so tasks don't hit the KDC; the RM renews them.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Troubleshooting · GSS</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>All jobs on one worker fail with “GSS initiate failed”</h4>
      <p class="scn__situation">Other workers are fine; nothing was deployed.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> a methodical Kerberos checklist.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check the clock (more than 5 minutes of skew), forward and reverse DNS of the host, and that the keytab's KVNO matches the KDC (klist -kt).</li>
          <li>Try kinit -kt with the service keytab on that host; enable sun.security.krb5.debug=true for the details.</li>
          <li>Check krb5.conf (realm, KDC address, allowed encryption types) against the working workers.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · Ranger</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Analysts need customer data, but not phone numbers</h4>
      <p class="scn__situation">An e-commerce company must restrict PII without blocking reports.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> masking, tags and audit, not more copies.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Tag PII columns in Atlas; one Ranger tag policy masks them (hash or last 4 digits) for analysts, clear for an approved group.</li>
          <li>Row-level filters if analysts should see only their region.</li>
          <li>Keep HDFS paths of the raw tables closed to analysts so they cannot bypass Hive; review Ranger audit monthly.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Basics · permissions</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Our folder is 700, so it's secure, right?”</h4>
      <p class="scn__situation">A teammate on an unsecured cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you know permissions need authentication.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Not on simple auth: anyone can set HADOOP_USER_NAME to the owner's name, as our lab showed with a delete.</li>
          <li>Permissions protect against mistakes; against people you need Kerberos (and a firewall around the cluster).</li>
          <li>Then add Ranger for central policies and audit, and encryption for data at rest.</li>
        </ul>
      </div></details>
    </article>
'''
