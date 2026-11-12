import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('AWS lists more than 200 services, Azure and Google Cloud a similar number. Do you need to learn them all?',
    'No. Almost every service belongs to one of about a dozen <b>categories</b>, and each category answers one question: where does my code run, where does my data live, how do I analyse it, how do I secure it, how do I watch and automate it, how do parts talk to each other. Learn the categories and the <b>one or two flagship services</b> in each, and you can read any cloud architecture — and translate it between AWS, Azure and Google Cloud. This lesson builds that map, follows one TiffinGo order through eight services, and has you browse the catalogue, send messages through a queue and list everything you own on <b>your own</b> account.',
    ['Seven product families beyond compute, storage and networking.', 'One order, eight services: how they fit together.', 'How to translate an AWS diagram into Azure or Google Cloud in five minutes.'])

def story_scene():
    o = t(180, 12, 'The menu card problem', 9, 'ink', bold=True)
    o += box(14, 26, 150, 90, 'card', rx=8) + t(89, 42, '200+ services', 8.4, 'ink', bold=True)
    for i in range(5): o += box(24, 52 + i * 12, 130, 8, 'card', rx=2)
    o += arrow(168, 70, 194, 70)
    for i, (n, tn) in enumerate([('Compute', 'blue'), ('Data', 'green'), ('Analytics', 'violet'), ('AI', 'amber'), ('Security', 'red'), ('Ops', 'blue')]):
        x = 198 + (i % 3) * 52; y = 30 + (i // 3) * 42
        o += box(x, y, 48, 36, tn, rx=5) + t(x + 24, y + 22, n, 6.6, 'ink', bold=True)
    o += t(180, 132, 'Group the menu into families — then each family has 1–2 dishes to learn first.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('A long list of 200 services turned into six family boxes: compute, data, analytics, AI, security and operations.', story_scene(), 'Learn the <tspan font-weight="700" class="s-acc">families</tspan>, not the whole menu.', h=146)
dialogue = '''R> Sir, the investor’s tech advisor sent an architecture: Aurora, ElastiCache, SQS, EventBridge, Kinesis, Athena, Bedrock, Cognito, CloudWatch… I know three of these.
A> Read it by family. Aurora and ElastiCache are databases. SQS and EventBridge connect parts. Kinesis and Athena are analytics. Bedrock is AI. Cognito is identity. CloudWatch watches everything.
K> And if they wanted Azure instead?
A> Same families, different names — Azure SQL, Service Bus, Event Hubs, Fabric, Azure OpenAI in Microsoft Foundry, Entra ID, Azure Monitor.
R> So the map matters more than the names.
A> Exactly. Let’s draw the map.'''

# ------------------------------------------------------------------ picture
def mapfig_big():
    o = t(320, 16, 'The cloud product map: ten families, flagship services in each', 10.5, 'ink', bold=True)
    fam = [('Compute', 'EC2 · Lambda · EKS', 'Lesson 6.1', 'blue'), ('Storage', 'S3 · EBS · EFS', 'Lesson 6.2', 'blue'), ('Networking', 'VPC · ELB · Route 53 · CloudFront', 'Lesson 6.3', 'blue'),
           ('Databases', 'RDS/Aurora · DynamoDB · ElastiCache', 'type 1', 'green'), ('Analytics & big data', 'Athena · EMR · Redshift · Kinesis', 'type 2', 'green'), ('AI & machine learning', 'Bedrock · SageMaker AI', 'type 3', 'violet'),
           ('Security & identity', 'IAM · KMS · GuardDuty', 'type 4', 'red'), ('Management & governance', 'CloudWatch · CloudTrail · Organizations', 'type 5', 'amber'), ('DevOps & IaC', 'CloudFormation · CodePipeline', 'type 6', 'amber'), ('Integration', 'SQS · SNS · EventBridge · API GW', 'type 7', 'violet')]
    for i, (n, s, l, tn) in enumerate(fam):
        x = 12 + (i % 5) * 124; y = 30 + (i // 5) * 98
        o += box(x, y, 118, 88, tn, rx=8) + t(x + 59, y + 22, n, 7.4, 'ink', bold=True)
        words = s.split(' · ')
        for j, w in enumerate(words): o += t(x + 59, y + 40 + j * 11, w, 6.4, 'ink')
        o += t(x + 59, y + 82, l, 6, 'ink2')
    o += t(320, 244, 'Shown with AWS names; the same ten families exist in Azure and Google Cloud (table below). Industry solutions are built from these blocks.', 7.2, 'ink2')
    return o
BIGMAP = bigfig('Ten boxes: compute, storage, networking (Lessons 6.1–6.3), databases, analytics and big data, AI and machine learning, security and identity, management and governance, DevOps and infrastructure as code, integration — each with flagship AWS services.', mapfig_big(), h=254)

def translate():
    return table(['Family', 'What it answers', 'AWS', 'Azure', 'Google Cloud'], [
        ['Relational database', 'tables, SQL, transactions', 'RDS, Aurora', 'Azure SQL Database, Azure Database for PostgreSQL/MySQL', 'Cloud SQL, AlloyDB, Spanner'],
        ['NoSQL database', 'huge scale key-value/document', 'DynamoDB', 'Cosmos DB', 'Firestore, Bigtable'],
        ['In-memory cache', 'microsecond reads', 'ElastiCache, MemoryDB', 'Azure Cache for Redis / Managed Redis', 'Memorystore'],
        ['Data warehouse / SQL on lake', 'analytics on TBs–PBs', 'Redshift, Athena', 'Microsoft Fabric, Synapse', 'BigQuery'],
        ['Spark / Hadoop', 'big-data processing', 'EMR, Glue', 'Fabric Spark, Azure Databricks, HDInsight', 'Dataproc, Dataflow'],
        ['Streaming', 'events in real time', 'Kinesis, MSK', 'Event Hubs', 'Pub/Sub, Managed Kafka'],
        ['Generative AI / ML platform', 'models and ML lifecycle', 'Bedrock, SageMaker AI', 'Azure OpenAI in Microsoft Foundry, Azure ML', 'Vertex AI, Gemini'],
        ['Identity', 'who are you, what may you do', 'IAM, IAM Identity Center, Cognito', 'Microsoft Entra ID, RBAC', 'Cloud IAM, Identity Platform'],
        ['Keys and secrets', 'encryption keys, passwords', 'KMS, Secrets Manager', 'Key Vault', 'Cloud KMS, Secret Manager'],
        ['Monitoring and audit', 'metrics, logs, who did what', 'CloudWatch, CloudTrail', 'Azure Monitor, Activity Log', 'Cloud Monitoring, Cloud Logging, Audit Logs'],
        ['Infrastructure as code', 'build environments from files', 'CloudFormation, CDK', 'ARM templates, Bicep', 'Infrastructure Manager (Terraform)'],
        ['Messaging and events', 'decouple parts', 'SQS, SNS, EventBridge', 'Service Bus, Event Grid', 'Pub/Sub, Eventarc'],
        ['APIs and workflows', 'front door for APIs, orchestration', 'API Gateway, Step Functions', 'API Management, Logic Apps', 'Apigee/API Gateway, Workflows']], minw=780)

picture = ('  <p>All cloud services fit on one page once you group them into families. Compute, storage and networking you already know from Lessons 6.1–6.3:</p>\n' + BIGMAP +
           '\n  <p>And the translation table — the single most useful page for multi-cloud interviews and certifications:</p>\n' + translate())

# ------------------------------------------------------------------ how: one order, eight services
RN = {'app': (4, 54, 54, 50, 'phone', 'App', 'Cognito login'), 'api': (66, 4, 60, 46, 'cloud', 'API Gateway', 'POST /order'), 'fn': (66, 104, 60, 46, 'app', 'Lambda', 'validate'),
      'db': (138, 54, 62, 50, 'db', 'DynamoDB', 'save order'), 'q': (212, 4, 64, 46, 'dns', 'SQS / SNS', 'notify kitchen'), 'an': (212, 104, 64, 46, 'chart', 'Kinesis → S3', 'Athena'), 'ai': (290, 54, 66, 50, 'chip', 'Bedrock', 'suggest dish')}
RS = [dict(on=['app', 'api'], hot='api', move=(58, 70, 70, 40, 'HTTPS'), head='Step 1 · Identity + API front door', text='The customer is signed in (Cognito issues a token). The app calls POST /order on', text2='API Gateway, which checks the token and throttles abuse.', svc='Security & identity + Integration families'),
      dict(on=['app', 'api', 'fn'], hot='fn', move=(96, 50, 96, 104, 'invoke'), head='Step 2 · Code runs only when called', text='API Gateway invokes a Lambda function that validates the order and the price.', text2='No server is waiting between orders.', svc='Compute family (Lesson 6.1)'),
      dict(on=['app', 'api', 'fn', 'db'], hot='db', move=(126, 127, 150, 90, 'PutItem'), head='Step 3 · Save to a managed database', text='The order is written to DynamoDB in single-digit milliseconds; capacity scales', text2='automatically with Diwali traffic.', svc='Database family (type 1)'),
      dict(on=['app', 'api', 'fn', 'db', 'q'], hot='q', move=(200, 70, 222, 40, 'event'), head='Step 4 · Tell the kitchen — without waiting', text='An “OrderPlaced” message goes to a queue/topic; the kitchen and delivery apps', text2='pick it up independently. If one is down, messages wait.', svc='Integration family (type 7)'),
      dict(on=['app', 'api', 'fn', 'db', 'q', 'an'], hot='an', move=(200, 90, 222, 120, 'stream'), head='Step 5 · Every order also flows to analytics', text='A stream lands orders in S3 as files; Athena runs SQL on them for the daily', text2='dashboard — no database load from reports.', svc='Analytics family (type 2)'),
      dict(on=list(RN), hot='ai', move=(276, 127, 298, 90, 'prompt'), head='Step 6 · AI suggests the next dish', text='A foundation model on Bedrock writes a personalised “You may also like…” line;', text2='CloudWatch and CloudTrail watch every step.', svc='AI family (type 3) + Management family (type 5)')]
FLOW = flow_anim('One TiffinGo order, eight cloud services', 'How families of services work together in a real application.', 'Order flow', 'Animation: login and API Gateway; Lambda validates; DynamoDB saves; a queue notifies the kitchen; a stream feeds analytics; an AI model suggests a dish.', RN, RS, hid='prodflow')

# ------------------------------------------------------------------ types
def tmap():
    o = t(320, 16, 'Seven more product families, one by one', 11, 'ink', bold=True)
    items = [('1', 'Databases', 'relational · NoSQL · cache', 'green'), ('2', 'Analytics & big data', 'warehouse · Spark · streams', 'green'), ('3', 'AI & machine learning', 'GenAI · ML platform · APIs', 'violet'),
             ('4', 'Security & identity', 'IAM · keys · threat detection', 'red'), ('5', 'Management & governance', 'monitor · audit · policy · cost', 'amber'), ('6', 'DevOps & IaC', 'pipelines · templates', 'amber'), ('7', 'Integration', 'queues · events · APIs', 'violet')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.6, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, '1–3 work on data · 4–5 keep everything safe and visible · 6–7 connect people, code and services.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven product families: 1 databases, 2 analytics and big data, 3 AI and machine learning, 4 security and identity, 5 management and governance, 6 DevOps and infrastructure as code, 7 integration.', tmap(), h=222)

def three(title_list, panel_fn, steps, ttl, intro, panel, aria, hid):
    return cap([panel_fn(k) for k in range(3)], steps, ttl, intro, panel, aria, hid)

def a_db(k):
    o = t(180, 12, ['Relational: tables + SQL', 'NoSQL: key → item, any scale', 'Cache: answers in microseconds'][k], 9, 'ink', bold=True)
    if k == 0:
        for i, n in enumerate(['orders', 'customers']):
            o += box(30 + i * 160, 34, 140, 70, 'green', rx=6) + t(100 + i * 160, 50, n, 8, 'ink', bold=True)
            for r in range(3): o += box(40 + i * 160, 58 + r * 14, 120, 10, 'card', rx=2)
        o += arrow(172, 70, 188, 70) + t(180, 120, 'JOIN on customer_id', 7, 'ink', mono=True)
    elif k == 1:
        for i in range(4): o += box(30 + i * 78, 40, 70, 60, 'blue', rx=6) + t(65 + i * 78, 64, f'partition {i + 1}', 6.8, 'ink', bold=True) + t(65 + i * 78, 82, 'order#…', 6.4, 'ink2', mono=True)
        o += t(180, 120, 'items spread by key over many servers', 7, 'ink')
    else:
        o += box(30, 44, 90, 52, 'card', rx=6) + t(75, 74, 'app', 8, 'ink') + box(150, 44, 80, 52, 'red', rx=6) + t(190, 70, 'cache', 8, 'ink', bold=True) + t(190, 86, 'hit: 0.5 ms', 6.6, 'ink2')
        o += box(260, 44, 80, 52, 'green', rx=6) + t(300, 70, 'database', 7.6, 'ink') + t(300, 86, 'miss: 5 ms', 6.6, 'ink2') + arrow(122, 70, 148, 70) + arrow(232, 70, 258, 70)
    o += t(180, 146, ['managed RDS/Azure SQL/Cloud SQL: backups, patching, Multi-AZ', 'DynamoDB/Cosmos DB/Firestore: scale out by key, no joins', 'Redis-compatible cache in front of the database'][k], 7.2, 'ink', bold=True)
    return o
A_DB = cap([a_db(k) for k in range(3)], [('Relational', 'Tables with fixed columns, SQL joins and transactions — managed by the provider.', ''), ('NoSQL', 'Items are spread over partitions by key — near-unlimited scale, simple queries.', ''), ('Cache', 'Hot data kept in memory in front of the database.', '')],
    'Managed databases in action', 'Three shapes of data store.', 'Databases', 'Animation: relational tables joined by SQL; a NoSQL table spread over partitions by key; an in-memory cache in front of a database.', 'p1anim')
T1 = vtype(1, 'Managed databases', 'green',
    '<b>Managed database services</b> run database engines for you — provisioning, patching, backups, replication and failover — in several models: <b>relational</b> (SQL, transactions: RDS, Aurora, Azure SQL, Cloud SQL), <b>NoSQL</b> (key-value, document, wide-column, graph: DynamoDB, Cosmos DB, Firestore, Bigtable) and <b>in-memory</b> caches (ElastiCache, Azure Cache for Redis, Memorystore).',
    'Renting a bank locker with a full-time locker staff, instead of buying your own safe and hiring a guard: you keep the valuables (data), they handle the locks, CCTV and backups.',
    'TiffinGo keeps customers, menus and payments in Aurora PostgreSQL (joins, transactions), live order status in DynamoDB (huge Diwali spikes, simple lookups by order ID) and the menu in a Redis cache so the app opens instantly.',
    'Amazon RDS, Aurora, DynamoDB, ElastiCache, DocumentDB, Neptune; Azure SQL Database, Azure Database for PostgreSQL/MySQL, Cosmos DB, Azure Managed Redis; Cloud SQL, AlloyDB, Spanner, Firestore, Bigtable, Memorystore.',
    '', A_DB,
    'you need a database and do not want to run its servers — which is almost always.',
    'you pick a NoSQL store for data full of relationships, or a relational database for unlimited simple key lookups at massive scale.',
    plain='Databases that the cloud company runs for you: it installs them, backs them up, fixes them and keeps a spare copy ready. You just store and read your data.',
    how=[('Choose engine and size', 'PostgreSQL/MySQL/SQL Server…, instance class or serverless capacity.'), ('Provisioned in your network', 'Placed in private subnets with security groups (Lesson 6.3).'), ('High availability', 'Synchronous standby in another AZ (Multi-AZ) with automatic failover.'), ('Backups', 'Automated daily snapshots + transaction logs → point-in-time restore.'), ('Scale', 'Read replicas, bigger instances, or automatic partitioning (NoSQL).')],
    words=[('relational', 'data in tables linked by keys, queried with SQL'), ('NoSQL', 'databases that do not use fixed tables, built for scale'), ('transaction', 'a group of changes that all succeed or all fail'), ('read replica', 'a read-only copy that takes reporting load')],
    diff=table(['', 'Relational (RDS/Azure SQL/Cloud SQL)', 'NoSQL (DynamoDB/Cosmos DB/Firestore)', 'Cache (Redis)'], [['Query', 'SQL, joins', 'by key / simple queries', 'by key'], ['Scale', 'up + read replicas', 'out, near-unlimited', 'in memory'], ['Durability', 'disk + backups', 'disk, multi-AZ', 'often not the source of truth']], minw=600),
    where=['Transactions: orders, payments, inventory', 'Huge scale lookups: sessions, carts, IoT', 'Caching: menus, leaderboards'],
    realworld='AWS reported that DynamoDB served <b>more than 100 million requests per second</b> at peak for Amazon’s Prime Day events while keeping single-digit-millisecond latency — the kind of spike a single relational server cannot absorb.',
    pro='Aurora separates compute from storage: the database writes only redo log records to a storage layer that keeps six copies across three AZs and builds pages itself — which is why Aurora replicas can be added in minutes without copying the data.')

def a_an(k):
    o = t(180, 12, ['Ingest: data lands in the lake', 'Process: Spark / ETL', 'Query and visualise'][k], 9, 'ink', bold=True)
    o += box(14, 34, 90, 80, 'card' if k else 'amber', rx=8) + t(59, 58, 'apps, logs,', 7, 'ink') + t(59, 72, 'streams', 7, 'ink') + t(59, 92, 'Kinesis / Event Hubs', 5.8, 'ink2')
    o += box(132, 34, 96, 80, 'green', rx=8) + t(180, 58, 'data lake', 7.6, 'ink', bold=True) + t(180, 74, 'S3 / ADLS / GCS', 6.6, 'ink2') + t(180, 92, 'Parquet files', 6.6, 'ink2')
    o += box(256, 34, 90, 80, ['card', 'violet', 'blue'][k], rx=8) + t(301, 58, ['', 'EMR / Dataproc', 'Athena / BigQuery'][k], 7, 'ink', bold=True) + t(301, 76, ['', 'Fabric Spark', 'dashboard'][k], 6.6, 'ink2')
    o += arrow(106, 74, 130, 74)
    if k >= 1: o += arrow(230, 74, 254, 74)
    o += t(180, 140, ['raw data stored cheaply, in open formats', 'Spark cleans, joins and aggregates — clusters on demand', 'serverless SQL and BI tools answer business questions'][k], 7.2, 'ink', bold=True)
    return o
A_AN = cap([a_an(k) for k in range(3)], [('Ingest', 'Streams and batch loads land raw data in object storage — the data lake.', ''), ('Process', 'Managed Spark/Hadoop or ETL services clean and transform it.', ''), ('Query', 'Warehouses and serverless SQL engines answer questions; BI tools visualise.', '')],
    'Analytics in action', 'From raw events to a dashboard.', 'Analytics', 'Animation: data ingested into a data lake; processed with Spark; queried with serverless SQL and shown on a dashboard.', 'p2anim')
T2 = vtype(2, 'Analytics and big data', 'green',
    '<b>Cloud analytics services</b> collect, store, process and query large datasets: <b>streaming</b> ingestion (Kinesis, Event Hubs, Pub/Sub), <b>data lakes</b> on object storage, managed <b>Spark/Hadoop</b> and ETL (EMR, Glue, Dataproc, Databricks, Fabric), <b>data warehouses</b> and serverless SQL (Redshift, Athena, BigQuery, Fabric/Synapse), and BI tools (QuickSight, Power BI, Looker).',
    'A sabzi mandi supply chain: trucks bring raw vegetables (ingest), the godown stores them cheaply (lake), workers sort and pack them (processing), and the shop shelf shows exactly what customers want (dashboard).',
    'Every TiffinGo order is streamed to S3 as Parquet files; a nightly Glue/Spark job builds daily tables; the owner’s dashboard asks Athena “which dishes sell best in Pune on Mondays?” — paying per TB scanned instead of running a warehouse 24×7.',
    'Amazon Kinesis, MSK, S3, Glue, EMR, Athena, Redshift, QuickSight, Lake Formation; Azure Event Hubs, Data Lake Storage, Microsoft Fabric, Synapse, Azure Databricks, Power BI; Google Pub/Sub, Dataflow, Dataproc, BigQuery, Looker.',
    'The Spark, Hive and Kafka courses on this site go deep into these tools.', A_AN,
    'you analyse more data than a single database should handle, or need reports without slowing the live app.',
    'a few thousand rows fit in a spreadsheet or the app database — a data platform is overkill.',
    plain='Services for big data: they collect lots of data, keep it cheaply, clean it and answer questions about it, often with charts.',
    how=[('Ingest', 'Batch uploads or real-time streams.'), ('Store', 'Raw and curated zones in object storage (open formats like Parquet, Iceberg, Delta).'), ('Catalogue', 'Glue Data Catalog / Unity Catalog / Dataplex describe tables and permissions.'), ('Process', 'Spark/Beam jobs on managed or serverless clusters.'), ('Serve', 'Warehouse or serverless SQL for analysts; BI dashboards for business users.')],
    words=[('data lake', 'a big store of raw files, usually object storage'), ('data warehouse', 'a database optimised for analysis over huge tables'), ('ETL', 'extract, transform, load — cleaning and moving data'), ('Parquet', 'a compressed, column-based file format for analytics')],
    diff=table(['', 'Data lake + serverless SQL', 'Data warehouse', 'Spark cluster'], [['Storage', 'object storage, open files', 'managed, internal format', 'reads lake files'], ['Best for', 'cheap, flexible ad-hoc queries', 'fast repeated BI queries', 'heavy transformations, ML'], ['Examples', 'Athena, BigQuery on GCS', 'Redshift, BigQuery, Fabric Warehouse', 'EMR, Dataproc, Databricks']], minw=600),
    where=['Business dashboards', 'Log and clickstream analysis', 'Feature preparation for machine learning'],
    realworld='Microsoft launched <b>Microsoft Fabric</b> (generally available in November 2023) as one SaaS analytics platform combining data engineering, warehousing, real-time analytics and Power BI on a single lake (OneLake) — a sign that analytics is moving from separate services to unified platforms.',
    pro='Google’s BigQuery separates storage and compute so completely that you can query petabytes without creating any cluster — you pay per TB scanned (or for reserved slots). Partitioning and clustering tables can cut both cost and time by 10× or more.')

def a_ai(k):
    o = t(180, 12, ['Ready-made AI APIs', 'Foundation models as a service', 'Build and train your own'][k], 9, 'ink', bold=True)
    o += box(14, 40, 90, 60, 'card', rx=8) + t(59, 66, 'your app', 7.6, 'ink') + arrow(106, 70, 136, 70)
    o += box(138, 34, 208, 72, ['blue', 'violet', 'amber'][k], rx=8)
    o += t(242, 56, ['Translate · Speech · Vision · OCR', 'Bedrock · Azure OpenAI · Vertex AI', 'SageMaker AI · Azure ML · Vertex AI'][k], 7.4, 'ink', bold=True)
    o += t(242, 76, ['one API call, no ML knowledge', 'prompt → text, image, code; pay per token', 'notebooks, training jobs, endpoints'][k], 6.8, 'ink')
    o += t(242, 94, ['e.g. menu photo → text', 'e.g. “write a Diwali offer”', 'e.g. delivery-time model'][k], 6.6, 'ink2')
    o += t(180, 136, ['fastest to use; least control', 'powerful general models; add your data with RAG', 'most control; needs data scientists and GPUs'][k], 7.2, 'ink', bold=True)
    return o
A_AI = cap([a_ai(k) for k in range(3)], [('AI APIs', 'Pre-trained services for speech, vision, translation and documents.', ''), ('Foundation models', 'Large generative models offered through an API, billed per token.', ''), ('ML platform', 'Tools to prepare data, train, tune, deploy and monitor your own models.', '')],
    'AI services in action', 'Three levels of AI in the cloud.', 'AI and ML', 'Animation: an app using ready-made AI APIs; then foundation models via an API; then a full ML platform for custom models.', 'p3anim')
T3 = vtype(3, 'AI and machine learning', 'violet',
    'Cloud <b>AI and ML services</b> come in three levels: <b>pre-trained AI APIs</b> (speech, vision, translation, document extraction), <b>generative AI / foundation-model services</b> that offer large language and image models through an API (Amazon Bedrock, Azure OpenAI in Microsoft Foundry, Vertex AI with Gemini), and <b>ML platforms</b> for building, training and deploying custom models (SageMaker AI, Azure Machine Learning, Vertex AI).',
    'Food options: buy a ready-made sweet (AI API), order a custom cake from a famous baker by describing it (foundation model), or bake your own in a rented commercial kitchen (ML platform).',
    'TiffinGo uses a document-extraction API to read supplier invoices, a foundation model through Bedrock to write menu descriptions in Hindi and Marathi, and SageMaker AI to train a delivery-time prediction model on two years of orders.',
    'AWS: Amazon Bedrock, SageMaker AI, Rekognition, Textract, Transcribe, Translate, Amazon Q; Azure: Microsoft Foundry (Azure OpenAI), Azure Machine Learning, Azure AI Vision/Speech/Language, Document Intelligence; Google: Vertex AI, Gemini, Document AI, Speech-to-Text, Vision AI.',
    '', A_AI,
    'you need language, vision or prediction features — start with the highest level that solves the problem.',
    'you train custom models when an API or a prompted foundation model already works — or send sensitive data without checking data-use and residency terms.',
    plain='Cloud services that add “intelligence” to apps — reading text in photos, translating, chatting, writing, or predicting things from your own data.',
    how=[('Pick the level', 'API → foundation model (+ your data) → custom model.'), ('Call the API', 'Send text/image/audio; get a result; pay per request, character or token.'), ('Ground with your data', 'Retrieval-augmented generation (RAG): search your documents and add them to the prompt.'), ('Train (if needed)', 'Managed notebooks and training jobs on GPUs; track experiments.'), ('Deploy and monitor', 'Endpoints, guardrails, evaluation, drift monitoring and cost limits.')],
    words=[('model', 'a program learned from data that makes predictions'), ('foundation model / LLM', 'a large model trained on huge data, usable for many tasks'), ('token', 'a piece of a word — the unit LLMs read and bill'), ('RAG', 'adding your own documents to a model’s prompt')],
    diff=table(['', 'AI APIs', 'Foundation models', 'ML platform'], [['Skill needed', 'developer', 'developer + prompting', 'data scientist'], ['Your data', 'input only', 'prompts + RAG, optional fine-tuning', 'full training data'], ['Billing', 'per call/unit', 'per token', 'compute hours (often GPUs)']], minw=540),
    where=['Chatbots and assistants', 'Document processing (invoices, KYC)', 'Forecasting, recommendations, fraud detection'],
    realworld='Product names in this family change fast: AWS renamed SageMaker to <b>SageMaker AI</b> (Dec 2024); Microsoft renamed Azure AI Foundry to <b>Microsoft Foundry</b> (Nov 2025); Google moved Cloud Functions-style names into Vertex AI and Gemini branding. Always check current names before an exam or interview.',
    pro='Most generative-AI cost is in <b>tokens</b>, and output tokens usually cost several times more than input tokens. Asking a model for short, structured answers (and caching repeated prompts) is often the biggest saving — bigger than switching providers.')

def a_sec(k):
    o = t(180, 12, ['Identity: who are you?', 'Authorisation: what may you do?', 'Detect and protect'][k], 9, 'ink', bold=True)
    o += box(14, 40, 80, 60, 'blue', rx=8) + t(54, 66, ['Riya', 'Riya', '?'][k], 8, 'ink', bold=True) + t(54, 84, ['password + MFA', 'role: developer', 'odd API calls'][k], 6.4, 'ink2')
    o += box(124, 34, 112, 72, 'red', rx=8) + t(180, 58, ['IAM / Entra ID', 'policy check', 'GuardDuty'][k], 7.6, 'ink', bold=True) + t(180, 76, ['verifies identity', 'allow s3:GetObject', 'Defender · SCC'][k], 6.8, 'ink2') + t(180, 92, ['issues a token', 'deny s3:DeleteBucket', 'raises a finding'][k], 6.6, 'ink2')
    o += box(266, 40, 80, 60, ['green', 'amber', 'red'][k], rx=8) + t(306, 66, ['signed in', 'read ✔ delete ✘', 'alert'][k], 7.4, 'ink', bold=True)
    o += arrow(96, 70, 122, 70) + arrow(238, 70, 264, 70)
    o += t(180, 134, ['strong sign-in: MFA, single sign-on, no root use', 'least privilege: only the permissions the job needs', 'encrypt with KMS; detect threats; audit everything'][k], 7.2, 'ink', bold=True)
    return o
A_SEC = cap([a_sec(k) for k in range(3)], [('Authenticate', 'Identity services verify who is calling (passwords, MFA, single sign-on).', ''), ('Authorise', 'Policies decide which actions on which resources are allowed.', ''), ('Protect and detect', 'Key management encrypts data; threat-detection services flag unusual behaviour.', '')],
    'Security services in action', 'Who you are, what you may do, what looks wrong.', 'Security', 'Animation: a user authenticates with MFA; policies allow reading but deny deleting; a threat detection service raises an alert.', 'p4anim')
T4 = vtype(4, 'Security, identity and compliance', 'red',
    '<b>Security and identity services</b> control and protect access to cloud resources: <b>identity and access management</b> (users, roles, policies, single sign-on — IAM, Microsoft Entra ID, Cloud IAM), <b>key and secret management</b> (KMS, Key Vault, Secret Manager), <b>threat detection and posture management</b> (GuardDuty, Security Hub, Defender for Cloud, Security Command Center), and network/application protection (WAF, DDoS).',
    'A hotel: the reception checks your ID (authentication), your key card opens only your room and the gym (authorisation), the safe in the room has its own key (KMS), and CCTV flags anyone trying every door (threat detection).',
    'TiffinGo staff sign in through IAM Identity Center with MFA; developers get read-only access to production; payment card tokens are encrypted with a KMS key; GuardDuty alerted when an old access key was used from an unknown country.',
    'AWS IAM, IAM Identity Center, Cognito, KMS, Secrets Manager, GuardDuty, Security Hub, Inspector, Macie, WAF, Shield; Microsoft Entra ID, Azure RBAC, Key Vault, Defender for Cloud, Sentinel; Google Cloud IAM, Identity Platform, Cloud KMS, Secret Manager, Security Command Center.',
    'Module 9 (Cloud security) covers this family in depth.', A_SEC,
    'always — identity is the new perimeter in the cloud; every other control depends on it.',
    'you share root/owner credentials, use long-lived access keys on laptops, or grant “*” permissions to make an error go away.',
    plain='Services that check who you are, decide what you are allowed to do, lock data with keys, and raise an alarm when something looks suspicious.',
    how=[('Identities', 'Users, groups, roles, service accounts / managed identities.'), ('Authenticate', 'Passwords + MFA, SSO federation, short-lived tokens.'), ('Authorise', 'JSON policies or role assignments evaluated on every API call (default deny).'), ('Encrypt', 'KMS keys for data at rest; TLS in transit.'), ('Detect and respond', 'Findings from logs and behaviour → alerts, automated fixes.')],
    words=[('authentication', 'proving who you are'), ('authorisation', 'deciding what you may do'), ('MFA', 'multi-factor authentication — e.g. password + phone code'), ('least privilege', 'only the permissions really needed')],
    diff=table(['', 'AWS', 'Azure', 'Google Cloud'], [['Workforce identity', 'IAM Identity Center', 'Microsoft Entra ID', 'Cloud Identity / Workspace'], ['Permissions model', 'IAM policies (JSON)', 'RBAC role assignments', 'IAM roles on resources'], ['Threat detection', 'GuardDuty, Security Hub', 'Defender for Cloud, Sentinel', 'Security Command Center']], minw=560),
    where=['Every account and every application', 'Compliance (PCI DSS, RBI, DPDP Act)', 'Incident detection and response'],
    realworld='<b>Microsoft Entra ID</b> is the 2023 new name of Azure Active Directory — the same identity service behind Microsoft 365 sign-ins. Exams and job descriptions still use both names.',
    pro='In AWS an explicit <b>Deny</b> anywhere (identity policy, resource policy, permission boundary, SCP) beats any number of Allows — that is how organisations put guardrails that even account administrators cannot remove.')

def a_mgmt(k):
    o = t(180, 12, ['Metrics and logs', 'Audit: who did what', 'Policy and cost guardrails'][k], 9, 'ink', bold=True)
    for i in range(3): o += box(14, 30 + i * 32, 90, 26, 'card', rx=4) + t(59, 47 + i * 32, ['VMs', 'database', 'functions'][i], 7, 'ink')
    o += box(132, 34, 110, 90, 'amber', rx=8) + t(187, 56, ['CloudWatch', 'CloudTrail', 'Organizations'][k], 7.8, 'ink', bold=True) + t(187, 74, ['Azure Monitor', 'Activity Log', 'Azure Policy'][k], 6.8, 'ink2') + t(187, 90, ['Cloud Monitoring', 'Audit Logs', 'Org Policy'][k], 6.8, 'ink2')
    for i in range(3): o += arrow(106, 43 + i * 32, 130, 70)
    o += box(266, 44, 80, 60, ['green', 'violet', 'red'][k], rx=8) + t(306, 68, ['dashboard', '“Riya deleted', 'blocked:'][k], 7, 'ink', bold=True) + t(306, 84, ['+ alarm', 'bucket at 3 pm”', 'Region us-*'][k], 6.8, 'ink')
    o += arrow(244, 74, 264, 74)
    o += t(180, 146, ['numbers and logs from every service in one place', 'every API call recorded — for security and debugging', 'rules applied to all accounts: Regions, tags, budgets'][k], 7.2, 'ink', bold=True)
    return o
A_MGMT = cap([a_mgmt(k) for k in range(3)], [('Observe', 'Metrics, logs and traces from all services flow into monitoring.', ''), ('Audit', 'Every API call is recorded with who, what, when and from where.', ''), ('Govern', 'Organisation-wide policies, budgets and tags keep many accounts under control.', '')],
    'Management and governance in action', 'Watch, record and control everything.', 'Management', 'Animation: services send metrics and logs to monitoring; API calls are audited; organisation policies block disallowed actions.', 'p5anim')
T5 = vtype(5, 'Management, monitoring and governance', 'amber',
    '<b>Management and governance services</b> observe and control cloud environments: <b>monitoring</b> of metrics, logs and traces with alarms (CloudWatch, Azure Monitor, Cloud Monitoring/Logging), <b>audit logs</b> of every API call (CloudTrail, Activity Log, Cloud Audit Logs), <b>configuration and policy</b> enforcement (AWS Config, Organizations SCPs, Azure Policy, Organization Policy), resource organisation and <b>cost management</b>.',
    'A building’s control room: CCTV and meters (monitoring), the visitor register (audit log), and the society rules notice board that the guard enforces (policy).',
    'TiffinGo’s CloudWatch dashboard shows orders per minute and errors; an alarm pages the on-call engineer (Lesson 5.4). CloudTrail showed who changed a security group the night of the incident. An Organizations policy blocks all Regions except Mumbai and Hyderabad.',
    'Amazon CloudWatch, AWS CloudTrail, AWS Config, AWS Organizations, Control Tower, Systems Manager, Trusted Advisor, Cost Explorer; Azure Monitor, Log Analytics, Activity Log, Azure Policy, Management Groups, Azure Arc, Advisor, Cost Management; Google Cloud Monitoring, Logging, Audit Logs, Resource Manager, Organization Policy, Recommender.',
    '', A_MGMT,
    'from day one — you cannot fix what you cannot see, and audits need a record of changes.',
    'logs are collected but never looked at, or log retention is so long that the logging bill exceeds the app bill.',
    plain='Tools that show how everything is running, record every change people make, and enforce company rules across all cloud accounts.',
    how=[('Collect', 'Services publish metrics automatically; agents add OS metrics and app logs.'), ('Visualise and alert', 'Dashboards and alarms on thresholds or anomalies.'), ('Audit', 'Control-plane API calls logged by default (90 days in CloudTrail event history).'), ('Evaluate', 'Config rules / Azure Policy check resources continuously.'), ('Enforce', 'Organisation-level guardrails (SCPs, policies) and budgets.')],
    words=[('metric', 'a number over time, e.g. CPU %'), ('log', 'a text record of an event'), ('trace', 'the path of one request through many services'), ('guardrail', 'a rule that prevents a risky action')],
    diff=table(['', 'Monitoring', 'Audit log', 'Policy'], [['Answers', 'is it healthy?', 'who changed what?', 'is it allowed?'], ['AWS', 'CloudWatch', 'CloudTrail', 'Config, SCPs'], ['Azure', 'Azure Monitor', 'Activity Log', 'Azure Policy'], ['Google Cloud', 'Cloud Monitoring/Logging', 'Cloud Audit Logs', 'Organization Policy']], minw=520),
    where=['Operations dashboards and on-call alerting', 'Security investigations and compliance audits', 'Multi-account governance'],
    realworld='<b>Azure Arc</b> extends Azure Monitor, Policy and management to servers and Kubernetes clusters running on-premises or in other clouds — Microsoft’s way of letting one control plane govern a hybrid, multi-cloud estate.',
    pro='CloudTrail records management (control-plane) events by default, but <b>data events</b> such as S3 GetObject or Lambda invocations are off by default because of their volume and cost — a forensic investigation often finds the one log it needed was never enabled.')

def a_dev(k):
    o = t(180, 12, ['Infrastructure as code', 'CI/CD pipeline', 'Same environment, every time'][k], 9, 'ink', bold=True)
    o += box(14, 34, 96, 80, 'amber', rx=8) + t(62, 54, ['template.yaml', 'git push', 'template'][k], 7.4, 'ink', bold=True, mono=True) + t(62, 72, ['VPC, ALB, ASG,', 'build → test →', 'run 3 times'][k], 6.4, 'ink') + t(62, 86, ['DB as code', 'deploy', ''][k], 6.4, 'ink')
    o += arrow(112, 74, 140, 74)
    if k < 2:
        o += box(142, 34, 204, 80, 'card', rx=8)
        for i, n in enumerate((['VPC', 'ALB', 'ASG', 'RDS'] if k == 0 else ['build', 'test', 'staging', 'prod'])): o += box(150 + i * 49, 54, 44, 40, 'green', rx=4) + t(172 + i * 49, 78, n, 6.6, 'ink')
    else:
        for i, n in enumerate(['dev', 'test', 'prod']): o += box(150 + i * 66, 44, 60, 56, 'blue', rx=6) + t(180 + i * 66, 76, n, 7.4, 'ink', bold=True)
    o += t(180, 140, ['the whole environment is written in a file and versioned in git', 'every change is built, tested and deployed automatically', 'identical dev, test and prod — no “works on my machine”'][k], 7.2, 'ink', bold=True)
    return o
A_DEV = cap([a_dev(k) for k in range(3)], [('IaC', 'Infrastructure is described in templates stored in git.', ''), ('Pipeline', 'Each commit is built, tested and deployed through stages automatically.', ''), ('Repeatable', 'The same template creates identical environments.', '')],
    'DevOps and IaC in action', 'Environments and releases from code.', 'DevOps', 'Animation: a template creates VPC, load balancer, auto scaling group and database; a pipeline builds, tests and deploys; identical dev, test and prod environments.', 'p6anim')
T6 = vtype(6, 'DevOps tools and infrastructure as code', 'amber',
    '<b>Infrastructure as code (IaC)</b> services create and update cloud resources from declarative templates kept in version control (CloudFormation/CDK, ARM/Bicep, Google Infrastructure Manager, and the cross-cloud Terraform/OpenTofu), while <b>DevOps services</b> automate building, testing and releasing software through pipelines (CodePipeline/CodeBuild, Azure DevOps, GitHub Actions, Cloud Build/Cloud Deploy).',
    'A recipe card instead of “cook from memory”: anyone can make the same dal every time, changes are written down, and a new kitchen can be set up from the same card.',
    'TiffinGo writes its VPC, load balancer, Auto Scaling group and database in a CloudFormation template; every git push runs tests and deploys to staging, and a manager approves production. A new “TiffinGo Bengaluru” environment takes 20 minutes, not two weeks.',
    'AWS CloudFormation, CDK, CodePipeline, CodeBuild, CodeDeploy; Azure Resource Manager templates, Bicep, Azure DevOps, GitHub Actions; Google Infrastructure Manager (Terraform), Cloud Build, Cloud Deploy, Artifact Registry; Terraform/OpenTofu, Pulumi.',
    'Module 8 (Operating the cloud) covers monitoring, automation and IaC further.', A_DEV,
    'more than one environment exists, more than one person changes infrastructure, or you need audits of changes.',
    'you click changes in the console on IaC-managed resources — “drift” makes the template lie.',
    plain='Writing your servers, networks and databases as a text file, so a tool can build them exactly the same way every time — and automating how new app versions go live.',
    how=[('Write', 'Declare resources and their settings in YAML/JSON/HCL/code.'), ('Plan', 'The tool computes the difference between the file and reality (change set / plan / what-if).'), ('Apply', 'It creates/updates/deletes resources in the right order.'), ('Version', 'Templates live in git; changes go through reviews.'), ('Pipeline', 'CI builds and tests code; CD deploys it through stages with approvals.')],
    words=[('IaC', 'infrastructure as code'), ('declarative', 'you describe the end state, the tool works out the steps'), ('drift', 'real resources differing from the template'), ('CI/CD', 'continuous integration / continuous delivery')],
    diff=table(['', 'CloudFormation / Bicep / Infra Manager', 'Terraform / OpenTofu'], [['Clouds', 'one provider', 'many providers'], ['State', 'kept by the provider', 'state file you store (e.g. S3, GCS)'], ['Language', 'YAML/JSON / Bicep', 'HCL']], minw=500),
    where=['Repeatable environments (dev/test/prod)', 'Disaster recovery (rebuild a Region from code)', 'Compliance: every change reviewed'],
    realworld='Google Cloud ended support for its own template tool, <b>Cloud Deployment Manager</b>, on 31 March 2026 (shutdown after June 2027) and recommends <b>Infrastructure Manager</b>, which runs Terraform — a sign of how Terraform became the common IaC language.',
    pro='In 2023 HashiCorp changed Terraform’s licence from open source (MPL) to the Business Source License; the community fork <b>OpenTofu</b> joined the Linux Foundation. Companies now choose between them — same HCL language, different licences.')

def a_int(k):
    o = t(180, 12, ['Queue: one consumer per message', 'Topic: fan-out to many', 'Events: route by content'][k], 9, 'ink', bold=True)
    o += box(14, 46, 80, 50, 'blue', rx=6) + t(54, 68, 'order', 7.6, 'ink', bold=True) + t(54, 84, 'service', 7, 'ink')
    o += box(120, 40, 100, 62, 'violet', rx=8) + t(170, 64, ['SQS queue', 'SNS topic', 'EventBridge'][k], 7.6, 'ink', bold=True) + t(170, 82, ['msgs wait', 'publish once', 'rules'][k], 6.8, 'ink2')
    o += arrow(96, 71, 118, 71)
    targets = [['kitchen worker'], ['kitchen', 'delivery', 'SMS'], ['Diwali → offers', 'payment → audit']][k]
    for i, n in enumerate(targets):
        y = 71 - (len(targets) - 1) * 18 + i * 36
        o += box(250, y - 14, 96, 28, 'green', rx=5) + t(298, y + 4, n, 6.8, 'ink') + arrow(222, 71, 248, y)
    o += t(180, 140, ['decouples: if the kitchen app is down, orders wait safely', 'one event, many independent subscribers', 'rules send each event type to the right targets'][k], 7.2, 'ink', bold=True)
    return o
A_INT = cap([a_int(k) for k in range(3)], [('Queue', 'Producers put messages in a queue; a consumer takes each one when ready.', ''), ('Topic', 'A message published to a topic is pushed to every subscriber.', ''), ('Event bus', 'Rules match events by content and route them to different targets.', '')],
    'Integration services in action', 'Parts that talk without waiting for each other.', 'Integration', 'Animation: a queue holding orders for a kitchen worker; a topic fanning out to kitchen, delivery and SMS; an event bus routing by rules.', 'p7anim')
T7 = vtype(7, 'Application integration (messaging, events, APIs)', 'violet',
    '<b>Application integration services</b> let independent components communicate reliably: <b>message queues</b> (SQS, Service Bus queues, Pub/Sub pull), <b>publish/subscribe topics</b> (SNS, Service Bus topics, Pub/Sub), <b>event buses</b> (EventBridge, Event Grid, Eventarc), <b>API gateways</b> (API Gateway, API Management, Apigee) and <b>workflow orchestration</b> (Step Functions, Logic Apps, Workflows).',
    'The kitchen order spike at a dhaba: waiters pin order slips on a rail (queue); the cook takes the next slip when free. Nobody shouts across the room and no order is lost in the rush.',
    'TiffinGo’s order service publishes “OrderPlaced” to a topic; the kitchen, delivery-partner and SMS services each get their own copy through queues. During the Diwali rush the kitchen queue grows to 4,000 messages and drains over 10 minutes — nothing is lost and the app stays fast.',
    'Amazon SQS, SNS, EventBridge, API Gateway, Step Functions, MQ, AppSync; Azure Service Bus, Event Grid, Storage Queues, API Management, Logic Apps; Google Pub/Sub, Eventarc, Cloud Tasks, Apigee, API Gateway, Workflows.',
    '', A_INT,
    'components should not wait for each other, traffic is spiky, or one event must reach several systems.',
    'a simple synchronous call is enough and you add queues “just in case” — every hop adds latency and things to monitor.',
    plain='Services that pass messages between parts of an app, so each part can work at its own speed and nothing is lost if one part is slow or down.',
    how=[('Produce', 'A service sends a message/event (JSON) to a queue, topic or bus.'), ('Store durably', 'The service keeps it replicated until delivered.'), ('Deliver', 'Consumers poll (queue) or receive pushes (topic/bus).'), ('Acknowledge', 'Consumers delete/ack after processing; otherwise it reappears (visibility timeout).'), ('Handle failures', 'Retries, then a dead-letter queue for messages that keep failing.')],
    words=[('message', 'a small piece of data sent between services'), ('decouple', 'make parts independent of each other'), ('pub/sub', 'publish once, every subscriber receives it'), ('dead-letter queue', 'a parking place for messages that keep failing')],
    diff=table(['', 'Queue', 'Topic (pub/sub)', 'Event bus'], [['Receivers per message', 'one', 'all subscribers', 'those whose rules match'], ['Delivery', 'pull', 'push', 'push by rule'], ['AWS · Azure · GCP', 'SQS · Service Bus queue · Pub/Sub pull', 'SNS · Service Bus topic · Pub/Sub', 'EventBridge · Event Grid · Eventarc']], minw=600),
    where=['Order processing and spikes', 'Microservice communication', 'Workflows (KYC, refunds) and API front doors'],
    realworld='<b>Amazon SQS</b> was the first AWS service ever offered (a public beta in 2004, before S3 and EC2); Amazon’s own retail site was built around such message queues long before “microservices” had a name.',
    pro='Standard SQS queues deliver <b>at least once</b> and not always in order; FIFO queues give ordering and exactly-once processing within a limit of throughput. Consumers must therefore be <b>idempotent</b> — processing the same order message twice must not create two tiffins.')

SUMMARY = table(['#', 'Family', 'Question it answers', 'AWS flagship', 'Azure flagship', 'Google flagship'], [
    ['1', 'Databases', 'where does structured data live?', 'RDS/Aurora, DynamoDB', 'Azure SQL, Cosmos DB', 'Cloud SQL, Firestore, Spanner'], ['2', 'Analytics', 'what does the data tell us?', 'Athena, EMR, Redshift', 'Fabric, Databricks', 'BigQuery, Dataproc'],
    ['3', 'AI & ML', 'can the app understand / predict?', 'Bedrock, SageMaker AI', 'Microsoft Foundry, Azure ML', 'Vertex AI, Gemini'], ['4', 'Security & identity', 'who may do what?', 'IAM, KMS, GuardDuty', 'Entra ID, Key Vault, Defender', 'Cloud IAM, KMS, SCC'],
    ['5', 'Management', 'is it healthy, who changed it, is it allowed?', 'CloudWatch, CloudTrail, Organizations', 'Monitor, Activity Log, Policy', 'Monitoring, Audit Logs, Org Policy'], ['6', 'DevOps & IaC', 'how do we build and release safely?', 'CloudFormation, CodePipeline', 'Bicep, Azure DevOps', 'Infra Manager, Cloud Build'],
    ['7', 'Integration', 'how do parts talk?', 'SQS, SNS, EventBridge, API GW', 'Service Bus, Event Grid, APIM', 'Pub/Sub, Eventarc, Apigee']], minw=760)
CHECK = ('  <h3>Check yourself: which family?</h3>\n' +
    qx('A. Find out who deleted a production bucket last night.', ['Monitoring metrics', 'Audit logs (CloudTrail / Activity Log)', 'CDN', 'Queue'], 1, 'Management family — audit.') +
    qx('B. Absorb an order spike without losing orders when the kitchen app is slow.', ['A message queue', 'A bigger VM', 'A data warehouse', 'KMS'], 0, 'Integration family.') +
    qx('C. Ask “top 10 dishes per city last year” over 2 TB of order files.', ['Relational OLTP database', 'Serverless SQL / warehouse (Athena, BigQuery, Fabric)', 'Redis cache', 'SNS'], 1, 'Analytics family.') +
    qx('D. Read text from photos of supplier invoices.', ['Train a model from scratch', 'Document AI / Textract / Document Intelligence', 'DynamoDB', 'VPN'], 1, 'AI APIs first.'))

TYPES = ('  <p>Seven more product families, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why must an SQS consumer be idempotent?', 'Why might the CloudTrail log you need for an investigation not exist?', 'Why do output tokens usually dominate a generative-AI bill?'], 'types 7, 5 and 3') + MAP
         + jump(['Databases', 'Analytics', 'AI & ML', 'Security', 'Management', 'DevOps & IaC', 'Integration']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Service family', 'A group of services that answer the same question.', 'Lets you read any architecture quickly.', 'The ten families above.'),
    ('Flagship service', 'The most used service in a family.', 'Learn these first; exams focus on them.', 'S3, EC2, RDS, Lambda, IAM, CloudWatch…'),
    ('Managed vs self-managed', 'Who runs the software.', 'Managed saves operations work; self-managed gives control.', 'RDS vs PostgreSQL on EC2.'),
    ('Serverless', 'No servers to size; scales and bills per use.', 'Fits spiky, event-driven work.', 'Lambda, DynamoDB, Athena, BigQuery, Cloud Run.'),
    ('Marketplace', 'Third-party software sold through the cloud bill.', 'Buy firewalls, databases, SaaS without new contracts.', 'AWS Marketplace, Azure Marketplace, Google Cloud Marketplace.'),
    ('Industry solutions', 'Reference architectures for sectors.', 'Faster, compliant designs.', 'Solutions libraries, Well-Architected, Cloud Adoption Framework, Architecture Center.')])

DEEP = ('  <h3>How to translate an architecture between clouds in five minutes</h3>\n  <ol><li>Label each box with its <b>family</b> (compute, database, integration…).</li><li>Find the matching service in the translation table above.</li><li>Check the <b>scope</b> differences (Google VPC is global; Azure needs resource groups; AWS subnets are per AZ).</li><li>Check identity: IAM roles ↔ managed identities ↔ service accounts.</li><li>Check pricing models (Lesson 5.5) — equivalent services rarely cost the same.</li></ol>\n'
    '  <h3>Service lifecycles: products appear, get renamed and retire</h3>\n' + table(['Change', 'When', 'What to use now'], [['AWS App Runner closed to new customers', '30 Apr 2026', 'Amazon ECS Express Mode'], ['AWS Snowball Edge / Snow devices no new orders', '2025', 'Data Transfer Terminal, DataSync'], ['Google Cloud Deployment Manager end of support', '31 Mar 2026', 'Infrastructure Manager (Terraform)'], ['Azure AI Foundry → Microsoft Foundry', 'Nov 2025', 'same service, new name'], ['Azure AD → Microsoft Entra ID', '2023', 'same service, new name'], ['Amazon SageMaker → SageMaker AI', 'Dec 2024', 'same service, new name']], minw=560) +
    '\n  <p>Before an interview or exam, check the provider’s “what’s new” pages: older practice questions often mention retired products.</p>\n'
    '  <h3>Where to discover services</h3>\n  <ul><li>AWS: the console’s [All services] menu and aws.amazon.com/products; Azure: [All services] in the portal and the Azure updates page; Google: the console’s navigation menu and the product overview page.</li><li>Architecture centres: AWS Architecture Center, Azure Architecture Center, Google Cloud Architecture Center — real reference designs by industry.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> ~200+ services grouped as Compute, Storage, Database, Networking & Content Delivery, Analytics, Machine Learning, Security, Identity & Compliance, Management & Governance, Developer Tools, Application Integration, IoT, Media, End User Computing, Migration & Transfer.</p>',
    '<p><b>Azure:</b> categories such as Compute, Containers, Databases, Analytics, AI + machine learning, Identity, Security, Management and governance, DevOps, Integration, Internet of Things, Hybrid + multicloud, Migration.</p>',
    '<p><b>Google Cloud:</b> Compute, Storage, Databases, Networking, Data analytics, AI and machine learning, Security, Management tools, Developer tools, Integration services, Hybrid and multicloud, Migration.</p>') + \
    cloud3([['Catalogue', 'aws.amazon.com/products', 'azure.microsoft.com/products', 'cloud.google.com/products'], ['Reference designs', 'AWS Architecture Center', 'Azure Architecture Center', 'Cloud Architecture Center'], ['Best-practice framework', 'AWS Well-Architected', 'Azure Well-Architected + CAF', 'Google Cloud Well-Architected Framework'], ['Comparison help', '—', 'AWS-to-Azure service comparison page', 'AWS/Azure to Google Cloud product mapping']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['Console Home', 'All services'], ['Recently visited', 'Favorites', 'All services', 'Applications'], 'All services',
       [('Search', 'queue'), ('Results', 'Simple Queue Service · Simple Notification Service · Amazon MQ'), ('Group by', '▾ Category: Application Integration')], 'Add to favorites'),
  mock('az', ['Home', 'All services'], ['All services', 'Favorites', 'Recent', 'Categories'], 'Categories',
       [('Filter services', 'queue'), ('Results', 'Service Bus · Storage accounts (Queues) · Event Grid'), ('Category', '▾ Integration')], 'Pin to sidebar'),
  mock('gcp', ['Navigation menu', 'View all products'], ['Pinned products', 'All products', 'Marketplace'], 'All products',
       [('Search', 'pub/sub'), ('Result', 'Pub/Sub — Integration Services'), ('APIs & Services', 'Cloud Pub/Sub API · Enabled')], 'Pin')),
 (mock('aws', ['Amazon SQS', 'Queues', 'Create queue'], ['Queues', 'Create queue'], 'Queues',
       [('Type', '( ) Standard'), ('Name', 'tiffingo-kitchen'), ('Visibility timeout', '30 seconds'), ('Dead-letter queue', '▾ Disabled (for this lab)')], 'Create queue'),
  mock('az', ['Home', 'tiffingo…', 'Queues', 'Add queue'], ['Containers', 'File shares', 'Queues', 'Tables'], 'Queues',
       [('Queue name', 'tiffingo-kitchen')], 'OK'),
  mock('gcp', ['Pub/Sub', 'Topics', 'Create topic'], ['Topics', 'Subscriptions', 'Snapshots', 'Schemas'], 'Topics',
       [('Topic ID', 'tiffingo-orders'), ('Add a default subscription', '[x] tiffingo-orders-sub')], 'Create')),
 (mock('aws', ['Resource Groups & Tag Editor', 'Tag Editor'], ['Saved Resource Groups', 'Create Resource Group', 'Tag Editor', 'Tag policies'], 'Tag Editor',
       [('Regions', '▾ ap-south-1'), ('Resource types', '▾ All supported resource types'), ('Tags', 'project = tiffingo')], 'Search resources'),
  mock('az', ['Home', 'All resources'], ['All resources', 'Resource groups', 'Resource Graph Explorer'], 'All resources',
       [('Filter', 'Resource group == rg-tiffingo'), ('Group by', '▾ Type')], 'Export to CSV'),
  mock('gcp', ['IAM & Admin', 'Asset Inventory'], ['IAM', 'Asset Inventory', 'Labels', 'Tags'], 'Asset Inventory',
       [('Scope', 'project tiffingo-lab'), ('Resource', 'Filter by resource type / location')], 'Search')),
])

STEP1 = ('1 · Explore the catalogue and enable a service', tri(
    (['Console top search bar → type <code>queue</code> → see SQS, SNS, MQ with one-line descriptions.', 'Click the ☆ next to [[Simple Queue Service]] to add it to [[Favorites]]; open [[All services]] and browse by category.', 'AWS services need no “enabling” — they are available in every account (some, like Bedrock models, need access requests).'],
     "aws ec2 describe-regions --query 'Regions[].RegionName' --output text | tr '\\t' '\\n' | head -5\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services \\\n  --query 'Parameters[].Value' --output text | tr '\\t' '\\n' | wc -l    # services offered in Mumbai",
     'a list of Regions and a count of services available in Mumbai (well over 200).'),
    (['Portal search bar → <code>queue</code> → [[Service Bus]], Storage queues, Event Grid.', '[[All services]] → [[Categories]] → [[Integration]]. Hover a service → ☆ [[Favorite]].', 'Many services need a <b>resource provider</b> registered in your subscription: [[Subscriptions]] → your subscription → [[Resource providers]] → <code>Microsoft.ServiceBus</code> → [[Register]].'],
     'az provider list --query "[?registrationState==\'Registered\'].namespace" --output tsv | head\naz provider register --namespace Microsoft.ServiceBus\naz provider show --namespace Microsoft.ServiceBus --query registrationState --output tsv',
     'registered providers, then <code>Registering</code> → <code>Registered</code> for Microsoft.ServiceBus.'),
    (['☰ [[Navigation menu]] → [[View all products]] → search <code>Pub/Sub</code> → pin it.', '[[APIs & Services]] → [[Library]] → search “Cloud Pub/Sub API” → [[Enable]].', 'Google Cloud requires each service’s API to be enabled per project before first use.'],
     'gcloud services list --enabled | head\ngcloud services enable pubsub.googleapis.com\ngcloud services list --available --filter="name:pubsub" --format="value(name)"',
     'enabled APIs, an “Operation … finished successfully” message, and <code>pubsub.googleapis.com</code>.')),
    'Three clouds, three habits: AWS services are on by default, Azure registers resource providers, Google enables APIs per project.')

STEP2 = ('2 · Decouple with a queue: send and receive an order', tri(
    (['[[Simple Queue Service]] → [[Create queue]] → [[Standard]], name <code>tiffingo-kitchen</code> → [[Create queue]].', 'Open it → [[Send and receive messages]] → body <code>{"order":101,"dish":"thali"}</code> → [[Send message]].', '[[Poll for messages]] → open the message → [[Delete]] (the consumer’s “done”).'],
     "Q=$(aws sqs create-queue --queue-name tiffingo-kitchen --query QueueUrl --output text)\naws sqs send-message --queue-url $Q --message-body '{\"order\":101,\"dish\":\"thali\"}'\nMSG=$(aws sqs receive-message --queue-url $Q --wait-time-seconds 5)\necho \"$MSG\"\nRH=$(echo \"$MSG\" | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"Messages\"][0][\"ReceiptHandle\"])')\naws sqs delete-message --queue-url $Q --receipt-handle \"$RH\"",
     'a MessageId after sending, the JSON body after receiving, and no output from delete. If you receive without deleting, the message reappears after the 30-second visibility timeout.'),
    (['Storage account from Lesson 6.2 (or create one) → [[Queues]] → [[+ Queue]] <code>tiffingo-kitchen</code>.', 'Open it → [[Add message]] → <code>{"order":101,"dish":"thali"}</code> → [[OK]].', '[[Dequeue message]] removes the oldest message (Service Bus offers the same with more features).'],
     'az storage queue create --account-name $SA --name tiffingo-kitchen --auth-mode key\naz storage message put --account-name $SA --queue-name tiffingo-kitchen --content \'{"order":101,"dish":"thali"}\' --auth-mode key\naz storage message get --account-name $SA --queue-name tiffingo-kitchen --auth-mode key --output json\n# delete with the id and popReceipt shown above:\n# az storage message delete --account-name $SA --queue-name tiffingo-kitchen --id ID --pop-receipt RECEIPT --auth-mode key',
     'the message with an <code>id</code> and <code>popReceipt</code>; until deleted it becomes visible again after 30 seconds.'),
    (['[[Pub/Sub]] → [[Topics]] → [[Create topic]] → ID <code>tiffingo-orders</code>, keep [[Add a default subscription]] → [[Create]].', 'Topic → [[Messages]] → [[Publish message]] → body <code>{"order":101,"dish":"thali"}</code> → [[Publish]].', 'Subscription → [[Messages]] → [[Pull]] → tick [[Enable ack messages]] → [[Ack]].'],
     'gcloud pubsub topics create tiffingo-orders\ngcloud pubsub subscriptions create tiffingo-kitchen --topic=tiffingo-orders\ngcloud pubsub topics publish tiffingo-orders --message=\'{"order":101,"dish":"thali"}\'\ngcloud pubsub subscriptions pull tiffingo-kitchen --auto-ack --limit=1',
     'a <code>messageIds</code> line after publishing and a table with the DATA after pulling. Add a second subscription and publish again — both get a copy (pub/sub fan-out).')),
    'The producer never waits for the consumer — that is what keeps the app fast during Diwali.')

STEP3 = ('3 · List everything you own (and tag it)', tri(
    (['[[Resource Groups & Tag Editor]] → [[Tag Editor]] → Region ap-south-1, all resource types → [[Search resources]].', 'Select the queue → [[Manage tags of selected resources]] → add <code>project = tiffingo</code> → [[Save changes]].', 'Search again with tag <code>project = tiffingo</code>.'],
     "aws sqs tag-queue --queue-url $Q --tags project=tiffingo\naws resourcegroupstaggingapi get-resources --tag-filters Key=project,Values=tiffingo \\\n  --query 'ResourceTagMappingList[].ResourceARN' --output text",
     'the ARN of the queue (and anything else you tagged).'),
    (['[[All resources]] → filter by resource group <code>rg-tiffingo</code> → group by type.', 'Select the storage account → [[Tags]] → <code>project : tiffingo</code> → [[Apply]].', '[[Resource Graph Explorer]] lets you query all resources with KQL.'],
     'az resource list --resource-group rg-tiffingo --query "[].[type,name]" --output table\naz tag update --resource-id $(az storage account show --name $SA --query id --output tsv) --operation Merge --tags project=tiffingo\naz resource list --tag project=tiffingo --query "[].name" --output tsv',
     'every resource in the group, then just the tagged ones.'),
    (['[[IAM & Admin]] → [[Asset Inventory]] → [[Resource]] tab — every resource in the project.', 'Add a label to the topic: Pub/Sub → topic → [[Labels]] → <code>project: tiffingo</code>.'],
     'P=$(gcloud config get-value project)\ngcloud services enable cloudasset.googleapis.com\ngcloud pubsub topics update tiffingo-orders --update-labels=project=tiffingo\ngcloud asset search-all-resources --scope=projects/$P --query="labels.project:tiffingo" --format="value(name)"',
     'the topic’s full resource name. (Asset search can take a few minutes to see new resources.)')),
    'Tags/labels are how companies find owners, split bills by team and clean up forgotten resources.')

prac = practical(OWN_INTRO + ' These steps use free-tier-level messaging and catalogue/inventory APIs — no VMs.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> [[SQS]] → select <code>tiffingo-kitchen</code> → [[Delete]]. CLI: <code>aws sqs delete-queue --queue-url $Q</code>.<br>'
            '<b>Azure:</b> delete the queue, or the whole resource group: <code>az storage queue delete --account-name $SA --name tiffingo-kitchen --auth-mode key</code> / <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud pubsub subscriptions delete tiffingo-kitchen; gcloud pubsub topics delete tiffingo-orders</code> (also delete any default <code>tiffingo-orders-sub</code> created in the console).'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Trying to memorise all 200+ services.', 'Exam anxiety.', 'Learn the families and 1–2 flagships each; look up the rest.'],
    ['Picking a service by name similarity across clouds.', 'Names mislead (Azure Functions vs Cloud Run functions vs Lambda are close; Cosmos DB ≠ DynamoDB exactly).', 'Compare features, limits and pricing, not names.'],
    ['Using a database where a queue was needed (polling tables).', 'Familiar tools.', 'Use queues/topics for work hand-off and events.'],
    ['Studying from old practice tests.', 'Retired or renamed products.', 'Check the lifecycle table and providers’ “what’s new”.'],
    ['No tags.', '“We’ll add them later.”', 'Tag every resource with project/owner/env from day one; enforce with policy.'],
    ['Self-managing what a managed service does.', 'Habit or fear of lock-in.', 'Prefer managed unless a clear need (control, cost at scale, portability) says otherwise.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud products and solutions; big data and analytics services in the cloud.'], ['AWS CLF-C02', 'Identify the right service for a use case across compute, storage, database, networking, analytics, ML, security, management, integration and developer tools.'], ['AZ-900', 'Core Azure services and solutions: databases, analytics, AI, IoT, identity (Entra ID), monitoring, governance (Policy, Arc), IaC (ARM/Bicep).'], ['Google Cloud Digital Leader', 'Google Cloud products for data, AI, infrastructure modernisation, security and operations.']], minw=560) + \
    qx('1. Which AWS service is a fully managed NoSQL key-value database?', ['Amazon RDS', 'Amazon DynamoDB', 'Amazon Redshift', 'Amazon EMR'], 1, 'DynamoDB.') + \
    qx('2. Which AWS service records API calls for auditing?', ['Amazon CloudWatch', 'AWS CloudTrail', 'AWS Config', 'Amazon Inspector'], 1, 'CloudTrail.') + \
    qx('3. Which service decouples components with a message queue?', ['Amazon SQS', 'Amazon S3', 'Amazon Route 53', 'AWS KMS'], 0, 'SQS.') + \
    qx('4. Which Azure service provides identity and access management (formerly Azure AD)?', ['Azure Key Vault', 'Microsoft Entra ID', 'Azure Policy', 'Azure Monitor'], 1, 'Entra ID.') + \
    qx('5. Which Google Cloud service is a serverless data warehouse?', ['Cloud SQL', 'BigQuery', 'Bigtable', 'Filestore'], 1, 'BigQuery.') + \
    qx('6. Which AWS service lets you build generative-AI apps using foundation models through an API?', ['Amazon Bedrock', 'Amazon Polly', 'AWS Glue', 'Amazon Lex only'], 0, 'Bedrock.')

proj = miniproject('Mini project: translate TiffinGo’s architecture to three clouds',
    'Prove you can read and translate any cloud diagram.',
    ['<b>Draw</b> TiffinGo’s order flow (the eight services in “How it works”).',
     '<b>Label</b> each box with its family.',
     '<b>Translate</b> it to Azure and Google Cloud using the translation table; note one real difference per box.',
     '<b>Check lifecycles:</b> make sure none of your choices is retired or renamed.',
     '<b>Prove one link:</b> on your own account, send and receive an order message through a queue/topic (step 2) and tag it (step 3).',
     '<b>Present</b> it as a three-column table (AWS · Azure · Google Cloud) with a one-line reason per choice.'],
    'A three-cloud architecture table and a working queue demo (then deleted).', 'Lessons 6.1–6.4 + 5.5 (pricing).')

assemble_v2(HERE, story_h2='Nine service names in one diagram', hook_html=hk,
    narration='An investor’s advisor sent TiffinGo an architecture full of service names the team had never heard of. The fix was not to memorise names — it was to learn the map.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud products and solutions',
    formal='Cloud providers offer hundreds of <b>products</b> organised into <b>families</b> — compute, storage, networking, databases, analytics, AI/ML, security and identity, management and governance, developer tools, integration, IoT and more — which customers combine, often with Marketplace software and reference architectures, into <b>solutions</b> for business and industry problems.',
    simple='The cloud’s menu card: hundreds of services grouped into a dozen sections. Learn the sections and the main dish in each, and you can understand any cloud design.',
    interview=['“I group cloud services into families — compute, storage, networking, databases, analytics, AI, security, management, DevOps and integration — and know the flagship in each for AWS, Azure and Google Cloud.”', '“For a new requirement I ask which family, then prefer the most managed service that fits, and check limits and pricing.”'],
    terms_rows=[('Service family', 'Group answering one question.'), ('Flagship', 'Most used service in a family.'), ('Managed service', 'Provider runs it.'), ('Serverless', 'No servers to size; per-use billing.'), ('Data lake', 'Raw data in object storage.'), ('Foundation model', 'Large general AI model via API.'), ('IaC', 'Infrastructure as code.'), ('Message queue', 'Hand-off buffer between services.'), ('Audit log', 'Record of API calls.'), ('Marketplace', 'Third-party software via the cloud bill.')],
    exam='CLF-C02 has many “which service fits this use case?” questions; AZ-900 tests core services and Entra ID/Policy/Arc; Digital Leader tests data, AI and modernisation products.',
    picture_h2='The product map, and the translation table', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven product families, one by one', TYPES)],
    how_h2='One order, eight cloud services', how_intro='How families work together in a real app.', how_anim=FLOW,
    parts_h2='Six words for reading any product page', parts_html=parts, lv='',
    myth_rows=[('You must know every service.', 'Know the families and flagships.', 'The map.'), ('Same name = same service.', 'Compare features and limits.', 'Translation table.'), ('Products never change.', 'They are renamed and retired regularly.', 'Deep dive lifecycle table.')],
    extra_secs=[('deep', 'Deep dive', 'Translating architectures, product lifecycles and where to discover services', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Group cloud services into families and name the flagships in AWS, Azure and Google Cloud.', 'Translate an architecture from one cloud to another.', 'Explain databases, analytics, AI, security, management, DevOps and integration services at a high level.', 'Spot retired or renamed products in older material.', 'Use the catalogue, a queue/topic and resource inventory on your own account (console and CLI).'],
    next_html='Module 7 — <a href="../../07-cloud-architecture/01-cloud-architecture-and-infrastructure/">7.1 Cloud architecture and infrastructure</a>.',
    pre='<b>Before you start:</b> <a href="../01-compute-products-and-services/">6.1</a>, <a href="../02-storage-systems-in-the-cloud/">6.2</a> and <a href="../03-cloud-networking/">6.3</a>.')
