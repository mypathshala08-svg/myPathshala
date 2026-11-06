import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
ADM = os.path.join(HERE, '..', '..', 'lab', 'admin') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def short(s):
    """Shorten the long Hive error prefix."""
    return s.replace('Error: Error while compiling statement: FAILED: ', 'FAILED: ').replace('Error: Error while processing statement: ', 'FAILED: ')
def setl(n):
    return '\n'.join(re.sub(r'^\|\s*|\s*\|$', '', l) for l in capf(n).split('\n') if '=' in l and l.startswith('|'))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(12, 20, '1 · Authentication', 'who are you?', 'blue', 180, 32) + opbox(12, 62, '2 · Authorization', 'what may you do?', 'violet', 180, 32) + opbox(12, 104, '3 · Audit and encryption', 'what did you do?', 'green', 180, 32) +
      arrow(196, 78, 236, 78, 'acc', 2.2) +
      box(240, 12, 390, 128, 'card') + t(435, 30, 'TiffinGo, after this lesson', 8.8, bold=True) +
      ''.join(t(256, 52 + k * 17, s, 7.4, c, anchor='start', mono=True) for k, (s, c) in enumerate([("riya (analyst): v_customers_safe ✓   customers ✗", 'ink'), ('riya: dfs, ADD JAR, TRANSFORM ✗', 'ink'), ('kabir (engineer): INSERT ✓   UPDATE needs DELETE', 'ink'), ('hive (admin): SET ROLE ADMIN', 'ink'), ('authentication NONE: anyone can say “hive” ✗', 'red')])))
scene_svg = scene('Security has three layers: authentication, authorization, and audit with encryption. In the lab, the analyst could read only a safe view, the engineer could insert but needed DELETE to update, and with authentication off anyone could claim to be the admin.', sc,
                  'Authorization without authentication is a <tspan font-weight="700" class="s-acc">lock without a door</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Analysts can see customers’ names”</h2>
  <div class="story">
    <p class="narration">An internal audit at TiffinGo found that every Beeline user can read every table, including customer names. Riya’s analysts should see cities and plans, not names; Kabir’s loaders should write orders, not drop tables. Arjun Sir has a week to fix it.</p>

{scene_svg}

R> Sir, can’t we just make a view without the names and tell analysts to use it?
A> Telling is not enforcing. Hive needs <b>authorization</b>: rules about who may SELECT, INSERT, UPDATE or DELETE on which table or view. The built-in option is <b>SQL-standard based authorization</b> with GRANT, REVOKE and roles. Large platforms use <b>Apache Ranger</b> for central policies, column masking and audit.
K> And how does Hive know that I am Kabir?
A> That is <b>authentication</b>: Kerberos or LDAP in production. We will switch authorization on in our lab, build roles, collect the real error messages, discover two surprises, and then show why our lab, with authentication set to NONE, is still not secure. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Hive security at three levels
L1> A building with guards
      <ul>
        <li><b>Authentication</b> is the ID card at the entrance: proving who you are.</li>
        <li><b>Authorization</b> is which rooms your card opens: what you may read or change.</li>
        <li><b>Audit</b> is the visitor log: who entered which room, and when.</li>
      </ul>
L2> The options in Hive
      <ul>
        <li><b>Authentication</b> (HiveServer2): <code>hive.server2.authentication</code> = NONE, LDAP, KERBEROS, PAM, CUSTOM; plus TLS for the connection.</li>
        <li><b>Authorization</b>: SQL-standard based (GRANT/REVOKE, roles <code>public</code> and <code>admin</code>), storage-based (file permissions), or Apache Ranger (central policies, masking, row filters, audit).</li>
        <li><b>doAs</b>: with <code>hive.server2.enable.doAs=false</code> queries access files as the Hive service user, which is required for SQL-standard and Ranger authorization to be meaningful.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Listing <code>hive</code> in <code>hive.users.in.admin.role</code> on HiveServer2 was not enough: “hive doesn’t belong to role admin” until the <b>metastore</b> had the setting too.</li>
        <li>Analysts were blocked from dfs, ADD JAR, TRANSFORM, CREATE TABLE and from switching authorization off; a permanent UDF still worked.</li>
        <li>UPDATE on an ACID table asked for the <b>DELETE</b> privilege (Hive 4 splits updates into delete + insert). With authentication NONE, anyone typing <code>-n hive</code> became admin.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Authentication, authorization and Hive security</h2>
''' + def_block(
    '<b>Authentication</b> establishes the identity of a client connecting to HiveServer2 (Kerberos, LDAP, PAM, custom providers, or none). <b>Authorization</b> decides which operations that identity may perform. Hive’s <b>SQL-standard based authorization</b> (<code>SQLStdHiveAuthorizerFactory</code>) enforces SELECT, INSERT, UPDATE and DELETE privileges and object ownership on databases, tables and views, managed with GRANT, REVOKE and roles, and disables risky commands (dfs, ADD JAR, TRANSFORM, changing security settings) for non-admin users. <b>Apache Ranger</b> replaces it in most enterprise platforms with centrally managed policies, column masking, row-level filtering and audit logs, while <b>Kerberos</b> secures identities across Hadoop services.',
    'Authentication answers “who are you?”, authorization answers “what are you allowed to do?”. Hive can enforce table permissions with GRANT and REVOKE, or with Apache Ranger policies, but both only work if users are properly authenticated, usually with Kerberos or LDAP.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Principal', 'A user, group or role that receives privileges.'),
    ('Role', 'A named set of privileges; public and admin are built in.'),
    ('Privilege', 'SELECT, INSERT, UPDATE, DELETE, ALL on an object.'),
    ('Ownership', 'Creator of an object; needed e.g. to create tables in a database.'),
    ('doAs', 'Run file access as the end user (true) or the Hive service user (false).'),
    ('Kerberos', 'Ticket-based authentication used across Hadoop.'),
    ('Ranger', 'Central policy, masking, row-filter and audit service.'),
    ('Column masking', 'Showing a transformed value (e.g. ****) instead of the real one.'),
]) + '''

  <h3>Authorization models</h3>
''' + table(['Model', 'How rules are defined', 'Granularity', 'Typical use'], [
    ['SQL-standard based (built in)', 'GRANT / REVOKE, roles in the metastore', 'Database, table, view', 'Hive-only clusters, learning'],
    ['Storage-based', 'HDFS / object-store permissions on folders', 'Directory', 'Metastore-level protection, Hive CLI era'],
    ['Apache Ranger', 'Policies in Ranger Admin, plugins in HiveServer2 (and HMS)', 'Column, row filter, masking, tags', 'Enterprise platforms (Cloudera)'],
    ['Cloud IAM / Lake Formation', 'Cloud catalog permissions', 'Table, column, row', 'AWS, Azure, GCP (Lesson 11.2)'],
], minw=720) + lv + '''
EXAM> “How do you secure Hive?” Authenticate users at HiveServer2 (Kerberos or LDAP, with TLS), authorize with SQL-standard GRANT/REVOKE and roles or with Ranger policies (column masking, row filters, audit), set doAs=false so access goes through the authorizer, and expose sensitive data through views or masks.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>SQL-standard authorization commands</h2>
''' + table(['Command', 'Who', 'Purpose'], [
    ['<code>SET ROLE ADMIN;</code>', 'Members of admin', 'Activate admin privileges for the session'],
    ['<code>CREATE ROLE r; DROP ROLE r; SHOW ROLES;</code>', 'Admin', 'Manage roles'],
    ['<code>GRANT ROLE r TO USER u; REVOKE ROLE r FROM USER u;</code>', 'Admin', 'Membership'],
    ['<code>GRANT SELECT, INSERT ON TABLE t TO ROLE r [WITH GRANT OPTION];</code>', 'Owner / admin', 'Privileges on tables and views'],
    ['<code>REVOKE SELECT ON TABLE t FROM ROLE r;</code>', 'Grantor / admin', 'Remove privileges'],
    ['<code>SHOW CURRENT ROLES; SHOW ROLE GRANT USER u;</code>', 'Anyone (own) / admin', 'Check membership'],
    ['<code>SHOW GRANT [USER u | ROLE r] ON TABLE t;</code>', 'Anyone (own) / admin', 'Check privileges'],
], minw=720) + '''
WARN> In SQL-standard mode there are <b>no column-level grants</b>. Hide columns with views (as here) or use Ranger’s column policies and masking. And because Hive checks privileges on the <b>view</b>, analysts can read a view without any privilege on its base table.
</section>
'''

AUTH = open(ADM + 'auth.yml').read().rstrip()
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Switching authorization on, role by role</h2>
  <p>All outputs are real, from Hive 4.2.1. Users connect with <code>beeline -n riya</code>, <code>-n kabir</code> or <code>-n hive</code>. Long error prefixes are shortened to “FAILED:”.</p>
''' + stepper([
    ('Step 1 · Turn authorization on',
     code('yaml', 'auth.yml (docker compose override)', AUTH),
     'HiveServer2 gets four settings: authorization enabled, the SQL-standard authorizer, an authenticator that takes the session user name, and <code>hive.users.in.admin.role=hive</code>. <code>doAs=false</code> makes HiveServer2 read files as its own service user, so the authorizer, not file permissions, decides. In a real cluster these lines go into <code>hive-site.xml</code>.'),
    ('Step 2 · Surprise: the admin role lives in the metastore',
     code('sql', 'Beeline · -n hive', "SET hive.security.authorization.enabled;\nSHOW CURRENT ROLES;\nSET ROLE ADMIN;\n\n-- after adding -Dhive.users.in.admin.role=hive to the METASTORE too and restarting it:\nSET ROLE ADMIN;\nSHOW CURRENT ROLES;", short(capf('l102_noadmin.txt')) + '\n\n' + capf('l102_admin_ok.txt')),
     'Roles and memberships are stored in the metastore (<code>ROLES</code>, <code>ROLE_MAP</code>). The metastore adds the users of <code>hive.users.in.admin.role</code> to the admin role from <b>its own</b> configuration; with the setting only on HiveServer2, <code>ROLE_MAP</code> stayed empty and <code>SET ROLE ADMIN</code> failed. Even admins start every session in the <code>public</code> role and must <code>SET ROLE ADMIN</code> explicitly.'),
    ('Step 3 · Deny by default',
     code('sql', 'Beeline · -n riya', 'SELECT COUNT(*) FROM customers;', short(capf('l102_denied.txt'))),
     'With authorization on, a new user has only the <code>public</code> role and no privileges: the query is refused at <b>compile time</b>, naming the principal, the missing privilege and the object (<code>hive.tiffingo.customers</code>: catalog, database, table).'),
    ('Step 4 · A safe view, a role and grants',
     code('sql', 'Beeline · -n hive', "SET ROLE ADMIN;\nCREATE OR REPLACE VIEW v_customers_safe AS SELECT customer_id, city, plan, joined_on FROM customers;\nCREATE ROLE analyst;\nGRANT SELECT ON TABLE v_customers_safe TO ROLE analyst;\nGRANT SELECT ON TABLE orders TO ROLE analyst;\nGRANT ROLE analyst TO USER riya;\nSHOW ROLE GRANT USER riya;\nSHOW GRANT ROLE analyst ON TABLE v_customers_safe;", capf('l102_setup.txt')),
     'The view drops <code>name</code>, the personal column. Privileges go to the <b>role</b>, and people join roles: when Riya’s team grows, nobody touches table grants. <code>SHOW GRANT</code> lists who has what, with grantor and time, which is handy for access reviews.'),
    ('Step 5 · The analyst’s view of the world',
     code('sql', 'Beeline · -n riya', "SHOW CURRENT ROLES;\nSELECT city, COUNT(*) AS customers FROM v_customers_safe GROUP BY city ORDER BY customers DESC LIMIT 3;\nSELECT name FROM customers LIMIT 1;", '\n'.join(l for l in capf('l102_riya.txt').split('\n') if l.strip()).split('Error')[0].rstrip() + '\n' + short('Error' + capf('l102_riya.txt').split('Error', 1)[1].split('\n')[0])),
     'Riya’s session has <code>analyst</code> and <code>public</code>. She can aggregate through the view (Mumbai 405 customers) even though she has <b>no privilege on the base table</b>: Hive checks the view. A direct query for names is denied.'),
    ('Step 6 · What non-admin users cannot do',
     code('sql', 'Beeline · -n riya', "INSERT INTO orders_tx VALUES (…);\ndfs -ls /;\nADD JAR /data/udf/tiffingo-udf.jar;\nSET hive.security.authorization.enabled=false;\nSET ROLE ADMIN;\nCREATE TABLE riya_scratch (x INT);\nSELECT TRANSFORM (order_id) USING 'cat' AS (x) FROM orders LIMIT 1;\nSELECT tiffingo.normalize_city('  bombay ') AS city;      -- permanent UDF from Lesson 9.1", short(capf('l102_denials.txt')) + '\n' + 'riya> CREATE TABLE riya_scratch (x INT);\n' + short(capf('l102_create.txt')) + '\nriya> SELECT TRANSFORM …\n' + short(capf('l102_transform.txt')) + '\nriya> SELECT tiffingo.normalize_city(…)\n' + capf('l102_udf.txt')),
     'Every escape hatch is closed: writing without INSERT, file-system commands and ADD JAR need the <b>ADMIN PRIVILEGE</b>, security settings cannot be changed at run time, admin cannot be self-assigned, creating tables needs <b>ownership</b> of the database, and TRANSFORM is disallowed (Lesson 9.3). Permanent functions registered by an admin remain usable.'),
    ('Step 7 · Write privileges, and a Hive 4 surprise',
     code('sql', 'Beeline · -n hive, then -n kabir', "-- hive:  GRANT SELECT, INSERT ON TABLE orders_tx TO USER kabir;  SHOW GRANT USER kabir ON TABLE orders_tx;\n-- kabir: INSERT INTO orders_tx VALUES (999000010, 7, 'Pune', 10.00, DATE '2026-10-29', 'NEW');\n--        SELECT COUNT(*) FROM orders_tx WHERE order_id = 999000010;\n-- kabir: UPDATE orders_tx SET status = 'CANCELLED' WHERE order_id = 999000010;\n-- hive:  GRANT UPDATE ON TABLE orders_tx TO USER kabir;     → kabir's UPDATE still fails\n-- hive:  GRANT DELETE ON TABLE orders_tx TO USER kabir;     → kabir's UPDATE works", capf('l102_kabir_grant.txt') + '\n' + capf('l102_kabir_ins.txt') + '\n' + short(capf('l102_kabir_upd.txt')) + '\n\n-- after UPDATE + DELETE grants:\n' + capf('l102_kabir_upd3.txt')),
     'Kabir could insert and check his row. His UPDATE was refused for missing <b>DELETE</b>, and still refused after an UPDATE grant. Hive 4 executes ACID updates as delete + insert (<code>hive.split.update=true</code> in our lab), and authorization checks those operations. Grant writers INSERT, UPDATE and DELETE together on tables they maintain.'),
    ('Step 8 · Why authentication matters',
     code('sql', 'Beeline · anyone, typing -n hive', "SET hive.server2.authentication;              -- NONE in our lab\nSET ROLE ADMIN;\nSELECT current_user() AS who, COUNT(*) AS customers FROM customers;\n\n-- clean-up: REVOKE ROLE analyst FROM USER riya;  then riya queries the view again", setl('l102_authset.txt').split('\n')[0] + '\n\n' + capf('l102_spoof.txt') + '\n\n' + capf('l102_revoke.txt') + '\n' + short(capf('l102_after.txt'))),
     'With <code>hive.server2.authentication=NONE</code>, HiveServer2 believes any user name a client sends. Anyone who types <code>-n hive</code> becomes admin and reads all 2,000 customers. Every grant above is only as strong as authentication: production clusters use <b>Kerberos</b> or <b>LDAP</b> (with TLS). Revoking the role took effect at once: Riya’s next query on the view was denied.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('SET ROLE ADMIN;', W), ("hive doesn't belong to role admin", RD), ('(metastore setting added, restarted)', W), ('SET ROLE ADMIN;  → admin', G)], size=7.6),
    term([('riya> SELECT … FROM customers', W), ('HiveAccessControlException', RD), ('  does not have [SELECT] on', RD), ('  hive.tiffingo.customers', RD)], size=7.6),
    term([('GRANT SELECT ON v_customers_safe TO ROLE analyst', W), ('GRANT ROLE analyst TO USER riya', W), ('riya> … FROM v_customers_safe', W), ('Mumbai 405 · Bengaluru 377 · Pune 316', G)], size=7.2),
    term([('kabir> INSERT … → 1 row', G), ('kabir> UPDATE …', W), ('  does not have [DELETE] on orders_tx', RD), ('GRANT UPDATE → still fails', Y), ('GRANT DELETE → CANCELLED', G)], size=7.4),
    term([('hive.server2.authentication=NONE', Y), ('anyone> beeline -n hive', W), ('SET ROLE ADMIN;  → ok', RD), ('who = hive · customers = 2000', RD)], size=7.6),
]
def flow(hi):
    o = ''
    for k, (a, b, tone) in enumerate([('Client', 'beeline -n …', 'card'), ('Authenticate', 'LDAP · Kerberos', 'blue'), ('Authorize', 'SQL std / Ranger', 'violet'), ('Execute', 'as service user', 'green')]):
        o += opbox(8 + k * 88, 54, a, b, 'acc' if k == hi else tone, 82, 30)
        if k:
            o += arrow(8 + k * 88 - 6, 69, 8 + k * 88, 69, 'ink3', 1.6)
    return o
B1 = [
    t(180, 22, 'Roles live in the metastore', 9.4, bold=True) + flow(2) + t(180, 112, 'ROLES · ROLE_MAP · TBL_PRIVS', 8.2, 'ink', mono=True) + cap('Admin members come from the metastore config.', '', 'amber', y=140, h=34),
    t(180, 22, 'Checked at compile time', 9.4, bold=True) + flow(2) + cap('No privilege, no plan, no task.', '', 'blue', y=140, h=34),
    t(180, 22, 'Grant to roles, add people to roles', 9.4, bold=True) + flow(2) + t(180, 112, 'view privilege is enough', 8.2, 'green', mono=True) + cap('Views hide columns; base table stays closed.', '', 'green', y=140, h=34),
    t(180, 22, 'Operations, not statements', 9.4, bold=True) + flow(2) + t(180, 112, 'UPDATE = DELETE + INSERT', 8.2, 'ink', mono=True) + cap('Grant all write privileges to writers.', '', 'amber', y=140, h=34),
    t(180, 22, 'No authentication, no security', 9.4, bold=True) + flow(1) + cap('Kerberos or LDAP + TLS in production.', '', 'amber', y=140, h=34),
]
see_caps = ['The admin role needed the setting on the metastore too.',
            'Without grants, Riya was denied.',
            'Through a role and a view, Riya could analyse without names.',
            'UPDATE needed the DELETE privilege.',
            'With authentication NONE, anyone could become admin.']
behind_caps = ['Roles and grants are metastore data.',
               'The authorizer checks privileges during compilation.',
               'Hive checks privileges on the view, not its base tables.',
               'Hive 4 splits ACID updates into delete and insert.',
               'HiveServer2 trusted the user name the client sent.']
two = anim_two('Authorization', 'Who may do what', 'Real lab outputs', 'How Hive decides', see, B1, see_caps, behind_caps)

# ---- scenario 1: Ranger masking
r1 = (t(180, 22, 'Analysts need phone numbers, partly', 9.4, bold=True) + t(180, 56, 'last 4 digits only, for support calls', 8.4, 'ink2') + cap('A view per variation does not scale.', '', 'blue', y=150, h=34))
r2 = (t(180, 22, 'Ranger column masking', 9.4, bold=True) + t(180, 56, 'policy: phone → show last 4 for group support', 8, 'ink', mono=True) + cap('Same table, different results per user.', '', 'green', y=150, h=34))
r3 = (t(180, 22, 'Row filters', 9.4, bold=True) + t(180, 56, "city managers: WHERE city = 'Pune'", 8.2, 'ink', mono=True) + cap('Applied automatically by the plugin.', '', 'green', y=150, h=34))
r4 = (t(180, 22, 'Tag-based policies', 9.4, bold=True) + t(180, 56, 'columns tagged PII in Atlas → masked everywhere', 8, 'ink2') + cap('Classify once, protect everywhere.', '', 'violet', y=150, h=34))
r5 = (t(180, 22, 'Audit', 9.4, 'acc', bold=True) + t(180, 56, 'every allowed and denied access logged', 8.2, 'ink2') + cap('Answers the auditor’s questions.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Column masking and row filters with Ranger',
              'What enterprise platforms add on top of GRANT/REVOKE. (Typical Ranger setup; not run in our lab.)',
              'Ranger policies', 'Ranger masks columns, filters rows and audits access through central policies, instead of many views', [r1, r2, r3, r4, r5],
              ['Partial access is needed.',
               'Masking shows only part of a value.',
               'Row filters limit rows per group.',
               'Tags drive policies.',
               'Every access is audited.'],
              hid='scenario-ranger')

# ---- scenario 2: Kerberos
k1 = (t(180, 22, 'Securing the lab properly', 9.4, bold=True) + t(180, 56, 'authentication NONE → anyone is “hive”', 8.4, 'red') + cap('As shown in Step 8.', '', 'amber', y=150, h=34))
k2 = (t(180, 22, 'Kerberos', 9.4, bold=True) + t(180, 56, 'hive.server2.authentication=KERBEROS', 8.2, 'ink', mono=True) + cap('Users run kinit; HiveServer2 has a keytab.', '', 'green', y=150, h=34))
k3 = (t(180, 22, 'JDBC URL changes', 9.4, bold=True) + t(180, 56, 'jdbc:hive2://hs2:10000/;principal=hive/_HOST@REALM', 7.6, 'ink', mono=True) + cap('No more -n user: the ticket proves identity.', '', 'green', y=150, h=34))
k4 = (t(180, 22, 'Or LDAP for BI tools', 9.4, bold=True) + t(180, 56, 'hive.server2.authentication=LDAP + TLS', 8.2, 'ink', mono=True) + cap('Username and password over an encrypted link.', '', 'blue', y=150, h=34))
k5 = (t(180, 22, 'Then authorization means something', 9.4, 'acc', bold=True) + t(180, 56, 'grants and policies tied to real identities', 8.2, 'ink2') + cap('Defence in depth.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Adding real authentication',
              'From NONE to Kerberos or LDAP. (Typical configuration; our lab stayed on NONE.)',
              'Authentication', 'Kerberos tickets or LDAP passwords over TLS make HiveServer2 trust identities, so grants are enforced against real users', [k1, k2, k3, k4, k5],
              ['NONE trusts any name.',
               'Kerberos uses tickets and keytabs.',
               'Clients connect with a principal.',
               'LDAP suits BI tools.',
               'Authorization becomes meaningful.'],
              hid='scenario-kerberos')

# ---- scenario 3: access review
a1 = (t(180, 22, 'Quarterly access review', 9.4, bold=True) + t(180, 56, 'auditor: who can read customer data?', 8.4, 'ink2') + cap('Answer from metadata, not memory.', '', 'blue', y=150, h=34))
a2 = (t(180, 22, 'List grants', 9.4, bold=True) + t(180, 56, 'SHOW GRANT ON TABLE customers; SHOW ROLE GRANT …', 7.6, 'ink', mono=True) + cap('Or query TBL_PRIVS / ROLE_MAP in the metastore.', '', 'green', y=150, h=34))
a3 = (t(180, 22, 'Remove leavers', 9.4, bold=True) + t(180, 56, 'REVOKE ROLE analyst FROM USER …', 8.2, 'ink', mono=True) + cap('Takes effect on the next query (Step 8).', '', 'green', y=150, h=34))
a4 = (t(180, 22, 'Least privilege', 9.4, bold=True) + t(180, 56, 'views for analysts, write grants for loaders only', 8, 'ink2') + cap('No direct grants to people.', '', 'blue', y=150, h=34))
a5 = (t(180, 22, 'Automate', 9.4, 'acc', bold=True) + t(180, 56, 'roles from LDAP groups; reviews from audit logs', 8, 'ink2') + cap('Ranger usersync does this.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'An access review',
              'Proving who can access what. (Typical practice; commands as used in the lab.)',
              'Access review', 'List grants and role memberships, revoke what is no longer needed, and automate group-based roles', [a1, a2, a3, a4, a5],
              ['The auditor asks who has access.',
               'Grants are listed from Hive or the metastore.',
               'Revoke access for leavers.',
               'Apply least privilege.',
               'Automate with groups and audit logs.'],
              hid='scenario-review')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Who may do what</h2>
  <p>Left: real outputs. Right: how Hive decides.</p>
''' + two + '''
  <p>Three live scenarios follow: Ranger masking, real authentication, and an access review.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Hive security at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'PII', 12, 'green', bold=True) + t(60, 58, 'protection', 7.4, 'ink2'),
    '1. Protecting personal data',
    'Names, phones and addresses are hidden behind views or Ranger masks to meet privacy laws such as India’s DPDP Act and GDPR.',
    ['PII columns', '*view / mask', 'Compliant access']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'roles', 11, 'blue', bold=True) + t(60, 58, 'by team', 7.4, 'ink2'),
    '2. Team-based access',
    'Analyst, engineer and data-science roles map to directory groups, so joining a team grants the right access automatically.',
    ['LDAP group', '*role', 'Privileges']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'audit', 11, 'violet', bold=True) + t(60, 58, 'logs', 7.4, 'ink2'),
    '3. Audit trails',
    'Ranger audit logs record every allowed and denied access, used in security investigations and compliance reports.',
    ['Access', '*audit log', 'Evidence']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'tenants', 10, 'acc', bold=True) + t(60, 58, 'separation', 7.4, 'ink2'),
    '4. Multi-tenant platforms',
    'Different business units share one cluster but only see their own databases, enforced by policies.',
    ['Shared cluster', '*policies', 'Isolated tenants']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'safe', 11, 'acc', bold=True) + t(60, 58, 'operations', 7.4, 'ink2'),
    '5. Safer operations',
    'Disabling dfs, ADD JAR and TRANSFORM for normal users prevents accidental or malicious use of cluster resources.',
    ['User', '*restricted', 'Stable cluster']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> views (<a href="../../09-extending-hive/02-views-and-materialized-views/">9.2</a>), ACID updates (<a href="../../07-acid-and-iceberg/01-acid-tables-update-delete/">7.1</a>) and the metastore (<a href="../01-metastore-administration/">10.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
