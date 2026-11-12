import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import loop_scene, star_vs_scoped, five_questions
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        bx = box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        o += (f'<g class="sa-glow">{bx}</g>' if i == k else bx) + (sa_tick(112 + i * 112, 38, 7) if i < k else '')
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)




hk = hook('EduSpark gave its faculty group “s3:*” on everything, to stop the AccessDenied complaints. In week two, a teacher cleaning up her folder deleted three batches of student submissions.',
    'Nobody was careless — the policy was. <b>Least privilege</b> means every identity gets exactly the actions it needs, on exactly the resources it needs, under the right conditions, and an explicit “never” for what must not happen. This lesson teaches a repeatable way to write such policies — five questions, seven techniques and a validate-and-prove loop — and on <b>your own</b> account (or in the simulator) you will build the faculty policy that examiners ask for and prove it line by line.',
    ['Answer five questions: who, what action, which resource, when, never.', 'Prefixes, conditions, policy variables and tags make policies precise.', 'Validate before use; prove allow and deny; trim later.'])

def story_scene():
    o = t(180, 12, 'Wide open vs just enough', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, '“s3:*” on “*”', 8.4, 'ink', bold=True) + t(88, 64, 'cleanup deletes', 7, 'ink2') + t(88, 78, 'student submissions', 7, 'ink2') + t(88, 92, '3 batches lost', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Scoped policy', 8.4, 'ink', bold=True) + t(272, 64, 'notes/ only', 7, 'ink2') + t(272, 78, 'Deny submissions/', 7, 'ink2') + t(272, 92, 'cleanup is safe', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Permissions should match the job, not the complaint', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: the faculty group had s3:* on everything and a cleanup deleted three batches of submissions. Right: a scoped policy allows only notes and denies submissions, so cleanup is safe.', story_scene(), 'Exactly what the job needs — <tspan font-weight="700" class="s-acc">no more</tspan>.', h=132)
dialogue = '''R> Sir, giving everyone full access stopped all the complaints.
A> And deleted three batches of submissions. Complaints are useful — each AccessDenied tells you exactly which permission is missing.
K> But writing JSON is hard.
A> Answer five questions first in plain words: who, does what, on which thing, when, and what must never happen. Then each answer becomes one part of the policy.
R> How do we know it is right?
A> Validate it with Access Analyzer, then prove it with the simulator — what works and what is blocked. Let’s write one.'''

BIG = five_questions()
picture = (newbie('A policy is like the instructions you give a house-sitter: “You may water the plants in the balcony and use the kitchen, only during the day. Never open the bedroom cupboard.” Each part — <b>who</b>, <b>what</b>, <b>where</b>, <b>when</b>, <b>never</b> — becomes one part of the written policy.',
            [('Least privilege', 'giving only the access needed, nothing extra'), ('Action', 'a specific thing you can do, like upload or delete'), ('Prefix', 'a folder-like path inside a storage bucket, e.g. notes/'), ('Condition', 'an extra rule like “only with OTP” or “only over a secure connection”'), ('Explicit deny', 'a written “never”, which always wins')]) +
    '  <p>Every good policy answers five questions. Write the plain answer first, then translate:</p>\n' + BIG +
    '\n  <h3>Situation — the same job, two policies</h3>\n' + star_vs_scoped())

SOLVE = loop_scene()

def mapfig():
    o = t(320, 16, 'Seven techniques for least privilege', 11, 'ink', bold=True)
    items = [('1', 'Exact actions', 'no service:*', 'blue'), ('2', 'Exact resources', 'ARNs + prefixes', 'green'), ('3', 'Conditions', 'MFA, HTTPS, IP, Region', 'violet'), ('4', 'Explicit Deny guards', 'the “never” list', 'red'),
             ('5', 'Policy variables', '${aws:username}', 'amber'), ('6', 'Tags (ABAC)', 'match principal ↔ resource', 'card'), ('7', 'Analyze + trim', 'Access Analyzer', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.2, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'Use 1–4 in every policy; 5–6 to scale to many users; 7 to keep it tight over time.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven least-privilege techniques: exact actions, exact resources, conditions, explicit deny guards, policy variables, tags (ABAC), analyze and trim.', mapfig(), h=222)

def lp(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 2', 'SAA-C03 / Security Specialty', 'C-DAC lab exams'], rw, pro)

A1 = mk(['Job needs', 'List actions', 'Nothing else'], ['job|upload notes|read notes', 'actions|PutObject|GetObject, List', 'exclude|Delete*|Put*Policy'], ['blue', 'amber', 'green'],
        ['write down what the job needs', 'list the exact API actions', 'leave every other action out'], [('Need', 'From the job description.', ''), ('Map', 'To API actions.', ''), ('Exclude', 'No wildcards like s3:*.', '')], 'Exact actions', 'Name every action.', 'Actions', 'Animation: job needs; list actions; nothing else.', 'p1anim')
T1 = lp(1, 'Exact actions (no service:*)', 'blue',
    'List the specific API actions the job requires (for example <code>s3:GetObject</code>, <code>s3:PutObject</code>, <code>s3:ListBucket</code>) instead of wildcards like <code>s3:*</code>; the Service Authorization Reference lists every action, its resource types and condition keys.',
    'A shopping list with items, not “buy whatever is in the shop”.',
    'Faculty: ListBucket + GetObject + PutObject. Not DeleteObject, not PutBucketPolicy.',
    'Tip: <code>s3:Get*</code> includes GetBucketPolicy and GetObjectAcl — wildcards hide surprises.', A1,
    'always.', 'copying “s3:*” from a blog to “make it work”.',
    'Allow only the exact things the person must do.',
    [('Job', 'Plain sentence.'), ('Actions', 'From the reference.'), ('Test', 'AccessDenied names gaps.'), ('Add', 'One by one.'), ('Avoid', 'service:*.')],
    [('API action', 'one operation, e.g. s3:PutObject'), ('wildcard', '* matches anything'), ('Service Authorization Reference', 'AWS list of actions per service')],
    table(['Task', 'Actions'], [['See files in a folder', 's3:ListBucket (bucket ARN)'], ['Download', 's3:GetObject (object ARN)'], ['Upload', 's3:PutObject (object ARN)']], minw=420),
    'Exam options with “*” are usually the wrong answer for least privilege.',
    'Read the AccessDenied message — since 2023 it often names which policy type is missing the Allow.')

A2 = mk(['Bucket ARN', 'Object ARN', 'Prefix'], ['bucket|arn:aws:s3:::b|List', 'objects|arn:aws:s3:::b/*|Get/Put', 'prefix|b/notes/*|one folder'], ['green', 'amber', 'blue'],
        ['bucket-level actions use the bucket ARN', 'object actions use bucket/key ARNs', 'narrow to a prefix (folder)'], [('Bucket', 'ListBucket on arn:aws:s3:::b.', ''), ('Objects', 'Get/Put on arn:aws:s3:::b/*.', ''), ('Prefix', 'b/notes/* for one folder.', '')], 'Exact resources', 'The right ARN shape.', 'Resources', 'Animation: bucket ARN; object ARN; prefix.', 'p2anim')
T2 = lp(2, 'Exact resources (ARNs and prefixes)', 'green',
    'Replace <code>"Resource": "*"</code> with the exact ARNs: bucket-level actions (ListBucket) on <code>arn:aws:s3:::bucket</code>, object-level actions on <code>arn:aws:s3:::bucket/prefix/*</code>, and the <code>s3:prefix</code> condition to limit what can be listed.',
    'A key that opens one cupboard in one room, not the whole building.',
    'Faculty: Get/Put on <code>edu-content/notes/*</code>; ListBucket on <code>edu-content</code> with <code>s3:prefix notes/*</code>.',
    'Tip: S3 “folders” are just key prefixes — permissions follow the key text.', A2,
    'always.', 'putting ListBucket on an object ARN (it silently never matches).',
    'Point the permission at the exact bucket and folder.',
    [('Bucket ARN', 'ListBucket.'), ('Object ARN', 'Get/Put/Delete.'), ('Prefix', 'folder/*.'), ('List limit', 's3:prefix.'), ('Check', 'Simulator.')],
    [('ARN', 'Amazon Resource Name'), ('prefix', 'start of an object key, like a folder'), ('s3:prefix', 'condition key for listing')],
    table(['Action', 'Resource ARN form'], [['s3:ListBucket', 'arn:aws:s3:::bucket'], ['s3:GetObject / PutObject', 'arn:aws:s3:::bucket/prefix/*'], ['dynamodb:GetItem', 'arn:aws:dynamodb:region:acct:table/Name']], minw=420),
    'Lab exams: “separated into notes, submissions and logs” → prefixes + prefix-scoped policies.',
    'For DynamoDB you can go further: dynamodb:LeadingKeys limits rows by partition key.')

A3 = mk(['Allow', 'only if', 'condition true'], ['allow|the action|on resource', 'if|key operator|value', 'e.g.|MFA, HTTPS|IP, Region'], ['violet', 'amber', 'green'],
        ['the statement allows (or denies) an action', 'a Condition block adds “only if”', 'checked against request context: MFA, HTTPS, IP, Region, tags'], [('Statement', 'Allow/Deny.', ''), ('Condition', 'Operator + key + value.', ''), ('Context', 'Evaluated per request.', '')], 'Conditions', 'Only if…', 'Conditions', 'Animation: allow; only if; condition true.', 'p3anim')
T3 = lp(3, 'Conditions', 'violet',
    'A <b>Condition</b> block makes a statement apply only when request context matches: e.g. <code>aws:MultiFactorAuthPresent</code>, <code>aws:SecureTransport</code>, <code>aws:SourceIp</code>, <code>aws:RequestedRegion</code>, <code>aws:PrincipalTag</code>, <code>s3:prefix</code> — using operators like StringEquals, StringLike, Bool, IpAddress, DateLessThan.',
    'A rule “you may enter the lab only with your ID card and only between 9 and 6”.',
    'Deny all S3 actions on the sales bucket when <code>aws:SecureTransport</code> is false (CityBite R1).',
    'Tip: combine Deny + condition for guard-rails (“deny if no MFA”) rather than Allow + condition.', A3,
    'access depends on how or from where the request is made.', 'condition keys that the action does not support — check the reference.',
    'Extra “only if” rules inside a permission.',
    [('Operator', 'StringEquals, Bool…'), ('Key', 'aws:… or service:…'), ('Value', 'what to match'), ('Multiple', 'AND between keys'), ('Lists', 'OR within values')],
    [('condition key', 'a fact about the request'), ('operator', 'how to compare'), ('IfExists', 'apply only if the key is present')],
    table(['Goal', 'Condition'], [['HTTPS only', 'Deny when Bool aws:SecureTransport = false'], ['MFA for sensitive actions', 'Deny when BoolIfExists aws:MultiFactorAuthPresent = false'], ['Office IP only', 'IpAddress aws:SourceIp 203.0.113.0/24'], ['India Regions only', 'StringNotEquals aws:RequestedRegion ap-south-1, ap-south-2 → Deny']], minw=480),
    'Security exams love aws:SecureTransport, aws:SourceIp and MFA conditions.',
    'aws:SourceIp does not work for requests that arrive through VPC endpoints — use aws:SourceVpce there.')

A4 = mk(['Allows', 'Explicit Deny', 'Always wins'], ['allows|from many|policies', 'deny|written “never”|guard', 'wins|over any|Allow'], ['card', 'red', 'green'],
        ['Allows may come from several policies', 'an explicit Deny states what must never happen', 'Deny wins over every Allow, now and in future'], [('Allows', 'Grant what is needed.', ''), ('Deny', 'State the never-list.', ''), ('Wins', 'Future-proof guard.', '')], 'Explicit Deny guards', 'Write the never-list.', 'Deny', 'Animation: allows; explicit deny; always wins.', 'p4anim')
T4 = lp(4, 'Explicit Deny guards', 'red',
    'An <b>explicit Deny</b> statement records what must never happen (delete data, read submissions, disable logging, leave approved Regions); because Deny overrides every Allow from any policy, it keeps the rule true even if broader permissions are attached later by mistake.',
    'A sign on the cupboard: “never open — even if someone gave you a master key”.',
    'Server role: Deny s3:DeleteObject on the sales bucket — “must never delete, even if hacked” (CityBite R6).',
    'Tip: Deny with <code>NotAction</code>/<code>NotResource</code> is powerful but easy to get wrong — test with the simulator.', A4,
    'a rule must hold no matter what else is attached.', 'using Deny as the main way to grant access — grant with Allow, guard with Deny.',
    'A written “never” that beats every “yes”.',
    [('Identify', 'Must-never actions.'), ('Write', 'Effect Deny.'), ('Scope', 'Exact resources.'), ('Condition', 'Optional (no MFA, no HTTPS).'), ('Test', 'explicitDeny in simulator.')],
    [('explicitDeny', 'simulator result for a Deny match'), ('implicitDeny', 'no Allow found'), ('guard-rail', 'rule that limits, not grants')],
    table(['', 'Implicit deny', 'Explicit deny'], [['Cause', 'no Allow', 'a Deny statement'], ['Can an Allow fix it?', 'yes', 'no'], ['Use for', 'default', 'never-rules']], minw=420),
    'Lab exams: “must never be able to delete, even if hacked” → explicit Deny on delete actions.',
    'Remember versioned buckets: deny s3:DeleteObjectVersion too, or old versions can still be removed.')

A5 = mk(['One policy', 'Variable', 'Per-user'], ['policy|for the group|written once', 'variable|${aws:username}|filled at runtime', 'result|home/meena/*|home/arjun/*'], ['amber', 'blue', 'green'],
        ['write one policy for the whole group', 'use a variable such as ${aws:username}', 'each user gets their own folder automatically'], [('Write once', 'Group policy.', ''), ('Variable', '${aws:username}, ${aws:PrincipalTag/dept}.', ''), ('Per user', 'Own folder each.', '')], 'Policy variables', 'One policy, many users.', 'Variables', 'Animation: one policy; variable; per-user.', 'p5anim')
T5 = lp(5, 'Policy variables', 'amber',
    '<b>Policy variables</b> such as <code>${aws:username}</code>, <code>${aws:userid}</code> or <code>${aws:PrincipalTag/department}</code> are replaced with request values at evaluation time, so one policy can give each user their own folder or scope by tag.',
    'One rule for the hostel: “each student may open only the locker with their own roll number”.',
    'Faculty drafts: <code>arn:aws:s3:::edu-content/drafts/${aws:username}/*</code> — each teacher sees only her drafts.',
    'Tip: policy variables need <code>"Version": "2012-10-17"</code> — the old 2008 version treats them as plain text.', A5,
    'many users need the same pattern on their own data.', 'roles assumed by many people — ${aws:username} is empty for roles (use tags or session names).',
    'Placeholders that become each user’s own name.',
    [('Variable', '${aws:username}.'), ('Resource', 'path with variable.'), ('Version', '2012-10-17.'), ('Test', 'simulate two users.'), ('Roles', 'use tags instead.')],
    [('${aws:username}', 'the IAM user name'), ('${aws:PrincipalTag/x}', 'a tag on the caller'), ('runtime substitution', 'filled at each request')],
    table(['Variable', 'Example value'], [['${aws:username}', 'meena'], ['${aws:PrincipalTag/dept}', 'physics'], ['${aws:CurrentTime}', 'request time']], minw=360),
    'Good for “home folder per user” scenarios.',
    'For Cognito app users use ${cognito-identity.amazonaws.com:sub}.')

A6 = mk(['Tag principal', 'Tag resource', 'Match'], ['principal|dept=physics|on user/role', 'resource|dept=physics|on bucket/instance', 'policy|allow if tags|equal'], ['card', 'amber', 'green'],
        ['tag people/roles with attributes', 'tag resources with the same attributes', 'one policy allows when tags match'], [('Principal tags', 'dept, project, env.', ''), ('Resource tags', 'Same keys.', ''), ('Match', 'aws:ResourceTag = aws:PrincipalTag.', '')], 'ABAC', 'Permissions follow tags.', 'ABAC', 'Animation: tag principal; tag resource; match.', 'p6anim')
T6 = lp(6, 'Tags — attribute-based access control (ABAC)', 'card',
    '<b>ABAC</b> grants access when attributes match — typically a tag on the principal and the same tag on the resource (<code>aws:ResourceTag/project</code> equals <code>${aws:PrincipalTag/project}</code>) — so new projects and people need new tags, not new policies.',
    'Coloured wristbands at an event: green-band people enter green-band areas.',
    'Developers tagged project=canteen can start/stop only EC2 instances tagged project=canteen.',
    'Tip: protect the tags too — deny changing the project tag, or people will just re-tag resources.', A6,
    'many teams/projects with the same pattern.', 'services that do not support tag-based authorisation for the action — check the reference.',
    'Access decided by matching labels on people and things.',
    [('Tag people', 'Identity Center / IAM.'), ('Tag resources', 'At creation.'), ('Policy', 'Match condition.'), ('Protect tags', 'Deny tag changes.'), ('Scale', 'No new policies.')],
    [('ABAC', 'attribute-based access control'), ('RBAC', 'role-based access control'), ('aws:ResourceTag', 'tag on the target resource')],
    table(['', 'RBAC', 'ABAC'], [['New project', 'new policy', 'new tag value'], ['Policy count', 'grows', 'stays small'], ['Needs', 'groups/roles', 'consistent tagging']], minw=420),
    'Advanced security exams and large organisations.',
    'Combine with Identity Center attributes so tags come from your HR directory automatically.')

A7 = mk(['Validate', 'Generate', 'Trim'], ['validate|grammar|risky patterns', 'generate|from CloudTrail|real usage', 'trim|unused|90 days'], ['green', 'amber', 'blue'],
        ['validate policies before deploying', 'generate a starting policy from real CloudTrail activity', 'remove permissions unused for months'], [('Validate', 'Errors, warnings, suggestions.', ''), ('Generate', 'From 90 days of activity.', ''), ('Trim', 'Unused access findings, last accessed.', '')], 'Access Analyzer', 'Keep it tight over time.', 'Analyze', 'Animation: validate; generate; trim.', 'p7anim')
T7 = lp(7, 'Analyze and trim (IAM Access Analyzer)', 'green',
    '<b>IAM Access Analyzer</b> validates policies (errors, security warnings, suggestions), can <b>generate</b> a least-privilege policy from a role’s CloudTrail activity, finds resources shared outside your account, and reports <b>unused access</b> (roles, keys, permissions not used recently); IAM <b>last-accessed</b> data shows when each service was last used.',
    'A tailor who measures you, cuts the cloth, and later takes in the extra fabric.',
    'After 3 months, the app role never used sqs:* — remove it.',
    'Tip: run validation in CI so a bad policy never reaches production.', A7,
    'every policy before deployment, and quarterly reviews.', 'treating a generated policy as final — review the resources it suggests.',
    'Tools that check and shrink policies.',
    [('Validate', 'validate-policy.'), ('Generate', 'start-policy-generation.'), ('External access', 'analyzer findings.'), ('Unused access', 'analyzer type.'), ('Last accessed', 'IAM console tab.')],
    [('finding', 'something Access Analyzer reports'), ('policy generation', 'policy from CloudTrail usage'), ('unused access', 'permissions nobody used')],
    table(['Feature', 'Answers'], [['Policy validation', 'is this policy valid and safe?'], ['Policy generation', 'what does this role really need?'], ['External access', 'what is shared outside?'], ['Unused access', 'what can we remove?']], minw=420),
    'Security Specialty and real audits rely on it.',
    'Custom policy checks (CheckNoNewAccess, CheckAccessNotGranted) can block a PR that widens permissions.')

SUMMARY = table(['#', 'Technique', 'Example', 'Use'], [
    ['1', 'Exact actions', 's3:PutObject', 'always'], ['2', 'Exact resources', 'bucket/notes/*', 'always'], ['3', 'Conditions', 'aws:SecureTransport', 'how/where rules'],
    ['4', 'Explicit Deny', 'Deny submissions/*', 'never-rules'], ['5', 'Policy variables', '${aws:username}', 'per-user data'], ['6', 'ABAC tags', 'project tag match', 'many teams'], ['7', 'Analyze + trim', 'Access Analyzer', 'before and after']], minw=560)

TYPES = ('  <p>Seven techniques, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which ARN does s3:ListBucket need?', 'How do you make “never delete” survive future Allows?', 'Why does ${aws:username} not work for roles?'], 'types 2, 4 and 5') + MAP
         + jump(['Actions', 'Resources', 'Conditions', 'Deny', 'Variables', 'ABAC', 'Analyze']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Plain sentence', 'the requirement in words.', 'Avoids JSON-first mistakes.', '“Faculty may upload notes…”'),
    ('Five answers', 'who, what, which, when, never.', 'Maps to policy elements.', 'See the big picture.'),
    ('Statements', 'one per purpose, with Sid.', 'Readable and reviewable.', 'ListNotes, ReadWriteNotes, NeverSubmissions.'),
    ('Validation', 'Access Analyzer.', 'Catches typos/risks.', 'validate-policy.'),
    ('Proof', 'simulator + real test.', 'Evidence both ways.', 'allowed / implicitDeny / explicitDeny.'),
    ('Review', 'last accessed, unused access.', 'Stays least-privilege.', 'quarterly.')])

DEEP = ('  <h3>The faculty policy (lab-exam pattern)</h3>\n' + code('json', 'FacultyNotes — list/read/upload notes, private drafts, never submissions, HTTPS only',
 '{\n  "Version": "2012-10-17",\n  "Statement": [\n    {"Sid": "SeeTheBucketInConsole", "Effect": "Allow",\n     "Action": ["s3:ListAllMyBuckets", "s3:GetBucketLocation"], "Resource": "*"},\n    {"Sid": "ListNotesAndOwnDrafts", "Effect": "Allow", "Action": "s3:ListBucket",\n     "Resource": "arn:aws:s3:::edu-content",\n     "Condition": {"StringLike": {"s3:prefix": ["", "notes/*", "drafts/${aws:username}/*"]}}},\n    {"Sid": "ReadWriteNotes", "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"],\n     "Resource": ["arn:aws:s3:::edu-content/notes/*", "arn:aws:s3:::edu-content/drafts/${aws:username}/*"]},\n    {"Sid": "NeverSubmissions", "Effect": "Deny", "Action": "s3:*",\n     "Resource": "arn:aws:s3:::edu-content/submissions/*"},\n    {"Sid": "HttpsOnly", "Effect": "Deny", "Action": "s3:*", "Resource": "*",\n     "Condition": {"Bool": {"aws:SecureTransport": "false"}}}\n  ]\n}') +
 '  <ul><li><b>SeeTheBucketInConsole</b>: the console needs ListAllMyBuckets to show the bucket list — a common “I can upload by CLI but see nothing in the console” fix.</li><li>The empty string <code>""</code> in <code>s3:prefix</code> lets the console show the top-level folders.</li><li>Deletes are not allowed anywhere (implicit deny); add an explicit Deny if the requirement says “must never”.</li></ul>\n'
 '  <h3>Common condition operators</h3>\n' + table(['Operator', 'Use'], [['StringEquals / StringLike', 'exact / wildcard text match'], ['Bool / BoolIfExists', 'true/false keys like SecureTransport, MFA'], ['IpAddress / NotIpAddress', 'source IP ranges'], ['ArnLike', 'match ARNs (e.g. aws:SourceArn)'], ['DateGreaterThan / DateLessThan', 'time windows'], ['ForAnyValue: / ForAllValues:', 'multi-valued keys like tag lists']], minw=440))

clouds = vendor_tabs('<p><b>AWS:</b> JSON policies with actions, ARNs, conditions; Access Analyzer validation, generation and unused access; ABAC with tags.</p>',
    '<p><b>Azure:</b> custom RBAC role definitions (Actions, NotActions, DataActions) assigned at narrow scopes; ABAC conditions on storage role assignments; Entra Permissions Management.</p>',
    '<p><b>Google Cloud:</b> custom roles with exact permissions, IAM Conditions (CEL expressions), deny policies, IAM Recommender to remove unused permissions.</p>') + \
    cloud3([['Exact permissions', 'actions list', 'custom role Actions/DataActions', 'custom role permissions'], ['Conditions', 'Condition block', 'role assignment conditions', 'IAM Conditions (CEL)'], ['Trim unused', 'Access Analyzer unused access', 'Permissions Management', 'IAM Recommender']])

MOCKA.extend([
 mock('aws', ['IAM', 'Policies', 'Create policy', 'JSON'], ['Visual', 'JSON'], 'JSON', [('Policy editor', '{ "Statement": [ … ] }'), ('Validation', '0 errors · 0 security warnings · 1 suggestion')], 'Next'),
 mock('aws', ['IAM', 'User groups', 'Faculty'], ['Users', 'Permissions', 'Access Advisor'], 'Permissions', [('Attached policy', 'FacultyNotes (customer managed)'), ('Members', 'meena · arjun')], 'Add users'),
 mock('aws', ['IAM', 'Policy Simulator'], ['Users, Groups, Roles', 'Policy Simulator'], 'Policy Simulator', [('Service', '▾ Amazon S3'), ('Actions', 'GetObject, PutObject, DeleteObject'), ('Resource', 'arn:aws:s3:::edu-content/submissions/a1.txt')], 'Run Simulation'),
])

STEP1 = astep('1 · Write the policy and validate it before use',
    ['[[IAM]] → [[Policies]] → [[Create policy]] → [[JSON]] → paste FacultyNotes (Deep dive), change the bucket name.', 'Look at the validation panel under the editor: errors, warnings, suggestions. Introduce a typo (s3:GetObjects) and watch it appear.'],
    "ACC=$(aws sts get-caller-identity --query Account --output text); B=edu-lp-$ACC\naws s3 mb s3://$B --region ap-south-1\nfor k in notes/l1.txt submissions/a1.txt; do echo x | aws s3 cp - s3://$B/$k; done\ncat > faculty.json <<EOF\n{\"Version\":\"2012-10-17\",\"Statement\":[\n{\"Effect\":\"Allow\",\"Action\":[\"s3:ListAllMyBuckets\",\"s3:GetBucketLocation\"],\"Resource\":\"*\"},\n{\"Effect\":\"Allow\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::$B\",\"Condition\":{\"StringLike\":{\"s3:prefix\":[\"\",\"notes/*\",\"drafts/\\${aws:username}/*\"]}}},\n{\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\"],\"Resource\":[\"arn:aws:s3:::$B/notes/*\",\"arn:aws:s3:::$B/drafts/\\${aws:username}/*\"]},\n{\"Effect\":\"Deny\",\"Action\":\"s3:*\",\"Resource\":\"arn:aws:s3:::$B/submissions/*\"}]}\nEOF\naws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://faculty.json --query 'findings[].[findingType,issueCode]' --output text\nsed 's/s3:GetObject\"/s3:GetObjects\"/' faculty.json > bad.json\naws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://bad.json --query 'findings[].[findingType,issueCode]' --output text",
    'little or nothing for the good policy (maybe a SUGGESTION), then an <code>ERROR</code> finding such as <code>INVALID_ACTION</code> for the typo — caught before anyone used it.',
    'Validation is free and takes a second — run it on every policy, ideally in your CI pipeline.')

STEP2 = astep('2 · Faculty group with two members — prove four actions',
    ['[[Policies]] → create <code>FacultyNotes</code>; [[User groups]] → create <code>Faculty</code> → attach it; [[Users]] → create <code>meena</code> and <code>arjun</code> → add to Faculty.', '[[Policy Simulator]] → choose user meena → S3 → test the four actions below.'],
    "POL=$(aws iam create-policy --policy-name FacultyNotes --policy-document file://faculty.json --query Policy.Arn --output text)\naws iam create-group --group-name Faculty >/dev/null; aws iam attach-group-policy --group-name Faculty --policy-arn $POL\nfor u in meena arjun; do aws iam create-user --user-name $u >/dev/null; aws iam add-user-to-group --group-name Faculty --user-name $u; done\nsleep 10; U=arn:aws:iam::$ACC:user/meena\nsim(){ aws iam simulate-principal-policy --policy-source-arn $U --action-names $1 --resource-arns $2 --query 'EvaluationResults[0].EvalDecision' --output text; }\necho \"PutObject notes/l2.txt:        $(sim s3:PutObject arn:aws:s3:::$B/notes/l2.txt)\"\necho \"GetObject submissions/a1.txt:   $(sim s3:GetObject arn:aws:s3:::$B/submissions/a1.txt)\"\necho \"DeleteObject notes/l1.txt:      $(sim s3:DeleteObject arn:aws:s3:::$B/notes/l1.txt)\"\necho \"PutObject drafts/meena/d.txt:   $(sim s3:PutObject arn:aws:s3:::$B/drafts/meena/d.txt)\"",
    '<code>allowed</code>, <code>explicitDeny</code>, <code>implicitDeny</code>, <code>allowed</code> — the policy does exactly what the requirement says. Adding a third faculty member next semester = one <code>add-user-to-group</code>.',
    'explicitDeny (a written never) and implicitDeny (simply not allowed) are different — explain both in your evidence.')

STEP3 = astep('3 · Per-user folders with one policy (${aws:username})',
    ['Policy Simulator: test user <b>arjun</b> on <code>drafts/meena/d.txt</code> and <code>drafts/arjun/d.txt</code>.'],
    "U2=arn:aws:iam::$ACC:user/arjun\nfor k in drafts/meena/d.txt drafts/arjun/d.txt; do\n  echo \"arjun PutObject $k: $(aws iam simulate-principal-policy --policy-source-arn $U2 --action-names s3:PutObject --resource-arns arn:aws:s3:::$B/$k --query 'EvaluationResults[0].EvalDecision' --output text)\"\ndone",
    '<code>implicitDeny</code> for meena’s drafts and <code>allowed</code> for arjun’s own — one policy, private folders for every member.',
    'The simulator substitutes ${aws:username} with the user being simulated — exactly what happens at runtime.')

prac = practical(AWS_INTRO + ' You will create a bucket, a policy, a group and two users, then delete everything. Cost: zero.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup="<code>for u in meena arjun; do aws iam remove-user-from-group --group-name Faculty --user-name $u; aws iam delete-user --user-name $u; done; aws iam detach-group-policy --group-name Faculty --policy-arn $POL; aws iam delete-group --group-name Faculty; aws iam delete-policy --policy-arn $POL; aws s3 rb s3://$B --force</code>")

mist = mistakes([
    ['Fixing AccessDenied with s3:* or AdministratorAccess.', 'Pressure to make it work.', 'Add the exact action/ARN the message names.'],
    ['ListBucket on an object ARN.', 'Copy-paste.', 'Bucket ARN for ListBucket; bucket/prefix/* for objects.'],
    ['Forgetting ListAllMyBuckets for console users.', 'CLI works, console does not.', 'Add ListAllMyBuckets + GetBucketLocation on *.'],
    ['Relying on implicit deny for must-never rules.', 'Seems enough.', 'Explicit Deny survives future Allows.'],
    ['${aws:username} for roles.', 'Assumed it works everywhere.', 'Use tags or session names for roles.'],
    ['Never reviewing old permissions.', 'Set and forget.', 'Quarterly last-accessed / unused-access review.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Principle of least privilege; IAM policies (Domain 2).'], ['SAA-C03 / Security Specialty', 'Conditions, explicit deny, ABAC, Access Analyzer, cross-account scoping.'], ['C-DAC lab exams', 'Faculty/accountant/auditor access to specific folders; prove both parts; one action to add members.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Least-privilege way to let a group upload to one folder?', ['s3:* on *', 's3:PutObject on bucket/folder/*', 'AmazonS3FullAccess', 'bucket ACL public-write'], 1, 'Exact action and resource.') + \
    qx('Deny all S3 requests not using HTTPS. Which condition?', ['aws:SecureTransport false', 'aws:SourceIp', 'aws:MultiFactorAuthPresent', 's3:prefix'], 0, 'SecureTransport.') + \
    qx('Tool to generate a policy from a role’s real activity?', ['IAM Access Analyzer policy generation', 'Trusted Advisor', 'Inspector', 'Macie'], 0, 'Access Analyzer.') + \
    qx('Give each user a private folder with one policy?', ['policy variable ${aws:username}', 'one policy per user', 'bucket ACLs', 'SCP'], 0, 'Variables.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, LADDER

assemble_v2(HERE, story_h2='“s3:*” and three lost batches', hook_html=hk,
    narration='EduSpark gave faculty s3:* on everything to stop AccessDenied complaints. A teacher’s cleanup deleted three batches of student submissions. Arjun Sir rewrote the policy with the five questions and an explicit never-list.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Writing least-privilege policies',
    formal='<b>Least privilege</b> is the practice of granting each identity only the permissions required to perform its tasks — specific actions on specific resources under specific conditions — and no more; in AWS it is implemented with precisely scoped IAM policies, explicit deny guard-rails, conditions, policy variables and attribute-based access control, and maintained through validation, testing and periodic removal of unused permissions.',
    simple='Give exactly what the job needs — specific actions, on specific folders, under the right conditions — and write down what must never happen.',
    interview=['“I write policies from five questions — who, what action, which resource, under what condition, what must never happen — validate them with Access Analyzer and prove allow and deny with the simulator.”', '“For faculty: ListBucket with an s3:prefix condition, Get/PutObject on notes/*, an explicit Deny on submissions/*, and a group so new members are one action.”'],
    terms_rows=[('Least privilege', 'Only what is needed.'), ('Exact action', 'service:Operation, no wildcard.'), ('Prefix', 'Folder-like key start in S3.'), ('Condition key', 'Request fact used in conditions.'), ('Explicit deny', 'Written never; always wins.'), ('Policy variable', '${aws:username} etc.'), ('ABAC', 'Access by matching tags.'), ('Access Analyzer', 'Validate, generate, find unused access.')],
    exam='Least privilege is the most repeated phrase in AWS security exam questions; lab exams test it with folder-level requirements.',
    picture_h2='Five questions that write any policy', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven least-privilege techniques, one by one', TYPES)],
    how_h2='The least-privilege loop', how_intro='How professionals write, check and maintain a policy.', how_anim=SOLVE,
    parts_h2='Six parts of writing a policy well', parts_html=parts, lv='',
    myth_rows=[('Least privilege slows teams down.', 'The AccessDenied loop is fast; incidents are slow.', 'Animation.'), ('Implicit deny is enough for must-never rules.', 'A future Allow can open it; explicit Deny cannot be overridden.', 'Type 4.'), ('Wildcards are fine if the bucket is private.', 'They include delete and policy changes.', 'Situation.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'The faculty policy line by line; condition operators', DEEP), ('hood', 'Under the hood', 'How conditions and variables are evaluated; limits; NotAction traps', HOOD), ('roles', 'By role', 'Least privilege for developers, data, ML, DevOps and security', ROLES), ('domains', 'By domain', 'Least-privilege patterns by industry', DOMAINS), ('pro', 'For working professionals', 'Errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Write, validate and prove the faculty policy — every result appears on the map.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Turn a requirement into a policy with five questions.', 'Use exact actions, ARNs, prefixes and conditions.', 'Add explicit Deny guards for must-never rules.', 'Use policy variables and tags to scale.', 'Validate, prove and trim policies.'],
    next_html='<a href="../04-encryption-with-kms/">2.4 Encryption with KMS</a>.',
    pre='<b>Before you start:</b> Lessons 2.1 and 2.2.')
