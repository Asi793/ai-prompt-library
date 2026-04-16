import json
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Prompt


def get_redis():
    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


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

    r = get_redis()
    key = f'prompt:{prompt.id}:views'
    view_count = int(r.incr(key))

    return JsonResponse({
        'id': prompt.id,
        'title': prompt.title,
        'content': prompt.content,
        'complexity': prompt.complexity,
        'created_at': prompt.created_at.isoformat(),
        'view_count': view_count,
    })
