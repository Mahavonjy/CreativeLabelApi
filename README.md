All Installation (#Python3)

install run elasticsearch before with port 9200
 
you should also install python3-venv and pip

__copy and run the following command from step 0 to 4 and 7 on your terminal___

0)`git clone this project`

1)`python3 -m venv venv`

2)`source venv/bin/activate`

3)`pip install --upgrade pip`

4)`pip install -r requirements.txt`

5)`create CreativeLabel.json and requests the content from the administrator`

6)**** _create file_ `.env` _and put it_ ****

    # this is a file run.py who run the flask app
    FLASK_APP=run.py
    
    # in this variable is located the file of Google credential for login
    # Contact admin for this information
    GOOGLE_APPLICATION_CREDENTIALS=CreativeLabel.json
    
    # sentry credentials
    SENTRY_SDK_DSN=your_sentry_key"
    
    # cloudinary credentials
    CLOUDINARY_CLOUD_NAME=your_cloudinary_name
    CLOUDINARY_API_KEY=your_cloudinary_key
    CLOUDINARY_API_SECRET=your_cloudinary_secret
    
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

___Ask the administrator for certain information in the .env file___
    
7)```(cd scripts && ./migrate.sh)```

###### run this command for start `flask run`


```UNITTESTING PROJECT``

use ```./scripts/run_tests.sh .env```
