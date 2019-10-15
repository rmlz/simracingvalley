# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 23:06:15 2019

@author: Ramon Barros
@github: https://github.com/rmlz

I'm a Python student that have been trying to create useful scripts for the Simracing Community. 
Also I may thanks all the people that helped me to develop the Simracing Valley Community:

Alisson Zanoni
Aparicio Felix Neto
Aurea Barros
Carlos Eduardo Pinto
Celso Pedri
Cesar Louro
Fabio Krek
Fernando Bueno
Glenio Lobo
Gracas Barros
Gustavo Pinto
Hernani Klehm
Iovan Lima
Maikon Sulivan
Matheus Manarim
Nicolas Sanchez Ernest
Pedro Phelipe Porto
Rodrigo Lepri
Rodrigo Vicente
Tadeu Costa
Tayane Campos
"""


import os
import re
import base64
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from flask import Flask,render_template,jsonify,json,request,flash,redirect,url_for,session,g
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from fabric.api import *
from flask_openid import OpenID
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, PasswordField, StringField, TextField, BooleanField, HiddenField, IntegerField
from wtforms.validators import InputRequired, Email, Length, Optional, NumberRange
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from mailchimp3 import MailChimp
#import dns
from urllib.parse import unquote_plus, urlencode
from urllib.request import urlopen, Request
from operator import itemgetter
from datetime import datetime, timedelta
import time
import pytz #python timezone
from flask_cache import Cache
#decorator function
from functools import wraps
#debugger
#from flask_debugtoolbar import DebugToolbarExtension

import logging
import logging.handlers
from wsgiref.simple_server import make_server


# Create logger
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

# Handler 
#LOG_FILE = '/opt/python/log/sample-app.log'
#handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
#handler.setLevel(logging.INFO)

# Formatter
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
#handler.setFormatter(formatter)

# add Handler to Logger
#logger.addHandler(handler)


'''def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'], environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        response = ''
    else:
        response = welcome
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]'''
    

application = Flask(__name__)
oid = OpenID(application)
#application.debug = False

#
#=================================================================================================
#       EDIT THIS DATA                ############################################################
#=================================================================================================
#
#mailchimpclient = MailChimp(mc_api='efc9999999999999999999999-us17', mc_user='Simracing Valley Ramon Barros') #uncooment this
#mailchimplistid = '4de999999999' #uncomment this
_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test")
#=================================================================================================
#=================================================================================================
#

db = client.ValleyAlliance
dbusers = client.users
#dbusers = client.usertest
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################

#=================================================================================================
#       EDIT THIS DATA                ############################################################
#=================================================================================================
application.config.update(dict(
    STEAM_API_KEY = 'CD3999999999999999999999999999999999',
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key",
    ########################################
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME ='simracingvalley@examplemail.com',
    MAIL_PASSWORD = 'PASSWORD_HERE',
    MAIL_DEFAULT_SENDER = 'simracingvalley@examplemail.com'
))

#=================================================================================================
#=================================================================================================
#
#toolbar = DebugToolbarExtension(application)
csrf = CsrfProtect(application)
mail = Mail(application)

#Cache
cache = Cache(application,config={'CACHE_TYPE': 'simple'})     
cache.init_app(application)   
now = (time.localtime().tm_hour, time.localtime().tm_min)

#USER CLASS FOR LOGIN IN SIMRACINGVALLEY    
class User(UserMixin):

    def __init__(self, username, _id):
        self.username = username
        self._id = _id

    def get_id(self):
        return self._id
    
    def get_username(self):
        return self.username
    def user_obj(self):
        return dbusers.users.find_one({'_id': self._id})
    
    

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
    

#FIND IF CURRENT USER IS ADMIN
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cur_user = dbusers.users.find_one({'_id': current_user.get_id()})
        if (cur_user == None):
            flash('Você não está logado, por favor faça seu Login!')
            return redirect(url_for('login'))
        elif (cur_user['admin'] == None) or (cur_user['admin'] is not True):
            flash('Você não tem permissão para acessar essa página')
            return redirect(url_for('driver', userid=current_user.get_id()))
        return f(*args, **kwargs)
    return decorated_function

def bookrace_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cur_user = dbusers.users.find_one({'_id': current_user.get_id()})
        if (cur_user == None):
            flash('Você não está logado, por favor faça seu Login!')
            return redirect(url_for('login'))
        elif (cur_user['bookrace'] == None) or (cur_user['bookrace'] is not True):
            flash('Você não tem permissão para marcar corridas')
            return redirect(url_for('driver', userid=current_user.get_id()))
        return f(*args, **kwargs)
    return decorated_function


#LOGIN MANAGER TO RETURN USER OR NONE    

@login_manager.user_loader
def load_user(user_id):
    u = dbusers.users.find_one({'_id' : user_id})
    if not u:
        return None
    return User(u['username'], u['_id'])


##########################################################################
#MANY FORMS OF THE WEBSITE
class RegisterForm(FlaskForm):
    name = StringField('Nome', validators=[InputRequired(message="Campo de Nome não preenchido"), Length(min=3, max=15, message="Esse não parece ser um nome válido!" )])
    lastname = StringField('Sobrenome', validators=[InputRequired(message="Campo de Sobrenome não preenchido"), Length(min=3, message="Esse não parece ser um sobrenome válido!" )])
    email = StringField('Email', validators=[InputRequired(message="Campo de Email não preenchido"), Email(message='Email Inválido'), Length(min=6, max=50, message='Email Inválido')])
    username = StringField('Usuário', validators=[InputRequired(message="Campo de Usuário não preenchido"), Length(min=4, max=15, message="Usuário deve conter entre 4 e 15 caracteres" )])
    password = PasswordField("Password", validators=[InputRequired(message="Campo de Password não preenchido"), Length(min=8, max=80, message="Senha deve conter pelo menos 8 caracteres" )])
    steam_id = HiddenField('SteamID', validators=[InputRequired()])
    accept = BooleanField('Aceito')
    
class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[InputRequired(message="Campo de Usuário não preenchido"), Length(min=4, max=15, message="Usuário deve conter entre 4 e 15 caracteres")])
    password = PasswordField("Password", validators=[InputRequired(message="Campo de Senha não preenchido"), Length(min=8, max=80, message="Senha deve conter pelo menos 8 caracteres")])
    remember = BooleanField('Lembre-se de mim')
    
class ForgetPass(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message="Campo Email deve ser preenchido"), Email(message='Email Inválido'), Length(min=6, max=50, message='Email Inválido')])
    
class PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(message="Campo Senha deve ser preenchido"), Length(min=8, max=80, message="Senha deve conter pelo menos 8 caracteres")])

class EditProfile(FlaskForm):
    estados = [
    (None, ''),
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
    ('NB', "Not in Brazil"),
    ('ND', 'Não Declarado')]
    phrase = StringField('Frase do Perfil', validators=[Length(max=100, message="Frase do Perfil deve conter o máximo de 100 caracteres"), Optional()])
    about = StringField('Sobre Você', validators=[Length(max=200, message="Campo 'Sobre Você' deve conter o máximo de 200 caracteres"), Optional()])
    name = StringField('Nome', validators=[Length(max=20, message="Nome deve conter o máximo de 20 caracteres"), Optional()])
    lastname = StringField('Sobrenome', validators=[Length(max=20 , message="Sobrenome deve conter o máximo de 20 caracteres"), Optional()])
    gender = SelectField('Sexo', choices=[(None, ''), ('M','Masculino'), ('F', 'Feminino'), ('ND', 'Não declarado')],validators=[Optional()])
    birthday = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[Optional()])
    state = SelectField('Estado', choices=estados, validators=[Optional()])
    city = StringField('Cidade', validators=[Length(max=20, message="Cidade deve conter o máximo de 20 caracteres"), Optional()])
    
class UploadPhoto(FlaskForm):
    photo = StringField('Copie a URL da foto')
    
    
class scheduleRace(FlaskForm):
    options = db.ServerOptions.find_one()
    tracks = [(option[0], option[0]) for option in options['tracks']]
    cars = [(option[0], option[0]) for option in options['cars']]
    
    carviews = [(option[0], option[0]) for option in options['carviews']]
    fixsetups = [(option[0], option[0]) for option in options['fixsetups']]
    fixupgrades =[(option[0], option[0]) for option in options['fixupgrades']]
    flags = [(option[0], option[0]) for option in options['flags']]
    fueltires = [(option[0], option[0]) for option in options['fueltires']]
    tiresets = [(option[0], option[0]) for option in options['tiresets']]
    mechfailures = [(option[0], option[0]) for option in options['mechfailures']]
    trackconds = [(option[0], option[0]) for option in options['trackconds']]
    timescales = [(option[0], option[0]) for option in options['timescales']]
    trackprogresses = [(option[0], option[0]) for option in options['trackprogresses']]
    starttypes = [(option[0], option[0]) for option in options['starttypes']]
    pitreturns = [(option[0], option[0]) for option in options['pitreturns']]
    warmup = [(option[0], option[0]) for option in options['warmups']]
    racefinishes =  [(option[0], option[0]) for option in options['racefinishes']]
    damages = [(option[0], option[0]) for option in options['damages']]
    privatequalifys = [(option[0], option[0]) for option in options['privatequalies']]
    
    track = SelectField('Pista', choices=tracks)
    car = SelectField('Carro', choices=cars)
    date = DateField('Data', format='%Y-%m-%d')
    time = TimeField('Começo do Practice (Abertura do Server)')
    carview = SelectField('Visão do carro', choices=carviews)
    fixsetup = SelectField('Setup Fixo', choices=fixsetups)
    fueltire = SelectField('Consumo Pneu/Gasolina', choices=fueltires)
    pitreturn = SelectField('Retorno aos pits', choices=pitreturns)
    
    #HELPS
    traction = SelectField('Controle de Tração', choices=[('3','Alto'), 
                                                          ('2', 'Médio'), 
                                                          ('1', 'Baixo'), 
                                                          ('0','Nenhum')
                                                          ])
        
    antilock = SelectField('ABS', choices=[('1', 'Baixo'),
                                           ('2', 'Médio'), 
                                           ('0','Nenhum')
                                           ])
        
    stability = SelectField('Controle de Estabilidade', choices=[('0','Nenhum'),
                                                                 ('1', 'Baixo'),
                                                                 ('2', 'Médio')
                                                                 ])
        
    gear = SelectField('Auto Marchas', choices=[('0','Não'),
                                                ('3', 'Sim')
                                                ])
        
    clutch = SelectField('Auto Embreagem', choices=[('1','Sim'),
                                                    ('0', 'Não')
                                                    ])
        
    invulnerability = SelectField('Invulnerabilidade', choices=[('0','Não'),
                                                                ('1', 'Sim')
                                                                ])
        
    opposite = SelectField('Contra Esterço', choices=[('0','Não'),
                                                      ('1', 'Sim')
                                                      ])
        
    steering = SelectField('Ajuda de Direção', choices=[('0','Nenhum'),
                                                        ('1', 'Baixo'),
                                                        ('2', 'Médio'),
                                                        ('3', 'Alto')
                                                        ])
        
    breakhelp = SelectField('Ajuda Frenagem', choices=[('0','Nenhum'),
                                                       ('1', 'Baixo'),
                                                       ('2', 'Médio')
                                                       ])
        
    spinhelp = SelectField('Ajuda rodada', choices=[('0','Não'),
                                                    ('1', 'Sim')
                                                    ])
        
    autopit = SelectField('Auto Pitstop', choices=[('0','Não'),
                                                   ('1', 'Sim')
                                                   ])
        
    autolift = SelectField('Levantar carro', choices=[('0','Não'),
                                                      ('1', 'Sim')
                                                      ])
        
    autoblip = SelectField('Auto blip', choices=[('1','Sim'),
                                                ('0', 'Não')
                                                ])
        
    driveline = SelectField('Linha de direção', choices=[('0','Não'),
                                                         ('1', 'Sim')
                                                         ])
    
    mechfailure = SelectField('Falhas Mecânicas', choices=mechfailures)
    maxplayers = IntegerField('Máximo de pilotos', default='20', validators=[NumberRange(min=4, max=25, message='Número máximo de pilotos deve ser entre 4 e 25')])
    ip = StringField('IP', default="100.66.74.252")
    password = SelectField('Senha', choices=[('1', 'Sim'), ('2', 'Não')] )
    rules = SelectField('Regras', choices=flags)
    tireset = SelectField('Jogos de Pneus', choices=tiresets)
    
    #Session values
    practice = IntegerField('Tempo de Practice', default='120',validators=[NumberRange(min=10, max=120, message='Tempo de practice deve ser entre 10 e 120')])
    qualify = IntegerField('Tempo de Qualify', default='10',validators=[NumberRange(min=5, max=120, message='Tempo de qualy deve ser entre 5 e 120')])
    qualylaps = IntegerField('Voltas de qualify', default='255',validators=[NumberRange(min=2, max=255, message='Voltas de qualy devem ser entre 2 e 255')])
    warmuptime = IntegerField('Tempo de Warmup', default='5',validators=[NumberRange(min=4, max=25, message='Tempo de warmup deve ser entre 5 e 120')])
    racetime = IntegerField('Tempo de Corrida', default='20',validators=[NumberRange(min=10, max=120, message='Tempo de corrida deve ser entre 10 e 120')])
    racelaps = IntegerField('Voltas de Corrida', default='10',validators=[NumberRange(min=10, max=70, message='Número de voltas deve ser entre 10 e 70')])
    starthour = IntegerField('Hora virtual', default='12',validators=[NumberRange(min=0, max=23, message='Hora virtual deve ser entre 0 e 23')])
    startminute = IntegerField('Minutos Virtual', default='00',validators=[NumberRange(min=0, max=59, message='Minuto virtual deve ser entre 0 e 59')])
    starttype = SelectField('Largada', choices=starttypes)
    fixupgrade = SelectField('Upgrade Fixo', choices=fixupgrades)
    turnwarmup = SelectField('Sessão de Warmup', choices=warmup)
    privatequaly = SelectField('Qualificação privada', choices=privatequalifys)
    timescale = SelectField('Progressão Temporal', choices=timescales)
    
    trackcond = SelectField('Emborrachamento Asfalto', choices=trackconds)
    trackprogress = SelectField('Progressão do Emborrachamento', choices=trackprogresses)
    damage = SelectField('Danos', choices=damages)
    racefinish = SelectField('Critério de Fim', choices=racefinishes)
    
    downstream = StringField('Downstream', default="10240" )
    upstream = StringField('Upstream', default="10240" )
    
    official = BooleanField('Corrida Oficial')
    cdc = BooleanField('Corrida dos Campeões')
    public = BooleanField('Publicar Server na Agenda?')
    registerrace = SubmitField('Marcar Corrida')
    
class deleteRace(FlaskForm):
    delete = SelectField('Deletar corrida marcada?', choices=[('Sim', 'Sim')])
    submitdelete = SubmitField('DELETAR') 
    
    
class recordsForm(FlaskForm):
     track = SelectField('Pista', choices=[])
     car = SelectField('Carro', choices=[])                       

class AltConfirmForm(FlaskForm):
    username = StringField('Usuário', validators=[InputRequired(message="Campo de Usuário não preenchido"), Length(min=4, max=15, message="Usuário deve conter entre 4 e 15 caracteres")])
    email = StringField('Email', validators=[InputRequired(message="Campo de Email não preenchido"), Email(message='Email Inválido'), Length(min=6, max=50, message='Email Inválido')])

    
#######################################################################################################################################
 

#FORM ERROR FLASHING
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

#############################
#ENCRYPT HELPERS
def encrypt_str(string):
    byteslike = str.encode(string)
    encode = base64.b64encode(byteslike)
    return encode
    
def decrypt_str(code):
    data = base64.b64decode(code).decode('utf-8')
    return data    

#STEAM BRIDGE TO GET INFO FROM SOME STEAMID
def get_steam_userinfo(steam_id):
    options = {
        'key': application.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001/?%s' % urlencode(options)
    rv = json.load(urlopen(url))
    return rv['response']['players']['player'][0] or {}

##############
#EMAIL HELPER#
##############
def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    
def send_confirmation_email(user_email, name, lastname):
    confirm_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
 
    confirm_url = url_for(
        'confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
 
    html = render_template(
        'email_confirmation.html',
        confirm_url=confirm_url,
        name=name,
        lastname=lastname)
 
    send_email('Confirmação de Email', [user_email], None, html)
def send_password_reset_email(user_email, user_username):
    password_reset_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
    user = dbusers.users.find_one({'email': user_email})
    lastpassdate = datetime.fromtimestamp(int(user['lastpassdate'])).strftime('%d-%m-%Y %H:%M:%S')
    #print(user_email)
    username = user_username
    password_reset_url = url_for(
            'reset_with_token',
            token = password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
            _external=True)
 
    html = render_template(
        'email_password_reset.html',
        password_reset_url=password_reset_url, lastpassdate=lastpassdate, username=username)
    
    print(html)
 
    send_email('Pedido de Redefinição de Senha', [user_email], None, html)
    
def send_enter_race_email(user_email):
    user = dbusers.users.find_one({'email': user_email})
    race = db.ScheduledRace.find_one({'_id': '0'})
    participants = race['participants']
    html = render_template('email_enter_race.html', user=user, race=race, participants=participants)
    send_email('Você se inscreveu para uma corrida!', [user_email], None, html)

############################################################################################################################################
#URLLIB UPLOADS HELPERS
class HeadRequest(Request):
    def get_method(self):
        return 'HEAD'

#ROUTING STARTS NOW
@application.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@application.route('/', methods=['GET', 'POST'])
def login():
    logged_user = dbusers.users.find_one({'_id': current_user.get_id()})
    formreset = ForgetPass()
    form = LoginForm()
    if form.validate_on_submit():
        user = dbusers.users.find_one({'username': form.username.data})
        if user:
            password = form.password.data + form.username.data
            if User.validate_login(user['password'], password):
                if (user['email_confirmed'] == False):
                    logout_user()
                    flash('Email não confimado! Favor checar sua caixa de entrada!')
                    send_confirmation_email(user['email'], user['name'], user['lastname'])
                    return redirect(url_for('login'))
                user_obj = User(user['username'], user['_id'])
                #print(user_obj.is_authenticated(), user_obj.get_id())
                login_user(user_obj, remember=form.remember.data)
                return redirect(url_for('driver', userid=user['_id']))
            else:           
                flash('Usuário e/ou senha incorretos')
        else:
            flash('Usuário e/ou senha incorretos')
    
    return render_template('login.html', form=form, formreset=formreset, logged_user=logged_user)

@application.route('/registration', methods=['GET', 'POST'])
#@login_required
def registration():
    form = RegisterForm()
    request_tok = request.args.get('tok')
    steam_id_code = request_tok.encode()
    flash_errors(form)
    tz = pytz.timezone('Brazil/East')
    #print(steam_id_code)
    try:
        steam_id = base64.urlsafe_b64decode(steam_id_code).decode()
        #print(steam_id)
        userinfo = get_steam_userinfo(steam_id)
    except:
        steam_id = steam_id_code.decode()
        userinfo =  get_steam_userinfo(steam_id)
    
    if userinfo == {}:
        flash('UM ERRO FOI ENCONTRADO! INICIE O PROCESSO DE REGISTRO NOVAMENTE')
        return redirect(url_for('login'))
    else:
        form.steam_id.data = steam_id   
        if request.method == 'GET':
            try:
                form.username.data = userinfo['personaname']
            except:
                pass
        if form.validate_on_submit():
            steam_id_data = form.steam_id.data
            #print(form.steam_id.data, form.email.data, form.username.data, form.password.data)
                
            if (dbusers.users.count({'email': form.email.data}) > 0) and (dbusers.users.count({'username': form.username.data}) > 0):
                flash('Email ({}) já está cadastrado'.format(form.email.data), 'error')
                flash('Usuário ({}) já está cadastrado'.format(form.username.data), 'error')
            elif (dbusers.users.count({'username': form.username.data}) > 0):
                flash('Usuário ({}) já está cadastrado'.format(form.username.data), 'error')
            elif (dbusers.users.count({'email': form.email.data}) > 0):
                flash('Email ({}) já está cadastrado'.format(form.email.data), 'error')
            elif form.accept.data == False:
                flash('Você deve marcar a caixa que garante a sua ciência de nosso Manual!')
            else:
                
                password = form.password.data + form.username.data
                hashpass = generate_password_hash(password, salt_length=20 ,method='pbkdf2:md5')
                registration_date = time.mktime(datetime.now(tz).timetuple())
                #print(password, ':'*150)
                rv = dbusers.users.find_one({'steam_id': steam_id_data})
                dbusers.users.update_one({'steam_id': steam_id_data}, {'$set': {
                        'name': form.name.data,
                        'lastname': form.lastname.data,
                        'username': form.username.data,
                        'email': form.email.data,
                        'password': hashpass,
                        'lastpassdate': registration_date,
                        'email_confirmed': False,
                        'email_confirmation_sent_on': registration_date,
                        'email_confirmed_on': None                 
                        }})
            
                send_confirmation_email(form.email.data, form.name.data, form.lastname.data)
                flash('CADASTRO CONCLUÍDO COM SUCESSO')
                flash('UM E-MAIL FOI ENVIADO PARA VALIDAÇÃO DA CONTA')
                try:
                    mailchimpclient.lists.members.create(mailchimplistid, {
                        'email_address': form.email.data,
                        'status': 'subscribed',
                        'merge_fields': {
                            'FNAME': form.name.data,
                            'LNAME': form.lastname.data,
                        },
                    })
                except Exception as e:
                    print(e)
                form = RegisterForm()
                return redirect(url_for('logout'))
        
    return render_template('register.html', form=form, tok=request_tok)

@application.route('/register')
@oid.loginhandler
def register():
    return oid.try_login('http://steamcommunity.com/openid/')

@oid.after_login
def aftersteamconfirmed(resp):
    match = _steam_id_re.search(resp.identity_url)
    steam_id = match.group(1)
    steam_id_code = base64.urlsafe_b64encode(steam_id.encode())
    user = get_steam_userinfo(steam_id)
    if (dbusers.users.count({'steam_id': steam_id, 'username': 'username'}) > 0):
        flash('UM ERRO FOI ENCONTRADO! INICIE O PROCESSO DE REGISTRO NOVAMENTE')
        dbusers.users.delete_many({'steam_id': steam_id, 'username': 'username'})
        return redirect(url_for('login'))
    elif (dbusers.users.count({'steam_id': steam_id}) > 0):
        flash('CONTA DA STEAM JÁ VINCULADA A UMA CONTA SIMRACING VALLEY')
        flash('PROCEDA AO LOGIN UTILIZANDO O FORMULÁRIO ABAIXO')
        return redirect(url_for('login'))
    else:
        u = 0
        d = 0
        c = 0
        m = 0
        dm = 0
        _id = str(dm) + str(m) + str(c) + str(d) + str(u)
        while (dbusers.users.count({'_id' : _id}) > 0):
            u += 1
            if u == 10:
                d += 1
                u = 0
                if d == 10:
                    c += 1
                    d = 0
                    if c == 10:
                        m += 1
                        c = 0
                        if m == 10:
                            dm += 1
                            m = 0
            _id = str(dm) + str(m) + str(c) + str(d) + str(u)
        hashpass = generate_password_hash('password', salt_length=20 ,method='pbkdf2:md5')
        insert = dbusers.users.insert_one({'_id' : _id,
                                            'steam_id': steam_id,
                                           'username': 'username',
                                           'password' : hashpass,
                                           'avatar': user['avatarfull'],
                                           'admin': False,
                                           'sponsor': False,
                                           'bookrace': False
                                           })
        return redirect(url_for('registration', tok=steam_id_code))
        ''' if User.validate_login(hashpass, 'password'):
            user = dbusers.users.find_one({'steam_id': steam_id})
            user_obj = User(user['_id'])
            login_user(user_obj)
            print(user_obj.is_authenticated(), user_obj.get_id())
            print('-'*150, current_user)
            return redirect(url_for('registration', steam_id=steam_id))'''
        


 
@application.route('/altconfirm/', methods=["GET", "POST"])
def altconfirm_email():
    form = AltConfirmForm()
    flash('Coloque aqui o nome de usuário e e-mail cadastrados no Vale!')
    if form.validate_on_submit():
        validate_user = dbusers.users.find_one({'username': form.username.data,
                                'email': form.email.data})
        if validate_user:
            confirm_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
            user_email = form.email.data
 
            return redirect(url_for('confirm_email', token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'), _external=True))
        else:
            flash('#############')
            flash('Combinação de usuário e email estão incorretos.')
            flash('------------')
            flash('Considere a utilização de letras maiúsculas no email ou nome de usuário!')
    return render_template('altconfirmemail.html', form=form)
        
        
    
@application.route('/confirm/<token>')
def confirm_email(token):
    tz = pytz.timezone('Brazil/East')
    try:
        confirm_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=86400)
    except:
        flash('O link de confirmação é inválido ou está expirado.', 'error')
        return redirect(url_for('login'))
 
    user = (dbusers.users.find_one({'email': email}))
 
    if user['email_confirmed']:
        flash('Esse e-mail já foi confirmado. Faça o Login', 'info')
    else:
        update = dbusers.users.update_one({'email': email}, {'$set': {
                'email_confirmed': True,
                'email_confirmed_on' : time.mktime(datetime.now(tz).timetuple())}
            })
        flash('Seu email foi confirmado com sucesso! Faça seu Login!.')
 
    return redirect(url_for('login'))    
        

@application.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    form = PasswordForm()
    tz = pytz.timezone('Brazil/East')
    try:
        password_reset_serializer = URLSafeTimedSerializer(application.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('O link de redefinição de senha é inválido ou está expirado.', 'error')
        return redirect(url_for('login'))
 
    
 
    if form.validate_on_submit():
        try:
            user = dbusers.users.find_one({'email': email})
            #print(user)
        except:
            flash('Endereço de Email Inválido!', 'error')
            return redirect(url_for('login'))
 
        #print(form.password.data)
        update = dbusers.users.update_one({'email': email}, {'$set': {
                'password': generate_password_hash((form.password.data + user['username']), salt_length=20 ,method='pbkdf2:md5'),
                'lastpassdate' : time.mktime(datetime.now(tz).timetuple())}})
        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('login'))
 
    return render_template('reset_password_with_token.html', form=form, token=token)

@application.route('/reset', methods=["POST"])
def reset():
    logged_user = dbusers.users.find_one({'_id': current_user.get_id()})
    formreset = ForgetPass()
    form = LoginForm()
    if formreset.validate_on_submit():
        try:
            user = dbusers.users.find_one({'email': formreset.email.data})
        except:
            flash('Endereço de email inválido', 'error')
            return render_template('login.html', form=form, formreset=formreset, logged_user=logged_user)
        
        if user is None:
            flash('Email não cadastrado.')
        elif user['email_confirmed']:
            print('SENDING EMAIL TO', user['email'])
            send_password_reset_email(user['email'], user['username'])
            flash('Um email com o link de redefinição foi enviado! Caso não tenha recebido o email, entre em contato. simracingvalley@examplemail.com', 'success')
        else:
            flash('Esse e-mail ainda não foi confirmado. Olhe a caixa de SPAM do seu email!', 'error')
        return render_template('login.html', form=form, formreset=formreset, logged_user=logged_user)
 
    return render_template('login.html', form=form, formreset=formreset, logged_user=logged_user)




#################################################################
#################################################################
#################################################################
#################################################################
#################################################################
@application.route('/ranking')
@application.route('/ranking/<kind>')
@csrf.exempt
def showDriverList(kind='global'):
    print(kind)
    return render_template('index-construction.html', kind=kind)


@application.route("/getDriverList",methods=['POST'])
@cross_origin()
@csrf.exempt
def getDriverList():       
    try:
        drivers = db.Drivers.find().sort([('points', -1)])

        driverList = []
        for driver in drivers:
            #print(driver['steamID'])
            user = dbusers.users.find_one({'steam_id': driver['steamID'] })
            #print(user)
            
            if user:
                if driver['races_done'] < 5:
                    if 'rank_pos' in driver:
                        driverItem = {
                            'Name':user['username'],
                            'Races':driver['races_done'],
                            'Points': 0,
                            'First':driver['top10']['1'],
                            'Second':driver['top10']['2'],
                            'Third':driver['top10']['3'],
                            'Fourth':driver['top10']['4'],
                            'Fifth':driver['top10']['5'],
                            'id':user['_id'],
                            'Class': driver['classimg'],
                            'Position': driver['rank_pos'],
                            'Votes': driver['votes'],
                            'Races_15': driver['races_15'],
                            }
                    else:
                        
                        driverItem = {
                                'Name':user['username'],
                                'Races':driver['races_done'],
                                'Points': 0,
                                'First':driver['top10']['1'],
                                'Second':driver['top10']['2'],
                                'Third':driver['top10']['3'],
                                'Fourth':driver['top10']['4'],
                                'Fifth':driver['top10']['5'],
                                'id':user['_id'],
                                'Class': driver['classimg'],
                                'Position': 999,
                                'Votes': driver['votes'],
                                'Races_15': driver['races_15'],
                                
                                
                                }
                else:
                    #print(driver)
                    driverItem = {
                            'Name':user['username'],
                            'Races':driver['races_done'],
                            'Points':round(driver['points'] * 1000),
                            'First':driver['top10']['1'],
                            'Second':driver['top10']['2'],
                            'Third':driver['top10']['3'],
                            'Fourth':driver['top10']['4'],
                            'Fifth':driver['top10']['5'],
                            'id':user['_id'],
                            'Class': driver['classimg'],
                            'Position': driver['rank_pos'],
                            'Votes': driver['votes'],
                            'Races_15': driver['races_15'],
                            }
            
                if driver['races_done'] == 0:
                    driverItem['Incidents'] = 0
                
                elif 'incident_ave' in driver:
                    driverItem['Incidents'] = round((driver['incident_ave']), 2)
                else:
                    driverItem['Incidents'] = round((driver['incidents'] / driver['races_done']), 2)
            
                driverList.append(driverItem)
            else:
                continue
        #sortdriverList = sorted(driverList, key=itemgetter('Points'), reverse=True)
        #print(driverList)
               
    except Exception as e:
        return str(e)
    return json.dumps(driverList)

@application.route("/getDriverList2",methods=['POST'])
@cross_origin()
@csrf.exempt
def getDriverList2():       
    try:
        drivers = db.SeasonDrivers.find().sort([('points', -1)])

        driverList = []
        for driver in drivers:
            #print(driver['steamID'])
            user = dbusers.users.find_one({'steam_id': driver['steamID'] })
            #print(user)
            
            if user:
                if driver['races_done'] < 5:
                    driverItem = {
                            'Name':user['username'],
                            'Races':driver['races_done'],
                            'Points': 0,
                            'First':driver['top10']['1'],
                            'Second':driver['top10']['2'],
                            'Third':driver['top10']['3'],
                            'Fourth':driver['top10']['4'],
                            'Fifth':driver['top10']['5'],
                            'id':user['_id'],
                            'Class': driver['classimg'],
                            'Position': driver['rank_pos'],
                            'Votes': driver['votes'],
                            'Races_15': driver['races_15'],
                            
                            
                            }
                else:
                    #print(driver)
                    driverItem = {
                            'Name':user['username'],
                            'Races':driver['races_done'],
                            'Points':round(driver['points'] * 1000),
                            'First':driver['top10']['1'],
                            'Second':driver['top10']['2'],
                            'Third':driver['top10']['3'],
                            'Fourth':driver['top10']['4'],
                            'Fifth':driver['top10']['5'],
                            'id':user['_id'],
                            'Class': driver['classimg'],
                            'Position': driver['rank_pos'],
                            'Votes': driver['votes'],
                            'Races_15': driver['races_15'],
                            }
            
            if driver['races_done'] == 0:
                driverItem['Incidents'] = 0
            
            elif 'incident_ave' in driver:
                driverItem['Incidents'] = round((driver['incident_ave']), 2)
            else:
                driverItem['Incidents'] = round((driver['incidents'] / driver['races_done']), 2)
            driverList.append(driverItem)
        #sortdriverList = sorted(driverList, key=itemgetter('Points'), reverse=True)
        #print(driverList)
               
    except Exception as e:
        return str(e)
    return json.dumps(driverList)

@application.route('/updateprofile', methods=['POST'])
@login_required
def updateProfile():
    userid = request.args.get('userid')
    if current_user.get_id() != userid:
        return redirect(url_for('driver', userid=userid))
    else:
        form = EditProfile()
        print('-'*50)
        print(form.validate_on_submit() == True)
        if form.validate_on_submit():
            print(form.errors)
            try:
                dbusers.users.update_one({'_id': userid}, {'$set': {
                'phrase' : form.phrase.data,
                'about': form.about.data,
                'name': form.name.data,
                'lastname': form.lastname.data,
                'gender': form.gender.data,
                'birthday': str(form.birthday.data.strftime('%d-%m-%Y')), 
                'state': form.state.data,
                'city': form.city.data
                }})
                print(form.phrase.data, form.about.data, form.name.data,
                      form.lastname.data, form.gender.data, str(form.birthday.data.strftime('%Y-%m-%d')),
                      form.state.data, form.city.data)
            except Exception as e:
                return str(e)
        else:
            print(form.errors)
    return redirect(url_for('driver', userid=userid))

@application.route('/upload', methods=['POST', 'GET'])
@login_required
def photoupload():
    userid = request.args.get('userid')
    if current_user.get_id() != userid:
        return redirect(url_for('driver', userid=userid))
    else:
        form = UploadPhoto()
        if form.validate_on_submit():
            try:
                url = form.photo.data
                response = urlopen(HeadRequest(url))
                maintype = response.headers['Content-Type'].split(';')[0].lower()
                if maintype not in ('image/png', 'image/jpeg', 'image/gif'):
                    flash('A URL deve ser uma imagem ou não é válida!')
                else:
                    dbusers.users.update_one({'_id':userid}, {'$set': {
                            'avatar': url}})
            except:
                flash('URL inacessível ou inválida!')
        else:
            print(form.errors)
    return redirect(url_for('driver', userid=userid))

def gen_password():
    #random password
    from string import ascii_letters as letters
    import random
    letters = letters[0:26]
    pw = ''
    for i in range(5):
        pw += random.choice(letters)
    
    return pw
@application.route('/schedulerace', methods=['POST', 'GET'])
@bookrace_required
def schedulerace():
    options = db.ServerOptions.find_one()
    form = scheduleRace()
    userid = current_user.get_id()
    user = dbusers.users.find_one({'_id': userid})
    form2 = deleteRace()
    scheduled_race_before = False
    tz = pytz.timezone('Brazil/East')
    race_db = db.ScheduledRace.find()
    
    for item in race_db:
        if item['user']['id'] == user['_id']:
            scheduled_race_before = True
    if form2.validate_on_submit() and form2.submitdelete.data:
        try:
            race = db.ScheduledRace.find_one({'user.id': user['_id']})
            if race['Online'] == True:
                db.ScheduledRace.update_one({'_id': race['_id']}, {'$set': {'Close': True}})
                flash('Servidor foi fechado com Sucesso!')
            else:
                db.ScheduledRace.delete_one({'user.id': user['_id']})
                flash('Corrida excluída com Sucesso!')

            
        except:
            flash('A corrida não foi excluída. Algo de errado aconteceu!')
        
    
    if form.validate_on_submit() and form.registerrace.data:
        try:
            #Check if time is valid
            if tz.localize(datetime.combine(form.date.data, form.time.data)) < datetime.now(tz) and user['admin'] == False:
                flash('O horário/dia escolhidos são inválidos. A data deve ser posterior ao horário atual que é: ' +
                      datetime.now(tz).strftime('%d-%m-%Y %H:%M'))
            else:
                #TIME IS VALID
                
               
                #CREATES A RANDOM PASSWORD OR BLANK PASSWORD 
                if form.password.data == '1':
                    form.password.data = gen_password()
                else:
                    form.password.data = ''
                
                answers = { 
                'tracks': form.track.data,
                'cars': form.car.data,
                'date': form.date.data.strftime('%d-%m-%Y'),
                'time':  form.time.data.strftime('%H:%M'),
                'carviews': form.carview.data,                 
                'damages': form.damage.data,
                'fixsetups': form.fixsetup.data,
                'fueltires': form.fueltire.data,
                'pitreturns': form.pitreturn.data,
                'help': [form.traction.data,
                         form.antilock.data,
                         form.stability.data,
                         form.gear.data,
                         form.clutch.data,
                         form.invulnerability.data,
                         form.opposite.data,
                         form.steering.data,
                         form.breakhelp.data,
                         form.spinhelp.data,
                         form.autopit.data,
                         form.autolift.data,
                         form.autoblip.data,
                         form.driveline.data
                         ],
                'mechfailures': form.mechfailure.data,
                'maxplayers': str(form.maxplayers.data),
                'ip': form.ip.data,
                'password': form.password.data,
                'flags': form.rules.data,
                'tiresets': form.tireset.data,
                'session': [str(form.practice.data), 
                            str(form.qualify.data),
                            str(form.qualylaps.data),
                            str(form.warmuptime.data),
                            str(form.racetime.data),
                            str(form.racelaps.data)],
                'starttime': [form.starthour.data,
                              form.startminute.data],
                'starttypes': form.starttype.data,
                'trackconds': form.trackcond.data,
                'trackprogresses': form.trackprogress.data,
                'Started': False,
                'racefinishes': form.racefinish.data,
                'downstream': form.downstream.data,
                'upstream': form.upstream.data, 
                'fixupgrades': form.fixupgrade.data,
                'warmups': form.turnwarmup.data,
                'privatequalies': form.privatequaly.data,
                'timescales': form.timescale.data,
                'Done': False,
                'participants': [],
                'user': {
                        'id': user['_id'],
                        'username': user['username']},
                'official': form.official.data,
                'cdc': form.cdc.data,
                'public': form.public.data,
                'Online': False,
                'Close': False
                
                }
                
            if answers['cdc'] == True: #Makes sure CDC races are always OFFICIAL races
                answers['official'] = True
            
            if answers['official']: #Makes sure OFFICIAL races are always PUBLIC races
                answers['public'] = True
            
            answers['timestamp_start'] = time.mktime(datetime.strptime(
                    answers['date']+' '+answers['time'], "%d-%m-%Y %H:%M").timetuple())
            answers['timestamp_end'] = answers['timestamp_start'] + ((form.practice.data + form.qualify.data + form.racetime.data + 15 )*60)
            if answers['warmups'] == 'Sim':
                answers['timestamp_end'] += (form.warmuptime.data) * 60
            
            for k,v in answers.items(): #Transforma as definições de answers em dados de configuração
                for key, value in options.items():
                    if key != '_id':
                        for i in range(len(value)):
                            if k == key:
                                if value[i][0] == v:
                                    answers[k] = value[i]
                
                            
            scheduled_race_before = False
            if user['admin'] == False:
                for item in db.ScheduledRace.find():
                    if item['user']['id'] == answers['user']['id']:
                        scheduled_race_before = True
            
            #We have to find if the car can only be used on special tracks (e.g: Karts and FTruck)
            
            
            if answers['cars'][3] in answers['tracks'][3]: #Checks if the selected car can be used in the track
                spc_track = True
            else:
                spc_track = False
            
            racefinish_ok = True
            if form.racefinish.data == 'Voltas' or form.racefinish.data == 'Tempo e voltas' and user['admin'] == False:
                #ONLY ADMINS CAN CREATE RACES USING LAPS AS FINITH TYPE, REGULAR PLAYERS SHALL USE ONLY TIME RACES
                racefinish_ok = False
            
            start_time_ok = True
            finish_time_ok = True
            race_db = db.ScheduledRace.find()
            
            for item in race_db:
                if start_time_ok:
                    if answers['timestamp_start'] <= item['timestamp_start']: #Corrida começa mais cedo que a outra?
                        if answers['timestamp_end'] >= item['timestamp_start']: #Corrida termina depois do começo da outra?
                            if answers['official'] and item['official'] == False:
                                db.ScheduledRace.delete_one({'_id': item['_id']})
                                flash('A corrida não oficial: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'] + ' foi desmarcada')
                            else:
                                start_time_ok = False
                                flash('Choque de horário com: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'])
                            
                    elif answers['timestamp_start'] <= item['timestamp_end']:
                        if answers['official'] and item['official'] == False:
                            db.ScheduledRace.delete_one({'_id': item['_id']})
                            flash('A corrida não oficial: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'] + ' foi desmarcada')
                        else:
                            start_time_ok = False
                            flash('Choque de horário com: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'])
                    elif answers['timestamp_start'] > item['timestamp_end']:
                        start_time_ok == True
                        
                        
            
            for item in race_db:
                if start_time_ok == True:
                    if answers['timestamp_start'] <= item['timestamp_end']:
                        if answers['official'] and item['official'] == False:
                            db.ScheduledRace.delete_one({'_id': item['_id']})
                            flash('A corrida não oficial: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'] + ' foi desmarcada')
                            
                        else:  
                            start_time_ok = False
                        flash('Choque de horário com: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'])
                    else:
                        if finish_time_ok == True:
                            if answers['timestamp_end'] >= item['timestamp_start']:
                                finish_time_ok = False
                                flash('Choque de horário com: ' + item['tracks'][0] + ' // ' + item['cars'][0] + ' ' + item['date'] + ' ' + item['time'])
            
                    
                
            
                    
            if scheduled_race_before == False: 
                if spc_track == True:
                    if racefinish_ok == True:
                        if start_time_ok == True:
                            if finish_time_ok == True:
                                db.ScheduledRace.insert_one(answers)
                                flash('Corrida Marcada com Sucesso')
                                pw = form.password.data
                                if pw == '':
                                    pw = 'SEM SENHA'
                                flash('A SENHA DA CORRIDA É: ' + pw )
                            else:
                                flash('O horário de término do servidor está chocando com outro Servidor já agendado. Diminua o tempo das sessões')                                
                        else:
                            flash('O horário de início marcado está chocando com outro Servidor já agendado')
                    else:
                        flash('Você não tem autorização para criar servidores com o critério de fim de corrida diferente de "TEMPO"')
                else:
                    flash('Carro e pista selecionados não podem ser utilizados em conjunto!')
            else:
                flash('Você já marcou uma corrida e só poderá marcar outra caso delete a anterior!')
        
                 
        except Exception as e:
            print(str(e))
    elif form.registerrace.data:
        flash('Não foi possível agendar essa corrida!')
        flash_errors(form)
    return render_template('schedulerace.html', form=form, scheduled_race_before=scheduled_race_before, form2=form2, user=user, userid=userid)
        

@application.route('/closerace/<raceid>')
@login_required
@csrf.exempt
def closerace(raceid):
    user = current_user.user_obj()
    race = db.ScheduledRace.find_one({'_id':ObjectId(raceid)})
    
    if race:
        if user['_id'] ==  race['user']['id'] or user['admin'] == True: 
        
            if race['Close'] == False:
                if race['Online']:
                    update = db.ScheduledRace.update_one({'_id':ObjectId(raceid)}, {'$set': {'Close': True}})
                    flash('A corrida ' + race['tracks'][0] + ' // ' + race['cars'][0])
                    flash('Data e Horário: ' + race['date'] + ' ' + race['time'])  
                    flash('id: (' + raceid + ') está sendo fechada agora mesmo.')
                else:
                    delete = db.ScheduledRace.delete_one({'_id':ObjectId(raceid)})
                    flash('A corrida ' + race['tracks'][0] + ' // ' + race['cars'][0])
                    flash('Data e Horário: ' + race['date'] + ' ' + race['time'])  
                    flash('id: (' + raceid + ') acaba de ser excluída da agenda!')
            else:
                flash('O pedido de fechamento dessa corrida está sendo processado')
        else:
            flash('Você não tem autorização para excluir a corrida ' + race['tracks'][0] + ' // ' + race['cars'][0])
            flash('Data e Horário: ' + race['date'] + ' ' + race['time'])  
            flash('id: (' + raceid + ')')
    else:
        flash('A corrida id: (' + raceid + ') não consta no banco de dados')
    
    return redirect(url_for('agenda'))


@application.route('/enterrace/<raceid>', methods=['POST', 'GET'])
@login_required
@csrf.exempt
def enterrace(raceid):
    tz = pytz.timezone('Brazil/East')
    race = db.ScheduledRace.find_one({'_id':ObjectId(raceid)})
    time_difference = tz.localize(datetime.strptime(race['date'] + ' ' + race['time'], '%d-%m-%Y %H:%M')) - datetime.now(tz)
    print(str(time_difference))
    user = current_user.user_obj()
    userid = user['_id']
    driver = db.Drivers.find_one({'steamID': user['steam_id']})
    seasondriver = db.SeasonDrivers.find_one({'steamID': user['steam_id']})
    maxplayers = int(race['maxplayers'])
    

    
    
    if time_difference < timedelta(0, 1800): #30 minutes to open server?
        if user['sponsor'] == False: #Se não for sponsor
            if time_difference > timedelta(0,0): #só na hora da corrida
                flash('Você só está autorizado a se registrar para a corrida após a abertura do Servidor')
            else:
                if current_user.get_id() != userid:
                    flash('Aconteceu algo de errado durante o registro na Corrida')
                    flash('Refaça o seu Login')
                    logout_user()
                    return redirect(url_for('login'))
                else:
                    if race['cdc']:
                        if not seasondriver:
                            flash('Você ainda não participou de uma corrida nessa temporada')
                            return redirect(url_for('agenda'))
                        else:
                            if seasondriver:
                                if seasondriver['rank_pos'] < 33:
                                    rank_pos = seasondriver['rank_pos']
                                    races_15 = seasondriver['races_15']
                            elif driver:
                                if driver['rank_pos'] < 33:
                                    rank_pos = driver['rank_pos']
                                    races_15 = driver['races_15']
                        if races_15 >= 5:
                            if rank_pos < 33:
                                if round(driver['incident_ave'], 1) <= 2:
                                    try:
                                        userobj = {'username': user['username'],
                                                   'userid': user['_id'],
                                                   'steamid': user['steam_id'],
                                                   'rankpos': driver['rank_pos'],
                                                   'classimg': driver['classimg'],
                                                   'points': round(driver['points'], 3) * 1000,
                                                   'incidents': round(driver['incident_ave'], 1),
                                                   'sponsor': user['sponsor']}
                                        
                                        password = race['password']
                                        if password == "":
                                            print('password sem senha')
                                            password = 'sem senha'
                                        if userobj in race['participants']:
                                            flash('Você já está inscrito para a corrida de ' + race['cars'][0] + ' em ' + race['tracks'][0])
                                            flash('A senha é: ' + password)
                                            print('Já inscrito')
                                        else:
                                            print('não inscrito ainda')
                                            if len(race['participants'])+1 >= maxplayers:
                                                if user['sponsor'] == False:
                                                    flash('O evento já alcançou o máximo de participantes. Mais sorte da próxima vez')
                                                    print('server lotado')
                                                else:
                                                    db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                                                    print('server lotado mas você é sponsor')
                                                    flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                                    flash('AVISO: Há mais pessoas cadastradas para a corrida do que o Server comporta..')
                                            else:
                                                print('Inscrição sucesso')
                                                flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                                db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                                    except Exception as e:
                                        return str(e)
                                else:
                                    flash('Seus pontos de incidentes ('+ str(round(driver['incident_ave'],1)) + ') ultrapassam o limite de 2.0')
                                    flash('Você não poderá participar da CDC.')
                        else:
                            flash('Para participar da CDC você deve contabilizar ao menos 5 participações nessa quinzena')
                            flash('Número de Participações = '+ str(races_15))
                    else:
                        try:
                            try:
                                userobj = {'username': user['username'],
                                           'userid': user['_id'],
                                           'steamid': user['steam_id'],
                                           'rankpos': driver['rank_pos'],
                                           'classimg': driver['classimg'],
                                           'points': round(driver['points'], 3) * 1000,
                                           'incidents': round(driver['incident_ave'], 1),
                                           'sponsor': user['sponsor']}
                            except:
                                userobj = {'username': user['username'],
                                           'userid': user['_id'],
                                           'steamid': user['steam_id'],
                                           'rankpos': 'TBD',
                                           'classimg': 'nao_ranqueado.png',
                                           'points': 0,
                                           'incidents': 0,
                                           'sponsor': user['sponsor']}
                            
                            password = race['password']
                            if password == "":
                                print('password sem senha')
                                password = 'sem senha'
                            if userobj in race['participants']:
                                flash('Você já está inscrito para a corrida de ' + race['cars'][0] + ' em ' + race['tracks'][0])
                                flash('A senha é: ' + password)
                                print('Já inscrito')
                            else:
                                print('não inscrito ainda')
                                if len(race['participants'])+1 >= maxplayers:
                                    if user['sponsor'] == False:
                                        flash('O evento já alcançou o máximo de participantes. Mais sorte da próxima vez')
                                        print('server lotado')
                                    else:
                                        db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                                        print('server lotado mas você é sponsor')
                                        flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                        flash('AVISO: Há mais pessoas cadastradas para a corrida do que o Server comporta..')
                                else:
                                    print('Inscrição sucesso')
                                    flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                    db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                        except Exception as e:
                            return str(e)
        else:
            if current_user.get_id() != userid:
                flash('Aconteceu algo de errado durante o registro na Corrida')
                flash('Refaça o seu Login')
                logout_user()
                return redirect(url_for('login'))
                
            if race['cdc']:
                if seasondriver['rank_pos'] < 33:
                    rank_pos = seasondriver['rank_pos']
                    races_15 = seasondriver['races_15']
                elif driver['rank_pos'] < 33:
                    rank_pos = driver['rank_pos']
                    races_15 = driver['races_15']
                if rank_pos < 33:
                    if races_15 >= 5:
                        if round(driver['incident_ave'], 1) <= 2:
                            try:
                                try:
                                    userobj = {'username': user['username'],
                                                   'userid': user['_id'],
                                                   'steamid': user['steam_id'],
                                                   'rankpos': driver['rank_pos'],
                                                   'classimg': driver['classimg'],
                                                   'points': round(driver['points'], 3) * 1000,
                                                   'incidents': round(driver['incident_ave'], 1),
                                                   'sponsor': user['sponsor']}
                                except:
                                    userobj = {'username': user['username'],
                                                   'userid': user['_id'],
                                                   'steamid': user['steam_id'],
                                                   'rankpos': 'TBD',
                                                   'classimg': 'nao_ranqueado.png',
                                                   'points': 0,
                                                   'incidents': 0,
                                                   'sponsor': user['sponsor']}
                                
                                password = race['password']
                                if password == "":
                                    print('password sem senha')
                                    password = 'sem senha'
                                if userobj in race['participants']:
                                    flash('Você já está inscrito para a corrida de ' + race['cars'][0] + ' em ' + race['tracks'][0])
                                    flash('A senha é: ' + password)
                                    print('Já inscrito')
                                else:
                                    print('não inscrito ainda')
                                    if len(race['participants'])+1 >= maxplayers:
                                        if user['sponsor'] == False:
                                            flash('O evento já alcançou o máximo de participantes. Mais sorte da próxima vez')
                                            print('server lotado')
                                        else:
                                            db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                                            print('server lotado mas você é sponsor')
                                            flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                            flash('AVISO: Há mais pessoas cadastradas para a corrida do que o Server comporta..')
                                    else:
                                        print('Inscrição sucesso')
                                        flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                        db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                            except Exception as e:
                                return str(e)
                        else:
                            flash('Seus pontos de incidentes ('+ str(round(driver['incident_ave'],1)) + ') ultrapassam o limite de 2.0')
                            flash('Você não poderá participar da CDC.')
                    else:
                        flash('Para participar da CDC você deve contabilizar ao menos 5 participações nessa quinzena')
                        flash('Número de Participações = '+ str(races_15))

                
            else:
                try:
                    try:
                        userobj = {'username': user['username'],
                                           'userid': user['_id'],
                                           'steamid': user['steam_id'],
                                           'rankpos': driver['rank_pos'],
                                           'classimg': driver['classimg'],
                                           'points': round(driver['points'], 3) * 1000,
                                           'incidents': round(driver['incident_ave'], 1),
                                           'sponsor': user['sponsor']}
                    except:
                        userobj = {'username': user['username'],
                                           'userid': user['_id'],
                                           'steamid': user['steam_id'],
                                           'rankpos': 'TBD',
                                           'classimg': 'nao_ranqueado.png',
                                           'points': 0,
                                           'incidents': 0,
                                           'sponsor': user['sponsor']}
                    
                    password = race['password']
                    if password == "":
                        print('password sem senha')
                        password = 'sem senha'
                    if userobj in race['participants']:
                        flash('Você já está inscrito para a corrida de ' + race['cars'][0] + ' em ' + race['tracks'][0])
                        flash('A senha é: ' + password)
                        print('Já inscrito')
                    else:
                        print('não inscrito ainda')
                        if len(race['participants'])+1 >= maxplayers:
                            if user['sponsor'] == False:
                                flash('O evento já alcançou o máximo de participantes. Mais sorte da próxima vez')
                                print('server lotado')
                            else:
                                db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                                print('server lotado mas você é sponsor')
                                flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                                flash('AVISO: Há mais pessoas cadastradas para a corrida do que o Server comporta..')
                        else:
                            print('Inscrição sucesso')
                            flash('Inscrição feita com sucesso! A senha do Servidor é: ' + password )
                            db.ScheduledRace.update_one({'_id': ObjectId(raceid)}, {'$push': {'participants':userobj}})
                    
                        #send_enter_race_email(user['email'])
                except Exception as e:
                    return str(e)
    else:
        if user['sponsor']:
            flash('Você só está autorizado a se inscrever em evento a partir de 30 minutos antes da abertura do server')
        else:
            flash('Você só está autorizado a se inscrever em evento a partir da abertura do server')
    return redirect(url_for('agenda'))

@application.route('/results')
def results():
    allresults = False
    raceresult_cursor = db.RaceResult.find().sort([('timestamp', -1)]).limit(20)
    return render_template('result.html', raceresult_cursor=raceresult_cursor, allresults=allresults)

@application.route('/allresults')
@cache.cached(timeout=300, unless=now >= (23,50))
def allresults():
    allresults = True
    raceresult_cursor = db.RaceResult.find().sort([('timestamp', -1)])
    return render_template('result.html', raceresult_cursor=raceresult_cursor, allresults=allresults)    
            
        

@application.route('/profile/<userid>',methods=['POST', 'GET'])
#@cache.cached(timeout=300, unless=now >= (23,50))
@csrf.exempt
def driver(userid):
    #defining the current user
    c_user = dbusers.users.find_one({'_id': current_user.get_id()})
    #print(c_user)
    form = EditProfile()
    formuploadphoto = UploadPhoto()
    
    #userid = current_user.get_id()
    #from pprint import pprint
    
    user = dbusers.users.find_one({'_id': userid})
    driver = db.Drivers.find_one({'steamID': user['steam_id']})
    season_driver = db.SeasonDrivers.find_one({'steamID': user['steam_id']})
    
    #histincident = db.HistIncident.find({'result.steamID': user['steam_id']}).sort([('filename', DESCENDING)])
    #pprint(driver)
    #pprint(user)
    if not season_driver:
        season_driver = {'top10': {
                    '1': 0, '2': 0, '3': 0},
                    'points': 'TBD',
                    'incidents': 0,
                    'pole': 0,
                    'unique_name': "",
                    'races_done': 0
                }
        season_driver['top10']['1'] = 0
        season_driver['top10']['2'] = 0
        season_driver['top10']['3'] = 0
        season_driver['classimg'] = ''
    if not driver:
        driver = {'top10': {
                    '1': 0, '2': 0, '3': 0},
                    'points': 'TBD',
                    'incidents': 0,
                    'pole': 0,
                    'unique_name': "",
                    'races_done': 0
                }
        driver['top10']['1'] = 0
        driver['top10']['2'] = 0
        driver['top10']['3'] = 0
        driver['classimg'] = ''
    else:
        
        driver['signedin'] = datetime.fromtimestamp(int(user['email_confirmed_on'])).strftime('%d-%m-%Y')
        driver['first'] = driver['top10']['1']
        driver['top3'] = int(driver['top10']['1']) + int(driver['top10']['2']) + int(driver['top10']['3']) 
        if 'incident_ave' in driver:
            driver['incidents'] = round((float(driver['incident_ave'])), 3)
            #print('round', round((float(driver['incident_ave'])), 3))
        else:
            driver['incidents'] = round((float(driver['incidents'] / driver['races_done'])), 3)
            #print('round', driver['incidents'])
        #print(driver['incidents'])
        driver['classimg'] = driver['classimg']
    if (type(driver['points']) == str):
        driver['points'] = 'TBD'
    else:
        try:
            driver['points'] = round(int(driver['points'], 3)) * 1000
        except:
            driver['points'] = round(driver['points'], 3) * 1000
        
    
    #global data
    top10list = []
    ratinglabels = ['start']
    ratingvalues = [0]
    ratingrange = [0]
    incidentlabels = ['start']
    incidentvalues = [0]
    incidentaverage = [0]
    rankposition = [0]
    ranklabels = ['start']
    racenum = 0
    racesList = []    
    
    if (driver['races_done'] > 0):
        for k, v in driver['top10'].items():
            top10list.append(v)
        top10list.append(driver['pole'])
        name = driver['unique_name']
        
        hist_rating = db.HistRating.find({'result.steamID':user['steam_id']})
        
        for rating in hist_rating:
            if (hist_rating.count() > 4):
                ratinglabels.append(rating['filename'])
                result = rating['result']
                for res in result:
                    if (res['steamID'] == user['steam_id']):
                        if (res['points'] <= 0):
                            ratingvalues.append(float(0))
                            ratingrange.append(float(0))
                        else:
                            ratingvalues.append(round(res['points']*1000, 2))
                            ratingrange.append(round((3* res['sigma'] + res['points']) * 1000))
        
        hist_incidents = db.HistIncident.find({'result.steamID':user['steam_id']})
         
        histlist = [0] 
        
        '''for incident in hist_incidents:
            incidentlabels.append(incident['filename'])
            incresult = incident['result']
            for inc_res in incresult:
                if (inc_res['steamID'] == user['steam_id']):
                    incidentvalues.append(round(inc_res['incidents'], 2))
                    racenum += 1
                    incidentaverage.append(round(inc_res['incidents'] / racenum, 2))'''
        
        for incident in hist_incidents:
            incidentlabels.append(incident['filename'])
            incresult = incident['result']
            for inc_res in incresult:
                if (inc_res['steamID'] == user['steam_id']):
                    incidentvalues.append(round(inc_res['raceincidents'], 2))
                    histlist.append(inc_res['raceincidents'])
        
        for hi in range(len(histlist)):
            if hi < 5 and hi > 0:
                incsum = sum(histlist[0:hi])
                #print('0', hi, incsum)
                incidentaverage.append(round(incsum/hi, 2))
            elif hi == 0:
                pass
            else:
                botsum = hi - 4
                incsum = sum(histlist[botsum:hi+1])/5
                #print(botsum, hi, incsum)
                incidentaverage.append(round(incsum, 2))
        
        hist_rank = db.HistRank.find()
        for rank in hist_rank:
            length = len(rank['positions'])
            #id_in = False
            for i in range(length):
                if rank['positions'][i]['steamID'] == user['steam_id']:
                    ranklabels.append(rank['filename'])
                    #id_in = True
                    rankposition.append(rank['positions'][i]['rank_pos'])
        #print(rankposition)
        ranklabels_len= len(ranklabels)
        ranklabels = ranklabels[ranklabels_len//3:]
        rankposition = rankposition[ranklabels_len//3:]
                
                
    #season data
    seasontop10list = []
    seasonratingvalues = []
    seasonratingrange = []
    seasonlabels = ['start']
    seasonrankposition = []
    seasonranklabels = ['start']
    if season_driver['races_done'] > 0:
        for k, v in season_driver['top10'].items():
            seasontop10list.append(v)
        seasontop10list.append(season_driver['pole'])
        

        season_hist_rating = db.SeasonHistRating.find({'result.steamID':user['steam_id']})
        for rating in season_hist_rating:
            seasonlabels.append(rating['filename'])
        
        season_hist_rank = db.SeasonHistRank.find()
        for rank in season_hist_rank:
            seasonranklabels.append(rank['filename'])
            
        
        for label in ratinglabels:
            if label in seasonlabels and label != 'start':
                season_race = db.SeasonHistRating.find_one({'filename':label})['result']
                for res in season_race:
                    if res['steamID'] == user['steam_id']:
                        if res['points'] <= 0:
                            seasonratingvalues.append(float(0))
                            seasonratingrange.append(float(0))
                        else:
                            seasonratingvalues.append(round(res['points']*1000, 2))
                            seasonratingrange.append(round((3* res['sigma'] + res['points']) * 1000))        
                        
            else:
                seasonratingvalues.append(float(0))
                seasonratingrange.append(float(0))
                
        for label in ranklabels:
            if label in seasonranklabels and label != 'start':
                season_rank = db.SeasonHistRank.find_one({'filename':label})['positions']
                for pos in season_rank:
                    if pos['steamID'] == user['steam_id']:
                        seasonrankposition.append(pos['rank_pos'])
            else:
                seasonrankposition.append(0)
                
            
        
        #print(incidentaverage)
            
    
    #user = dbusers.users.find_one({'_id': userid})
    #print(user)
    try:
        form.phrase.data = user['phrase'] 
        form.about.data = user['about']
        form.name.data = user['name']
        form.lastname.data = user['lastname']
        form.city.data = user['city']
        form.gender.data = user['gender']
        form.state.data = user['state']
        form.birthday.data = datetime.strptime(user['birthday'], '%d-%m-%Y')
    except:
        pass
    
    return render_template('user-single.html',formuploadphoto=formuploadphoto, form=form, user=user, 
                           top10list=top10list, ratingrange=ratingrange, incidentaverage=incidentaverage, 
                           incidentlabels=incidentlabels, incidentvalues=incidentvalues, userid=userid, 
                           driver=driver, ratinglabels = ratinglabels, ratingvalues=ratingvalues,
                           rankposition=rankposition, ranklabels=ranklabels, c_user=c_user, seasontop10list=seasontop10list,
                           seasonratingvalues=seasonratingvalues, seasonratingrange=seasonratingrange, seasonrankposition=seasonrankposition)

@application.route('/agenda')
@login_required
def agenda():
    #gets logged user information
    user = current_user.user_obj()
    driver = db.Drivers.find_one({'steamID': user['steam_id']})
    
    agenda = list(db.ScheduledRace.find().sort([('timestamp_start', 1)]))
    tz = pytz.timezone('Brazil/East')
    
    for i in range(len(agenda)):
        time_difference = tz.localize(datetime.strptime(agenda[i]['date'] + ' ' + agenda[i]['time'], '%d-%m-%Y %H:%M')) - datetime.now(tz)
        
        if time_difference < timedelta(0, 1800):
            agenda[i]['open'] = True
        else:
            agenda[i]['open'] = False
    
    return render_template('agenda.html', agenda=agenda, user=user)
    

@application.route('/raceresult/<raceid>')
@login_required
def raceresult(raceid):
    voters = db.ResultVote.find_one({'resultid': ObjectId(raceid)})
    user = current_user.get_id()
    username = current_user.get_username()
    print(username)
    result = db.RaceResult.find_one({'_id': ObjectId(raceid)})
    try:
        delta = db.HistRank.find_one({'filename': result['racefilename']})['positions']
    except:
        delta = []
        for res in result['race']:
            dr_dict = {'steamID': res['steamID'],
                       'delta' : 0}
            delta.append(dr_dict)
    
    for r in range(len(result['race'])):
        for de in delta:
            if de['steamID'] == result['race'][r]['steamID']:
                try:
                    result['race'][r]['delta'] = de['delta']
                except:
                    result['race'][r]['delta'] = 0
        if 'delta' not in result['race'][r]:
            result['race'][r]['delta'] = 0
       
           
           
            
    print(result['race'])
    
 
        
    practice = result['practice']
    qualify = result['qualify']
    race = result['race']
    return render_template('raceresult.html', result=result, practice=practice,
                           qualify=qualify, race=race, user=user, username=username, voters=voters, raceid=raceid)



@application.route('/upvote/<resultid>/<voterid>/<userid>')
@login_required
def upvote(resultid, voterid, userid):
    result = db.RaceResult.find_one({'_id': ObjectId(resultid),
                                     'race.userid': voterid})
    voteruser = dbusers.users.find_one({'_id': voterid})
    user = dbusers.users.find_one({'_id':userid})
    username = voteruser['username']
    votedict = {'voterid': voterid,
                'userid': userid,
                'username': username}
    
    user_steamid = user['steam_id']
    
    
 
    if voterid == userid:
        #check if user is trying to vote himself/herself
        flash('Recomendação não computada pois você não pode votar em si mesmo')
        #print('Votar em si mesmo')
        return redirect(url_for('raceresult', raceid=resultid))
        
    if not result:
        #check if the voter was participating in the race
        flash('Recomendação não computada pois ' + current_user.get_username() + ' não participou da corrida!')
        #print('Votante não participou da corrida')
        return redirect(url_for('raceresult', raceid=resultid))
    
    #Check if the voted id is really in the result
    result = db.RaceResult.find_one({'_id': ObjectId(resultid),
                                     'race.userid': userid})
    if not result:
        flash('Recomendação não computada pois o piloto em que você votou parece não ter participado da corrida!')
        #print('Votado não participou da corrida')
        return redirect(url_for('raceresult', raceid=resultid))
        
    votedoc = db.ResultVote.find_one({'resultid': ObjectId(resultid)})
        
    #CHECK IF A VOTING DOCUMENT IS ALREADY WRITTEN FOR THE RESULT
    if votedoc: 
        #Here the document already exists, so we update it!
        votelist = votedoc['upvote']
        downvotelist = votedoc['downvote']
        
        #Each user has ONE upvote for the race,
        #now we check if the user have already voted for any driver    
        votetwice = False
        for item in votedoc['upvote']:
            if item['voterid'] == voterid:
                votetwice = True #yes, he voted for some driver!
        
        #Now we check if the voter have already voted in the same driver
        vote = False
        if votedict in votelist:
            vote = True
                        
        #After checking, we update the Document
        if votetwice == False:
            #The voter didnt vote in any driver
            #we input his vote!
            votelist.append(votedict)
            if votedict in downvotelist:
                downvotelist.remove(votedict)
            db.ResultVote.update_one({'resultid': ObjectId(resultid)}, {'$set':{'upvote':votelist,
                                                                                'downvote': downvotelist}})
            db.Drivers.update_one({'steamID': user_steamid}, {'$inc': {'votes': 1}})
            flash('Recomendação computada')
            #print('Voto computado')
            
        else:
            #The voter have voted before, 
            #if he is voting in the same driver, we might take the vote out
            if vote:
                votelist.remove(votedict)
                db.ResultVote.update_one({'resultid': ObjectId(resultid)}, {'$set':{'upvote':votelist}})
                db.Drivers.update_one({'steamID': user_steamid}, {'$inc': {'votes': -1}})
                flash('Recomendação retirada!')
                #print('Voto retirado')
            #The voter has already voted. So we take out his/her vote
            elif votetwice:
                flash('Recomendação não computada pois você não pode recomendar mais de um piloto')
                #print('Recomendar duplamente')
                return redirect(url_for('raceresult', raceid=resultid))
                
    else:
        #Here the doc doesnt exist, so we create it
        db.ResultVote.insert_one({'resultid': ObjectId(resultid),
                                  'upvote': [votedict],
                                  'downvote': []})
        db.Drivers.update_one({'steamID': user_steamid}, {'$inc': {'votes': 1}})
        flash('Recomendação computada')
        #print('voto computado, db criado')
    return redirect(url_for('raceresult', raceid=resultid))

@application.route('/downvote/<resultid>/<voterid>/<userid>')
@login_required
def downvote(resultid, voterid, userid):
    result = db.RaceResult.find_one({'_id': ObjectId(resultid),
                                     'race.userid': voterid})
    username = dbusers.users.find_one({'_id': voterid})['username']
    votedict = {'voterid': voterid,
                'userid': userid,
                'username': username}
    if voterid == userid:
        #check if user is trying to vote himself/herself
        flash('Contra-indicação não computada pois você não pode votar em si mesmo')
        #print('Votar em si mesmo')
        return redirect(url_for('raceresult', raceid=resultid))
        
    if not result:
        #check if the voter was participating in the race
        flash('Contra-indicação não computada pois ' + current_user.get_username() + ' não participou da corrida!')
        #print('Votante não participou da corrida')
        return redirect(url_for('raceresult', raceid=resultid))
    
    #Check if the voted id is really in the result
    result = db.RaceResult.find_one({'_id': ObjectId(resultid),
                                     'race.userid': userid})
    if not result:
        flash('Contra-indicação não computada pois parece que o piloto não indicado não participou da corrida!')
        #print('Votado não participou da corrida')
        return redirect(url_for('raceresult', raceid=resultid))
        

    
    votedoc = db.ResultVote.find_one({'resultid': ObjectId(resultid)})
        
    #CHECK IF A VOTING DOCUMENT IS ALREADY WRITTEN FOR THE RESULT
    if votedoc: 
        #Here the document already exists, so we update it
        downvotelist = votedoc['downvote']
        votelist = votedoc['upvote']
        
        #Each user has ONE upvote for the race,
        #now we check if the user have already voted for any driver    
        votetwice = False
        for item in votedoc['downvote']:
            if item['voterid'] == voterid:
                votetwice = True #yes, he voted for some driver!
        
        #Now we check if the voter have already voted in the same driver
        vote = False
        if votedict in votelist:
            vote = True
                        
        #After checking, we update the Document
        if votetwice == False:
            #The voter didnt vote in any driver
            #we input his vote!
            downvotelist.append(votedict)
            if votedict in votelist:
                votelist.remove(votedict)
            db.ResultVote.update_one({'resultid': ObjectId(resultid)}, {'$set':{'upvote':votelist,
                                                                                'downvote': downvotelist}})
            flash('Contra-indicação computada!')
            #print('Voto computado')
            
        else:
            #The voter have voted before, 
            #if he is voting in the same driver, we might take the vote out
            if vote:
                votelist.remove(votedict)
                db.ResultVote.update_one({'resultid': ObjectId(resultid)}, {'$set':{'downvote':votelist}})
                flash('Contra-indicação retirada!')
                #print('Voto retirado')
            #The voter has already voted. So we take out his/her vote
            elif votetwice:
                flash('Contra-indicação não computada pois você não pode contra-indicar mais de um piloto')
                #print('Recomendar duplamente')
                return redirect(url_for('raceresult', raceid=resultid))
    
    else:
        #Here the doc doesnt exist, so we create it
        db.ResultVote.insert_one({'resultid': ObjectId(resultid),
                                  'upvote': [],
                                  'downvote': [votedict]})
        flash('Contra-indicação computada!')
        #print('voto computado, db criado')
    return redirect(url_for('raceresult', raceid=resultid))
    
'''
@application.route('/conduta')
def conduct():
    return render_template('conduta.html')'''

@application.route('/getRandom', methods=['POST'])
@csrf.exempt
def getRandom():
    try:
        track_car_list = [[],[]]
        track = 'static/images/randomizer/tracks'
        cars = 'static/images/randomizer/cars'
        subdirscars = [x[0] for x in os.walk(cars)]
        subdirstracks = [x[0] for x in os.walk(track)]
        for subdir in subdirscars:
            files = next(os.walk(subdir))[2]
            if (len(files) > 0):
                for file in files:
                    track_car_list[1].append(base64.standard_b64encode(open(subdir + "/" + file,"rb").read()).decode('utf-8'))
        for subdir in subdirstracks:
            files = next(os.walk(subdir))[2]
            if (len(files) > 0):
                for file in files:
                    track_car_list[0].append(base64.standard_b64encode(open(subdir + "/" + file,"rb").read()).decode('utf-8'))
        #print(jsonify(track_car_list), track_car_list)
    except Exception as e:
        return str(e)
    return jsonify(track_car_list)

@application.route('/trackrecords', methods =['GET', 'POST'])
def trackrecords():
    form = recordsForm()
    all_records = db.RaceRecord.find()
    recordtable = []
    tracks = {}
    cars = {}
    for record in all_records:
        tracks[record['track'][1]] = record['track'][0]
        cars[record['car'][1]] = record['car'][0]
        recordtable.append(record)
   
                
    choices = [('','')] + [(k, v) for k, v in tracks.items()]
    choices = sorted(choices, key=lambda choice: choice[1])
    form.track.choices = choices
    #form.car.choices = [(k, v) for k, v in cars.items()]
    
    if form.validate_on_submit():
        try:
            selected_record = db.RaceRecord.find_one({'track.1': form.track.data,'car.1': form.car.data})
            _id = selected_record['_id']
            print(_id)
        except Exception as e:
            return str(e)
            
                
    return render_template('trackrecord.html', form=form)

@application.route('/trecord/<track>')
def trecord(track):
    try:
        #print(track)
        records = db.RaceRecord.find({'track.1': track})
        #print(db.RaceRecord.find({'track.1': track}).count())
        
        cars_array = []
        
        for record in records:
            carObj = {'car': record['car'][0],
                      'id': record['car'][1]}
            cars_array.append(carObj)
        
        
        #print(cars_array)
         
    except Exception as e:
        return str(e)
    return jsonify({'cars': cars_array})   
        

@application.route('/getrecord') 
@csrf.exempt
def getrecord():
    try:
        recdb = db.RaceRecord.find()
        recarray = []
        
        for item in recdb:
            itemObj = {}
            itemObj['car'] = item['car'][1]
            itemObj['track'] = item['track'][1]
            itemObj['laprecord'] = item['laprecord']
            for i in range(len(itemObj['laprecord'])):
                obj = (itemObj['laprecord'][i]['resultid'])
                strobj = str(obj)
                itemObj['laprecord'][i]['resultid'] = strobj
            recarray.append(itemObj)
            print(recarray)
        print(recarray)
    except Exception as e:
        return str(e)
    return jsonify({'records': recarray})



@application.route('/randomizer')
def randomizerPage():  
    return render_template('random.html')


    
if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
