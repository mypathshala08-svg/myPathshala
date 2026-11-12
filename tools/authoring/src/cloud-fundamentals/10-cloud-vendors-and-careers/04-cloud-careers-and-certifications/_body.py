import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)


hk = hook('Riya finished this course. She has three certificates to choose from, seven job titles to read about, and one question: “What do I do on Monday morning to get a cloud job?”',
    'Pick a <b>role</b>, not a random certificate. This lesson explains seven cloud roles one by one — <b>cloud support/administrator</b>, <b>cloud/DevOps engineer</b>, <b>solutions architect</b>, <b>cloud security engineer</b>, <b>data engineer</b>, <b>ML/AI engineer</b> and <b>FinOps practitioner</b> — with the skills and certifications for each on AWS, Azure and Google Cloud (2026 names), animates a realistic learning journey, and on <b>your own</b> account you publish a portfolio site on all three clouds and set up a free-tier tracker so practice never costs money.',
    ['Certificates open interviews; projects pass them.', 'Which exam codes changed in 2026 — and why to check official pages.', 'The portfolio piece most hiring managers ask about.'])

def story_scene():
    o = t(180, 12, 'From course to first cloud job', 9, 'ink', bold=True)
    S = [('Fundamentals', 'cert + basics', 'blue'), ('Hands-on', 'labs, projects', 'amber'), ('Associate', 'role cert', 'violet'), ('Job', 'portfolio wins', 'green')]
    for i, (a, b, tn) in enumerate(S):
        x = 8 + i * 88
        o += box(x, 32, 80, 54, tn, rx=8) + t(x + 40, 54, a, 7.8, 'ink', bold=True) + t(x + 40, 70, b, 6.8, 'ink2')
        if i < 3: o += arrow(x + 80, 59, x + 88, 59)
    o += t(180, 108, 'Projects carry more weight than certificate count', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Four steps: fundamentals certificate, hands-on labs and projects, associate role certificate, job — with projects carrying more weight than certificate count.', story_scene(), 'Choose a <tspan font-weight="700" class="s-acc">role</tspan>, then the certificate that matches it.', h=120)
dialogue = '''R> Sir, should I do AWS, Azure and Google fundamentals, all three?
A> One fundamentals exam is enough to prove the basics. Then pick a role: do you enjoy building pipelines, designing systems, securing things, or working with data?
R> Data. I liked the BigQuery and Spark parts.
A> Then a data-engineer path: SQL and Python, one cloud’s data certification, and two real pipeline projects on GitHub.
K> And the interview?
A> They will ask you to explain a project you built and a mistake you fixed. Certificates get you the call; projects get you the job.'''

def rolefig():
    o = t(320, 16, 'Seven cloud roles and how they connect', 11, 'ink', bold=True)
    R = [('Support / admin', 160, 50, 'blue'), ('Cloud / DevOps engineer', 320, 50, 'amber'), ('Solutions architect', 480, 50, 'violet'), ('Security engineer', 160, 140, 'red'), ('Data engineer', 320, 140, 'green'), ('ML / AI engineer', 480, 140, 'green'), ('FinOps', 320, 200, 'card')]
    for a, x, y, tn in R:
        o += box(x - 72, y - 16, 144, 32, tn, rx=8) + t(x, y + 4, a, 8, 'ink', bold=True)
    o += arrow(232, 50, 248, 50) + arrow(392, 50, 408, 50) + arrow(320, 66, 320, 124) + arrow(392, 140, 408, 140) + arrow(248, 66, 200, 124)
    o += t(320, 236, 'A common path: support/admin → engineer → architect; data and ML branch from engineering.', 7.4, 'ink2')
    return o
ROLES = bigfig('Seven roles: support/admin leads to cloud/DevOps engineer, then solutions architect; security engineer, data engineer and ML/AI engineer branch from engineering; FinOps sits alongside.', rolefig(), h=246)

picture = ('  <p>The roles connect — most people move between them during a career:</p>\n' + ROLES +
           '\n  <h3>Certification levels on each cloud (2026)</h3>\n' + table(['Level', 'AWS', 'Microsoft Azure', 'Google Cloud'], [
               ['Fundamentals', 'Cloud Practitioner (CLF-C02), AI Practitioner', 'AZ-900, AI-901 (replaces AI-900), DP-900, SC-900', 'Cloud Digital Leader, Generative AI Leader'],
               ['Associate', 'Solutions Architect, Developer, CloudOps Engineer, Data Engineer, Machine Learning Engineer', 'AZ-104 Administrator, AI-200 (replaces AZ-204), DP-700, AI-103, SC-500 (replaces AZ-500)', 'Associate Cloud Engineer, Associate Data Practitioner'],
               ['Professional / Expert', 'Solutions Architect – Professional, DevOps Engineer – Professional, Generative AI Developer – Professional', 'AZ-305 Solutions Architect Expert, AZ-400 DevOps Engineer Expert', 'Cloud Architect, Data Engineer, DevOps Engineer, Security Engineer, ML Engineer and more'],
               ['Specialty', 'Security – Specialty; Advanced Networking – Specialty (retires 31 Dec 2026)', 'specialty exams (e.g. networking AZ-700)', '—']], minw=680) +
           '\n  <p><b>Exam names and codes change often</b> (Microsoft retired several exams in 2026; AWS retired the Machine Learning – Specialty). Always confirm on the official certification pages before you book.</p>')

RN = {'base': (4, 54, 50, 50, 'user', 'Learner', 'Linux, networks'), 'fund': (66, 4, 62, 46, 'meter', 'Fundamentals', 'one cloud'), 'lab': (66, 104, 62, 46, 'server', 'Hands-on', 'labs, free tier'),
      'assoc': (142, 54, 60, 50, 'shield', 'Associate', 'role cert'), 'proj': (216, 4, 62, 46, 'app', 'Projects', 'GitHub, blog'), 'int': (216, 104, 62, 46, 'phone', 'Interviews', 'explain + debug'), 'job': (292, 54, 64, 50, 'chart', 'First role', 'keep learning')}
RS = [dict(on=['base'], hot='base', move=None, head='Step 1 · Foundations that never expire', text='Linux commands, networking (IP, DNS, HTTP), one programming language (Python),', text2='SQL and Git. Every cloud role uses them.', svc='The Linux, networking and Python modules of this site'),
      dict(on=['base', 'fund'], hot='fund', move=(54, 79, 72, 30, 'exam'), head='Step 2 · One fundamentals certificate', text='Pick the cloud most used by employers you target: Cloud Practitioner, AZ-900 or', text2='Cloud Digital Leader. This course covers all three syllabi.', svc='2–4 weeks of revision after this course'),
      dict(on=['fund', 'lab'], hot='lab', move=(97, 50, 97, 104, 'practise'), head='Step 3 · Hands-on every week', text='Do every own-account practical in this course with budgets on. Break things on', text2='purpose and fix them — that is what interviews test.', svc='Free tiers + budget alerts (practical step 2)'),
      dict(on=['lab', 'assoc'], hot='assoc', move=(128, 127, 150, 90, 'role'), head='Step 4 · An associate certificate for your role', text='Solutions Architect / CloudOps / Data Engineer (AWS), AZ-104 / DP-700 (Azure), Associate', text2='Cloud Engineer (Google) — chosen by the role you want.', svc='2–3 months alongside projects'),
      dict(on=['assoc', 'proj', 'int'], hot='proj', move=(202, 66, 226, 30, 'publish'), head='Step 5 · Two portfolio projects', text='A deployed app with CI/CD and monitoring, and a role-specific project (data pipeline,', text2='security guard-rails, cost dashboard). Code on GitHub, a short write-up for each.', svc='Practical step 1 starts your portfolio site'),
      dict(on=list(RN), hot='job', move=(278, 127, 298, 90, 'hired'), head='Step 6 · Interviews and the first role', text='Explain your projects, a failure you debugged, and a design trade-off. After joining, add', text2='a professional/specialty certificate when your work needs it.', svc='Learning never stops — services change every year')]
PATH = flow_anim('A realistic path from course to cloud job', 'What Riya can do, week by week, after this course.', 'Learning path', 'Animation: foundations; one fundamentals certificate; weekly hands-on; associate certificate for a role; two portfolio projects; interviews and first role.', RN, RS, hid='careerflow')

def mapfig():
    o = t(320, 16, 'Seven cloud roles', 11, 'ink', bold=True)
    items = [('1', 'Cloud support / admin', 'keep it running', 'blue'), ('2', 'Cloud / DevOps engineer', 'automate, build platforms', 'amber'), ('3', 'Solutions architect', 'design the whole system', 'violet'), ('4', 'Cloud security engineer', 'protect identities, data', 'red'),
             ('5', 'Data engineer', 'pipelines, warehouses', 'green'), ('6', 'ML / AI engineer', 'models in production', 'green'), ('7', 'FinOps practitioner', 'cloud cost and value', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, 'Each has a matching certification track on every major cloud.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven roles: cloud support/admin, cloud/DevOps engineer, solutions architect, cloud security engineer, data engineer, ML/AI engineer, FinOps practitioner.', mapfig(), h=222)

def role(n, name, tone, d, an, day, certs, nxt, A, use, avoid, plain, how, words, diff, where, rw, pro):
    return vt(n, name, tone, d, an, day, certs, nxt, A, use, avoid, plain, how, words, diff, where, rw, pro)

A1 = mk(['Tickets + alerts', 'Fix + document', 'Automate repeats'], ['tickets|access, errors|alarms', 'fix|runbooks|patch, restore', 'automate|scripts|move to engineer'], ['blue', 'amber', 'green'],
        ['handle user requests and monitoring alerts', 'fix issues using runbooks; patch, back up, restore', 'automate repeated tasks — the step into engineering'],
        [('Respond', 'User requests and alerts.', ''), ('Fix', 'Runbooks, patching, backups, restores.', ''), ('Automate', 'Scripts for repeated tasks.', '')],
        'Support / admin day', 'Keep it running.', 'Support/admin', 'Animation: tickets and alerts; fix and document; automate repeats.', 'j1anim')
T1 = role(1, 'Cloud support engineer / cloud administrator', 'blue',
    'A <b>cloud support engineer or administrator</b> operates cloud environments day to day: managing identities and access, monitoring and responding to alerts, patching, backups and restores, cost hygiene and user requests, following runbooks and gradually automating routine work.',
    'The facilities manager of an office building: lights, access cards, repairs and safety checks — every day.',
    'At TiffinGo, Kabir started as cloud admin: MFA for new staff, fixing a failed backup, answering “why is my VM slow?”, and writing his first CLI script to clean old snapshots.',
    'AWS CloudOps Engineer – Associate; Azure Administrator (AZ-104); Google Associate Cloud Engineer.', 'Module 8 (operations) is the core of this role.', A1,
    'you like troubleshooting and keeping systems healthy — a common first cloud job.',
    'you stop at clicking in consoles — learn CLI and scripting to grow.',
    'The person who keeps cloud systems running every day — users, alerts, backups and fixes.',
    [('Skills', 'Linux/Windows, networking, IAM.'), ('Tools', 'Console, CLI, monitoring.'), ('Daily', 'Tickets, alerts, patching.'), ('Growth', 'Scripting, IaC.'), ('Next role', 'Cloud/DevOps engineer.')],
    [('runbook', 'step-by-step fix instructions'), ('ticket', 'tracked request or issue'), ('on-call', 'rota for responding out of hours')],
    table(['', 'Admin', 'DevOps engineer'], [['Focus', 'operate', 'automate + build'], ['Main tools', 'console, CLI, monitoring', 'IaC, CI/CD, scripting'], ['Typical entry', 'yes', 'after 1–2 years or strong projects']], minw=420),
    ['Every cloud-using company', 'Managed service providers', 'IT departments'],
    'Managed service providers and support teams hire many entry-level cloud admins — a practical first step for freshers in India.',
    'Write down every fix as a runbook; turning runbooks into scripts is the fastest promotion path.')

A2 = mk(['Write IaC', 'Build pipelines', 'Run platforms'], ['IaC|Terraform, Bicep|CloudFormation', 'CI/CD|GitHub Actions|CodePipeline, Cloud Build', 'platform|Kubernetes|observability'], ['amber', 'blue', 'green'],
        ['define infrastructure as code', 'build CI/CD pipelines and deployment strategies', 'run platforms (Kubernetes, serverless) with observability'],
        [('IaC', 'Terraform/Bicep/CloudFormation.', ''), ('CI/CD', 'Pipelines and safe releases.', ''), ('Platform', 'Kubernetes/serverless + observability.', '')],
        'Cloud/DevOps engineer day', 'Automate everything.', 'DevOps', 'Animation: write IaC; build pipelines; run platforms.', 'j2anim')
T2 = role(2, 'Cloud engineer / DevOps or platform engineer', 'amber',
    'A <b>cloud or DevOps/platform engineer</b> builds and automates cloud infrastructure and delivery: infrastructure as code, CI/CD pipelines, container platforms, observability, reliability practices and internal developer platforms that let application teams ship safely.',
    'The engineer who designs the factory’s assembly line, so every product is built the same way, quickly and safely.',
    'TiffinGo’s platform engineer built the pipeline from Lesson 8.3, the canary releases from 8.2 and the alarms from 8.1 — and maintains the EKS cluster.',
    'AWS DevOps Engineer – Professional (after an associate); Azure DevOps Engineer Expert (AZ-400, with AZ-104 or AI-200); Google Professional Cloud DevOps Engineer; CNCF Kubernetes (CKA/CKAD); Terraform Associate.', 'Lessons 8.2–8.3 cover the core.', A2,
    'you enjoy automation, scripting and building tools for other engineers.',
    'you collect tools without understanding fundamentals (Linux, networking).',
    'An engineer who automates how cloud systems are built, tested and released.',
    [('Skills', 'Linux, Git, Python/Bash, networking.'), ('IaC', 'Terraform/Bicep/CloudFormation.'), ('Pipelines', 'GitHub Actions, CodePipeline.'), ('Platforms', 'Kubernetes, serverless.'), ('Reliability', 'SLOs, on-call.')],
    [('platform engineering', 'building internal tools/platforms for developers'), ('SRE', 'site reliability engineering'), ('CKA', 'Certified Kubernetes Administrator')],
    table(['', 'DevOps engineer', 'Solutions architect'], [['Output', 'working automation', 'designs and decisions'], ['Hands-on time', 'most of the day', 'less, more meetings'], ['Typical experience', '1–5 years', '5+ years']], minw=420),
    ['Product companies', 'Start-ups', 'Platform teams in enterprises'],
    'DevOps/platform roles are among the most frequently advertised cloud jobs because every product team needs pipelines and reliable platforms.',
    'Show a pipeline in your portfolio: tests, deploy, canary and rollback — exactly what interviews ask you to explain.')

A3 = mk(['Understand needs', 'Design options', 'Decide + guide'], ['needs|business, rules|constraints', 'design|trade-offs|cost, risk', 'decide|ADRs|guide teams'], ['violet', 'amber', 'green'],
        ['understand business needs, constraints and non-functional requirements', 'design options and compare trade-offs (cost, reliability, security)', 'decide, document (ADRs) and guide teams through delivery'],
        [('Understand', 'Business needs, rules, non-functional requirements.', ''), ('Design', 'Options with trade-offs.', ''), ('Decide', 'ADRs, reviews, guiding teams.', '')],
        'Solutions architect day', 'Design the whole system.', 'Architect', 'Animation: understand needs; design options; decide and guide.', 'j3anim')
T3 = role(3, 'Solutions architect', 'violet',
    'A <b>solutions architect</b> designs cloud solutions that meet business and technical requirements — choosing services, deployment and service models, security, reliability and cost trade-offs — documents decisions, reviews designs against well-architected frameworks and guides teams and customers through implementation.',
    'The architect of a housing project: understands the families’ needs, the land rules and budget, then draws a plan builders can follow.',
    'The four scenario briefs in Lesson 10.3 are architect work: constraints first, then models, providers, governance and an ADR.',
    'AWS Solutions Architect – Associate then – Professional; Azure Solutions Architect Expert (AZ-305 with AZ-104); Google Professional Cloud Architect.', 'Modules 7 and 10 are architect material.', A3,
    'you like seeing the big picture, talking to people and making trade-offs.',
    'you jump to architecture without hands-on experience — credibility comes from having built things.',
    'The person who designs the overall cloud system so it meets business needs safely and at the right cost.',
    [('Requirements', 'Functional + non-functional.'), ('Options', 'Compare 2–3 designs.'), ('Review', 'Well-Architected.'), ('Document', 'Diagrams + ADRs.'), ('Guide', 'Delivery support.')],
    [('non-functional requirement', 'quality needs: performance, security, availability'), ('pre-sales architect', 'architect who helps customers before purchase'), ('reference architecture', 'reusable proven design')],
    table(['', 'Solutions architect', 'Enterprise architect'], [['Scope', 'one solution', 'whole organisation'], ['Depth', 'technical', 'strategic'], ['Cloud certs', 'very relevant', 'helpful']], minw=420),
    ['Consultancies', 'Cloud providers and partners', 'Enterprises'],
    'The AWS Solutions Architect – Associate is consistently among the most popular cloud certifications worldwide.',
    'Practise drawing a design in 10 minutes and defending one trade-off — that is the core of architect interviews.')

A4 = mk(['Identity + guard-rails', 'Detect + respond', 'Comply + improve'], ['identity|IAM, SSO|policies', 'detect|GuardDuty, SIEM|runbooks', 'comply|audits|posture'], ['red', 'amber', 'green'],
        ['design identities, least privilege and organisation guard-rails', 'detect threats and respond to incidents', 'support audits and improve security posture'],
        [('Prevent', 'IAM, SSO, guard-rails, encryption.', ''), ('Detect', 'Threat detection, SIEM, runbooks.', ''), ('Comply', 'Audits, posture, improvements.', '')],
        'Cloud security engineer day', 'Protect, detect, prove.', 'Security', 'Animation: identity and guard-rails; detect and respond; comply and improve.', 'j4anim')
T4 = role(4, 'Cloud security engineer', 'red',
    'A <b>cloud security engineer</b> protects cloud environments by designing identity and access, guard-rails, encryption and network controls, deploying threat detection and posture management, responding to incidents and supporting compliance audits, increasingly by writing security as code.',
    'The security head of a large mall: designs access cards and cameras, watches alarms and runs drills.',
    'Module 9’s labs — public-access blocks, GuardDuty, credential hunting, KMS keys — are a cloud security engineer’s first week at TiffinGo.',
    'AWS Security – Specialty; Microsoft SC-500 (replaces AZ-500 in 2026), SC-900 for basics; Google Professional Cloud Security Engineer; vendor-neutral CCSK, CCSP, Security+.', 'Module 9 is the core.', A4,
    'you enjoy finding weaknesses and building protections.',
    'you skip fundamentals (networking, identity, Linux) — security needs them most.',
    'An engineer who keeps cloud accounts, data and users safe from attacks and mistakes.',
    [('Identity', 'SSO, least privilege.'), ('Guard-rails', 'SCPs, policies.'), ('Detection', 'GuardDuty, Defender, SCC, SIEM.'), ('Response', 'Runbooks, forensics.'), ('Compliance', 'Evidence, audits.')],
    [('SIEM', 'security information and event management'), ('CSPM', 'cloud security posture management'), ('security as code', 'security controls written in IaC/policy')],
    table(['', 'Cloud security', 'Traditional network security'], [['Perimeter', 'identity', 'firewall'], ['Tools', 'APIs, policies, CSPM', 'appliances'], ['Skills', 'IAM, IaC, scripting', 'network devices']], minw=420),
    ['Banks and fintech', 'Security consultancies', 'Any regulated company'],
    'Demand for cloud security skills is high in India’s BFSI sector because of RBI, CERT-In and DPDP requirements (Lesson 9.3).',
    'A portfolio of guard-rail code (SCPs, Azure Policy, org policies, Terraform checks) impresses more than a list of tools.')

A5 = mk(['Ingest', 'Transform', 'Serve'], ['ingest|batch, streams|Kafka, DMS', 'transform|Spark, SQL|dbt, Glue', 'serve|warehouse, lake|BI, ML'], ['green', 'blue', 'amber'],
        ['ingest data from apps, databases and streams', 'transform it with Spark and SQL into clean models', 'serve it in warehouses and lakes for BI and ML'],
        [('Ingest', 'Batch and streaming sources.', ''), ('Transform', 'Spark/SQL pipelines, quality checks.', ''), ('Serve', 'Warehouse/lakehouse for BI and ML.', '')],
        'Data engineer day', 'Pipelines all day.', 'Data engineer', 'Animation: ingest; transform; serve.', 'j5anim')
T5 = role(5, 'Data engineer', 'green',
    'A <b>data engineer</b> builds and operates pipelines that ingest, transform and serve data — batch and streaming — into data lakes, warehouses and lakehouses on the cloud, ensuring quality, governance, cost efficiency and reliability for analytics and machine learning.',
    'The water-supply engineer of a city: collects water from many sources, cleans it, and delivers it reliably to every tap.',
    'TiffinGo’s data engineer moves order data from RDS to BigQuery nightly, streams rider locations through Kafka, and runs Spark jobs for demand forecasting — exactly the C-DAC PGCP-BDA toolset.',
    'AWS Data Engineer – Associate; Microsoft Fabric Data Engineer (DP-700); Google Professional Data Engineer, Associate Data Practitioner; Databricks and Snowflake certifications.', 'The Big Data track (Hadoop, Spark, Hive, Kafka) on this site plus Lesson 10.2.', A5,
    'you like SQL, Python and making data reliable.',
    'you learn only tools without data modelling and SQL depth.',
    'An engineer who builds the pipes that move and clean data so others can analyse it.',
    [('SQL + Python', 'Core languages.'), ('Ingest', 'CDC, streams, files.'), ('Process', 'Spark, SQL, dbt.'), ('Store', 'Lake, warehouse, lakehouse.'), ('Govern', 'Quality, catalogues, cost.')],
    [('lakehouse', 'combination of data lake and warehouse'), ('CDC', 'change data capture'), ('dbt', 'tool for SQL transformations')],
    table(['', 'Data engineer', 'Data analyst'], [['Builds', 'pipelines, models', 'reports, insights'], ['Main tools', 'Spark, SQL, Python, cloud', 'SQL, BI tools'], ['Cloud depth', 'high', 'medium']], minw=420),
    ['E-commerce and delivery', 'Banking analytics', 'Telecom'],
    'Microsoft retired the older Azure Data Engineer exam (DP-203) in 2025; DP-700 (Fabric Data Engineer) is the current Microsoft path — another reason to check exam pages before studying.',
    'Big Data course graduates already have Spark, Hive and Kafka — add one cloud’s data certification and a deployed pipeline project.')

A6 = mk(['Data + model', 'Deploy + monitor', 'GenAI apps'], ['model|train, evaluate|features', 'MLOps|endpoints|drift monitoring', 'GenAI|RAG, agents|guardrails'], ['green', 'blue', 'violet'],
        ['prepare data, train and evaluate models', 'deploy them and monitor quality and drift (MLOps)', 'build generative-AI applications with retrieval and guardrails'],
        [('Model', 'Data prep, training, evaluation.', ''), ('MLOps', 'Deployment, monitoring, retraining.', ''), ('GenAI', 'RAG, agents, safety guardrails.', '')],
        'ML/AI engineer day', 'Models in production.', 'ML/AI', 'Animation: data and model; deploy and monitor; generative-AI applications.', 'j6anim')
T6 = role(6, 'ML / AI engineer', 'green',
    'An <b>ML or AI engineer</b> takes machine-learning and generative-AI models into production on the cloud: preparing data, training or fine-tuning, deploying endpoints, building retrieval-augmented and agentic applications, and monitoring quality, cost and safety (MLOps/LLMOps).',
    'A chef who not only creates a new recipe but also sets up the kitchen so it can be cooked the same way every day for thousands of customers.',
    'TiffinGo’s ML engineer deploys the demand-forecast model (Vertex AI) and a menu-assistant chatbot using a managed foundation model with retrieval over the menu database.',
    'AWS AI Practitioner, Machine Learning Engineer – Associate, Generative AI Developer – Professional; Azure AI-901, AI-103 (replaces AI-102), AI-300 (replaces DP-100); Google Professional Machine Learning Engineer, Generative AI Leader.', '', A6,
    'you enjoy maths, data and building intelligent features.',
    'you skip engineering basics — most ML work is data and deployment, not modelling.',
    'An engineer who puts AI models into real apps on the cloud and keeps them working well.',
    [('Data', 'Features, labelling.'), ('Train', 'Or use foundation models.'), ('Deploy', 'Endpoints, batch.'), ('GenAI', 'RAG, agents, evaluation.'), ('Monitor', 'Drift, cost, safety.')],
    [('MLOps', 'operations practices for ML'), ('RAG', 'retrieval-augmented generation'), ('drift', 'model accuracy falling as data changes')],
    table(['', 'ML engineer', 'Data scientist'], [['Focus', 'production systems', 'analysis and modelling'], ['Cloud depth', 'high', 'medium'], ['Key skill', 'engineering + ML', 'statistics + ML']], minw=420),
    ['AI product companies', 'Banks (fraud)', 'Retail (recommendations)'],
    'AWS retired the Machine Learning – Specialty certification and added associate and professional AI credentials, reflecting the shift to generative-AI engineering.',
    'Show an end-to-end GenAI project with evaluation and cost numbers — rare in student portfolios, valued in interviews.')

A7 = mk(['See costs', 'Optimise', 'Plan value'], ['visibility|tags, reports|showback', 'optimise|rightsize, commit|waste', 'value|unit cost|forecast'], ['card', 'amber', 'green'],
        ['make cloud costs visible per team, product and customer', 'remove waste and buy commitments wisely', 'connect spend to business value and forecast it'],
        [('Inform', 'Allocation, showback, dashboards.', ''), ('Optimise', 'Right-size, schedule, commit, remove waste.', ''), ('Operate', 'Unit economics, forecasts, policies.', '')],
        'FinOps day', 'Spend well, not just less.', 'FinOps', 'Animation: see costs; optimise; plan value.', 'j7anim')
T7 = role(7, 'FinOps practitioner / cloud cost analyst', 'card',
    'A <b>FinOps practitioner</b> brings finance, engineering and business together to manage cloud spend: making costs visible and allocated, optimising usage and pricing (right-sizing, commitments, waste removal), forecasting, and tracking unit economics so cloud spending delivers business value.',
    'A household budget planner who knows exactly which family member spends on what, cancels unused subscriptions and plans the next year’s expenses.',
    'TiffinGo’s first FinOps review found idle dev databases, unattached disks and no Savings Plans; cost per order fell by a third.',
    'FinOps Certified Practitioner (FinOps Foundation); provider cost tools: Cost Explorer, Cost Management, Billing reports; FOCUS billing data standard.', 'Pricing is Lesson 5.5; tagging in 10.3.', A7,
    'you like numbers, business and engineering together.',
    'you treat FinOps as “cut costs” only — the goal is value per rupee.',
    'Someone who helps companies understand and control what they spend on the cloud.',
    [('Allocate', 'Tags, accounts, showback.'), ('Analyse', 'Trends, anomalies.'), ('Optimise', 'Rightsize, commit, schedule.'), ('Forecast', 'Budgets.'), ('Unit metrics', 'Cost per order/user.')],
    [('unit economics', 'cost per business unit, e.g. per order'), ('commitment', 'Savings Plan/reservation/CUD'), ('FOCUS', 'open standard for cloud billing data')],
    table(['', 'FinOps', 'Traditional IT finance'], [['Cadence', 'daily/weekly', 'yearly budget'], ['Who acts', 'engineers + finance', 'finance'], ['Data', 'usage-level billing', 'invoices']], minw=420),
    ['Large cloud users', 'SaaS companies', 'Consultancies'],
    'The FinOps Foundation (part of the Linux Foundation) maintains the FinOps framework and the FOCUS standard that the major clouds now support for billing exports.',
    'Engineers who can talk cost (cost per request, commitment coverage) stand out in any cloud interview.')

SUMMARY = table(['#', 'Role', 'Core skills', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'Support / admin', 'operations, IAM, monitoring', 'CloudOps Engineer – Assoc.', 'AZ-104', 'Associate Cloud Engineer'], ['2', 'Cloud / DevOps engineer', 'IaC, CI/CD, K8s', 'DevOps Engineer – Pro', 'AZ-400', 'Prof. Cloud DevOps Engineer'],
    ['3', 'Solutions architect', 'design, trade-offs', 'Solutions Architect – Assoc./Pro', 'AZ-305', 'Prof. Cloud Architect'], ['4', 'Security engineer', 'IAM, detection, compliance', 'Security – Specialty', 'SC-500', 'Prof. Cloud Security Engineer'],
    ['5', 'Data engineer', 'SQL, Spark, pipelines', 'Data Engineer – Assoc.', 'DP-700', 'Prof. Data Engineer'], ['6', 'ML / AI engineer', 'ML, MLOps, GenAI', 'ML Engineer – Assoc., GenAI Developer – Pro', 'AI-103, AI-300', 'Prof. ML Engineer'], ['7', 'FinOps', 'cost, data, business', '(FinOps Practitioner)', '(FinOps Practitioner)', '(FinOps Practitioner)']], minw=700)
CHECK = ('  <h3>Check yourself: which role?</h3>\n' +
    qx('A. Builds CI/CD pipelines and Terraform modules all day.', ['Cloud/DevOps engineer', 'FinOps', 'Data analyst', 'Support'], 0, 'DevOps.') +
    qx('B. Writes the design and ADR for a bank’s new platform.', ['Solutions architect', 'Support', 'Data engineer', 'FinOps'], 0, 'Architect.') +
    qx('C. Moves orders data into BigQuery with Spark jobs.', ['Data engineer', 'Security engineer', 'Admin', 'Architect'], 0, 'Data.') +
    qx('D. Reports cost per order and buys Savings Plans.', ['FinOps practitioner', 'ML engineer', 'Admin', 'Security'], 0, 'FinOps.'))

TYPES = ('  <p>Seven roles, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, a day at TiffinGo and an expert note. “Products” lists the matching certifications (2026 names).</p>\n'
         + challenge(['Which role is the most common first cloud job?', 'Which Microsoft exam replaced AZ-500 in 2026?', 'What makes a data-engineer portfolio stand out?'], 'types 1, 4 and 5') + MAP
         + jump(['Support', 'DevOps', 'Architect', 'Security', 'Data', 'ML/AI', 'FinOps']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Foundations', 'Linux, networking, Python, SQL, Git.', 'Every role and interview uses them.', 'This site’s Linux and Python courses.'),
    ('One fundamentals cert', 'CLF-C02, AZ-900 or Cloud Digital Leader.', 'Proves basics; this course covers all three.', '2–4 weeks revision.'),
    ('Role certification', 'Associate/professional for your role.', 'Signals direction to employers.', 'Table above.'),
    ('Portfolio', 'Deployed projects with write-ups.', 'Interviews are about what you built.', 'GitHub + portfolio site.'),
    ('Community', 'Meetups, user groups, open source.', 'Referrals and learning.', 'AWS/Azure/GDG communities.'),
    ('Continuous learning', 'Services change yearly.', 'Stay current.', 'Release notes, re-certification.')])

DEEP = ('  <h3>Exam basics (check official pages)</h3>\n' + table(['Item', 'Typical facts'], [['Format', 'multiple choice / multiple response, some labs/case studies at higher levels'], ['Delivery', 'test centre or online proctored'], ['Validity', 'usually 2–3 years (Microsoft role-based: renew yearly free online)'], ['Fees', 'vary by level and country; foundational exams are cheapest; discounts via training events and student programmes'], ['Retirements', 'exams are replaced regularly (Microsoft 2026: AZ-204→AI-200, AI-900→AI-901, AI-102→AI-103, DP-100→AI-300, AZ-500→SC-500)']], minw=560) +
    '\n  <h3>Interview preparation checklist</h3>\n  <ul><li>Explain one project end to end (architecture, choices, problems, cost).</li><li>Answer the classics: IaaS vs PaaS vs SaaS, shared responsibility, CloudWatch vs CloudTrail, scaling vs elasticity, blue/green vs canary.</li><li>Debug live: “site not loading” → DNS, security group, health check, logs (Lessons 6.3, 8.1).</li><li>Have a story about a mistake and what you changed.</li><li>Ask questions about their cloud setup and on-call.</li></ul>\n'
    '  <h3>The Cloud Resume Challenge idea</h3>\n  <p>A well-known portfolio project (created by Forrest Brazeal): host your résumé as a static site, add a visitor counter through a serverless API and NoSQL table, define it all in IaC, deploy it with CI/CD, and write a blog post. Practical step 1 is the first stage — extend it with Lessons 8.2–8.3.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> AWS Skill Builder, AWS Academy (colleges), AWS Educate, AWS re/Start (job-focused programme), certification paths from Cloud Practitioner to Professional/Specialty.</p>',
    '<p><b>Azure:</b> Microsoft Learn (free paths and sandboxes), Azure for Students credits, Microsoft Applied Skills, role-based certifications with free yearly renewal.</p>',
    '<p><b>Google Cloud:</b> Google Cloud Skills Boost (labs, skill badges), Google Cloud Innovators, education credits, certifications from Cloud Digital Leader to Professional.</p>') + \
    cloud3([['Free learning', 'Skill Builder', 'Microsoft Learn', 'Cloud Skills Boost'], ['Student programme', 'AWS Academy / Educate', 'Azure for Students', 'education credits'], ['Fundamentals exam', 'Cloud Practitioner', 'AZ-900', 'Cloud Digital Leader'], ['Hands-on badges', 'Skill Builder labs', 'Applied Skills', 'skill badges']])

SITE = '''mkdir portfolio && cd portfolio
cat > index.html <<'EOF'
<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Riya Sharma — Cloud Portfolio</title></head>
<body style="font-family:sans-serif;max-width:720px;margin:40px auto">
<h1>Riya Sharma</h1><p>Cloud &amp; data engineering learner · C-DAC PGCP-BDA</p>
<h2>Projects</h2><ul><li>Canary release with rollback (Lambda / App Service / Cloud Run)</li>
<li>CI/CD pipeline with tests and IaC</li><li>Big Data pipeline: Kafka → Spark → warehouse</li></ul>
<h2>Certifications</h2><p>In progress: cloud fundamentals</p></body></html>
EOF'''

MOCKQ.extend([
 (mock('aws', ['AWS Amplify', 'Deploy without Git'], ['All apps', 'Create new app'], 'Create new app', [('App name', 'portfolio'), ('Method', '[x] Drag and drop (zip / folder)'), ('Branch', 'main')], 'Save and deploy'),
  mock('az', ['Storage account', 'Static website'], ['Overview', 'Data management', 'Static website'], 'Static website', [('Static website', '[x] Enabled'), ('Index document name', 'index.html'), ('Primary endpoint', 'https://NAME.z29.web.core.windows.net/')], 'Save'),
  mock('gcp', ['Cloud Storage', 'portfolio bucket', 'Website configuration'], ['Objects', 'Configuration', 'Permissions'], 'Configuration', [('Index page suffix', 'index.html'), ('Public access', 'allUsers · Storage Object Viewer')], 'Save')),
 (mock('aws', ['Billing and Cost Management', 'Free Tier'], ['Home', 'Free Tier', 'Bills'], 'Free Tier', [('Service', 'AWS Lambda · Amazon S3 · …'), ('Usage', 'current vs limit · forecast')], 'View all'),
  mock('az', ['Subscriptions', 'Free services'], ['Overview', 'Free services', 'Cost analysis'], 'Free services', [('Service', 'Linux VM B1s · Blob storage · …'), ('Usage', 'used vs 12-month limit')], 'Refresh'),
  mock('gcp', ['Billing', 'Reports'], ['Overview', 'Reports', 'Budgets & alerts'], 'Reports', [('Credits', 'Free trial · remaining'), ('Group by', 'Service')], 'Download')),
])

STEP1 = ('1 · Publish your portfolio site (on any — or all three — clouds)', tri(
    (['[[AWS Amplify]] → [[Create new app]] → [[Deploy without Git]] → name <code>portfolio</code>, branch <code>main</code> → drag the zip of your folder → [[Save and deploy]].', 'Amplify gives an HTTPS URL like <code>https://main.APPID.amplifyapp.com</code>.'],
     SITE + "\nzip -q site.zip index.html\nAPPID=$(aws amplify create-app --name portfolio --query app.appId --output text)\naws amplify create-branch --app-id $APPID --branch-name main >/dev/null\nread JOB URL < <(aws amplify create-deployment --app-id $APPID --branch-name main --query '[jobId,zipUploadUrl]' --output text)\ncurl -s -T site.zip \"$URL\"\naws amplify start-deployment --app-id $APPID --branch-name main --job-id $JOB --query jobSummary.status --output text\necho https://main.$APPID.amplifyapp.com",
     '<code>PENDING</code> then, a minute later, your page at the printed HTTPS URL. Amplify Hosting has a free allowance for small static sites.'),
    (['[[Storage account]] (Central India) → [[Static website]] → [[Enabled]], index <code>index.html</code> → [[Save]] → upload to the <code>$web</code> container.', 'The primary endpoint is an HTTPS URL ending in <code>web.core.windows.net</code>.'],
     SITE + "\naz group create -n rg-portfolio -l centralindia >/dev/null\nSA=portfolio$RANDOM; az storage account create -n $SA -g rg-portfolio -l centralindia --sku Standard_LRS --kind StorageV2 >/dev/null\nKEY=$(az storage account keys list -n $SA -g rg-portfolio --query [0].value -o tsv)\naz storage blob service-properties update --account-name $SA --account-key $KEY --static-website --index-document index.html >/dev/null\naz storage blob upload --account-name $SA --account-key $KEY -c '$web' -f index.html -n index.html --content-type text/html --only-show-errors >/dev/null\naz storage account show -n $SA -g rg-portfolio --query primaryEndpoints.web -o tsv",
     'an HTTPS URL like <code>https://portfolio12345.z29.web.core.windows.net/</code> showing your page. Cost: a few paise per month.'),
    (['[[Cloud Storage]] → [[Create]] bucket in asia-south1 → upload <code>index.html</code> → [[Permissions]] → [[Grant access]] → <code>allUsers</code> → [[Storage Object Viewer]] (this site is meant to be public) → [[Edit website configuration]] → index <code>index.html</code>.'],
     SITE + "\nB=portfolio-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1 --uniform-bucket-level-access\ngcloud storage cp index.html gs://$B/ --content-type=text/html\ngcloud storage buckets add-iam-policy-binding gs://$B --member=allUsers --role=roles/storage.objectViewer --quiet >/dev/null\ngcloud storage buckets update gs://$B --web-main-page-suffix=index.html\necho https://storage.googleapis.com/$B/index.html",
     'an HTTPS URL that shows your page. If your organisation enforces public access prevention, use a personal project or Firebase Hosting instead.')),
    'Edit the HTML with your real projects. Next steps for a stronger portfolio: custom domain, visitor counter (serverless + NoSQL), IaC and CI/CD — the Cloud Resume Challenge (deep dive).')

STEP2 = ('2 · Track free-tier usage so practice never costs money', tri(
    (['[[Billing and Cost Management]] → [[Free Tier]] shows each service’s usage against its free limit and a forecast.', 'New accounts (since July 2025) get credits and a free plan; the [[Account plan]] page shows remaining credits and days.'],
     "aws freetier get-free-tier-usage --region us-east-1 --query 'freeTierUsages[].[service,usageType,actualUsageAmount,limit]' --output table | head -15\naws freetier get-account-plan-state --region us-east-1 --query '[accountPlanType,accountPlanStatus,accountPlanRemainingCredits.amount]' --output text 2>&1 | tail -1",
     'a table of services with used vs limit, and (for free-plan accounts) your plan type, status and remaining credits.'),
    (['[[Subscriptions]] → your subscription → [[Free services]] (Azure free account) shows usage of each 12-month free service; [[Cost analysis]] shows credit burn.'],
     'az consumption usage list --top 10 --query "[].{service:consumedService,quantity:usageQuantity,cost:pretaxCost}" -o table 2>&1 | tail -12',
     'recent usage rows with quantity and cost (often 0 on free services). The Free services blade is the clearest view of 12-month limits.'),
    (['[[Billing]] → [[Overview]] shows free-trial credits remaining and days left; [[Reports]] grouped by service shows where credits go.'],
     'gcloud billing accounts list --format="table(name,displayName,open)"\ngcloud billing projects describe $(gcloud config get-value project) --format="value(billingEnabled,billingAccountName)"',
     'your billing account(s) and whether this project is linked — then check credits and reports in the console.')),
    'Combine this with the budget alert from step 0: safe practice is part of a professional habit.')

prac = practical(OWN_INTRO + ' You start your career portfolio by publishing a site, and set up free-tier tracking so your weekly practice stays free.', [SETUP_STEP, STEP1, STEP2],
    cleanup='Keep your portfolio online if you like (costs paise). To remove: <b>AWS</b> <code>aws amplify delete-app --app-id $APPID</code>; <b>Azure</b> <code>az group delete -n rg-portfolio --yes --no-wait</code>; <b>Google Cloud</b> <code>gcloud storage rm -r gs://$B</code>.')

mist = mistakes([
    ['Collecting certificates without projects.', 'Certificates feel like progress.', 'One cert per role + two deployed projects.'],
    ['Studying old exam codes.', 'Old blogs and videos.', 'Check official exam pages first.'],
    ['Learning three clouds shallowly.', 'Fear of missing out.', 'One cloud deep, mappings to others.'],
    ['Skipping Linux and networking.', 'Cloud seems to hide them.', 'They are tested in every interview.'],
    ['Practice bills.', 'Forgotten resources.', 'Budgets, free-tier tracking, clean-up.'],
    ['No write-ups.', 'Code only.', 'Short README/blog per project.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud careers and the role of certifications (course outcome).'], ['AWS CLF-C02', 'AWS learning resources and support (Skill Builder, re:Post, support plans).'], ['AZ-900', 'Microsoft Learn, support and service options.'], ['Google Cloud Digital Leader', 'Google Cloud learning and digital transformation skills.']], minw=560) + \
    qx('1. Which certification is AWS’s entry-level cloud exam?', ['Cloud Practitioner (CLF-C02)', 'Solutions Architect – Professional', 'Security – Specialty', 'DevOps Engineer – Professional'], 0, 'Foundational.') + \
    qx('2. Microsoft’s Azure fundamentals exam is…', ['AZ-900', 'AZ-305', 'AZ-104', 'DP-700'], 0, 'AZ-900.') + \
    qx('3. Google Cloud’s foundational business-level certification is…', ['Cloud Digital Leader', 'Professional Cloud Architect', 'Associate Cloud Engineer', 'Data Engineer'], 0, 'CDL.') + \
    qx('4. Which role mostly writes IaC and CI/CD pipelines?', ['DevOps/platform engineer', 'FinOps', 'Data analyst', 'Help desk'], 0, 'DevOps.') + \
    qx('5. In 2026, Microsoft’s AZ-500 security exam was replaced by…', ['SC-500', 'AZ-900', 'DP-700', 'AI-901'], 0, 'SC-500.') + \
    qx('6. Best evidence of skill in interviews?', ['number of certificates', 'deployed projects you can explain', 'tool list', 'years of watching videos'], 1, 'Projects.')

proj = miniproject('Mini project: your 90-day cloud career plan',
    'Turn this course into a job-ready plan.',
    ['<b>Role:</b> choose one of the seven roles and write why.',
     '<b>Gaps:</b> list foundations you still need (Linux, networking, Python, SQL).',
     '<b>Certificates:</b> one fundamentals + one role exam, with official exam guide links and dates.',
     '<b>Projects:</b> two portfolio projects from this course, extended (e.g. Cloud Resume Challenge).',
     '<b>Portfolio:</b> publish step 1 with your real details and link GitHub.',
     '<b>Weekly rhythm:</b> hours for study, labs, write-ups and community.'],
    'A 90-day plan, a live portfolio URL and two project READMEs.', 'Every module of this course.')

assemble_v2(HERE, story_h2='“What do I do on Monday?”', hook_html=hk,
    narration='Riya finished the cloud course. Job sites listed dozens of titles and every blog recommended a different certificate. She wanted a plan she could start the next Monday.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud careers and certifications',
    formal='<b>Cloud careers</b> span roles such as cloud support and administration, cloud/DevOps and platform engineering, solutions architecture, cloud security, data engineering, ML/AI engineering and FinOps; <b>cloud certifications</b> — offered by AWS, Microsoft, Google and vendor-neutral bodies at foundational, associate, professional and specialty levels — validate knowledge for these roles, and are most effective when combined with hands-on projects and strong fundamentals.',
    simple='Choose a cloud job role, learn the basics, earn the matching certificate, and build real projects you can show and explain.',
    interview=['“I’m targeting a data-engineer role: I have Spark, Hive and Kafka from PGCP-BDA, I’m taking the AWS Data Engineer – Associate, and my portfolio has a deployed pipeline with CI/CD and monitoring.”', '“Certifications show I know the services; my projects show I can build and debug them.”'],
    terms_rows=[('Foundational cert', 'Entry-level exam.'), ('Associate cert', 'Role-level exam.'), ('Professional / expert', 'Advanced design/operations.'), ('Specialty', 'Deep single area.'), ('Portfolio', 'Projects you can show.'), ('Platform engineering', 'Internal developer platforms.'), ('FinOps', 'Cloud financial management.'), ('Retirement', 'Exam replaced or withdrawn.')],
    exam='Fundamentals exams ask where to learn and get help (Skill Builder, Microsoft Learn, Skills Boost, support plans); role exams test the role’s tasks.',
    picture_h2='Seven roles and the certification levels', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven cloud roles, one by one', TYPES)],
    how_h2='A realistic path from course to cloud job', how_intro='What to do after this course, step by step.', how_anim=PATH,
    parts_h2='Six ingredients of a cloud career', parts_html=parts, lv='',
    myth_rows=[('More certificates = more jobs.', 'One relevant cert + projects beats many certs.', 'Story.'), ('You must learn all three clouds.', 'One deep + mappings.', 'Parts.'), ('Exam names are stable.', 'Several changed in 2026.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Exam basics, interview checklist, Cloud Resume Challenge', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Describe seven cloud roles and their daily work.', 'Map roles to current AWS, Azure and Google certifications.', 'Plan a realistic path from course to first job.', 'Publish a portfolio site and track free-tier usage on your own account.', 'Prepare for cloud interviews with projects.'],
    next_html='Module 11 — <a href="../../11-capstone-and-exam-preparation/01-capstone-design-a-cloud-solution/">11.1 Capstone: design a cloud solution</a>.',
    pre='<b>Before you start:</b> any earlier modules — this lesson ties them together.')
