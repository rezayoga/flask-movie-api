from dataclasses import dataclass
from datetime import datetime
from flaskvuenginx.starter import app
import pathlib
print(str(pathlib.Path().resolve()))

@dataclass
class Task(app.db.Model):

    id: int
    title: str
    date: datetime
    completed: bool

    id = app.db.Column(app.db.Integer(), primary_key=True)
    title = app.db.Column(app.db.String(140))
    date = app.db.Column(app.db.DateTime(), default=datetime.now())
    completed = app.db.Column(app.db.Boolean(), default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Task id: {self.id} - {self.title}>'