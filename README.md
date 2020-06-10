All Installation

run elasticsearch before with port 9200

0)`git clone this project`

1)`python3 -m venv venv`

2)`source venv/bin/activate`

3)`pip install --upgrade pip`

4)`pip install -r requirements.txt`

**** _create file_ `.env` _and put it_ ****

    # this is a file run.py who run the flask app
    FLASK_APP=run.py
    
    # in this variable is located the file of Google credential for login
    # Contact admin for this information
    GOOGLE_APPLICATION_CREDENTIALS=CreativeLabel.json
    
    # this is a secret key
    # this is a key for encode or decode token JWT
    JWT_SECRET_KEY="qwerty"
    # th flask app use this key for build
    FN_FLASK_SECRET_KEY="IslCreative"
    
    # Email config
    # in this variable is located the mail of admin
    MAIL_USERNAME_API=mahavonjy.cynthion@gmail.com
    # in this variable is located the password of admin email
    MAIL_PASSWORD_API=contact_support_for_password
    
    # Social Network Configuration for login register
    # This is a facebook_app_id
    FACEBOOK_APP_ID=your_facebook_app_id
    # This is a facebook_app_secret_key
    FACEBOOK_APP_SECRET=your_facebook_app_secret
    
    # Here is Google client ID
    GOOGLE_CLIENT_ID=your_google_id
    # Here is the link for check the profile information
    GOOGLE_USER_INFO=https://www.googleapis.com/userinfo/v2/me
    
    # Here is my environemnt name
    FLASK_ENV="development"

###### run this command for start `flask run`