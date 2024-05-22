# management/commands/populate_consolidated_user_transactions.py

from django.core.management.base import BaseCommand
from cubaapp.models import Users, Transactions, TransactionItems, ConsolidatedUserTransactions
from django.db.models import Sum, Avg, Count, F, Max

class Command(BaseCommand):
    help = 'Populate the consolidated user transactions table'

    def handle(self, *args, **kwargs):
        ConsolidatedUserTransactions.objects.all().delete()  # Clear existing data

        users = Users.objects.all()

        for user in users:
            transactions = Transactions.objects.filter(user_id=user.id)
            total_sales = transactions.aggregate(Sum('invoice_total'))['invoice_total__sum'] or 0
            total_transactions = transactions.count()
            total_items = TransactionItems.objects.filter(transaction_id__in=transactions.values_list('id', flat=True)).count()
            total_discount = transactions.aggregate(Sum('invoice_total_before_discount'))['invoice_total_before_discount__sum'] - total_sales or 0
            last_transaction_date = transactions.aggregate(last_date=Max('created_at'))['last_date']
            average_sales = total_sales / total_transactions if total_transactions > 0 else 0

            ConsolidatedUserTransactions.objects.create(
                user=user,
                total_sales=total_sales,
                average_sales=average_sales,
                total_transactions=total_transactions,
                total_items=total_items,
                total_discount=total_discount,
                last_transaction_date=last_transaction_date
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated consolidated user transactions table'))
