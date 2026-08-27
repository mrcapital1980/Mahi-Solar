"""
Comprehensive API endpoint tester for Mahi Solar backend
Run: python qa_test.py
"""
import json
import urllib.request
import urllib.error
import sys
import os

# Need Django setup for DB queries
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

BASE = 'http://127.0.0.1:8000'
results = []

def test_get(path, token=None, desc=""):
    try:
        req = urllib.request.Request(BASE + path)
        req.add_header('Accept', 'application/json')
        if token:
            req.add_header('Authorization', f'Token {token}')
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            data = json.loads(e.read())
        except Exception:
            data = {}
    except Exception as ex:
        status = 0
        data = {"error": str(ex)}
    ok = "PASS" if status in (200, 201) else ("WARN" if status == 405 else "FAIL")
    label = desc or path
    print(f"  {ok} [{status}] GET {label}")
    results.append((ok, status, "GET", label, data))
    return status, data


def test_post(path, payload, token=None, desc=""):
    try:
        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(BASE + path, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        if token:
            req.add_header('Authorization', f'Token {token}')
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            data = json.loads(e.read())
        except Exception:
            data = {}
    except Exception as ex:
        status = 0
        data = {"error": str(ex)}
    ok = "PASS" if status in (200, 201) else "FAIL"
    label = desc or path
    print(f"  {ok} [{status}] POST {label}")
    results.append((ok, status, "POST", label, data))
    return status, data


print("\n" + "="*60)
print("  MAHI SOLAR QA ENDPOINT TEST SUITE")
print("="*60)

# ---- PUBLIC ENDPOINTS ----
print("\n[1] PUBLIC ENDPOINTS")
test_get('/products/', desc='Product Catalog')
test_get('/blog/', desc='Blog List')
status, d = test_get('/leads/contact/', desc='Contact (GET - should succeed or 405)')
status, d = test_get('/accounts/login/', desc='Login (GET - should return method info)')

# ---- CALCULATOR (POST) ----
print("\n[2] CALCULATOR")
status, d = test_post('/calculator/calculate/', {'monthly_bill': 5000, 'units': 0}, desc='Calculate Solar (bill=5000)')
if d.get('success'):
    print(f"    -> recommended_kw={d.get('recommended_kw')} final_cost={d.get('final_cost')} roi_years={d.get('roi_years')}")

# ---- AUTH FLOW ----
print("\n[3] AUTHENTICATION FLOW")
status, d = test_post('/accounts/login/', {'username': 'nonexistent', 'password': 'wrongpass'}, desc='Login (invalid credentials)')
print(f"    -> error={d.get('error')}")

# Get real user token
user = User.objects.filter(is_superuser=False, is_active=True).first()
token_obj, _ = Token.objects.get_or_create(user=user)
user_token = token_obj.key
print(f"    -> Using token for user '{user.username}': {user_token[:20]}...")

# ---- AUTH-REQUIRED ENDPOINTS ----
print("\n[4] AUTHENTICATED USER ENDPOINTS")
status, d = test_get('/orders/cart/', token=user_token, desc='Cart View (authenticated)')
if d.get('success'):
    print(f"    -> cart items={d.get('cart', {}).get('item_count', 0)}")

status, d = test_get('/orders/my-orders/', token=user_token, desc='My Orders (authenticated)')
if d.get('success'):
    print(f"    -> orders count={len(d.get('orders', []))}")

status, d = test_get('/accounts/profile/', token=user_token, desc='Profile (authenticated)')
if d.get('success'):
    print(f"    -> user={d.get('profile', {}).get('username')}")

# ---- LEAD FORMS ----
print("\n[5] LEAD FORM SUBMISSIONS")
status, d = test_post('/leads/contact/', {
    'name': 'QA Tester', 'email': 'qa@mahisolar.in',
    'phone': '9876543210', 'subject': 'QA Test Enquiry',
    'message': 'This is an automated QA test message for Mahi Solar.'
}, desc='Contact Lead Submission')
print(f"    -> id={d.get('id')} message={d.get('message')}")

status, d = test_post('/leads/site-visit/', {
    'name': 'QA Tester', 'email': 'qa@mahisolar.in',
    'phone': '9876543210', 'address': 'QA Street, Athwa Lines',
    'city': 'Surat', 'preferred_date': '2026-08-20', 'preferred_slot': 'morning'
}, desc='Site Visit Lead Submission')
print(f"    -> id={d.get('id')} message={d.get('message')}")

status, d = test_post('/calculator/save-lead/', {
    'name': 'QA Tester', 'email': 'qa@mahisolar.in',
    'phone': '9876543210', 'monthly_bill': 5000,
    'recommended_kw': 5.0, 'final_cost': 210000, 'roof_area': 500
}, desc='Calculator Lead Save')
print(f"    -> success={d.get('success')}")

# ---- ADMIN ENDPOINTS ----
print("\n[6] ADMIN-ONLY ENDPOINTS")
superuser = User.objects.filter(is_superuser=True).first()
admin_token_obj, _ = Token.objects.get_or_create(user=superuser)
admin_token = admin_token_obj.key
print(f"    -> Admin user: '{superuser.username}' token: {admin_token[:20]}...")

status, d = test_get('/leads/contacts-list/', token=admin_token, desc='Contacts List (admin)')
print(f"    -> count={len(d.get('leads', []))}")

status, d = test_get('/leads/site-visits-list/', token=admin_token, desc='Site Visits List (admin)')
print(f"    -> count={len(d.get('leads', []))}")

status, d = test_get('/leads/calculator-list/', token=admin_token, desc='Calculator Leads (admin)')
print(f"    -> count={len(d.get('leads', []))}")

status, d = test_get('/orders/my-orders/', token=admin_token, desc='All Orders (admin)')
print(f"    -> count={len(d.get('orders', []))}")

# ---- PRODUCT DETAIL ----
print("\n[7] PRODUCT DETAIL")
from products.models import Product
for prod in Product.objects.filter(is_active=True)[:3]:
    status, d = test_get(f'/products/{prod.slug}/', desc=f'Product: {prod.name}')
    if d.get('success'):
        p = d.get('product') or d
        print(f"    -> price={p.get('price')} discounted={p.get('discounted_price')} images={bool(p.get('image'))}")

# ---- PROTECTED ENDPOINTS WITHOUT AUTH ----
print("\n[8] AUTH GUARD TESTS (no token)")
for path in ['/orders/cart/', '/orders/my-orders/', '/accounts/profile/']:
    status, d = test_get(path, desc=f'Protected: {path}')
    print(f"    -> expected 401, got={status} ok={'YES' if status == 401 else 'UNEXPECTED'}")

# ---- SUMMARY ----
print("\n" + "="*60)
print("  TEST SUMMARY")
print("="*60)
passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
warned = sum(1 for r in results if r[0] == "WARN")
print(f"  PASS:  {passed}")
print(f"  FAIL:  {failed}")
print(f"  WARN:  {warned}")
print(f"  TOTAL: {len(results)}")
if failed > 0:
    print("\n  FAILURES:")
    for r in results:
        if r[0] == "FAIL":
            print(f"    - [{r[1]}] {r[2]} {r[3]}")
print("="*60 + "\n")
