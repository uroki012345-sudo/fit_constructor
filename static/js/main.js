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

        // Обновляем цифры
        document.getElementById('total-calories').textContent = data.total_calories;
        document.getElementById('total-burned').textContent = data.total_burned;
        document.getElementById('net-calories').textContent = data.net_calories;
        document.getElementById('total-protein').textContent = data.total_protein;
        document.getElementById('total-fat').textContent = data.total_fat;
        document.getElementById('total-carbs').textContent = data.total_carbs;

        // 1️⃣ ПРОГРЕСС-БАР КАЛОРИЙ
        const percent = (data.net_calories / data.daily_norm) * 100;
        const progressBar = document.getElementById('calorie-progress');
        const percentText = document.getElementById('calorie-percent');
        
        if (progressBar) {
            const width = Math.min(percent, 100);
            progressBar.style.width = width + '%';
            
            // Меняем цвет в зависимости от процента
            if (percent > 100) {
                progressBar.style.background = 'linear-gradient(90deg, #e74c3c, #c0392b)';
            } else if (percent > 85) {
                progressBar.style.background = 'linear-gradient(90deg, #f39c12, #e67e22)';
            } else {
                progressBar.style.background = 'linear-gradient(90deg, #2ecc71, #27ae60)';
            }
        }
        if (percentText) {
            percentText.textContent = Math.round(percent) + '%';
        }

        // Вердикт
        const verdictDiv = document.getElementById('verdict');
        if (data.is_ok) {
            verdictDiv.textContent = '✅ Отлично! Ты уложился в норму!';
            verdictDiv.className = 'verdict ok';
        } else {
            verdictDiv.textContent = `⚠️ Перебор на ${data.net_calories - data.daily_norm} ккал. Норма ${data.daily_norm} ккал в день.`;
            verdictDiv.className = 'verdict bad';
        }
        
        // 5️⃣ СОВЕТ ДНЯ (добавляем под вердиктом)
        showAdvice(data);
        
        // 3️⃣ СОХРАНЯЕМ В localStorage
        localStorage.setItem('selectedFoods', JSON.stringify(selectedFoods));
        localStorage.setItem('selectedExercises', JSON.stringify(selectedExercises));
        
    } catch (error) {
        console.error('Ошибка:', error);
        const verdictDiv = document.getElementById('verdict');
        if (verdictDiv) {
            verdictDiv.textContent = '⚠️ Ошибка соединения с сервером';
            verdictDiv.className = 'verdict bad';
        }
    }
}

// 5️⃣ ФУНКЦИЯ СОВЕТОВ ДНЯ
function showAdvice(data) {
    const adviceDiv = document.getElementById('daily-advice');
    if (!adviceDiv) return;
    
    let advice = '';
    
    if (data.total_protein < 100) {
        advice = '💪 Мало белка! Добавь курицу, творог или протеин.';
    } else if (data.total_fat > 80) {
        advice = '🥑 Много жиров! Уменьши количество масла и жирного мяса.';
    } else if (data.total_carbs > 250) {
        advice = '🍚 Много углеводов! Замени простые углеводы на сложные.';
    } else if (data.net_calories > data.daily_norm) {
        advice = '⚠️ Перебор калорий! Добавь кардио-тренировку или убери один приём пищи.';
    } else if (data.net_calories < data.daily_norm - 500) {
        advice = '📉 Слишком мало калорий! Не забывай полноценно питаться для энергии.';
    } else {
        advice = '🌟 Отличный баланс! Так держать! Ты на правильном пути.';
    }
    
    adviceDiv.innerHTML = '💡 <strong>Совет дня:</strong> ' + advice;
}

// Функция для привязки обработчиков к карточкам
function bindCardEvents() {
    const cards = document.querySelectorAll('.card');
    console.log('Найдено карточек:', cards.length);
    
    cards.forEach(card => {
        card.removeEventListener('click', card.clickHandler);
        
        const handler = () => {
            const type = card.dataset.type;
            const id = parseInt(card.dataset.id);

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

            updateResults();
        };
        
        card.clickHandler = handler;
        card.addEventListener('click', handler);
    });
}

// 4️⃣ ФУНКЦИЯ ФИЛЬТРАЦИИ ПРОДУКТОВ
function filterFoods(mealType) {
    const cards = document.querySelectorAll('.card[data-type="food"]');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    // Обновляем активную кнопку
    filterBtns.forEach(btn => {
        if (btn.dataset.filter === mealType) {
            btn.classList.add('active-filter');
        } else {
            btn.classList.remove('active-filter');
        }
    });
    
    cards.forEach(card => {
        if (mealType === 'all' || card.dataset.meal === mealType) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease';
        } else {
            card.style.display = 'none';
        }
    });
}

// 5️⃣ ФУНКЦИЯ "ИДЕАЛЬНЫЙ ДЕНЬ"
function setPerfectDay() {
    // Оптимальная комбинация для здорового дня
    const perfectFoods = [1, 2, 5, 8]; // Овсянка, Курица, Протеин, Лосось
    const perfectExercises = [101, 103, 106, 115]; // Приседания, Планка, Берпи, Прыжки
    
    // Очищаем текущий выбор
    selectedFoods = [];
    selectedExercises = [];
    document.querySelectorAll('.card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Выбираем новые
    perfectFoods.forEach(foodId => {
        selectedFoods.push(foodId);
        const card = document.querySelector(`.card[data-type="food"][data-id="${foodId}"]`);
        if (card) card.classList.add('selected');
    });
    
    perfectExercises.forEach(exId => {
        selectedExercises.push(exId);
        const card = document.querySelector(`.card[data-type="exercise"][data-id="${exId}"]`);
        if (card) card.classList.add('selected');
    });
    
    updateResults();
    
    // Анимация уведомления
    const notification = document.createElement('div');
    notification.textContent = '🎯 Идеальный день выбран! Твой план питания и тренировок готов!';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2ecc71;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        z-index: 9999;
        animation: slideIn 0.5s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Ждём полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('Скрипт загружен!');
    
    // 3️⃣ ЗАГРУЖАЕМ СОХРАНЁННЫЙ ВЫБОР ИЗ LOCALSTORAGE
    const savedFoods = localStorage.getItem('selectedFoods');
    const savedExercises = localStorage.getItem('selectedExercises');
    
    if (savedFoods) {
        selectedFoods = JSON.parse(savedFoods);
    }
    if (savedExercises) {
        selectedExercises = JSON.parse(savedExercises);
    }
    
    // Привязываем обработчики к карточкам
    bindCardEvents();
    
    // Восстанавливаем визуальное выделение карточек из localStorage
    document.querySelectorAll('.card').forEach(card => {
        const type = card.dataset.type;
        const id = parseInt(card.dataset.id);
        
        if (type === 'food' && selectedFoods.includes(id)) {
            card.classList.add('selected');
        }
        if (type === 'exercise' && selectedExercises.includes(id)) {
            card.classList.add('selected');
        }
    });
    
    // 4️⃣ ДОБАВЛЯЕМ КНОПКИ ФИЛЬТРАЦИИ
    const foodsSection = document.querySelector('.section:first-child');
    if (foodsSection && !document.querySelector('.filter-buttons')) {
        const filterHTML = `
            <div class="filter-buttons" style="margin: 15px 0;">
                <button class="filter-btn active-filter" data-filter="all" style="background: #ff6b35;">📋 Все</button>
                <button class="filter-btn" data-filter="breakfast" style="background: rgba(255,255,255,0.1);">🍳 Завтрак</button>
                <button class="filter-btn" data-filter="lunch" style="background: rgba(255,255,255,0.1);">🍝 Обед</button>
                <button class="filter-btn" data-filter="dinner" style="background: rgba(255,255,255,0.1);">🌙 Ужин</button>
                <button class="filter-btn" data-filter="snack" style="background: rgba(255,255,255,0.1);">🍎 Перекус</button>
            </div>
        `;
        
        const sectionTitle = foodsSection.querySelector('h2');
        sectionTitle.insertAdjacentHTML('afterend', filterHTML);
        
        // Добавляем обработчики на кнопки фильтра
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.dataset.filter;
                filterFoods(filter);
            });
        });
    }
    
    // 5️⃣ ДОБАВЛЯЕМ КНОПКУ "ИДЕАЛЬНЫЙ ДЕНЬ"
    const resultPanel = document.querySelector('.result-panel');
    if (resultPanel && !document.querySelector('.perfect-day-btn')) {
        const perfectBtn = document.createElement('button');
        perfectBtn.textContent = '⭐ Идеальный день';
        perfectBtn.className = 'perfect-day-btn';
        perfectBtn.style.cssText = `
            background: linear-gradient(135deg, #f39c12, #e67e22);
            margin-left: 10px;
        `;
        perfectBtn.addEventListener('click', setPerfectDay);
        
        const resetBtn = document.getElementById('reset-btn');
        if (resetBtn) {
            resetBtn.insertAdjacentElement('afterend', perfectBtn);
        }
    }
    
    // 1️⃣ ДОБАВЛЯЕМ ПРОГРЕСС-БАР В РЕЗУЛЬТАТЫ
    const statsDiv = document.querySelector('.stats');
    if (statsDiv && !document.getElementById('progress-container')) {
        const progressHTML = `
            <div id="progress-container" style="grid-column: span 3; margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>🎯 Прогресс дня</span>
                    <span id="calorie-percent">0%</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 25px; overflow: hidden;">
                    <div id="calorie-progress" style="width: 0%; height: 100%; transition: width 0.3s; border-radius: 10px;"></div>
                </div>
            </div>
        `;
        statsDiv.insertAdjacentHTML('beforeend', progressHTML);
    }
    
    // 5️⃣ ДОБАВЛЯЕМ БЛОК С СОВЕТАМИ
    const verdictDiv = document.getElementById('verdict');
    if (verdictDiv && !document.getElementById('daily-advice')) {
        const adviceHTML = `
            <div id="daily-advice" style="
                background: rgba(255,107,53,0.1);
                padding: 10px 15px;
                border-radius: 10px;
                margin-top: 15px;
                font-size: 14px;
                border-left: 3px solid #ff6b35;
            "></div>
        `;
        verdictDiv.insertAdjacentHTML('afterend', adviceHTML);
    }
    
    // Кнопка сброса
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            selectedFoods = [];
            selectedExercises = [];
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('selected');
            });
            localStorage.removeItem('selectedFoods');
            localStorage.removeItem('selectedExercises');
            updateResults();
        });
    }
    // Кнопка сохранения дня (НОВЫЙ КОД)
const saveDayBtn = document.getElementById('save-day-btn');
if (saveDayBtn) {
    saveDayBtn.addEventListener('click', saveCurrentDay);
}
    // Инициализация
    updateResults();
});

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    .filter-btn {
        padding: 8px 15px;
        margin: 0 5px;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
        color: white;
    }
    .filter-btn:hover {
        transform: translateY(-2px);
    }
    .active-filter {
        background: #ff6b35 !important;
        box-shadow: 0 2px 10px rgba(255,107,53,0.3);
    }
    .perfect-day-btn {
        transition: all 0.3s;
    }
    .perfect-day-btn:hover {
        transform: scale(1.05);
    }
`;
document.head.appendChild(style);
// Функция для сохранения текущего дня
async function saveCurrentDay() {
    // Проверка: выбрал ли пользователь хоть что-то?
    if (selectedFoods.length === 0 && selectedExercises.length === 0) {
        alert('❌ Выберите хотя бы одно блюдо или упражнение!');
        return;
    }
    
    try {
        // Отправляем запрос на сервер
        const response = await fetch('/save_combination', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                foods: selectedFoods,
                exercises: selectedExercises
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Показываем красивое уведомление
            showNotification('✅ ' + data.message, '#2ecc71');
        } else {
            alert('❌ Ошибка сохранения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка соединения с сервером');
    }
}
// Функция для показа уведомления
function showNotification(message, color) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${color};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        z-index: 9999;
        animation: slideIn 0.5s ease;
    `;
    document.body.appendChild(notification);
    
    // Через 3 секунды уведомление исчезает
    setTimeout(() => notification.remove(), 3000);
}