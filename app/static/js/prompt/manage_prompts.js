$(document).ready(function () {
    console.log('Управление промптами подключилось');
    const token = localStorage.getItem('access_token');

    // Если токен отсутствует, перенаправляем на домашнюю страницу
    if (!token) {
        console.warn('JWT токен отсутствует. Перенаправление на главную страницу.');
        window.location.href = '/';
    } else {
        // Проверка валидности токена на сервере
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function (response) {
                loadPrompts();
                console.log('Токен валидный, пользователь: ', response.logged_in_as);
            },
            error: function (xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    // Функция для загрузки промптов
    function loadPrompts() {
        console.log('Загрузка промптов...');
        $.ajax({
            url: '/prompt/all',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function (response) {
                const promptList = $('#promptList');
                promptList.empty(); // Очищаем перед обновлением списка
                console.log('Промпты успешно загружены:', response.prompt_data);

                response.prompt_data.forEach(prompt => {
                    promptList.append(`
                        <tr class="clickable-row" data-id="${prompt.prompt_id}">
                            <td>${prompt.prompt_name}</td>
                            <td>${prompt.text}</td>
                            <td>
                                <input type="checkbox" class="use-automatic" data-id="${prompt.prompt_id}" ${prompt.use_automatic ? 'checked' : ''} />
                            </td>
                            <td>
                                <div class="dropdown">
                                    <span class="dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="cursor: pointer;">&#x22EE;</span>
                                    <div class="dropdown-menu">
                                        <a class="dropdown-item" href="/prompt/${prompt.prompt_id}/view">Подробнее</a>
                                        <a class="dropdown-item" href="/prompt/${prompt.prompt_id}">Редактировать</a>
                                        <a class="dropdown-item delete-prompt" href="#" data-id="${prompt.prompt_id}">Удалить</a>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    `);
                });

                // Обработчик для изменения флага
                $('.use-automatic').change(function (event) {
                    event.stopPropagation(); // Остановить всплытие события
                    const promptId = $(this).data('id');
                    const isChecked = $(this).is(':checked');
                    console.log(`Изменение флага "Использовать автоматически" для промпта ID: ${promptId} на ${isChecked}`);

                    // Сбрасываем флаг для других промптов
                    if (isChecked) {
                        $('.use-automatic').not(this).prop('checked', false); // Сбрасываем другие чекбоксы
                        $('.use-automatic').not(this).trigger('change'); // Вызов события change для сброса флагов на сервере
                    }

                    // Отправка запроса на изменение флага
                    $.ajax({
                        url: `/prompt/${promptId}/set_automatic`,
                        type: 'PATCH',
                        data: JSON.stringify({ use_automatic: isChecked }),
                        contentType: 'application/json',
                        headers: {
                            'Authorization': 'Bearer ' + token
                        },
                        success: function (response) {
                            console.log('Флаг успешно обновлён:', response);
                        },
                        error: function (xhr, status, error) {
                            console.error('Ошибка при обновлении флага:', status, error);
                        }
                    });
                });

                // Обработчик для клика по строкам
                $('.clickable-row').on('click', function (event) {
                    // Проверяем, был ли клик на элементе внутри строки, который не должен вызывать переход
                    const target = $(event.target);
                    if (!target.closest('.delete-prompt').length && !target.closest('.use-automatic').length) {
                        const promptId = $(this).data('id');
                        window.location.href = `/prompt/${promptId}`; // Переход на страницу просмотра
                    }
                });

                // Обработчик для удаления промптов
                attachDeleteHandler(); // Присоединяем обработчик удаления
            },
            error: function (xhr, status, error) {
                console.error('Ошибка загрузки промптов:', status, error);
            }
        });
    }

    // Функция для присоединения обработчика для удаления промптов
    function attachDeleteHandler() {
        $('.delete-prompt').off('click').on('click', function (event) {
            event.preventDefault(); // Предотвращаем переход по ссылке
            const promptId = $(this).data('id');
            deletePrompt(promptId);
        });
    }

    // Функция для удаления промпта
    function deletePrompt(prompt_id) {
        if (confirm('Are you sure you want to delete this prompt?')) {
            console.log(`Удаление промпта ID: ${prompt_id}`);
            $.ajax({
                url: `/prompt/${prompt_id}/delete`,
                type: 'DELETE',
                headers: {
                    'Authorization': 'Bearer ' + token
                },
                success: function () {
                    loadPrompts();  // Перезагрузить список после удаления
                    console.log(`Промпт ID: ${prompt_id} успешно удалён.`);
                },
                error: function (xhr, status, error) {
                    console.error('Ошибка удаления промпта:', status, error);
                    alert('Ошибка удаления промпта. Пожалуйста, попробуйте снова.');
                }
            });
        }
    }
});
