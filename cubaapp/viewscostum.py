import datetime

from django.db.models.functions import TruncDay, TruncHour, TruncWeek, TruncMonth, TruncYear
from django.middleware import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum ,Count ,Max
from .models import Orders, Users, Transactions
from django.core.cache import cache
from django.contrib.auth.decorators import login_required   #@login_required ME I VENDOS MA VON ME I BA PROTECT

def fetch_order_summaries(request):
    orders = Orders.objects.all()
    order_summaries = orders.values('order_type').annotate(total_sum=Sum('total'))

    if request.GET.get('format') == 'json':
        return JsonResponse(list(order_summaries), safe=False)

    return render(request, 'order_summaries.html', {'order_summaries': order_summaries})


def fetch_order_summaries_total(request):
    orders = Orders.objects.all()

    # Aggregation by hour
    hourly_orders = orders.annotate(period=TruncHour('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')

    # Aggregation by day
    daily_orders = orders.annotate(period=TruncDay('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')

    # Aggregation by month
    monthly_orders = orders.annotate(period=TruncMonth('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total')).order_by('period')

    # Prepare the results in a clear structure
    def prepare_data(queryset, period_key):
        data = {}
        for item in queryset:
            period = item[period_key].strftime('%Y-%m-%dT%H:%M:%SZ')
            order_type = item['order_type']
            total_sum = round(float(item['total_sum']), 0)  # Round the total sum to 2 decimal places
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
        """
        Aggregates order data by truncating the date field using the provided trunc_function.
        If filter_recent is True, only the most recent period data is returned.
        Returns a list of dictionaries containing the status, period, count, and total_sum.
        """
        aggregated_data = orders.annotate(period=trunc_function('created_at')).values('status', 'period').annotate(
            count=Count('id'), total_sum=Sum('total'))

        if filter_recent:
            # Filter to keep only the most recent period
            most_recent_period = aggregated_data.aggregate(most_recent=Max('period'))['most_recent']
            aggregated_data = aggregated_data.filter(period=most_recent_period)

        return list(aggregated_data)

    def calculate_profit_percentage(data):
        """
        Calculates the profit percentage as the ratio of completed orders to total orders.
        """
        completed_count = sum(item['count'] for item in data if item['status'] == 'completed')
        other_count = sum(item['count'] for item in data if item['status'] != 'completed')
        profit_percentage = (completed_count / (completed_count + other_count)) * 100 if (
                                                                                                     completed_count + other_count) > 0 else 0
        return profit_percentage

    # Get aggregated data for different time periods
    daily_orders = get_aggregated_data(TruncDay, filter_recent=True)
    weekly_orders = get_aggregated_data(TruncWeek)
    monthly_orders = get_aggregated_data(TruncMonth)
    yearly_orders = get_aggregated_data(TruncYear)

    # Calculate profit percentages for each time period
    daily_profit_percentage = calculate_profit_percentage(daily_orders)
    weekly_profit_percentage = calculate_profit_percentage(weekly_orders)
    monthly_profit_percentage = calculate_profit_percentage(monthly_orders)
    yearly_profit_percentage = calculate_profit_percentage(yearly_orders)

    # Prepare the final result dictionary
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

    # Return the result as JSON if requested
    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    # Otherwise, render the result in an HTML template
    return render(request, 'order_status_summary.html', {'result': result})
def fetch_new_users_summary(request):
    user_types = Users.objects.values_list('type', flat=True).distinct()

    result = {
        'daily': {},
        'weekly': {},
        'monthly': {},
        'yearly': {},
    }

    for user_type in user_types:
        users = Users.objects.filter(type=user_type)

        # Aggregation by day
        daily_users = users.annotate(period=TruncDay('created_at')).values('period').annotate(total_count=Count('id')).order_by('period')
        daily_data = list(daily_users)
        for i in range(1, len(daily_data)):
            current_count = daily_data[i]['total_count']
            previous_count = daily_data[i-1]['total_count']
            daily_data[i]['percentage_difference'] = ((current_count - previous_count) / previous_count) * 100 if previous_count != 0 else None
        result['daily'][user_type] = daily_data

        # Aggregation by week
        weekly_users = users.annotate(period=TruncWeek('created_at')).values('period').annotate(total_count=Count('id')).order_by('period')
        weekly_data = list(weekly_users)
        for i in range(1, len(weekly_data)):
            current_count = weekly_data[i]['total_count']
            previous_count = weekly_data[i-1]['total_count']
            weekly_data[i]['percentage_difference'] = ((current_count - previous_count) / previous_count) * 100 if previous_count != 0 else None
        result['weekly'][user_type] = weekly_data

        # Aggregation by month
        monthly_users = users.annotate(period=TruncMonth('created_at')).values('period').annotate(total_count=Count('id')).order_by('period')
        monthly_data = list(monthly_users)
        for i in range(1, len(monthly_data)):
            current_count = monthly_data[i]['total_count']
            previous_count = monthly_data[i-1]['total_count']
            monthly_data[i]['percentage_difference'] = ((current_count - previous_count) / previous_count) * 100 if previous_count != 0 else None
        result['monthly'][user_type] = monthly_data

        # Aggregation by year
        yearly_users = users.annotate(period=TruncYear('created_at')).values('period').annotate(total_count=Count('id')).order_by('period')
        yearly_data = list(yearly_users)
        for i in range(1, len(yearly_data)):
            current_count = yearly_data[i]['total_count']
            previous_count = yearly_data[i-1]['total_count']
            yearly_data[i]['percentage_difference'] = ((current_count - previous_count) / previous_count) * 100 if previous_count != 0 else None
        result['yearly'][user_type] = yearly_data

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'new_users_summary.html', {'result': result})

def get_highest_operator_organization_id(request):
    cache_key = 'highest_operator_organization_data'

    # Check if the data is already cached
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    # Get filter parameters from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    operator_name = request.GET.get('operator_name')

    # Start with the base queryset
    queryset = Transactions.objects.all()

    # Apply filters to queryset
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        queryset = queryset.filter(transaction_date__range=(start_date, end_date))

    if operator_name:
        queryset = queryset.filter(operator_name=operator_name)

    # Count the number of transactions per operator_name
    operator_counts = queryset.values('operator_name').annotate(count=Count('id'))

    # Initialize a list to store results for all operators
    operator_results = []

    # Iterate through each operator and retrieve organization ID and transaction count
    for operator_data in operator_counts:
        operator_name = operator_data['operator_name']
        transaction_count = operator_data['count']
        organization_id = Transactions.objects.filter(
            operator_name=operator_name).values_list('organization_id', flat=True).first()
        operator_result = {
            'operator_name': operator_name,
            'organization_id': organization_id,
            'transaction_count': transaction_count
        }
        operator_results.append(operator_result)

    # Sort operators from highest to lowest based on transaction count
    operator_results.sort(key=lambda x: x['transaction_count'], reverse=True)

    # Cache the response
    cache.set(cache_key, {'operators': operator_results}, timeout=None)  # Set timeout=None for indefinite caching

    return JsonResponse({'operators': operator_results})
def most_valuable_customers(request):
    # Aggregate transaction amounts for each user
    top_customers = Transactions.objects.values('user__first_name', 'user__last_name', 'user__id') \
        .annotate(total_spent=Sum('invoice_total')) \
        .order_by('-total_spent')[:10]  # Limit to top 10 customers

    # Convert the QuerySet to a list of dictionaries
    top_customers_list = list(top_customers)

    # Return the data as a JSON response
    return JsonResponse({'top_customers': top_customers_list})