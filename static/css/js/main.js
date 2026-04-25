// Хранилище выбранных ID
let selectedFoods = [];
let selectedExercises = [];

// Функция обновления итогов через сервер
async function updateResults() {
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                foods: selectedFoods,
                exercises: selectedExercises
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка сервера');
        }
        
        const data = await response.json();

        document.getElementById('total-calories').textContent = data.total_calories;
        document.getElementById('total-burned').textContent = data.total_burned;
        document.getElementById('net-calories').textContent = data.net_calories;
        document.getElementById('total-protein').textContent = data.total_protein;
        document.getElementById('total-fat').textContent = data.total_fat;
        document.getElementById('total-carbs').textContent = data.total_carbs;

        const verdictDiv = document.getElementById('verdict');
        if (data.is_ok) {
            verdictDiv.textContent = '✅ Отлично! Ты уложился в норму!';
            verdictDiv.className = 'verdict ok';
        } else {
            verdictDiv.textContent = `⚠️ Перебор на ${data.net_calories - data.daily_norm} ккал. Норма ${data.daily_norm} ккал в день.`;
            verdictDiv.className = 'verdict bad';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        const verdictDiv = document.getElementById('verdict');
        if (verdictDiv) {
            verdictDiv.textContent = '⚠️ Ошибка соединения с сервером';
            verdictDiv.className = 'verdict bad';
        }
    }
}

// Функция для привязки обработчиков к карточкам
function bindCardEvents() {
    const cards = document.querySelectorAll('.card');
    console.log('Найдено карточек:', cards.length); // Проверка
    
    cards.forEach(card => {
        // Удаляем старый обработчик, если есть
        card.removeEventListener('click', card.clickHandler);
        
        // Создаём новый обработчик
        const handler = () => {
            const type = card.dataset.type;
            const id = parseInt(card.dataset.id);

            console.log('Клик по:', type, id); // Проверка клика

            if (type === 'food') {
                const index = selectedFoods.indexOf(id);
                if (index === -1) {
                    selectedFoods.push(id);
                    card.classList.add('selected');
                } else {
                    selectedFoods.splice(index, 1);
                    card.classList.remove('selected');
                }
            } else if (type === 'exercise') {
                const index = selectedExercises.indexOf(id);
                if (index === -1) {
                    selectedExercises.push(id);
                    card.classList.add('selected');
                } else {
                    selectedExercises.splice(index, 1);
                    card.classList.remove('selected');
                }
            }

            console.log('Выбрано еды:', selectedFoods);
            console.log('Выбрано упражнений:', selectedExercises);
            updateResults();
        };
        
        // Сохраняем обработчик и добавляем
        card.clickHandler = handler;
        card.addEventListener('click', handler);
    });
}

// Ждём полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('Скрипт загружен!');
    
    // Привязываем обработчики к карточкам
    bindCardEvents();
    
    // Кнопка сброса
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            selectedFoods = [];
            selectedExercises = [];
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('selected');
            });
            updateResults();
        });
    } else {
        console.error('Кнопка сброса не найдена!');
    }
    
    // Инициализация (пустые результаты)
    updateResults();
});