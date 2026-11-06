import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def short(s):
    return s.replace('Error: Error while compiling statement: FAILED: ', 'FAILED: ')
BODY = body(HERE)

META = dict(
    module='10-administration-and-security', lesson='02-authorization-and-security', n='10.2',
    module_label='Module 10 · Administration and security',
    title='Authorization and security: SQL standard, Ranger and Kerberos',
    desc='Secure Hive with real Hive 4.2.1 outputs: enabling SQL-standard based authorization, the admin role and why the metastore must list admin users, roles, GRANT/REVOKE and SHOW GRANT, deny-by-default errors, a column-hiding view for analysts, blocked dfs, ADD JAR, TRANSFORM and CREATE TABLE, UPDATE needing the DELETE privilege in Hive 4, privileges stored in the metastore, and why authentication (Kerberos, LDAP) must come first. Ranger masking, row filters and audit explained.',
    og_desc='Our analyst was locked out of customer names, our engineer needed DELETE to UPDATE, and anyone could become admin. Hive 4.2.1 security, measured.',
    minutes=40, level='Intermediate → Advanced',
    lead='This lesson switches Hive’s built-in <b>SQL-standard authorization</b> on in our lab, gives TiffinGo’s analysts and engineers exactly the access they need, and collects every real error message along the way. It ends with the uncomfortable truth our lab shows: without <b>authentication</b> (Kerberos or LDAP), grants protect nothing. <b>All outputs are real</b>, from Hive 4.2.1; Ranger and Kerberos are explained, not run.',
    chips=['Real access-denied messages', 'Roles, grants and a safe view', 'Two Hive 4 surprises', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny SQL-standard authorizer: roles, grants, and a check at "compile time"
grants = {("ROLE", "analyst"): {("v_customers_safe", "SELECT"), ("orders", "SELECT")},
          ("USER", "kabir"): {("orders_tx", "SELECT"), ("orders_tx", "INSERT")}}
roles = {"riya": {"public", "analyst"}, "kabir": {"public"}}

def allowed(user, obj, priv):
    principals = [("USER", user)] + [("ROLE", r) for r in roles.get(user, {"public"})]
    return any((obj, priv) in grants.get(p, set()) for p in principals)

for user, obj, priv in [("riya", "v_customers_safe", "SELECT"), ("riya", "customers", "SELECT"),
                        ("kabir", "orders_tx", "INSERT"), ("kabir", "orders_tx", "DELETE")]:
    print(f"{user:6} {priv:6} {obj:17}", "OK" if allowed(user, obj, priv) else "Permission denied")
'''
RUN = dict(
    heading='Run the code: model the authorizer',
    intro='<p>These programs model how SQL-standard authorization decides, using the grants from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    principals = [("USER", user)] + [("ROLE", r) for r in roles.get(user, {"public"})]', 'A user’s effective privileges are their own grants plus those of every active role.'),
        ('    return any((obj, priv) in grants.get(p, set()) for p in principals)', 'One matching grant is enough; otherwise Hive raises HiveAccessControlException before running anything.'),
    ],
    tasks=[
        dict(label='1 · Check four requests', hint='Press <b>Run</b>. The results match the lab: the view yes, the base table no, INSERT yes, DELETE no.', code=None),
        dict(label='2 · Predict first: UPDATE in Hive 4', hint='<b>Predict first:</b> Hive 4 runs an ACID UPDATE as DELETE + INSERT. Which privileges are checked?',
             code='''needed = {"UPDATE": {"DELETE", "INSERT"}}       # as seen in the lab: DELETE was demanded
kabir = {"SELECT", "INSERT", "UPDATE"}
missing = needed["UPDATE"] - kabir
print("missing:", missing or "nothing")
'''),
        dict(label='3 · Revoke', hint='Remove Riya from the analyst role and check again, like REVOKE ROLE in Step 8.',
             code='''roles = {"riya": {"public", "analyst"}}
grants = {"analyst": {"v_customers_safe"}}
roles["riya"].discard("analyst")
ok = any("v_customers_safe" in grants.get(r, set()) for r in roles["riya"])
print("riya can read the view:", ok)
'''),
        dict(label='4 · Spoofed identity', hint='With authentication NONE the server believes the claimed name. Compare with a verified ticket.',
             code='''def who_is(claimed, auth, ticket_user=None):
    return claimed if auth == "NONE" else ticket_user
print("NONE     ->", who_is("hive", "NONE"))
print("KERBEROS ->", who_is("hive", "KERBEROS", ticket_user="riya"))
'''),
        dict(label='5 · Spot the error', hint='This access check lets everyone in the public role read customers. Fix the grant table.', expect='error',
             code='''grants = {"public": {"customers"}, "analyst": {"v_customers_safe"}}   # bug
assert "customers" not in grants["public"], "never grant base tables with personal data to public"
print("ok")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: grants in the metastore, and the UPDATE grant that was not enough',
    intro='<p>More evidence from the lab. <b>Outputs are real</b>.</p>',
    items=[
        dict(title='1 · Where grants are stored', cmd='-- psql on the metastore database\nSELECT t."TBL_NAME", p."PRINCIPAL_NAME", p."PRINCIPAL_TYPE", p."TBL_PRIV", p."GRANTOR"\nFROM "TBL_PRIVS" p JOIN "TBLS" t ON t."TBL_ID" = p."TBL_ID"\nWHERE p."PRINCIPAL_NAME" IN (\'analyst\', \'kabir\') ORDER BY 1, 2, 4;\nSELECT r."ROLE_NAME", m."PRINCIPAL_NAME", m."PRINCIPAL_TYPE"\nFROM "ROLE_MAP" m JOIN "ROLES" r ON r."ROLE_ID" = m."ROLE_ID";', file='psql · metastore_db',
             output=capf('l102_privs_db.txt'),
             note='Grants are metastore rows (TBL_PRIVS, DB_PRIVS, ROLE_MAP), so they are backed up with the metastore (Lesson 10.1) and visible to auditors. Riya no longer appears in ROLE_MAP after the REVOKE.'),
        dict(title='2 · UPDATE privilege alone was not enough', cmd="-- as hive:  GRANT UPDATE ON TABLE orders_tx TO USER kabir;\n-- as kabir:\nUPDATE orders_tx SET status = 'CANCELLED' WHERE order_id = 999000010;", file='Beeline · -n kabir',
             output=short(capf('l102_kabir_upd2.txt')),
             note='Still asking for DELETE. Only after GRANT DELETE did the update succeed (Step 7).'),
        dict(title='3 · The security settings in force', cmd='SET hive.server2.authentication;\nSET hive.server2.enable.doAs;\nSET hive.security.authorization.manager;\nSET hive.security.authenticator.manager;', file='Beeline · -n hive',
             output='\n'.join(re.sub(r'^\|\s*|\s*\|$', '', l) for l in capf('l102_authset.txt').split('\n') if '=' in l),
             note='Authorization on, authentication NONE: fine for learning, unacceptable in production.'),
    ],
)

TRACE = dict(
    heading='How a request is decided',
    intro='<p>Follow Riya’s query on the base table through the checks.</p>',
    code='''user = "riya"                              # from the session (authentication NONE)
active_roles = ["public", "analyst"]
needed = ("SELECT", "hive.tiffingo.customers")
granted = {("SELECT", "hive.tiffingo.v_customers_safe"), ("SELECT", "hive.tiffingo.orders")}
ok = needed in granted
print("Permission denied" if not ok else "OK")
''',
    notes={1: 'Identity :: Whatever name the client sent; Kerberos would prove it.', 3: 'Needed :: Hive derives required privileges from the query plan.', 5: 'Decision :: Before any task starts.'},
)

WORKED_INTRO = 'Three access designs from real platforms.'
EXAMPLES = [
    dict(level='b', tag='Analytics · access', title='Design roles for three teams',
         problem='<p>Write roles and grants for analysts, loaders and data scientists.</p>',
         inp='tables: customers (PII), orders, orders_tx; view v_customers_safe',
         approach=['One role per team.', 'Analysts: views only.', 'Loaders: write on their tables only.'],
         code='''plan = {
  "analyst":  ["SELECT ON v_customers_safe", "SELECT ON orders"],
  "loader":   ["SELECT, INSERT, UPDATE, DELETE ON orders_tx"],
  "ds":       ["SELECT ON v_customers_safe", "SELECT ON orders", "SELECT ON orders_tx"],
}
for role, grants in plan.items():
    for g in grants:
        print(f"GRANT {g.replace(' ON ', ' ON TABLE ')} TO ROLE {role};")
''', notes={3: 'Writers :: All three write privileges, because UPDATE needed DELETE in Hive 4.'},
         tryit='Then GRANT ROLE analyst TO USER riya; and so on, ideally from directory groups.'),
    dict(level='i', tag='Security · PII', title='Find tables exposing personal columns',
         problem='<p>From a column list, find tables with PII columns that a public-facing role can read.</p>',
         inp='columns and grants from the lab',
         approach=['List PII column names.', 'Match tables containing them.', 'Check which roles can SELECT.'],
         code='''pii = {"name", "phone", "email"}
tables = {"customers": {"customer_id", "name", "city"}, "v_customers_safe": {"customer_id", "city", "plan"}}
grants = {"analyst": {"v_customers_safe"}}
for role, objs in grants.items():
    for o in objs:
        print(role, o, "EXPOSES PII" if tables[o] & pii else "ok")
''', notes={4: 'Join :: Column metadata comes from the metastore (COLUMNS_V2).'},
         tryit='Our analyst role only reaches the safe view: no PII exposed.'),
    dict(level='a', tag='Architecture · platform', title='SQL standard or Ranger?',
         problem='<p>Decide for three organisations.</p>',
         inp='A: one Hive cluster, 20 users · B: Hive + Spark + Trino, 500 users, PII · C: AWS-only data lake',
         approach=['Single engine, few users → SQL standard.', 'Many engines, masking, audit → Ranger.', 'Cloud-native → the cloud catalogue’s permissions.'],
         code='''orgs = {"A": "SQL-standard GRANT/REVOKE + LDAP",
        "B": "Apache Ranger (masking, row filters, audit) + Kerberos",
        "C": "AWS Lake Formation permissions on the Glue catalog"}
for k, v in orgs.items():
    print(k, "->", v)
''', notes={3: 'Engines :: Ranger has plugins for Hive, HDFS, Kafka and more; SQL-standard grants only apply inside HiveServer2.'},
         tryit='Whatever the model, the first step is the same: real authentication.'),
]

QUIZ = mix([
    dict(q='Beginner: What is the difference between authentication and authorization?', options=['None', 'Authentication proves identity; authorization decides permitted actions', 'Authorization comes first', 'Both encrypt data'], answer=1,
         why='Who are you vs what may you do.'),
    dict(q='Beginner: Which role does every user have?', options=['admin', 'public', 'analyst', 'owner'], answer=1,
         why='Riya’s roles were analyst and public.'),
    dict(q='Beginner: How did analysts read customers without names?', options=['Column grants', 'A view without the name column, granted to their role', 'Encryption', 'Ranger'], answer=1,
         why='SQL-standard mode has no column grants; views do the job.'),
    dict(q='Intermediate: Why did SET ROLE ADMIN fail for hive at first?', options=['Wrong password', 'Admin membership is created by the metastore from its own hive.users.in.admin.role', 'Authorization was off', 'A bug'], answer=1,
         why='ROLE_MAP was empty until the metastore had the setting.'),
    dict(q='Intermediate: Which commands were blocked for a normal user?', options=['SELECT on the view', 'dfs, ADD JAR, TRANSFORM, changing security settings', 'SHOW CURRENT ROLES', 'Using a permanent UDF'], answer=1,
         why='They need the ADMIN PRIVILEGE or are disallowed.'),
    dict(q='Intermediate: Where are grants stored?', options=['In hive-site.xml', 'In metastore tables such as TBL_PRIVS and ROLE_MAP', 'In HDFS ACLs', 'In Beeline'], answer=1,
         why='Backed up with the metastore.'),
    dict(q='Advanced: Why did UPDATE need the DELETE privilege?', options=['A typo', 'Hive 4 executes ACID updates as delete + insert', 'UPDATE is not supported', 'Ranger was on'], answer=1,
         why='hive.split.update=true in the lab.'),
    dict(q='Advanced: Why was the lab still insecure with authorization on?', options=['No Ranger', 'Authentication NONE: anyone could connect as hive and SET ROLE ADMIN', 'doAs was false', 'No views'], answer=1,
         why='Use Kerberos or LDAP with TLS.'),
])

REVISION = [
    '<b>Authentication</b> (who): <code>hive.server2.authentication</code> NONE/LDAP/KERBEROS/PAM/CUSTOM + TLS. <b>Authorization</b> (what): SQL standard, storage-based, Ranger.',
    'SQL standard: <code>hive.security.authorization.enabled=true</code>, <code>SQLStdHiveAuthorizerFactory</code>, <code>SessionStateUserAuthenticator</code>, <code>doAs=false</code>.',
    'Admins: <code>hive.users.in.admin.role</code> must be set on the <b>metastore</b>; then <code>SET ROLE ADMIN</code> per session.',
    'Roles: <code>CREATE ROLE</code>, <code>GRANT ROLE r TO USER u</code>; privileges: <code>GRANT SELECT|INSERT|UPDATE|DELETE ON TABLE t TO ROLE r</code>; check with <code>SHOW GRANT</code>.',
    'Deny by default: HiveAccessControlException at compile time. View privileges suffice for views. No column grants: use views or Ranger masks.',
    'Blocked for users: dfs, ADD JAR, TRANSFORM, security SETs, CREATE TABLE without database ownership.',
    'Hive 4 UPDATE needs DELETE (+ INSERT) privileges. Grants live in TBL_PRIVS / ROLE_MAP.',
    '<b>Ranger</b>: central policies, column masking, row filters, tag policies, audit. <b>Kerberos/LDAP</b> first, or nothing is secure.',
]
FAQ = [
    ('Do Spark and Trino respect Hive’s SQL-standard grants?', 'No. Those grants are enforced inside HiveServer2. Spark reading the files or the metastore directly bypasses them. Platforms with several engines use Ranger plugins (or a cloud permission layer) and restrict direct file access.'),
    ('What does doAs do?', 'With doAs=true, HiveServer2 accesses files as the end user, so HDFS permissions decide; with doAs=false, it uses the Hive service user and the authorizer decides. SQL-standard authorization and Ranger expect doAs=false, with the warehouse readable only by the Hive user.'),
    ('How does Kerberos login work for Beeline?', 'The user runs kinit to get a ticket, then connects with a URL containing the server principal, e.g. <code>jdbc:hive2://hs2.example.com:10000/default;principal=hive/_HOST@EXAMPLE.COM</code>. No user name or password is typed; the ticket proves identity.'),
    ('Can I mask a column without Ranger?', 'With SQL-standard authorization, create a view that applies a function (e.g. <code>mask(phone)</code> or <code>concat(\'XXXXXX\', substr(phone, -4))</code>) and grant the view instead of the table. Ranger does this centrally without extra views.'),
    ('What about encryption?', 'Use TLS for client connections to HiveServer2 (<code>hive.server2.use.SSL</code>), HDFS transparent encryption zones or object-store encryption for data at rest, and secure the metastore database connection.'),
]

PRACTICE_INTRO = 'Programs that check and generate access rules, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Generate a GRANT', stmt='Write the GRANT for analysts on the safe view.', inp='role analyst, view v_customers_safe',
         code='''print("GRANT SELECT ON TABLE v_customers_safe TO ROLE analyst;")
''', explain='Exactly the statement used in Step 4.'),
    dict(level='easy', title='Effective roles', stmt='List Riya’s active roles.', inp='granted: analyst; built-in: public',
         code='''print(sorted({"public"} | {"analyst"}))
''', explain='SHOW CURRENT ROLES returned analyst and public.'),
    dict(level='easy', title='Missing privilege', stmt='Which privilege is missing for Kabir’s UPDATE?', inp='has SELECT, INSERT',
         code='''print({"DELETE", "INSERT"} - {"SELECT", "INSERT"})
''', explain='DELETE: the privilege named in the error.'),
    dict(level='medium', title='Parse an access error', stmt='Extract principal, privilege and object from a denial message.', inp='real error text',
         code='''import re
msg = "Principal [name=riya, type=USER] does not have following privileges for operation QUERY [[SELECT] on Object [type=TABLE_OR_VIEW, name=hive.tiffingo.customers]]"
print(re.search(r"name=(\\w+)", msg).group(1), re.search(r"\\[\\[(\\w+)\\]", msg).group(1), msg.rsplit("name=", 1)[1].rstrip("]"))
''', explain='Useful for summarising denials from logs.'),
    dict(level='medium', title='Masked phone', stmt='Show only the last four digits of a phone number.', inp="'9876543210'",
         code='''p = "9876543210"
print("X" * (len(p) - 4) + p[-4:])
''', explain="In a view: concat(repeat('X', length(phone) - 4), substr(phone, -4))."),
    dict(level='medium', title='Roles to revoke', stmt='Revoke roles of users who left.', inp='leavers and memberships',
         code='''members = {"riya": ["analyst"], "arun": ["analyst", "loader"]}
leavers = ["arun"]
for u in leavers:
    for r in members[u]:
        print(f"REVOKE ROLE {r} FROM USER {u};")
''', explain='Takes effect immediately, as Riya’s denied query after the REVOKE showed.'),
    dict(level='business', title='Exposure count', stmt='How many users could read names before the fix?', inp='all 120 Beeline users (illustrative)',
         code='''print("before:", 120, "  after:", 0, "(only admins via the base table)")
''', explain='With authorization off, every user could read every table.'),
    dict(level='business', title='Policy count', stmt='Views per team and region vs one Ranger row filter.', inp='4 teams × 8 cities (illustrative)',
         code='''print("views:", 4 * 8, " vs Ranger: 1 row-filter policy with a user attribute")
''', explain='Central policies scale better than many views.'),
]

SCN_INTRO = 'Security questions test whether you separate authentication from authorization and know the enterprise tools.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“How do you give a user access to a table?”',
        'Explain Hive’s GRANT model.',
        'do you know roles and privileges?',
        '<p>With SQL-standard authorization, an admin creates a role, grants privileges such as SELECT or INSERT on tables or views to the role, and grants the role to users. Users check their access with SHOW CURRENT ROLES and SHOW GRANT. In enterprise platforms the same is done with Ranger policies.</p>', 'Answering only with HDFS chmod.') +
    scn('Data platform', 'Mid-level', 'Hide personal columns',
        'Analysts must analyse customers without seeing names or phone numbers.',
        'can you combine views and grants, or masking?',
        '''<ol>
          <li>Create a view without (or masking) the personal columns.</li>
          <li>Grant SELECT on the view to the analyst role; no grant on the base table.</li>
          <li>With Ranger: a column masking policy instead of extra views; audit access.</li>
        </ol>''', '“Ask analysts not to select those columns.”') +
    scn('Data engineering', 'Mid-level', 'UPDATE permission denied',
        'A loader with INSERT and UPDATE privileges gets “does not have [DELETE]” on an UPDATE.',
        'do you know how Hive executes updates?',
        '''<ul>
          <li>Hive 4 runs ACID updates as delete + insert; authorization checks those operations.</li>
          <li>Grant DELETE (and INSERT) as well to the loader role.</li>
          <li>Review the privilege set for all writers.</li>
        </ul>''', 'Making the loader an admin.') +
    scn('Architecture', 'Senior', 'Securing a shared data lake',
        'Hive, Spark and Trino share one metastore; 500 users; personal data. Design security.',
        'can you design end-to-end security?',
        '''<ul>
          <li>Kerberos (or LDAP + TLS for BI) everywhere; doAs=false; warehouse files readable only by service users.</li>
          <li>Ranger policies for Hive, HDFS and Trino: masking, row filters, tag-based PII policies, audit.</li>
          <li>Roles from directory groups; regular access reviews; encryption in transit and at rest.</li>
        </ul>''', 'Relying on SQL-standard grants while Spark reads files directly.')
)
