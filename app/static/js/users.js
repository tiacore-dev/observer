$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let usersLoaded = false;
    let usersData = [];

    if (!token) {
        console.warn('JWT токен отсутствует. Перенаправление на главную страницу.');
        window.location.href = '/';
    } else {
        console.log('Токен найден, проверяем его валидность...');
        // Проверка валидности токена на сервере
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                Authorization: 'Bearer ' + token,
            },
            success: function (response) {
                console.log('Токен валиден, пользователь:', response.logged_in_as);
                console.log('Загружаем пользователей...');
                loadUsers();
            },
            error: function (xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                console.warn('Перенаправляем на главную страницу...');
                window.location.href = '/';
            },
        });
    }

    function showError(message) {
        console.error('Ошибка:', message);
        $('#error').text(message).show();
    }

    function loadUsers() {
        console.log('Запрашиваем список пользователей...');
        $.ajax({
            url: '/api/users',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (users) {
                console.log('Список пользователей успешно загружен:', users);
                usersData = users;
                usersLoaded = true;
                renderUsers(usersData);
                $('#content').show();
            },
            error: function () {
                showError('Ошибка загрузки пользователей.');
            },
        });
    }

    function renderUsers(users) {
        console.log('Рендерим таблицу пользователей...');
        const userTable = $('#userTable');
        userTable.empty();

        users.forEach(user => {
            console.log(`Рендерим пользователя: ${user.user_id} (${user.username || 'Без имени'})`);
            const userRow = $(`
                <tr>
                    <td>${user.user_id}</td>
                    <td>${user.login}</td>
                    <td>
                        <input type="text" class="form-control username-input" data-user-id="${user.user_id}" value="${user.username || ''}">
                    </td>
                    <td>
                        <button class="btn btn-primary save-user-btn" data-user-id="${user.user_id}">Сохранить</button>
                    </td>
                </tr>
            `);
            userTable.append(userRow);
        });

        $('.save-user-btn').on('click', function () {
            const userId = $(this).data('user-id');
            const username = $(`.username-input[data-user-id="${userId}"]`).val();

            saveUser(userId, username);
        });
    }

    function saveUser(userId, username) {
        console.log(`Сохраняем имя пользователя ${username} для ID ${userId}...`);
        $.ajax({
            url: `/users/${userId}/edit`,
            type: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ username }),
            success: function () {
                console.log(`Имя пользователя ${username} для ID ${userId} успешно сохранено.`);
                alert('Имя пользователя успешно обновлено.');
            },
            error: function () {
                showError('Ошибка при сохранении имени пользователя.');
            }
        });
    }

    $('#updateUsersButton').on('click', function () {
        console.log('Обновляем пользователей...');
        $.ajax({
            url: '/api/users/update',
            type: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            contentType: 'application/json',
            success: function (response) {
                console.log('Пользователи успешно обновлены:', response);
                alert('Пользователи успешно обновлены.');
                loadUsers();
            },
            error: function () {
                showError('Ошибка при обновлении пользователей.');
            },
        });
    });
});
