$(document).ready(function() {
    const token = localStorage.getItem('access_token');

    if (!token) {
        window.location.href = '/';
        return;
    }

    loadAccount();

    function loadAccount() {
    
        $.ajax({
            url: '/api/accounts/info',  // <== не забудь, какой префикс у тебя
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(data) {
                $('#username').text(data.username);
                $('#company_name').text(data.company_name);
            },
            error: function(xhr, status, error) {
                console.error('Ошибка получения информации о пользователе:', error);
                $('#username').text('Ошибка');
                $('#company_name').text('Ошибка');
                // Можно не редиректить, а просто показать ошибку
            }
        });
    }
});
