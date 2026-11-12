from cloudkit import *

def detect_scene():
    st = sa_building(10, 14, 616, 300, 'AWS account — security services working together', 'grey')
    st += box(24, 40, 120, 60, 'red', rx=8) + sa_icon('globe', 32, 48, 1.0, 'red') + t(90, 62, 'Attacker', 8.4, 'ink', bold=True) + t(90, 78, 'unknown IP', 6.8, 'ink2') + t(90, 90, 'stolen key', 6.8, 'ink2')
    st += box(170, 40, 120, 60, 'blue', rx=8) + sa_icon('server', 178, 48, 1.0, 'blue') + t(236, 62, 'EC2 / S3 / IAM', 8, 'ink', bold=True) + t(236, 78, 'your resources', 6.8, 'ink2')
    st += box(170, 140, 120, 56, 'card', rx=8) + sa_icon('clock', 178, 148, 1.0, 'grey') + t(236, 164, 'CloudTrail', 8.4, 'ink', bold=True) + t(236, 180, 'every API call', 6.8, 'ink2')
    st += box(320, 140, 120, 56, 'amber', rx=8) + sa_icon('shield', 328, 148, 1.0, 'saffron') + t(386, 164, 'GuardDuty', 8.4, 'ink', bold=True) + t(386, 180, 'threat detection', 6.8, 'ink2')
    st += box(470, 140, 140, 56, 'violet', rx=8) + sa_icon('chart', 478, 148, 1.0, 'violet') + t(546, 164, 'Security Hub', 8.4, 'ink', bold=True) + t(546, 180, 'all findings, prioritised', 6.6, 'ink2')
    st += box(320, 236, 120, 56, 'blue', rx=8) + sa_icon('gear', 328, 244, 1.0, 'blue') + t(386, 260, 'EventBridge', 8.4, 'ink', bold=True) + t(386, 276, 'rule: severity ≥ 7', 6.8, 'ink2')
    st += box(470, 236, 140, 56, 'green', rx=8) + sa_icon('mail', 478, 244, 1.0, 'green') + t(546, 260, 'SNS + Lambda', 8.4, 'ink', bold=True) + t(546, 276, 'alert + auto-response', 6.6, 'ink2')
    st += box(24, 236, 270, 56, 'card', rx=8) + t(159, 256, 'Config + Inspector + Macie + Access Analyzer', 7.6, 'ink', bold=True) + t(159, 272, 'misconfigurations · vulnerabilities · sensitive data · exposure', 6.6, 'ink2')
    f1 = sa_flow('M144 70 L170 70', 'red', 0.9, 3, 4, 'RunInstances ×20', 157, 118) + sa_badge(300, 30, 1, 'red') + sa_note(470, 40, 140, ['Sunday 11:40 pm', 'leaked key used', 'from abroad'], 'red')
    f2 = sa_flow('M230 100 L230 140', 'grey', 0.9, 3) + sa_pill(236, 124, 'logged', 'grey') + sa_badge(300, 30, 2, 'grey') + sa_note(470, 40, 140, ['CloudTrail records', 'every call: who, what,', 'from which IP'], 'grey')
    f3 = sa_flow('M290 168 L320 168', 'amber', 0.9, 3) + '<g class="sa-pop">' + sa_screen(320, 70, 150, 60, 'GuardDuty finding', ['Impact:IAMUser/', 'AnomalousBehavior', 'severity: HIGH'], dark=True) + '</g>' + sa_badge(300, 30, 3, 'amber') + sa_note(546, 70, 150, ['ML + threat intel:', 'unusual IP, unusual', 'API pattern'], 'saffron')
    f4 = sa_flow('M440 168 L470 168', 'violet', 0.9, 3) + sa_flow('M386 196 L386 236', 'blue', 0.9, 3) + sa_badge(300, 30, 4, 'blue') + sa_note(546, 70, 150, ['Finding → Security Hub', 'and an EventBridge rule', '(severity ≥ 7) fires'], 'blue')
    f5 = sa_flow('M440 264 L470 264', 'green', 0.9, 3) + '<g class="sa-pop">' + sa_screen(470, 60, 150, 70, 'auto-response (Lambda)', ['deactivate access key ✓', 'stop launched instances ✓', 'e-mail + SMS on-call ✓'], dark=True) + '</g>' + sa_badge(300, 30, 5, 'green') + sa_note(84, 110, 140, ['Within minutes: key', 'disabled, damage stopped,', 'humans alerted'], 'green')
    f6 = sa_tick(600, 30, 12) + '<g class="sa-pop">' + sa_screen(24, 110, 270, 110, 'Incident review (Monday)', ['1 contain: key off, instances stopped', '2 investigate: CloudTrail by access key', '3 eradicate: delete key, rotate secrets', '4 recover: clean resources, verify bill', '5 learn: no long-term keys; SCP; training'], dark=True) + '</g>' + sa_badge(300, 30, 6, 'green') + sa_note(460, 40, 150, ['Detect → respond →', 'learn. Total cost:', '₹300, not ₹1 lakh'], 'green')
    return scene_anim('Detect and respond: how AWS security services work together', 'A leaked key is used on Sunday night. Watch the account detect it, alert and fix it — before Monday.', 'Detection chain',
        'Animation: attacker uses a leaked key to launch instances; CloudTrail records the calls; GuardDuty raises a high-severity finding; it flows to Security Hub and an EventBridge rule; Lambda deactivates the key and stops instances while SNS alerts on-call; Monday incident review follows five steps.',
        st, [(f1, 'Step 1 · The attack', 'a leaked access key is used from an unfamiliar country to launch 20 instances at 11:40 pm.'),
             (f2, 'Step 2 · Everything is recorded', 'CloudTrail logs each RunInstances call with the access key ID, source IP and time — the raw evidence.'),
             (f3, 'Step 3 · GuardDuty notices', 'machine learning and threat intelligence flag anomalous API use from an unusual location — a HIGH-severity finding within minutes.'),
             (f4, 'Step 4 · Findings are routed', 'the finding appears in Security Hub with others, and an EventBridge rule matching severity ≥ 7 triggers automation.'),
             (f5, 'Step 5 · Automatic response', 'a Lambda function deactivates the key and stops the new instances; SNS e-mails/SMSes the on-call engineer.'),
             (f6, 'Step 6 · Learn', 'the incident review follows contain → investigate → eradicate → recover → learn, and adds guard-rails so it cannot repeat.')], hid='detectflow')

def layers_picture():
    o = t(320, 16, 'Defence in depth: six layers around your data', 11, 'ink', bold=True)
    L = [('Identity', 'MFA, SSO, least privilege, no long-term keys', '#D64545'), ('Detection', 'CloudTrail, GuardDuty, Security Hub', '#E0A100'), ('Network', 'private subnets, security groups, WAF, Shield', '#7C4DDB'), ('Compute', 'patching, Inspector, IMDSv2, no SSH from 0.0.0.0/0', '#2E5AAC'), ('Application', 'secrets in Secrets Manager, input validation', '#2F7D5B'), ('Data', 'encryption (KMS), Block Public Access, Macie, backups', '#E8772E')]
    cx, cy = 200, 140
    for i, (n, d, c) in enumerate(L):
        r = 120 - i * 18
        o += f'<circle cx="{cx}" cy="{cy}" r="{r}" style="fill:{c};opacity:.12;stroke:{c};stroke-width:1.5"/>'
        o += f'<text x="{cx}" y="{cy - r + 12}" text-anchor="middle" font-size="7.4" font-weight="700" style="fill:{c}">{n}</text>'
    o += sa_icon('file', cx - 12, cy - 8, 1.0, 'saffron') + t(cx, cy + 26, 'your data', 7.6, 'ink', bold=True)
    for i, (n, d, c) in enumerate(L):
        y = 40 + i * 32
        o += f'<rect x="350" y="{y}" width="276" height="26" rx="6" style="fill:{c};opacity:.12"/><text x="358" y="{y + 11}" font-size="7.8" font-weight="700" style="fill:{c}">{n}</text><text x="358" y="{y + 21}" font-size="6.8" class="s-ink2">{d}</text>'
    o += t(488, 248, 'An attacker must beat every layer; you only need one to stop them.', 7.4, 'ink', bold=True)
    return bigfig('Defence in depth: concentric layers around data — identity, detection, network, compute, application and data — each listing the AWS controls used.', o, h=262)

def baseline_picture():
    o = t(320, 16, 'Security baseline for every new account (first day)', 11, 'ink', bold=True)
    items = [('Root MFA, no root keys', 'Lesson 1.2'), ('People via SSO / users with MFA', '2.1'), ('Roles for apps, IMDSv2', '2.2'), ('Budgets + Cost Anomaly Detection', '1.2'), ('CloudTrail trail, all Regions, to S3', 'this lesson'), ('GuardDuty on', 'this lesson'), ('Security Hub / CSPM standards on', 'this lesson'), ('S3 Block Public Access (account)', '4.2'), ('EBS + S3 default encryption', '2.4'), ('Access Analyzer (external + unused)', '2.3')]
    for i, (a, b) in enumerate(items):
        x = 14 + (i % 2) * 312; y = 34 + (i // 2) * 40
        o += box(x, y, 300, 32, 'card', rx=6) + sa_tick(x + 16, y + 16, 8) + t(x + 32, y + 20, a, 8, 'ink', anchor='start', bold=True) + t(x + 292, y + 20, b, 6.8, 'ink2', anchor='end')
    o += t(320, 244, 'Ten settings, about an hour, mostly free or very cheap — and most real-world breaches would have been stopped.', 7.4, 'ink2')
    return bigfig('Checklist of ten baseline settings for a new AWS account with the lesson where each is taught.', o, h=254)
