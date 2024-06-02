# views.py
from django.views.decorators.cache import cache_page
from django.db.models.functions import TruncDay, TruncHour, TruncWeek, TruncMonth, TruncYear
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Max
from .models import Orders, Users, Transactions, TransactionItems
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from datetime import datetime as dt

def fetch_order_summaries(request):
    orders = Orders.objects.all()
    order_summaries = orders.values('order_type').annotate(total_sum=Sum('total'))

    if request.GET.get('format') == 'json':
        return JsonResponse(list(order_summaries), safe=False)

    return render(request, 'order_summaries.html', {'order_summaries': order_summaries})

def fetch_order_summaries_total(request):
    orders = Orders.objects.all()

    hourly_orders = orders.annotate(period=TruncHour('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')
    daily_orders = orders.annotate(period=TruncDay('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')
    monthly_orders = orders.annotate(period=TruncMonth('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')

    def prepare_data(queryset, period_key):
        data = {}
        for item in queryset:
            period = item[period_key].strftime('%Y-%m-%dT%H:%M:%SZ')
            order_type = item['order_type']
            total_sum = round(float(item['total_sum']), 0)
            if period not in data:
                data[period] = {}
            data[period][order_type] = total_sum
        return [{'period': period, **totals} for period, totals in data.items()]

    result = {
        'hourly': prepare_data(hourly_orders, 'period'),
        'daily': prepare_data(daily_orders, 'period'),
        'monthly': prepare_data(monthly_orders, 'period')
    }

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'order_summaries.html', {'result': result})

def fetch_order_status_summary(request):
    orders = Orders.objects.all()

    def get_aggregated_data(trunc_function, filter_recent=False):
        aggregated_data = orders.annotate(period=trunc_function('created_at')).values('status', 'period').annotate(
            count=Count('id'), total_sum=Sum('total'))

        if filter_recent:
            most_recent_period = aggregated_data.aggregate(most_recent=Max('period'))['most_recent']
            aggregated_data = aggregated_data.filter(period=most_recent_period)

        return list(aggregated_data)

    def calculate_profit_percentage(data):
        completed_count = sum(item['count'] for item in data if item['status'] == 'completed')
        other_count = sum(item['count'] for item in data if item['status'] != 'completed')
        profit_percentage = (completed_count / (completed_count + other_count)) * 100 if (completed_count + other_count) > 0 else 0
        return profit_percentage

    daily_orders = get_aggregated_data(TruncDay, filter_recent=True)
    weekly_orders = get_aggregated_data(TruncWeek)
    monthly_orders = get_aggregated_data(TruncMonth)
    yearly_orders = get_aggregated_data(TruncYear)

    daily_profit_percentage = calculate_profit_percentage(daily_orders)
    weekly_profit_percentage = calculate_profit_percentage(weekly_orders)
    monthly_profit_percentage = calculate_profit_percentage(monthly_orders)
    yearly_profit_percentage = calculate_profit_percentage(yearly_orders)

    result = {
        'daily': daily_orders,
        'weekly': weekly_orders,
        'monthly': monthly_orders,
        'yearly': yearly_orders,
        'profit_percentage': {
            'daily': daily_profit_percentage,
            'weekly': weekly_profit_percentage,
            'monthly': monthly_profit_percentage,
            'yearly': yearly_profit_percentage,
        }
    }

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'order_status_summary.html', {'result': result})



def is_valid_datetime(dt_value):
    try:
        if dt_value and isinstance(dt_value, dt):
            return True
        return False
    except ValueError:
        return False

def calculate_latest_and_previous(data):
    if len(data) < 2:
        return data
    latest = data[-1]
    previous = data[-2]
    latest['percentage_difference'] = ((latest['total_count'] - previous['total_count']) / previous['total_count']) * 100 if previous['total_count'] != 0 else 0
    return [previous, latest]

def safe_annotate(queryset, trunc_func):
    try:
        annotated = queryset.annotate(period=trunc_func('updated_at')).values('period').annotate(total_count=Count('id')).order_by('period')
        return [entry for entry in annotated if is_valid_datetime(entry['period'])]
    except ValueError as e:
        print(f"Error annotating with {trunc_func.__name__}: {e}")
        return []

@cache_page(timeout=None)  # Cache the view response forever
def fetch_consumer_summary(request):
    cache_key = 'consumer_summary_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    user_type = 'consumer'
    periods = ['daily', 'weekly', 'monthly', 'yearly']

    result = {period: {'enabled': [], 'disabled': []} for period in periods}

    trunc_functions = {
        'daily': TruncDay,
        'weekly': TruncWeek,
        'monthly': TruncMonth,
        'yearly': TruncYear
    }

    users = Users.objects.filter(type=user_type)
    disabled_users = users.filter(active=0)
    enabled_users = users.filter(active=1)

    for period, trunc_func in trunc_functions.items():
        enabled_users_data = safe_annotate(enabled_users, trunc_func)
        disabled_users_data = safe_annotate(disabled_users, trunc_func)

        enabled_users_data = calculate_latest_and_previous(enabled_users_data)
        disabled_users_data = calculate_latest_and_previous(disabled_users_data)

        if enabled_users_data:
            result[period]['enabled'] = [enabled_users_data[-1]]
        if disabled_users_data:
            result[period]['disabled'] = [disabled_users_data[-1]]

    cache.set(cache_key, result, timeout=None)  # Cache the result forever

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'consumer_summary.html', {'result': result})

@cache_page(60 * 15)
def fetch_business_summary(request):
    cache_key = 'business_summary_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    user_type = 'business'
    periods = ['daily', 'weekly', 'monthly', 'yearly']

    result = {period: {'enabled': [], 'disabled': []} for period in periods}

    trunc_functions = {
        'daily': TruncDay,
        'weekly': TruncWeek,
        'monthly': TruncMonth,
        'yearly': TruncYear
    }

    users = Users.objects.filter(type=user_type)
    disabled_users = users.filter(active=0)
    enabled_users = users.filter(active=1)

    for period, trunc_func in trunc_functions.items():
        enabled_users_data = safe_annotate(enabled_users, trunc_func)
        disabled_users_data = safe_annotate(disabled_users, trunc_func)

        enabled_users_data = calculate_latest_and_previous(enabled_users_data)
        disabled_users_data = calculate_latest_and_previous(disabled_users_data)

        if enabled_users_data:
            result[period]['enabled'] = [enabled_users_data[-1]]
        if disabled_users_data:
            result[period]['disabled'] = [disabled_users_data[-1]]

    cache.set(cache_key, result, timeout=None)  # Cache the result forever

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'business_summary.html', {'result': result})
def is_valid_datetime(dt_value):
    """Check if a datetime object is valid."""
    try:
        if dt_value and isinstance(dt_value, dt):
            return True
        return False
    except ValueError:
        return False


def get_highest_operator_organization_id(request):
    cache_key = 'highest_operator_organization_data'

    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    operator_name = request.GET.get('operator_name')

    queryset = Transactions.objects.all()

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        queryset = queryset.filter(transaction_date__range=(start_date, end_date))

    if operator_name:
        queryset = queryset.filter(operator_name=operator_name)

    operator_counts = queryset.values('operator_name').annotate(count=Count('id'))

    operator_results = []
    for operator_data in operator_counts:
        operator_name = operator_data['operator_name']
        transaction_count = operator_data['count']
        organization_id = Transactions.objects.filter(operator_name=operator_name).values_list('organization_id', flat=True).first()
        operator_result = {
            'operator_name': operator_name,
            'organization_id': organization_id,
            'transaction_count': transaction_count
        }
        operator_results.append(operator_result)

    operator_results.sort(key=lambda x: x['transaction_count'], reverse=True)

    cache.set(cache_key, {'operators': operator_results}, timeout=None)

    return JsonResponse({'operators': operator_results})

def fetch_top_customers():
    return list(
        Transactions.objects.select_related('user')
        .exclude(user__first_name='Default First Name')  # Exclude entries with "Default First Name"
        .values('user__first_name', 'user__last_name', 'user__id')
        .annotate(total_spent=Sum('invoice_total'))
        .order_by('-total_spent')[:10]
    )

def most_valuable_customers(request):
    cache_key = 'most_valuable_customers'

    top_customers = cache.get(cache_key)

    if not top_customers:
        top_customers = fetch_top_customers()
        cache.set(cache_key, top_customers, timeout=None)

    return JsonResponse({'top_customers': top_customers})


def most_sold_products(request):
    top_products = TransactionItems.objects.values('product_id') \
        .annotate(total_quantity_sold=Sum('quantity')) \
        .order_by('-total_quantity_sold')[:10]

    return JsonResponse({'top_products': list(top_products)})

def fetch_all_users_summary(request):
    result = {
        'business_count': Users.objects.filter(type='business').count(),
        'consumer_count': Users.objects.filter(type='consumer').count(),
    }

    if request.GET.get('format') == 'json':
        return JsonResponse(result)

    return render(request, 'all_users_summary.html', {'result': result})
