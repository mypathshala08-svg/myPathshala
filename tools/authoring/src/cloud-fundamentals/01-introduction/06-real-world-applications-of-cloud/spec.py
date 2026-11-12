import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='06-real-world-applications-of-cloud', n='1.6', module_label='Module 1 · Introduction to cloud computing',
    title='Real-world applications of cloud',
    desc='Real-world applications of cloud computing: web and mobile apps, payments, streaming, healthcare, education, e-governance, agriculture, IoT, big data and AI, with real data from the Registry of Open Data on AWS, hands-on AWS CLI access to public datasets, and the Module 1 combined project.',
    og_desc='1,474 open datasets and ten industries: where cloud computing is really used, with a hands-on public-data lab.',
    minutes=20, level='Beginner',
    lead='Where is the cloud used? We map <b>ten application areas</b> to cloud building blocks, explore <b>1,474 open datasets</b> on AWS, read a public bucket with the AWS CLI, and finish Module 1 with a <b>combined project</b>.',
    chips=['10 industries', 'Open data on AWS', 'Module 1 project', 'Diagrams + animations'])
MAIN = '''# Match a use case to cloud building blocks
blocks = {
    "food delivery app": ["load balancer", "auto-scaled compute", "managed database", "CDN"],
    "satellite crop map": ["object storage (open data)", "Spark on cloud", "dashboard"],
    "smart meters": ["IoT hub", "stream", "time-series DB"],
    "X-ray triage": ["encrypted storage (India region)", "GPU inference", "audit logs"],
}
for app, parts in blocks.items():
    print(f"{app:20} -> " + " + ".join(parts))
'''
RUN = dict(heading='Run the code: use case → building blocks', intro='<p>Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    "food delivery app": ["load balancer", "auto-scaled compute", "managed database", "CDN"],', 'Classic web app pattern.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: top tag', hint='<b>Predict first:</b> most common open-data topic?', code='tags = {"life sciences": 527, "satellite imagery": 310, "medicine": 293}\nprint(max(tags, key=tags.get))\n'),
        dict(label='3 · Add one', hint='Online exam portal.', code='print("online exam -> auto-scaled web + database + CDN + logs")\n'),
        dict(label='4 · Share', hint='% satellite of 1474.', code='print(round(310 / 1474 * 100), "% of datasets")\n'),
        dict(label='5 · Spot the error', hint='Download petabytes.', expect='error', code='dataset_tb, laptop_tb = 5000, 1\nif dataset_tb > laptop_tb:\n    raise MemoryError("do not download: analyse in the cloud next to the data")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Python 3 / AWS CLI, internet. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l16_apps.py', file='terminal', output='  datasets on the page: 1474  tag uses: 8714', note='Grows over time.'),
           dict(title='2 · Public bucket', cmd='aws s3 ls --no-sign-request s3://noaa-ghcn-pds/', file='terminal', output='', note='No account needed.')])
TRACE = dict(heading='Counting tags step by step', intro='<p>Counter.</p>',
    code='from collections import Counter\nc = Counter(["climate", "health", "climate"])\nprint(c.most_common(1))\n', notes={2: 'Count :: each tag.'})
WORKED_INTRO = 'Three use-case mappings.'
EXAMPLES = [
    dict(level='b', tag='web', title='Static website', problem='<p>College fest website.</p>', inp='need', approach=['Static files.', 'Object storage.', 'CDN.'], code='print("S3 static website + CloudFront")\n', notes={1: 'AWS course 4.5.'}, tryit='Exam tip.'),
    dict(level='i', tag='data', title='Analyse open data', problem='<p>Query 10 years of weather.</p>', inp='need', approach=['Data on S3.', 'Serverless SQL.', 'Pay per query.'], code='print("Athena over the public bucket")\n', notes={1: 'Bring compute to data.'}, tryit='Practical.'),
    dict(level='a', tag='AI', title='Hospital AI', problem='<p>X-ray triage with rules.</p>', inp='need', approach=['India region.', 'Encrypt.', 'GPU inference + audit.'], code='print(["ap-south-1", "KMS", "GPU endpoint", "CloudTrail"])\n', notes={1: 'Compliance.'}, tryit='Scenario 3.')]
QUIZ = mix([{'q': 'Beginner: Who uses the cloud?', 'options': ['Only IT companies', 'Streaming, payments, health, education, government, farming and more', 'Nobody in India', 'Only games'], 'answer': 1, 'why': 'The industries × building blocks picture shows eight very different industries using the same cloud blocks.'}, {'q': 'Beginner: A CDN is used to…', 'options': ['Store passwords', 'Deliver content fast from servers near the user', 'Make bills', 'Back up laptops'], 'answer': 1, 'why': 'CDN edge locations in many cities keep copies of video, images and web pages close to viewers (cricket animation, step 4).'}, {'q': 'Beginner: Why is the live cricket video encoded into several qualities?', 'options': ['To make it smaller on disk', 'So slow and fast connections can both play smoothly', 'For copyright', 'It is not'], 'answer': 1, 'why': 'Adaptive bitrate: the player picks 1080p on fast Wi-Fi and 240p on weak mobile data (cricket animation, step 2).'}, {'q': 'Intermediate: In the crop-advice animation, why does Spark run in the same region as the satellite data?', 'options': ['It is cheaper to download everything', 'To analyse data in place instead of moving terabytes', 'Spark needs no data', 'For security only'], 'answer': 1, 'why': '“Bring compute to data”: reading data in the same region is fast and avoids huge downloads and transfer fees.'}, {'q': 'Intermediate: Most common topic in AWS’s open data registry (our count)…', 'options': ['Gaming', 'Life sciences', 'Music', 'Sports'], 'answer': 1, 'why': 'Real proof step 2: life sciences 527 datasets, then satellite imagery 310.'}, {'q': 'Intermediate: The Government of India’s cloud initiative is called…', 'options': ['ONDC', 'MeghRaj (GI Cloud)', 'UPI', 'Aadhaar'], 'answer': 1, 'why': 'MeghRaj guides government departments to use cloud services from empanelled providers. UPI and ONDC are digital public platforms that run on large-scale infrastructure.'}, {'q': 'Advanced: Readings from lakhs of smart electricity meters fit which pattern?', 'options': ['Archive storage only', 'IoT hub + stream processing + database + analytics', 'CDN only', 'Email'], 'answer': 1, 'why': 'Devices send small messages continuously; they are ingested by an IoT/streaming service, processed and stored for billing and analytics.'}, {'q': 'Advanced: Reading a public open-data bucket without an AWS account uses…', 'options': ['--force', '--no-sign-request', '--root', '--public'], 'answer': 1, 'why': 'The AWS CLI option --no-sign-request sends anonymous requests, allowed only for public buckets (hands-on step 3).'}])
REVISION = ['Same building blocks everywhere: compute, storage, database, streaming, analytics, AI, CDN.', 'Live streaming: encode once → origin → CDN edges in each city → scale for the final over.', 'Big data on cloud: open data (1,474 datasets on AWS) + Spark next to the data → results → map → SMS.', 'India: national-scale platforms (DigiLocker, CoWIN, UPI, IRCTC) show why elastic, multi-zone infrastructure matters; MeghRaj guides government cloud use.', 'Describe patterns, not guesses about a company’s exact setup; read open-data licences.']
FAQ = [('Is reading open data really free?', 'For public open-data buckets, yes for you; costs are covered by the program. Your own compute is billed.'),
    ('Can I use this for my capstone?', 'Yes — weather, satellite, transport and health datasets are great; check licences.'),
    ('What is MeghRaj?', 'The Government of India’s cloud initiative (GI Cloud) for government departments.'),
    ('Which course next?', 'Module 2 service models; for hands-on, the AWS course.')]
PRACTICE_INTRO = 'Application programs.'
PROBLEMS = [
    dict(level='easy', title='Percent', stmt='Weather share.', inp='ints', code='print(round(197 / 1474 * 100))\n', explain='13%.'),
    dict(level='easy', title='Top 2', stmt='Two largest.', inp='dict', code='d = {"a": 527, "b": 310, "c": 293}\nprint(sorted(d, key=d.get)[-2:])\n', explain='b, a.'),
    dict(level='easy', title='Avg tags', stmt='Tags per dataset.', inp='ints', code='print(round(8714 / 1474, 1))\n', explain='~5.9.'),
    dict(level='medium', title='Map', stmt='Use case → service.', inp='dict', code='m = {"video": "CDN", "files": "object storage"}\nprint(m["video"])\n', explain='CDN.'),
    dict(level='medium', title='Filter', stmt='Names with "noaa".', inp='list', code='n = ["noaa-goes", "sentinel-2", "noaa-nexrad"]\nprint([x for x in n if "noaa" in x])\n', explain='2.'),
    dict(level='medium', title='Group', stmt='Count by first word.', inp='list', code='from collections import Counter\nn = ["noaa-goes", "noaa-nexrad", "sentinel-2"]\nprint(Counter(x.split("-")[0] for x in n))\n', explain='noaa 2.'),
    dict(level='business', title='Download time', stmt='5 PB at 100 Mbps.', inp='ints', code='print(round(5e15 * 8 / 100e6 / 86400 / 365, 1), "years")\n', explain='~12.7 years!'),
    dict(level='business', title='Pick project', stmt='Score ideas.', inp='dict', code='s = {"weather": 8, "toy csv": 3, "satellite": 9}\nprint(max(s, key=s.get))\n', explain='satellite.')]
SCN_INTRO = 'Applications interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“Where is cloud computing used?”', 'Checks real-world awareness.', 'Can you connect industries to services?', '<p>“Streaming (encode + CDN), payments (elastic compute, multi-AZ databases), e-commerce, healthcare, education, e-governance, IoT, big data and AI. All combine the same blocks: compute, storage, databases, streaming, analytics, AI and CDN.”</p>', '“Google Drive.”') +
    scn('Analytics', 'Fresher', 'Analysing 5 TB of satellite images', 'A capstone idea.', 'Do you know “compute next to data”?', '<ul><li>Use the open data where it is stored; run Spark/Athena in the same region; download only small results.</li></ul>', 'Downloading everything to a laptop.') +
    scn('Media', 'Mid-level', 'Final over: viewers ×50', 'Live stream design.', 'Do you know CDN + elasticity?', '<ul><li>Adaptive bitrate encoding, CDN edges absorb the spike, origin and encoder scale out, scale back after the match.</li></ul>', 'One big server.') +
    scn('Government', 'Mid-level', 'Citizen portal on result day', 'Crores of users at 10 am.', 'Can you design for spikes and rules?', '<ul><li>Indian region, multiple zones, auto scaling, CDN and a web application firewall, queue for heavy tasks.</li></ul>', 'A single VM.'))
