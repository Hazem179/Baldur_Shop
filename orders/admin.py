import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


# def order_pdf(obj):
#     url = reverse('orders:admin_order_pdf', args=[obj.id])
#     return mark_safe(f'<a href="{url}">PDF</a>')


# order_pdf.short_description = 'Invoice PDF'

'''
This is a function that takes an Order object as an argument and returns an HTML 
link for the admin_order_detail URL
'''


def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = 'attachment; filename={opts.verbose_name}.csv'

    '''
    create an instance of HttpResponse, specifying the text/csv content
    type, to tell the browser that the response has to be treated as a CSV file. You
    also add a Content-Disposition header to indicate that the HTTP response
    contains an attached file.
    '''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)  # write to the response object
    '''
    You get the model fields dynamically using the get_fields() method
    of the model _meta options. You exclude many-to-many and one-to-many
    relationships

    '''
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])  # write header row including field names
    '''
    You iterate over the given QuerySet and write a row for each object returned
    by the QuerySet. You take care of formatting datetime objects because the
    output value for CSV has to be a string
    '''
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'  # customize display name


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid', 'created', 'updated', order_detail]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
