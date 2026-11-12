# Shared sample files for Module 6 (created silently before each recorded command that needs them).
APPLOG = r"""cat > app.log << 'EOF'
2026-11-06 09:00:01 INFO  server started on port 8080
2026-11-06 09:00:05 INFO  GET /health 200
2026-11-06 09:01:10 WARN  disk usage 81% on /data
2026-11-06 09:02:30 ERROR db connection refused (host=db01)
2026-11-06 09:02:31 INFO  retrying db connection
2026-11-06 09:02:35 ERROR db connection refused (host=db01)
2026-11-06 09:03:00 INFO  GET /health 200
2026-11-06 09:04:12 error payment timeout for order 7781
2026-11-06 09:05:40 FATAL out of memory, shutting down
2026-11-06 09:06:00 INFO  server started on port 8080
EOF"""

EMP = r"""cat > employees.csv << 'EOF'
id,name,dept,city,salary
101,Asha,Engineering,Pune,85000
102,Ravi,Sales,Mumbai,52000
103,Meena,Engineering,Bengaluru,98000
104,Kabir,HR,Pune,47000
105,Riya,Sales,Delhi,61000
106,Arjun,Engineering,Mumbai,72000
EOF"""

ACCESS = r"""python3 - << 'PY'
import random
random.seed(7)
ips = ['49.36.12.8']*9 + ['103.21.44.7']*6 + ['157.48.1.20']*4 + ['10.0.0.5']*3 + ['185.220.101.4']*7 + ['117.99.3.3']*2
pages = ['/', '/login', '/cart', '/api/orders', '/products?id=7', '/health']
codes = [200]*7 + [404, 500, 302]
random.shuffle(ips)
with open('access.log', 'w') as f:
    for k, ip in enumerate(ips):
        p = '/admin' if ip == '185.220.101.4' else random.choice(pages)
        c = 401 if p == '/admin' else random.choice(codes)
        f.write(f'{ip} - - [06/Nov/2026:10:{k:02d}:00 +0530] "GET {p} HTTP/1.1" {c} {random.randint(200, 9000)}\n')
PY"""

CODE = r"""mkdir -p src/app src/tests
printf 'import os\n\ndef main():\n    # TODO: read config from env\n    password = "admin123"\n    print("starting")\n\ndef helper():\n    pass  # FIXME slow\n' > src/app/main.py
printf 'def test_main():\n    assert True  # TODO more tests\n' > src/tests/test_main.py
printf 'public class Main {\n  public static void main(String[] a) { System.out.println("hi"); }\n}\n' > src/app/Main.java
printf 'DB_HOST=db01\nDB_PASSWORD=Secret#42\n# API_KEY=old\n' > src/app/.env"""

ALL = '\n'.join([APPLOG, EMP, ACCESS, CODE])
