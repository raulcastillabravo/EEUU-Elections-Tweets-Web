#**************** #
# *** IMPORTS *** #
#**************** #

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
from datetime import datetime
from Model import Model


# *********************************** #
# *** LOAD THE DEEPLEARNING MODEL *** #
# *********************************** #

model = Model('./deeplearning_model/deployable_middle_model')


# ******************************************** #
# *** CREATE THE APP AND LOAD THE DATABASE *** #
# ******************************************** #

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


# *************************** #
# *** FUNCTIONS AND CLASS *** #
# *************************** #

class Tweet(db.Model):
    """
    Data structure to save the information of each tweet in 
    the database.

    """

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    politic = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Tweet %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Load the index page and introduced new tweets if
    there is a POST.

    """

    if request.method == 'POST':

        # Get tweet text
        tweet_content = request.form['content']

        # Predict with the DeepLearning model
        prediction = model.predict(tweet_content)

        # Save prediction
        if prediction is None:
            politic = 'Not English'
        else:
            if prediction == 0:
                politic = 'Trump'
            else:
                politic = 'Biden'

        # Create the tweet object
        new_tweet = Tweet(content=tweet_content, politic=politic)
  
        try:
            # Remove tweets if there is more than 9 to keep
            # the table in 10 tweets
            num_tweets = db.session.query(Tweet.id).count()
            while num_tweets > 9:
                
                # Get the older tweet
                tweet_to_delete = Tweet.query.order_by(Tweet.date_created.asc()).first()

                # Remove the tweet
                db.session.delete(tweet_to_delete)

                # Recalculate the number of tweets
                num_tweets = db.session.query(Tweet.id).count()
            
            # Add the new tweet
            db.session.add(new_tweet)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
        
    else:
        # Show tweets order by date posted
        tweets = Tweet.query.order_by(Tweet.date_created.desc()).all()

        return render_template('index.html', tweets=tweets)

@app.route('/delete/<int:id>')
def delete(id):
    """
    Delete a tweet after pressing the delete action.

    """

    # Get the tweet selected by the user
    tweet_to_delete = Tweet.query.get_or_404(id)

    try:
        # Delete the tweet
        db.session.delete(tweet_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


def create_app():
    """
    Create and run the app in localhost port 8000.
    
    """
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=True)

