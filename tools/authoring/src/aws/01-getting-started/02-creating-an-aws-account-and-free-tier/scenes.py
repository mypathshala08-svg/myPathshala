from cloudkit import *

def leak_scene():
    st = sa_people(16, 128, 1) + t(24, 164, 'Kabir', 8, 'ink', bold=True)
    st += sa_screen(40, 90, 120, 60, 'config.py', ['AWS_KEY = "AKIA…"', 'AWS_SECRET = "…"', '# TODO remove'], dark=True)
    st += box(186, 30, 110, 54, 'card', rx=8) + sa_icon('git', 194, 38, 1.0, 'grey') + t(250, 54, 'Public repo', 8, 'ink', bold=True) + t(250, 70, 'github.com/…', 6.6, 'ink2')
    st += sa_building(330, 14, 296, 300, 'AWS account (root keys = no limits)', 'red')
    for i, (x, y) in enumerate([(350, 60), (400, 60), (450, 60), (500, 60), (550, 60), (350, 140), (400, 140), (450, 140), (500, 140), (550, 140)]):
        pass
    st += box(186, 226, 120, 70, 'card', rx=8) + t(246, 240, 'Monday’s bill', 8, 'ink', bold=True)
    st += t(478, 170, 'EC2 · S3 · IAM · every Region', 9, 'ink2')
    gpus = lambda n: ''.join(f'<g class="sa-pop" style="animation-delay:{i * .15:.2f}s">{sa_server(350 + (i % 5) * 52, 60 + (i // 5) * 80, col="red", label="GPU")}</g>' for i in range(n))
    f1 = sa_badge(30, 76, 1) + sa_flow('M100 150 C110 170 120 175 130 175', 'red', 1.2, 2) + sa_note(98, 200, 160, ['Root access key created', 'and pasted into code', '“just to save time”'], 'red')
    f2 = sa_flow('M160 110 C175 90 180 70 186 60', 'red', 1.0, 3, 4, 'git push', 168, 92) + sa_badge(30, 76, 2) + sa_note(98, 200, 160, ['Pushed to a public repo', 'deleting the file later does', 'not remove it from history'], 'red')
    bot = '<g class="sa-shake">' + sa_icon('gear', 226, 98, 1.6, 'violet') + '</g>' + t(258, 136, 'scanner bot', 7.4, 'ink', bold=True)
    f3 = bot + sa_flow('M241 84 L241 98', 'violet', 0.6, 2, 3) + sa_pill(241, 154, 'AKIA… found in 4 min', 'violet') + sa_badge(30, 76, 3, 'violet') + sa_note(98, 200, 160, ['Bots watch public commits', 'for the AKIA pattern —', 'minutes, not days'], 'violet')
    f4 = bot + sa_flow('M270 112 C300 112 320 100 346 90', 'red', 0.9, 4, 4, 'RunInstances ×100', 306, 120) + gpus(4) + sa_badge(30, 76, 4, 'red') + sa_note(98, 200, 160, ['Attacker calls AWS APIs', 'root: every call allowed', 'GPU servers start'], 'red')
    f5 = gpus(10) + sa_gauge(196, 244, 96, 'USD') + t(256, 270, '$1,200', 12, 'ink', bold=True) + t(256, 284, 'in one weekend', 7, 'ink2') + sa_badge(30, 76, 5, 'red') + sa_note(98, 200, 160, ['Crypto-mining all weekend', 'no budget alert,', 'nobody notices'], 'red')
    shield = (box(346, 40, 270, 250, 'green', rx=12) + t(481, 64, 'What would have stopped it', 10, 'ink', bold=True)
              + ''.join(sa_tick(368, 92 + i * 38, 9) + t(384, 96 + i * 38, s, 8, 'ink', anchor='start') for i, s in enumerate(['No root access keys — nothing to leak', 'MFA on root and every user', 'Admin user / SSO for daily work', 'Budget + anomaly alert on day one', 'Secret scanning before git push'])))
    f6 = shield + sa_badge(30, 76, 6, 'green') + sa_note(98, 200, 160, ['Prevention costs nothing', 'and takes ten minutes', '— Lesson 1.2 lab'], 'green')
    return scene_anim('How one leaked key becomes a $1,200 bill', 'Kabir’s weekend, as it happened — and the five settings that would have stopped it.', 'Leaked key',
        'Animation: a root access key is pasted into code; pushed to a public repository; a scanner bot finds it in minutes; the attacker launches GPU servers; the bill reaches 1,200 dollars; five prevention settings shown.',
        st, [(f1, 'Step 1 · A root key in code', 'Kabir creates an access key for the root user and pastes it into config.py.'),
             (f2, 'Step 2 · Pushed to public GitHub', 'the key is now public. Deleting the line later does not remove it from Git history or from copies already made.'),
             (f3, 'Step 3 · Found in minutes', 'automated scanners watch every public commit for the AKIA… pattern. AWS also scans and may quarantine the key — but attackers can be faster.'),
             (f4, 'Step 4 · The attacker calls AWS', 'root credentials cannot be limited by any policy, so every RunInstances call succeeds — the largest GPU servers, in many Regions.'),
             (f5, 'Step 5 · The weekend bill', 'the servers mine cryptocurrency all weekend. Without a budget alert nobody notices until Monday.'),
             (f6, 'Step 6 · What prevents it', 'no root keys, MFA everywhere, an admin user or SSO for daily work, budget and anomaly alerts, and secret scanning before every push.')], hid='leakflow')

def root_vs_admin_picture():
    o = t(320, 16, 'Two identities, two very different risks', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 200, 'Root user (sign-up e-mail)', 'red') + sa_building(328, 28, 300, 200, 'Admin user (IAM / Identity Center)', 'green')
    o += sa_icon('lock', 40, 52, 1.6, 'red') + t(160, 64, 'Can do everything — incl. close the account', 7.8, 'ink', bold=True)
    o += ''.join(t(30, 92 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✘ cannot be limited by any IAM policy', '✘ access keys = total compromise if leaked', '✓ needed for a few tasks (close account, support plan…)', '→ MFA on, no keys, password in a safe, rarely used'])) 
    o += sa_cross(290, 46, 10) + t(162, 214, 'Lock it away', 9, 'ink', bold=True)
    o += sa_icon('user', 356, 52, 1.6, 'green') + t(476, 64, 'Daily work, with guard-rails', 7.8, 'ink', bold=True)
    o += ''.join(t(346, 92 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✓ permissions from a group/permission set', '✓ MFA; can be disabled or audited any time', '✓ CloudTrail shows exactly who did what', '→ one per person; never shared'])) 
    o += sa_tick(606, 46, 10) + t(478, 214, 'Use this every day', 9, 'ink', bold=True)
    return bigfig('Comparison: the root user can do everything, cannot be limited and is dangerous if its keys leak — lock it away. The admin user has permissions from a group, MFA, is auditable and is used every day.', o, h=240)
