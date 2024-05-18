
from django.db.models.functions import TruncDay, TruncHour, TruncMonth
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
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
    hourly_orders = orders.annotate(period=TruncHour('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total'))

    # Aggregation by day
    daily_orders = orders.annotate(period=TruncDay('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total'))

    # Aggregation by month
    monthly_orders = orders.annotate(period=TruncMonth('created_at')).values('order_type', 'period').annotate(total_sum=Sum('total'))

    # Combine results into a dictionary
    result = {
        'hourly': list(hourly_orders),
        'daily': list(daily_orders),
        'monthly': list(monthly_orders)
    }

    if request.GET.get('format') == 'json':
        return JsonResponse(result, safe=False)

    return render(request, 'order_summaries.html', {'result': result})

