import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='03-characteristics-and-advantages-of-cloud', n='1.3', module_label='Module 1 · Introduction to cloud computing',
    title='Advantages of cloud computing',
    desc='The five NIST characteristics of cloud computing and the six AWS advantages explained with real AWS Mumbai prices from the public price list: S3 per GB-month, requests, EC2 per hour. AZ-900 benefits, exam wording, mistakes and a calculator mini project.',
    og_desc='$0.025 per GB-month and $0.0112 per hour: the characteristics and advantages of cloud with real AWS prices.',
    minutes=20, level='Beginner',
    lead='Learn the <b>five characteristics</b> and <b>six advantages</b> exams ask for, then prove “measured service” by reading <b>AWS’s real Mumbai price list</b> and calculating a bill.',
    chips=['5 characteristics', '6 advantages', 'Real price list', 'Diagrams + animations'])
MAIN = '''# TiffinGo monthly bill with real AWS Mumbai prices (US$)
storage_gb_month = 0.025      # S3 Standard, first 50 TB
per_request = 0.000005        # PUT/COPY/POST/LIST
vm_hour = {"t3.micro": 0.0112, "t3.medium": 0.0448}

photos = 500 * storage_gb_month + 200_000 * per_request
dev_vm = vm_hour["t3.medium"] * 10 * 22          # 10 h/day, 22 working days
always_on = vm_hour["t3.medium"] * 730
print(f"photos: ${photos:.2f}")
print(f"dev VM office hours: ${dev_vm:.2f}  vs always on: ${always_on:.2f}")
'''
RUN = dict(heading='Run the code: a real cloud bill', intro='<p>Prices from Steps 2–5. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('dev_vm = vm_hour["t3.medium"] * 10 * 22          # 10 h/day, 22 working days', 'Stop at night: pay fewer hours.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: 2 TB', hint='<b>Predict first:</b> 2,000 GB storage.', code='print(2000 * 0.025)\n'),
        dict(label='3 · Match', hint='Characteristic for each story.', code='s = {"recharge yourself": "on-demand self-service", "Diwali servers": "rapid elasticity", "exact usage bill": "measured service"}\nfor k, v in s.items(): print(k, "->", v)\n'),
        dict(label='4 · Rupees', hint='₹84 per $ (assumption).', code='print(round(13.5 * 84), "₹ per month")\n'),
        dict(label='5 · Spot the error', hint='Elastic vs scalable.', expect='error', code='answer = "scalability"\nquestion = "automatically add and remove resources with demand"\nif answer != "elasticity":\n    raise ValueError("that is elasticity: scalability is only the ability to grow")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Python 3, internet. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l13_measured.py', file='terminal', output='  total ≈ $13.50 per month · if photos removed next month: $0 storage', note='EC2 section needs the 315 MB EC2 file.')])
TRACE = dict(heading='A bill step by step', intro='<p>Usage × price.</p>',
    code='usage = {"GB": 500, "req": 200000}\nprice = {"GB": 0.025, "req": 0.000005}\nbill = sum(usage[k] * price[k] for k in usage)\nprint(round(bill, 2))\n', notes={3: 'Rating :: usage × price.'})
WORKED_INTRO = 'Three advantage questions.'
EXAMPLES = [
    dict(level='b', tag='trait', title='Name the characteristic', problem='<p>Manage resources from the AWS mobile app on a train.</p>', inp='story', approach=['Any device.', 'Standard network.', 'Broad network access.'], code='print("broad network access")\n', notes={1: 'NIST.'}, tryit='Types table.'),
    dict(level='i', tag='advantage', title='Exam phrase', problem='<p>No need to buy servers for the peak.</p>', inp='story', approach=['Peak handled by scaling.', 'No forecasting.', 'Stop guessing capacity.'], code='print("stop guessing capacity")\n', notes={1: 'AWS wording.'}, tryit='Levels L3.'),
    dict(level='a', tag='cost', title='Office hours saving', problem='<p>Dev VM 24×7 vs 10×22.</p>', inp='prices', approach=['730 h vs 220 h.', 'Same price per hour.', '70% saving.'], code='print(round((1 - 220 / 730) * 100), "% saved")\n', notes={1: 'Measured service.'}, tryit='RUN.')]
QUIZ = mix([{'q': 'Beginner: “Trade capital expense for variable expense” means…', 'options': ['Buy servers in advance', 'Pay for what you use instead of buying up front', 'Pay a fixed fee', 'Free cloud'], 'answer': 1, 'why': 'CapEx = up-front purchase; variable/OpEx = monthly usage. In the capacity picture the red line is CapEx; the green line is pay-per-use.'}, {'q': 'Beginner: S3 Standard storage in Mumbai costs about…', 'options': ['$2.50 per GB-month', '$0.025 per GB-month', '$0.25 per GB-month', 'Free'], 'answer': 1, 'why': 'From the real price list (Real proof step 2): $0.025 for the first 50 TB, cheaper above that.'}, {'q': 'Beginner: In the capacity-vs-demand picture, the red shaded area means…', 'options': ['Profit', 'Servers paid for but not used (waste)', 'Cloud capacity', 'Free tier'], 'answer': 1, 'why': 'Owned capacity is bought for a forecast; whenever demand is below it, you paid for idle machines.'}, {'q': 'Intermediate: “Stop guessing capacity” comes from which characteristic?', 'options': ['Security', 'Elasticity', 'Compliance', 'Support plans'], 'answer': 1, 'why': 'Because capacity grows and shrinks with demand automatically, you no longer have to forecast peak load.'}, {'q': 'Intermediate: Lower prices because AWS buys hardware for millions of customers is…', 'options': ['Agility', 'Economies of scale', 'Resource pooling', 'Self-service'], 'answer': 1, 'why': 'Huge scale lowers cost per unit, passed on as lower prices (S3 tiers $0.025 → $0.024 → $0.023).'}, {'q': 'Intermediate: Replacing a VM with a bigger one (more CPU/RAM) is…', 'options': ['Scale out', 'Scale up (vertical scaling)', 'Elasticity', 'Pooling'], 'answer': 1, 'why': 'Scale up = bigger machine (has a ceiling, often a restart). Scale out = more machines. Elasticity = automatic scale out and in (animation 2).'}, {'q': 'Advanced: In AZ-900, “the ability to forecast performance and cost” is called…', 'options': ['Governance', 'Predictability', 'Elasticity', 'Manageability'], 'answer': 1, 'why': 'Microsoft lists predictability of performance and cost as a cloud benefit (budgets, calculators, autoscale).'}, {'q': 'Advanced: Which pricing idea is “consumption-based model”?', 'options': ['Pay a licence once', 'Pay only for the resources you consume, no up-front cost', 'Pay per employee', 'Pay per region'], 'answer': 1, 'why': 'AZ-900 term for pay-as-you-go: no up-front cost, pay for what you use, stop paying when you stop using.'}])
REVISION = ['Capacity vs demand: owning = waste + shortage; cloud follows demand.', 'AWS 6: CapEx→variable, economies of scale, stop guessing capacity, speed/agility, no data centres, global in minutes.', 'Also: backup & recovery, collaboration & mobility, sustainability, security tools, innovation.', 'Scale up = bigger VM; scale out = more VMs; elasticity = automatic both ways.', 'Bill = usage × price list (real Mumbai: t3.micro $0.0112/h, S3 $0.025/GB-mo) → $21.56 example.', 'AZ-900 words: high availability, scalability, elasticity, reliability, predictability, security, governance, manageability; consumption-based model.']
FAQ = [('Are prices the same in every region?', 'No; compare the same region. Mumbai and US East differ.'),
    ('Does AWS bill per hour or per second?', 'Linux EC2: per second with a 60-second minimum; others vary.'),
    ('What is the free tier?', 'A small monthly allowance or credits for new accounts; AWS course 1.3.'),
    ('Where do I see my real bill?', 'Billing console / Cost Explorer (AWS), Cost Management (Azure), Billing reports (GCP).')]
PRACTICE_INTRO = 'Pricing programs.'
PROBLEMS = [
    dict(level='easy', title='Storage', stmt='1 TB month.', inp='float', code='print(1000 * 0.025)\n', explain='$25.'),
    dict(level='easy', title='VM day', stmt='t3.micro 24 h.', inp='float', code='print(round(0.0112 * 24, 4))\n', explain='$0.27.'),
    dict(level='easy', title='Requests', stmt='1 million PUTs.', inp='float', code='print(1_000_000 * 0.000005)\n', explain='$5.'),
    dict(level='medium', title='Tier', stmt='Price for 60 TB.', inp='floats', code='gb = 60_000\nprint(51200 * 0.025 + (gb - 51200) * 0.024)\n', explain='Tiered.'),
    dict(level='medium', title='Office hours', stmt='Saving %.', inp='ints', code='print(round((730 - 220) / 730 * 100))\n', explain='70%.'),
    dict(level='medium', title='Map', stmt='Trait for words.', inp='dict', code='w = {"self": "on-demand", "meter": "measured"}\nprint(w["meter"])\n', explain='measured.'),
    dict(level='business', title='Yearly', stmt='Photo bill per year.', inp='float', code='print(13.5 * 12)\n', explain='$162.'),
    dict(level='business', title='Box vs cloud', stmt='₹60,000 NAS vs cloud 3 years.', inp='ints', code='print(60000, round(13.5 * 36 * 84))\n', explain='Compare TCO (Lesson 1.5).')]
SCN_INTRO = 'Benefits interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“What are the advantages of cloud computing?”', 'Very common question.', 'Do you know the standard list and can you give an example?', '<p>“We trade capital expense for variable expense, benefit from economies of scale, stop guessing capacity because of elasticity, gain speed and agility, stop spending on data centres, and can go global in minutes. Plus backup and recovery, collaboration from anywhere and sustainability.”</p>', 'Only saying “it is cheap”.') +
    scn('Azure team', 'Fresher', 'Scalability vs elasticity', 'AZ-900 favourite.', 'Do you know the precise difference?', '<ul><li>Scalability: the system can handle more load (scale up or out).</li><li>Elasticity: it scales out and in automatically with demand.</li></ul>', '“They are the same.”') +
    scn('Finance', 'Mid-level', 'Prove pay-as-you-go to finance', 'Finance doubts the savings.', 'Can you work with real pricing?', '<ul><li>Pricing calculator / price list API, usage × price per service.</li><li>Budgets, tags, monthly review of Cost Explorer.</li></ul>', '“Trust the vendor.”') +
    scn('Startup', 'Mid-level', 'When are the advantages NOT real?', 'A steady 24×7 workload.', 'Do you know the limits?', '<ul><li>Steady loads on on-demand prices can cost more; use savings plans/reserved or compare TCO (Lesson 1.5).</li></ul>', '“Cloud is always cheaper.”'))
