from cloudkit import *

def eval_scene():
    """IAM policy evaluation for an intern's DeleteObject request."""
    st = sa_people(16, 120, 1) + t(24, 156, 'intern-kabir', 7.6, 'ink', bold=True) + t(24, 167, 'group: Interns', 6.6, 'ink2')
    st += sa_screen(40, 70, 150, 40, 'CloudShell', ['$ aws s3 rm s3://tiffingo-menu/', '    menu.pdf'], dark=True)
    st += sa_building(206, 14, 420, 300, 'IAM — evaluating one request', 'red')
    gates = [('1', 'Authenticate', 'who is it?', 'blue', 222, 40), ('2', 'Collect policies', 'identity, resource, boundary, SCP', 'violet', 222, 110), ('3', 'Explicit Deny?', 'any "Effect": "Deny"', 'red', 222, 180), ('4', 'Allow found?', 'needed in every layer', 'green', 222, 250)]
    for n, a, b, tn, x, y in gates:
        st += box(x, y, 168, 50, tn, rx=8) + t(x + 96, y + 22, a, 8.6, 'ink', bold=True) + t(x + 96, y + 38, b, 6.6, 'ink2') + f'<circle cx="{x + 16}" cy="{y + 16}" r="9" style="fill:{SA_COL.get(tn, "#7A8496")}"/><text x="{x + 16}" y="{y + 19.5}" text-anchor="middle" font-size="9" font-weight="700" style="fill:#fff">{n}</text>'
    for y in (90, 160, 230):
        st += arrow(306, y, 306, y + 18)
    pol = lambda x, y, title, lines, col: f'<g class="sa-pop">{sa_screen(x, y, 200, 14 + 11 * len(lines) + 6, title, lines)}</g>'
    req = sa_pill(116, 128, 's3:DeleteObject on tiffingo-menu/menu.pdf', 'blue', 210)
    f1 = req + sa_flow('M190 92 C205 80 212 66 222 64', 'blue', 1.0, 3) + sa_tick(400, 46, 9) + t(470, 50, 'signature OK → intern-kabir', 7.4, 'ink', bold=True) + sa_badge(30, 50, 1) + sa_note(110, 200, 170, ['Every request starts', 'with “who is calling?”', '(SigV4 signature)'], 'blue')
    f2 = req + sa_flow('M306 90 L306 110', 'violet', 0.9, 2, 3) + pol(410, 96, 'Interns group → S3ReadMenu', ['"Effect": "Allow",', '"Action": ["s3:GetObject",', '  "s3:ListBucket"]'], 'violet') + pol(410, 172, 'bucket policy (resource)', ['no statement for interns'], 'grey') + sa_badge(30, 50, 2, 'violet') + sa_note(110, 200, 170, ['AWS gathers every policy', 'that applies: user, group,', 'bucket, boundary, SCP'], 'violet')
    f3 = req + pol(410, 96, 'Interns group → S3ReadMenu', ['"Effect": "Allow",', '"Action": ["s3:GetObject",', '  "s3:ListBucket"]'], 'violet') + sa_flow('M306 160 L306 180', 'red', 0.9, 2, 3) + t(470, 210, 'no Deny statement → continue', 7.6, 'ink', bold=True) + sa_badge(30, 50, 3, 'red') + sa_note(110, 200, 170, ['Any explicit Deny', 'anywhere wins instantly', '— none here, keep going'], 'red')
    f4 = req + pol(410, 96, 'Interns group → S3ReadMenu', ['"Effect": "Allow",', '"Action": ["s3:GetObject",', '  "s3:ListBucket"]'], 'violet') + sa_flow('M306 230 L306 250', 'green', 0.9, 2, 3) + sa_cross(400, 262, 10) + t(500, 270, 'DeleteObject not allowed anywhere', 7.4, 'ink', bold=True) + sa_badge(30, 50, 4, 'red') + sa_note(110, 200, 170, ['No Allow for DeleteObject', '= implicit deny', '(the default answer is No)'], 'red')
    f5 = req + '<g class="sa-shake">' + sa_screen(40, 180, 160, 70, 'CloudShell', ['delete failed: s3://tiffingo-', 'menu/menu.pdf An error occurred', '(AccessDenied) … not authorized', 'to perform: s3:DeleteObject'], dark=True) + '</g>' + sa_flow('M222 275 C170 270 150 260 130 250', 'red', 1.0, 2) + sa_cross(196, 186, 9) + sa_badge(30, 50, 5, 'red') + sa_note(450, 230, 170, ['AccessDenied', 'menu.pdf is safe;', 'CloudTrail logs the attempt'], 'red')
    f6 = sa_pill(116, 128, 's3:GetObject on tiffingo-menu/menu.pdf', 'green', 210) + pol(410, 96, 'Interns group → S3ReadMenu', ['"Effect": "Allow",', '"Action": ["s3:GetObject",', '  "s3:ListBucket"]'], 'violet') + sa_tick(400, 262, 10) + t(500, 270, 'Allow found, no Deny → ALLOWED', 7.4, 'ink', bold=True) + sa_flow('M222 275 C170 270 150 200 140 140', 'green', 1.2, 3) + sa_badge(30, 50, 6, 'green') + sa_note(110, 200, 170, ['Reading the same file?', 'Allow exists → download', 'works. Least privilege.'], 'green')
    return scene_anim('How IAM decides: Allow or Deny', 'Kabir the intern tries to delete the menu file, then to read it. Watch IAM evaluate both requests.', 'Policy evaluation',
        'Animation: intern sends DeleteObject; IAM authenticates; collects policies; checks for explicit deny; finds no allow so implicit deny; AccessDenied returned; a GetObject request on the same file is allowed.',
        st, [(f1, 'Step 1 · Authenticate', 'the request is signed; AWS confirms it really comes from the IAM user intern-kabir.'),
             (f2, 'Step 2 · Collect every policy', 'policies attached to the user and his groups, the bucket’s own policy, and any permissions boundary or organisation SCP.'),
             (f3, 'Step 3 · Look for an explicit Deny', 'one Deny anywhere ends the evaluation with “No”, whatever Allows exist. There is none here.'),
             (f4, 'Step 4 · Look for an Allow', 'the Interns policy allows only GetObject and ListBucket. Nothing allows DeleteObject, so the answer is an implicit deny — AWS’s default.'),
             (f5, 'Step 5 · AccessDenied', 'the CLI shows AccessDenied with the action name; the menu file is untouched and CloudTrail records the failed attempt.'),
             (f6, 'Step 6 · The same file, a different action', 'GetObject is allowed by the group policy and nothing denies it, so reading works. Give people exactly what their job needs.')], hid='evalflow')

def shared_vs_own():
    o = t(320, 16, 'Shared login vs one identity per person', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 210, 'Before: everyone uses “admin”', 'red') + sa_building(328, 28, 300, 210, 'After: IAM users in groups', 'green')
    o += sa_people(40, 70, 5, 'red') + t(80, 104, '5 people', 8, 'ink', bold=True)
    o += box(170, 56, 120, 44, 'red', rx=8) + t(230, 76, 'one password', 8.4, 'ink', bold=True) + t(230, 90, 'full admin', 7, 'ink2') + arrow(112, 78, 168, 78)
    o += ''.join(t(26, 130 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✘ a bucket is deleted — who did it? unknown', '✘ someone leaves — change the password for all', '✘ the intern can delete production', '✘ no MFA, password on WhatsApp']))
    o += sa_cross(290, 46, 10)
    for i, (n, g, col) in enumerate([('riya', 'Admins', 'violet'), ('arjun', 'Admins', 'violet'), ('meena', 'Developers', 'blue'), ('kabir', 'Interns', 'green')]):
        y = 58 + i * 34
        o += sa_icon('user', 344, y, 0.9, col) + t(398, y + 13, n, 8, 'ink', bold=True) + arrow(420, y + 9, 470, y + 9) + box(472, y - 2, 110, 24, col, rx=6) + t(527, y + 13, g, 7.6, 'ink', bold=True)
    o += t(478, 210, '✓ each action traced to a person · ✓ MFA each · ✓ remove one user, not everyone', 7, 'ink2')
    o += sa_tick(606, 46, 10)
    return bigfig('Before: five people share one admin password, so actions cannot be traced and an intern can delete production. After: each person has an IAM user in a group that gives only the permissions their job needs.', o, h=250)

def badge_picture():
    o = t(320, 16, 'User vs role: an employee ID card vs a visitor badge', 11, 'ink', bold=True)
    o += box(12, 30, 300, 180, 'blue', rx=12) + sa_icon('user', 36, 50, 1.8, 'blue') + t(182, 62, 'IAM user = employee ID card', 9, 'ink', bold=True)
    o += ''.join(t(30, 96 + i * 16, s, 7.8, 'ink2', anchor='start') for i, s in enumerate(['belongs to one person', 'long-term: password, maybe access keys', 'permissions from its groups', 'use for: people (if no SSO)']))
    o += box(328, 30, 300, 180, 'amber', rx=12) + sa_icon('role', 352, 50, 1.8, 'saffron') + t(498, 62, 'IAM role = visitor badge', 9, 'ink', bold=True)
    o += ''.join(t(346, 96 + i * 16, s, 7.8, 'ink2', anchor='start') for i, s in enumerate(['anyone trusted can pick it up (assume it)', 'temporary: expires in 1–12 hours', 'trust policy says WHO may assume it', 'use for: EC2/Lambda, other accounts, SSO']))
    o += t(320, 228, 'Rule of thumb: people → Identity Center or users in groups; software → roles. Never keys in code.', 7.6, 'ink', bold=True)
    return bigfig('Comparison: an IAM user is like an employee ID card belonging to one person with long-term credentials; an IAM role is like a visitor badge anyone trusted can borrow, with temporary credentials that expire.', o, h=240)
