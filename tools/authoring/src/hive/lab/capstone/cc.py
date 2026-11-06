"""python3 capstone/cc.py NAME 'SQL' [--info]  -> captures/NAME.txt (db tiffingo_dw)"""
import sys, time; sys.path.insert(0, '/root/lab/hive'); from hq import hq
def cc(name, sql, info=False):
    t = time.time(); o = hq(sql, info, 'tiffingo_dw'); el = time.time() - t
    open(f'/root/lab/hive/captures/{name}.txt', 'w').write(o + '\n'); return o, el
if __name__ == '__main__':
    o, el = cc(sys.argv[1], sys.argv[2], '--info' in sys.argv); print(o); print(f'[{el:.1f}s]')
