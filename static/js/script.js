let usernameInput = document.querySelector('.username');
let passwordInput = document.querySelector('.password');
let showPasswordButton = document.querySelector('.password-button');
let face = document.querySelector('.face');

// Handle focus on the password input
passwordInput.addEventListener('focus', function(event) {
    document.querySelectorAll('.hand').forEach(hand => {
        hand.classList.add('hide');
    });
});

// Handle blur on the password input
passwordInput.addEventListener('blur', function(event) {
    document.querySelectorAll('.hand').forEach(hand => {
        hand.classList.remove('hide');
        hand.classList.remove('peek');
    });
});

// Handle focus on the username input
usernameInput.addEventListener('focus', event => {
    let length = Math.min(usernameInput.value.length - 16, 19);
    document.querySelectorAll('.hand').forEach(hand => {
        hand.classList.remove('hide');
        hand.classList.remove('peek');
    });

    face.style.setProperty('--rotate-head', `${-length}deg`);
});

// Handle blur on the username input
usernameInput.addEventListener('blur', event => {
    face.style.setProperty('--rotate-head', '0deg');
});

// Handle input on the username field
usernameInput.addEventListener('input', event => {
    let length = Math.min(usernameInput.value.length - 16, 19);
    face.style.setProperty('--rotate-head', `${-length}deg`);
});

// Show or hide the password
showPasswordButton.addEventListener('click', event => {
    if (passwordInput.type === 'text') {
        passwordInput.type = 'password';

        document.querySelectorAll('.hand').forEach(hand => {
            hand.classList.remove('peek');
            hand.classList.add('hide');
        });
    } else if (passwordInput.type === 'password') {
        passwordInput.type = 'text';

        document.querySelectorAll('.hand').forEach(hand => {
            hand.classList.remove('hide');
            hand.classList.add('peek');
        });
    }
});
