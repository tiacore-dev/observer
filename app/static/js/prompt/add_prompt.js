$(document).ready(function() {
    console.log('Добавление нового промпта подключилось');
    const token = localStorage.getItem('access_token');

    // Если токен отсутствует, перенаправляем на домашнюю страницу
    if (!token) {
        window.location.href = '/';
    } else {
        // Проверка валидности токена на сервере
        $.ajax({
            url: '/protected',  // Защищённый маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Токен валидный, пользователь: ', response.logged_in_as);
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                // Если токен недействителен, перенаправляем на домашнюю страницу
                window.location.href = '/';
            }
        });
    }

    // Обработчик для кнопки "Назад"
    $('#backButton').on('click', function() {
        window.location.href = '/manage_prompts';  // Перенаправляем на страницу /manage_prompts
    });

    // Остальной код для обработки добавления нового промпта
    $('#promptForm').on('submit', function(event) {
        event.preventDefault();

        const prompt_name = $('#prompt_name').val(); // Получаем значение имени промпта
        const text = $('#text').val(); // Получаем текст

        // Проверка, что prompt_name не пустой
        if (!prompt_name || !text) {
            console.error('Prompt name and text must be provided.');
            return;
        }

        $.ajax({
            url: '/prompt/add',
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            contentType: 'application/json', // Указываем, что отправляем JSON
            data: JSON.stringify({  // Преобразуем данные в JSON
                prompt_name: prompt_name,
                text: text
            }),
            success: function() {
                $('#promptForm')[0].reset(); // Сброс формы
                alert('Промпт добавлен успешно!');
                

            },
            error: function(xhr, status, error) {
                console.error('Ошибка при добавлении промпта:', status, error);
            }
        });
    });
});