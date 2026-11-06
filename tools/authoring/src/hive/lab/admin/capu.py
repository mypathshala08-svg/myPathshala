"""python3 capu.py NAME USER 'SQL' [--info] -> captures/NAME.txt as USER (db tiffingo)"""
import sys, subprocess, os
def run(user, sql, info=False, db='tiffingo'):
    fn = '/home/claude/lab/hive/data/_qu.hql'; open(fn, 'w').write(sql)
    p = subprocess.run(['docker', 'exec', '-e', 'HADOOP_CLIENT_OPTS=-Dorg.jline.terminal.type=dumb -Dorg.jline.terminal.provider=exec', 'hiveserver2', 'beeline', '-u', f'jdbc:hive2://localhost:10000/{db}', '-n', user,
                        '--silent=' + ('false' if info else 'true'), '-f', '/data/_qu.hql'], capture_output=True, text=True)
    out = (p.stdout + p.stderr).replace('\r', '')
    src = set(l.strip() for l in sql.split('\n') if l.strip())
    keep = [l for l in out.split('\n') if not l.startswith('SLF4J') and l.strip() not in src]
    if not info:
        keep = [l for l in keep if l[:1] in '+|' or l.startswith(('Error', 'FAILED', 'WARN'))]
    import re
    return re.sub(r'; Query ID[^\n]*', '', '\n'.join(keep).strip('\n'))
if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--info']
    o = run(a[1], a[2], '--info' in sys.argv)
    open(f'/root/lab/hive/captures/{a[0]}.txt', 'w').write(o + '\n'); print(o)
