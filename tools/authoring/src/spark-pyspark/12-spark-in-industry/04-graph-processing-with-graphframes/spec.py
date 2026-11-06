import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='12-spark-in-industry', lesson='04-graph-processing-with-graphframes', n='12.4', module_label='Module 12 · Spark in industry today',
    title='Graph processing with GraphFrames',
    desc='Graph analytics from PySpark with GraphFrames: vertices and edges as DataFrames, degrees, PageRank, connected components, shortest paths, label propagation and motif finding, GraphX vs GraphFrames, and setup for Spark 4. Real PySpark 4.3 lab with GraphFrames 0.12.3 on a referral network.',
    og_desc='Zoya beats Asha on PageRank: a referral graph analysed with GraphFrames on Spark 4.3.',
    minutes=20, level='Intermediate',
    lead='How do you analyse relationships at scale? We load referrals as a <b>graph</b>, rank <b>influence</b>, find <b>communities</b>, query <b>patterns</b> and measure <b>hops</b>. <b>All outputs are real.</b>',
    chips=['PageRank', '3 components', 'Motif find', 'Runs in your browser (Python)'])
MAIN = '''# PageRank by hand on a tiny referral graph
edges = [("asha", "ravi"), ("asha", "meera"), ("ravi", "kabir"), ("meera", "kabir"), ("kabir", "zoya"), ("zoya", "asha")]
nodes = sorted({n for e in edges for n in e})
out = {n: [d for s, d in edges if s == n] for n in nodes}
rank = {n: 1.0 for n in nodes}
for _ in range(20):
    new = {n: 0.15 for n in nodes}
    for s in nodes:
        for d in out[s]:
            new[d] += 0.85 * rank[s] / len(out[s])
    rank = new
for n, r in sorted(rank.items(), key=lambda x: -x[1]):
    print(f"{n:6s} {r:.3f}")
'''
RUN = dict(heading='Run the code: PageRank by hand', intro='<p>Rank flows along edges. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('            new[d] += 0.85 * rank[s] / len(out[s])', 'Each node shares its rank among its out-links.'), ('    new = {n: 0.15 for n in nodes}', 'resetProbability 0.15.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add an edge ravi → zoya.', code=None),
        dict(label='2 · Predict first: in-degree', hint='<b>Predict first:</b> who has most incoming?', code='edges = [("asha", "ravi"), ("asha", "meera"), ("ravi", "kabir"), ("meera", "kabir")]\nfrom collections import Counter\nprint(Counter(d for _, d in edges).most_common(1))\n'),
        dict(label='3 · Components', hint='Union-find on undirected edges.', code='p = {}\ndef f(x):\n    p.setdefault(x, x)\n    while p[x] != x: x = p[x]\n    return x\nfor a, b in [("a", "b"), ("b", "c"), ("x", "y")]: p[f(a)] = f(b)\nprint(len({f(n) for n in "abcxy"}))\n'),
        dict(label='4 · Two hops', hint='Chains a→b→c.', code='e = [("asha", "ravi"), ("ravi", "kabir")]\nprint([(a, b, d) for a, b in e for c, d in e if b == c])\n'),
        dict(label='5 · Spot the error', hint='Missing checkpoint dir.', expect='error', code='raise RuntimeError("Checkpoint directory is not set. Please set it first using sc.setCheckpointDir().")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4 + GraphFrames. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Install', cmd='pip install graphframes-py\npyspark --packages io.graphframes:graphframes-spark4_2.13:0.12.3', file='terminal', output='', note='Jar + Python package.'),
           dict(title='2 · Run', cmd='python3 l124_graph.py', file='terminal', output='| zoya|   1.799|', note='PageRank.')])
TRACE = dict(heading='One PageRank step', intro='<p>Share rank along edges.</p>',
    code='rank = {"asha": 1.0}\nout = ["ravi", "meera"]\nprint({d: 0.85 * rank["asha"] / len(out) for d in out})\n', notes={3: 'Split :: 0.425 each.'})
WORKED_INTRO = 'Three graph decisions.'
EXAMPLES = [
    dict(level='b', tag='Graph · model', title='Model the data', problem='<p>Referral table.</p>', inp='tables',
         approach=['Vertices: customers with id.', 'Edges: src, dst.', 'GraphFrame(v, e).'], code='print(["vertices(id, ...)", "edges(src, dst, ...)"])\n', notes={1: 'Two DataFrames.'}, tryit='Step 1.'),
    dict(level='i', tag='Graph · metric', title='Influence metric', problem='<p>Pick top referrers.</p>', inp='choice',
         approach=['Degree for volume.', 'PageRank for influence.', 'Compare both.'], code='print("pageRank(resetProbability=0.15, maxIter=10)")\n', notes={1: 'Different winners.'}, tryit='Step 3.'),
    dict(level='a', tag='Graph · fraud', title='Find rings', problem='<p>Shared devices.</p>', inp='approach',
         approach=['Bipartite graph accounts–devices.', 'connectedComponents.', 'Flag big components.'], code='print("components with > 10 accounts -> review")\n', notes={1: 'Checkpoint dir.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: A GraphFrame is built from…', options=['One DataFrame', 'Vertices and edges DataFrames', 'An RDD only', 'A CSV'], answer=1, why='Two tables.'),
    dict(q='Beginner: Edges need columns…', options=['id', 'src and dst', 'from/to', 'key/value'], answer=1, why='Required names.'),
    dict(q='Beginner: PageRank measures…', options=['Size', 'Influence', 'Distance', 'Time'], answer=1, why='Rank.'),
    dict(q='Intermediate: Top PageRank in our lab…', options=['asha', 'zoya', 'kabir', 'tara'], answer=1, why='1.799.'),
    dict(q='Intermediate: connectedComponents needs…', options=['A GPU', 'A checkpoint directory', 'Hive', 'Kafka'], answer=1, why='Lineage.'),
    dict(q='Intermediate: Motif "(a)-[]->(b); (b)-[]->(c)" finds…', options=['Triangles only', 'Two-step chains', 'Single edges', 'Cycles only'], answer=1, why='Step 5.'),
    dict(q='Advanced: GraphX can be used from…', options=['Python', 'Scala/Java', 'SQL', 'R'], answer=1, why='Scala-only.'),
    dict(q='Advanced: NULL in shortest paths means…', options=['0 hops', 'Unreachable', 'Error', 'Self'], answer=1, why='No path.')])
REVISION = ['GraphFrame(vertices id, edges src/dst).', 'Degrees, PageRank (zoya 1.799), connectedComponents (3), shortestPaths, labelPropagation.',
    'Motifs: g.find("(a)-[]->(b); (b)-[]->(c)").', 'Setup: graphframes-spark4_2.13 0.12.3 + graphframes-py; checkpoint dir.', 'GraphX is Scala-only.']
FAQ = [('Is GraphFrames part of Spark?', 'No, it is a separate open-source package; add it with --packages or spark.jars.'),
    ('Can I use SQL on results?', 'Yes, every result is a DataFrame.'),
    ('How large can graphs be?', 'Billions of edges on a cluster for batch analytics; use a graph database for low-latency traversals.'),
    ('Undirected graphs?', 'Add edges both ways or use algorithms that ignore direction (components).')]
PRACTICE_INTRO = 'Graph programs.'
PROBLEMS = [
    dict(level='easy', title='Out-degree', stmt='Count per src.', inp='list', code='from collections import Counter\nprint(Counter(s for s, _ in [("a", "b"), ("a", "c"), ("b", "c")]))\n', explain='a: 2.'),
    dict(level='easy', title='Nodes', stmt='Distinct nodes.', inp='list', code='e = [("a", "b"), ("b", "c")]\nprint(sorted({n for x in e for n in x}))\n', explain='3.'),
    dict(level='easy', title='Self-loop', stmt='Find loops.', inp='list', code='print([e for e in [("t", "t"), ("a", "b")] if e[0] == e[1]])\n', explain='tara.'),
    dict(level='medium', title='BFS hops', stmt='Hops from asha.', inp='dict', code='g = {"asha": ["ravi"], "ravi": ["kabir"], "kabir": []}\nfrom collections import deque\nd, q = {"asha": 0}, deque(["asha"])\nwhile q:\n    u = q.popleft()\n    for v in g[u]:\n        if v not in d: d[v] = d[u] + 1; q.append(v)\nprint(d)\n', explain='kabir 2.'),
    dict(level='medium', title='Chains', stmt='Two-hop chains.', inp='list', code='e = [("a", "b"), ("b", "c"), ("b", "d")]\nprint([(x, y, z) for x, y in e for w, z in e if y == w])\n', explain='2 chains.'),
    dict(level='medium', title='Top rank', stmt='Max PageRank.', inp='dict', code='r = {"zoya": 1.799, "kabir": 1.623}\nprint(max(r, key=r.get))\n', explain='zoya.'),
    dict(level='business', title='Ring size', stmt='Flag components > 10.', inp='dict', code='c = {1: 40, 2: 3}\nprint([k for k, v in c.items() if v > 10])\n', explain='[1].'),
    dict(level='business', title='Reward budget', stmt='Top 3 × ₹500.', inp='ints', code='print(3 * 500)\n', explain='₹1,500.')]
SCN_INTRO = 'Graph interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you do graph analytics in PySpark?”', 'Explain.', 'answer?', '<p>With GraphFrames: vertices and edges DataFrames, then degrees, PageRank, connected components, shortest paths and motif queries. GraphX exists but is Scala-only.</p>', '“With groupBy only.”') +
    scn('Fintech', 'Mid-level', 'Fraud rings', 'Design.', 'answer?', '<ul><li>Accounts–devices graph, connected components, motifs.</li></ul>', 'Manual review only.') +
    scn('Data', 'Mid-level', 'Checkpoint error', 'components fails.', 'fix?', '<ul><li>sc.setCheckpointDir(path).</li></ul>', 'Disable it.') +
    scn('Architecture', 'Senior', 'Graph DB or Spark?', 'Choose.', 'answer?', '<ul><li>Spark for batch analytics; graph DB for online traversals.</li></ul>', 'Always Spark.'))
