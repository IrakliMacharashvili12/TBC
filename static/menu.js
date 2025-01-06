let products = [];
let categories = [];

fetch('/api/products')
    .then(response => response.json())
    .then(data => {
        products = data;
        categories = [...new Set(data.map(product => product.category))];
        populateCategories();
        displayProducts();
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });


        function populateCategories() {
            const categorySelect = document.getElementById('category');
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categorySelect.appendChild(option);
            });
        }

        // Function to filter products by selected category
        function filterData() {
            const selectedCategory = document.getElementById('category').value;
            const filteredProducts = selectedCategory ?
                products.filter(product => product.category === selectedCategory) :
                products;
            displayProducts(filteredProducts);
        }

        // Function to display products using Bootstrap cards
        function displayProducts(filteredProducts = products) {
            const productContainer = document.getElementById('product-container');
            productContainer.innerHTML = ''; // Clear previous products

            filteredProducts.forEach(product => {
                const productCard = document.createElement('div');
                productCard.classList.add('col-md-4', 'col-sm-6', 'mb-4', 'product-card'); // Responsive grid classes

                productCard.innerHTML = `
                    <div class="card">
                        <img class="card-img-top" src="${product.image}" alt="${product.title}">
                        <div class="card-body">
                            <h5 class="card-title">${product.title}</h5>
                            <p class="card-text">${product.description.slice(0, 100)}...</p>
                            <div class="price">$${product.price}</div>
                            <button class="add-to-cart btn btn-primary" onclick="addToCart(${product.id})">Add to Cart</button>
                        </div>
                    </div>
                `;
                productContainer.appendChild(productCard);
            });
        }


function addToCart(productId) {
  const product = products.find(p => p.id === productId);
    if (product) {
      let cart = JSON.parse(localStorage.getItem('cart')) || [];
      const existingProductIndex = cart.findIndex(p => p.id === productId);
      if (existingProductIndex === -1) {
        cart.push(product);
      }
        localStorage.setItem('cart', JSON.stringify(cart));
         alert(`${product.title} has been added to the cart!`);
            }
        }