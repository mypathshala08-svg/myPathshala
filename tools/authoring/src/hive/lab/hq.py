"""Run HiveQL in the lab and return Beeline's real output.
usage: python3 hq.py 'SQL;' | -f file.hql   [--info]  (INFO lines kept with --info)"""
import subprocess, sys, os, re, tempfile
def hq(sql, info=False, db='default'):
    d = '/home/claude/lab/hive/data'
    fn = os.path.join(d, '_q.hql'); open(fn, 'w').write(sql)
    p = subprocess.run(['docker', 'exec', '-e', 'HADOOP_CLIENT_OPTS=-Dorg.jline.terminal.type=dumb -Dorg.jline.terminal.provider=exec', 'hiveserver2', 'beeline', '-u', f'jdbc:hive2://localhost:10000/{db}', '-n', 'hive',
                        '--silent=' + ('false' if info else 'true'), '-f', '/data/_q.hql'], capture_output=True, text=True)
    out = (p.stdout + p.stderr).replace('\r', '')
    src = set(l.strip() for l in sql.split('\n') if l.strip())
    keep = [l for l in out.split('\n') if not l.startswith('SLF4J') and l.strip() not in src]
    if not info:
        keep = [l for l in keep if l[:1] in '+|' or l.startswith(('Error', 'FAILED', 'WARN'))]
    return '\n'.join(keep).strip('\n')
if __name__ == '__main__':
    a = sys.argv[1:]; info = '--info' in a; a = [x for x in a if x != '--info']
    sql = open(a[1]).read() if a[0] == '-f' else a[0]
    print(hq(sql, info))
