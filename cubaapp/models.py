# -*- coding: utf-8 -*-
from django.db import models  # type: ignore

class ActivityLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    log_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    subject_type = models.CharField(max_length=255, blank=True, null=True)
    event = models.CharField(max_length=255, blank=True, null=True)
    subject_id = models.PositiveBigIntegerField(blank=True, null=True)
    causer_type = models.CharField(max_length=255, blank=True, null=True)
    causer_id = models.PositiveBigIntegerField(blank=True, null=True)
    properties = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    batch_uuid = models.CharField(max_length=36, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'activity_log'


class AppOpens(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField()
    device_id = models.CharField(max_length=255)
    app_opens = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'app_opens'

class Brands(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'brands'


class BucketLists(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField()
    product_id = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    organization_id = models.PositiveBigIntegerField()

    class Meta:
        db_table = 'bucket_lists'


class BusinessTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'business_types'


class Categories(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=255)
    type = models.CharField(unique=True, max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    level = models.PositiveIntegerField()
    field_lft = models.PositiveIntegerField(db_column='_lft')  # Field renamed because it started with '_'.
    field_rgt = models.PositiveIntegerField(db_column='_rgt')  # Field renamed because it started with '_'.
    parent_id = models.PositiveIntegerField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'categories'


class Cities(models.Model):
    id = models.BigAutoField(primary_key=True)
    city_name = models.CharField(max_length=255)
    city_zip = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    organization_id = models.IntegerField(blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'cities'


class ControllerHistories(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_id = models.PositiveBigIntegerField()
    user_id = models.PositiveBigIntegerField()
    organization_id = models.PositiveBigIntegerField()
    payload = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'controller_histories'


class Coupons(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=5)
    type = models.CharField(max_length=7, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    user_id = models.PositiveBigIntegerField()
    created_by = models.PositiveBigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    unique_id = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'coupons'


class CouponsAndProductPivot(models.Model):
    coupon_id = models.PositiveBigIntegerField(primary_key=True)
    product_id = models.PositiveBigIntegerField()

    class Meta:
        db_table = 'coupons_and_product_pivot'
        unique_together = (('coupon_id', 'product_id'),)


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    complete = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        db_table = 'task'


class CustomerSatisfactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField()
    feedback_question_id = models.PositiveBigIntegerField()
    rating = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    order_id = models.PositiveBigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'customer_satisfactions'


class DeactivateReasons(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField()
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'deactivate_reasons'


class Devices(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.TextField()
    user_id = models.PositiveBigIntegerField()
    user_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'devices'


class DiscountGroupUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    discount_group_id = models.PositiveBigIntegerField()
    user_id = models.PositiveBigIntegerField()

    class Meta:
        db_table = 'discount_group_user'


class DiscountGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'discount_groups'


class Discounts(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_id = models.PositiveBigIntegerField(blank=True, null=True)
    user_id = models.PositiveBigIntegerField(blank=True, null=True)
    active = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    discount_1_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_2_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_3_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    organization_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'discounts'



class CustomDjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        db_table = 'custom_django_content_type'
        unique_together = (('app_label', 'model'),)


class CustomDjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        db_table = 'custom_django_migrations'


class CustomDjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        db_table = 'custom_django_session'


class FeedbackQuestions(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=255)

    class Meta:
        db_table = 'feedback_questions'


class FirebaseNotifications(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    delay_until = models.DateTimeField(blank=True, null=True)
    sent = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    data = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'firebase_notifications'


class Flyers(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=7, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    schedule = models.IntegerField()
    track_opens = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'flyers'


class InvoiceTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'invoice_types'


class LoyaltyAddresses(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField()
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    organization_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'loyalty_addresses'


class Notifications(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    type = models.CharField(max_length=255)
    notifiable_type = models.CharField(max_length=255)
    notifiable_id = models.PositiveBigIntegerField()
    data = models.TextField()
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    firebase_notification_id = models.PositiveBigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'notifications'


class OrderControlleds(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_id = models.PositiveBigIntegerField()
    user_id = models.PositiveBigIntegerField()
    organization_id = models.PositiveBigIntegerField()
    payload = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'order_controlleds'


class OrderLines(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_id = models.PositiveBigIntegerField()
    product_id = models.PositiveBigIntegerField()
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=5)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=5)
    discount_1_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_1 = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    discount_2_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_2 = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    discount_3_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_3 = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    vat = models.DecimalField(max_digits=10, decimal_places=5)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'order_lines'


class Orders(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=5)
    discount = models.DecimalField(max_digits=10, decimal_places=5)
    vat = models.DecimalField(max_digits=10, decimal_places=5)
    subtotal = models.DecimalField(max_digits=10, decimal_places=5)
    parent_id = models.PositiveBigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    transport_type_id = models.PositiveBigIntegerField(blank=True, null=True)
    payment_method_id = models.PositiveBigIntegerField(blank=True, null=True)
    invoice_type_id = models.PositiveBigIntegerField(blank=True, null=True)
    address_first_name = models.CharField(max_length=255, blank=True, null=True)
    address_last_name = models.CharField(max_length=255, blank=True, null=True)
    address_first_line = models.CharField(max_length=255, blank=True, null=True)
    address_second_line = models.CharField(max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(max_length=255, blank=True, null=True)
    address_city = models.CharField(max_length=255, blank=True, null=True)
    address_country = models.CharField(max_length=255, blank=True, null=True)
    address_email = models.CharField(max_length=255, blank=True, null=True)
    address_phone_number = models.CharField(max_length=255, blank=True, null=True)
    sent_status = models.IntegerField()
    cfma_no = models.CharField(max_length=255, blank=True, null=True)
    web_no = models.CharField(max_length=255, blank=True, null=True)
    weight = models.CharField(max_length=255, blank=True, null=True)
    boxes = models.CharField(max_length=255, blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    payload = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    time_slot = models.CharField(max_length=255, blank=True, null=True)
    order_type = models.CharField(max_length=7)
    date_time_slot = models.CharField(max_length=255, blank=True, null=True)
    date_slot = models.CharField(max_length=255, blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    reject_until = models.DateTimeField(blank=True, null=True)
    extra_phone_number = models.CharField(max_length=255, blank=True, null=True)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=5)
    timeslot_start_date = models.DateTimeField(blank=True, null=True)
    timeslot_end_date = models.DateTimeField(blank=True, null=True)
    timeslot_id = models.IntegerField(blank=True, null=True)
    previous_total = models.DecimalField(max_digits=10, decimal_places=5)
    balance = models.DecimalField(max_digits=10, decimal_places=5)
    organization_id = models.PositiveIntegerField(blank=True, null=True)
    transferred_to = models.CharField(max_length=255, blank=True, null=True)
    should_notify = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'orders'


class OrganizationStocks(models.Model):
    id = models.BigAutoField(primary_key=True)
    organization_id = models.BigIntegerField()
    product_id = models.BigIntegerField()
    stock = models.DecimalField(max_digits=10, decimal_places=5)
    min_stock = models.DecimalField(max_digits=10, decimal_places=5)
    base_price = models.DecimalField(max_digits=10, decimal_places=5)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    max_stock = models.DecimalField(max_digits=8, decimal_places=2)
    stock_percentage = models.IntegerField()
    max_order_quantity = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = 'organization_stocks'
        unique_together = (('product_id', 'organization_id'),)


class PasswordResets(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'password_resets'


class PaymentMethods(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    key = models.TextField(blank=True, null=True)
    show_on = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payment_methods'


class Products(models.Model):
    id = models.BigAutoField(primary_key=True)
    category_id = models.PositiveBigIntegerField(blank=True, null=True)
    brand_id = models.PositiveBigIntegerField(blank=True, null=True)
    code = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    barcode = models.CharField(max_length=255)
    unit_of_measure = models.CharField(max_length=10)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=5)
    stock = models.DecimalField(max_digits=10, decimal_places=5)
    stock_percentage = models.IntegerField(blank=True, null=True)
    max_stock = models.DecimalField(max_digits=8, decimal_places=2)
    max_order_quantity = models.BigIntegerField(blank=True, null=True)
    packing_size = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    commercial_packing = models.DecimalField(max_digits=8, decimal_places=2)
    incremental = models.DecimalField(max_digits=5, decimal_places=2)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.IntegerField()
    priority = models.PositiveIntegerField()
    private_label = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    flagged_stock = models.IntegerField()
    reserved_stock = models.DecimalField(max_digits=10, decimal_places=5)
    classification = models.CharField(max_length=255, blank=True, null=True)
    int_code = models.BigIntegerField(unique=True, blank=True, null=True)
    search_field = models.TextField(blank=True, null=True)
    emoji_flag = models.CharField(max_length=255, blank=True, null=True)
    origin = models.CharField(max_length=255, blank=True, null=True)
    b2c_increment = models.DecimalField(max_digits=5, decimal_places=2)
    b2c_priority = models.PositiveIntegerField()

    class Meta:
        db_table = 'products'


class ProgramMenus(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    category_ids = models.CharField(max_length=255)

    class Meta:
        db_table = 'program_menus'


class RcbResponses(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=7, blank=True, null=True)
    response = models.TextField(db_collation='utf8mb4_bin', blank=True, null=True)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rcb_responses'


class Roles(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    guard_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'roles'
        unique_together = (('name', 'guard_name'),)


class TempUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    active = models.IntegerField()
    phone_number = models.CharField(unique=True, max_length=255, blank=True, null=True)
    username = models.CharField(unique=True, max_length=255, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    address_first_line = models.CharField(max_length=255, blank=True, null=True)
    address_second_line = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    classif_3 = models.CharField(max_length=255, blank=True, null=True)
    classif_4 = models.CharField(max_length=255, blank=True, null=True)
    id_number = models.CharField(max_length=255, blank=True, null=True)
    fiscal_no = models.CharField(max_length=255, blank=True, null=True)
    business_no = models.CharField(max_length=255, blank=True, null=True)
    vat_no = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_no = models.CharField(max_length=255, blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    commercial_name = models.CharField(max_length=255, blank=True, null=True)
    sales_agent = models.CharField(max_length=255, blank=True, null=True)
    business_type_id = models.PositiveBigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'temp_users'


class TimeSlots(models.Model):
    id = models.BigAutoField(primary_key=True)
    organization_id = models.IntegerField()
    start_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'time_slots'


class TransactionItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    base_price = models.DecimalField(max_digits=20, decimal_places=2)
    discount_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    coupon_applied = models.PositiveBigIntegerField(blank=True, null=True)
    product_id = models.PositiveBigIntegerField(blank=True, null=True)
    transaction_id = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        db_table = 'transaction_items'


class Transactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    post_id = models.CharField(max_length=255, blank=True, null=True)
    coupons_applied = models.CharField(max_length=255, blank=True, null=True)
    invoice_total = models.DecimalField(max_digits=20, decimal_places=2)
    invoice_total_before_discount = models.DecimalField(max_digits=20, decimal_places=2)
    user_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    organization_id = models.IntegerField()
    group_of_arka = models.IntegerField(blank=True, null=True)
    number_of_arka = models.IntegerField(blank=True, null=True)
    operator_id = models.IntegerField(blank=True, null=True)
    transaction_id = models.IntegerField()
    operator_name = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'transactions'

class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    password = models.CharField(max_length=255)
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    active = models.IntegerField()
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    address_first_line = models.CharField(max_length=255, blank=True, null=True)
    address_second_line = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    classif_3 = models.CharField(max_length=255, blank=True, null=True)
    classif_4 = models.CharField(max_length=255, blank=True, null=True)
    id_number = models.CharField(max_length=255, blank=True, null=True)
    fiscal_no = models.CharField(max_length=255, blank=True, null=True)
    business_no = models.CharField(max_length=255, blank=True, null=True)
    vat_no = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_no = models.CharField(max_length=255, blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    base_discount = models.CharField(max_length=255, blank=True, null=True)
    barcode_id = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    blocked_at = models.DateTimeField(blank=True, null=True)
    roulette_plays = models.IntegerField()
    roulette_attempts_left = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    sales_agent = models.CharField(max_length=255, blank=True, null=True)
    commercial_name = models.CharField(max_length=255, blank=True, null=True)
    group_type_id = models.PositiveBigIntegerField()
    business_type_id = models.PositiveBigIntegerField(blank=True, null=True)
    int_code = models.BigIntegerField(blank=True, null=True)
    feedback_timer = models.DateTimeField()
    show_survey = models.IntegerField()

    class Meta:
        db_table = 'users'

class TransportTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        db_table = 'transport_types'




class VivaLocations(models.Model):
    id = models.BigAutoField(primary_key=True)
    store_number = models.IntegerField()
    name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    lng = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    work_hours = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'viva_locations'


class VivaOrganizations(models.Model):
    id = models.BigAutoField(primary_key=True)
    organization_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    like_per_like = models.IntegerField()

    class Meta:
        db_table = 'viva_organizations'


class WishlistItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    wishlist_id = models.PositiveBigIntegerField()
    product_id = models.PositiveBigIntegerField()
    quantity = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'wishlist_items'


class Wishlists(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'wishlists'

class ConsolidatedUserTransactions(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    total_sales = models.DecimalField(max_digits=20, decimal_places=2)
    average_sales = models.DecimalField(max_digits=20, decimal_places=2)
    total_transactions = models.IntegerField()
    total_items = models.IntegerField()
    total_discount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    last_transaction_date = models.DateTimeField()

    class Meta:
        db_table = 'consolidated_user_transactions'