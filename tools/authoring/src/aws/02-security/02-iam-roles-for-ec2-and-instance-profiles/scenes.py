from cloudkit import *

def imds_scene():
    st = sa_building(10, 14, 300, 300, 'EC2 instance (Amazon Linux)', 'blue')
    st += sa_screen(24, 36, 272, 64, 'app.py (boto3)', ["s3 = boto3.client('s3')", "s3.download_file(B, 'notes/l1.pdf', …)", '# no keys anywhere in code or files'], dark=True)
    st += box(24, 120, 130, 60, 'amber', rx=8) + sa_icon('key', 32, 128, 1.0, 'saffron') + t(102, 140, 'SDK credential', 7.6, 'ink', bold=True) + t(102, 154, 'chain → #6', 7, 'ink2') + t(102, 168, 'instance role', 7, 'ink2')
    st += box(170, 120, 126, 60, 'violet', rx=8) + t(233, 140, 'IMDS', 8.4, 'ink', bold=True) + t(233, 154, '169.254.169.254', 7, 'ink2') + t(233, 168, 'inside the host', 6.8, 'ink2')
    st += box(24, 200, 272, 50, 'card', rx=8) + t(160, 220, 'Instance profile → role LabAppRole', 8, 'ink', bold=True) + t(160, 236, 'trust: ec2.amazonaws.com', 7, 'ink2')
    st += sa_building(330, 14, 296, 140, 'AWS STS + IAM', 'violet')
    st += box(346, 40, 120, 50, 'violet', rx=8) + t(406, 62, 'STS', 9, 'ink', bold=True) + t(406, 78, 'temporary creds', 7, 'ink2')
    st += box(486, 40, 126, 50, 'red', rx=8) + t(549, 62, 'IAM policy', 8.6, 'ink', bold=True) + t(549, 78, 'notes/ read · logs/ write', 6.6, 'ink2')
    st += sa_building(330, 170, 296, 144, 'S3 bucket edu-content', 'green')
    st += svc(380, 196, 'folder', 'notes/', 'read', 'green', w=66) + svc(470, 196, 'folder', 'logs/', 'write', 'blue', w=66) + svc(565, 196, 'folder', 'submissions/', 'no access', 'red', w=80)
    f1 = sa_flow('M160 250 L160 260', 'violet', 1, 1, 0.1) + sa_pill(160, 276, 'launched with --iam-instance-profile LabAppRole', 'violet', 250) + sa_flow('M296 225 C320 160 360 100 380 90', 'violet', 1.4, 3) + sa_badge(296, 302, 1) + sa_note(478, 106, 260, ['EC2 assumes the role for the instance; STS issues keys'], 'violet')
    f2 = sa_flow('M154 150 L170 150', 'amber', 0.8, 2, 3) + sa_pill(160, 108, 'PUT /latest/api/token (IMDSv2)', 'saffron', 190) + sa_badge(296, 302, 2, 'amber') + sa_note(160, 262, 270, ['SDK first gets a session token (IMDSv2, 6 h max)'], 'saffron')
    f3 = sa_flow('M233 120 L233 102', 'violet', 0.8, 2, 3) + '<g class="sa-pop">' + sa_screen(170, 100, 140, 70, 'GET …/security-credentials/', ['"AccessKeyId": "ASIA…",', '"SessionToken": "…",', '"Expiration": "…T15:42Z"'], dark=True) + '</g>' + sa_badge(296, 302, 3, 'violet') + sa_note(160, 262, 270, ['IMDS hands back temporary keys for LabAppRole'], 'violet')
    f4 = sa_flow('M296 70 C330 120 360 196 380 210', 'green', 1.1, 3) + sa_tick(380, 182, 9) + sa_flow('M296 80 C340 140 440 190 470 210', 'blue', 1.3, 3) + sa_tick(470, 182, 9) + sa_badge(296, 302, 4, 'green') + sa_note(478, 106, 260, ['Read notes/ ✓ · write logs/ ✓ (signed with the role’s keys)'], 'green')
    f5 = sa_flow('M296 90 C380 160 520 180 565 210', 'red', 1.3, 3) + sa_cross(565, 182, 10) + sa_pill(565, 268, 'AccessDenied', 'red') + sa_badge(296, 302, 5, 'red') + sa_note(478, 106, 260, ['submissions/ → AccessDenied: policy never allows it'], 'red')
    f6 = sa_flow('M406 90 C350 140 260 150 233 150', 'violet', 1.6, 3) + sa_pill(233, 108, 'new keys before expiry', 'violet', 140) + sa_cross(120, 290, 9) + t(200, 294, 'stolen copy expires in hours', 7.4, 'ink', bold=True) + sa_badge(296, 302, 6, 'green') + sa_note(478, 106, 260, ['Keys rotate automatically; nothing to leak long-term'], 'green')
    return scene_anim('How an EC2 server gets AWS permissions without any keys', 'The app on the server asks the instance metadata service for temporary credentials of its role — watch the full path.', 'Instance role',
        'Animation: instance launched with an instance profile; SDK gets an IMDSv2 token; IMDS returns temporary role credentials; reads notes and writes logs succeed; submissions access denied; credentials rotate automatically before expiry.',
        st, [(f1, 'Step 1 · Launch with an instance profile', 'the instance profile is the container that attaches role LabAppRole to the instance; its trust policy lets ec2.amazonaws.com assume it.'),
             (f2, 'Step 2 · The SDK asks IMDSv2 for a token', 'boto3 finds no keys in env vars or files, so it reaches chain step 6: a PUT to 169.254.169.254 returns a short-lived session token.'),
             (f3, 'Step 3 · IMDS returns temporary keys', 'with the token, a GET on /latest/meta-data/iam/security-credentials/LabAppRole returns ASIA… keys, a session token and an expiry time.'),
             (f4, 'Step 4 · Allowed calls succeed', 'requests are signed with the role’s keys; IAM allows GetObject on notes/* and PutObject on logs/*.'),
             (f5, 'Step 5 · Forbidden calls fail', 'submissions/ is not in the role’s policy (and can be explicitly denied), so S3 answers AccessDenied — proof the server cannot read it.'),
             (f6, 'Step 6 · Keys rotate themselves', 'AWS refreshes the credentials before they expire; the SDK picks up new ones automatically. A copied key dies within hours.')], hid='imdsflow')

def keys_vs_role():
    o = t(320, 16, 'Keys on the server vs a role on the server', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 200, 'Access keys in a config file', 'red') + sa_building(328, 28, 300, 200, 'Instance role (no keys)', 'green')
    o += sa_screen(26, 48, 180, 50, '/etc/app/config', ['AWS_KEY=AKIA…', 'AWS_SECRET=…'], dark=True) + sa_cross(290, 46, 10)
    o += ''.join(t(26, 118 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✘ copied into AMIs, backups, Git, logs', '✘ never expire until someone deletes them', '✘ if the server is hacked, keys work from anywhere', '✘ rotating means editing every server']))
    o += sa_server(350, 50, col='green') + arrow(386, 70, 420, 70) + box(422, 52, 110, 36, 'amber', rx=6) + t(477, 74, 'LabAppRole', 8, 'ink', bold=True) + sa_tick(606, 46, 10)
    o += ''.join(t(342, 118 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✓ nothing stored on disk or in the image', '✓ temporary keys, refreshed automatically', '✓ permissions changed once, on the role', '✓ lab exams: “no passwords or keys on the server”']))
    return bigfig('Comparison: access keys in a server config file get copied, never expire and work from anywhere if stolen; an instance role stores nothing, uses temporary keys that rotate automatically and is managed centrally.', o, h=240)

def proof_picture():
    o = t(320, 16, 'What examiners mean by “prove what the server can and cannot do”', 11, 'ink', bold=True)
    rows = [('aws s3 cp s3://B/notes/l1.pdf .', 'download: s3://B/notes/l1.pdf', True), ('aws s3 cp report.txt s3://B/logs/', 'upload: ./report.txt to s3://B/logs/report.txt', True), ('aws s3 ls s3://B/submissions/', 'An error occurred (AccessDenied) when calling the ListObjectsV2 operation', False), ('aws s3 rm s3://B/notes/l1.pdf', 'delete failed … (AccessDenied) … not authorized to perform: s3:DeleteObject', False)]
    o += sa_screen(20, 32, 600, 150, 'on the server (role credentials)', [])
    for i, (c, r, ok) in enumerate(rows):
        y = 58 + i * 30
        o += f'<text x="30" y="{y}" font-size="7.6" font-family="var(--font-code)" class="s-ink">$ {c}</text><text x="30" y="{y + 12}" font-size="7" font-family="var(--font-code)" style="fill:{"#2F7D5B" if ok else "#D64545"}">{r}</text>'
        o += sa_tick(604, y + 2, 8) if ok else sa_cross(604, y + 2, 8)
    o += t(320, 202, 'Two ✓ (what it must do) + two ✘ (what it must never do) = proof. Save this output as evidence.', 7.8, 'ink', bold=True)
    return bigfig('Evidence screen: from the server, downloading a note and uploading a log succeed; listing submissions and deleting a note fail with AccessDenied.', o, h=214)
