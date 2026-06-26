import json
from .vk_notify import send_vk_message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Product, Review
from .forms import RegistrationForm, LoginForm, ReviewForm


@csrf_exempt
@require_POST
def vk_webhook(request):
    try:
        data = json.loads(request.body)

        if data.get('type') == 'confirmation':
            confirmation_code = getattr(settings, 'VK_CONFIRMATION_CODE', '04b3e813')
            return JsonResponse({'response': confirmation_code})

        if data.get('type') == 'message_new':
            message = data.get('object', {}).get('message', {})
            user_id = message.get('from_id')
            text = message.get('text', '')

            from .vk_notify import send_vk_message
            send_vk_message(user_id, "Ваше сообщение получено!")

            return JsonResponse({'ok': True})

        return JsonResponse({'ok': True})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def index(request):
    top_products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    ).filter(
        reviews_count__gt=0
    ).order_by('-avg_rating')[:3]

    if top_products.count() < 3:
        existing_ids = top_products.values_list('id', flat=True)
        additional_products = Product.objects.exclude(
            id__in=existing_ids
        ).order_by('-created_at')[:3 - top_products.count()]

        top_products = list(top_products) + list(additional_products)

    context = {
        'top_products': top_products,
    }
    return render(request, 'mainpage/index.html', context)


def catalog(request):
    products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    ).order_by('-created_at')
    return render(request, 'mainpage/catalog.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'average_rating': product.average_rating(),
        'reviews_count': product.reviews_count(),
    }
    return render(request, 'mainpage/product_detail.html', context)


def about(request):
    return render(request, 'mainpage/about.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'mainpage/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'mainpage/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('index')

