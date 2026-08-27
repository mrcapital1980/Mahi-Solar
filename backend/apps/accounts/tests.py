import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category
from orders.models import Order, Cart, CartItem
from leads.models import ContactLead, SiteVisitLead

class MahiSolarAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user
        self.username = "testuser"
        self.password = "Secr3tP@ssword"
        self.email = "testuser@mahisolar.in"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        
        # Create category & product
        self.category = Category.objects.create(name="Solar Panel", slug="solar-panel")
        self.product = Product.objects.create(
            name="Mahi High efficiency Monoperc 500W",
            slug="mahi-500w",
            category=self.category,
            price=25000.00,
            discounted_price=22000.00,
            wattage=500,
            brand="Mahi Solar",
            stock=15,
            is_active=True
        )

    def test_registration_and_login_api(self):
        # 1. Test register api
        register_url = reverse('register')
        payload = {
            'username': 'newuser',
            'email': 'newuser@mahisolar.in',
            'password': 'StrongPassword123'
        }
        res = self.client.post(register_url, json.dumps(payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data['success'])

        # 2. Test login api
        login_url = reverse('login')
        login_payload = {
            'username': self.username,
            'password': self.password
        }
        res = self.client.post(login_url, json.dumps(login_payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('access', data)
        self.assertEqual(data['username'], self.username)

    def test_profile_api(self):
        # Authenticate first
        self.client.login(username=self.username, password=self.password)
        profile_url = reverse('profile')
        
        # Get profile
        res = self.client.get(profile_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['profile']['email'], self.email)

        # Update profile
        update_payload = {
            'first_name': 'Mahi',
            'last_name': 'Developer',
            'phone': '9377309325',
            'address': '117 Oberon Hub',
            'city': 'Surat'
        }
        res = self.client.post(profile_url, json.dumps(update_payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Profile updated')

        # Get profile again and verify update
        res = self.client.get(profile_url, HTTP_ACCEPT='application/json')
        data = res.json()
        self.assertEqual(data['profile']['first_name'], 'Mahi')

    def test_products_catalog_api(self):
        # List products
        products_url = reverse('products')
        res = self.client.get(products_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0]['name'], self.product.name)

        # Product detail
        detail_url = reverse('product_detail', kwargs={'slug': self.product.slug})
        res = self.client.get(detail_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['price'], 25000.00)

    def test_leads_submission_api(self):
        # Contact lead
        contact_url = reverse('contact')
        payload = {
            'name': 'Customer Name',
            'email': 'customer@test.com',
            'phone': '9876543210',
            'subject': 'Inquiry about 500W panel',
            'message': 'Hello, please call me back.'
        }
        res = self.client.post(contact_url, json.dumps(payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        self.assertTrue(ContactLead.objects.filter(email='customer@test.com').exists())

        # Site visit lead
        visit_url = reverse('site_visit')
        visit_payload = {
            'name': 'Customer Visit',
            'phone': '9876543210',
            'email': 'visit@test.com',
            'address': 'Vesu, Surat',
            'preferred_date': '2026-06-15',
            'preferred_time': 'morning',
            'roof_area': 1200,
            'monthly_bill': 4500
        }
        res = self.client.post(visit_url, json.dumps(visit_payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        self.assertTrue(SiteVisitLead.objects.filter(email='visit@test.com').exists())

    def test_orders_checkout_and_cancellation_api(self):
        # Authenticate
        self.client.login(username=self.username, password=self.password)
        
        # Populate cart in database first
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # Checkout placement
        checkout_url = reverse('checkout')
        checkout_payload = {
            'full_name': 'Test Checkout User',
            'email': 'checkout@test.com',
            'phone': '9377309325',
            'address': 'Pal, Surat',
            'city': 'Surat',
            'state': 'Gujarat',
            'pincode': '395009',
            'notes': 'Deliver carefully',
            'payment_method': 'cod'
        }
        res = self.client.post(checkout_url, json.dumps(checkout_payload), content_type='application/json', HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        order_id = data['order_id']
        
        # Verify order created in database
        order = Order.objects.get(order_id=order_id)
        # Note: COD order status changes to confirmed in views
        self.assertEqual(order.total_amount, 44000.00)
        self.assertEqual(order.status, 'confirmed')

        # Order list API
        list_url = reverse('order_list')
        res = self.client.get(list_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        self.assertEqual(len(res.json()['orders']), 1)

        # Order detail API
        detail_url = reverse('order_detail', kwargs={'order_id': order_id})
        res = self.client.get(detail_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])

        # Cancel order API
        cancel_url = reverse('cancel_order', kwargs={'order_id': order.id})
        res = self.client.post(cancel_url, HTTP_ACCEPT='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])
        
        # Verify cancelled in DB
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

    def test_unauthenticated_profile_access(self):
        profile_url = reverse('profile')
        res = self.client.get(profile_url)
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Authentication credentials were not provided.')

