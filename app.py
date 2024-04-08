from flask import Flask, render_template, request, url_for, session
from flask_migrate import Migrate
from werkzeug.utils import redirect

from database import db
from forms import PersonaForm
from models import Persona

app = Flask(__name__)
app.secret_key="develoteca"

USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'clientes_db'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'llave_secreta'

db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)


@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/sobre')
def sobre():
    return render_template('sitio/sobre.html')


@app.route('/servicios')
def servicios():
    return render_template('sitio/servicios.html')


@app.route('/admin')
def admin_index():
    if not 'login' in session:
        return redirect('/admin/login')
    return render_template('admin/indexad.html')


@app.route('/admin/login')
def login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def log():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    if _usuario == 'admin' and _password == '123':
        session['login']=True
        session['usuario']='Administrador'
        return redirect('/admin')
    return render_template('admin/login.html')


@app.route('/admin/clientes')
def clientes():
    if not 'login' in session:
        return redirect('/admin/login')
    personas = Persona.query.order_by('id')
    total_personas = Persona.query.count()
    app.logger.debug(f'Listado personas: {personas}')
    app.logger.debug(f'Total personas: {total_personas}')
    return render_template('admin/clientes.html', personas=personas, total_personas=total_personas)


@app.route('/admin/ver/<int:id>')
def ver_detalle(id):
    persona = Persona.query.get_or_404(id)
    app.logger.debug(f'Ver Persona{persona}')
    return render_template('admin/detalle.html', persona=persona)


@app.route('/admin/agregar', methods=['GET','POST'])
def agregar():
    persona = Persona()
    personaForm = PersonaForm(obj=persona)
    if request.method == 'POST':
        if personaForm.validate_on_submit():
            personaForm.populate_obj(persona)
            app.logger.debug(f'Persona a insertar: {persona}')
            db.session.add(persona)
            db.session.commit()
            return redirect(url_for('clientes'))
    return render_template('admin/agregar.html', forma=personaForm)


@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    persona = Persona.query.get_or_404(id)
    personaForma = PersonaForm(obj=persona)
    if request.method == 'POST':
        if personaForma.validate_on_submit():
            personaForma.populate_obj(persona)
            app.logger.debug(f'Persona a actualizar: {persona}')
            db.session.commit()
            return redirect(url_for('clientes'))
    return render_template('admin/editar.html', forma=personaForma)

@app.route('/admin/eliminar/<int:id>')
def eliminar(id):
    persona = Persona.query.get_or_404(id)
    app.logger.debug(f'Persona a eliminar: {persona}')
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for('clientes'))


@app.route('/admin/cerrar')
def cerrar():
    session.clear()
    return redirect('/admin/login')
