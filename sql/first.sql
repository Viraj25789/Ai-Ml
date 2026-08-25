create table products(
product_id serial primary key,
name varchar(50) not null,
sku_code char(8) unique not null check (char_length(sku_code) = 8),
price decimal(10,2) default 0 check(price>=0),
stock_quantity int default 0 check(stock_quantity>=0),
available boolean default TRUE,
category text not null,
added_on date default current_date,
last_update_on timestamp default now()
)

insert into products(name, sku_code, price, stock_quantity, category)
values ('t-shirt', '12343244', 453.00, 30, 'cloths' )

-- PROBLEMS:

-- if id is inserted manually then count violates n next insertation, then use below code so count start from last maximum id.

insert into products(product_id, name, sku_code, price, stock_quantity, category)
values (2, 'shirt', '12343374', 503.00, 30, 'cloths' )

-- use this
select last_value from products_product_id_seq;
select setval('products_product_id_seq' ,(select max(product_id) from products))

insert into products(name, sku_code, price, stock_quantity, category)
values ('jeans-pant', '12353374', 600.00, 30, 'cloths' )



-- here sku_code is maximum 8, we want compulsary 8. here less than 8 is also work so change in table format.

-- X -- sku_code char(8) unique not null
-- insert into products(name, sku_code, price, stock_quantity, category) values ('cotton-pant', '123374', 500.00, 30, 'cloths' )

-- ^ -- sku_code char(8) unique not null check (char_length(sku_code) = 8)
-- insert into products(name, sku_code, price, stock_quantity, category) values ('cotton-pant', '123374', 500.00, 30, 'cloths' )
-- gives error so change in database, then value of sku_code

select * from products

-- no use Rs. in price
-- data type is not proper

