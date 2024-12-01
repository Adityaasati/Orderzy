import datetime
import simplejson as json
from decimal import Decimal
import time
def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M')
    order_number = current_datetime + str(pk)
    return order_number
# def generate_order_number(pk, add_timestamp=True):
#     current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M')
#     base_order_number = current_datetime + str(pk)

#     if add_timestamp:
#         unique_suffix = f"_{int(time.time())}"
#         return base_order_number + unique_suffix

#     return base_order_number
    

def order_total_by_restaurant(order, restaurant_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(restaurant_id))
    
    subtotal = 0
    service_charge = 0
    service_charge_dict = {}
    
    for key, val in data.items():
        subtotal += float(key)
        val = val.replace("'",'"')
        val = json.loads(val)
        service_charge_dict.update(val)

        for i in val:
            for j in val[i]:
                service_charge += float(val[i][j])
    grand_total = float(subtotal) + float(service_charge) 
    context = {
        'subtotal':subtotal,
        'service_charge_dict':service_charge_dict,
        'grand_total':grand_total,
        }    
    return context



class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
