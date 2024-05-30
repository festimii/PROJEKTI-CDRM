# views.py
from django.views.decorators.cache import cache_page
from django.db.models.functions import TruncDay, TruncHour, TruncWeek, TruncMonth, TruncYear
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Max , DecimalField , Avg , ExpressionWrapper, DurationField,F
from .models import Orders, Users, Transactions, TransactionItems
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from datetime import datetime as dt
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncQuarter
from django.utils import timezone
import logging
from decimal import Decimal

# Define a logger
logger = logging.getLogger(__name__)
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
def transaction_stats_api(request):
    # Get overall transaction sum for all users
    overall_sum = Transactions.objects.aggregate(overall_sum=Sum('invoice_total'))['overall_sum'] or 0

    # Get transaction sum for business users
    business_sum = Transactions.objects.filter(user__type='business').aggregate(business_sum=Sum('invoice_total'))['business_sum'] or 0

    # Get average basket price for consumers
    consumer_avg_price = Transactions.objects.filter(user__type='consumer').aggregate(consumer_avg_price=Avg('invoice_total'))['consumer_avg_price'] or 0

    # Get average basket price for business users
    business_avg_price = Transactions.objects.filter(user__type='business').aggregate(business_avg_price=Avg('invoice_total'))['business_avg_price'] or 0

    # Convert results to Decimal
    overall_sum = Decimal(overall_sum)
    business_sum = Decimal(business_sum)
    consumer_avg_price = Decimal(consumer_avg_price)
    business_avg_price = Decimal(business_avg_price)

    # Prepare the response data
    response_data = {
        'overall_transaction_sum': overall_sum,
        'business_transaction_sum': business_sum,
        'consumer_average_basket_price': consumer_avg_price,
        'business_average_basket_price': business_avg_price,
    }

    # Return the data as JSON response
    return JsonResponse(response_data)

from django.http import JsonResponse
from django.db.models import Min, Max
from .models import Users


def calculate_customer_retention_rate(period_start, period_end, time_filter):
    log_messages = []

    # Helper function to log messages
    def log(message):
        log_messages.append(message)
        logger.info(message)

    log(f"Calculating retention rate for {time_filter} period from {period_start} to {period_end}")

    # Determine the time filter to use
    if time_filter == 'month':
        trunc_function = TruncMonth('created_at')
    elif time_filter == 'quarter':
        trunc_function = TruncQuarter('created_at')
    elif time_filter == 'year':
        trunc_function = TruncYear('created_at')
    else:
        raise ValueError("Invalid time filter. Use 'month', 'quarter', or 'year'.")

    # Find the earliest and latest timestamps in the Users table for the given period
    queryset = Users.objects.filter(created_at__range=(period_start, period_end)).annotate(period=trunc_function)
    period_info = queryset.aggregate(Min('created_at'), Max('created_at'))
    earliest_period = period_info['created_at__min']
    latest_period = period_info['created_at__max']

    log(f"Earliest timestamp: {earliest_period}, Latest timestamp: {latest_period}")

    # If there are no records in the table for the given period, return retention rate of 0
    if not earliest_period or not latest_period:
        message = "No records found for the period"
        log(message)
        return 0, None, 0, 0, 0, message  # Include a message indicating no records found

    # Calculate the number of unique customers at the start and end of the period
    customers_at_start = Users.objects.filter(created_at__lte=earliest_period).values('id').distinct().count()
    customers_at_end = Users.objects.filter(created_at__lte=latest_period).values('id').distinct().count()
    new_customers = Users.objects.filter(created_at__range=(period_start, period_end)).values('id').distinct().count()

    log(f"Unique customers at start of period: {customers_at_start}, Unique customers at end of period: {customers_at_end}")
    log(f"New customers during the period: {new_customers}")


    # Calculate retention rate using the given formula
    retention_rate = ((customers_at_end - new_customers) / customers_at_start) * 100
    formatted_retention_rate = f"{retention_rate:.1f}%"  # Format the retention rate to one decimal place
    log(f"Retention rate calculated: {formatted_retention_rate}")

    return formatted_retention_rate, earliest_period, customers_at_start, customers_at_end, new_customers, log_messages


def retention_rate_view(request):
    start_year = 2021
    end_year = 2024
    result = {}

    for year in range(start_year, end_year + 1):
        year_result = {}
        for time_filter in ['year', 'quarter', 'month']:
            if time_filter == 'month':
                for month in range(1, 13):
                    # Create an aware datetime object for the start of the month
                    period_start = timezone.make_aware(timezone.datetime(year, month, 1))
                    # Create an aware datetime object for the end of the month
                    if month == 12:
                        period_end = timezone.make_aware(timezone.datetime(year, month, 31, 23, 59, 59))
                    else:
                        period_end = timezone.make_aware(
                            timezone.datetime(year, month + 1, 1) - timezone.timedelta(seconds=1))
                    retention_rate, earliest_period, customers_at_start, customers_at_end, new_customers, log_messages = calculate_customer_retention_rate(
                        period_start, period_end, time_filter)

                    year_result[f"{time_filter}-{month}"] = {
                        'customer_retention_rate': retention_rate,
                        'earliest_period': earliest_period.strftime('%Y-%m-%d') if earliest_period else None,
                        'customers_at_start': customers_at_start,
                        'customers_at_end': customers_at_end,
                        'new_customers': new_customers,
                        'log_messages': log_messages  # Include log messages in the response
                    }
            else:
                # Create an aware datetime object for the start of the period
                period_start = timezone.make_aware(timezone.datetime(year, 1, 1))
                # Create an aware datetime object for the end of the period
                period_end = timezone.make_aware(timezone.datetime(year, 12, 31, 23, 59, 59))
                retention_rate, earliest_period, customers_at_start, customers_at_end, new_customers, log_messages = calculate_customer_retention_rate(
                    period_start, period_end, time_filter)

                year_result[time_filter] = {
                    'customer_retention_rate': retention_rate,
                    'earliest_period': earliest_period.strftime('%Y-%m-%d') if earliest_period else None,
                    'customers_at_start': customers_at_start,
                    'customers_at_end': customers_at_end,
                    'new_customers': new_customers,
                    'log_messages': log_messages  # Include log messages in the response
                }
        result[year] = year_result

    return JsonResponse(result)


def calculate_repeat_purchase_rate():
    # Aggregate the number of transactions for each user
    user_transaction_counts = Transactions.objects.values('user').annotate(transaction_count=Count('id'))

    # Number of customers who made more than one purchase
    customers_with_multiple_purchases = user_transaction_counts.filter(transaction_count__gt=1).count()

    # Total number of unique customers
    total_customers = user_transaction_counts.count()

    # Calculate Repeat Purchase Rate
    repeat_purchase_rate = (customers_with_multiple_purchases / total_customers) * 100 if total_customers > 0 else 0

    return repeat_purchase_rate, customers_with_multiple_purchases, total_customers


def repeat_purchase_rate_view(request):
    # Calculate the Repeat Purchase Rate
    repeat_purchase_rate, customers_with_multiple_purchases, total_customers = calculate_repeat_purchase_rate()

    # Create a JSON response
    data = {
        'repeat_purchase_rate': f"{repeat_purchase_rate:.2f}%",
        'customers_with_multiple_purchases': customers_with_multiple_purchases,
        'total_customers': total_customers,
    }
    return JsonResponse(data)


def calculate_customer_lifetime_value():
    # Calculate total revenue
    total_revenue = Transactions.objects.aggregate(total_revenue=Sum('invoice_total'))['total_revenue'] or Decimal(0)

    # Calculate total number of transactions
    total_transactions = Transactions.objects.count()

    # Calculate the number of unique customers
    total_customers = Transactions.objects.values('user').distinct().count()

    # Calculate Average Purchase Value (APV)
    average_purchase_value = total_revenue / Decimal(total_transactions) if total_transactions > 0 else Decimal(0)

    # Calculate Purchase Frequency (PF)
    purchase_frequency = Decimal(total_transactions) / Decimal(total_customers) if total_customers > 0 else Decimal(0)

    # Calculate Customer Lifespan (CL)
    # Calculate the average lifespan of a customer
    user_lifespans = Transactions.objects.values('user').annotate(
        first_purchase=Min('created_at'),
        last_purchase=Max('created_at')
    ).annotate(
        lifespan=ExpressionWrapper(F('last_purchase') - F('first_purchase'), output_field=DurationField())
    ).aggregate(average_lifespan=Avg('lifespan'))['average_lifespan'] or 0

    average_customer_lifespan = Decimal(
        user_lifespans.total_seconds() / (365 * 24 * 3600)) if user_lifespans else Decimal(0)

    # Calculate Customer Lifetime Value (CLV)
    customer_lifetime_value = average_purchase_value * purchase_frequency * average_customer_lifespan

    return customer_lifetime_value, average_purchase_value, purchase_frequency, average_customer_lifespan


def customer_lifetime_value_view(request):
    # Calculate the Customer Lifetime Value (CLV)
    customer_lifetime_value, average_purchase_value, purchase_frequency, average_customer_lifespan = calculate_customer_lifetime_value()

    # Create a JSON response
    data = {
        'customer_lifetime_value': f"${customer_lifetime_value:.2f}",
        'average_purchase_value': f"${average_purchase_value:.2f}",
        'purchase_frequency': f"{purchase_frequency:.2f}",
        'customer_lifespan': f"{average_customer_lifespan:.2f} years",
    }
    return JsonResponse(data)