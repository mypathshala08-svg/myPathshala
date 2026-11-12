# Lesson 5.3 — scale out on one machine: 1 vs 2 server processes, same load (real measurement)
import http.server, threading, time, urllib.request, multiprocessing as mp, concurrent.futures as cf, hashlib
def serve(port):
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            h = b'menu'
            for _ in range(60000): h = hashlib.sha256(h).digest()      # ~CPU work per request
            self.send_response(200); self.end_headers(); self.wfile.write(h[:4].hex().encode())
        def log_message(self, *a): pass
    http.server.HTTPServer(('127.0.0.1', port), H).serve_forever()
def load(ports, n=120, conc=8):
    urls = [f'http://127.0.0.1:{ports[i % len(ports)]}/' for i in range(n)]
    t = time.time()
    with cf.ThreadPoolExecutor(conc) as ex: list(ex.map(lambda u: urllib.request.urlopen(u).read(), urls))
    return n / (time.time() - t)
if __name__ == '__main__':
    procs = [mp.Process(target=serve, args=(p,), daemon=True) for p in (8101, 8102)]
    [p.start() for p in procs]; time.sleep(1)
    print(f"machine has {mp.cpu_count()} CPU cores; 120 requests, 8 at a time")
    r1 = load([8101]); print(f"== 1) one server process (no scaling):    {r1:6.1f} requests/s")
    r2 = load([8101, 8102]); print(f"== 2) two server processes (scaled out): {r2:6.1f} requests/s  → {r2/r1:.1f}× throughput")
