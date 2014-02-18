from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from masquerade.forms import MaskForm, MaskUserForm
from masquerade.signals import mask_on, mask_off

MASQUERADE_REDIRECT_URL = getattr(settings, 'MASQUERADE_REDIRECT_URL', '/')

MASQUERADE_REQUIRE_SUPERUSER = getattr(settings,
  'MASQUERADE_REQUIRE_SUPERUSER', False)

def mask(request, template_name='masquerade/mask_form.html', pk=None):
    if not request.user.is_masked and not request.user.is_staff:
        return HttpResponseForbidden()
    elif not request.user.is_superuser and MASQUERADE_REQUIRE_SUPERUSER:
        return HttpResponseForbidden()

    if pk:
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            form = MaskUserForm(request.POST)
            if form.is_valid():
                request.session['mask_user'] = user.username
                mask_on.send(sender=form, mask_username=user.username)
                return HttpResponseRedirect(MASQUERADE_REDIRECT_URL)
        else:
            form = MaskUserForm()
            return render_to_response('masquerade/mask_user_form.html',
                                      {'form': form, 'user': user}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = MaskForm(request.POST)
        if form.is_valid():
            # turn on masquerading
            request.session['mask_user'] = form.cleaned_data['mask_user']
            mask_on.send(sender=form,
                mask_username=form.cleaned_data['mask_user'])
            return HttpResponseRedirect(MASQUERADE_REDIRECT_URL)
    else:
        form = MaskForm()

    return render_to_response(template_name, {'form': form},
      context_instance=RequestContext(request))

def unmask(request):
    # Turn off masquerading. Don't bother checking permissions.
    try:
        mask_username = request.session['mask_user']
        del(request.session['mask_user']) 
        mask_off.send(sender=object(), mask_username=mask_username)
    except KeyError:
        pass

    return HttpResponseRedirect(MASQUERADE_REDIRECT_URL)
