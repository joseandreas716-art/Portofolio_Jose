// Admin Login scripting
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const usernameInput = document.querySelector('#username');
            const passwordInput = document.querySelector('#password');
            if (usernameInput && passwordInput) {
                if (!usernameInput.value.strip() || !passwordInput.value) {
                    e.preventDefault();
                    alert('Harap isi username dan password.');
                }
            }
        });
    }
});
