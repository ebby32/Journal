from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from werkzeug.utils import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField, CKEditor
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.secret_key = "This_is_another_secret_key"

ckeditor = CKEditor(app)

Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db =SQLAlchemy(model_class=Base)
db.init_app(app)

today = datetime.today()

class Entry(FlaskForm):
    date = today.strftime('%Y-%m-%d')
    title = StringField('Title')
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')

class EditForm(FlaskForm):
    date = today.strftime('%Y-%m-%d')
    title = StringField('Title')
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class Journal(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    date:Mapped[str] = mapped_column(String(50), nullable=False)
    title:Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    body:Mapped[str] = mapped_column(String(1000), nullable=False)


with app.app_context():
    db.create_all()




@app.route('/', methods = ['GET', 'POST'])
def home():
    data = db.session.execute(db.select(Journal).order_by(Journal.id)).scalars().all()
    return render_template('home.html', journal_data=data)


@app.route('/read/<int:entry_id>', methods =['GET','POST'])
def read(entry_id):
    body_to_show=db.session.execute(db.select(Entry).where(Entry.id==entry_id)).scalar()

    return render_template('body.html', body = body_to_show)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = Entry()
    if form.validate_on_submit():
        new_entry = Journal(
            title = request.form.get('title'),
            body = request.form.get('body')
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form = form)

@app.route('/delete/<int:entry_id>', methods = ['GET','POST'])
def delete(entry_id):
    to_delete = db.session.execute(db.select(Entry).where(Entry.id == entry_id)).scalar()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit_entry/<int:entry_id>', methods = ['GET', 'POST'])
def edit(entry_id):
    entry_to_edit = db.session.execute(db.select(Entry).where(Entry.id == entry_id)).scalar()
    if request.method == 'POST':
        entry_to_edit.title = request.form.get('title')
        entry_to_edit.body = request.form.get('body')
        db.session.commit()
        return redirect(url_for('read'))
    return render_template('edit.html', entry = entry_to_edit)


if __name__=='__main__':
    app.run(debug=True)

