import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l103_security.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Out of the box, anyone who can reach port 9092 can read every payment and delete every topic. How many locks does a production Kafka need?',
    'Three: <b>TLS</b> (nobody can read or fake traffic), <b>SASL</b> (who are you?) and <b>ACLs</b> (what may you do?). We built a broker that only accepts SASL_SSL with SCRAM, and tried four ways in: plaintext timed out, a wrong password was rejected, an untrusted certificate failed the handshake, and only the admin got through. Then billing could write but not read, kitchen could read but not write, and neither could use another group.',
    ['Encryption with TLS: keystores, truststores, certificates.',
     'Authentication with SASL: SCRAM, OAUTHBEARER, mTLS, GSSAPI.',
     'Authorization with ACLs and least privilege.'])
cmap = concept_map('Concept map. Beginner: listener, port, who can connect. Intermediate: TLS, SASL/SCRAM, principals, ACLs. Advanced: mTLS, OAUTHBEARER, super users, StandardAuthorizer in KRaft, quotas, secrets handling.',
    [[('ls', 'Listeners', 'ports + protocols', None), ('ar', 'Architecture', 'Lesson 1.3', B + '01-introduction/03-kafka-architecture/')],
     [('tl', 'TLS', 'encrypt + verify', None), ('sa', 'SASL', 'authenticate', None), ('pr', 'Principal', 'User:billing', None), ('ac', 'ACLs', 'authorize', None)],
     [('mt', 'mTLS / OAuth', 'other auth', None), ('su', 'Super users', 'break-glass', None), ('qa', 'Quotas', 'limit tenants', None), ('sc', 'Secrets', 'config providers', B + '07-kafka-connect/01-kafka-connect/')]],
    [('ls', 'tl'), ('ar', 'ls'), ('tl', 'sa'), ('sa', 'pr'), ('pr', 'ac'), ('sa', 'mt'), ('ac', 'su'), ('pr', 'qa'), ('sa', 'sc')],
    {'ls', 'tl', 'sa', 'pr', 'ac', 'mt', 'su', 'qa'},
    '<b>Builds on:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3</a>. <b>Next:</b> <a href="../04-multi-cluster-and-mirrormaker-2/">10.4 Multi-cluster</a>.')
whw = why_how_where(
    'Kafka carries payments, personal data and business events. Without security, any app (or attacker) on the network can read, write or delete them, and audits fail.',
    'Each listener has a security protocol: PLAINTEXT, SSL, SASL_PLAINTEXT or SASL_SSL. TLS encrypts and proves the broker’s identity with certificates; SASL proves the client’s identity and gives a principal (User:billing); the authorizer (StandardAuthorizer in KRaft) checks ACLs for every request.',
    'Every shared or regulated cluster; multi-tenant platforms; managed services (which force SASL_SSL or IAM/OAuth).',
    'TLS costs some CPU and disables zero-copy for TLS traffic. Certificates expire; passwords leak if stored in plain files. ACLs need maintenance as apps change.')

def locks(hl=-1):
    parts = [('client', 'card'), ('TLS', 'blue'), ('SASL', 'violet'), ('ACL', 'amber'), ('topic', 'green')]
    o = ''
    for k, (n, tn) in enumerate(parts):
        o += box(8 + k * 70, 50, 62, 40, 'acc' if k == hl else tn, rx=6) + t(39 + k * 70, 74, n, 8, bold=True)
        if k < 4: o += arrow(70 + k * 70, 70, 78 + k * 70, 70)
    return o + t(180, 30, 'encrypt → who are you → may you?', 7.6)
scene_svg = scene('A request passes three locks: TLS encrypts and verifies the broker, SASL authenticates the user, and an ACL check decides if the user may access the topic.', locks(),
                  'Three locks: <tspan font-weight="700" class="s-acc">TLS, SASL, ACL</tspan>.')
dialogue = '''K> Sir, the auditor asks: can the kitchen app read payment data? Honestly… yes, everyone can read everything.
A> Then we add three locks. TLS so nobody can sniff the wire, SASL so every app has a name, ACLs so each name gets only what it needs.
R> Will apps need code changes?
A> Mostly configuration: a few client properties. Let’s build a locked broker and try to break in.'''

lv = '''
LEVELS> Security at three levels
L1> A bank branch
      <ul>
        <li>Tinted, locked glass (TLS) so nobody sees inside; ID check at the door (SASL); and each employee’s card opens only certain rooms (ACLs). The manager has a master key (super user) used rarely.</li>
      </ul>
L2> Configuration
      <ul>
        <li>Broker: <code>listeners=SECURE://:9095</code>, <code>listener.security.protocol.map=SECURE:SASL_SSL</code>, <code>sasl.enabled.mechanisms=SCRAM-SHA-512</code>, <code>ssl.keystore.*</code>, <code>ssl.truststore.*</code>, <code>authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer</code>, <code>super.users</code>.</li>
        <li>Client: <code>security.protocol=SASL_SSL</code>, <code>sasl.mechanism=SCRAM-SHA-512</code>, <code>sasl.jaas.config=… username password</code>, <code>ssl.truststore.location</code>.</li>
        <li>SCRAM users: <code>kafka-configs --alter --entity-type users --add-config SCRAM-SHA-512=[password=…]</code>; the first admin is added at format time with <code>kafka-storage format --add-scram</code>.</li>
      </ul>
L3> Choices and details
      <ul>
        <li>Mechanisms: SCRAM-SHA-256/512 (passwords stored salted in metadata), OAUTHBEARER (tokens from an identity provider, common in clouds), mTLS (certificate = identity), GSSAPI/Kerberos (enterprises), PLAIN (only over TLS, with external checks).</li>
        <li>ACLs: principal, host, operation (Read, Write, Create, Describe, Alter…), resource (Topic, Group, Cluster, TransactionalId), pattern (literal or prefixed), allow/deny. Deny wins. Consumers need Read on the topic <i>and</i> the group.</li>
        <li>Keep secrets out of files with config providers, rotate certificates before expiry, and use quotas (produce/fetch bytes per second, request %) to protect tenants from each other.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of an ACL binding: principal User:billing, host star, operation WRITE, permission ALLOW, resource type TOPIC, name payments-103, pattern LITERAL.',
    t(16, 22, 'One ACL from the lab', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('User:billing', 'violet', 1), ('host=*', 'card', 2), ('WRITE', 'amber', 3), ('ALLOW', 'green', 4), ('TOPIC payments-103', 'blue', 5), ('LITERAL', 'card', 6)]) +
    legend(16, 84, [(1, 'Principal', 'identity from SASL (or the TLS certificate)'), (2, 'Host', 'client IP, * = any'), (3, 'Operation', 'Read, Write, Describe, Create, Alter, Delete …'),
                    (4, 'Permission', 'ALLOW or DENY (deny wins)'), (5, 'Resource', 'Topic, Group, Cluster, TransactionalId'), (6, 'Pattern', 'LITERAL name or PREFIXED (e.g. payments-)')], size=8, gap=15, w=90),
    h=186, caption='kafka-acls --list prints exactly these fields.')
extra = '''

  <h3>Dissect an ACL</h3>
''' + DIS

types_html = table(['Protocol', 'Encrypted', 'Authenticated', 'Use'], [
    ['PLAINTEXT', 'no', 'no', 'local dev only'], ['SSL', 'yes', 'optional (mTLS)', 'certificate-based identity'],
    ['SASL_PLAINTEXT', 'no', 'yes', 'avoid (passwords on the wire with PLAIN)'], ['SASL_SSL', 'yes', 'yes', 'production default'],
], minw=560) + table(['App', 'Needs', 'Our lab'], [
    ['Producer', 'Write (+ Describe) on topic; idempotent needs Write', 'billing'], ['Consumer', 'Read on topic + Read on group', 'kitchen'],
    ['Transactional producer', '+ Write on TransactionalId', '—'], ['Admin tools', 'Cluster / Alter / Create as needed', 'admin (super user)'],
], minw=560)
warn = 'Do not leave User:ANONYMOUS or wide super.users in production, and never set allow.everyone.if.no.acl.found=true on a shared cluster. Our lab listed ANONYMOUS as a super user only because its controller listener is plaintext inside a private Docker network; in production secure the controller listener too.'

steps = [
    ('Step 1 · Certificates',
     code('bash', 'terminal', 'keytool -genkeypair -alias ca … -ext bc:c          # lab CA\nkeytool -genkeypair -alias sec1 … -ext SAN=dns:sec1   # broker key\nkeytool -certreq … | keytool -gencert -alias ca …     # CA signs it\nkeytool -importcert … -keystore trust.p12             # clients trust the CA', sec('== 1)', '== 2)')),
     'The broker certificate names the host (SAN dns:sec1) and is signed by our CA. Clients trust the CA, not each broker.'),
    ('Step 2 · Four ways in',
     code('properties', 'admin.properties', 'security.protocol=SASL_SSL\nsasl.mechanism=SCRAM-SHA-512\nsasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="admin" password="admin-secret";\nssl.truststore.location=/s/trust.p12', sec('== 2)', '== 3)')),
     'Plaintext to a TLS port just times out; a wrong password fails SASL; a client that trusts another CA fails the TLS handshake; the right config works.'),
    ('Step 3 · Users and a topic',
     code('bash', 'terminal', 'kafka-configs.sh --bootstrap-server sec1:9095 --command-config admin.properties --alter --entity-type users --entity-name billing --add-config "SCRAM-SHA-512=[iterations=8192,password=billing-secret]"', sec('== 3)', '== 4)')),
     'Credentials are stored salted in the KRaft metadata, never as plain passwords.'),
    ('Step 4 · Denied by default',
     code('bash', 'terminal', 'echo … | kafka-console-producer.sh --bootstrap-server sec1:9095 --producer.config billing.properties --topic payments-103', sec('== 4)', '== 5)')),
     'With an authorizer and no ACLs, only super users can act.'),
    ('Step 5 · Least privilege',
     code('bash', 'terminal', 'kafka-acls.sh … --add --allow-principal User:billing --operation Write --operation Describe --topic payments-103\nkafka-acls.sh … --add --allow-principal User:kitchen --operation Read --topic payments-103 --group kitchen-103', sec('== 5)', '== 6)')),
     'Billing may write; kitchen may read, using only the group kitchen-103.'),
    ('Step 6 · Try again',
     code('bash', 'terminal', 'billing writes · kitchen reads · kitchen writes · kitchen uses another group', sec('== 6)')),
     'Exactly as granted. Kitchen’s write failed even earlier, at ClusterAuthorization: its idempotent producer could not get a producer id without Write on the topic.'),
]
see = [term([('Owner CN=sec1', W), ('Issuer CN=TiffinGo Lab CA', G)], size=7.0), term([('plaintext: timeout', RD), ('wrong pw: SASL failed', RD), ('other CA: SSL failed', RD), ('admin: OK', G)], size=6.8),
       term([('users billing, kitchen', G), ('SCRAM-SHA-512', W)], size=7.0), term([('billing: TopicAuthorization', RD)], size=7.0),
       term([('billing WRITE, DESCRIBE', G), ('kitchen READ + group', G)], size=7.0), term([('billing write OK', G), ('kitchen read OK', G), ('kitchen write DENIED', RD)], size=6.8)]
B1 = [locks(1), locks(2), locks(2), locks(3), locks(3), locks(4)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Certificates', 'Wrong keys rejected', 'Users created', 'Default deny', 'ACLs granted', 'Exactly as granted'], ['blue', 'red', 'violet', 'red', 'amber', 'green'])]
two = anim_two('Security', 'TLS, SASL, ACLs', 'Real outputs from the lab', 'The three locks', see, B1, ['Certs.', 'Break in.', 'Users.', 'Deny.', 'Grant.', 'Verify.'], ['TLS.', 'Fail.', 'SCRAM.', 'Default.', 'ACLs.', 'Done.'])
pe = peel('One produce request, layer by layer', 'billing → payments-103 over SASL_SSL. (Simplified.)',
    [('TCP', ''), ('TLS', ''), ('SASL', ''), ('Principal', ''), ('Authorize', ''), ('Append', '')],
    [['TCP', 'connect sec1:9095', '', ''], ['TLS', 'broker cert verified', 'against trust.p12', 'channel encrypted'], ['SASL', 'SCRAM-SHA-512', 'challenge/response', 'no password sent'],
     ['Principal', 'User:billing', 'attached to session', ''], ['Authorize', 'WRITE on Topic payments-103?', 'ALLOW ACL found', ''], ['Append', 'leader writes', 'ack to billing', '']],
    ['Connect.', 'Encrypt.', 'Prove.', 'Name.', 'Check.', 'Write.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Audit finding', 'Everyone can read payments. (Typical.)', ('Least privilege', 'Per-app users + ACLs'), [
    ('Shared PLAINTEXT cluster', 'no auth', 'Finding.', 'red'), ('Add SASL_SSL listener', 'keep old during migration', 'Dual.', 'amber'),
    ('Per-app SCRAM users', 'ACLs per topic/group', 'Grant.', 'green'), ('Move apps one by one', 'then close PLAINTEXT', 'Migrate.', 'green'),
    ('Audit passes', 'ACL review quarterly', 'Done.', 'blue')], ['Open.', 'Listener.', 'Grant.', 'Move.', 'Pass.'], 'scenario-audit') + \
       five('Real-time scenario 2', 'Certificate expired at night', 'All clients fail TLS. (Typical.)', ('Cert lifecycle', 'Rotate before expiry'), [
    ('SslAuthenticationException', 'everywhere', 'Outage.', 'red'), ('Check validity', 'expired 02:00', 'Cause.', 'amber'),
    ('New cert, same CA', 'dynamic update via kafka-configs', 'No restart.', 'green'), ('Clients reconnect', 'trust the CA', 'Recover.', 'green'),
    ('Alert 30 days before expiry', 'automation', 'Prevent.', 'blue')], ['Fail.', 'Expired.', 'Rotate.', 'Recover.', 'Alert.'], 'scenario-cert') + \
       five('Real-time scenario 3 · advanced', 'Noisy tenant', 'One team floods the cluster. (Typical.)', ('Quotas', 'Bytes/s and request %'), [
    ('Analytics backfill', '500 MB/s', 'Others slow.', 'red'), ('Identify principal', 'User:analytics', 'Who.', 'amber'),
    ('Set quota', 'producer_byte_rate=50MB', 'Throttle.', 'green'), ('Throttle-time metric', 'client sees delay', 'Fair.', 'green'),
    ('Per-tenant quotas by default', 'platform policy', 'Done.', 'blue')], ['Flood.', 'Who.', 'Quota.', 'Fair.', 'Policy.'], 'scenario-quota')
assemble(HERE, h2_story='Locking down the cluster', hook_html=hk,
    narration='An auditor asks whether the kitchen app can read TiffinGo’s payments. On the current cluster, every app can read and write everything.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Security: TLS, SASL and ACLs',
    formal='Kafka security has three layers configured per <b>listener</b>: <b>encryption</b> and server identity with <b>TLS</b>; client <b>authentication</b> with SASL mechanisms (SCRAM, OAUTHBEARER, GSSAPI, PLAIN) or TLS client certificates, which yields a <b>principal</b>; and <b>authorization</b> by an authorizer that evaluates <b>ACLs</b> (principal, host, operation, resource, pattern, allow/deny) for every request. Quotas additionally limit resource use per principal or client.',
    simple='Encrypt the connection (TLS), make every app log in (SASL), and give each login only the permissions it needs (ACLs). Nothing else changes for apps except a few connection settings.',
    term_rows=[('Listener', 'Port + protocol.'), ('TLS', 'Encryption + identity.'), ('Truststore', 'CAs the client trusts.'), ('SASL', 'Login framework.'), ('SCRAM', 'Salted password auth.'), ('Principal', 'User:name.'), ('ACL', 'Permission rule.'), ('Super user', 'Bypasses ACLs.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('TLS alone is enough.', 'TLS encrypts; SASL and ACLs decide who does what.', 'Step 4.'),
               ('A consumer needs only topic Read.', 'Also Read on its group.', 'Step 6.'),
               ('SCRAM sends the password.', 'Challenge/response; stored salted.', 'Peel.')],
    exam='“How do you secure Kafka?” SASL_SSL listeners: TLS for encryption/identity (keystore/truststore, CA), SASL SCRAM/OAUTHBEARER/mTLS for authentication, StandardAuthorizer ACLs for least privilege (topic + group for consumers), super users minimal, quotas, secret providers, cert rotation.',
    types_h2='Protocols and permissions', types_html=types_html, warn=warn,
    steps_h2='Build a locked broker', steps_intro='All outputs are real: a separate Kafka 4.4.0 broker (sec1) with a SASL_SSL listener, SCRAM-SHA-512 and StandardAuthorizer.',
    steps=steps, two=two, peel_intro='Now peel one secured request.', peel_html=pe,
    scen_intro='Three live scenarios: an audit, an expired certificate, and a noisy tenant.', scen=scen,
    uc_h2='Security at work', ucs=[uc_('pci', 'payments', 'red', '1. Payments (PCI)', 'Encrypt, authenticate, restrict.', ['Payments', '*locks', 'Audit']),
        uc_('tenant', 'tenants', 'blue', '2. Multi-tenant platforms', 'Per-team users, prefixed ACLs, quotas.', ['Teams', '*ACL+quota', 'Isolation']),
        uc_('cloud', 'cloud', 'violet', '3. Managed Kafka', 'SASL_SSL, OAuth or IAM.', ['App', '*SASL_SSL', 'Cloud']),
        uc_('pii', 'privacy', 'green', '4. Personal data', 'Only approved apps read.', ['PII', '*ACL', 'Approved'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3 Architecture</a>.')
