from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tweet %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        tweet_content = request.form['content']

        new_tweet = Tweet(content = tweet_content)

        try:
            db.session.add(new_tweet)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
        
    else:
        tweets = Tweet.query.order_by(Tweet.date_created).all()

        return render_template('index.html', tweets=tweets)

@app.route('/delete/<int:id>')
def delete(id):
    tweet_to_delete = Tweet.query.get_or_404(id)

    try:
        db.session.delete(tweet_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=True)

