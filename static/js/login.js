document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault();

    var type = document.getElementById('type').value;
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    var userRole;
    if (type === 'staff') {
        userRole = 'admin';
    } else if (type === 'student') {
        userRole = 'student';
    } else {
        alert('Invalid credentials!');
        return;
    }

    localStorage.setItem('userRole', userRole);

    // Example AJAX request for login
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            // Redirect to appropriate dashboard
            if (response.role === 'admin') {
                window.location.href = 'index';
            } else {
                window.location.href = 'index3';
            }
        } else {
            alert('Login failed!');
        }
    };
    xhr.send(JSON.stringify({ username: username, password: password, type: type }));
});
