from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
from dotenv import load_dotenv   # 👈 НОВАЯ СТРОКА
import os                         # 👈 НОВАЯ СТРОКА
from datetime import datetime 
load_dotenv()  # 👈 НОВАЯ СТРОКА (загружает .env файл)

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')  # 👈 ИЗМЕНЁННАЯ СТРОКА
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в аккаунт'

# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    saved_combinations = db.Column(db.Text, default='[]')
    
    # 👇 НОВОЕ ПОЛЕ - дневная норма калорий
    daily_norm = db.Column(db.Integer, default=2200)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ДАННЫЕ О ЕДЕ И УПРАЖНЕНИЯХ ====================

foods = [
    # ЗАВТРАКИ (breakfast)
    {"id": 1, "name": "Овсянка с ягодами и мёдом", "calories": 320, "protein": 12, "fat": 8, "carbs": 52, "type": "breakfast"},
    {"id": 2, "name": "Омлет с овощами и сыром", "calories": 380, "protein": 24, "fat": 22, "carbs": 15, "type": "breakfast"},
    {"id": 3, "name": "Смузи из шпината, банана и протеина", "calories": 280, "protein": 25, "fat": 5, "carbs": 35, "type": "breakfast"},
    {"id": 4, "name": "Творожная запеканка с изюмом", "calories": 350, "protein": 28, "fat": 10, "carbs": 38, "type": "breakfast"},
    {"id": 5, "name": "Гречневая каша с молоком", "calories": 290, "protein": 10, "fat": 6, "carbs": 48, "type": "breakfast"},
    {"id": 6, "name": "Панкейки из овсяной муки", "calories": 420, "protein": 15, "fat": 18, "carbs": 52, "type": "breakfast"},
    {"id": 7, "name": "Яичница с авокадо и тостом", "calories": 450, "protein": 20, "fat": 28, "carbs": 30, "type": "breakfast"},
    {"id": 8, "name": "Чиа пудинг с кокосовым молоком", "calories": 310, "protein": 8, "fat": 18, "carbs": 32, "type": "breakfast"},
    
    # ОБЕДЫ (lunch)
    {"id": 9, "name": "Куриная грудка с гречкой и овощами", "calories": 520, "protein": 42, "fat": 12, "carbs": 58, "type": "lunch"},
    {"id": 10, "name": "Рис с тунцом и овощами", "calories": 480, "protein": 35, "fat": 14, "carbs": 52, "type": "lunch"},
    {"id": 11, "name": "Паста с курицей и песто", "calories": 620, "protein": 38, "fat": 24, "carbs": 68, "type": "lunch"},
    {"id": 12, "name": "Борщ с говядиной и сметаной", "calories": 380, "protein": 22, "fat": 16, "carbs": 38, "type": "lunch"},
    {"id": 13, "name": "Греческий салат с курицей", "calories": 410, "protein": 34, "fat": 22, "carbs": 18, "type": "lunch"},
    {"id": 14, "name": "Лосось с киноа и спаржей", "calories": 580, "protein": 48, "fat": 28, "carbs": 42, "type": "lunch"},
    {"id": 15, "name": "Индейка с бурым рисом", "calories": 490, "protein": 44, "fat": 12, "carbs": 52, "type": "lunch"},
    {"id": 16, "name": "Овощное рагу с нутом", "calories": 360, "protein": 16, "fat": 10, "carbs": 52, "type": "lunch"},
    {"id": 17, "name": "Бургер с говяжьей котлетой", "calories": 680, "protein": 42, "fat": 34, "carbs": 52, "type": "lunch"},
    {"id": 18, "name": "Том Ям с морепродуктами", "calories": 420, "protein": 32, "fat": 18, "carbs": 28, "type": "lunch"},
    
    # УЖИНЫ (dinner)
    {"id": 19, "name": "Запечённый лосось с брокколи", "calories": 550, "protein": 46, "fat": 30, "carbs": 18, "type": "dinner"},
    {"id": 20, "name": "Салат с тунцом и яйцом", "calories": 320, "protein": 28, "fat": 18, "carbs": 15, "type": "dinner"},
    {"id": 21, "name": "Говядина с цветной капустой", "calories": 480, "protein": 42, "fat": 22, "carbs": 22, "type": "dinner"},
    {"id": 22, "name": "Куриные котлеты с греческим салатом", "calories": 430, "protein": 38, "fat": 20, "carbs": 24, "type": "dinner"},
    {"id": 23, "name": "Творог с зеленью и огурцом", "calories": 260, "protein": 28, "fat": 12, "carbs": 14, "type": "dinner"},
    {"id": 24, "name": "Рыбные палочки с пюре", "calories": 520, "protein": 32, "fat": 24, "carbs": 48, "type": "dinner"},
    {"id": 25, "name": "Цыплёнок табака с овощами", "calories": 590, "protein": 52, "fat": 28, "carbs": 32, "type": "dinner"},
    {"id": 26, "name": "Сёмга на пару с рисом", "calories": 480, "protein": 42, "fat": 22, "carbs": 38, "type": "dinner"},
    
    # ПЕРЕКУСЫ (snack)
    {"id": 27, "name": "Протеиновый коктейль", "calories": 200, "protein": 32, "fat": 3, "carbs": 10, "type": "snack"},
    {"id": 28, "name": "Греческий йогурт с мёдом", "calories": 180, "protein": 14, "fat": 6, "carbs": 22, "type": "snack"},
    {"id": 29, "name": "Яблоко с арахисовой пастой", "calories": 220, "protein": 6, "fat": 14, "carbs": 24, "type": "snack"},
    {"id": 30, "name": "Творожный десерт с ягодами", "calories": 250, "protein": 22, "fat": 8, "carbs": 28, "type": "snack"},
    {"id": 31, "name": "Ореховый микс (30г)", "calories": 180, "protein": 6, "fat": 16, "carbs": 8, "type": "snack"},
    {"id": 32, "name": "Сырники со сметаной", "calories": 340, "protein": 18, "fat": 16, "carbs": 32, "type": "snack"},
    {"id": 33, "name": "Банан и горсть миндаля", "calories": 240, "protein": 6, "fat": 14, "carbs": 28, "type": "snack"},
    {"id": 34, "name": "Протеиновый батончик", "calories": 220, "protein": 18, "fat": 8, "carbs": 20, "type": "snack"},
    {"id": 35, "name": "Смузи из зелени и яблока", "calories": 150, "protein": 4, "fat": 2, "carbs": 32, "type": "snack"},
]

exercises = [
    # НОГИ И ЯГОДИЦЫ (legs)
    {"id": 101, "name": "Приседания с собственным весом", "calories_burn": 50, "muscles": "Ноги, ягодицы", "reps": "3x15", "type": "legs"},
    {"id": 102, "name": "Выпады с гантелями", "calories_burn": 60, "muscles": "Ноги, ягодицы", "reps": "3x12", "type": "legs"},
    {"id": 103, "name": "Приседания сумо", "calories_burn": 55, "muscles": "Внутренняя часть бедра", "reps": "3x15", "type": "legs"},
    {"id": 104, "name": "Мостик ягодичный на одной ноге", "calories_burn": 45, "muscles": "Ягодицы, поясница", "reps": "3x12", "type": "legs"},
    {"id": 105, "name": "Зашагивания на платформу", "calories_burn": 50, "muscles": "Ноги, ягодицы", "reps": "3x12", "type": "legs"},
    {"id": 106, "name": "Болгарские выпады", "calories_burn": 65, "muscles": "Ноги, баланс", "reps": "3x10", "type": "legs"},
    {"id": 107, "name": "Выпрыгивания из приседа", "calories_burn": 70, "muscles": "Ноги, кардио", "reps": "3x10", "type": "legs"},
    
    # ГРУДЬ И ТРИЦЕПС (chest/arms)
    {"id": 108, "name": "Отжимания от пола", "calories_burn": 45, "muscles": "Грудь, трицепс", "reps": "3x12", "type": "chest"},
    {"id": 109, "name": "Отжимания узким хватом", "calories_burn": 50, "muscles": "Трицепс, грудь", "reps": "3x10", "type": "chest"},
    {"id": 110, "name": "Жим гантелей лёжа", "calories_burn": 55, "muscles": "Грудь, плечи", "reps": "3x12", "type": "chest"},
    {"id": 111, "name": "Разведение гантелей лёжа", "calories_burn": 40, "muscles": "Грудные мышцы", "reps": "3x15", "type": "chest"},
    {"id": 112, "name": "Отжимания на брусьях", "calories_burn": 60, "muscles": "Трицепс, грудь", "reps": "3x8", "type": "chest"},
    {"id": 113, "name": "Французский жим гантели", "calories_burn": 40, "muscles": "Трицепс", "reps": "3x12", "type": "arms"},
    
    # ПРЕСС И КОР (core)
    {"id": 114, "name": "Планка классическая", "calories_burn": 35, "muscles": "Кор, пресс", "reps": "3x40 сек", "type": "core"},
    {"id": 115, "name": "Скручивания на пресс", "calories_burn": 40, "muscles": "Верхний пресс", "reps": "3x20", "type": "core"},
    {"id": 116, "name": "Подъём ног в висе", "calories_burn": 50, "muscles": "Нижний пресс", "reps": "3x12", "type": "core"},
    {"id": 117, "name": "Русский твист с весом", "calories_burn": 45, "muscles": "Косые мышцы", "reps": "3x20", "type": "core"},
    {"id": 118, "name": "Велосипед лёжа", "calories_burn": 45, "muscles": "Пресс, ноги", "reps": "3x20", "type": "core"},
    {"id": 119, "name": "Боковая планка", "calories_burn": 35, "muscles": "Косые мышцы", "reps": "3x30 сек", "type": "core"},
    {"id": 120, "name": "Альпинист", "calories_burn": 65, "muscles": "Кор, кардио", "reps": "3x20", "type": "core"},
    {"id": 121, "name": "Вакуум живота", "calories_burn": 20, "muscles": "Глубокие мышцы", "reps": "3x15 сек", "type": "core"},
    
    # СПИНА (back)
    {"id": 122, "name": "Супермен (гиперэкстензия)", "calories_burn": 35, "muscles": "Спина, ягодицы", "reps": "3x12", "type": "back"},
    {"id": 123, "name": "Тяга гантели к поясу", "calories_burn": 50, "muscles": "Широчайшие", "reps": "3x12", "type": "back"},
    {"id": 124, "name": "Подтягивания обратным хватом", "calories_burn": 70, "muscles": "Спина, бицепс", "reps": "3x6", "type": "back"},
    {"id": 125, "name": "Лодочка лёжа на животе", "calories_burn": 30, "muscles": "Поясница, ягодицы", "reps": "3x12", "type": "back"},
    
    # ПЛЕЧИ (shoulders)
    {"id": 126, "name": "Жим гантелей сидя", "calories_burn": 50, "muscles": "Дельты, плечи", "reps": "3x12", "type": "shoulders"},
    {"id": 127, "name": "Разведение гантелей в стороны", "calories_burn": 40, "muscles": "Средняя дельта", "reps": "3x15", "type": "shoulders"},
    {"id": 128, "name": "Тяга штанги к подбородку", "calories_burn": 45, "muscles": "Трапеция, дельты", "reps": "3x12", "type": "shoulders"},
    
    # КАРДИО И ПОЛНОТЕЛОВЫЕ (cardio/fullbody)
    {"id": 129, "name": "Берпи", "calories_burn": 80, "muscles": "Всё тело", "reps": "3x10", "type": "fullbody"},
    {"id": 130, "name": "Прыжки на скакалке", "calories_burn": 100, "muscles": "Кардио, ноги", "reps": "5 мин", "type": "cardio"},
    {"id": 131, "name": "Бег на месте с высоким подниманием колен", "calories_burn": 70, "muscles": "Кардио, ноги", "reps": "3x30 сек", "type": "cardio"},
    {"id": 132, "name": "Боксирование с тенью", "calories_burn": 75, "muscles": "Плечи, кардио", "reps": "3x45 сек", "type": "cardio"},
    {"id": 133, "name": "Джампинг Джекс", "calories_burn": 60, "muscles": "Кардио, всё тело", "reps": "3x30 сек", "type": "cardio"},
    {"id": 134, "name": "Скалолаз (попеременные подтягивания колен)", "calories_burn": 70, "muscles": "Кор, кардио", "reps": "3x20", "type": "fullbody"},
    {"id": 135, "name": "Толчки санок", "calories_burn": 90, "muscles": "Ноги, кардио", "reps": "4x20м", "type": "fullbody"},
]

# ==================== МАРШРУТЫ ====================

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/constructor')
@login_required
def constructor():
    return render_template('index.html', foods=foods, exercises=exercises)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))  # 👈 МЕНЯЕМ: было 'constructor', стало 'profile'
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(url_for('profile'))  # 👈 МЕНЯЕМ: было 'constructor', стало 'profile'
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверки
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:  # 👈 ДОБАВИЛИ проверку длины
            flash('Пароль должен быть минимум 6 символов', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'danger')
            return render_template('register.html')
        
        # Создание пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите в аккаунт.', 'success')
        return redirect(url_for('login'))  # 👈 НЕ ИЗМЕНЯЕТСЯ: после регистрации на страницу входа
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('landing'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, foods=foods, exercises=exercises)

@app.route('/save_combination', methods=['POST'])
@login_required
def save_combination():
    from datetime import datetime
    
    data = request.get_json()
    foods_selected = data.get('foods', [])
    exercises_selected = data.get('exercises', [])
    
    # Получаем текущие сохранения
    saved = json.loads(current_user.saved_combinations) if current_user.saved_combinations else []
    
    # Рассчитываем данные для сохранения
    total_calories = 0
    total_burned = 0
    
    for food in foods:
        if food['id'] in foods_selected:
            total_calories += food['calories']
    
    for ex in exercises:
        if ex['id'] in exercises_selected:
            total_burned += ex['calories_burn']
    
    net_calories = total_calories - total_burned
    
    # Добавляем новую комбинацию с полной информацией
    new_combination = {
        'id': len(saved) + 1,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'foods': foods_selected,
        'exercises': exercises_selected,
        'foods_count': len(foods_selected),
        'exercises_count': len(exercises_selected),
        'net_calories': net_calories,
        'daily_norm': current_user.daily_norm,
        'total_calories': total_calories,
        'total_burned': total_burned
    }
    saved.append(new_combination)
    
    # Сохраняем последние 20 комбинаций
    if len(saved) > 20:
        saved = saved[-20:]
    
    current_user.saved_combinations = json.dumps(saved)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Комбинация сохранена!'})

@app.route('/get_saved_combinations', methods=['GET'])
@login_required
def get_saved_combinations():
    saved = json.loads(current_user.saved_combinations) if current_user.saved_combinations else []
    return jsonify({'combinations': saved})
@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.get_json()
    
    selected_food_ids = data.get('foods', [])
    selected_exercise_ids = data.get('exercises', [])
    
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    
    for food in foods:
        if food['id'] in selected_food_ids:
            total_calories += food['calories']
            total_protein += food['protein']
            total_fat += food['fat']
            total_carbs += food['carbs']
    
    total_burned = 0
    for ex in exercises:
        if ex['id'] in selected_exercise_ids:
            total_burned += ex['calories_burn']
    
    net_calories = total_calories - total_burned
    
    # 👇 ИСПРАВЛЕНО: используем норму из профиля пользователя
    daily_norm = current_user.daily_norm
    
    return jsonify({
        'total_calories': total_calories,
        'total_burned': total_burned,
        'net_calories': net_calories,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs,
        'daily_norm': daily_norm,
        'is_ok': net_calories <= daily_norm
    })
# Добавьте новый маршрут после других маршрутов

@app.route('/update_norm', methods=['POST'])
@login_required
def update_norm():
    data = request.get_json()
    new_norm = data.get('daily_norm')
    
    if new_norm and 500 <= new_norm <= 5000:  # Валидация
        current_user.daily_norm = new_norm
        db.session.commit()
        return jsonify({'success': True, 'daily_norm': new_norm})
    
    return jsonify({'success': False, 'error': 'Некорректное значение'}), 400

# Создание базы данных
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)