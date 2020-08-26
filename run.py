#!/usr/bin/env python3
""" shebang """

from preferences.config import Production as Prod
from sources.app import welcome
from sources.models import es
import os

app = welcome(os.getenv('FLASK_ENV'))

for index in Prod.ES_INDEX:
    # warnings
    if not es.indices.exists(index=index):
        es.indices.create(index=index)

if __name__ == '__main__':
    """ 
        This is the application main  
    """

    app.run(threaded=True)
    # app.run(ssl_context='adhoc')  # transform http to https
