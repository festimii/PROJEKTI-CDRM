from django.core.management.base import BaseCommand
from django.utils import timezone
from cubaapp.models import Users, Transactions, TransactionItems, ConsolidatedUserTransactions
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Populate the ConsolidatedUserTransactions table'

    def handle(self, *args, **options):
        users = Users.objects.all()
        ConsolidatedUserTransactions.objects.all().delete()  # Clear existing data

        for user in users:
            transactions = Transactions.objects.filter(user=user)
            if not transactions.exists():
                print(f"No transactions found for user: {user.id} - {user.first_name} {user.last_name}")
                continue

            print(f"User {user.id} - {user.first_name} {user.last_name} has the following transactions:")

            total_sales = 0
            total_transactions = transactions.count()
            total_items = 0
            total_discount = 0

            for transaction in transactions:
                print(f"  Transaction ID: {transaction.id}, Invoice Total: {transaction.invoice_total}")
                total_sales += transaction.invoice_total
                total_discount += transaction.invoice_total_before_discount - transaction.invoice_total
                
                items = TransactionItems.objects.filter(transaction=transaction)
                total_items += items.count()

                for item in items:
                    print(f"    Item ID: {item.id}, Amount: {item.amount}, Base Price: {item.base_price}")

            average_sales = total_sales / total_transactions if total_transactions > 0 else 0
            last_transaction_date = transactions.latest('created_at').created_at if transactions.exists() else timezone.now()

            ConsolidatedUserTransactions.objects.create(
                user=user,
                total_sales=total_sales,
                average_sales=average_sales,
                total_transactions=total_transactions,
                total_items=total_items,
                total_discount=total_discount,
                last_transaction_date=last_transaction_date
            )

        print("ConsolidatedUserTransactions table has been populated.")
