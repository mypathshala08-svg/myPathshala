from cloudkit import *

def launch_scene():
    st = sa_people(20, 132, 1) + t(28, 168, 'Riya', 8, 'ink', bold=True)
    st += sa_screen(48, 96, 120, 74, 'Console — EC2', ['Name: tiffingo-web', 'Type: t3.micro', 'Region: Mumbai', ''])
    st += sa_building(196, 14, 438, 300, 'AWS Cloud', 'grey')
    st += box(214, 104, 82, 40, 'amber', rx=8) + sa_icon('app', 222, 112, 1.0, 'saffron') + t(266, 122, 'API', 8, 'ink', bold=True) + t(266, 134, 'endpoint', 6.6, 'ink2')
    st += box(214, 196, 82, 40, 'red', rx=8) + sa_icon('shield', 222, 204, 1.0, 'red') + t(266, 214, 'IAM', 8, 'ink', bold=True) + t(266, 226, 'allowed?', 6.6, 'ink2')
    st += box(318, 150, 90, 40, 'violet', rx=8) + sa_icon('gear', 326, 158, 1.0, 'violet') + t(370, 168, 'EC2 control', 7.6, 'ink', bold=True) + t(370, 180, 'plane', 6.6, 'ink2')
    st += sa_building(428, 34, 196, 150, 'Region ap-south-1 · AZ a', 'blue')
    st += sa_server(446, 66, label='host') + sa_server(494, 66, label='host') + sa_server(542, 66, label='host')
    st += box(428, 200, 92, 100, 'card', rx=8) + t(474, 216, 'CloudTrail', 8, 'ink', bold=True)
    st += box(532, 200, 92, 100, 'card', rx=8) + t(578, 216, 'Billing', 8, 'ink', bold=True)
    btn = '<g class="sa-glow"><rect x="96" y="150" width="62" height="14" rx="4" style="fill:#E0A100"/><text x="127" y="160" text-anchor="middle" font-size="7.4" font-weight="700" style="fill:#111">Launch ▶</text></g>'
    f1 = btn + sa_badge(40, 80, 1) + sa_note(110, 196, 150, ['Riya clicks Launch', 'the console is just a', 'client of the EC2 API'], 'saffron')
    f2 = btn + sa_flow('M168 130 C190 126 200 124 214 124', 'blue', 1.2, 3, 4, 'RunInstances', 190, 112) + sa_icon('lock', 176, 138, 0.8, 'green') + sa_badge(40, 80, 2) + sa_note(110, 196, 150, ['Signed HTTPS request', 'SigV4 signature proves', 'it is really Riya'], 'blue')
    f3 = sa_flow('M255 144 L255 196', 'blue', 1.0, 2) + sa_tick(306, 216, 10) + t(330, 246, 'ec2:RunInstances → Allow', 7.2, 'ink', bold=True) + sa_badge(40, 80, 3) + sa_note(110, 196, 150, ['IAM checks policies', 'no Allow → AccessDenied,', 'nothing is created'], 'red')
    f4 = sa_flow('M296 216 C310 200 318 186 330 186', 'blue', 1.0, 2) + sa_flow('M408 160 C430 150 470 120 494 112', 'violet', 1.2, 3) + f'<g class="sa-pop">{sa_server(494, 66, col="amber", label="pending")}</g>' + sa_badge(40, 80, 4) + sa_note(110, 196, 150, ['Control plane picks a host', 'with free capacity in AZ a,', 'returns an instance ID'], 'violet')
    f5 = sa_server(494, 66, col='green', label="running") + sa_flow('M408 176 C420 210 430 240 440 250', 'grey', 1.4, 2) + ''.join(f'<text x="436" y="{232 + i * 12}" font-size="6.4" font-family="var(--font-code)" class="s-ink">{ln}</text>' for i, ln in enumerate(['13:10 RunInstances', 'user: riya-admin', 'from: 49.36.x.x', 'result: success'])) + sa_badge(40, 80, 5, 'green') + sa_note(110, 196, 150, ['Instance boots in AZ a', 'CloudTrail records who,', 'what, when, from where'], 'green')
    f6 = sa_server(494, 66, col='green', label="running") + sa_gauge(546, 232, 35, 'meter') + t(594, 248, 'USD 0.0112', 7.4, 'ink', bold=True) + t(594, 260, 'per hour', 6.8, 'ink2') + t(594, 280, 'stop → stops', 6.6, 'ink2') + sa_flow('M540 120 C560 160 570 190 570 220', 'amber', 1.6, 2) + sa_badge(40, 80, 6, 'amber') + sa_note(110, 196, 150, ['Billing meter starts', 'per second while running', '(+ disk while it exists)'], 'amber')
    return scene_anim('What happens when you click “Launch” — inside AWS', 'Follow one click from Riya’s browser to a running server and a line on the bill.', 'Inside AWS',
        'Animation: Riya clicks Launch; a signed RunInstances request goes to the EC2 API endpoint; IAM allows it; the control plane picks a host in AZ a; the instance boots and CloudTrail logs the call; billing starts metering.',
        st, [(f1, 'Step 1 · The click', 'the console turns Riya’s form into an API request — the same call the CLI or SDK would make.'),
             (f2, 'Step 2 · A signed request', 'an HTTPS request “RunInstances” goes to ec2.ap-south-1.amazonaws.com, signed with SigV4 so AWS can verify who sent it.'),
             (f3, 'Step 3 · IAM decides', 'AWS checks Riya’s policies for ec2:RunInstances. With no Allow (or any explicit Deny) the answer is AccessDenied and nothing happens.'),
             (f4, 'Step 4 · The control plane acts', 'EC2 finds a physical host with free capacity in an Availability Zone, attaches a disk and network card, and replies with an instance ID.'),
             (f5, 'Step 5 · Running — and recorded', 'the instance boots; CloudTrail writes who called RunInstances, when, from which IP and whether it succeeded.'),
             (f6, 'Step 6 · The meter runs', 'billing counts every second the instance runs (plus its disk). Stop it and compute charges stop; terminate it and the disk is deleted by default.')], hid='launchflow')

def capacity_picture():
    """Demand over a week vs fixed servers vs elastic AWS capacity."""
    o = t(320, 16, 'Diwali week: demand vs capacity', 11, 'ink', bold=True)
    X0, Y0, W, H = 60, 40, 540, 170
    o += f'<line x1="{X0}" y1="{Y0 + H}" x2="{X0 + W}" y2="{Y0 + H}" style="stroke:var(--line);stroke-width:1.5"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0 + H}" style="stroke:var(--line);stroke-width:1.5"/>'
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Diwali', 'Sat', 'Sun']
    dem = [30, 34, 32, 40, 150, 60, 36]
    pts = []
    for i, d in enumerate(days):
        x = X0 + 40 + i * 76; o += t(x, Y0 + H + 14, d, 7.4, 'ink2')
        pts.append((x, Y0 + H - dem[i]))
    path = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
    o += f'<path d="{path}" style="fill:none;stroke:#2E5AAC;stroke-width:3"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="3.5" style="fill:#2E5AAC"/>' for x, y in pts)
    fy = Y0 + H - 70
    o += f'<line x1="{X0}" y1="{fy}" x2="{X0 + W}" y2="{fy}" style="stroke:#D64545;stroke-width:2.5;stroke-dasharray:7 4"/>' + t(X0 + W - 4, fy - 6, 'own servers: fixed capacity', 7.6, 'ink', anchor='end', bold=True)
    el = 'M' + ' L'.join(f'{x - 20} {y - 12} L{x + 20} {y - 12}' for x, y in pts)
    o += f'<path d="{el}" style="fill:none;stroke:#2F7D5B;stroke-width:2.5"/>' + t(X0 + 6, Y0 + 8, 'AWS: capacity follows demand', 7.6, 'ink', anchor='start', bold=True)
    o += f'<rect x="{X0 + 2}" y="{fy}" width="{W - 4}" height="{Y0 + H - fy}" style="fill:#D64545;opacity:.06"/>'
    o += sa_note(pts[4][0], Y0 + H - 150 - 4, 0, [''], 'red') if False else ''
    o += f'<rect x="{pts[4][0] - 18}" y="{pts[4][1]}" width="36" height="{fy - pts[4][1]}" style="fill:#D64545;opacity:.25"/>' + t(pts[4][0] + 92, pts[4][1] + 22, 'demand above fixed capacity', 7.2, 'ink', bold=True) + t(pts[4][0] + 92, pts[4][1] + 34, '= late orders, app frozen', 7, 'ink2')
    o += t(pts[1][0] + 40, fy + 16, 'paid for, but idle most of the week', 7.4, 'ink', bold=True)
    return bigfig('Line chart of TiffinGo orders over Diwali week: demand is low most days and spikes on Diwali. A fixed line shows own servers — idle most days and overwhelmed on Diwali. A green step line shows AWS capacity following demand.', o, h=232)
