import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='02-history-and-evolution-of-cloud-computing', n='1.2', module_label='Module 1 · Introduction to cloud computing',
    title='History and evolution of cloud computing',
    desc='How cloud computing evolved: mainframe time-sharing, utility computing, client-server, internet, grid computing, virtualization, Salesforce, AWS S3 and EC2 (2006), Google App Engine, Azure, serverless and AI. Real evidence from the AWS SDK: 436 services and their growth by year.',
    og_desc='From 1961’s “computing as a utility” to 436 AWS services: the history of cloud computing with real data.',
    minutes=18, level='Beginner',
    lead='The cloud’s ideas are sixty years old, but the business began in 2006. We walk through <b>six eras</b> as pictures, watch one bank’s IT change across fifty years, and see exactly how <b>virtualization</b> turned into the cloud.',
    chips=['6 eras', '436 AWS services', 'AWS · Azure · GCP dates', 'Diagrams + animations'])
MAIN = '''# Services added per year (real counts from the AWS SDK), running total
added = {2006: 1, 2009: 2, 2010: 7, 2011: 3, 2012: 9, 2013: 6, 2014: 19, 2015: 22, 2016: 22,
         2017: 50, 2018: 82, 2019: 30, 2020: 47, 2021: 33, 2022: 30, 2023: 32, 2024: 15, 2025: 19, 2026: 7}
total = 0
for year, n in added.items():
    total += n
    print(year, f"+{n:3d}", f"total {total:3d}", "#" * (n // 5))
'''
RUN = dict(heading='Run the code: the growth curve', intro='<p>Real counts from Step 2. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    total += n', 'Running total = services known so far.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: busiest year', hint='<b>Predict first:</b> which year added most?', code='added = {2017: 50, 2018: 82, 2020: 47}\nprint(max(added, key=added.get))\n'),
        dict(label='3 · Order the eras', hint='Sort by year.', code='eras = {"cloud": 2006, "mainframe": 1960, "virtualization": 1999, "internet": 1991}\nprint(sorted(eras, key=eras.get))\n'),
        dict(label='4 · Age', hint='How old is S3?', code='print(2026 - 2006, "years")\n'),
        dict(label='5 · Spot the error', hint='Wrong claim.', expect='error', code='first_public_iaas = 1999\nif first_public_iaas != 2006:\n    raise ValueError("1999 was Salesforce (SaaS) and VMware; public IaaS started with AWS S3/EC2 in 2006")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Python 3 and pip. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l12_history.py', file='terminal', output="== 1) services the AWS SDK (botocore 1.43.127) knows today: 436", note='Needs the wheel from Practical step 1.')])
TRACE = dict(heading='Running total step by step', intro='<p>Three years.</p>',
    code='total = 0\nfor n in [1, 2, 7]:\n    total += n\n    print(total)\n', notes={3: 'Add :: this year.'})
WORKED_INTRO = 'Three history questions.'
EXAMPLES = [
    dict(level='b', tag='era', title='Which era?', problem='<p>Many users share one big computer and pay for time.</p>', inp='clue', approach=['Shared big computer.', '1960s.', 'Mainframe time-sharing.'], code='print("mainframe time-sharing")\n', notes={1: 'Era 1.'}, tryit='Types table.'),
    dict(level='i', tag='enabler', title='Key enabler', problem='<p>What lets one server be rented to 10 customers safely?</p>', inp='clue', approach=['Isolation.', 'Hypervisor.', 'Virtualization.'], code='print("virtualization")\n', notes={1: 'Module 4.'}, tryit='Exam tip.'),
    dict(level='a', tag='model', title='First model per provider', problem='<p>AWS, Google, Azure started with?</p>', inp='dates', approach=['AWS S3/EC2.', 'Google App Engine.', 'Azure PaaS.'], code='print({"AWS": "IaaS", "Google": "PaaS", "Azure": "PaaS"})\n', notes={1: 'Clouds tab.'}, tryit='Clouds.')]
QUIZ = mix([{'q': 'Beginner: The modern public cloud business began with…', 'options': ['Gmail in 2004', 'AWS S3 and EC2 in 2006', 'Windows 95', 'Linux in 1991'], 'answer': 1, 'why': 'AWS launched S3 (storage, March 2006) and EC2 (VMs, August 2006): anyone could rent infrastructure by the hour. Gmail is a SaaS product, not the start of public IaaS.'}, {'q': 'Beginner: Many users sharing one big computer and paying for time is called…', 'options': ['Serverless', 'Time-sharing on mainframes', 'Edge computing', 'Containers'], 'answer': 1, 'why': '1960s–70s mainframes were shared through terminals; this is where the ideas of sharing and metering come from.'}, {'q': 'Beginner: Which company sold CRM software over the web from 1999, an early SaaS?', 'options': ['Docker', 'Salesforce', 'Kubernetes', 'VMware'], 'answer': 1, 'why': 'Salesforce delivered software through the browser instead of a CD, years before AWS. VMware is a virtualization company.'}, {'q': 'Intermediate: Which technology most directly made IaaS possible?', 'options': ['SQL', 'Virtualization', 'HTML', 'Email'], 'answer': 1, 'why': 'A hypervisor lets one physical server run many isolated VMs, so a provider can rent slices of servers (animation 2).'}, {'q': 'Intermediate: What did the cloud add on top of virtualization?', 'options': ['A faster CPU', 'Self-service, metering and access for anyone over the internet', 'Bigger hard disks', 'Mainframe terminals'], 'answer': 1, 'why': 'Company data centres had VMs from about 2000. The cloud appeared when providers added a self-service portal/API, a meter and opened it to the public (animation 2, steps 4–5).'}, {'q': 'Intermediate: Clusters vs grids: which statement is right?', 'options': ['A grid is always in one room', 'A cluster is tightly connected computers in one place; a grid joins computers across organisations', 'They are the same', 'A cluster spans the internet'], 'answer': 1, 'why': 'Cluster = similar machines on a fast local network acting as one system (e.g. Hadoop cluster). Grid = loosely coupled, often different machines from several organisations (e.g. scientific grids).'}, {'q': 'Advanced: AWS Lambda (serverless) launched in…', 'options': ['2006', '2014', '2020', '1999'], 'answer': 1, 'why': 'Lambda (2014) made “run code, pay per call” mainstream; Azure Functions followed in 2016 and Google Cloud Functions in 2017 (beta).'}, {'q': 'Advanced: Why did web services and APIs matter for the cloud?', 'options': ['They made websites colourful', 'They let programs request resources from the provider automatically', 'They replaced the internet', 'They are only for banks'], 'answer': 1, 'why': 'Every cloud action (create VM, store file) is an API call over HTTP. Service-oriented architecture and web APIs (2000s) made self-service and automation possible.'}])
REVISION = ['The problem: computers are costly and mostly idle; each era fixed part of it.', 'Eras: mainframe → PC → client-server/web → grid → virtualization → cloud → serverless/AI.', 'Paradigms: centralized, parallel, distributed, cluster, grid, cloud (see the paradigms section).', 'Key enabler: hypervisor + VMs; cloud = virtualization + self-service + metering + internet; web APIs make it programmable.', 'Milestones: Salesforce 1999, AWS S3/EC2 2006, App Engine 2008, Azure 2010, Docker 2013, Kubernetes 2014, Lambda 2014.', 'India: Azure 2015, AWS Mumbai 2016, GCP Mumbai 2017.']
FAQ = [('What is the difference between parallel and distributed computing?', 'Parallel computing splits one task across many processors that usually share memory in one machine; distributed computing uses many separate computers that talk over a network. Clusters, grids and clouds are all forms of distributed computing.'), ('Is cloud the same as mainframe?', 'Same sharing idea, but self-service, internet access, elastic scale and millions of commodity servers.'),
    ('Why did Amazon start a cloud?', 'It had learned to run huge infrastructure for its retail business and turned that into products (commonly told story).'),
    ('Will the cloud keep growing?', 'Yes: AI, data and edge services keep adding services; the SDK still adds new ones every year.'),
    ('Do exams ask dates?', 'Rarely exact dates; they ask benefits and evolution concepts.')]
PRACTICE_INTRO = 'History programs.'
PROBLEMS = [
    dict(level='easy', title='Sum', stmt='Services 2017+2018.', inp='ints', code='print(50 + 82)\n', explain='132.'),
    dict(level='easy', title='Years', stmt='1961 → 2006.', inp='ints', code='print(2006 - 1961)\n', explain='45 years.'),
    dict(level='easy', title='Share', stmt='% added 2017–18.', inp='ints', code='print(round(132 / 436 * 100), "%")\n', explain='30%.'),
    dict(level='medium', title='Peak year', stmt='Max of dict.', inp='dict', code='a = {2016: 22, 2017: 50, 2018: 82}\nprint(max(a, key=a.get))\n', explain='2018.'),
    dict(level='medium', title='Decades', stmt='Group by decade.', inp='dict', code='a = {2006: 1, 2009: 2, 2010: 7, 2014: 19, 2018: 82, 2021: 33}\nfrom collections import Counter\nc = Counter()\nfor y, n in a.items(): c[y // 10 * 10] += n\nprint(dict(c))\n', explain='2010s dominate.'),
    dict(level='medium', title='Sort eras', stmt='Chronological.', inp='dict', code='e = {"cloud": 2006, "grid": 1998, "web": 1991}\nprint(sorted(e, key=e.get))\n', explain='web, grid, cloud.'),
    dict(level='business', title='Age of region', stmt='Mumbai region age.', inp='int', code='print(2026 - 2016, "years")\n', explain='10.'),
    dict(level='business', title='Avg per year', stmt='Services per year.', inp='ints', code='print(round(436 / 20, 1))\n', explain='~22.')]
SCN_INTRO = 'History interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“How did cloud computing evolve?”', 'A common warm-up question.', 'Can you tell it as a cause-and-effect story?', '<p>“From mainframe time-sharing, to PCs, to client-server and the web, to grid and utility computing, to virtualization — and then providers added self-service, metering and internet access: AWS in 2006, Google App Engine in 2008, Azure in 2010. Today it continues with containers, serverless and AI services.”</p>', '“Amazon invented the cloud in 2006.”') +
    scn('Training', 'Fresher', 'Cluster vs grid vs cloud', 'Asked in C-DAC and university vivas.', 'Do you know the paradigms?', '<ul><li>Cluster: tightly coupled machines in one place acting as one.</li><li>Grid: loosely coupled machines across organisations for big jobs.</li><li>Cloud: on-demand, self-service, metered resources for anyone.</li></ul>', 'Saying they are all the same.') +
    scn('Consulting', 'Mid-level', 'Is virtualization the same as cloud?', 'A client says “we already have VMware, so we have a cloud”.', 'Do you know what makes a cloud?', '<ul><li>Virtualization is the technology; a cloud also needs self-service, elasticity, metering and broad access (NIST).</li><li>A VMware farm becomes a private cloud only with a self-service portal and automation.</li></ul>', 'Agreeing without checking.') +
    scn('Product', 'Mid-level', 'Why is serverless “the next step”?', 'Team debates VMs vs functions.', 'Can you link history to design choices?', '<ul><li>Each era removed more ownership: hardware → OS → servers.</li><li>Serverless bills per call/ms and scales to zero, the utility idea taken furthest.</li></ul>', '“It is just a fashion.”'))
