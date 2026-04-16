import json
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Prompt


def get_redis():
    password = getattr(settings, 'REDIS_PASSWORD', None)
    kwargs = {
        'host': getattr(settings, 'REDIS_HOST', 'localhost'),
        'port': getattr(settings, 'REDIS_PORT', 6379),
        'db': getattr(settings, 'REDIS_DB', 0),
        'socket_connect_timeout': 2,
        'socket_timeout': 2,
    }
    if password:
        kwargs['password'] = password
    return redis.Redis(**kwargs)


@csrf_exempt
def prompt_list(request):
    if request.method == 'GET':
        prompts = Prompt.objects.all().values('id', 'title', 'complexity', 'created_at')
        result = [
            {
                'id': p['id'],
                'title': p['title'],
                'complexity': p['complexity'],
                'created_at': p['created_at'].isoformat(),
            }
            for p in prompts
        ]
        return JsonResponse(result, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

        title = str(data.get('title', '')).strip()
        content = str(data.get('content', '')).strip()
        complexity = data.get('complexity')

        errors = {}
        if len(title) < 3:
            errors['title'] = 'Title must be at least 3 characters.'
        if len(content) < 20:
            errors['content'] = 'Content must be at least 20 characters.'
        if not isinstance(complexity, int) or not (1 <= complexity <= 10):
            errors['complexity'] = 'Complexity must be an integer between 1 and 10.'

        if errors:
            return JsonResponse({'errors': errors}, status=400)

        prompt = Prompt.objects.create(title=title, content=content, complexity=complexity)
        return JsonResponse({
            'id': prompt.id,
            'title': prompt.title,
            'content': prompt.content,
            'complexity': prompt.complexity,
            'created_at': prompt.created_at.isoformat(),
        }, status=201)

    return JsonResponse({'error': 'Method not allowed.'}, status=405)


def prompt_detail(request, prompt_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    try:
        prompt = Prompt.objects.get(id=prompt_id)
    except Prompt.DoesNotExist:
        return JsonResponse({'error': 'Prompt not found.'}, status=404)

    view_count = 0
    try:
        r = get_redis()
        key = f'prompt:{prompt.id}:views'
        view_count = int(r.incr(key))
    except Exception:
        # Redis is optional in deployed environments; return prompt data even if Redis is unavailable.
        view_count = 0

    return JsonResponse({
        'id': prompt.id,
        'title': prompt.title,
        'content': prompt.content,
        'complexity': prompt.complexity,
        'created_at': prompt.created_at.isoformat(),
        'view_count': view_count,
    })
