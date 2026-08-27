from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import BlogPost


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)

    return JsonResponse({
        'success': True,
        'posts': [{
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt or (p.content[:150] if p.content else ''),
            'image': p.image.url if p.image else None,
            'author': p.author.get_full_name() or p.author.username if p.author else 'Mahi Solar',
            'created_at': p.created_at.strftime('%d %b %Y') if p.created_at else '',
            'views_count': p.views_count,
            'tags': p.tags if p.tags else '',
        } for p in posts],
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views_count += 1
    post.save(update_fields=['views_count'])
    related = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]

    return JsonResponse({
        'success': True,
        'post': {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'content': post.content,
            'excerpt': post.excerpt,
            'image': post.image.url if post.image else None,
            'author': post.author.get_full_name() or post.author.username if post.author else 'Mahi Solar',
            'created_at': post.created_at.strftime('%d %b %Y') if post.created_at else '',
            'views_count': post.views_count,
            'tags': post.tags if post.tags else '',
        },
        'related': [{
            'id': r.id,
            'title': r.title,
            'slug': r.slug,
            'excerpt': r.excerpt or (r.content[:150] if r.content else ''),
            'image': r.image.url if r.image else None,
            'created_at': r.created_at.strftime('%d %b %Y') if r.created_at else '',
        } for r in related],
    })
