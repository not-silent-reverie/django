from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Product, Review
from .forms import RegistrationForm, LoginForm, ReviewForm, FeedbackForm
from .vk_notify import send_vk_message
from django.db.models import Avg, Count
import json

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
            print("Ошибки формы:", form.errors)
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
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


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', 'Не указан')
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']

            try:
                vk_message = f"""НОВАЯ ЗАЯВКА С САЙТА

 Имя: {name}
 Email: {email}
 Телефон: {phone}
 Тема: {subject}

 Сообщение:
 {message_text}

 🕐 {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}"""

                send_vk_message(settings.VK_USER_ID, vk_message)
                messages.success(request, 'Сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
            except Exception as e:
                messages.error(request, f'Ошибка отправки: {e}')

            return redirect('feedback_success')
    else:
        form = FeedbackForm()

    return render(request, 'mainpage/feedback.html', {'form': form})


def feedback_success(request):
    return render(request, 'mainpage/feedback_success.html')


@csrf_exempt
@require_POST
def vk_webhook(request):
    try:
        data = json.loads(request.body)

        if data.get('type') == 'confirmation':
            return HttpResponse(settings.VK_CONFIRMATION_CODE, content_type='text/plain')

        if data.get('type') == 'message_new':
            message = data.get('object', {}).get('message', {})
            user_id = message.get('from_id')
            text = message.get('text', '')

            if text.lower() == 'привет':
                response = ' Привет! Это бот Apex!'
            elif text.lower() == 'помощь':
                response = ' Команды:\n- Привет\n- Помощь\n- Товары\n- Контакты\n- Сайт'
            elif text.lower() == 'товары':
                response = '🛍 Каталог товаров: https://ваш-проект.up.railway.app/catalog/'
            elif text.lower() == 'контакты':
                response = ' Свяжитесь с нами:\nEmail: info@apex.ru\nТелефон: +7 (999) 123-45-67'
            elif text.lower() == 'сайт':
                response = ' Наш сайт: https://ваш-проект.up.railway.app/'
            else:
                response = ' Неизвестная команда. Напишите "Помощь" для списка команд.'

            send_vk_message(user_id, response)
            return JsonResponse({'ok': True})

        return JsonResponse({'ok': True})

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def api_like(request, product_id):
    """API для лайков/дизлайков"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        action = data.get('action')
        product = Product.objects.get(id=product_id)

        if action == 'like':
            product.likes += 1
        elif action == 'dislike':
            product.dislikes += 1
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        product.save()

        return JsonResponse({
            'success': True,
            'likes': product.likes,
            'dislikes': product.dislikes,
            'percent': product.get_rating_percent()
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def api_comment(request, product_id):
    """API для комментариев (fallback)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        comment = data.get('comment')
        rating = data.get('rating', 0)

        product = Product.objects.get(id=product_id)

        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return JsonResponse({
            'success': True,
            'review_id': review.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)