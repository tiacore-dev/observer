$(document).ready(function() {
    // Проверка, есть ли боковое меню и jwt токен
    const hasSidebar = $('#sidebar').length > 0;

    if (localStorage.getItem('access_token')) {
         $('#logoutButton').show();
        if (hasSidebar) {
            $('#sidebar').show();  // Показываем боковое меню
        } else {
            $('#sidebar').hide();  // Если бокового меню нет, скрываем
            $('#content-wrapper').addClass('sidebar-hidden');  // Добавляем класс для центрирования контента
        }
    } else {
        $('#logoutButton').hide();  // Скрываем кнопку выхода, если нет токена
        $('#sidebar').hide();  // Скрываем боковое меню
        $('#content-wrapper').addClass('sidebar-hidden');  // Центрируем контент
    }

    function adjustSidebar() {
        const navbarHeight = $('.navbar').outerHeight();
        $('.sidebar').css('top', navbarHeight + 'px'); // Устанавливаем верхнее положение сайдбара
        $('#main-content').css('padding-top', navbarHeight + 'px'); // Увеличиваем верхний отступ для основного контента
    }

    adjustSidebar(); // Настраиваем сайдбар при загрузке страницы

    $(window).resize(function() {
        adjustSidebar(); // Перенастраиваем сайдбар при изменении размера окна
    });

    // Функция для обновления токена
    function refreshAccessToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            console.error('Refresh token отсутствует.');
            return;
        }
    
        console.log('Обновление токена. Refresh token:', refreshToken);
    
        return $.ajax({
            url: '/auth/refresh',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ refresh_token: refreshToken }),
            success: function(response) {
                console.log('Токен успешно обновлен. Новый токен:', response.access_token);
                saveTokens(response.access_token, refreshToken);
            },
            error: function(xhr) {
                console.error('Ошибка при обновлении токена. Статус:', xhr.status);
                window.location.href = '/';  // Редирект при неудачном обновлении
            }
        });
    }
    

    // Функция для выполнения запроса с проверкой access token
    function withAuthRequest(settings) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        settings.headers = { ...settings.headers, 'Authorization': `Bearer ${token}` };
        
        return $.ajax(settings).fail(async function(xhr) {
            if (xhr.status === 401) { // Если access token истек
                await refreshAccessToken();
                // Повторный запрос после обновления токена
                settings.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
                return $.ajax(settings);
            } else {
                console.error('Ошибка при выполнении запроса:', xhr);
            }
        });
    }

    // Функция для сохранения токенов в localStorage
    function saveTokens(accessToken, refreshToken) {
        console.log('Сохранение токенов. Access token:', accessToken, 'Refresh token:', refreshToken);
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }


    // Форма входа
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        let username = $('#username').val();
        let password = $('#password').val();

        $.ajax({
            url: '/auth/token',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                saveTokens(response.access_token, response.refresh_token);
                $('#loginAlert').html('<div class="alert alert-success">Login successful!</div>');
                
                setTimeout(() => {
                    window.location.href = '/account';
                }, 300);  // Даем браузеру чуть-чуть времени записать токены
            },
            error: function(xhr) {
                let errorMsg = 'An error occurred.';
                if (xhr.responseJSON && xhr.responseJSON.msg) {
                    errorMsg = xhr.responseJSON.msg;
                }
                $('#loginAlert').html(`<div class="alert alert-danger">${errorMsg}</div>`);
            }
        });
    });

    // Кнопка выхода
    $('#logoutButton').on('click', function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
    });



    // Таймер для регулярного обновления токена
    function startTokenRefreshInterval() {
        setInterval(refreshAccessToken, 15 * 60 * 1000); // Обновление каждые 15 минут
    }

    if (localStorage.getItem('refresh_token')) {
        startTokenRefreshInterval();
    }

    // Флаг активности пользователя
    let userActive = true;

    // Сброс флага активности при любом действии пользователя
    $(document).on('mousemove click keypress', function() {
        userActive = true;
    });

    // Функция для обновления токена при активности пользователя
    function checkAndRefreshToken() {
        if (userActive) {
            refreshAccessToken();
            userActive = false; // Сбрасываем флаг после обновления токена
        }
    }

    // Таймер для проверки активности пользователя и обновления токена
    setInterval(checkAndRefreshToken, 10 * 60 * 1000); // Проверка активности каждые 10 минут
});
