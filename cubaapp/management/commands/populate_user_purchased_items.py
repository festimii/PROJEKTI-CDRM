from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor
from cubaapp.models import Users, Transactions, TransactionItems, UserPurchasedItems
from django.db import transaction

class Command(BaseCommand):
    help = 'Populate the UserPurchasedItems table'

    def handle(self, *args, **options):
        users = Users.objects.all()
        UserPurchasedItems.objects.all().delete()  # Clear existing data

        def process_user(user):
            transactions = Transactions.objects.filter(user=user)
            if not transactions.exists():
                print(f"No transactions found for user: {user.id} - {user.first_name} {user.last_name}")
                return

            for transaction in transactions:
                items = TransactionItems.objects.filter(transaction=transaction)
                with transaction.atomic():
                    for item in items:
                        print(f"User {user.id} bought Item {item.id} in Transaction {transaction.id}")
                        UserPurchasedItems.objects.create(
                            user=user,
                            transaction=transaction,
                            item=item,
                            amount=item.amount,
                            base_price=item.base_price,
                            discount_price=item.discount_price,
                            quantity=item.quantity
                        )

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(process_user, users)

        print("UserPurchasedItems table has been populated.")
