from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Product
from .models import Product, Cart, CartItem
from django.utils.decorators import method_decorator


def home(request):
    return render(request, 'home.html')

def products(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'products.html', {'products': products})

@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            
            # Ensure session_key is set and valid
            session_id = request.session.session_key
            if not session_id:
                request.session.save()
                session_id = request.session.session_key

            # Retrieve or create the cart for this session
            cart, created = Cart.objects.get_or_create(session_id=session_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not created:
                # If the item already exists, increase the quantity
                cart_item.quantity += 1
                cart_item.save()
            else:
                # If it's a new item, set quantity to 1
                cart_item.quantity = 1
                cart_item.save()

            return JsonResponse({'status': 'success', 'cart_item_id': cart_item.id})

        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)
    
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)

            # Ensure session_key is set and valid
            session_id = request.session.session_key
            if not session_id:
                request.session.save()
                session_id = request.session.session_key
            
            # Retrieve the cart for this session
            cart = get_object_or_404(Cart, session_id=session_id)
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()

            if cart_item:
                cart_item.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)
    
    return JsonResponse({'status': 'failed'}, status=400)

def cart_view(request):
    session_id = request.session.session_key or request.session.create()
    cart = Cart.objects.filter(session_id=session_id).first()
    cart_items = CartItem.objects.filter(cart=cart) if cart else []
    
    return render(request, 'cart.html', {'cart_items': cart_items})

def contact(request):
    return render(request, 'contact.html')
