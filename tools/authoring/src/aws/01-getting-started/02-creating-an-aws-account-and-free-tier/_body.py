import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import leak_scene, root_vs_admin_picture
sys.path.insert(0, HERE)
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


hk = hook('Kabir opened an AWS account on Friday, created root access keys “to save time”, and pushed them to a public GitHub repo. On Monday the bill showed $1,200 of GPU servers mining cryptocurrency.',
    'Bots scan GitHub for AWS keys within minutes. Riya’s account, opened the same day, had <b>MFA on root</b>, <b>no root keys</b>, a separate <b>admin user</b> and a <b>budget alert</b> — and cost nothing. This lesson walks through creating an AWS account safely, explains the <b>Free plan</b> and <b>Paid plan</b>, credits, always-free offers and trials, and on <b>your own</b> account you will lock down root, create an admin user and set budget alerts.',
    ['Root user: MFA on, no access keys, used almost never.', 'Daily work: an admin user (or Identity Center) with MFA.', 'Budget alert before the first resource.'])

def story_scene():
    o = t(180, 12, 'Same Friday, two accounts', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Kabir', 8.4, 'ink', bold=True) + t(88, 64, 'root keys in GitHub', 7, 'ink2') + t(88, 78, 'no MFA, no budget', 7, 'ink2') + t(88, 92, '$1,200 on Monday', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Riya', 8.4, 'ink', bold=True) + t(272, 64, 'root MFA, no root keys', 7, 'ink2') + t(272, 78, 'admin user + budget', 7, 'ink2') + t(272, 92, '$0 and an alert ready', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Ten minutes of setup prevents the worst bills', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: Kabir put root access keys in GitHub, had no MFA or budget, and got a $1,200 bill. Right: Riya enabled root MFA, created no root keys, used an admin user and a budget — $0 with an alert ready.', story_scene(), 'Secure the account <tspan font-weight="700" class="s-acc">before</tspan> you build.', h=132)
dialogue = '''K> Sir, I only wanted to try the CLI. Root keys were the fastest way.
A> Root can do anything, including close the account. Leaked root keys are the worst case. AWS support can sometimes adjust a first bill, but never count on it.
R> So what should he have done?
A> MFA on root, never create root keys, make an admin user for daily work, and set a budget. Ten minutes.
K> And the Free Tier? I thought it was all free.
A> New accounts choose a Free plan with credits for six months, or a Paid plan. Some services are always free up to limits. Let’s read it properly.'''

def bigpic():
    o = t(320, 16, 'From sign-up to a safe account', 11, 'ink', bold=True)
    S = [('1', 'Sign up', 'e-mail, card, phone', 'blue'), ('2', 'Choose plan', 'Free or Paid', 'amber'), ('3', 'Lock root', 'MFA, no keys', 'red'), ('4', 'Admin user', 'daily work + MFA', 'violet'), ('5', 'Budget', 'alerts by e-mail', 'green')]
    for i, (n, a, b, tn) in enumerate(S):
        x = 12 + i * 126
        o += box(x, 36, 118, 80, tn, rx=8) + pin(x + 14, 50, n) + t(x + 59, 74, a, 8.6, 'ink', bold=True) + t(x + 59, 94, b, 6.8, 'ink2')
        if i < 4: o += arrow(x + 118, 76, x + 126, 76)
    o += t(320, 140, 'Do steps 3–5 before creating any resource; then sign out of root.', 7.4, 'ink2')
    return o
BIG = bigfig('Five steps: sign up with e-mail, card and phone; choose the Free or Paid plan; lock the root user with MFA and no keys; create an admin user with MFA; set a budget with e-mail alerts.', bigpic(), h=150)

picture = ('  <p>An <b>AWS account</b> is the container for everything you create and the unit AWS bills. It comes with one all-powerful <b>root user</b>. A safe start is five steps:</p>\n' + BIG +
           '\n  <h3>Free plan vs Paid plan (for accounts created from 15 July 2025)</h3>\n' + table(['', 'Free plan', 'Paid plan'], [
               ['Sign-up credits', 'USD 100', 'USD 100'], ['Extra credits for activities', 'up to USD 100', 'up to USD 100'],
               ['How long', 'six months or until credits are used, whichever comes first', 'no end; pay as you go after credits'],
               ['Charges', 'none while on the plan', 'normal prices beyond credits/free limits'],
               ['Services', 'select services; things that could drain credits (e.g. Savings Plans, Reserved Instances, some Marketplace offers) are blocked', 'all services'],
               ['At the end', 'account closes; data kept 90 days unless you upgrade', 'continues'],
               ['Automatic upgrade', 'e.g. joining AWS Organizations or setting up Control Tower', '—']], minw=600) +
           '\n  <h3>The one picture to remember</h3>\n' + root_vs_admin_picture() + '\n  <p>Accounts created <b>before</b> 15 July 2025 keep the older model: a 12-month free tier for some services plus always-free offers. Check the AWS Free Tier page for current details — they change.</p>')

SOLVE = leak_scene()

def mapfig():
    o = t(320, 16, 'Seven ways to get started on AWS (free or paid)', 11, 'ink', bold=True)
    items = [('1', 'Free plan', '6 months / credits', 'green'), ('2', 'Paid plan', 'all services', 'blue'), ('3', 'Credits', '$100 + up to $100', 'amber'), ('4', 'Always free', 'monthly limits', 'green'),
             ('5', 'Short-term trials', 'some services', 'violet'), ('6', 'Legacy 12-month', 'pre-15 Jul 2025', 'card'), ('7', 'Programmes', 'Educate · Academy · Activate', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'Several apply at once: e.g. Free plan + credits + always-free limits.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven ways to start on AWS: Free plan, Paid plan, credits, always-free offers, short-term trials, legacy 12-month free tier, and programmes such as AWS Educate, AWS Academy and AWS Activate.', mapfig(), h=222)

def ft(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 4 (Billing, pricing, support)', 'C-DAC lab setup', 'Interviews'], rw, pro)

A1 = mk(['Sign up', 'Free plan', 'End or upgrade'], ['sign up|choose Free|plan', 'use|select services|no charges', 'end|6 months/credits|upgrade or close'], ['blue', 'green', 'amber'],
        ['choose the Free plan at sign-up', 'use select services with credits; no charges', 'after six months or when credits run out: upgrade, or the account closes'],
        [('Choose', 'Free plan at sign-up.', ''), ('Use', 'Select services, credits, no charges.', ''), ('End', 'Upgrade or account closes (data kept 90 days).', '')],
        'Free plan', 'Safe sandbox with an end date.', 'Free plan', 'Animation: sign up; use; end or upgrade.', 't1anim')
T1 = ft(1, 'Free account plan', 'green',
    'The <b>Free account plan</b> (for new accounts since 15 July 2025) gives access to select services with sign-up credits and no charges, for six months or until credits are used; features that could drain credits are restricted, and at the end the account closes unless you upgrade within 90 days.',
    'A prepaid phone SIM with a fixed talk-time: you cannot overspend, and it stops when the balance or validity ends.',
    'Riya’s students each open a Free plan account for the course — no risk of a surprise bill.',
    'Tip: note your plan’s end date; upgrade before it if you want to keep your work.', A1,
    'you are learning and want zero risk of charges.', 'you need Organizations, Control Tower, Reserved Instances or Savings Plans.',
    'A free, time-limited AWS account for learning.',
    [('Sign up', 'Choose Free.'), ('Credits', 'USD 100 + activities.'), ('Limits', 'Select services.'), ('Watch', 'Remaining credits.'), ('End', 'Upgrade or close.')],
    [('credits', 'money-value applied to usage'), ('upgrade', 'switch to the Paid plan'), ('account closure', 'access stops; data kept 90 days')],
    table(['', 'Free plan'], [['Charges', 'none'], ['Duration', '6 months or credits used'], ['Services', 'select']], minw=360),
    'Ideal for classrooms and self-study.',
    'Joining an organisation upgrades the account automatically — do not join a company Organization from a learning account.')

A2 = mk(['Sign up / upgrade', 'All services', 'Pay as you go'], ['paid|chosen at sign-up|or upgrade', 'access|every service|all Regions', 'bill|after credits|monthly'], ['blue', 'amber', 'green'],
        ['choose Paid at sign-up or upgrade later', 'access every service and feature', 'pay normal prices after credits and free limits'],
        [('Choose', 'At sign-up or upgrade.', ''), ('Access', 'All services and features.', ''), ('Pay', 'After credits; monthly invoice.', '')],
        'Paid plan', 'Full access, real bills.', 'Paid plan', 'Animation: sign up or upgrade; all services; pay as you go.', 't2anim')
T2 = ft(2, 'Paid account plan', 'blue',
    'The <b>Paid account plan</b> gives immediate access to all AWS services and features; credits and free-tier limits still apply, and usage beyond them is billed at normal pay-as-you-go prices; the account does not close when credits run out.',
    'A postpaid phone connection: everything works, and the bill comes at month end.',
    'TiffinGo’s production account is on the Paid plan, with budgets and alerts.',
    'Tip: a Paid plan without a budget alert is how surprise bills happen.', A2,
    'you run real workloads or need any restricted feature.', 'you only want a risk-free sandbox.',
    'A normal AWS account with all services and real charges.',
    [('Access', 'All services.'), ('Credits', 'Still applied.'), ('Free limits', 'Still apply.'), ('Billing', 'Monthly.'), ('Guard', 'Budgets.')],
    [('pay-as-you-go', 'billed for actual usage'), ('invoice', 'monthly bill'), ('payment method', 'card or bank on file')],
    table(['', 'Free plan', 'Paid plan'], [['All services', 'no', 'yes'], ['Can be charged', 'no', 'yes'], ['Closes at end', 'yes', 'no']], minw=420),
    'Every company account is on the Paid plan.',
    'Set budgets, Cost Anomaly Detection and tags from day one on Paid accounts.')

A3 = mk(['Sign-up credit', 'Activity credits', 'Applied to bill'], ['signup|USD 100|automatic', 'activities|up to USD 100|complete tasks', 'apply|usage first|then charges'], ['amber', 'green', 'blue'],
        ['USD 100 credit at sign-up', 'earn up to USD 100 more by completing activities', 'credits are applied to eligible usage before any charge'],
        [('Sign-up', 'USD 100 automatically.', ''), ('Activities', 'Up to USD 100 more.', ''), ('Apply', 'Credits cover eligible usage first.', '')],
        'Credits', 'Money-value for learning.', 'Credits', 'Animation: sign-up credit; activity credits; applied to bill.', 't3anim')
T3 = ft(3, 'Credits', 'amber',
    '<b>Credits</b> are a money-value balance applied to eligible AWS usage: new accounts receive USD 100 at sign-up and can earn up to USD 100 more by completing guided activities; credits have an expiry and do not cover every charge.',
    'A gift card for a supermarket: it pays for most items until the balance or expiry date runs out.',
    'Riya’s course labs use only a few dollars of credits in total.',
    'Tip: credits do not make expensive mistakes safe on the Paid plan — they only delay the bill.', A3,
    'you start a new account.', 'you assume credits cover everything (some services or Marketplace items are excluded).',
    'Money-value that AWS gives you to try services.',
    [('Receive', 'Sign-up.'), ('Earn', 'Activities.'), ('Apply', 'Eligible usage.'), ('Watch', 'Billing → Credits.'), ('Expire', 'Check date.')],
    [('credit', 'balance applied to your bill'), ('eligible', 'usage the credit can pay for'), ('expiry', 'date after which credit is lost')],
    table(['Source', 'Amount'], [['Sign-up', 'USD 100'], ['Activities', 'up to USD 100'], ['Programmes', 'varies']], minw=320),
    'Exams ask about pricing models and billing tools rather than credit amounts — but interviews like real numbers.',
    'Check Billing → Credits for exact balance and expiry; amounts can change over time.')

A4 = mk(['Service with limit', 'Monthly allowance', 'Above limit'], ['service|Lambda, DynamoDB|SNS…', 'allowance|resets monthly|no expiry', 'above|normal price|on Paid plan'], ['green', 'blue', 'amber'],
        ['some services have an always-free allowance', 'it resets every month and does not expire', 'usage above it is charged on the Paid plan'],
        [('Service', 'Lambda, DynamoDB, SNS and others.', ''), ('Allowance', 'Monthly, never expires.', ''), ('Above', 'Normal price on Paid plan.', '')],
        'Always free', 'Small monthly allowances, forever.', 'Always free', 'Animation: service with limit; monthly allowance; above limit.', 't4anim')
T4 = ft(4, 'Always-free offers', 'green',
    '<b>Always-free offers</b> are monthly usage allowances that never expire, available on both plans — for example AWS Lambda (1 million requests and 400,000 GB-seconds of compute per month) and Amazon DynamoDB (25 GB of storage); exact limits are listed on the Free Tier page.',
    'A free daily newspaper page in the library: always there, but only one page.',
    'TiffinGo’s SMS-sending Lambda function stays inside the always-free requests each month.',
    'Tip: always-free is per account per month across all Regions — not per Region.', A4,
    'your usage is small and steady.', 'you plan heavy production traffic.',
    'Small monthly allowances that stay free forever.',
    [('Service', 'Check list.'), ('Limit', 'Per month.'), ('Scope', 'Whole account.'), ('Track', 'Free Tier page.'), ('Above', 'Charged (Paid).')],
    [('allowance', 'free quantity'), ('GB-second', 'memory × duration unit for Lambda'), ('reset', 'allowance renews monthly')],
    table(['Service', 'Example always-free allowance'], [['Lambda', '1M requests + 400,000 GB-s / month'], ['DynamoDB', '25 GB storage'], ['SNS', 'mobile push / publish allowance']], minw=420),
    'CLF-C02 asks you to know the three Free Tier offer types: always free, 12-month/plan-based and trials.',
    'Track usage with the Free Tier usage alerts and the <code>freetier</code> API in the lab.')

A5 = mk(['Activate trial', 'Limited period', 'Normal price'], ['trial|from first use|of a service', 'period|e.g. 30–60 days|monthly limits', 'after|pay as you go|on Paid'], ['violet', 'amber', 'blue'],
        ['a trial starts when you first use that service', 'it lasts a limited period with usage limits', 'after it ends, normal prices apply on the Paid plan'],
        [('Start', 'From first use of the service.', ''), ('Period', 'Limited days and limits.', ''), ('After', 'Normal prices.', '')],
        'Short-term trials', 'A clock starts on first use.', 'Trials', 'Animation: activate trial; limited period; normal price.', 't5anim')
T5 = ft(5, 'Short-term free trials', 'violet',
    '<b>Short-term trials</b> give free usage of selected services for a limited period that starts when you first use the service; when it ends, normal pricing applies.',
    'A gym trial week: it starts on your first visit, not on the day you got the pass.',
    'Kabir tried a managed service for a demo; the trial clock started that day.',
    'Tip: do not “warm up” a trial early — start it when you are ready to use it.', A5,
    'you want to evaluate a service briefly.', 'you will forget to stop it after the trial.',
    'Free use of some services for a short time.',
    [('Find', 'Free Tier page filter “trials”.'), ('Start', 'First use.'), ('Use', 'Within limits.'), ('Track', 'Free Tier page.'), ('Stop', 'Before it ends.')],
    [('trial period', 'free days for a service'), ('first use', 'start of the clock'), ('limit', 'maximum free usage')],
    table(['Offer', 'Clock starts'], [['Always free', 'never expires'], ['Trial', 'first use of the service'], ['Free plan', 'account creation']], minw=360),
    'Exam keyword: “trial” = short-term, service-specific.',
    'Delete trial resources the day you finish — trial resources continue billing after the trial.')

A6 = mk(['Old account', '12 months', 'Then charged'], ['before|15 Jul 2025|sign-up', 'free|12-month offers|e.g. t2/t3.micro', 'after|month 13|normal price'], ['card', 'amber', 'red'],
        ['accounts created before 15 July 2025', 'got 12-month free-tier offers from sign-up', 'after 12 months those offers end and normal prices apply'],
        [('Old', 'Created before 15 Jul 2025.', ''), ('12 months', 'Offers like 750 hours/month of a micro instance.', ''), ('After', 'Normal prices from month 13.', '')],
        'Legacy 12-month free tier', 'Older accounts, older rules.', 'Legacy', 'Animation: old account; 12 months; then charged.', 't6anim')
T6 = ft(6, 'Legacy 12-month free tier', 'card',
    'The <b>legacy 12-month free tier</b> applies to accounts created before 15 July 2025: selected services were free up to limits (for example 750 hours a month of a micro EC2 instance and 5 GB of S3 Standard) for the first 12 months, plus always-free offers; after that, normal prices apply.',
    'An old phone plan you kept: its rules are different from today’s plans.',
    'Arjun Sir’s 2023 account is past 12 months — every EC2 hour is charged now.',
    'Tip: many tutorials still describe the 12-month model — check your account’s actual plan in Billing.', A6,
    'your account was created before 15 July 2025.', 'you follow old tutorials on a new account.',
    'The older free tier for accounts created before mid-2025.',
    [('Check', 'Account creation date.'), ('Offers', '12-month list.'), ('Limits', 'Per month.'), ('Expiry', 'Month 12.'), ('After', 'Paid.')],
    [('legacy', 'older rules still in force for old accounts'), ('750 hours', 'about one instance running all month'), ('month 13', 'when offers end')],
    table(['', 'Legacy', 'Since 15 Jul 2025'], [['Model', '12-month offers', 'Free/Paid plan + credits'], ['Charges in year 1', 'above limits', 'none on Free plan'], ['Always free', 'yes', 'yes']], minw=420),
    'Older exam materials and blogs describe this model.',
    'If you are on a legacy account, a budget alert is essential — there is no automatic stop.')

A7 = mk(['Who you are', 'Programme', 'What you get'], ['who|student|educator, startup', 'programme|Educate · Academy|Activate', 'get|labs, courses|credits'], ['amber', 'blue', 'green'],
        ['who you are: student, educator or startup', 'the matching AWS programme', 'what it gives: no-card labs, curriculum or credits'],
        [('Who', 'Student, educator, startup.', ''), ('Programme', 'Educate, Academy, Activate.', ''), ('Get', 'Labs, curriculum, credits.', '')],
        'Programmes', 'Free learning paths.', 'Programmes', 'Animation: who you are; programme; what you get.', 't7anim')
T7 = ft(7, 'Learning and startup programmes', 'amber',
    '<b>AWS programmes</b> add free access beyond the Free Tier: <b>AWS Educate</b> (self-paced learning and labs, no credit card), <b>AWS Academy</b> (curriculum and lab environments delivered by institutions) and <b>AWS Activate</b> (credits and support for eligible startups), alongside <b>AWS Skill Builder</b> for training.',
    'Scholarships: a library card for students, a teaching kit for colleges, and seed money for new businesses.',
    'C-DAC-style institutes can run courses through AWS Academy; TiffinGo could apply to Activate as a startup.',
    'Tip: sandbox labs from programmes are perfect for practice without any billing risk.', A7,
    'you are a student, educator or startup.', 'you need a long-running personal account (use the Free/Paid plan).',
    'Free AWS programmes for students, colleges and startups.',
    [('Eligibility', 'Check.'), ('Apply', 'Programme site.'), ('Use', 'Labs/credits.'), ('Limits', 'Sandbox rules.'), ('Move on', 'Own account.')],
    [('sandbox', 'temporary, limited lab account'), ('curriculum', 'course material for teachers'), ('startup credits', 'credits for new companies')],
    table(['Programme', 'For', 'Gives'], [['AWS Educate', 'learners', 'self-paced labs, no card'], ['AWS Academy', 'institutions', 'curriculum + lab environments'], ['AWS Activate', 'startups', 'credits + support']], minw=420),
    'Mention these in student interviews — it shows you know how to learn cheaply.',
    'Programme details change — check eligibility on the official pages before promising them to students.')

SUMMARY = table(['#', 'Option', 'Key point', 'Watch out'], [
    ['1', 'Free plan', 'no charges; 6 months or credits', 'closes at end'], ['2', 'Paid plan', 'all services', 'real bills'], ['3', 'Credits', '$100 + up to $100', 'expiry, exclusions'],
    ['4', 'Always free', 'monthly allowances', 'account-wide limits'], ['5', 'Trials', 'start on first use', 'normal price after'], ['6', 'Legacy 12-month', 'pre-15 Jul 2025 accounts', 'ends month 12'], ['7', 'Programmes', 'Educate, Academy, Activate', 'eligibility']], minw=600)

TYPES = ('  <p>Seven ways to get free or paid access to AWS, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which plan blocks Savings Plans and Reserved Instances?', 'When does a short-term trial’s clock start?', 'What happens at the end of the Free plan if you do not upgrade?'], 'types 1, 5 and 1') + MAP
         + jump(['Free plan', 'Paid plan', 'Credits', 'Always free', 'Trials', 'Legacy', 'Programmes']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('AWS account', 'Container for resources and billing.', 'Isolation boundary.', '12-digit account ID.'),
    ('Root user', 'E-mail sign-in with full power.', 'Cannot be restricted by IAM.', 'MFA, no keys, rare use.'),
    ('IAM / Identity Center users', 'Everyday identities.', 'Least privilege, MFA.', 'Admin user for you.'),
    ('Account plan', 'Free or Paid.', 'Decides charges and access.', 'Billing → plan.'),
    ('Budgets', 'Alerts on cost.', 'Early warning.', 'Monthly $5 / zero-spend.'),
    ('Contacts and support', 'Alternate contacts, Basic support.', 'Security e-mails reach you.', 'Account settings.')])

DEEP = ('  <h3>Tasks only the root user can do</h3>\n  <ul><li>Change account name, root e-mail or root password.</li><li>Close the AWS account.</li><li>Change or cancel the support plan.</li><li>Restore permissions when an IAM admin locks everyone out.</li><li>Some billing tasks and tax settings.</li></ul>\n  <p>Everything else should be done as a user or role. Keep root credentials and the MFA device safe and offline.</p>\n'
    '  <h3>Why not root access keys?</h3>\n  <p>Access keys are long-term secrets used by the CLI/SDK. Root keys cannot be limited by IAM policies, so a leak means total compromise. Use CloudShell (temporary credentials), IAM Identity Center (short-lived SSO credentials) or, if you must, an IAM user’s keys with least privilege and rotation.</p>\n'
    '  <h3>IAM user or IAM Identity Center?</h3>\n' + table(['', 'IAM user', 'IAM Identity Center'], [['Best for', 'single learning account', 'companies, many accounts'], ['Credentials', 'password + optional long-term keys', 'SSO sign-in, short-lived credentials'], ['Needs Organizations', 'no', 'organisation instance yes (upgrades a Free plan to Paid)'], ['AWS recommendation', 'limited use', 'preferred for people']], minw=520) +
    '\n  <h3>Sign-up checklist</h3>\n  <ol><li>Use a long-lived e-mail (a group alias for companies), not a personal one you may lose.</li><li>Card for verification (Indian cards may need online/international transactions enabled; a small refundable verification charge may appear).</li><li>Phone verification.</li><li>Support plan: Basic (free).</li></ol>')

clouds = vendor_tabs('<p><b>AWS:</b> Free or Paid plan with credits (since July 2025), always-free offers, trials; root user + IAM/Identity Center.</p>',
    '<p><b>Azure:</b> free account with credit for 30 days, 12 months of popular services and always-free services; Entra ID tenant with Global Administrator.</p>',
    '<p><b>Google Cloud:</b> free trial credit for 90 days plus Free Tier always-free limits; Google account as project Owner.</p>') + \
    cloud3([['All-powerful first identity', 'root user', 'Global Administrator', 'Owner / Super Admin'], ['Daily admin', 'IAM user / Identity Center', 'Entra user with role', 'Google account with role'], ['Budget alerts', 'AWS Budgets', 'Cost Management budgets', 'Billing budgets'], ['Free start', 'Free plan + credits', 'free account credit', 'free trial credit']])

MOCKA.extend([
 mock('aws', ['Account', 'Security credentials'], ['Account', 'Security credentials', 'Billing'], 'Security credentials', [('Multi-factor authentication (MFA)', 'Assign MFA device'), ('Access keys', 'No access keys ✓'), ('Device type', '( ) Passkey · ( ) Authenticator app')], 'Assign MFA device'),
 mock('aws', ['IAM', 'Users', 'Create user'], ['Dashboard', 'User groups', 'Users', 'Roles'], 'Users', [('User name', 'riya-admin'), ('Console access', '[x] Provide user access to the AWS Management Console'), ('Permissions', '▾ Add user to group: Admins')], 'Create user'),
 mock('aws', ['Billing and Cost Management', 'Budgets', 'Create budget'], ['Home', 'Bills', 'Free Tier', 'Budgets'], 'Budgets', [('Template', '( ) Zero spend budget · ( ) Monthly cost budget'), ('Budgeted amount', '$5.00'), ('E-mail recipients', 'you@example.com')], 'Create budget'),
])

STEP1 = astep('1 · Lock the root user (MFA, no keys)',
    ['Sign in as root (your sign-up e-mail) → account menu (top right) → [[Security credentials]].', '[[Assign MFA device]] → choose a passkey or an authenticator app → follow the prompts.', 'Under [[Access keys]] confirm there are none — delete any you created.'],
    "# run in CloudShell while signed in as root (only this once)\naws iam get-account-summary --query 'SummaryMap.{rootMFA:AccountMFAEnabled,rootKeys:AccountAccessKeysPresent}'",
    '<code>rootMFA: 1</code> and <code>rootKeys: 0</code>. If <code>rootKeys</code> is 1, delete the key in Security credentials now.',
    'Root MFA is set in the console only. This is the single most important security step in AWS.')

STEP2 = astep('2 · Create an admin user for daily work',
    ['[[IAM]] → [[User groups]] → [[Create group]] <code>Admins</code> → attach <code>AdministratorAccess</code>.', '[[Users]] → [[Create user]] <code>riya-admin</code> → [[Provide user access to the AWS Management Console]] → custom password, must change at next sign-in → add to <code>Admins</code>.', 'Copy the sign-in URL, sign out of root, sign in as <code>riya-admin</code> → [[Security credentials]] → [[Assign MFA device]].'],
    "aws iam create-group --group-name Admins\naws iam attach-group-policy --group-name Admins --policy-arn arn:aws:iam::aws:policy/AdministratorAccess\naws iam create-user --user-name riya-admin\naws iam add-user-to-group --group-name Admins --user-name riya-admin\nread -s -p \"Temporary password: \" PW; echo\naws iam create-login-profile --user-name riya-admin --password \"$PW\" --password-reset-required\nACC=$(aws sts get-caller-identity --query Account --output text)\necho \"Sign in at: https://$ACC.signin.aws.amazon.com/console\"\naws iam list-groups-for-user --user-name riya-admin --query 'Groups[].GroupName' --output text",
    'the sign-in URL and <code>Admins</code>. Sign out of root, sign in as riya-admin, change the password and add MFA. From now on, root stays locked away.',
    'The password is typed with <code>read -s</code> so it never appears on screen or in shell history. Companies use IAM Identity Center instead (it needs AWS Organizations, which moves a Free plan to Paid).')

STEP3 = astep('3 · Budget alerts and your plan',
    ['Signed in as riya-admin: [[Billing and Cost Management]] → [[Budgets]] → [[Create budget]] → [[Zero spend budget]] (alerts on the first cent) — and a monthly cost budget of $5.', 'Billing home: note your plan (Free/Paid), remaining credits and end date.'],
    "ACC=$(aws sts get-caller-identity --query Account --output text)\naws budgets create-budget --account-id $ACC \\\n  --budget '{\"BudgetName\":\"monthly-5usd\",\"BudgetLimit\":{\"Amount\":\"5\",\"Unit\":\"USD\"},\"TimeUnit\":\"MONTHLY\",\"BudgetType\":\"COST\"}' \\\n  --notifications-with-subscribers '[{\"Notification\":{\"NotificationType\":\"ACTUAL\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":80,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"you@example.com\"}]},{\"Notification\":{\"NotificationType\":\"FORECASTED\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":100,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"you@example.com\"}]}]'\naws budgets describe-budgets --account-id $ACC --query 'Budgets[].[BudgetName,BudgetLimit.Amount,CalculatedSpend.ActualSpend.Amount]' --output table\naws freetier get-account-plan-state --region us-east-1 --query '{plan:accountPlanType,status:accountPlanStatus,credits:accountPlanRemainingCredits.amount,ends:accountPlanExpirationDate}'",
    'a table with <code>monthly-5usd</code> (and the zero-spend budget if you made it in the console), current spend near 0, and your plan, credits and end date. Replace the e-mail with yours before running.',
    'Simple budget alerts like these are enough for learning; AWS checks spend a few times a day, so alerts arrive within hours of crossing a threshold.')


SIMD = awsfig('Account diagram: root user locked with MFA; Admins group with AdministratorAccess; riya-admin user in the group; monthly budget with e-mail alert.',
    grp('acct', 10, 10, 620, 200, 'AWS account {acct}') +
    svc(80, 50, 'lock', 'root user', 'MFA, no keys', 'red', k='root') +
    grp('cloud', 170, 34, 250, 160, 'IAM', k='iam') +
    svc(240, 60, 'role', 'Admins', 'group', 'violet', k='grp') +
    svc(240, 130, 'key', 'AdministratorAccess', 'managed policy', 'amber', k='pol', w=96) +
    svc(350, 95, 'user', 'riya-admin', 'console + MFA', 'blue', k='user') +
    link(275, 86, 315, 110, k='member', label='member') + link(240, 112, 240, 128, k='attach') +
    svc(530, 60, 'meter', 'monthly-5usd', 'budget', 'green', k='budget') + svc(530, 135, 'mail', 'E-mail alert', '80% / forecast 100%', 'green', k='alert', w=86) +
    link(530, 112, 530, 133, k='notify'), h=222)
SIM = simlab(dict(title='Secure a new AWS account', intro='Do the whole lab here first: each step works in the <b>Console</b> tab or by typing the real command in <b>CloudShell</b>. The diagram lights up as you build.',
    vars={'you': 'root (sign-up e-mail)'}, diagram=SIMD,
    banner='Welcome to AWS CloudShell (simulated).\nRegion: {region}   Signed in as: root — only for this setup!\nType  help  for help.',
    free=[dict(re=r'^aws sts get-caller-identity$', out='{\n    "UserId": "{acct}",\n    "Account": "{acct}",\n    "Arn": "arn:aws:iam::{acct}:root"\n}')],
    steps=[
     dict(title='Lock root with MFA', goal='Turn on MFA for the root user and confirm root has no access keys.',
          hint='Console: Security credentials → Assign MFA device. CLI: check with <code>aws iam get-account-summary</code>.', answer="aws iam get-account-summary --query 'SummaryMap.{rootMFA:AccountMFAEnabled,rootKeys:AccountAccessKeysPresent}'",
          cli=[dict(re=r"^aws iam get-account-summary( --query .*)?( --output \w+)?$", out='{\n    "rootMFA": 1,\n    "rootKeys": 0\n}')],
          errors=[dict(re=r'^aws iam create-access-key$', out='STOP: you are signed in as root. Root access keys cannot be limited by any policy.\nThis is exactly what leaked in Kabir’s story. Do not create them.')],
          console=dict(crumbs='Account › Security credentials › Assign MFA device', fields=[dict(label='Device name', key='mfa', re=r'^[\w+=,.@-]{1,64}$', ph='root-phone', why='Use letters, numbers and + = , . @ - only.'),
                       dict(label='MFA device', type='select', options=['Passkey or security key', 'Authenticator app', 'Hardware TOTP token'], re=r'.+', why='Choose an MFA device type.')], button='Add MFA', out='MFA device assigned to the root user.'),
          lights=['root'], explain='AWS now asks for a second factor every time root signs in. The account summary shows <code>AccountMFAEnabled = 1</code> and <code>AccountAccessKeysPresent = 0</code> — nothing for a bot to steal.'),
     dict(title='Create the Admins group', goal='Create an IAM group named <code>Admins</code>.', hint='CLI: <code>aws iam create-group --group-name Admins</code>.', answer='aws iam create-group --group-name Admins',
          cli=[dict(re=r'^aws iam create-group --group-name (?<grp>Admins)$', out='{\n    "Group": {\n        "Path": "/",\n        "GroupName": "Admins",\n        "GroupId": "AGPA5EXAMPLE{rnd}",\n        "Arn": "arn:aws:iam::{acct}:group/Admins",\n        "CreateDate": "2026-11-12T09:30:00+00:00"\n    }\n}')],
          errors=[dict(re=r'^aws iam create-group --group-name (?!Admins$)\S+$', out='Created — but the lab asks for the name Admins. Names are case-sensitive; use exactly Admins.')],
          console=dict(crumbs='IAM › User groups › Create user group', fields=[dict(label='User group name', key='grp', re=r'^Admins$', ph='Admins', why='The lab asks for exactly: Admins')], button='Create user group', out='User group Admins created.'),
          lights=['iam', 'grp'], explain='IAM stored a new group with a unique ID and ARN. A group has no permissions yet — it is just a container for users.'),
     dict(title='Attach AdministratorAccess', goal='Attach the AWS managed policy <code>AdministratorAccess</code> to <code>Admins</code>.', hint='Policy ARN: <code>arn:aws:iam::aws:policy/AdministratorAccess</code>.', answer='aws iam attach-group-policy --group-name Admins --policy-arn arn:aws:iam::aws:policy/AdministratorAccess',
          cli=[dict(re=r'^aws iam attach-group-policy --group-name Admins --policy-arn arn:aws:iam::aws:policy/AdministratorAccess$', out='')],
          errors=[dict(re=r'^aws iam attach-group-policy .*arn:aws:iam::\d{12}:policy/AdministratorAccess', out='An error occurred (NoSuchEntity) when calling the AttachGroupPolicy operation: Policy arn:aws:iam::{acct}:policy/AdministratorAccess does not exist or is not attachable.\n→ AWS managed policies use the account “aws”, not your account number.')],
          console=dict(crumbs='IAM › User groups › Admins › Permissions › Attach policies', fields=[dict(label='Permissions policy', type='select', options=['ReadOnlyAccess', 'AdministratorAccess', 'PowerUserAccess', 'AmazonS3FullAccess'], re=r'^AdministratorAccess$', why='This group needs full admin rights: choose AdministratorAccess.')], button='Attach policies', out='Policy AdministratorAccess attached to Admins.'),
          lights=['pol', 'attach'], explain='The group now points to a JSON policy that allows <code>"Action": "*"</code> on <code>"Resource": "*"</code>. Every member inherits it — permissions are managed once, on the group.'),
     dict(title='Create riya-admin and add to Admins', goal='Create user <code>riya-admin</code> and add it to <code>Admins</code>.', hint='Two commands: <code>aws iam create-user --user-name riya-admin</code>, then <code>aws iam add-user-to-group ...</code>. In the simulator, the add-to-group command completes the step.', answer='aws iam add-user-to-group --group-name Admins --user-name riya-admin',
          cli=[dict(re=r'^aws iam add-user-to-group --group-name Admins --user-name riya-admin$', out='')],
          errors=[dict(re=r'^aws iam create-user --user-name riya-admin$', out='{\n    "User": {\n        "UserName": "riya-admin",\n        "Arn": "arn:aws:iam::{acct}:user/riya-admin"\n    }\n}\n(User created. Now add it to the Admins group.)', ok=True)],
          console=dict(crumbs='IAM › Users › Create user', fields=[dict(label='User name', key='user', re=r'^riya-admin$', ph='riya-admin', why='Use exactly riya-admin.'), dict(label='Provide user access to the AWS Management Console', type='check', must=True, why='Tick console access — riya-admin signs in to the console.'), dict(label='Add user to group', type='select', options=['Admins'], re=r'^Admins$', why='Add the user to Admins.')], button='Create user', out='User riya-admin created and added to Admins. Sign-in URL: https://{acct}.signin.aws.amazon.com/console'),
          lights=['user', 'member'], explain='The user has no permissions of its own; it inherits AdministratorAccess through the group. Next: sign out of root, sign in as riya-admin and add MFA for this user too.'),
     dict(title='Budget with e-mail alerts', goal='Create a monthly cost budget of <b>$5</b> named <code>monthly-5usd</code> with an e-mail alert at 80%.', hint='Console: Budgets → Create budget → Monthly cost budget. CLI: <code>aws budgets create-budget --account-id {acct} --budget ... --notifications-with-subscribers ...</code>', answer='aws budgets create-budget --account-id {acct} --budget file://budget.json --notifications-with-subscribers file://alerts.json',
          cli=[dict(re=r'^aws budgets create-budget --account-id {acct} --budget .*monthly-5usd.*--notifications-with-subscribers .+$', out=''), dict(re=r'^aws budgets create-budget --account-id {acct} --budget file://\S+ --notifications-with-subscribers file://\S+$', out='')],
          errors=[dict(re=r'^aws budgets create-budget --account-id (?!{acct})\d+', out='An error occurred (AccessDeniedException) when calling the CreateBudget operation: account mismatch.\n→ Use your own account ID: {acct}'), dict(re=r'^aws budgets create-budget --account-id {acct} --budget \S+$', out='Budget created — but with no alert nobody is told. Add --notifications-with-subscribers.')],
          console=dict(crumbs='Billing and Cost Management › Budgets › Create budget', fields=[dict(label='Budget name', key='bname', re=r'^monthly-5usd$', ph='monthly-5usd', why='Name it monthly-5usd.'), dict(label='Budgeted amount ($)', re=r'^\$?5(\.00?)?$', ph='5.00', why='Enter 5.'), dict(label='E-mail recipients', key='mail', re=r'^\S+@\S+\.\S+$', ph='you@example.com', why='Enter a valid e-mail address.')], button='Create budget', out='Budget monthly-5usd created. Alert at 80% → {mail}'),
          lights=['budget', 'alert', 'notify'], explain='AWS Budgets checks your spend several times a day. When actual cost crosses $4 (80%) or the forecast crosses $5, it e-mails you — an early warning, not a hard stop.'),
    ]))

prac = practical(AWS_INTRO + ' In this lab you create the safe foundation for the whole course: root locked, an admin user, budgets. Cost: free.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup='Keep the admin user and budgets — every later lesson uses them. If you created any access keys while experimenting, delete them: <code>aws iam list-access-keys --user-name riya-admin</code> then <code>aws iam delete-access-key --user-name riya-admin --access-key-id KEY_ID</code>. Sign out of root and store its MFA device safely.')

mist = mistakes([
    ['Creating root access keys.', 'Quick CLI access.', 'Use CloudShell or an admin user; delete root keys.'],
    ['No MFA on root.', 'Skipped during sign-up.', 'Enable MFA first, before anything else.'],
    ['Using a personal e-mail you may lose.', 'Convenience.', 'Use a long-lived address; companies use an alias.'],
    ['No budget alert.', '“Free Tier is free.”', 'Zero-spend + monthly budget on day one.'],
    ['Following 12-month tutorials on a new account.', 'Old blogs.', 'Check your plan in Billing.'],
    ['Committing keys to Git.', 'Config files in repos.', 'Never store keys in code; use roles and git-secrets scanners.']])

cert = table(['Exam / syllabus', 'What is asked from this lesson'], [['AWS CLF-C02', 'Root user tasks and protection; IAM users vs root; Free Tier offer types; Budgets and billing tools (Domains 2 and 4).'], ['C-DAC PGCP-BDA', 'Lab account setup and cost control.'], ['Interviews', '“How do you secure a new AWS account?”']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Which task requires the root user?', ['launching EC2', 'closing the AWS account', 'creating an S3 bucket', 'reading CloudWatch metrics'], 1, 'Account closure is root-only.') + \
    qx('Best practice for the root user?', ['use it daily', 'enable MFA and do not create access keys', 'share it with the team', 'store keys in code'], 1, 'Lock it away.') + \
    qx('Which tool alerts you when costs exceed a threshold?', ['AWS Budgets', 'CloudTrail', 'Inspector', 'Shield'], 0, 'Budgets.')

proj = miniproject('Mini project: a safe-account checklist for your class',
    'Write and test a one-page checklist students follow on day one.',
    ['<b>Steps:</b> sign-up, plan choice, root MFA, admin user, budgets, sign-out of root.',
     '<b>Proof:</b> for each step, the command or screen that proves it (from this lab).',
     '<b>Test:</b> ask a friend to follow it on a new account and time it.',
     '<b>Leaks:</b> add “what to do if a key leaks”: deactivate, check CloudTrail, delete resources, contact AWS Support.',
     '<b>Share:</b> keep it in your course notes.'],
    'A tested one-page checklist that takes under 20 minutes.', 'This lesson and Lesson 1.1.')

from deep_v3 import HOOD, PRO, PROJ, ROLES, DOMAINS, NEWBIE, LADDER
assemble_v2(HERE, story_h2='Root keys on GitHub and a $1,200 Monday', hook_html=hk,
    narration='Kabir and Riya opened AWS accounts on the same Friday. Kabir created root access keys and pushed them to GitHub; bots found them and launched GPU servers. Riya locked root, made an admin user and set a budget. Her account cost nothing.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Creating an AWS account and free tier',
    formal='An <b>AWS account</b> is the container that holds AWS resources and is the unit of billing and isolation; it is created with a <b>root user</b> that has unrestricted access. The <b>AWS Free Tier</b> lets new customers explore services at no or low cost through a Free or Paid account plan with credits, always-free monthly offers and short-term trials (accounts created before 15 July 2025 use the earlier 12-month model).',
    simple='Open an account, protect the all-powerful root login, do your work as a separate admin user, and set a budget so learning stays free.',
    interview=['“On a new account I enable root MFA, never create root keys, create admin access through Identity Center or an IAM user with MFA, and set budget alerts before building anything.”', '“New AWS accounts choose a Free plan — credits for six months with no charges — or a Paid plan with all services; always-free offers apply to both.”'],
    terms_rows=[('Account ID', '12-digit number identifying the account.'), ('Root user', 'Sign-up identity with full access.'), ('MFA', 'Second factor at sign-in.'), ('Access key', 'Long-term CLI/SDK credential.'), ('IAM user', 'Identity inside the account.'), ('Free plan', 'No-charge plan for 6 months or credits.'), ('Credits', 'Money-value applied to usage.'), ('Budget', 'Spending threshold with alerts.')],
    exam='CLF-C02 asks which tasks need root, how to protect root, Free Tier offer types and which tool alerts on costs (Budgets).',
    picture_h2='From sign-up to a safe account', picture_html=NEWBIE + picture,
    after_picture=[('types', 'Types, one by one', 'Seven ways to start on AWS, one by one', TYPES)],
    how_h2='How a leaked key becomes a big bill', how_intro='Kabir’s weekend, step by step.', how_anim=SOLVE,
    parts_h2='Six parts of a new account', parts_html=parts, lv='',
    myth_rows=[('The Free Tier means nothing can ever cost money.', 'Paid plans and legacy accounts can be charged above limits.', 'Types 2 and 6.'), ('Root is fine for learning.', 'Root leaks are the worst case.', 'Story.'), ('Deleting a leaked key from GitHub fixes it.', 'History and copies remain — deactivate the key.', 'Animation.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Root-only tasks, root keys, IAM user vs Identity Center, sign-up checklist', DEEP), ('hood', 'Under the hood', 'Sign-in doors, MFA codes, credential types, billing pipeline, account closure', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use it', ROLES), ('domains', 'By domain', 'Banking, healthcare, retail, education, IoT, media, government', DOMAINS), ('pro', 'For working professionals', 'Multi-account setups, hardening, forgotten-lab costs, errors, cheat sheet', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>No AWS account yet, or want a dry run first? Do the same lab in this simulator — Console or CloudShell, your choice.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Create an AWS account and choose a plan.', 'Lock the root user with MFA and no keys.', 'Create an admin user for daily work.', 'Set budgets and read your plan and credits.', 'Explain the Free Tier offer types.'],
    next_html='<a href="../03-aws-global-infrastructure/">1.3 AWS global infrastructure</a>.',
    pre='<b>Before you start:</b> Lesson 1.1, an e-mail address, a phone and a debit/credit card for verification.')
