const hamburger = document.getElementById('hamburger');
const navigation = document.getElementById('navigation');

function toggleBurgerMenu(){
    hamburger.classList.toggle('active');
    navigation.classList.toggle('active');
}

hamburger.addEventListener('click', toggleBurgerMenu);

const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () =>{
        hamburger.classList.remove('active');
        navigation.classList.remove('active');
    });
});