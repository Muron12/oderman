from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class FeedbackForm(FlaskForm):
    name = StringField('Ваше імʼя', validators=[DataRequired(), Length(max=50)])
    rating = SelectField('Оцінка', choices=[('good', 'Гарно'), ('bad', 'Погано')], validators=[DataRequired()])
    comment = TextAreaField('Коментар', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Надіслати')
