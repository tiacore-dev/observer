$(document).ready(function() {
    // Проверка наличия токена в localStorage
    const token = localStorage.getItem('access_token');

    // Если токен отсутствует, перенаправляем на страницу home
    if (!token) {
        window.location.href = '/';
    } else {
        // Проверка валидности токена с сервером
        $.ajax({
            url: '/protected',  // Защищенный маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Токен валидный, пользователь: ', response.logged_in_as);

                // Запрос имени пользователя
                $.ajax({
                    url: '/get_username',  // Маршрут для получения имени пользователя
                    type: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + token
                    },
                    success: function(username) {
                        // Вставляем имя пользователя в HTML
                        $('#username').text(username);
                    },
                    error: function(xhr, status, error) {
                        console.error('Ошибка получения имени пользователя:', error);
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }
    

});