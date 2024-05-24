from django.core.management.base import BaseCommand
from cubaapp.models import Users, Transactions, TransactionItems, UserPurchasedItems

class Command(BaseCommand):
    help = 'Populate the UserPurchasedItems table'

    def handle(self, *args, **options):
        users = Users.objects.all()
        UserPurchasedItems.objects.all().delete()  # Clear existing data

        for user in users:
            transactions = Transactions.objects.filter(user=user)
            if not transactions.exists():
                print(f"No transactions found for user: {user.id} - {user.first_name} {user.last_name}")
                continue

            for transaction in transactions:
                items = TransactionItems.objects.filter(transaction=transaction)
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

        print("UserPurchasedItems table has been populated.")
