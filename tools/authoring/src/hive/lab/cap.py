"""python3 cap.py NAME 'SQL'  -> captures/NAME.txt (db tiffingo), prints output"""
import sys; sys.path.insert(0, '/root/lab/hive'); from hq import hq
def cap(name, sql, info=False, db='tiffingo'):
    o = hq(sql, info, db); open(f'/root/lab/hive/captures/{name}.txt', 'w').write(o + '\n'); return o
if __name__ == '__main__':
    print(cap(sys.argv[1], sys.argv[2], '--info' in sys.argv))
