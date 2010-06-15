from django.conf.urls.defaults import *
import views as vv;
urlpatterns = patterns('',
    (r'^$', vv.begin,{'sreg':'nickname,email,fullname,dob,gender,postcode,country,language,timezone'}),
    (r'^complete/$', vv.complete),
    (r'^signout/$', vv.signout),
)