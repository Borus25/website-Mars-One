from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    job_title = TextAreaField('Job Title', validators=[DataRequired()])
    team_leader_id = StringField("Team Leader id", validators=[DataRequired()])
    work_size = StringField("Work size", validators=[DataRequired()])
    collaborators = StringField("Collaborators", validators=[DataRequired()])
    is_finished_job = BooleanField("Is finished job?")
    submit = SubmitField('Submit')