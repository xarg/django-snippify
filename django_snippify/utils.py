import json

from django.http import HttpResponse
from django.template import RequestContext, loader, Context

def build_context(request, extra_context = {}):
    """ Add flash message from session, and add some custom vars via extra_context"""
    if 'flash' in request.session:
        extra_context['flash']= request.session['flash']
        del request.session['flash']
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] =  value() if callable(value) else value
    return context

def extend(class_to_extend):
    """ Dinamicaly extend a class via decorator"""
    def decorator(extending_class):
        extending_class.__dict__.update(class_to_extend.__dict__)
        return class_to_extend
    return decorator

class JsonResponse(HttpResponse):
    """ XXX: Broken """
    def __init__(self, data):
        content = json.dumps(data, indent=2, ensure_ascii=False)
        super(JsonResponse, self).__init__(content=content,
                                    mimetype='application/json; charset=utf8')
