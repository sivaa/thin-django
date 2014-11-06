from _io import BytesIO
import hashlib
import os
import sys
import urllib

import Image
import ImageDraw
from django import forms
from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import etag


# Settings
BASE_DIR = os.path.dirname(__file__)
settings.configure(
                   DEBUG            =   os.environ.get('DEBUG', 'on') == 'on',
                   ALLOWED_HOSTS    =   os.environ.get('ALLOWED_HOSTS', 'localhost').split(","),
                   SECERT_KEY       =   os.environ.get('SECERT_KEY', ''),
                   ROOT_URLCONF     =   __name__,

                   MIDDLEWARE_CLASSES   = (
                                           'django.middleware.common.CommonMiddleware',
                                           'django.middleware.csrf.CsrfViewMiddleware',
                                           'django.middleware.clickjacking.XFrameOptionsMiddleware',
                   ),
                   TEMPLATE_DIRS        =  (
                                            os.path.join(BASE_DIR, "templates"),
                   ),
)

from django.core.cache import cache

## Forms
class ImageForm(forms.Form):
    image_url           =   forms.URLField()
    water_mark_text     =   forms.CharField(min_length=3)

    def add_water_mark(self):
        image_url           =   self.cleaned_data['image_url']
        water_mark_text     =   self.cleaned_data['water_mark_text']

        # Download the image from image_url
        image_key      = hashlib.sha224(image_url).hexdigest()

        # Check in cache
        image_location = cache.get(image_key)

        if image_location is None:
#             print "Not found in Cache", water_mark_text, image_url
            image_location = os.path.join('images', image_key)

            with open(image_location, 'wb') as fp:
                fp.write(urllib.urlopen(image_url).read())

            cache.set(image_key, image_location)
#         else :
#             print "Found in Cache", water_mark_text, image_url

        image_content = Image.open(image_location)
        draw = ImageDraw.Draw(image_content)

        draw.text((100, 100), water_mark_text, (255, 0 , 0))

        content = BytesIO()
        image_content.save(content, "PNG")
        content.seek(0)

        return content


## Views
def home(request):
    return render(request, "index.html")

def etag_water_mark_image(request, image_url, water_mark_text):
    wm_key = "WM : {} : {}".format(image_url, water_mark_text)
    return hashlib.sha224(wm_key.encode('utf-8')).hexdigest()

@etag(etag_water_mark_image)
def water_mark_image(request, image_url, water_mark_text):
    print "ETAG NOT HIT", water_mark_text, image_url
    image_form = ImageForm({'image_url'         : image_url,
                            'water_mark_text'   : water_mark_text
                            })

    if image_form.is_valid() is False:
        return HttpResponseBadRequest("Invalid Data Supplied.")

    image = image_form.add_water_mark()
    return HttpResponse(image, content_type='image/png')

# Routing
urlpatterns = (
               url(r'^image/(?P<image_url>.*)/(?P<water_mark_text>.*)/$', water_mark_image, name='water_mark_image'),
               url(r'^$', home, name='home'),
)

# Execution
application = get_wsgi_application()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
