$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let offset = 0;
    const limit = 10;
    let currentPage = 1;
    let totalPages = 1;

    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function () {
                loadAnalyses();
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    function formatDate(timestamp) {
        if (!timestamp) {
            console.log("formatDate: timestamp отсутствует или null", timestamp);
            return "Не указано";
        }
    
        console.log("formatDate: обработка timestamp", timestamp);
        return moment.utc(timestamp).local().format("DD.MM.YYYY HH:mm:ss");
    }
    
    

    function loadAnalyses() {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/analysis/all?offset=${offset}&limit=${limit}`,
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function (response) {
                $('#loadingIndicator').hide();
                const tableBody = $('#analysisTable tbody');
                tableBody.empty();
    
                if (response.analyses.length === 0) {
                    tableBody.append('<tr><td colspan="4">Нет доступных анализов.</td></tr>');
                    return;
                }
                console.log("Полученные анализы:", response.analyses);

    
                response.analyses.forEach(function (analysis, index) {
                    const rowNumber = offset + index + 1;
                    const trimmedFilters = analysis.filters ? JSON.stringify(analysis.filters) : 'Не указаны';
                
                    const row = `
                        <tr class="clickable-row" data-analysis-id="${analysis.analysis_id}">
                            <td>${rowNumber}</td>
                            <td>${analysis.prompt_name || 'Не указано'}</td>
                            <td>${trimmedFilters}</td>
                            <td>${formatDate(analysis.timestamp)}</td>
                        </tr>`;
                    tableBody.append(row);
                });
    
                $('.clickable-row').off('click').on('click', function () {
                    const analysisId = $(this).attr('data-analysis-id');
                    if (analysisId) {
                        window.location.href = `/analysis/${analysisId}/view`;
                    } else {
                        console.error('Не удалось получить analysis_id из строки таблицы.');
                        alert('Ошибка: ID анализа не найден.');
                    }
                });

                // Обновляем информацию о пагинации
                updatePagination(response.total_count);
            },
            error: function () {
                $('#loadingIndicator').hide();
                alert('Ошибка при загрузке анализов.');
            }
        });
    }

    function updatePagination(totalCount) {
        totalPages = Math.ceil(totalCount / limit);
        $('#pageInfo').text(`Страница ${currentPage} из ${totalPages}`);
        $('#prevPage').prop('disabled', currentPage === 1);
        $('#nextPage').prop('disabled', currentPage === totalPages);
    }

    $('#prevPage').on('click', function () {
        if (currentPage > 1) {
            currentPage--;
            offset -= limit;
            loadAnalyses();
        }
    });

    $('#nextPage').on('click', function () {
        if (currentPage < totalPages) {
            currentPage++;
            offset += limit;
            loadAnalyses();
        }
    });
});
