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

    // Обработчик для формы редактирования промпта
    $('#editPromptForm').on('submit', function(event) {
        event.preventDefault();

        const prompt_id = $('#editPromptForm').data('prompt-id');  // Получаем ID промпта из атрибута data
        
        const prompt_name = $('#prompt_name').val();  // Получаем название промпта
        const text = $('#text').val(); // Получаем текст

        $.ajax({
            url: `/prompt/${prompt_id}/edit`,
            type: 'PATCH',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            contentType: 'application/json',
            data: JSON.stringify({ prompt_name: prompt_name, text: text }),  // Отправляем и название, и текст
            success: function() {
                window.location.href = '/manage_prompts';
            },
            error: function(xhr, status, error) {
                console.error('Ошибка редактирования промпта:', status, error);
            }
        });
    });
});
