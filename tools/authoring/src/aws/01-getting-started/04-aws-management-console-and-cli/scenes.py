from cloudkit import *

def cli_scene():
    cmd = "$ aws s3api list-buckets --query 'Buckets[].Name' --output table"
    st = sa_screen(14, 20, 300, 60, 'CloudShell — ap-south-1', ['$ aws s3api list-buckets', "    --query 'Buckets[].Name' --output table"], dark=True)
    chain = ['1 --profile / --region', '2 environment variables', '3 SSO / role profile', '4 ~/.aws/credentials', '5 container role (CloudShell)', '6 EC2 instance role']
    st += box(14, 100, 190, 112, 'card', rx=8) + t(109, 116, 'Credential provider chain', 8, 'ink', bold=True)
    st += ''.join(t(24, 132 + i * 13, c, 7, 'ink2', anchor='start') for i, c in enumerate(chain))
    st += box(14, 226, 190, 50, 'card', rx=8) + t(109, 242, 'Config', 8, 'ink', bold=True) + t(109, 258, 'region ap-south-1 · output json', 7, 'ink2')
    st += box(236, 150, 84, 44, 'red', rx=8) + sa_icon('shield', 244, 158, 1.0, 'red') + t(286, 168, 'SigV4', 8, 'ink', bold=True) + t(286, 182, 'sign', 6.8, 'ink2')
    st += sa_building(340, 20, 286, 150, 'AWS · s3.ap-south-1.amazonaws.com', 'blue')
    st += box(360, 50, 90, 40, 'red', rx=8) + t(405, 74, 'IAM check', 8, 'ink', bold=True) + box(470, 50, 90, 40, 'green', rx=8) + t(515, 74, 'ListBuckets', 8, 'ink', bold=True)
    st += box(360, 110, 200, 44, 'card', rx=8) + t(460, 128, 'CloudTrail: ListBuckets by riya-admin', 7, 'ink2')
    hl = lambda i, col: f'<rect class="sa-pop" x="18" y="{123 + i * 13}" width="182" height="12" rx="3" style="fill:{SA_COL[col]};opacity:.25"/>'
    f1 = '<rect class="sa-glow" x="18" y="36" width="292" height="26" rx="4" style="fill:none;stroke:#E0A100;stroke-width:2"/>' + sa_badge(330, 30, 1) + sa_note(170, 286, 300, ['You type: service (s3api) · operation (list-buckets) · options'], 'saffron')
    f2 = hl(0, 'grey') + hl(1, 'grey') + hl(2, 'grey') + hl(3, 'grey') + hl(4, 'green') + sa_cross(196, 133, 6) + sa_cross(196, 146, 6) + sa_cross(196, 159, 6) + sa_cross(196, 172, 6) + sa_tick(196, 185, 6) + sa_flow('M110 80 L110 100', 'blue', 0.8, 2, 3) + sa_badge(330, 30, 2) + sa_note(170, 286, 300, ['Credentials: first source that exists wins → #5 container role'], 'green')
    f3 = '<rect class="sa-glow" x="18" y="230" width="182" height="42" rx="6" style="fill:none;stroke:#E0A100;stroke-width:2"/>' + sa_badge(330, 30, 3) + sa_note(170, 286, 300, ['Config: Region ap-south-1, output json (overridden by --output)'], 'saffron')
    f4 = sa_flow('M204 186 C220 180 226 176 236 172', 'red', 0.9, 2) + sa_flow('M204 248 C220 230 226 200 236 186', 'red', 0.9, 2) + sa_icon('lock', 300, 196, 0.9, 'green') + sa_badge(330, 30, 4, 'red') + sa_note(170, 286, 300, ['Request built and signed locally — the secret never leaves'], 'red')
    f5 = sa_flow('M320 170 C340 160 345 90 360 76', 'blue', 1.0, 3, 4, 'HTTPS', 336, 128) + sa_tick(440, 50, 8) + sa_flow('M450 70 L470 70', 'green', 0.8, 2, 3) + '<g class="sa-pop">' + sa_screen(470, 186, 156, 70, 'response (JSON)', ['{"Buckets": [', ' {"Name": "tiffingo-menu",', '  "CreationDate": …}, …]}'], dark=True) + '</g>' + sa_badge(330, 30, 5, 'blue') + sa_note(170, 286, 300, ['IAM allows → S3 lists buckets → CloudTrail logs → JSON comes back'], 'blue')
    f6 = sa_screen(470, 186, 156, 70, 'response (JSON)', ['{"Buckets": [', ' {"Name": "tiffingo-menu",', '  "CreationDate": …}, …]}'], dark=True) + sa_flow('M470 230 C420 250 400 270 380 280', 'violet', 1.0, 2) + '<g class="sa-pop">' + sa_screen(236, 210, 140, 58, '--query + --output table', ['+-----------------+', '| tiffingo-menu   |', '| tiffingo-logs   |'], dark=True) + '</g>' + sa_badge(330, 30, 6, 'violet') + sa_note(170, 286, 300, ['JMESPath keeps only names, on your side, printed as a table'], 'violet')
    return scene_anim('What happens when you run one CLI command', 'From keyboard to table — each step lights up the part of the CLI or AWS doing the work.', 'CLI flow',
        'Animation: you type a command; the CLI checks the credential provider chain and picks the container role; reads Region and output config; signs the request; S3 answers with JSON after IAM allows it; --query and --output turn it into a table.',
        st, [(f1, 'Step 1 · You type a command', 'aws + service + operation + options. The CLI parses it before contacting AWS.'),
             (f2, 'Step 2 · Find credentials', 'the provider chain is checked in order; in CloudShell the first one present is the container role from your console session.'),
             (f3, 'Step 3 · Read configuration', 'Region and output come from options, environment variables or ~/.aws/config. No Region → “You must specify a region”.'),
             (f4, 'Step 4 · Build and sign', 'the CLI builds the HTTPS request and signs it with SigV4. Your secret key is used locally and never sent.'),
             (f5, 'Step 5 · AWS answers', 'the S3 endpoint verifies the signature, IAM allows s3:ListAllMyBuckets, S3 lists buckets, CloudTrail logs the call, JSON comes back.'),
             (f6, 'Step 6 · Shape the output', '--query (JMESPath) keeps only bucket names and --output table formats them — on your machine, after the full response arrived.')], hid='cliflow')
