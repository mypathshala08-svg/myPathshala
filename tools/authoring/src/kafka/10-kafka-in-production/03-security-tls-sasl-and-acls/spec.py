import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-kafka-in-production', lesson='03-security-tls-sasl-and-acls', n='10.3', module_label='Module 10 · Kafka in production',
    title='Security: TLS, SASL and ACLs',
    desc='Securing Kafka: listeners and security protocols, TLS certificates, keystores and truststores, SASL authentication with SCRAM (and OAUTHBEARER, mTLS, Kerberos), principals, the KRaft StandardAuthorizer and ACLs for least privilege, super users and quotas. Real Kafka 4.4 lab: a SASL_SSL broker rejects plaintext, wrong passwords and untrusted certificates, and ACLs let billing write and kitchen read only.',
    og_desc='A locked Kafka 4.4 broker: TLS + SCRAM + ACLs, four break-in attempts and least-privilege access.',
    minutes=24, level='Advanced',
    lead='How do you stop any app from reading payments? We build a broker with <b>TLS</b>, <b>SCRAM</b> logins and <b>ACLs</b>, try to break in, and grant least privilege. <b>All outputs are real.</b>',
    chips=['SASL_SSL only', '4 break-in attempts', 'billing write · kitchen read', 'Runs in your browser (Python)'])
MAIN = '''# A tiny authorizer: deny by default, allow by ACL
acls = [("User:billing", "WRITE", "TOPIC", "payments-103"),
        ("User:billing", "DESCRIBE", "TOPIC", "payments-103"),
        ("User:kitchen", "READ", "TOPIC", "payments-103"),
        ("User:kitchen", "READ", "GROUP", "kitchen-103")]
super_users = {"User:admin"}

def authorize(principal, op, rtype, name):
    if principal in super_users:
        return "ALLOW (super user)"
    return "ALLOW" if (principal, op, rtype, name) in acls else "DENY"

for req in [("User:billing", "WRITE", "TOPIC", "payments-103"), ("User:kitchen", "WRITE", "TOPIC", "payments-103"),
            ("User:kitchen", "READ", "GROUP", "other-group"), ("User:admin", "DELETE", "TOPIC", "payments-103")]:
    print(req, "->", authorize(*req))
'''
RUN = dict(heading='Run the code: an authorizer', intro='<p>How ACL checks decide. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    return "ALLOW" if (principal, op, rtype, name) in acls else "DENY"', 'No matching ACL = deny.'), ('    if principal in super_users:', 'Super users skip ACLs: keep the list tiny.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a prefixed rule.', code=None),
        dict(label='2 · Predict first: consumer ACLs', hint='<b>Predict first:</b> how many ACLs does a consumer need?', code='print(2, "(topic Read + group Read)")\n'),
        dict(label='3 · Prefixed', hint='payments- prefix.', code='print("payments-103".startswith("payments-"))\n'),
        dict(label='4 · Deny wins', hint='ALLOW and DENY both match.', code='print("DENY")\n'),
        dict(label='5 · Spot the error', hint='Wrong password.', expect='error', code='raise PermissionError("SaslAuthenticationException: Authentication failed during authentication due to invalid credentials with SASL mechanism SCRAM-SHA-512")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: secure a broker', intro='<p>Needs Docker. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Format with a first user', cmd="kafka-storage.sh format -t SecLab00000000000001A -c server.properties --add-scram 'SCRAM-SHA-512=[name=admin,password=admin-secret]'", file='terminal', output='', note='Bootstrap admin.'),
           dict(title='2 · Add a user', cmd='kafka-configs.sh --bootstrap-server sec1:9095 --command-config admin.properties --alter --entity-type users --entity-name billing --add-config "SCRAM-SHA-512=[password=billing-secret]"', file='terminal', output='Completed updating config for user billing.', note='Salted.'),
           dict(title='3 · Grant', cmd='kafka-acls.sh --bootstrap-server sec1:9095 --command-config admin.properties --add --allow-principal User:kitchen --operation Read --topic payments-103 --group kitchen-103', file='terminal', output='', note='Topic + group.')])
TRACE = dict(heading='One check step by step', intro='<p>Who, what, allowed?</p>',
    code='principal = "User:kitchen"\nop, res = "WRITE", "payments-103"\nallowed = {("User:kitchen", "READ", "payments-103")}\nprint((principal, op, res) in allowed)\n',
    notes={1: 'Principal :: From SASL.', 4: 'Decision :: DENY.'})
WORKED_INTRO = 'Three security decisions.'
EXAMPLES = [
    dict(level='b', tag='Security · protocol', title='Pick a protocol', problem='<p>Shared cluster, passwords.</p>', inp='need',
         approach=['Encrypt: TLS.', 'Login: SCRAM.', 'SASL_SSL.'], code='print("SASL_SSL + SCRAM-SHA-512")\n', notes={1: 'Default :: Production.'}, tryit='Types table.'),
    dict(level='i', tag='Security · ACL', title='Team prefix', problem='<p>Team owns all payments-* topics.</p>', inp='pattern',
         approach=['--resource-pattern-type prefixed.', '--topic payments-.', 'One ACL per op.'], code='print("kafka-acls --add --allow-principal User:payments-team --operation All --topic payments- --resource-pattern-type prefixed")\n', notes={1: 'Prefixed :: Fewer rules.'}, tryit='ACL figure.'),
    dict(level='a', tag='Security · OAuth', title='Cloud identity', problem='<p>Use company SSO identities.</p>', inp='mechanism',
         approach=['SASL/OAUTHBEARER.', 'Tokens from IdP.', 'Principal from token claim.'], code='print({"sasl.mechanism": "OAUTHBEARER", "sasl.oauthbearer.token.endpoint.url": "https://idp.example/token"})\n', notes={1: 'No passwords :: Short-lived tokens.'}, tryit='Level 3.')]
QUIZ = mix([
    dict(q='Beginner: TLS provides…', options=['ACLs', 'Encryption and server identity', 'Compression', 'Replication'], answer=1, why='Lock 1.'),
    dict(q='Beginner: SASL provides…', options=['Who the client is', 'Faster disks', 'Retention', 'Partitions'], answer=0, why='Authentication.'),
    dict(q='Beginner: ACLs provide…', options=['Encryption', 'Authorization', 'Backups', 'Schemas'], answer=1, why='What you may do.'),
    dict(q='Intermediate: A consumer needs Read on…', options=['Topic only', 'Topic and group', 'Cluster', 'Nothing'], answer=1, why='Step 6.'),
    dict(q='Intermediate: Plaintext client on a TLS port in our lab…', options=['Worked', 'Timed out', 'Got data', 'Deleted topic'], answer=1, why='Step 2.'),
    dict(q='Intermediate: Default with an authorizer and no ACLs…', options=['Allow all', 'Deny (except super users)', 'Read only', 'Random'], answer=1, why='Step 4.'),
    dict(q='Advanced: SCRAM stores passwords…', options=['Plain text', 'Salted hashes in metadata', 'In ZooKeeper only', 'Client side'], answer=1, why='Iterations.'),
    dict(q='Advanced: The KRaft authorizer class is…', options=['AclAuthorizer', 'StandardAuthorizer', 'ZkAuthorizer', 'SimpleAuth'], answer=1, why='4.x.')])
REVISION = ['Three locks: TLS (encrypt), SASL (who), ACLs (what).', 'SASL_SSL + SCRAM-SHA-512 + StandardAuthorizer; super users minimal.',
    'Lab: plaintext timeout, wrong password, untrusted CA fail; admin OK.', 'Default deny; billing Write+Describe; kitchen Read topic + group.', 'OAuth/mTLS options; config providers; cert rotation; quotas.']
FAQ = [('Does TLS slow Kafka?', 'Some CPU cost, and zero-copy is not used for TLS connections; modern CPUs handle it well.'),
    ('Where are ACLs stored?', 'In the KRaft metadata log (Lesson 5.4).'),
    ('Can I use mTLS instead of SASL?', 'Yes: ssl.client.auth=required; the certificate’s DN becomes the principal (map it with ssl.principal.mapping.rules).'),
    ('How do managed services do it?', 'SASL_SSL with API keys, OAuth, or cloud IAM (e.g. MSK IAM).')]
PRACTICE_INTRO = 'Security programs.'
PROBLEMS = [
    dict(level='easy', title='Protocol', stmt='Encrypted + authenticated?', inp='str', code='print("SASL_SSL")\n', explain='Both.'),
    dict(level='easy', title='Principal', stmt='Format a principal.', inp='str', code='print("User:" + "billing")\n', explain='User:billing.'),
    dict(level='easy', title='Default', stmt='No ACL found?', inp='str', code='print("DENY")\n', explain='Secure default.'),
    dict(level='medium', title='Check', stmt='Allowed?', inp='set', code='acl = {("kitchen", "READ")}\nprint(("kitchen", "WRITE") in acl)\n', explain='False.'),
    dict(level='medium', title='Prefix match', stmt='Prefix rule.', inp='str', code='print([t for t in ["payments-1", "orders-1"] if t.startswith("payments-")])\n', explain='payments-1.'),
    dict(level='medium', title='Expiry', stmt='Days left.', inp='dates', code='from datetime import date\nprint((date(2027, 11, 6) - date(2026, 11, 6)).days)\n', explain='365.'),
    dict(level='business', title='ACL count', stmt='20 apps × 3 ACLs.', inp='ints', code='print(20 * 3)\n', explain='60 rules.'),
    dict(level='business', title='Quota', stmt='50 MB/s for 10 tenants.', inp='ints', code='print(50 * 10, "MB/s max")\n', explain='Capacity plan.')]
SCN_INTRO = 'Security interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How is Kafka secured?”', 'Explain.', 'answer?', '<p>TLS to encrypt traffic and verify brokers, SASL (SCRAM, OAuth, Kerberos) or mTLS to authenticate clients, and ACLs to authorize each principal for topics, groups and cluster operations.</p>', '“With a firewall only.”') +
    scn('Platform', 'Mid-level', 'Consumer denied', 'GroupAuthorizationException.', 'fix?', '<ul><li>Add Read on the group.</li><li>Check group id spelling.</li></ul>', 'Make it super user.') +
    scn('Platform', 'Mid-level', 'Cert expired', 'All clients failing.', 'fix?', '<ul><li>Rotate certificate (dynamic config).</li><li>Monitor expiry.</li></ul>', 'Switch to PLAINTEXT.') +
    scn('Fintech', 'Senior', 'Multi-tenant', 'Ten teams, one cluster.', 'design?', '<ul><li>Per-team principals, prefixed ACLs.</li><li>Quotas, audit, secret providers.</li></ul>', 'Shared admin user.'))
