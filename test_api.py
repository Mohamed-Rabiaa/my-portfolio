from blog.models import Category, BlogPost
from django.test import Client
import json

c = Client()
cat = Category.objects.first()
print(f'Category: {cat.name} ({cat.slug})')

# Test basic endpoint
response = c.get('/api/blog/posts/')
print(f'Basic endpoint status: {response.status_code}')

if response.status_code == 200:
    data = json.loads(response.content)
    print(f'Results count: {len(data.get("results", []))}')
    if data.get('results'):
        print(f'First post category: {data["results"][0].get("category")}')

# Test filtering by category slug
response = c.get(f'/api/blog/posts/?category={cat.slug}')
print(f'Filter by category slug status: {response.status_code}')
if response.status_code != 200:
    print(f'Error content: {response.content.decode()[:500]}')

# Test filtering by category ID
response = c.get(f'/api/blog/posts/?category={cat.id}')
print(f'Filter by category ID status: {response.status_code}')
if response.status_code != 200:
    print(f'Error content: {response.content.decode()[:500]}')