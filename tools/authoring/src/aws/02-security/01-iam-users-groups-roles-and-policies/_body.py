import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import eval_scene, shared_vs_own, badge_picture
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




hk = hook('On a Monday, TiffinGo’s menu photos vanished from S3. Five people used the same “admin” login. Nobody could say who deleted them.',
    'The fix was not a better password. It was <b>IAM — Identity and Access Management</b>: one identity per person, people placed in <b>groups</b>, each group given only the <b>permissions</b> its job needs, and <b>roles</b> for software. This lesson explains users, groups, roles and policies from zero, shows exactly how AWS decides <b>Allow or Deny</b>, and on <b>your own</b> account (or in the simulator) you will read a real policy, give an intern read-only access to one folder, prove what he can and cannot do, and use a role’s temporary credentials.',
    ['Who (identity) + what (action) + on which thing (resource) = a permission.', 'Default answer is No; an explicit Deny beats any Allow.', 'People get users/SSO; software gets roles — never keys in code.'])

def story_scene():
    o = t(180, 12, 'One login for five people', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Shared “admin”', 8.4, 'ink', bold=True) + t(88, 64, 'photos deleted', 7, 'ink2') + t(88, 78, 'who did it? unknown', 7, 'ink2') + t(88, 92, 'intern had full power', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'IAM done right', 8.4, 'ink', bold=True) + t(272, 64, 'one user per person', 7, 'ink2') + t(272, 78, 'groups + least privilege', 7, 'ink2') + t(272, 92, 'every action traced', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Identity first, permissions second', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: five people share one admin login, photos get deleted and nobody knows who; the intern had full power. Right: one IAM user per person, groups with least privilege, every action traced.', story_scene(), 'Give each person an <tspan font-weight="700" class="s-acc">identity</tspan>, each job a policy.', h=132)
dialogue = '''R> Sir, we changed the admin password. Is that enough?
A> No. Five people still share it. AWS logs show “admin” deleted the photos — not which person.
K> So everyone gets their own login?
A> Yes — an IAM user each (or, better, single sign-on). Then put people in groups: Admins, Developers, Interns. Attach permissions to groups, not to people.
R> And our order app that reads from S3 — does it get a login too?
A> Software gets a role — like a visitor badge with temporary keys that expire. No passwords, no keys in code. Let’s see how AWS decides yes or no.'''

def bigpic():
    o = t(320, 14, 'IAM: who can do what, on which resource', 11, 'ink', bold=True)
    o += sa_building(10, 28, 190, 250, 'WHO (principals)', 'blue')
    for i, (icn, a, b) in enumerate([('user', 'IAM users', 'people (long-term)'), ('role', 'IAM groups', 'collections of users'), ('role', 'IAM roles', 'temporary, assumed'), ('server', 'AWS services', 'EC2, Lambda via roles'), ('globe', 'Federated / SSO', 'Identity Center, Google…')]):
        y = 46 + i * 46
        o += box(22, y, 166, 38, 'blue', rx=6) + ai(icn, 28, y + 8, 0.9) + t(112, y + 17, a, 8, 'ink', bold=True) + t(112, y + 30, b, 6.6, 'ink2')
    o += sa_building(220, 28, 200, 250, 'WHAT (policies, JSON)', 'amber')
    pol = ['{', '  "Effect": "Allow",', '  "Action": "s3:GetObject",', '  "Resource":', '   "arn:aws:s3:::menu/*",', '  "Condition": {…}', '}']
    o += sa_screen(232, 48, 176, 100, 'policy statement', pol)
    o += ''.join(t(236, 170 + i * 15, s, 7, 'ink2', anchor='start') for i, s in enumerate(['identity-based: on users/groups/roles', 'resource-based: on a bucket, queue, key', 'boundaries + SCPs: maximum limits', 'default = deny; explicit Deny wins']))
    o += sa_building(440, 28, 190, 250, 'ON WHAT (resources)', 'green')
    for i, (icn, a) in enumerate([('bucket', 'S3 bucket / object'), ('server', 'EC2 instance'), ('db', 'DynamoDB table'), ('key', 'KMS key'), ('mail', 'SQS queue / SNS topic')]):
        y = 46 + i * 46
        o += box(452, y, 166, 38, 'green', rx=6) + ai(icn, 458, y + 8, 0.9) + t(548, y + 23, a, 8, 'ink', bold=True)
    o += arrow(200, 150, 218, 150) + arrow(420, 150, 438, 150)
    o += t(320, 292, 'Every request: principal + action + resource (+ conditions) → IAM evaluates policies → Allow or Deny.', 7.6, 'ink2')
    return o
BIG = bigfig('IAM big picture: principals (users, groups, roles, AWS services, federated users) are given permissions by JSON policies (identity-based, resource-based, boundaries and SCPs) over resources such as S3 buckets, EC2 instances, DynamoDB tables, KMS keys and queues.', bigpic(), h=300)

picture = (newbie('Think of AWS as a big office building. <b>IAM is the security desk.</b> It gives every person an ID card (<i>user</i>), puts people in departments (<i>groups</i>), hands visitors temporary badges (<i>roles</i>), and keeps a rulebook of which doors each card opens (<i>policies</i>). If the rulebook does not say “yes”, the door stays shut.',
            [('Identity / principal', 'who is asking (a person or a program)'), ('Permission', 'a “yes” for one action on one thing'), ('Policy', 'a written list of permissions (in JSON text)'), ('Action', 'what they want to do, e.g. read a file, delete a file'), ('Resource', 'the thing, e.g. one storage bucket'), ('ARN', 'the full address of a thing in AWS')]) +
    '  <p>IAM answers one question for <b>every</b> request to AWS: <i>is this principal allowed to do this action on this resource right now?</i></p>\n' + BIG +
    '\n  <h3>Situation 1 — the shared login problem</h3>\n' + shared_vs_own() +
    '\n  <h3>Situation 2 — people vs software</h3>\n' + badge_picture() +
    '\n  <h3>IAM facts that matter</h3>\n' + table(['Fact', 'Detail'], [['Cost', 'IAM is free'], ['Scope', 'global — not tied to a Region'], ['Default', 'everything is denied until a policy allows it'], ['Who decides', 'every API call, console click and CLI command passes through IAM'], ['Changes take effect', 'within seconds (eventually consistent)']], minw=460))

SOLVE = eval_scene()

def mapfig():
    o = t(320, 16, 'Seven IAM building blocks', 11, 'ink', bold=True)
    items = [('1', 'IAM user', 'one person / one app', 'blue'), ('2', 'IAM group', 'users with one job', 'violet'), ('3', 'IAM role', 'temporary, assumed', 'amber'), ('4', 'AWS managed policy', 'written by AWS', 'green'),
             ('5', 'Customer managed policy', 'written by you, reusable', 'green'), ('6', 'Inline policy', 'embedded in one identity', 'card'), ('7', 'Resource-based policy', 'on the bucket/queue/key', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–3 are WHO; 4–7 are WHAT. Guard-rails (boundaries, SCPs) are in Under the hood.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven IAM building blocks: IAM user, IAM group, IAM role, AWS managed policy, customer managed policy, inline policy, resource-based policy.', mapfig(), h=222)

def ia(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 2', 'SAA-C03 / Security Specialty', 'C-DAC cloud security'], rw, pro)

A1 = mk(['Create user', 'Credentials', 'Sign in'], ['create|name|e.g. meena', 'creds|password+MFA|keys only if needed', 'use|console / CLI|as herself'], ['blue', 'amber', 'green'],
        ['create one user per person', 'give a console password with MFA (access keys only if truly needed)', 'the person signs in as herself; every action is traced to her'],
        [('Create', 'One per person.', ''), ('Credentials', 'Password + MFA.', ''), ('Use', 'Actions traced to her.', '')], 'IAM user', 'One person, one identity.', 'User', 'Animation: create user; credentials; sign in.', 'i1anim')
T1 = ia(1, 'IAM user', 'blue',
    'An <b>IAM user</b> is an identity inside one AWS account that represents a person or application, with long-term credentials — a console password and/or up to two access keys — and permissions from policies attached directly or through groups.',
    'An employee ID card: one per person, with their name on it.',
    'meena, arjun and kabir each get an IAM user; CloudTrail shows who did what.',
    'Tip: AWS now recommends IAM Identity Center for people; IAM users remain common for small accounts, labs and some legacy tools.', A1,
    'a person needs access and SSO is not set up (labs, small accounts).', 'you are tempted to create one user for a whole team or put its keys in code.',
    'A login for one person inside the account.',
    [('Name', 'Unique in the account.'), ('Password', 'Console sign-in.'), ('MFA', 'Second factor.'), ('Groups', 'Up to 10 per user.'), ('Keys', 'Max 2; avoid.')],
    [('access key', 'long-term CLI/SDK credential (AKIA…)'), ('console password', 'for the web console'), ('credential report', 'CSV of all users and their credentials')],
    table(['', 'IAM user', 'Identity Center user'], [['Credentials', 'long-term', 'short-lived via SSO'], ['Multi-account', 'one account', 'many accounts'], ['AWS recommendation for people', 'only when needed', 'preferred']], minw=420),
    'Exam: “each employee needs access” → individual users/SSO, never shared credentials.',
    'Run the credential report monthly: users without MFA and keys older than 90 days are your top risks.')

A2 = mk(['Create group', 'Attach policy', 'Add users'], ['group|Developers|by job', 'policy|what the job|needs', 'users|inherit|automatically'], ['violet', 'amber', 'green'],
        ['create a group per job function', 'attach the policies that job needs', 'users added to the group inherit the permissions'],
        [('Group', 'By job: Admins, Developers…', ''), ('Policy', 'Permissions on the group.', ''), ('Members', 'Add/remove users — one action.', '')], 'IAM group', 'Permissions by job, not by person.', 'Group', 'Animation: create group; attach policy; add users.', 'i2anim')
T2 = ia(2, 'IAM group', 'violet',
    'An <b>IAM group</b> is a collection of IAM users; policies attached to the group apply to every member, so permissions are managed by job function. Groups cannot be nested, cannot sign in, and cannot be named as a principal in a resource policy.',
    'A department: join Accounts and you get the Accounts keys; move to Sales and you swap keys.',
    'A new faculty member next semester → add her to the Faculty group: one action, no new permissions.',
    'Tip: never attach policies directly to users — always to groups (or permission sets in Identity Center).', A2,
    'several people share a job.', 'you expect a group to be used by software or to contain other groups.',
    'A team folder for users that share the same permissions.',
    [('Name', 'By job.'), ('Policies', 'Up to 10 managed.'), ('Members', 'Users only.'), ('Change', 'Edit once, applies to all.'), ('Audit', 'List group members.')],
    [('job function', 'what a person does'), ('membership', 'being in a group'), ('inheritance', 'members get the group’s policies')],
    table(['', 'Group', 'Role'], [['Contains', 'users', 'no members — assumed'], ['Credentials', 'none of its own', 'temporary'], ['Used by', 'people', 'people, services, other accounts']], minw=420),
    'Lab exams love: “adding a new member must take one action” → group.',
    'Name groups after jobs (Faculty, Accountants) — auditors read them.')

A3 = mk(['Trust policy', 'Assume role', 'Temporary keys'], ['trust|who may|assume it', 'assume|sts:AssumeRole|or attached', 'keys|ASIA… + token|expire'], ['amber', 'blue', 'green'],
        ['the trust policy says who may assume the role', 'a user, service or account assumes it via STS', 'STS returns temporary credentials that expire'],
        [('Trust', 'Who may assume it.', ''), ('Assume', 'STS AssumeRole (or service does it).', ''), ('Use', 'Temporary keys, auto-expire.', '')], 'IAM role', 'A badge, not a card.', 'Role', 'Animation: trust policy; assume role; temporary keys.', 'i3anim')
T3 = ia(3, 'IAM role', 'amber',
    'An <b>IAM role</b> is an identity with permission policies but no long-term credentials; trusted principals (users, AWS services such as EC2 or Lambda, other accounts, federated users) <b>assume</b> it through AWS STS and receive temporary credentials that expire (15 minutes to 12 hours).',
    'A visitor badge at reception: borrowed for a while, returned automatically at the end of the day.',
    'The order app on EC2 uses role <i>TiffinGoAppRole</i> to read the menu bucket — no keys anywhere.',
    'Tip: every role has two policies — a <b>trust policy</b> (who may wear the badge) and <b>permission policies</b> (what the badge opens).', A3,
    'software needs AWS access, or someone needs temporary/cross-account access.', 'you create access keys for an application instead.',
    'A temporary set of permissions that people or programs can borrow.',
    [('Trust policy', 'Who may assume.'), ('Permissions', 'What it can do.'), ('Assume', 'sts:AssumeRole.'), ('Session', '1 h default, up to 12 h.'), ('Audit', 'CloudTrail shows who assumed.')],
    [('STS', 'Security Token Service'), ('trust policy', 'resource policy on the role'), ('session', 'the temporary credentials period')],
    table(['Role type', 'Trusted principal', 'Example'], [['Service role', 'ec2.amazonaws.com', 'app on EC2 reads S3'], ['Cross-account', 'another account ID', 'auditor account reads logs'], ['Federation / SSO', 'identity provider', 'staff sign in with company login']], minw=480),
    'Most-asked IAM exam fact: “application on EC2 needs S3 access” → IAM role (instance profile).',
    'Use AWS service-linked roles where offered — AWS maintains them for you.')

A4 = mk(['AWS writes', 'You attach', 'AWS updates'], ['AWS|maintains|ReadOnlyAccess…', 'attach|to group|or role', 'updates|new actions|added by AWS'], ['green', 'amber', 'blue'],
        ['AWS writes and maintains the policy', 'you attach it to groups, users or roles', 'AWS updates it as services change'],
        [('AWS writes', 'ReadOnlyAccess, AmazonS3ReadOnlyAccess…', ''), ('Attach', 'To groups/roles.', ''), ('Updated', 'By AWS over time.', '')], 'AWS managed policy', 'Quick, broad, maintained.', 'AWS managed', 'Animation: AWS writes; you attach; AWS updates.', 'i4anim')
T4 = ia(4, 'AWS managed policy', 'green',
    'An <b>AWS managed policy</b> is a standalone policy created and maintained by AWS (ARN <code>arn:aws:iam::aws:policy/…</code>), such as AdministratorAccess, ReadOnlyAccess or AmazonS3ReadOnlyAccess, including job-function policies; you can attach but not edit it.',
    'A ready-made uniform from the shop: fits most people, but you cannot tailor it.',
    'The Auditors group gets ReadOnlyAccess in one click.',
    'Tip: AWS managed policies are usually broader than you need — fine for learning, often too wide for production.', A4,
    'you need a quick, standard permission set.', 'you need access to one bucket or one folder — write your own.',
    'Ready-made permission lists written by AWS.',
    [('Find', 'IAM → Policies → AWS managed.'), ('Read', 'Check the JSON.'), ('Attach', 'Group/role.'), ('Watch', 'Version changes.'), ('Narrow', 'Replace later.')],
    [('job-function policy', 'e.g. Billing, DatabaseAdministrator'), ('policy version', 'AWS keeps versions'), ('ARN account “aws”', 'marks AWS managed')],
    table(['Policy', 'Gives'], [['AdministratorAccess', 'everything'], ['PowerUserAccess', 'everything except IAM/Organizations management'], ['ReadOnlyAccess', 'read everything'], ['AmazonS3ReadOnlyAccess', 'read all buckets']], minw=420),
    'Know AdministratorAccess vs PowerUserAccess vs ReadOnlyAccess.',
    'ReadOnlyAccess can still read sensitive data (S3 objects, logs) — read-only is not “harmless”.')

A5 = mk(['Write JSON', 'Create policy', 'Attach + reuse'], ['write|exact actions|exact resources', 'create|versioned|in your account', 'reuse|many groups|or roles'], ['green', 'blue', 'amber'],
        ['write the exact actions and resources needed', 'create it in your account (versioned)', 'attach it to any number of groups/roles'],
        [('Write', 'Exact actions + resources.', ''), ('Create', 'Named, versioned.', ''), ('Reuse', 'Attach to many identities.', '')], 'Customer managed policy', 'Least privilege, reusable.', 'Customer managed', 'Animation: write JSON; create policy; attach and reuse.', 'i5anim')
T5 = ia(5, 'Customer managed policy', 'green',
    'A <b>customer managed policy</b> is a standalone policy you create in your account, with exactly the actions, resources and conditions you choose; it keeps up to five versions and can be attached to many users, groups and roles — the main tool for <b>least privilege</b>.',
    'A tailored uniform: made for your job, reused by everyone with the same job.',
    'Policy <i>S3ReadMenu</i> allows GetObject only on <code>tiffingo-menu/*</code>; attached to Interns and to the app role.',
    'Tip: start from the AWS policy generator or the visual editor, then tighten resources to exact ARNs.', A5,
    'you need precise, reusable permissions.', 'the permission is truly unique to one identity and must die with it (inline).',
    'Your own permission list, written exactly for a job.',
    [('Write', 'JSON / visual editor.'), ('Validate', 'Access Analyzer checks.'), ('Version', 'Up to 5.'), ('Attach', 'Many identities.'), ('Review', 'Last-accessed info.')],
    [('least privilege', 'only what is needed'), ('policy validation', 'Access Analyzer finds errors and risks'), ('default version', 'the active version')],
    table(['', 'AWS managed', 'Customer managed', 'Inline'], [['Who writes', 'AWS', 'you', 'you'], ['Reusable', 'yes', 'yes', 'no'], ['Precise', 'rarely', 'yes', 'yes']], minw=460),
    'Lab exams: “faculty may upload notes but not see submissions” → customer managed policy scoped to a prefix.',
    'Use IAM Access Advisor (last accessed) to remove actions nobody has used in 90 days.')

A6 = mk(['Embed', 'One identity', 'Deleted with it'], ['embed|inside a user|group or role', 'only|that identity|not reusable', 'delete|identity →|policy gone'], ['card', 'amber', 'red'],
        ['the policy is embedded inside one identity', 'it applies only to that identity', 'it is deleted when the identity is deleted'],
        [('Embed', 'Inside one user/group/role.', ''), ('Only there', 'Not reusable.', ''), ('Lifecycle', 'Dies with the identity.', '')], 'Inline policy', 'One-to-one.', 'Inline', 'Animation: embed; one identity; deleted with it.', 'i6anim')
T6 = ia(6, 'Inline policy', 'card',
    'An <b>inline policy</b> is embedded directly in a single user, group or role and has a strict one-to-one relationship with it; it is deleted with the identity and cannot be attached elsewhere — useful when a permission must never be accidentally reused.',
    'A note written on one person’s ID card: it travels with that card only.',
    'A one-off migration role has an inline policy that is deleted together with the role afterwards.',
    'Tip: inline policies are hard to audit across an account — prefer customer managed policies.', A6,
    'a permission must be tied to exactly one identity’s lifetime.', 'you want reuse or central review.',
    'A permission list stuck to one identity only.',
    [('Create', 'On the identity.'), ('Size', 'Small limits.'), ('Review', 'Per identity.'), ('Delete', 'With identity.'), ('Prefer', 'Managed policies.')],
    [('embedded', 'part of the identity'), ('one-to-one', 'one policy, one identity'), ('policy size limit', 'inline ones are smaller')],
    table(['', 'Inline', 'Customer managed'], [['Reuse', 'no', 'yes'], ['Versioning', 'no', 'up to 5'], ['Audit', 'harder', 'easier']], minw=420),
    'Rarely tested directly; know it exists and when it fits.',
    'Search all inline policies with the CLI before audits — they hide permissions.')

A7 = mk(['Policy on resource', 'Names principals', 'Cross-account'], ['attach|bucket, queue|KMS key', 'Principal|who may|access it', 'share|other accounts|services'], ['red', 'amber', 'green'],
        ['the policy is attached to the resource itself', 'it names which principals may act on it', 'it can grant access to other accounts or services'],
        [('Attach', 'To bucket/queue/key/role trust.', ''), ('Principal', 'Says who.', ''), ('Share', 'Cross-account, services, conditions.', '')], 'Resource-based policy', 'The door’s own rule.', 'Resource-based', 'Animation: policy on resource; names principals; cross-account.', 'i7anim')
T7 = ia(7, 'Resource-based policy', 'red',
    'A <b>resource-based policy</b> is attached to a resource — an S3 bucket policy, SQS queue policy, KMS key policy, Lambda resource policy or a role’s trust policy — and includes a <code>Principal</code> element naming who may act on it, enabling cross-account and service access and resource-wide rules such as “deny any request not using HTTPS”.',
    'A notice on a room door: “Only Accounts staff and the auditor may enter; no entry without ID.”',
    'Bucket policy: deny every request where <code>aws:SecureTransport</code> is false — protects the data whoever asks.',
    'Tip: identity policies say what <i>I</i> can do; resource policies say who can touch <i>this thing</i>.', A7,
    'a resource must enforce its own rules or be shared with another account/service.', 'you need to give one internal user access — an identity policy is simpler.',
    'A rulebook stuck on the resource itself.',
    [('Attach', 'Resource.'), ('Principal', 'Who.'), ('Action/Resource', 'What.'), ('Condition', 'HTTPS, IP, org…'), ('Evaluate', 'Together with identity policies.')],
    [('Principal', 'the who in a resource policy'), ('bucket policy', 'resource policy on S3'), ('key policy', 'resource policy on a KMS key')],
    table(['', 'Identity-based', 'Resource-based'], [['Attached to', 'user/group/role', 'bucket/queue/key/role'], ['Has Principal', 'no', 'yes'], ['Cross-account', 'needs both sides', 'can grant directly (for many services)']], minw=460),
    'Exam: “deny non-HTTPS access to a bucket” → bucket policy with aws:SecureTransport.',
    'KMS key policies are mandatory and primary — IAM policies alone cannot use a key unless the key policy allows it.')

SUMMARY = table(['#', 'Block', 'Is it WHO or WHAT?', 'Typical use'], [
    ['1', 'IAM user', 'who (long-term)', 'a person (if no SSO)'], ['2', 'IAM group', 'who (container)', 'permissions by job'], ['3', 'IAM role', 'who (temporary)', 'apps, services, cross-account, SSO'],
    ['4', 'AWS managed policy', 'what', 'quick standard access'], ['5', 'Customer managed policy', 'what', 'least privilege, reusable'], ['6', 'Inline policy', 'what', 'one-off, tied to one identity'], ['7', 'Resource-based policy', 'what (+ who)', 'bucket/key/queue rules, sharing']], minw=600)

TYPES = ('  <p>Seven IAM building blocks, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which wins: an Allow in a group policy or a Deny in a bucket policy?', 'Why can a group not be the Principal in a bucket policy?', 'What two policies does every role have?'], 'types 7, 2 and 3') + MAP
         + jump(['User', 'Group', 'Role', 'AWS managed', 'Customer managed', 'Inline', 'Resource-based']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Effect', 'Allow or Deny.', 'Deny always wins.', '<code>"Effect": "Allow"</code>'),
    ('Action', 'service:Operation.', 'What is permitted.', '<code>"s3:GetObject"</code>, wildcards <code>s3:Get*</code>'),
    ('Resource', 'ARN(s).', 'On which thing.', '<code>arn:aws:s3:::menu/notes/*</code>'),
    ('Principal', 'who (resource policies only).', 'Who may act on this resource.', '<code>{"AWS": "arn:aws:iam::111122223333:root"}</code>'),
    ('Condition', 'when/how (optional).', 'MFA, IP, HTTPS, tags, time.', '<code>"Bool": {"aws:SecureTransport": "false"}</code>'),
    ('Sid / Version', 'statement ID; language version.', 'Readability; always "2012-10-17".', '<code>"Version": "2012-10-17"</code>')])

DEEP = ('  <h3>A complete policy, line by line</h3>\n' + code('json', 'S3ReadMenu — read the menu folder only, and only over HTTPS',
 '{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Sid": "ListOnlyMenuFolder",\n      "Effect": "Allow",\n      "Action": "s3:ListBucket",\n      "Resource": "arn:aws:s3:::tiffingo-menu",\n      "Condition": {"StringLike": {"s3:prefix": ["menu/*"]}}\n    },\n    {\n      "Sid": "ReadMenuObjects",\n      "Effect": "Allow",\n      "Action": "s3:GetObject",\n      "Resource": "arn:aws:s3:::tiffingo-menu/menu/*"\n    },\n    {\n      "Sid": "NoPlainHttp",\n      "Effect": "Deny",\n      "Action": "s3:*",\n      "Resource": ["arn:aws:s3:::tiffingo-menu", "arn:aws:s3:::tiffingo-menu/*"],\n      "Condition": {"Bool": {"aws:SecureTransport": "false"}}\n    }\n  ]\n}') +
 '  <ul><li><b>ListBucket</b> applies to the <i>bucket</i> ARN; <b>GetObject</b> applies to <i>object</i> ARNs (<code>bucket/key</code>). Mixing them up is the #1 S3 policy bug.</li><li><code>s3:prefix</code> limits what folder names can be listed.</li><li>The Deny statement wins over any Allow when the request is not HTTPS.</li></ul>\n'
 '  <h3>Identity-based vs resource-based, together</h3>\n' + table(['Same account?', 'Identity policy Allow', 'Resource policy Allow', 'Result (no Deny anywhere)'], [['yes', 'yes', 'no', 'allowed'], ['yes', 'no', 'yes (names the user/role)', 'allowed'], ['no (cross-account)', 'yes', 'yes', 'allowed'], ['no (cross-account)', 'yes', 'no', 'denied — both sides needed']], minw=560))

clouds = vendor_tabs('<p><b>AWS:</b> IAM users, groups, roles, JSON policies (identity and resource), IAM Identity Center for SSO, Organizations SCPs.</p>',
    '<p><b>Azure:</b> Microsoft Entra ID users and groups, managed identities for apps, Azure RBAC role assignments at a scope; Azure Policy for resource rules.</p>',
    '<p><b>Google Cloud:</b> Google accounts and groups, service accounts for apps, IAM role bindings on resources (allow policies), deny policies, organisation policies.</p>') + \
    cloud3([['Person', 'IAM user / Identity Center user', 'Entra ID user', 'Google account'], ['Team', 'IAM group', 'Entra group', 'Google group'], ['App identity', 'IAM role', 'managed identity', 'service account'], ['Permission set', 'policy (JSON)', 'role definition + assignment', 'role + binding']])

MOCKA.extend([
 mock('aws', ['IAM', 'Policies', 'AmazonS3ReadOnlyAccess'], ['Permissions', 'Entities attached', 'Policy versions'], 'Permissions', [('Type', 'AWS managed'), ('JSON', '"Action": ["s3:Get*", "s3:List*", …]')], 'Edit (not allowed)'),
 mock('aws', ['IAM', 'Policies', 'Create policy'], ['Visual', 'JSON'], 'JSON', [('Policy name', 'S3ReadMenu'), ('Statements', 'Allow s3:GetObject on tiffingo-menu/menu/*')], 'Create policy'),
 mock('aws', ['IAM', 'Roles', 'Create role'], ['Trusted entity', 'Permissions', 'Name'], 'Trusted entity', [('Trusted entity type', '( ) AWS account · this account'), ('Role name', 'MenuReader'), ('Max session duration', '1 hour')], 'Create role'),
])

STEP1 = astep('1 · Read a real AWS policy (anatomy)',
    ['[[IAM]] → [[Policies]] → search <code>AmazonS3ReadOnlyAccess</code> → [[Permissions]] tab → switch to JSON.', 'Note: Version, Statement, Effect, Action (with wildcards), Resource.'],
    "ARN=arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess\nV=$(aws iam get-policy --policy-arn $ARN --query Policy.DefaultVersionId --output text)\naws iam get-policy-version --policy-arn $ARN --version-id $V --query PolicyVersion.Document\naws iam list-entities-for-policy --policy-arn $ARN",
    'the JSON document with <code>"Effect": "Allow"</code>, actions like <code>s3:Get*</code> and <code>s3:List*</code> and <code>"Resource": "*"</code>, then which users/groups/roles use it (probably none).',
    'Every permission in AWS — whoever wrote it — is this same JSON shape. Learn to read it and you can read any policy.')

STEP2 = astep('2 · Give an intern read-only access to one folder — and prove both sides',
    ['[[S3]]: create bucket <code>iam-lab-ACCOUNTID</code> with folders <code>menu/</code> and <code>finance/</code>.', '[[IAM]] → [[Policies]] → [[Create policy]] → JSON from the Deep dive (change the bucket name) → name <code>S3ReadMenu</code>.', '[[User groups]] → create <code>Interns</code> → attach <code>S3ReadMenu</code>; [[Users]] → create <code>intern-kabir</code> (no console access needed) → add to Interns.', '[[Users]] → intern-kabir → [[Permissions]] → [[Simulate]] (Policy Simulator) → test GetObject on menu/ and finance/, DeleteObject on menu/.'],
    "ACC=$(aws sts get-caller-identity --query Account --output text); B=iam-lab-$ACC\naws s3 mb s3://$B --region ap-south-1\necho menu > m.txt; echo secret > f.txt\naws s3 cp m.txt s3://$B/menu/m.txt; aws s3 cp f.txt s3://$B/finance/f.txt\ncat > s3readmenu.json <<EOF\n{\"Version\":\"2012-10-17\",\"Statement\":[\n {\"Effect\":\"Allow\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::$B\",\"Condition\":{\"StringLike\":{\"s3:prefix\":[\"menu/*\"]}}},\n {\"Effect\":\"Allow\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$B/menu/*\"}]}\nEOF\nPOL=$(aws iam create-policy --policy-name S3ReadMenu --policy-document file://s3readmenu.json --query Policy.Arn --output text)\naws iam create-group --group-name Interns >/dev/null\naws iam attach-group-policy --group-name Interns --policy-arn $POL\naws iam create-user --user-name intern-kabir >/dev/null\naws iam add-user-to-group --group-name Interns --user-name intern-kabir\nsleep 10\nU=arn:aws:iam::$ACC:user/intern-kabir\nfor a in \"s3:GetObject arn:aws:s3:::$B/menu/m.txt\" \"s3:GetObject arn:aws:s3:::$B/finance/f.txt\" \"s3:DeleteObject arn:aws:s3:::$B/menu/m.txt\"; do\n  set -- $a\n  aws iam simulate-principal-policy --policy-source-arn $U --action-names $1 --resource-arns $2 \\\n    --query 'EvaluationResults[0].[EvalActionName,EvalResourceName,EvalDecision]' --output text\ndone",
    'three lines: <code>s3:GetObject …/menu/m.txt allowed</code>, <code>s3:GetObject …/finance/f.txt implicitDeny</code>, <code>s3:DeleteObject …/menu/m.txt implicitDeny</code> — proof of both what he can and cannot do.',
    'The Policy Simulator evaluates the real policies attached to intern-kabir (through the Interns group) without needing his password or keys — the professional way to prove permissions.')

STEP3 = astep('3 · Use a role: temporary credentials in action',
    ['[[IAM]] → [[Roles]] → [[Create role]] → Trusted entity [[AWS account]] → This account → attach <code>S3ReadMenu</code> → name <code>MenuReader</code>.', 'Top-right account menu → [[Switch role]] → your account ID + MenuReader → open S3: menu/ works, finance/ shows Access Denied.'],
    "ACC=$(aws sts get-caller-identity --query Account --output text)\ncat > trust.json <<EOF\n{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::$ACC:root\"},\"Action\":\"sts:AssumeRole\"}]}\nEOF\naws iam create-role --role-name MenuReader --assume-role-policy-document file://trust.json --query Role.Arn --output text\naws iam attach-role-policy --role-name MenuReader --policy-arn arn:aws:iam::$ACC:policy/S3ReadMenu\nsleep 10\nCREDS=$(aws sts assume-role --role-arn arn:aws:iam::$ACC:role/MenuReader --role-session-name lab --query Credentials --output json)\necho \"$CREDS\" | python3 -c \"import sys,json; c=json.load(sys.stdin); print(c['AccessKeyId'][:4]+'…', 'expires', c['Expiration'])\"\nexport AWS_ACCESS_KEY_ID=$(echo $CREDS | python3 -c \"import sys,json;print(json.load(sys.stdin)['AccessKeyId'])\")\nexport AWS_SECRET_ACCESS_KEY=$(echo $CREDS | python3 -c \"import sys,json;print(json.load(sys.stdin)['SecretAccessKey'])\")\nexport AWS_SESSION_TOKEN=$(echo $CREDS | python3 -c \"import sys,json;print(json.load(sys.stdin)['SessionToken'])\")\naws sts get-caller-identity --query Arn --output text\naws s3 cp s3://iam-lab-$ACC/menu/m.txt - ; aws s3 cp s3://iam-lab-$ACC/finance/f.txt - ; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN",
    '<code>ASIA… expires 2026-…</code> (temporary key, one hour), the identity <code>assumed-role/MenuReader/lab</code>, the word <code>menu</code>, then <code>AccessDenied</code> for finance — the role can do exactly what its policy says, and nothing more.',
    'Temporary keys start with ASIA (long-term ones with AKIA) and need a session token. When they expire, they are useless to anyone who copied them.')

prac = practical(AWS_INTRO + ' You will create a bucket, a policy, a group, a user and a role, then delete everything. Cost: zero.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup="<code>ACC=$(aws sts get-caller-identity --query Account --output text); aws iam detach-role-policy --role-name MenuReader --policy-arn arn:aws:iam::$ACC:policy/S3ReadMenu; aws iam delete-role --role-name MenuReader; aws iam remove-user-from-group --group-name Interns --user-name intern-kabir; aws iam delete-user --user-name intern-kabir; aws iam detach-group-policy --group-name Interns --policy-arn arn:aws:iam::$ACC:policy/S3ReadMenu; aws iam delete-group --group-name Interns; aws iam delete-policy --policy-arn arn:aws:iam::$ACC:policy/S3ReadMenu; aws s3 rb s3://iam-lab-$ACC --force</code>")

mist = mistakes([
    ['Sharing one login across a team.', 'Convenience.', 'One identity per person; groups for permissions.'],
    ['Attaching policies directly to users.', 'Fastest click.', 'Attach to groups/roles; users inherit.'],
    ['Access keys in code or on EC2.', 'Old tutorials.', 'Roles: instance profiles, Lambda execution roles.'],
    ['Using AdministratorAccess for everyone.', 'Avoids AccessDenied.', 'Start narrow; widen from real AccessDenied messages.'],
    ['Wrong ARN form for S3 (bucket vs object).', 'Looks similar.', 'ListBucket → bucket ARN; Get/Put/DeleteObject → bucket/key ARN.'],
    ['Thinking ReadOnlyAccess is harmless.', '“Only reading.”', 'It can read every object and secret-looking data.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Users, groups, roles, policies; least privilege; root vs IAM users; MFA (Domain 2).'], ['SAA-C03', 'Roles for EC2/Lambda, cross-account roles, resource policies, policy evaluation.'], ['C-DAC PGCP-BDA / lab exams', 'Faculty/accountant/auditor groups; server roles with folder-level access; prove allow and deny.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('An application on EC2 needs to read S3. Most secure option?', ['store access keys on the instance', 'IAM role attached to the instance', 'root credentials', 'make the bucket public'], 1, 'Role → temporary credentials.') + \
    qx('A user has an Allow from a group and a Deny from a bucket policy for the same action. Result?', ['allowed', 'denied', 'depends on order', 'allowed only in the console'], 1, 'Explicit deny always wins.') + \
    qx('Best way to give 20 developers the same permissions?', ['attach policies to each user', 'IAM group with the policy', 'share one user', 'inline policy on each user'], 1, 'Groups.') + \
    qx('What does an IAM role’s trust policy define?', ['what the role can do', 'who can assume the role', 'the role’s password', 'the Region'], 1, 'Trust = who.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, LADDER

assemble_v2(HERE, story_h2='Five people, one login, deleted photos', hook_html=hk,
    narration='TiffinGo’s menu photos were deleted. Five people shared the admin login, so CloudTrail could only say “admin did it”. Arjun Sir rebuilt access with IAM: one identity per person, groups by job, roles for software.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='IAM: users, groups, roles and policies',
    formal='<b>AWS Identity and Access Management (IAM)</b> is the global, no-cost service that controls authentication and authorisation in an AWS account: it defines <b>principals</b> (IAM users, groups of users, and roles assumed for temporary access) and evaluates <b>policies</b> — JSON documents allowing or denying actions on resources under conditions — for every request, denying by default and letting an explicit deny override any allow.',
    simple='IAM is AWS’s security desk: it gives people and programs identities, and written rules decide exactly what each one may do.',
    interview=['“IAM authenticates and authorises every AWS request: users or SSO for people, roles with temporary credentials for applications, and JSON policies with least privilege; default deny, explicit deny wins.”', '“For an app on EC2 reading S3 I attach a role through an instance profile with a customer managed policy scoped to the exact bucket prefix — no keys anywhere.”'],
    terms_rows=[('Principal', 'Who makes the request.'), ('IAM user', 'Long-term identity.'), ('IAM group', 'Collection of users.'), ('IAM role', 'Assumable identity, temporary credentials.'), ('Policy', 'JSON permissions.'), ('Least privilege', 'Only what is needed.'), ('Implicit deny', 'No Allow found → denied.'), ('Explicit deny', '"Effect": "Deny" — always wins.')],
    exam='CLF-C02 Domain 2 (30%) is built on IAM; SAA-C03 tests roles, resource policies and evaluation logic.',
    picture_h2='IAM: who, what, on which resource', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven IAM building blocks, one by one', TYPES)],
    how_h2='How IAM decides: Allow or Deny', how_intro='One request, evaluated step by step.', how_anim=SOLVE,
    parts_h2='Six parts of a policy statement', parts_html=parts, lv='',
    myth_rows=[('A strong shared password is fine.', 'Sharing removes accountability.', 'Situation 1.'), ('Allow beats Deny if it is more specific.', 'Explicit Deny always wins.', 'Animation.'), ('Roles are only for AWS services.', 'People and other accounts assume roles too.', 'Type 3.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'A complete policy line by line; identity + resource policies together', DEEP), ('hood', 'Under the hood', 'Full evaluation logic, boundaries, SCPs, STS, propagation, limits', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use IAM', ROLES), ('domains', 'By domain', 'IAM patterns by industry', DOMAINS), ('pro', 'For working professionals', 'Quotas, errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Build the intern’s access and prove allow and deny — the diagram shows each identity and policy as you create it.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Explain users, groups, roles and the four kinds of policies.', 'Read and write a least-privilege JSON policy.', 'Explain how IAM decides Allow or Deny.', 'Prove allowed and denied actions with the Policy Simulator.', 'Use a role and its temporary credentials.'],
    next_html='<a href="../02-iam-roles-for-ec2-and-instance-profiles/">2.2 IAM roles for EC2 and instance profiles</a>.',
    pre='<b>Before you start:</b> Module 1 (an admin user with MFA, CloudShell).')
