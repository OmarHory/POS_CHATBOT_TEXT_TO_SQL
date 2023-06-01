#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


#read all data
orders_header = pd.read_csv('../../data/updates/order_header.csv')
orders_details = pd.read_csv('../../data/updates/order_details.csv')
products = pd.read_csv('../../data/updates/products.csv')

payment_methods = pd.read_csv('../../data/updates/payment_methods.csv')
branches = pd.read_csv('../../data/updates/branches.csv')
categories = pd.read_csv('../../data/updates/categories.csv')






# # Orders Headers

# In[3]:


orders_header.head()


# In[4]:


orders_types = {1:'Dine In', 2:'Pick Up', 3:'Delivery', '4':'Drive Thru'}
orders_sources = {1:'Cashier', 2:'API', 3:'Call Center'}
orders_statuses = {1:'Pending', 2:'Active', 3:'Declined', 4:'Closed', 5:'Returned', 6:'Joined', 7:'Void'}
# orders_delivery_statuses = {1:'sent to kitchen', 2:'ready', 3:'assigned', 4:'en route', 5:'delivered', 6:'closed'}
# products_statuses = {1:'Pending', 2:'Active', 3:'Closed', 4:'Moved', 5:'Void', 6:'Returned', 7:'Declined'}
# discounts_types = {1:'Open', 2:'Predefined', 3:'Coupon', 4:'Loyalty', 5:'Promotion'}

#---------------

orders_header['order_type'] = orders_header['order_type'].map(orders_types)
orders_header['order_source'] = orders_header['order_source'].map(orders_sources)
orders_header['order_status'] = orders_header['order_status'].map(orders_statuses)


# In[5]:


orders_header['order_datetime'] = pd.to_datetime(orders_header['order_date'])

orders_header['order_time'] = orders_header['order_datetime'].dt.time
orders_header['order_date'] = orders_header['order_datetime'].dt.date

# orders_header['hour'] = orders_header['order_datetime'].dt.hour
# orders_header['day_name'] = orders_header['order_datetime'].dt.day_name()
# orders_header['is_weekend'] = orders_header['order_datetime'].dt.dayofweek.isin([4, 5])
# orders_header['is_weekend'].replace({True:'Yes', False:'No'}, inplace=True)
# orders_header['month'] = orders_header['order_datetime'].dt.month
# orders_header['year'] = orders_header['order_datetime'].dt.year




# In[6]:


orders_header.drop_duplicates(inplace=True)


# In[7]:


orders_header.isnull().sum()


# In[8]:


orders_header.head()


# In[9]:


orders_header.rename(columns={'order_id':'order_header_id'}, inplace=True)


# In[10]:


orders_header['order_status'].fillna('Void', inplace=True)


# In[11]:


orders_header.rename(columns={'order_id':'order_header_id'}, inplace=True)


# In[12]:


orders_header.to_csv('../../data/processed/updates/order_header.csv', index=False)


# # Order Details

# In[13]:


orders_details.head()


# In[14]:


filtered_orders_details = orders_details.drop(columns=['order_date', 'order_total_price','order_source', 'order_type', 'order_status', 'branch_id'])
filtered_orders_details.head()


# In[15]:


#filtered_orders_details['order_line_id'] = filtered_orders_details['order_id'] + '-' + filtered_orders_details['product_id'].apply(lambda x: x.split('-')[1]) + 
import uuid
filtered_orders_details['order_details_id'] = [str(uuid.uuid4()) for _ in range(len(filtered_orders_details))]
filtered_orders_details.rename(columns={'order_id':'order_header_id'}, inplace=True)


# In[16]:


filtered_orders_details.head()


# In[17]:


filtered_orders_details.drop_duplicates(inplace=True)


# In[18]:


filtered_orders_details.to_csv('../../data/processed/updates/order_details.csv', index=False)


# # Products

# In[19]:


products.head()


# In[20]:


products.head()


# In[21]:


products.product_name.unique()


# In[22]:


products.product_sku.unique()


# In[23]:


products.product_sku.nunique()


# In[24]:


products.to_csv('../../data/processed/updates/products.csv', index=False)


# # Branches

# In[25]:


branches.head()


# In[26]:


branches['opening_from'] = pd.to_datetime(branches['opening_from'])
branches['opening_to'] = pd.to_datetime(branches['opening_to'])

branches['opening_from'] = branches['opening_from'].dt.hour
branches['opening_to'] = branches['opening_to'].dt.hour


# In[27]:


branches.to_csv('../../data/processed/updates/branches.csv', index=False)


# # Categories

# In[28]:


categories


# In[29]:


categories.to_csv('../../data/processed/updates/categories.csv', index=False)


# In[30]:


# def check_values_exist(list1, list2):
#     return all(value in list2 for value in list1)

# check_values_exist(products.category_id.unique(), categories.category_id.unique())

