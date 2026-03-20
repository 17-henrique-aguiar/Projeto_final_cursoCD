from flask import Flask, render_template, redirect, request, url_for
from models import db, Usuario, Lancamento
from flask_login import LoginMaster, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://banco.db'

db.init_app(app)

login_manager = LoginMaster()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(usser_id))

with app.app_context():
    db.create_all()

# Rotas

# Rota (home)
@app.route('/')
def home():
    return render_template('home.html')

# Rota do dashboard
@app.route('/dashboard')
@login_required
def index():
    lancamentos = Lancamento.query.filter_by(usuario_id=current_user.id).all()

    # Transformando em DataFrame
    df = pd.DataFrame([{
        "tipo": l.tipo,
        "valor": l.valor
    } for l in lancamentos])

    total_entrada = df[df['tipo'] == 'entrada']['valor'].sum() if not df.empty else 0
    total_saida = df[df['tipo'] == 'saida']['valor'].sum() if not df.empty else 0
    saldo = total_entrada - total_saida

    return render_template(
        'index.html',
        entrada=total_entrada,
        saida=total_saida,
        saldo=saldo,
        lancamentos=lancamentos
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/cadstro', method=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        senha_hash = generate_password_hash(request.form['password'])

        novo_usuario = Usuario(
            username=request.form['username'],
            password=senha_hash
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect('/login')
    
    return render_template('cadstro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/lancamentos', method=['GET', 'POST'])
@login_required
def lancamentos():
    if request.method == 'POST':
        novo = Lancamento(
            tipo=request.form['tipo'],
            valor=float(request.form['valor']),
            data=request.form['data'],
            descricao=request.form['descricao'],
            usuario_id=current_user.id
        )

        db.session.add(novo)
        db.session.commit()

        return
    
    return render_template('/lancamentos.html')

if __name__ == '__main__':
    app.run(debug=True)
