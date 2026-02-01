let mode = 'login';

function togglePassword() {
    const passInput = document.getElementById('password-field');
    const eyeIcon = document.getElementById('eye-icon');
    if (passInput.type === 'password') {
        passInput.type = 'text';
        eyeIcon.classList.add('text-blue-500');
    } else {
        passInput.type = 'password';
        eyeIcon.classList.remove('text-blue-500');
    }
}

function switchMode() {
    mode = mode === 'login' ? 'register' : 'login';
    document.getElementById('auth-title').innerText = mode === 'login' ? 'ORBIT LOGIN' : 'ORBIT REGISTER';
    document.getElementById('auth-btn').innerText = mode === 'login' ? 'Zaloguj się' : 'Zarejestruj się';
    document.getElementById('mode-toggle-text').innerText = mode === 'login' ? 'Nie masz konta? Zarejestruj się' : 'Masz już konto? Zaloguj się';
    document.getElementById('error-msg').classList.add('hidden');
}

document.getElementById('auth-form').onsubmit = async (e) => {
    e.preventDefault();
    const errorMsg = document.getElementById('error-msg');

    try {
        const res = await fetch(`/api/${mode}`, {
            method: 'POST',
            body: new FormData(e.target)
        });
        const data = await res.json();

        if (res.ok) {
            if (mode === 'login') {
                window.location.href = '/dashboard';
            } else {
                alert("Konto utworzone! Teraz możesz się zalogować.");
                switchMode();
            }
        } else {
            errorMsg.innerText = data.message || "Wystąpił błąd";
            errorMsg.classList.remove('hidden');
        }
    } catch (err) {
        errorMsg.innerText = "Błąd połączenia z serwerem";
        errorMsg.classList.remove('hidden');
    }
};