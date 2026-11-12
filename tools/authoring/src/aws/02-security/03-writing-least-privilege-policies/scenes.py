from cloudkit import *

def loop_scene():
    st = sa_people(20, 40, 1) + t(28, 76, 'Meena (faculty)', 7.6, 'ink', bold=True)
    st += sa_screen(12, 90, 200, 80, 'Faculty policy (v1)', ['{ "Effect": "Allow",', '  "Action": "s3:PutObject",', '  "Resource": "…/notes/*" }'], dark=True)
    st += sa_building(232, 14, 394, 300, 'Least-privilege loop', 'green')
    stages = [('1', 'Start from nothing', 'deny all by default', 'grey', 252, 40), ('2', 'Try the real task', 'read the AccessDenied', 'red', 446, 40), ('3', 'Add exact action + ARN', 'nothing more', 'blue', 446, 140), ('4', 'Validate', 'Access Analyzer', 'violet', 252, 140), ('5', 'Simulate allow + deny', 'Policy Simulator', 'amber', 252, 240), ('6', 'Trim unused', 'last-accessed data', 'green', 446, 240)]
    for n, a, b, tn, x, y in stages:
        st += box(x, y, 164, 54, tn if tn != 'grey' else 'card', rx=8) + t(x + 92, y + 24, a, 8.2, 'ink', bold=True) + t(x + 92, y + 40, b, 6.8, 'ink2') + f'<circle cx="{x + 16}" cy="{y + 16}" r="9" style="fill:{SA_COL.get(tn, "#7A8496")}"/><text x="{x + 16}" y="{y + 19.5}" text-anchor="middle" font-size="9" font-weight="700" style="fill:#fff">{n}</text>'
    st += arrow(416, 67, 444, 67) + arrow(528, 94, 528, 138) + arrow(444, 167, 418, 167) + arrow(334, 194, 334, 238) + arrow(416, 267, 444, 267)
    P = [(252, 40), (446, 40), (446, 140), (252, 140), (252, 240), (446, 240)]
    hl = lambda i: f'<rect class="sa-glow" x="{P[i][0] - 3}" y="{P[i][1] - 3}" width="170" height="60" rx="10" style="fill:none;stroke:#E0A100;stroke-width:3"/>'
    f1 = hl(0) + sa_badge(220, 22, 1, 'grey') + sa_note(112, 196, 196, ['New identity = no permissions', 'AWS denies everything until', 'a policy says Allow'], 'grey')
    f2 = hl(1) + sa_flow('M212 120 C320 110 420 80 446 70', 'red', 1.2, 3) + sa_pill(112, 186, 'AccessDenied: s3:ListBucket on edu-content', 'red', 220) + sa_badge(220, 22, 2, 'red') + sa_note(112, 214, 196, ['The error names the exact', 'action and resource missing', '— your shopping list'], 'red')
    f3 = hl(2) + '<g class="sa-pop">' + sa_screen(12, 90, 200, 100, 'Faculty policy (v2)', ['+ { "Action": "s3:ListBucket",', '    "Resource": "…:::edu-content",', '    "Condition": {"StringLike":', '      {"s3:prefix": ["notes/*"]}}}'], dark=True) + '</g>' + sa_badge(220, 22, 3, 'blue') + sa_note(112, 214, 196, ['Add only what the error', 'asked for, scoped to the', 'notes/ prefix'], 'blue')
    f4 = hl(3) + sa_flow('M446 167 L418 167', 'violet', 0.8, 2) + sa_pill(334, 128, '0 errors · 0 security warnings', 'violet', 180) + sa_badge(220, 22, 4, 'violet') + sa_note(112, 214, 196, ['Access Analyzer checks', 'grammar, typos and risky', 'patterns (e.g. iam:PassRole *)'], 'violet')
    f5 = hl(4) + '<g class="sa-pop">' + sa_screen(12, 90, 210, 90, 'simulate-principal-policy', ['PutObject notes/l2.pdf    allowed', 'GetObject submissions/x   explicitDeny', 'DeleteObject notes/l1.pdf implicitDeny'], dark=True) + '</g>' + sa_tick(222, 104, 7) + sa_cross(222, 128, 7) + sa_cross(222, 152, 7) + sa_badge(220, 22, 5, 'amber') + sa_note(112, 214, 196, ['Prove both sides before', 'anyone uses it'], 'saffron')
    f6 = hl(5) + sa_pill(528, 304, '70% unused for 90 days → remove', 'green', 190) + sa_badge(220, 22, 6, 'green') + sa_note(112, 214, 196, ['Months later: last-accessed', 'data shows what is unused;', 'trim it. Repeat.'], 'green')
    return scene_anim('The least-privilege loop', 'How professionals write a policy: start from nothing, let real AccessDenied messages tell you what to add, validate, prove, and trim.', 'Least privilege',
        'Animation: start with no permissions; try the task and read AccessDenied; add the exact action and resource; validate with Access Analyzer; simulate allowed and denied actions; trim unused permissions later.',
        st, [(f1, 'Step 1 · Start from nothing', 'a new user, group or role has no permissions; every request is an implicit deny.'),
             (f2, 'Step 2 · Try the real task', 'Meena tries to list notes/; the AccessDenied message names the exact action (s3:ListBucket) and resource.'),
             (f3, 'Step 3 · Add exactly that', 'add s3:ListBucket on the bucket ARN with an s3:prefix condition for notes/* — not s3:* on *.'),
             (f4, 'Step 4 · Validate', 'IAM Access Analyzer policy validation catches typos (s3:GetObjects), wrong ARNs and risky patterns before deployment.'),
             (f5, 'Step 5 · Prove both sides', 'the Policy Simulator shows uploads to notes/ allowed, submissions/ explicitly denied, deletes implicitly denied.'),
             (f6, 'Step 6 · Trim over time', 'last-accessed information and Access Analyzer unused-access findings show permissions nobody uses — remove them.')], hid='lploop')

def star_vs_scoped():
    o = t(320, 16, '“s3:*” on “*” vs a scoped policy', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 210, 'Too broad', 'red') + sa_building(328, 28, 300, 210, 'Least privilege', 'green')
    o += sa_screen(24, 46, 276, 50, 'FacultyPolicy (bad)', ['{"Effect":"Allow","Action":"s3:*",', ' "Resource":"*"}'], dark=True)
    o += ''.join(t(26, 116 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✘ every bucket in the account, incl. finance', '✘ delete, change policies, make public', '✘ read every student submission', '✘ one mistake or stolen password = everything']))
    o += sa_cross(290, 46, 10)
    o += sa_screen(340, 46, 276, 62, 'FacultyPolicy (good)', ['ListBucket edu-content  prefix notes/*', 'Get/PutObject edu-content/notes/*', 'Deny *  edu-content/submissions/*'], dark=True)
    o += ''.join(t(342, 128 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✓ one bucket, one folder', '✓ upload and read notes only', '✓ submissions invisible — even if someone adds Allows', '✓ new faculty: add to group, done']))
    o += sa_tick(606, 46, 10)
    return bigfig('Comparison: a policy allowing s3:* on all resources gives access to every bucket and action; a scoped policy allows list, read and upload in the notes folder of one bucket and explicitly denies submissions.', o, h=250)

def five_questions():
    o = t(320, 16, 'Five questions that write any policy', 11, 'ink', bold=True)
    Q = [('WHO?', 'Faculty group', 'Principal (implied by where it is attached)', 'blue'), ('DOES WHAT?', 'list, read, upload', 'Action: s3:ListBucket, s3:GetObject, s3:PutObject', 'amber'), ('ON WHICH THING?', 'notes/ in edu-content', 'Resource: arn:aws:s3:::edu-content/notes/*', 'green'), ('WHEN / HOW?', 'only with MFA, only over HTTPS', 'Condition: aws:MultiFactorAuthPresent, aws:SecureTransport', 'violet'), ('NEVER?', 'submissions, deletes', 'Effect: Deny … submissions/*', 'red')]
    for i, (q, plain, tech, tn) in enumerate(Q):
        y = 34 + i * 40
        o += box(16, y, 120, 32, tn, rx=6) + t(76, y + 20, q, 8.6, 'ink', bold=True) + arrow(136, y + 16, 158, y + 16)
        o += box(160, y, 150, 32, 'card', rx=6) + t(235, y + 20, plain, 7.8, 'ink') + arrow(310, y + 16, 332, y + 16)
        o += box(334, y, 290, 32, 'card', rx=6) + t(479, y + 20, tech, 6.9, 'ink', mono=True)
    o += t(236, 244, 'plain answer', 7, 'ink2') + t(480, 244, 'policy element', 7, 'ink2')
    return bigfig('Five questions turn a business sentence into a policy: who, does what, on which thing, when or how, and what must never happen, each mapped to a policy element.', o, h=252)
