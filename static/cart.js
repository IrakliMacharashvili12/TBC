function loadCart() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContainer = document.getElementById('cart-items');
    const totalPriceElement = document.getElementById('total-price');

    cartContainer.innerHTML = '';
    let totalPrice = 0;

    cart.forEach((product, index) => {
        const productCard = document.createElement('div');
        productCard.classList.add('card', 'mb-3');
        productCard.innerHTML = `
            <div class="row g-0">
                <div class="col-md-4">
                    <img src="${product.image}" class="img-fluid rounded-start" alt="${product.title}">
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <h5 class="card-title">${product.title}</h5>
                        <p class="card-text">${product.description.slice(0, 100)}...</p>
                        <div class="price">$${product.price}</div>
                        <button class="btn btn-danger" onclick="removeFromCart(${index})">Remove</button>
                    </div>
                </div>
            </div>
        `;
        cartContainer.appendChild(productCard);
        totalPrice += product.price;
    });

    totalPriceElement.textContent = totalPrice.toFixed(2);
}

function removeFromCart(index) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    loadCart();
}

document.getElementById('clear-cart').addEventListener('click', function() {
    localStorage.removeItem('cart');
    loadCart();
});

function checkout() {
    localStorage.removeItem('cart');
    alert('Your cart has been cleared. Proceeding to checkout...');
    window.location.href = '/cart';
}

window.onload = loadCart;
