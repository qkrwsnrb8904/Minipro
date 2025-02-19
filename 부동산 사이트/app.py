from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 비밀번호 변경 기능
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dK7x9M3Qp2Lz5Fw8Ej1Hy6Vn4Bt0Cg'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:toor@localhost/FLASK_BASIC'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

KAKAO_API_KEY = "your_kakao_api_key_here"

@app.route('/')
def index():
    return render_template('index.html', KAKAO_API_KEY=KAKAO_API_KEY)

@login_required
def home():
    return "<h1>Welcome!</h1><a href='/logout'>Logout</a>"  # 간단한 홈 페이지

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입이 완료되었습니다.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('로그인 성공!')
            return redirect(url_for('home'))  # 'home' 라우트가 정의되어 있어야 합니다.
        flash('로그인 실패. 사용자 이름 또는 비밀번호를 확인하세요.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.')
    return redirect(url_for('home'))  # 'home' 라우트가 정의되어 있어야 합니다.

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    new_password = PasswordField('새 비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField('새 비밀번호 확인', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('비밀번호 변경')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('비밀번호가 변경되었습니다.')
            return redirect(url_for('profile'))
        else:
            flash('현재 비밀번호가 일치하지 않습니다.')
    return render_template('change_password.html', form=form)

@app.route('/search')
def search():
    address = request.args.get('address')
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={address}"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    response = requests.get(url, headers=headers)
    result = response.json()

    if result['documents']:
        address_info = result['documents'][0]
        x, y = float(address_info['x']), float(address_info['y'])
        polygon_coords = get_polygon_coords(x, y)
        return jsonify({"status": "OK", "coordinates": polygon_coords})
    else:
        return jsonify({"status": "ZERO_RESULTS"})

def get_polygon_coords(x, y):
    # 이 함수는 실제로 폴리곤 좌표를 생성해야 합니다.
    # 예시로 간단한 사각형을 만들어 반환합니다.
    offset = 0.01
    return [
        [x - offset, y - offset],
        [x + offset, y - offset],
        [x + offset, y + offset],
        [x - offset, y + offset]
    ]


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
