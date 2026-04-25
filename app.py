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
    
    # Сохранённые комбинации (храним как JSON строку)
    saved_combinations = db.Column(db.Text, default='[]')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ДАННЫЕ О ЕДЕ И УПРАЖНЕНИЯХ ====================

foods = [
    {"id": 1, "name": "Овсянка с ягодами", "calories": 300, "protein": 12, "fat": 8, "carbs": 45, "type": "breakfast"},
    {"id": 2, "name": "Куриная грудка с гречкой", "calories": 500, "protein": 40, "fat": 10, "carbs": 60, "type": "lunch"},
    {"id": 3, "name": "Творог с бананом", "calories": 350, "protein": 25, "fat": 8, "carbs": 40, "type": "snack"},
    {"id": 4, "name": "Салат с тунцом", "calories": 250, "protein": 20, "fat": 12, "carbs": 15, "type": "dinner"},
    {"id": 5, "name": "Протеиновый коктейль", "calories": 200, "protein": 30, "fat": 3, "carbs": 12, "type": "snack"},
    {"id": 6, "name": "Рис с овощами", "calories": 400, "protein": 8, "fat": 5, "carbs": 80, "type": "lunch"},
    {"id": 7, "name": "Греческий йогурт с мёдом", "calories": 180, "protein": 12, "fat": 5, "carbs": 22, "type": "snack"},
    {"id": 8, "name": "Запечённый лосось с брокколи", "calories": 550, "protein": 45, "fat": 28, "carbs": 18, "type": "dinner"},
    {"id": 9, "name": "Смузи из шпината и яблока", "calories": 150, "protein": 4, "fat": 2, "carbs": 32, "type": "breakfast"},
    {"id": 10, "name": "Макароны из твёрдых сортов с томатами", "calories": 480, "protein": 14, "fat": 9, "carbs": 85, "type": "lunch"},
    {"id": 11, "name": "Омлет с овощами", "calories": 320, "protein": 22, "fat": 18, "carbs": 12, "type": "breakfast"},
    {"id": 12, "name": "Говядина с киноа", "calories": 600, "protein": 48, "fat": 22, "carbs": 50, "type": "dinner"},
    {"id": 13, "name": "Творожная запеканка", "calories": 280, "protein": 20, "fat": 9, "carbs": 30, "type": "snack"},
    {"id": 14, "name": "Свекольный салат с чесноком", "calories": 120, "protein": 3, "fat": 5, "carbs": 16, "type": "dinner"},
]

exercises = [
    {"id": 101, "name": "Приседания", "calories_burn": 50, "muscles": "Ноги, ягодицы", "reps": "3x15", "type": "legs"},
    {"id": 102, "name": "Отжимания", "calories_burn": 40, "muscles": "Грудь, трицепс", "reps": "3x10", "type": "chest"},
    {"id": 103, "name": "Планка", "calories_burn": 30, "muscles": "Кор, пресс", "reps": "3x30 сек", "type": "core"},
    {"id": 104, "name": "Выпады", "calories_burn": 45, "muscles": "Ноги", "reps": "3x12", "type": "legs"},
    {"id": 105, "name": "Скручивания", "calories_burn": 35, "muscles": "Пресс", "reps": "3x20", "type": "core"},
    {"id": 106, "name": "Берпи", "calories_burn": 70, "muscles": "Всё тело", "reps": "3x10", "type": "fullbody"},
    {"id": 107, "name": "Выпрыгивания", "calories_burn": 55, "muscles": "Ноги, кардио", "reps": "3x12", "type": "legs"},
    {"id": 108, "name": "Отжимания узким хватом", "calories_burn": 45, "muscles": "Трицепс, грудь", "reps": "3x8", "type": "chest"},
    {"id": 109, "name": "Подъём ног лёжа", "calories_burn": 30, "muscles": "Нижний пресс", "reps": "3x15", "type": "core"},
    {"id": 110, "name": "Боковая планка", "calories_burn": 35, "muscles": "Косые мышцы живота", "reps": "3x20 сек на сторону", "type": "core"},
    {"id": 111, "name": "Зашагивания на стул", "calories_burn": 40, "muscles": "Ноги, ягодицы", "reps": "3x12", "type": "legs"},
    {"id": 112, "name": "Мостик ягодичный", "calories_burn": 35, "muscles": "Ягодицы, поясница", "reps": "3x15", "type": "legs"},
    {"id": 113, "name": "Супермен", "calories_burn": 30, "muscles": "Спина, ягодицы", "reps": "3x10", "type": "back"},
    {"id": 114, "name": "Альпинист", "calories_burn": 60, "muscles": "Кор, кардио", "reps": "3x20", "type": "fullbody"},
    {"id": 115, "name": "Прыжки на месте", "calories_burn": 50, "muscles": "Кардио, ноги", "reps": "3x30 сек", "type": "cardio"},
    {"id": 116, "name": "Боксирование с тенью", "calories_burn": 65, "muscles": "Плечи, кардио", "reps": "3x45 сек", "type": "cardio"},
    {"id": 117, "name": "Русский твист", "calories_burn": 40, "muscles": "Косые мышцы, пресс", "reps": "3x20", "type": "core"},
    {"id": 118, "name": "Приседания сумо", "calories_burn": 50, "muscles": "Внутренняя часть бедра", "reps": "3x12", "type": "legs"},
    {"id": 119, "name": "Обратные отжимания", "calories_burn": 45, "muscles": "Трицепс", "reps": "3x10", "type": "arms"},
    {"id": 120, "name": "Велосипед лёжа", "calories_burn": 40, "muscles": "Пресс, ноги", "reps": "3x20", "type": "core"},
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
        return redirect(url_for('constructor'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(url_for('constructor'))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('constructor'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверки
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
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
        return redirect(url_for('login'))
    
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
    return render_template('profile.html', user=current_user)

@app.route('/save_combination', methods=['POST'])
@login_required
def save_combination():
    data = request.get_json()
    foods_selected = data.get('foods', [])
    exercises_selected = data.get('exercises', [])
    
    # Получаем текущие сохранения
    saved = json.loads(current_user.saved_combinations) if current_user.saved_combinations else []
    
    # Добавляем новую комбинацию
    new_combination = {
        'id': len(saved) + 1,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),  
        'foods': foods_selected,
        'exercises': exercises_selected
    }
    saved.append(new_combination)
    
    # Сохраняем последние 10 комбинаций
    if len(saved) > 10:
        saved = saved[-10:]
    
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
    daily_norm = 2200
    
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

# Создание базы данных
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)