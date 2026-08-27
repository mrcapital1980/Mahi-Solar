/*
 * MAHI SOLAR — GLOBAL FRONTEND API GATEWAY
 */

const API_BASE_URL = window.API_BASE_URL || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://mahi-solar-backend.onrender.com'
);
window.API_BASE_URL = API_BASE_URL;

// Image URL Helper to prevent double host prefixes or broken paths
function getImageUrl(path) {
    if (!path) return null;
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${cleanPath}`;
}

// Auth State Helper
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    // CSRF token fallback
    const csrf = getCookie('csrftoken');
    if (csrf) {
        headers['X-CSRFToken'] = csrf;
    }
    return headers;
}

// Cookie Helper
function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

// Global UI Updater (JWT/Token + Cart Badge)
document.addEventListener('DOMContentLoaded', () => {
    updateGlobalUI();
});

function updateGlobalUI() {
    // 1. Auth Links & Dropdowns
    const authLinks = document.getElementById('authLinks');
    const userDropdown = document.getElementById('userDropdown');
    const userNameField = document.getElementById('userNameField');
    
    const userJson = localStorage.getItem('user_profile');
    if (userJson) {
        try {
            const user = JSON.parse(userJson);
            if (authLinks) authLinks.style.display = 'none';
            if (userDropdown) {
                userDropdown.style.display = 'block';
                if (userNameField) userNameField.textContent = user.first_name || user.username || 'Account';
            }
            
            // Dynamic injection of admin dashboard link
            if (user.is_superuser || user.is_staff) {
                const dropdownMenus = document.querySelectorAll('.dropdown-menu');
                dropdownMenus.forEach(menu => {
                    if (!menu.querySelector('.admin-dash-link')) {
                        const adminLink = document.createElement('a');
                        adminLink.href = 'admin-dashboard.html';
                        adminLink.className = 'admin-dash-link';
                        adminLink.style.color = '#ffb300';
                        adminLink.style.fontWeight = 'bold';
                        adminLink.innerHTML = '<i class="fas fa-user-shield"></i> Admin Dashboard';
                        menu.insertBefore(adminLink, menu.firstChild);
                    }
                });
            }
        } catch (e) {
            localStorage.clear();
        }
    } else {
        if (authLinks) authLinks.style.display = 'flex';
        if (userDropdown) userDropdown.style.display = 'none';
    }

    // 2. Synchronize Shopping Cart Badge count
    const cartBadge = document.getElementById('cartBadgeCount');
    if (cartBadge) {
        const cart = getLocalCart();
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartBadge.textContent = totalItems;
        if (totalItems > 0) {
            cartBadge.style.display = 'inline-block';
        } else {
            cartBadge.style.display = 'none';
        }
    }
}

// Auth Signout handler
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
    alert("Signed out successfully!");
    window.location.href = 'index.html';
}

// Local Cart Management
function getLocalCart() {
    try {
        return JSON.parse(localStorage.getItem('mahi_solar_cart')) || [];
    } catch(e) {
        return [];
    }
}

function saveLocalCart(cart) {
    localStorage.setItem('mahi_solar_cart', JSON.stringify(cart));
    updateGlobalUI();
}

function addToCartLocal(product) {
    let cart = getLocalCart();
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            slug: product.slug,
            price: product.price,
            discounted_price: product.discounted_price,
            image: getImageUrl(product.image),
            quantity: 1
        });
    }
    saveLocalCart(cart);

    // Sync with backend if logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        fetch(`${API_BASE_URL}/orders/cart/add/${product.id}/`, {
            method: 'POST',
            headers: getAuthHeaders()
        }).catch(() => {});
    }

    alert(`${product.name} added to shopping cart!`);
}
