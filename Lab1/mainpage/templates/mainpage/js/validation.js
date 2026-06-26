// Валидация полей в реальном времени
document.addEventListener('DOMContentLoaded', function() {

    // Функция валидации имени и фамилии
    function validateName(input, errorId) {
        const value = input.value;
        const errorElement = document.getElementById(errorId);
        const nameRegex = /^[A-ZА-Я][a-zа-я]*$/;

        if (value.length === 0) {
            errorElement.textContent = 'Поле обязательно для заполнения';
            input.classList.remove('valid', 'invalid');
            return false;
        }

        if (!nameRegex.test(value)) {
            errorElement.textContent = 'Только буквы, первая заглавная';
            input.classList.remove('valid');
            input.classList.add('invalid');
            return false;
        }

        errorElement.textContent = '';
        input.classList.remove('invalid');
        input.classList.add('valid');
        return true;
    }

    // Функция валидации логина
    function validateUsername(input, errorId) {
        const value = input.value;
        const errorElement = document.getElementById(errorId);

        if (value.length === 0) {
            errorElement.textContent = 'Поле обязательно для заполнения';
            input.classList.remove('valid', 'invalid');
            return false;
        }

        if (value.length < 3) {
            errorElement.textContent = 'Минимум 3 символа';
            input.classList.remove('valid');
            input.classList.add('invalid');
            return false;
        }

        if (value.length > 150) {
            errorElement.textContent = 'Максимум 150 символов';
            input.classList.remove('valid');
            input.classList.add('invalid');
            return false;
        }

        errorElement.textContent = '';
        input.classList.remove('invalid');
        input.classList.add('valid');
        return true;
    }

    // Функция валидации email
    function validateEmail(input, errorId) {
        const value = input.value;
        const errorElement = document.getElementById(errorId);
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (value.length === 0) {
            errorElement.textContent = 'Поле обязательно для заполнения';
            input.classList.remove('valid', 'invalid');
            return false;
        }

        if (!emailRegex.test(value)) {
            errorElement.textContent = 'Введите корректный email (example@mail.com)';
            input.classList.remove('valid');
            input.classList.add('invalid');
            return false;
        }

        errorElement.textContent = '';
        input.classList.remove('invalid');
        input.classList.add('valid');
        return true;
    }

    // Функция валидации пароля
    function validatePassword(input, errorId) {
        const value = input.value;
        const errorElement = document.getElementById(errorId);

        if (value.length === 0) {
            errorElement.textContent = 'Поле обязательно для заполнения';
            input.classList.remove('valid', 'invalid');
            return false;
        }

        if (value.length < 8) {
            errorElement.textContent = 'Минимум 8 символов';
            input.classList.remove('valid');
            input.classList.add('invalid');
            return false;
        }

        errorElement.textContent = '';
        input.classList.remove('invalid');
        input.classList.add('valid');
        return true;
    }

    // Функция проверки совпадения паролей
    function validatePasswordMatch(password1, password2, errorId) {
        const errorElement = document.getElementById(errorId);

        if (password2.value.length === 0) {
            errorElement.textContent = 'Подтвердите пароль';
            password2.classList.remove('valid', 'invalid');
            return false;
        }

        if (password1.value !== password2.value) {
            errorElement.textContent = 'Пароли не совпадают';
            password2.classList.remove('valid');
            password2.classList.add('invalid');
            return false;
        }

        errorElement.textContent = '';
        password2.classList.remove('invalid');
        password2.classList.add('valid');
        return true;
    }

    // ==== Регистрация ====
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const firstName = registerForm.querySelector('#id_first_name');
        const lastName = registerForm.querySelector('#id_last_name');
        const username = registerForm.querySelector('#id_username');
        const email = registerForm.querySelector('#id_email');
        const password1 = registerForm.querySelector('#id_password1');
        const password2 = registerForm.querySelector('#id_password2');

        // События для подсветки и валидации
        firstName.addEventListener('input', function() {
            validateName(this, 'first_name_error');
        });

        lastName.addEventListener('input', function() {
            validateName(this, 'last_name_error');
        });

        username.addEventListener('input', function() {
            validateUsername(this, 'username_error');
        });

        email.addEventListener('input', function() {
            validateEmail(this, 'email_error');
        });

        password1.addEventListener('input', function() {
            validatePassword(this, 'password1_error');
            if (password2.value.length > 0) {
                validatePasswordMatch(this, password2, 'password2_error');
            }
        });

        password2.addEventListener('input', function() {
            validatePasswordMatch(password1, this, 'password2_error');
        });

        // Отправка формы
        registerForm.addEventListener('submit', function(e) {
            let isValid = true;

            // Проверяем все поля
            if (!validateName(firstName, 'first_name_error')) isValid = false;
            if (!validateName(lastName, 'last_name_error')) isValid = false;
            if (!validateUsername(username, 'username_error')) isValid = false;
            if (!validateEmail(email, 'email_error')) isValid = false;
            if (!validatePassword(password1, 'password1_error')) isValid = false;
            if (!validatePasswordMatch(password1, password2, 'password2_error')) isValid = false;

            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, исправьте ошибки в форме');
            }
        });
    }

    // ==== Вход ====
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const loginUsername = loginForm.querySelector('#id_username');
        const loginPassword = loginForm.querySelector('#id_password');

        loginUsername.addEventListener('input', function() {
            if (this.value.length > 0) {
                this.classList.remove('invalid');
                this.classList.add('valid');
                document.getElementById('login_username_error').textContent = '';
            } else {
                this.classList.remove('valid');
                this.classList.add('invalid');
                document.getElementById('login_username_error').textContent = 'Введите логин';
            }
        });

        loginPassword.addEventListener('input', function() {
            if (this.value.length > 0) {
                this.classList.remove('invalid');
                this.classList.add('valid');
                document.getElementById('login_password_error').textContent = '';
            } else {
                this.classList.remove('valid');
                this.classList.add('invalid');
                document.getElementById('login_password_error').textContent = 'Введите пароль';
            }
        });
    }
});