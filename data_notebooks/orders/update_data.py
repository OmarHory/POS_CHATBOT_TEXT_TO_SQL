#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import time
from datetime import date
pd.set_option('display.max_columns', None)


# In[2]:


def foodics_api(method, payload={}):

  url = f"https://api.foodics.com/v5/{method}"
  token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImM1ZmIxMjE2MDk0YTEyODQ3ZTkyMTBhNDAxNjUzNDE4ZDI2ZWEyZGY1YTMzYzQ2ZDcyMzM3ZDhlMTc2ZDQwMmJkNjVkNTFiNmQ4YThlYTE3In0.eyJhdWQiOiI5OTNjNWM1Ni05YjkyLTRhYmMtOWUwNy05YjdjMGNiMzQ0NzUiLCJqdGkiOiJjNWZiMTIxNjA5NGExMjg0N2U5MjEwYTQwMTY1MzQxOGQyNmVhMmRmNWEzM2M0NmQ3MjMzN2Q4ZTE3NmQ0MDJiZDY1ZDUxYjZkOGE4ZWExNyIsImlhdCI6MTY4NDk0MDU3OSwibmJmIjoxNjg0OTQwNTc5LCJleHAiOjE4NDI3OTMzNzksInN1YiI6Ijk3NWIzY2U3LTIyMTItNDZjMS1hMjg2LTA4NjU4YjQ1NWRiNSIsInNjb3BlcyI6W10sImJ1c2luZXNzIjoiOTc1YjNjZTctMzllZC00MGIxLWJmODItYmZhZjRkYmY0YTdlIiwicmVmZXJlbmNlIjoiNjMyMzc4In0.aMxoYSkN1NFxvEgfd0itmmvENYt73A7gky5AIup7rgRIe8uY5T9sJPVzOj3kJfFcCadNwBjB-h6fKMKAc1QmcJY1G5j8Va9edCUYXmUNl1hMh2OydMH87AFJ7DSqK2Wic-spanliG7tsRdLihN9aRl4676TriA8Bd93iV9J4ZPgfmhdhytE5VMNqVDDTjX2CRNo2HzJQwEQFzZjZCZwt36jSjt_zk36YGNx2Fd1zk2ryZvfDsnnSZB4G8DNJPNmd9gAfvoSW3RvYn46qXm3ZRO4dZoUaixO7Fqb1-p0_UHHTDKIHV50i4Wpc1hNCjdRGI6g1dVG8cl-sYIKa8cNKHn_PzBRy6Q81XIEMrnSLQUHxLlqDms4f4YDIAUVSfem0gKtR2UMIeS8X1FtJkgTvbXTipvoXDMilWWo0sNAJ3wSQ_75b0aPd_p_6Hbydh2-2gJilLZ6tsDbkjsx5FjUp9LNDTuWof5U-5x-1glQAixoQPcqz-LMB6pFFPq-kaecmSPOhKM24MMg2YFBTyzARjah36lZ8YtJCZ0A4N87pDsOzTI8HGyBH19Z-MtFuQpoAVoBgDG9kApCgeEjnIuJtmrEWdcyWPx0WjXqm7qGot-fRQ71IhDJT8EQ5YRiYm8Gg3Yn3AobpwhBtWRaNiVDBCxIQJMUQrQL40YCWYQxwZy4'
  headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  if response.status_code != 200:
        return response.status_code

  return response.json()


# In[3]:


def call_foodics(method, last_page, includables=None, filter = {}):

    list_responses = []

    for page in range(1, last_page+1):
        print(f"page {page}")
        retries = 3
        success = False

        while not success and retries > 0:
            method_ = f'{method}?page={page}'
            try:
                if includables is not None:
                    method_ = method_ + f'&include={includables}'
                if len(filter):
                    filters = ''
                    for key, val in filter.items():
                        filters = f'&filter[{key}]={val}'
                    method_ = method_ + filters
                print(method_)

                response = foodics_api(method_)
                
                # If the request is successful, the following line will be executed
                list_responses.append(response['data'])
                success = True
            except Exception as e:
                print(f"Request failed with page: {page} {str(e)}, retrying... {retries} retries left.")
                retries -= 1
                time.sleep(70) # wait 70 seconds before retrying


        if not success:
            print(f"Failed to retrieve data for page {page} after 3 retries.")
            continue
    return list_responses


# # Branches

# In[4]:


response = foodics_api('branches')
last_page = response['meta']['last_page']
last_page

list_responses = call_foodics('branches', last_page)


# In[5]:


df_branches = pd.DataFrame([item for sublist in list_responses for item in sublist])
df_branches


# In[6]:


df_branches = df_branches[['id', 'name', 'opening_from', 'opening_to']]


# In[7]:


df_branches = df_branches.rename(columns={'id': 'branch_id', 'name': 'branch_name'})


# In[8]:


df_branches.to_csv('../../data/updates/branches.csv', index=False)


# # Products

# In[9]:


response = foodics_api('products')
last_page = response['meta']['last_page']
last_page

list_responses = call_foodics('products', last_page, includables='category')


# In[10]:


df_products = pd.DataFrame([item for sublist in list_responses for item in sublist])


# In[11]:


df_products['category_name'] = df_products['category'].apply(lambda x: x['name_localized'])
df_products = df_products[~df_products.category_name.isna()]
df_products['category_name'] = df_products['category_name'].apply(lambda x: x.capitalize())

df_products['category_id'] = df_products['category'].apply(lambda x: x['id'])
df_products.rename(columns={'id': 'product_id', 'name_localized': 'product_name', 'sku':"product_sku"}, inplace=True)
df_products.drop('category', axis=1, inplace=True)
# df_products = df_products[df_products.deleted_at.ina()]
df_products


# In[12]:


df_products.isnull().sum()


# In[13]:


df_products = df_products[['product_id', 'product_sku', 'name', 'category_name', 'category_id', 'is_active', 'is_stock_product', 'price']]


# In[14]:


df_products = df_products.rename(columns={'name': 'product_name'})


# In[15]:


df_products.head()


# In[16]:


df_products.product_name.unique()


# # Categories

# In[17]:


response = foodics_api('categories')
last_page = response['meta']['last_page']
last_page

list_responses = call_foodics('categories', last_page)


# In[18]:


df_categories = pd.DataFrame([item for sublist in list_responses for item in sublist])
df_categories


# In[19]:


cats_to_be_deleted = df_categories[~df_categories.deleted_at.isna()]
cats_to_be_deleted


# In[20]:


df_categories = df_categories[df_categories.deleted_at.isna()]


# In[21]:


df_categories = df_categories[['id', 'name_localized']].rename(columns={"id":"category_id", 'name_localized':"category_name"})


# In[22]:


df_categories.head()


# In[23]:


df_categories.category_name = df_categories.category_name.apply(lambda x: x.capitalize())


# In[24]:


df_categories.head()


# In[25]:


df_categories.to_csv('../../data/updates/categories.csv', index=False)


# # Payment Method

# In[26]:


response = foodics_api('payment_methods')
last_page = response['meta']['last_page']
last_page

list_responses = call_foodics('payment_methods', last_page)


# In[27]:


df_payment_methods = pd.DataFrame([item for sublist in list_responses for item in sublist])
df_payment_methods


# In[28]:


df_payment_methods = df_payment_methods[['id', 'name']].rename(columns={"id":"payment_method_id", 'name':"payment_method_name"})
df_payment_methods


# In[29]:


df_payment_methods.to_csv('../../data/updates/payment_methods.csv', index=False)


# # Orders

# In[30]:


df_orders = pd.read_csv('../../data/orders_final_include.csv')
df_orders.reset_index(drop=True, inplace=True)


# In[31]:


df_orders.created_at = pd.to_datetime(df_orders.created_at)
max_date = df_orders.created_at.max().date().strftime('%Y-%m-%d')
max_date


# In[32]:


today = date.today().strftime('%Y-%m-%d')
today


# In[33]:


response = foodics_api(f'orders?filter[business_date_after]={max_date}')
last_page = response['meta']['last_page']
print(last_page)

filters = {'business_date_after':max_date}
includables = 'products,branch,products.product,tags,products.promotion,payments.payment_method'
list_responses = call_foodics('orders', last_page, includables=includables, filter=filters)


# In[34]:


df_new_orders = pd.DataFrame([item for sublist in list_responses for item in sublist])
df_new_orders


# In[35]:


df_updated_data = pd.concat([df_orders, df_new_orders])
df_updated_data.to_csv('../../data/orders_final_include_updated.csv', index=False)

# import boto3
# from src.config import config_aws

# s3 = boto3.client('s3', aws_access_key_id=config_aws['access_key'], aws_secret_access_key=config_aws['secret_access_key'])

# bucket_name = config_aws['bucket_name']

# s3.upload_file('data/orders_final_include_updated.csv', bucket_name, 'chicks/orders_final_include.csv')


# In[36]:


df_orders = df_new_orders.copy()
del df_new_orders


# In[37]:


df_orders=df_orders.reset_index(drop=True)


# In[38]:


df_orders.head()


# In[39]:


df_orders['branch'] = df_orders['branch'].astype(str)
df_orders['tags'] = df_orders['tags'].astype(str)
df_orders['payments'] = df_orders['payments'].astype(str)
df_orders['products'] = df_orders['products'].astype(str)


# In[40]:


df_orders['branch_id'] = df_orders['branch'].apply(lambda x: eval(x)['id'])


# In[41]:


orders_header = df_orders[['id', 'branch_id', 'created_at', 'total_price', 'source', 'type', 'status']].rename(columns={'id':'order_id', 'created_at':'order_date', 'total_price':'order_total_price', 'source':'order_source', 'type':'order_type', 'status':'order_status'})
orders_header.isnull().sum()


# In[42]:


orders_header.head()


# In[ ]:





# # Order Details

# In[43]:


df_orders.head()


# In[44]:


# I want to create a dataframe with the following columns:
# order_id, product_id, category_id, quantity, price

# I will create a list of dictionaries, where each dictionary is a row in the dataframe
# I will then convert the list of dictionaries to a dataframe

list_order_details = []

for index, row in df_orders.iterrows():

    order_id = row['id']
    branch_id = eval(row['branch'])['id']
    order_date = row['created_at']
    order_total_price = row['total_price']
    order_source = row['source']
    order_type = row['type']
    order_status = row['status']

    for order_product in eval(row['products']):

        product_id = order_product['product']['id']
        category_id = df_products[df_products['product_id'] == product_id]['category_id'].values[0]
        quantity = order_product['quantity']
        price = order_product['product']['price']

        list_order_details.append({'order_id':order_id,
                                   'branch_id':branch_id,
                                   'order_date':order_date,
                                   'order_total_price':order_total_price,
                                   'order_source':order_source,
                                   'order_type':order_type,
                                   'order_status':order_status,
                                   'product_id':product_id,
                                   'category_id':category_id,
                                   'quantity':quantity,
                                   'price':price})


# In[45]:


orders_details = pd.DataFrame(list_order_details)


# In[46]:


orders_details.head()


# In[47]:


cats_to_be_deleted.id.values.tolist()


# In[48]:


order_header_id_to_be_deleted = orders_details[orders_details.category_id.isin(cats_to_be_deleted.id.values.tolist())].order_id.unique()


# In[49]:


orders_details = orders_details[~orders_details.category_id.isin(cats_to_be_deleted.id.values.tolist())]


# In[50]:


orders_header = orders_header[~orders_header.order_id.isin(order_header_id_to_be_deleted)]


# In[51]:


df_products = df_products[~df_products.category_id.isin(cats_to_be_deleted.id.values.tolist())]


# # UTC TO AMMAN

# In[52]:


import pytz


orders_details['order_date'] = pd.to_datetime(orders_details['order_date'])
orders_details['order_date'] = orders_details['order_date'].dt.tz_localize('UTC')
orders_details['order_date'] = orders_details['order_date'].dt.tz_convert(pytz.timezone('Asia/Amman'))

orders_header['order_date'] = pd.to_datetime(orders_header['order_date'])
orders_header['order_date'] = orders_header['order_date'].dt.tz_localize('UTC')
orders_header['order_date'] = orders_header['order_date'].dt.tz_convert(pytz.timezone('Asia/Amman'))


# # Write to CSV

# In[53]:


df_products.to_csv('../../data/updates/products.csv', index=False)


# In[54]:


orders_details.to_csv('../../data/updates/order_details.csv', index=False)


# In[55]:


orders_header.to_csv('../../data/updates/order_header.csv', index=False)


# # Display all

# In[56]:


df_products.head()


# In[57]:


orders_details.head()


# In[58]:


orders_header.head()


# In[ ]:





# In[ ]:




