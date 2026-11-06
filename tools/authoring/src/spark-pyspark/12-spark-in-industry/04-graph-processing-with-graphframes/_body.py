import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l124_graph.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Asha referred Ravi and Meera; both referred Kabir; Kabir referred Zoya, who referred Asha back. Who is the most influential customer, and which referral groups never touch each other?',
    'That is a <b>graph</b> question, and tables answer it badly. <b>GraphFrames</b> keeps vertices and edges as DataFrames and adds graph algorithms. In our lab <b>PageRank</b> ranked Zoya first (1.799), <b>connected components</b> split 9 customers into 3 communities, a <b>motif</b> query found every two-step referral chain, and <b>shortest paths</b> showed Zoya is 3 hops from Kabir while four customers cannot reach him at all.',
    ['Graphs as two DataFrames: vertices and edges.',
     'Degrees, PageRank, connected components, shortest paths.',
     'Motif finding: pattern queries on a graph.'])
cmap = concept_map('Concept map. Beginner: nodes and edges, examples. Intermediate: GraphFrame, degrees, PageRank, connected components. Advanced: motifs, shortest paths, GraphX vs GraphFrames, checkpoints, scale.',
    [[('df', 'DataFrames', 'Module 4', B + '04-dataframes/01-sparksession-and-dataframes/'), ('jn', 'Joins', 'Lesson 6.2', B + '06-transformations/02-joins/')],
     [('gf', 'GraphFrame', 'vertices + edges', None), ('dg', 'Degrees', 'in / out', None), ('pr', 'PageRank', 'influence', None), ('cc', 'Components', 'communities', None)],
     [('mo', 'Motifs', '(a)-[]->(b)', None), ('sp', 'Shortest paths', 'hops', None), ('gx', 'GraphX', 'Scala only', None), ('ck', 'Checkpoints', 'Lesson 3.3', B + '03-persistence-and-shared-variables/03-checkpointing-and-fault-tolerance/')]],
    [('df', 'gf'), ('jn', 'mo'), ('gf', 'dg'), ('gf', 'pr'), ('gf', 'cc'), ('gf', 'mo'), ('gf', 'sp'), ('gf', 'gx'), ('cc', 'ck')],
    {'gf', 'dg', 'pr', 'cc', 'mo', 'sp', 'gx'},
    '<b>Builds on:</b> <a href="../../06-transformations/02-joins/">6.2 Joins</a>. <b>Next:</b> <a href="../../13-capstone/01-problem-and-dataset/">Capstone</a>.')
whw = why_how_where(
    'Relationships (who refers whom, which accounts share a device, how places connect) are hard with joins alone: “3 hops away” means 3 self-joins, and influence needs iterative algorithms.',
    'A GraphFrame wraps a vertices DataFrame (column <code>id</code>) and an edges DataFrame (<code>src</code>, <code>dst</code>). Algorithms run as iterative DataFrame jobs (or GraphX underneath): PageRank, connected components (needs a checkpoint directory), shortest paths, label propagation, and motif queries that compile to joins.',
    'Referral and influencer analysis, fraud rings (shared cards, devices, addresses), recommendation graphs, network and route analysis, knowledge graphs.',
    'GraphFrames is a separate package (jar + Python), not part of Apache Spark; GraphX is Scala-only. Very large or real-time graph traversals may fit a graph database better.')

V = {'asha': (40, 40), 'ravi': (110, 20), 'meera': (110, 70), 'kabir': (180, 45), 'zoya': (110, 110), 'arjun': (250, 25), 'neha': (300, 55), 'om': (340, 90), 'tara': (260, 110)}
E = [('asha', 'ravi'), ('asha', 'meera'), ('ravi', 'kabir'), ('meera', 'kabir'), ('kabir', 'zoya'), ('zoya', 'asha'), ('arjun', 'neha'), ('neha', 'om')]
def graph(hl=None):
    o = ''.join(arrow(V[a][0], V[a][1], V[b][0], V[b][1]) for a, b in E)
    comp = {'asha': 'blue', 'ravi': 'blue', 'meera': 'blue', 'kabir': 'blue', 'zoya': 'blue', 'arjun': 'green', 'neha': 'green', 'om': 'green', 'tara': 'violet'}
    for n, (x, y) in V.items():
        o += box(x - 20, y - 9, 40, 18, 'acc' if hl and n in hl else comp[n], rx=9) + t(x, y + 3, n, 6.8, bold=True)
    return o
scene_svg = scene('The referral graph: asha refers ravi and meera, both refer kabir, kabir refers zoya, zoya refers asha; a second group arjun to neha to om; tara alone. Colours show the three connected components.', graph(),
                  'Nine customers, three <tspan font-weight="700" class="s-acc">communities</tspan>.')
dialogue = '''K> Sir, marketing wants to reward our top referrers. I counted referrals per customer with groupBy. Asha wins with 2.
A> Counting is degree. Influence is different: a referral from someone who is themselves often referred counts more. That is PageRank.
R> And “which groups of customers are linked at all”?
A> Connected components. Let’s load the referrals as a graph and ask all of it.'''

lv = '''
LEVELS> Graphs at three levels
L1> A map of who knows whom
      <ul>
        <li>People are dots, referrals are arrows. Count arrows (degree), follow arrows (paths), find islands (components), and see who many important people point to (PageRank).</li>
      </ul>
L2> The API
      <ul>
        <li><code>GraphFrame(vertices, edges)</code> with <code>id</code> and <code>src</code>/<code>dst</code> columns; <code>g.inDegrees</code>, <code>g.outDegrees</code>, <code>g.degrees</code>.</li>
        <li><code>g.pageRank(resetProbability=0.15, maxIter=10)</code>; <code>g.connectedComponents()</code> (set <code>sc.setCheckpointDir</code>); <code>g.shortestPaths(landmarks=[…])</code>; <code>g.labelPropagation(maxIter)</code>; <code>g.bfs(from, to)</code>.</li>
        <li>Motifs: <code>g.find("(a)-[e]->(b); (b)-[]->(c)")</code> returns a DataFrame you can filter like any other.</li>
      </ul>
L3> Setup and scale
      <ul>
        <li>Spark 4 package: <code>io.graphframes:graphframes-spark4_2.13</code> (we used 0.12.3) plus the <code>graphframes-py</code> Python package; add with <code>--packages</code> or <code>spark.jars</code>.</li>
        <li>Iterative algorithms produce long lineages: checkpoints keep them manageable; cache vertices/edges.</li>
        <li>GraphX (Scala) is the older RDD graph API; GraphFrames is the DataFrame one usable from Python.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a motif pattern: (a)-[]->(b); (b)-[]->(c) means vertex a has an edge to b and b has an edge to c; the result has columns a, b and c, filtered so a is not c.',
    t(16, 22, 'A motif query (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('(a)', 'blue', 1), ('-[]->', 'card', 2), ('(b)', 'green', 3), (';', 'card', 4), ('(b)-[]->(c)', 'violet', 5)]) +
    legend(16, 84, [(1, 'Named vertex', 'becomes a struct column a'), (2, 'Anonymous edge', 'name it [e] to keep its columns'), (3, 'Shared name', 'b must be the same vertex in both parts'),
                    (4, 'And', 'all parts must match'), (5, 'Second hop', 'b points to c')], size=8, gap=15, w=90),
    h=172, caption='Motifs compile to joins on the edges DataFrame.')
extra = '''

  <h3>Dissect a motif</h3>
''' + DIS

types_html = table(['Algorithm', 'Answers', 'Our lab'], [
    ['inDegrees / outDegrees', 'how many referrals in/out', 'kabir 2 in, asha 2 out'], ['pageRank', 'who is influential', 'zoya 1.799 first'],
    ['connectedComponents', 'separate communities', '3 components'], ['find (motif)', 'pattern matches', 'two-step chains'],
    ['shortestPaths', 'hops to landmarks', 'zoya → kabir 3 hops'], ['labelPropagation', 'community detection', '—'],
], minw=560)
warn = 'Degree is not influence. Asha has the most outgoing referrals, but PageRank ranks Zoya first because her referral leads to Asha, who brings many. Choose the metric that matches the business question.'

steps = [
    ('Step 1 · Build the graph',
     code('python', 'l124_graph.py', 'v = spark.createDataFrame([("asha", "customer"), …], "id string, kind string")\ne = spark.createDataFrame([("asha", "ravi", "referred"), …], "src string, dst string, relationship string")\ng = GraphFrame(v, e)', sec('== 1)', '== 2)')),
     'Two ordinary DataFrames. Tara “referred” herself: a self-loop.'),
    ('Step 2 · Degrees',
     code('python', 'l124_graph.py', 'g.inDegrees.join(g.outDegrees, "id", "full").fillna(0)', sec('== 2)', '== 3)')),
     'Kabir is referred most (2); Asha refers most (2).'),
    ('Step 3 · PageRank',
     code('python', 'l124_graph.py', 'g.pageRank(resetProbability=0.15, maxIter=10).vertices', sec('== 3)', '== 4)')),
     'Zoya ranks first: the cycle zoya → asha → … → kabir → zoya concentrates rank.'),
    ('Step 4 · Communities',
     code('python', 'l124_graph.py', 'spark.sparkContext.setCheckpointDir("/tmp/gf-ckpt")\ng.connectedComponents()', sec('== 4)', '== 5)')),
     'Three separate communities; component ids are just labels.'),
    ('Step 5 · Motifs',
     code('python', 'l124_graph.py', 'g.find("(a)-[]->(b); (b)-[]->(c)").filter("a.id != c.id")', sec('== 5)', '== 6)')),
     'Every two-step referral chain, e.g. asha → ravi → kabir.'),
    ('Step 6 · Shortest paths',
     code('python', 'l124_graph.py', 'g.shortestPaths(landmarks=["kabir"])', sec('== 6)')),
     'Hops to Kabir follow edge direction; NULL means unreachable.'),
]
see = [term([('9 customers, 9 referrals', W)], size=7.2), term([('kabir in 2', G), ('asha out 2', G)], size=7.2), term([('zoya 1.799', G), ('kabir 1.623', W)], size=7.2),
       term([('3 components', G)], size=7.2), term([('asha → ravi → kabir', G), ('kabir → zoya → asha', W)], size=7.0), term([('zoya 3 hops', W), ('arjun NULL', RD)], size=7.2)]
B1 = [graph(), graph({'kabir', 'asha'}), graph({'zoya'}), graph(), graph({'asha', 'ravi', 'kabir'}), graph({'zoya', 'kabir'})]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Vertices + edges', 'Degrees', 'PageRank', 'Components', 'Motif chains', 'Shortest paths'], ['blue', 'blue', 'amber', 'green', 'violet', 'blue'])]
two = anim_two('GraphFrames', 'Ask the graph', 'Real outputs (local[2])', 'The referral graph', see, B1, ['Build.', 'Degree.', 'PageRank.', 'Islands.', 'Motifs.', 'Paths.'], ['9 + 9.', 'In/out.', 'Zoya.', '3.', 'Chains.', 'Hops.'])
pe = peel('A motif query, layer by layer', '(a)-[]->(b); (b)-[]->(c). (Simplified.)',
    [('Parse', ''), ('Edge e1', ''), ('Edge e2', ''), ('Join', ''), ('Vertices', ''), ('Filter', '')],
    [['Parse', 'two edge patterns', 'shared b', ''], ['Edge e1', 'edges as (a, b)', '', ''], ['Edge e2', 'edges as (b, c)', '', ''],
     ['Join', 'e1.dst = e2.src', 'a DataFrame join', ''], ['Vertices', 'attach a, b, c', 'structs', ''], ['Filter', 'a.id != c.id', 'your condition', '']],
    ['Parse.', 'Hop 1.', 'Hop 2.', 'Join.', 'Attach.', 'Filter.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Reward top referrers', 'Marketing budget. (Typical.)', ('PageRank vs degree', 'Influence'), [
    ('Count referrals', 'degree', 'Simple.', 'blue'), ('PageRank', 'weighted influence', 'Better.', 'green'),
    ('Compare top 10', 'different people', 'Insight.', 'amber'), ('Reward by PageRank', 'A/B test', 'Act.', 'green'),
    ('Recompute weekly', 'new referrals', 'Operate.', 'blue')], ['Count.', 'Rank.', 'Compare.', 'Reward.', 'Refresh.'], 'scenario-ref') + \
       five('Real-time scenario 2', 'Fraud ring', 'Accounts sharing cards and devices. (Typical.)', ('Connected components', 'Find linked groups'), [
    ('Vertices: accounts, cards, devices', 'edges: uses', 'Model.', 'blue'), ('connectedComponents', 'checkpoint dir', 'Group.', 'green'),
    ('Component with 40 accounts', 'one card', 'Suspicious.', 'red'), ('Review + block', 'rules', 'Act.', 'amber'),
    ('Motifs for patterns', 'shared device + card', 'Refine.', 'violet')], ['Model.', 'Group.', 'Flag.', 'Block.', 'Pattern.'], 'scenario-fraud') + \
       five('Real-time scenario 3 · advanced', 'Graph job too slow', 'Iterative lineage. (Typical.)', ('Checkpoints + cache', 'Cut lineage'), [
    ('100M edges', 'components slow', 'Problem.', 'red'), ('Cache vertices/edges', 'reused', 'Speed.', 'green'),
    ('Checkpoint dir', 'required, cuts lineage', 'Stable.', 'green'), ('Partition edges by src', 'fewer shuffles', 'Tune.', 'amber'),
    ('Or a graph DB', 'for online traversals', 'Choose.', 'blue')], ['Slow.', 'Cache.', 'Checkpoint.', 'Partition.', 'Choose.'], 'scenario-scale')
assemble(HERE, h2_story='When the question is about relationships', hook_html=hk,
    narration='TiffinGo wants to reward its most influential referrers and find separate referral communities. Kabir’s groupBy only counts arrows.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Graph processing with GraphFrames',
    formal='<b>GraphFrames</b> is a Spark package that represents a property graph as two DataFrames, vertices (with an <code>id</code>) and edges (with <code>src</code> and <code>dst</code>), and provides graph queries (motif finding, BFS) and algorithms (degrees, PageRank, connected components, label propagation, shortest paths) implemented with DataFrame operations and GraphX. It is the Python-accessible successor to Spark’s Scala-only GraphX API.',
    simple='Put people in one table and their links in another, and GraphFrames can tell you who is most influential, which groups are connected, how many steps apart people are, and which link patterns exist.',
    term_rows=[('Vertex', 'A node (id).'), ('Edge', 'A link src → dst.'), ('Degree', 'Number of links.'), ('PageRank', 'Influence score.'), ('Component', 'Connected group.'), ('Motif', 'Link pattern query.'), ('Landmark', 'Target for shortest paths.'), ('GraphX', 'Scala graph API.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Most referrals = most influential.', 'PageRank picked Zoya, not Asha.', 'Step 3.'),
               ('Spark has a Python graph API built in.', 'GraphFrames is a separate package; GraphX is Scala.', 'Level 3.'),
               ('Shortest paths ignore direction.', 'They follow edge direction here.', 'Step 6.')],
    exam='“Graph processing in PySpark?” GraphFrames (vertices id, edges src/dst DataFrames): degrees, pageRank, connectedComponents (checkpoint dir), shortestPaths, labelPropagation, bfs, motif find; package graphframes-spark4; GraphX is Scala-only.',
    types_h2='Algorithms and answers', types_html=types_html, warn=warn,
    steps_h2='Ask the referral graph', steps_intro='All outputs are real: PySpark 4.3.0, GraphFrames 0.12.3 (graphframes-spark4_2.13), local[2].',
    steps=steps, two=two, peel_intro='Now peel a motif query.', peel_html=pe,
    scen_intro='Three live scenarios: rewards, a fraud ring, and a slow graph job.', scen=scen,
    uc_h2='Graphs at work', ucs=[uc_('ref', 'referrals', 'blue', '1. Referral programs', 'Influence and chains.', ['Referrals', '*PageRank', 'Rewards']),
        uc_('fraud', 'fraud', 'red', '2. Fraud rings', 'Shared devices and cards.', ['Links', '*components', 'Alerts']),
        uc_('route', 'routes', 'green', '3. Delivery networks', 'Areas and roads.', ['Areas', '*paths', 'Routes']),
        uc_('kg', 'knowledge', 'violet', '4. Knowledge graphs', 'Products and attributes.', ['Entities', '*motifs', 'Insights'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../06-transformations/02-joins/">6.2 Joins</a>.')
