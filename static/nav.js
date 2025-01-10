const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links'); // Use the correct id here

function toggleMenu() {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
}

hamburger.addEventListener('click', toggleMenu);

const links = document.querySelectorAll('.nav-link');
links.forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});
