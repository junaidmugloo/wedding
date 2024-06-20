# 1 activate virtual env
# 2 virtual/Scripts/Activate.ps1
# 3 ~ deactivate
# 4  django-admin startapp su_admin   
# If your database is not on localhost or is secured, you should also fill in the CLIENT information like HOST, USERNAME, PASSWORD, etc.
<!-- DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': 'mongodb+srv://<username>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority'
            }  
        }
} -->


# pip install djongo