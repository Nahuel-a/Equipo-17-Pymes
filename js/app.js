class User {
    constructor(id, name, lastname, email, password) {
        this.id = id;
        this.name = name;
        this.lastname = lastname;
        this.email = email;
        this.password = password;
    }
}

class UserDB {
    constructor() {
        this.dbName = 'creditbusters_users_db';
        this.users = this._load();
    }

    _load() {
        const usersJson = localStorage.getItem(this.dbName);
        return usersJson ? JSON.parse(usersJson) : [];
    }

    _save() {
        localStorage.setItem(this.dbName, JSON.stringify(this.users));
    }

    addUser({ name, lastname, email, password }) {
        const id = Date.now().toString();
        const newUser = new User(id, name, lastname, email, password);
        this.users.push(newUser);
        this._save();
        return newUser;
    }

    findUserByEmail(email) {
        return this.users.find(user => user.email.toLowerCase() === email.toLowerCase());
    }

    updateUserPassword(email, newPassword) {
        const user = this.findUserByEmail(email);
        if (user) {
            user.password = newPassword;
            this._save();
            return true;
        }
        return false;
    }
}

class App {
    constructor() {
        this.db = new UserDB();
        this._route();
        this._setupCommonListeners();
    }

    _route() {
        const path = window.location.pathname.split("/").pop();
        this._displayFlashMessage(); // Display flash on every page load

        if (path === 'dashboard.html') {
            this._setupDashboardPage();
        } else if (['log-in.html', 'register-user.html', 'password-user.html', 'reset-password.html'].includes(path)) {
            this._setupAuthPage();
        } else {
            this._setupHomePage(); // index.html and other pages are public
        }
    }

    _setupHomePage() {
        // Lógica para la página de inicio pública (si es necesario)
        // Ya no se requiere autenticación aquí
    }

    _setupDashboardPage() {
        const loggedInUser = JSON.parse(localStorage.getItem('loggedInUser'));
        if (!loggedInUser) {
            window.location.href = 'log-in.html';
            return;
        }

        const welcomeEl = document.getElementById('welcome-message');
        if (welcomeEl) {
            welcomeEl.textContent = `Hola, ${loggedInUser.name}`;
        }

        const userInfoEl = document.getElementById('user-info');
        if (userInfoEl) {
            const logoutBtn = document.createElement('button');
            logoutBtn.textContent = 'Cerrar Sesión';
            logoutBtn.className = 'btn btn-secondary';
            logoutBtn.onclick = () => {
                localStorage.removeItem('loggedInUser');
                this._setFlashMessage('Has cerrado sesión.', 'success');
                window.location.href = 'log-in.html';
            };
            userInfoEl.appendChild(logoutBtn);
        }
    }

    _setupAuthPage() {
        const form = document.querySelector('.auth-form');
        if (!form) return;

        if (localStorage.getItem('loggedInUser')) {
            window.location.href = 'dashboard.html';
            return;
        }

        switch (form.id) {
            case 'registerForm': this._setupRegistrationPage(); break;
            case 'loginForm': this._setupLoginPage(); break;
            case 'recoveryForm': this._setupRecoveryPage(); break;
            case 'resetPasswordForm': this._setupResetPasswordPage(); break;
        }
    }

    _setupCommonListeners() {
        document.querySelectorAll('.btn-toggle-password').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.previousElementSibling;
                const icon = btn.querySelector('i');
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                }
            });
        });
    }

    _displayMessage(text, type) {
        const container = document.getElementById('message-container');
        container.innerHTML = `<div class="message ${type}">${text}</div>`;
    }

    _setFlashMessage(message, type) {
        sessionStorage.setItem('flashMessage', JSON.stringify({ message, type }));
    }

    _displayFlashMessage() {
        const flash = sessionStorage.getItem('flashMessage');
        if (flash) {
            const { message, type } = JSON.parse(flash);
            const container = document.getElementById('flash-message-container');
            if(container) {
                container.innerHTML = `<div class="flash-message ${type}">${message}</div>`;
                sessionStorage.removeItem('flashMessage');
            }
        }
    }

    _setLoading(form, isLoading) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner');
        if (!submitBtn) return;
        submitBtn.disabled = isLoading;
        if (spinner) spinner.style.display = isLoading ? 'inline-block' : 'none';
        if (btnText) btnText.style.display = isLoading ? 'none' : 'inline-block';
    }

    _setupRegistrationPage() {
        const form = document.getElementById('registerForm');
        const state = { name: false, lastname: false, email: false, passwordStrength: false, passwordMatch: false };

        const checkFormState = () => {
            form.querySelector('button[type="submit"]').disabled = !Object.values(state).every(Boolean);
        };

        form.name.addEventListener('input', () => { state.name = form.name.value.trim() !== ''; checkFormState(); });
        form.lastname.addEventListener('input', () => { state.lastname = form.lastname.value.trim() !== ''; checkFormState(); });

        form.email.addEventListener('input', () => {
            const feedbackEl = form.email.nextElementSibling;
            if (!/.+@.+\..+/.test(form.email.value)) {
                feedbackEl.textContent = 'Debe ser un email válido.'; state.email = false;
            } else if (this.db.findUserByEmail(form.email.value)) {
                feedbackEl.textContent = 'Este email ya está en uso.'; state.email = false;
            } else {
                feedbackEl.textContent = 'Email disponible.'; state.email = true;
            }
            feedbackEl.className = `form-feedback ${state.email ? 'valid' : 'invalid'}`;
            checkFormState();
        });

        const strengthEl = document.getElementById('password-strength-feedback');
        const requirements = {
            length: { el: strengthEl.querySelector('[data-requirement="length"]'), regex: /.{8,}/ },
            uppercase: { el: strengthEl.querySelector('[data-requirement="uppercase"]'), regex: /[A-Z]/ },
            lowercase: { el: strengthEl.querySelector('[data-requirement="lowercase"]'), regex: /[a-z]/ },
            number: { el: strengthEl.querySelector('[data-requirement="number"]'), regex: /[0-9]/ },
            special: { el: strengthEl.querySelector('[data-requirement="special"]'), regex: /[!@#$%^&*(),.?":{}|<>]/ }
        };

        form.password.addEventListener('input', () => {
            let allReqsMet = true;
            for (const key in requirements) {
                const req = requirements[key];
                const met = req.regex.test(form.password.value);
                if (req.el) { // Defensive check
                    req.el.classList.toggle('valid', met);
                }
                if (!met) allReqsMet = false;
            }
            state.passwordStrength = allReqsMet;
            validatePasswordsMatch();
        });

        const validatePasswordsMatch = () => {
            const matchFeedbackEl = form.confirmPassword.parentElement.nextElementSibling;
            state.passwordMatch = form.password.value === form.confirmPassword.value && form.confirmPassword.value.length > 0;
            matchFeedbackEl.textContent = state.passwordMatch ? 'Las contraseñas coinciden.' : (form.confirmPassword.value.length > 0 ? 'No coinciden.' : '');
            matchFeedbackEl.className = `form-feedback ${state.passwordMatch ? 'valid' : 'invalid'}`;
            checkFormState();
        };

        form.confirmPassword.addEventListener('input', validatePasswordsMatch);

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this._setLoading(form, true);
            setTimeout(() => {
                this.db.addUser({ name: form.name.value, lastname: form.lastname.value, email: form.email.value, password: form.password.value });
                this._setFlashMessage('¡Registro Exitoso! Ahora puedes iniciar sesión.', 'success');
                window.location.href = 'log-in.html';
            }, 1000);
        });
    }

    _setupLoginPage() {
        const form = document.getElementById('loginForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this._setLoading(form, true);

            setTimeout(() => {
                const email = form.email.value;
                const password = form.password.value;
                const user = this.db.findUserByEmail(email);

                if (user && user.password === password) {
                    localStorage.setItem('loggedInUser', JSON.stringify({ email: user.email, name: user.name }));
                    this._setFlashMessage(`¡Bienvenido de nuevo, ${user.name}!`, 'success');
                    window.location.href = 'dashboard.html';
                } else {
                    this._displayMessage('El email o la contraseña son incorrectos.', 'error');
                    this._setLoading(form, false);
                }
            }, 1000);
        });
    }

    _setupRecoveryPage() {
        const form = document.getElementById('recoveryForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this._setLoading(form, true);

            setTimeout(() => {
                const email = form.email.value;
                if (this.db.findUserByEmail(email)) {
                    sessionStorage.setItem('recoveryEmail', email);
                    this._setFlashMessage('Se ha enviado un enlace para restablecer tu contraseña.', 'success');
                    window.location.href = 'reset-password.html';
                } else {
                    this._displayMessage('No se encontró ninguna cuenta con ese email.', 'error');
                    this._setLoading(form, false);
                }
            }, 1000);
        });
    }

    _setupResetPasswordPage() {
        const form = document.getElementById('resetPasswordForm');
        const recoveryEmail = sessionStorage.getItem('recoveryEmail');

        if (!recoveryEmail) {
            window.location.href = 'password-user.html';
            return;
        }

        const state = { passwordStrength: false, passwordMatch: false };
        const checkFormState = () => {
            form.querySelector('button[type="submit"]').disabled = !Object.values(state).every(Boolean);
        };

        const strengthEl = document.getElementById('password-strength-feedback');
        const requirements = {
            length: { el: strengthEl.querySelector('[data-requirement="length"]'), regex: /.{8,}/ },
            uppercase: { el: strengthEl.querySelector('[data-requirement="uppercase"]'), regex: /[A-Z]/ },
            lowercase: { el: strengthEl.querySelector('[data-requirement="lowercase"]'), regex: /[a-z]/ },
            number: { el: strengthEl.querySelector('[data-requirement="number"]'), regex: /[0-9]/ },
            special: { el: strengthEl.querySelector('[data-requirement="special"]'), regex: /[!@#$%^&*(),.?":{}|<>]/ }
        };

        form.password.addEventListener('input', () => {
            let allReqsMet = true;
            for (const key in requirements) {
                const req = requirements[key];
                const met = req.regex.test(form.password.value);
                if (req.el) { // Defensive check
                    req.el.classList.toggle('valid', met);
                }
                if (!met) allReqsMet = false;
            }
            state.passwordStrength = allReqsMet;
            validatePasswordsMatch();
        });

        const validatePasswordsMatch = () => {
            const matchFeedbackEl = form.confirmPassword.parentElement.nextElementSibling;
            state.passwordMatch = form.password.value === form.confirmPassword.value && form.confirmPassword.value.length > 0;
            matchFeedbackEl.textContent = state.passwordMatch ? 'Las contraseñas coinciden.' : (form.confirmPassword.value.length > 0 ? 'No coinciden.' : '');
            matchFeedbackEl.className = `form-feedback ${state.passwordMatch ? 'valid' : 'invalid'}`;
            checkFormState();
        };

        form.confirmPassword.addEventListener('input', validatePasswordsMatch);
        checkFormState();

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!state.passwordStrength || !state.passwordMatch) return;

            this._setLoading(form, true);

            setTimeout(() => {
                this.db.updateUserPassword(recoveryEmail, form.password.value);
                sessionStorage.removeItem('recoveryEmail');
                this._setFlashMessage('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success');
                window.location.href = 'log-in.html';
            }, 1000);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => new App());