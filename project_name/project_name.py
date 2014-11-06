import os
import sys

from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.http.response import HttpResponse


## Views
def home(request):
    return HttpResponse("Hello {{ project_name }}!")

# Routing
urlpatterns = (
               url(r'^$', home, name='home'),
)

# Settings
settings.configure(
                   DEBUG            =   os.environ.get('DEBUG', 'on') == 'on',
                   ALLOWED_HOSTS    =   os.environ.get('ALLOWED_HOSTS', 'localhost').split(","),
                   SECERT_KEY       =   os.environ.get('SECERT_KEY', '{{ secert_key }}'),
                   ROOT_URLCONF     =   __name__,
                   MIDDLEWARE_CLASSES = (
                                         'django.middleware.common.CommonMiddleware',
                                         'django.middleware.csrf.CsrfViewMiddleware',
                                         'django.middleware.clickjacking.XFrameOptionsMiddleware',
                   )
)

# Execution
application = get_wsgi_application()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
