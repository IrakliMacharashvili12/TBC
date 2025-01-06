function toggleForms(showLogin) {
      document.getElementById('registerForm').style.display = showLogin ? 'none' : 'block';
      document.getElementById('loginForm').style.display = showLogin ? 'block' : 'none';
}
function autoDismissFlashMessages() {
     setTimeout(() => {
     const flashMessages = document.getElementById('flash-messages');
     if (flashMessages) {
            flashMessages.style.display = 'none';
        }
     }, 2000);
}