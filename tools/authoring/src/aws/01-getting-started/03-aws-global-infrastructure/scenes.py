from cloudkit import *

def az_failure():
    st = sa_building(108, 14, 526, 306, 'Region ap-south-1 (Mumbai)', 'blue')
    st += sa_people(22, 150, 3) + t(36, 186, 'Customers', 8, 'ink', bold=True) + t(36, 197, 'lunch orders', 6.8, 'ink2')
    st += box(300, 30, 170, 30, 'amber', rx=8) + t(385, 49, 'Application Load Balancer', 8.2, 'ink', bold=True)
    for x, lab in [(124, 'AZ a · aps1-az1'), (296, 'AZ b · aps1-az2'), (468, 'AZ c · aps1-az3')]:
        st += sa_building(x, 82, 160, 228, lab, 'green')
    st += sa_server(140, 104, label='web-1') + sa_server(190, 104, label='web-2') + sa_server(312, 104, label='web-3') + sa_server(362, 104, label='web-4')
    st += sa_db(176, 222, 'RDS standby') + sa_db(348, 222, 'RDS primary', crown=False)
    users = 'M70 158 C150 150 220 46 300 46'
    to_a1, to_a2, to_b1, to_b2 = 'M330 60 C300 80 170 80 157 104', 'M340 60 C320 84 220 84 207 104', 'M380 60 C370 80 330 86 329 104', 'M400 60 C400 80 380 86 379 104'
    sync = 'M330 236 L194 236'
    dark_b = sa_dark(296, 82, 160, 228) + sa_bolt(362, 150, 1.4) + sa_cross(430, 108, 11)
    f1 = (sa_flow(users, 'blue', 2.4, 4) + sa_flow(to_a1, 'blue', 1.6, 2) + sa_flow(to_a2, 'blue', 1.6, 2) + sa_flow(to_b1, 'blue', 1.6, 2) + sa_flow(to_b2, 'blue', 1.6, 2) +
          sa_flow(sync, 'green', 1.4, 3, 3, 'sync copy', 262, 252) + sa_badge(120, 70, 1) + sa_note(552, 150, 150, ['Normal lunch hour', 'traffic split over 2 AZs', 'DB copied synchronously'], 'blue'))
    f2 = (sa_flow(users, 'blue', 2.4, 4) + sa_flow(to_a1, 'blue', 1.6, 2) + sa_flow(to_b1, 'red', 1.6, 2) + dark_b +
          sa_badge(120, 70, 2, 'red') + sa_note(552, 150, 150, ['1:10 pm — power lost', 'AZ b servers and', 'DB primary go dark'], 'red'))
    f3 = (sa_flow(users, 'blue', 2.4, 4) + sa_flow(to_a1, 'blue', 1.6, 2) + sa_flow('M392 60 C392 74 390 90 380 104', 'amber', 1.0, 2, 3) + dark_b +
          sa_cross(318, 78, 7) + sa_cross(338, 78, 7) + sa_cross(358, 78, 7) + t(338, 72, 'health check ×3', 7, 'ink', bold=True) +
          sa_badge(120, 70, 3, 'amber') + sa_note(552, 150, 150, ['Health checks fail', 'every few seconds', '→ AZ b marked unhealthy'], 'amber'))
    f4 = (sa_flow(users, 'blue', 1.6, 6) + sa_flow(to_a1, 'blue', 0.9, 4) + sa_flow(to_a2, 'blue', 0.9, 4) + dark_b +
          sa_gauge(250, 104, 88, 'CPU') + sa_badge(120, 70, 4) + sa_note(552, 150, 150, ['All orders → AZ a', 'CPU rises to 88%', 'customers barely notice'], 'saffron'))
    f5 = (sa_flow(users, 'blue', 1.6, 6) + sa_flow(to_a1, 'blue', 1.4, 3) + sa_flow('M440 60 C480 80 500 86 501 104', 'blue', 1.4, 3) + sa_flow('M450 60 C520 80 550 86 551 104', 'blue', 1.4, 3) + dark_b +
          f'<g class="sa-pop">{sa_server(484, 104, col="green", label="web-5 new")}</g><g class="sa-pop">{sa_server(534, 104, col="green", label="web-6 new")}</g>' +
          sa_gauge(250, 104, 55, 'CPU') + sa_badge(120, 70, 5, 'green') + sa_note(552, 190, 150, ['Auto Scaling', 'launches 2 servers', 'in healthy AZ c'], 'green'))
    f6 = (sa_flow(users, 'blue', 2.0, 5) + sa_flow(to_a1, 'blue', 1.4, 3) + sa_flow('M450 60 C520 80 550 86 551 104', 'blue', 1.4, 3) + dark_b +
          sa_server(484, 104, col='green', label='web-5') + sa_server(534, 104, col='green', label='web-6') +
          sa_db(176, 222, '', crown=True) + f'<rect x="132" y="258" width="90" height="16" rx="8" style="fill:#2F7D5B"/><text x="177" y="269" text-anchor="middle" font-size="7.6" font-weight="700" style="fill:#fff">now PRIMARY</text>' +
          sa_flow('M157 148 L170 214', 'green', 1.0, 2, 3) + sa_tick(600, 60, 13) +
          sa_badge(120, 70, 6, 'green') + sa_note(552, 230, 150, ['DB failover 1–2 min', 'standby → primary', 'no data lost'], 'green'))
    return scene_anim('An Availability Zone fails — watch what happens', 'TiffinGo’s 1:10 pm outage, as it happens inside Mumbai. Blue dots are customer requests; green dots are database copies.', 'AZ failure',
        'Animation: customers send orders through a load balancer to servers in AZ a and AZ b; AZ b loses power; health checks mark it unhealthy; all traffic goes to AZ a and CPU rises; Auto Scaling launches servers in AZ c; the database standby in AZ a becomes primary with no data loss.',
        st, [(f1, 'Step 1 · Normal lunch hour', 'the load balancer spreads orders over servers in AZ a and AZ b; every database write is copied synchronously from the primary (AZ b) to the standby (AZ a).'),
             (f2, 'Step 2 · 1:10 pm — AZ b loses power', 'its servers and the database primary stop. AZ a and AZ c are separate buildings with separate power, so they keep running.'),
             (f3, 'Step 3 · Health checks notice', 'the load balancer probes every target every few seconds; after consecutive failures AZ b’s servers are marked unhealthy and get no new orders.'),
             (f4, 'Step 4 · All orders flow to AZ a', 'capacity is halved, CPU climbs to about 88% — this is why you size for losing one AZ (N+1).'),
             (f5, 'Step 5 · Auto Scaling heals', 'the Auto Scaling group sees missing capacity and launches new servers in the healthy AZ c within minutes; CPU drops back.'),
             (f6, 'Step 6 · Database fails over', 'RDS promotes the standby in AZ a to primary and repoints its DNS name in about 1–2 minutes; because copies were synchronous, no order is lost.')], hid='azfail')

def single_vs_multi():
    """Static situation picture: the same outage, single-AZ vs multi-AZ."""
    o = t(320, 16, 'The same power cut, two designs', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 200, 'Competitor: everything in AZ b', 'red') + sa_building(328, 28, 300, 200, 'TiffinGo: AZ a + AZ b', 'green')
    o += sa_server(70, 70) + sa_server(120, 70) + sa_db(200, 80, 'database') + sa_dark(24, 46, 276, 120) + sa_bolt(150, 92, 1.6)
    o += sa_cross(262, 66, 14) + t(162, 190, 'site down for 2 hours', 9, 'ink', bold=True) + t(162, 206, '≈ 600 lunch orders lost', 7.6, 'ink2')
    o += sa_building(340, 46, 130, 120, 'AZ a', 'green') + sa_building(486, 46, 130, 120, 'AZ b', 'green')
    o += sa_server(360, 72) + sa_server(410, 72) + sa_server(506, 72) + sa_server(556, 72) + sa_dark(486, 46, 130, 120) + sa_bolt(540, 92, 1.4)
    o += sa_tick(604, 40, 13) + t(478, 190, 'orders keep flowing', 9, 'ink', bold=True) + t(478, 206, 'AZ a carries the load; replacements start', 7.6, 'ink2')
    return bigfig('Two designs during the same power cut: the competitor with everything in one AZ goes down; TiffinGo with servers in two AZs keeps taking orders.', o, h=240)

def latency_map():
    """Static: Dubai user with and without edge caching."""
    o = t(320, 16, 'Why Dubai users wait — and how the edge fixes it', 11, 'ink', bold=True)
    o += sa_people(30, 70, 1) + t(36, 104, 'Dubai user', 8, 'ink', bold=True)
    o += box(500, 50, 120, 54, 'blue', rx=8) + t(560, 72, 'Mumbai Region', 8.4, 'ink', bold=True) + t(560, 88, 'S3: menu photos', 7, 'ink2')
    o += f'<path d="M60 70 C200 20 380 20 500 70" class="sa-dash" style="fill:none;stroke:#D64545;stroke-width:2"/>' + t(290, 62, 'direct: ~1,900 km each way, tens of ms per round trip, many round trips', 7.4, 'ink')
    o += box(200, 130, 130, 50, 'amber', rx=8) + t(265, 151, 'Edge location', 8.4, 'ink', bold=True) + t(265, 166, 'near Dubai (cache)', 7, 'ink2')
    o += f'<path d="M60 90 C110 140 150 156 200 156" style="fill:none;stroke:#2F7D5B;stroke-width:3"/>' + t(120, 160, 'few ms', 8, 'ink', bold=True)
    o += f'<path d="M330 150 C420 140 470 120 520 104" style="fill:none;stroke:#7A8496;stroke-width:1.5;stroke-dasharray:4 3"/>' + t(440, 150, 'fetched once, then cached', 7, 'ink2')
    o += t(320, 206, 'Before: every request crosses the Arabian Sea. After: the first request fills the edge cache; everyone else is served nearby.', 7.4, 'ink2')
    return bigfig('A Dubai user loading photos directly from Mumbai pays the distance on every request; with an edge location near Dubai, photos are cached and served in a few milliseconds.', o, h=220)
