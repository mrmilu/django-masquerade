from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^mask/$', 'masquerade.views.mask'),
    url(r'^mask/(?P<pk>\w+)$', 'masquerade.views.mask', name="masquerade_user"),
    url(r'^unmask/$', 'masquerade.views.unmask'),
)
