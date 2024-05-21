
from django.db.models.functions import TruncDay, TruncHour, TruncMonth
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum ,Count
from .models import Orders
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

    # Aggregation by status
    status_summary = orders.values('status').annotate(count=Count('id'), total_sum=Sum('total'))

    # Total summary for all time
    total_summary = orders.aggregate(total_count=Count('id'), total_sum=Sum('total'))

    # Combine results into a dictionary
    result = {
        'status_summary': list(status_summary),
        'total_summary': total_summary
    }

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'order_status_summary.html', {'result': result})