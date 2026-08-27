"""
Deployed Live Backend & Frontend QA Performance & Latency Test Suite
"""
import time
import json
import urllib.request
import urllib.error
import ssl

BACKEND_URL = "https://mahi-solar-backend.onrender.com"
FRONTEND_URL = "https://mahi-solar-frontend.mrcapital1980.workers.dev"

print("\n" + "="*70)
print("  MAHI SOLAR LIVE PRODUCTION QA & LATENCY BENCHMARK")
print("="*70)

ctx = ssl.create_default_context()

results = []

def test_endpoint(name, url, method="GET", payload=None):
    start = time.time()
    try:
        req_data = json.dumps(payload).encode('utf-8') if payload else None
        req = urllib.request.Request(url, data=req_data, method=method)
        req.add_header('Accept', 'application/json')
        if req_data:
            req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            status = resp.status
            body = resp.read()
            elapsed_ms = round((time.time() - start) * 1000, 2)
            cors = resp.headers.get('Access-Control-Allow-Origin', 'None')
            print(f"  [PASS] [{status}] {name:<35} -> {elapsed_ms:>7.2f} ms | CORS: {cors}")
            results.append({
                "name": name,
                "url": url,
                "status": status,
                "time_ms": elapsed_ms,
                "cors": cors,
                "size_bytes": len(body),
                "error": None
            })
            try:
                return json.loads(body)
            except Exception:
                return body
    except urllib.error.HTTPError as e:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        print(f"  [WARN] [{e.code}] {name:<35} -> {elapsed_ms:>7.2f} ms")
        results.append({
            "name": name,
            "url": url,
            "status": e.code,
            "time_ms": elapsed_ms,
            "cors": e.headers.get('Access-Control-Allow-Origin', 'None'),
            "size_bytes": 0,
            "error": str(e)
        })
        return None
    except Exception as ex:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        print(f"  [FAIL] [ERR] {name:<35} -> {elapsed_ms:>7.2f} ms | Error: {ex}")
        results.append({
            "name": name,
            "url": url,
            "status": 0,
            "time_ms": elapsed_ms,
            "cors": "None",
            "size_bytes": 0,
            "error": str(ex)
        })
        return None

# 1. Warm up / Cold start measurement
print("\n[1] TESTING BACKEND COLD START & LATENCY")
prod_data = test_endpoint("1. Product Catalog API", f"{BACKEND_URL}/products/")

# 2. Sequential warm requests
print("\n[2] WARM BACKEND API ENDPOINT SPEEDS")
test_endpoint("2. Blog List API", f"{BACKEND_URL}/blog/")
test_endpoint("3. Solar Calculator Engine", f"{BACKEND_URL}/calculator/calculate/", method="POST", payload={"monthly_bill": 5000, "units": 0})

# 3. Product image fetch speed
print("\n[3] TESTING PRODUCT IMAGE FETCH SPEEDS")
if prod_data and isinstance(prod_data, list):
    for prod in prod_data[:3]:
        img = prod.get('image')
        pname = prod.get('name', 'Product')
        if img:
            if not img.startswith('http'):
                img = f"{BACKEND_URL}{img if img.startswith('/') else '/' + img}"
            test_endpoint(f"Img: {pname[:25]}", img)
elif prod_data and isinstance(prod_data, dict) and 'results' in prod_data:
    for prod in prod_data['results'][:3]:
        img = prod.get('image')
        pname = prod.get('name', 'Product')
        if img:
            if not img.startswith('http'):
                img = f"{BACKEND_URL}{img if img.startswith('/') else '/' + img}"
            test_endpoint(f"Img: {pname[:25]}", img)

# 4. Frontend CDN edge latency
print("\n[4] CLOUDFLARE FRONTEND EDGE LATENCY")
test_endpoint("Frontend index.html", f"{FRONTEND_URL}/pages/index.html")
test_endpoint("Frontend style.css", f"{FRONTEND_URL}/css/style.css")
test_endpoint("Frontend api.js", f"{FRONTEND_URL}/js/api.js")

print("\n" + "="*70)
print("  QA SUMMARY & DIAGNOSTICS")
print("="*70)
for r in results:
    status_str = f"HTTP {r['status']}" if r['status'] else "FAILED"
    print(f"  {r['name']:<35} : {r['time_ms']:>7.2f} ms | {status_str:<8} | Size: {r['size_bytes']:>6} B")
print("="*70 + "\n")
