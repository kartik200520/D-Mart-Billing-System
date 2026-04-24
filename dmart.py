import os
import pymysql
import math
from datetime import datetime, timedelta
import io
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import ttk, messagebox, simpledialog, filedialog
import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import qrcode
except Exception:
    qrcode = None
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
except Exception:
    canvas = None

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASS = "sakshi9284"
database = "billing"
DB_SCHEMAS = [
    "dmart_products_db",
    "dmart_customers_db",
    "dmart_sales_db",
    "dmart_users_db",
    "dmart_stock_db",
    "dmart_suppliers_db",
    "dmart_reports_db",
]
BILLS_DIR = "bills"
PDF_DIR = os.path.join(BILLS_DIR, "pdf")
FEEDBACK_DIR = "feedback"
CONTACT_FILE = os.path.join(FEEDBACK_DIR, "contacts.json")
os.makedirs(BILLS_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Email configuration (for feedback/contact us)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "dmart.billing@gmail.com",
    "sender_password": "your_app_password_here",
    "admin_email": "admin@dmart.com"
}

REQUESTS_AVAILABLE = True
PIL_AVAILABLE = True

categories = {
    "Grocery": [
        {"name": "Rice", "price": 60, "qty": 100,
         "img": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"},
        {"name": "Oil", "price": 150, "qty": 50,
         "img": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400"},
        {"name": "Snacks", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400"},
        {"name": "Wheat", "price": 45, "qty": 90,
         "img": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400"},
        {"name": "Sugar", "price": 50, "qty": 100,
         "img": "https://images.unsplash.com/photo-1582005450386-52b25f82d9bb?w=400"},
        {"name": "Spices", "price": 120, "qty": 50,
         "img": "https://images.unsplash.com/photo-1596040033229-a0b59e4d7bbe?w=400"},
        {"name": "Salt", "price": 20, "qty": 200,
         "img": "https://images.unsplash.com/photo-1607467623051-6c1b8ffb3992?w=400"},
        {"name": "Peanuts", "price": 80, "qty": 50,
         "img": "https://images.unsplash.com/photo-1560750586-7d0bc5a45f6d?w=400"},
        {"name": "Tea", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400"},
        {"name": "Coffee", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400"},
        {"name": "Bread", "price": 30, "qty": 70,
         "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"},
        {"name": "Pasta", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1551462147-37a42ba22e5c?w=400"},
        {"name": "Biscuits", "price": 50, "qty": 90,
         "img": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400"},
        {"name": "Dal", "price": 120, "qty": 60,
         "img": "https://images.unsplash.com/photo-1607672632458-9eb56696346b?w=400"},
        {"name": "Dry Fruits", "price": 500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=400"},
    ],

    "Clothing": [
        {"name": "T-shirt", "price": 500, "qty": 20,
         "img": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"},
        {"name": "Jeans", "price": 500, "qty": 20,
         "img": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"},
        {"name": "Shirt", "price": 500, "qty": 20,
         "img": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400"},
        {"name": "Shorts", "price": 500, "qty": 20,
         "img": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=400"},
        {"name": "Kurta", "price": 500, "qty": 20,
         "img": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400"},
        {"name": "Kurtis", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1583391733956-6c78276477e5?w=400"},
        {"name": "Hoodie", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400"},
        {"name": "Jacket", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400"},
        {"name": "Saree", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1610030469024-61598c1a2d68?w=400"},
        {"name": "Lehenga", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1583391733981-2bbb37da4c0e?w=400"},
        {"name": "Dress", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400"},
        {"name": "Skirt", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400"},
        {"name": "Pajama", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=400"},
        {"name": "Innerwear", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=400"},
        {"name": "Cap", "price": 1200, "qty": 20,
         "img": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400"},
    ],

    "BED & BATH": [
        {"name": "Bedsheet", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=400"},
        {"name": "Pillow", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1566475877635-b07a6ce0f1c5?w=400"},
        {"name": "Blanket", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1631654870230-c1030ae785e1?w=400"},
        {"name": "Mattress", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400"},
        {"name": "Bath Towel", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1622197352395-7a7f5a4a73f7?w=400"},
        {"name": "Hand Towel", "price": 400, "qty": 20,
         "img": "https://images.unsplash.com/photo-1580870069867-74c892c0ac1f?w=400"},
        {"name": "Shower Curtain", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400"},
        {"name": "Bathrobe", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1602810316498-ab67cf68c8e1?w=400"},
        {"name": "Soap", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1588865198282-293a8ae7a8f4?w=400"},
        {"name": "Body Wash", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400"},
        {"name": "Face Towel", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=400"},
        {"name": "Duvet", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1631049552240-59c37f38802b?w=400"},
        {"name": "Mattress Protector", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400"},
        {"name": "Pillow Cover", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400"},
        {"name": "Bath Mat", "price": 900, "qty": 20,
         "img": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400"},
    ],

    "Personal Care": [
        {"name": "Soap Bar", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1588865198282-293a8ae7a8f4?w=400"},
        {"name": "Shampoo", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400"},
        {"name": "Conditioner", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1608248593803-ba4f8c70ae0b?w=400"},
        {"name": "Body Lotion", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400"},
        {"name": "Deodorant", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1625911223163-f85f82d5d7d1?w=400"},
        {"name": "Toothpaste", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=400"},
        {"name": "Toothbrush", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=400"},
        {"name": "Face Wash", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?w=400"},
        {"name": "Moisturizer", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"},
        {"name": "Sunscreen", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400"},
        {"name": "Lip Balm", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1591360236480-4ed861025fa1?w=400"},
        {"name": "Hair Oil", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400"},
        {"name": "Perfume", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400"},
        {"name": "Razor", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1620756726574-31c7995bb69f?w=400"},
        {"name": "Hand Sanitizer", "price": 400, "qty": 40,
         "img": "https://images.unsplash.com/photo-1584670747037-2bafaa95bbda?w=400"},
    ],

    "Plastic Containers": [
        {"name": "Water Bottle", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400"},
        {"name": "Lunch Box", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=400"},
        {"name": "Storage Box", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1600493572882-d0b68f9f0b8e?w=400"},
        {"name": "Dustbin", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=400"},
        {"name": "Bucket", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=400"},
        {"name": "Plastic Jar", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1601158935942-52255782d322?w=400"},
        {"name": "Tiffin", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1614887663614-7b788c4f7535?w=400"},
        {"name": "Mug", "price": 80, "qty": 40,
         "img": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400"},
        {"name": "Tub", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1600493572882-d0b68f9f0b8e?w=400"},
        {"name": "Cup Set", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1565345614-d4b6f6610a05?w=400"},
        {"name": "Spoon Set", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1563299796-17596f486249?w=400"},
        {"name": "Bowl", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1578663899664-27b62d94a4d6?w=400"},
        {"name": "Cutlery Set", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1616486701797-4b8b0b2d5d0d?w=400"},
        {"name": "Food Container", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1584473457493-2f50f8eba2c0?w=400"},
        {"name": "Soap Box", "price": 200, "qty": 40,
         "img": "https://images.unsplash.com/photo-1600857062241-98e5e6b17bfd?w=400"},
    ],

    "Toys": [
        {"name": "Ball", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1575407520495-38843e96dfe6?w=400"},
        {"name": "RC Car", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
        {"name": "Puzzle", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400"},
        {"name": "Doll", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1594088838534-62830d94f909?w=400"},
        {"name": "Teddy Bear", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1519872436884-2c7d2d6d43d9?w=400"},
        {"name": "Toy Train", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
        {"name": "Toy Car", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
        {"name": "LEGO Set", "price": 150, "qty": 30,
         "img": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400"},
        {"name": "Action Figure", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1601015604735-0c45e1d66b8f?w=400"},
        {"name": "Board Game", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1606167668584-78701c57f13d?w=400"},
        {"name": "YoYo", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
        {"name": "Kites", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1599003793331-1f8e7e7ba87f?w=400"},
        {"name": "Rubik's Cube", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1591991731833-b6884ec3ce5f?w=400"},
        {"name": "Water Gun", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1530103043960-ef38714abb15?w=400"},
        {"name": "Frisbee", "price": 600, "qty": 30,
         "img": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=400"},
    ],

    "Dairy Product": [
        {"name": "Milk", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400"},
        {"name": "Paneer", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400"},
        {"name": "Yogurt", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1571212515416-fad2b1f79c1e?w=400"},
        {"name": "Cheese", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=400"},
        {"name": "Butter", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400"},
        {"name": "Cream", "price": 60, "qty": 50,
         "img": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400"},
        {"name": "Ghee", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1619602162664-de3fbb5c8e03?w=400"},
        {"name": "Ice Cream", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400"},
        {"name": "Milk Powder", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1587049352846-4a222e784778?w=400"},
        {"name": "Curd", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1571212515416-fad2b1f79c1e?w=400"},
        {"name": "Buttermilk", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=400"},
        {"name": "Flavored Milk", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400"},
        {"name": "Custard", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400"},
        {"name": "Whey", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1593252719532-c48c5a95a05f?w=400"},
        {"name": "Khoa", "price": 180, "qty": 50,
         "img": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400"},
    ],

    "Fruits": [
        {"name": "Apple", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400"},
        {"name": "Banana", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400"},
        {"name": "Mango", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400"},
        {"name": "Orange", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1547514701-42782101795e?w=400"},
        {"name": "Grapes", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1599819177344-8d294643e8a7?w=400"},
        {"name": "Papaya", "price": 60, "qty": 60,
         "img": "https://images.unsplash.com/photo-1617112848923-cc2234396a8d?w=400"},
        {"name": "Guava", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1610394025335-ee2a9a71e43c?w=400"},
        {"name": "Pineapple", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400"},
        {"name": "Pomegranate", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1615485290937-4102784c6c57?w=400"},
        {"name": "Kiwi", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400"},
        {"name": "Cherry", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400"},
        {"name": "Lychee", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1600882891884-8f80f9b3c4cd?w=400"},
        {"name": "Strawberry", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400"},
        {"name": "Watermelon", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1587049352846-4a222e784778?w=400"},
        {"name": "Dragon Fruit", "price": 200, "qty": 60,
         "img": "https://images.unsplash.com/photo-1527325678964-54921661f888?w=400"},
    ],

    "Footwear": [
        {"name": "Sneakers", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"},
        {"name": "Slippers", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400"},
        {"name": "Sandals", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400"},
        {"name": "Formal Shoes", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=400"},
        {"name": "Heels", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400"},
        {"name": "Flip Flops", "price": 800, "qty": 30,
         "img": "https://images.unsplash.com/photo-1560343787-b90cb337028e?w=400"},
        {"name": "Boots", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400"},
        {"name": "Sports Shoes", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400"},
        {"name": "Loafers", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=400"},
        {"name": "Canvas Shoes", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400"},
        {"name": "Walking Shoes", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1562183241-b937e95585b6?w=400"},
        {"name": "Crocs", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400"},
        {"name": "Wedges", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400"},
        {"name": "Moccasins", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=400"},
        {"name": "Socks", "price": 2500, "qty": 30,
         "img": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=400"},
    ],

    "Cold Drinks": [
        {"name": "Coca Cola", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400"},
        {"name": "Pepsi", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400"},
        {"name": "Sprite", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=400"},
        {"name": "Fanta", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1624517452488-04869289c4ca?w=400"},
        {"name": "Mountain Dew", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400"},
        {"name": "Red Bull", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1622543925917-763c34f3865b?w=400"},
        {"name": "Limca", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=400"},
        {"name": "Thumbs Up", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=400"},
        {"name": "7Up", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=400"},
        {"name": "Appy Fizz", "price": 40, "qty": 80,
         "img": "https://images.unsplash.com/photo-1625772452859-1c03d5bf1137?w=400"},
        {"name": "Mirinda", "price": 120, "qty": 80,
         "img": "https://images.unsplash.com/photo-1624517452488-04869289c4ca?w=400"},
        {"name": "Slice", "price": 120, "qty": 80,
         "img": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400"},
        {"name": "Maaza", "price": 120, "qty": 80,
         "img": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400"},
        {"name": "Tonic Water", "price": 120, "qty": 80,
         "img": "https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=400"},
        {"name": "Soda Water", "price": 120, "qty": 80,
         "img": "https://images.unsplash.com/photo-1625772452859-1c03d5bf1137?w=400"},
    ],

    "Others": [
        {"name": "Gift Item", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=400"},
        {"name": "Stationery Set", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=400"},
        {"name": "Umbrella", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1495344517868-8ebaf0a2044a?w=400"},
        {"name": "Bag", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
        {"name": "Wallet", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=400"},
        {"name": "Watch", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=400"},
        {"name": "Keychain", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=400"},
        {"name": "Mobile Cover", "price": 150, "qty": 40,
         "img": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400"},
        {"name": "Home Decor", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400"},
        {"name": "Candle", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1602874801006-94c78b7f3611?w=400"},
        {"name": "Picture Frame", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1513519245088-0e12902e35ca?w=400"},
        {"name": "Tool Kit", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=400"},
        {"name": "Battery", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1609091839311-d6f052f26f62?w=400"},
        {"name": "Sewing Kit", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1597899992116-c777c2957d1e?w=400"},
        {"name": "Stapler", "price": 600, "qty": 40,
         "img": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400"},
    ],
}

BACKGROUND_IMAGES = {
    "login_bg": "https://images.unsplash.com/photo-1607082350899-7e105aa886ae?w=800",  # Supermarket aisle
    "dashboard_bg": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=800",  # Shopping cart
    "category_bg": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=800",  # Retail store
}


# Load contact data
def load_contacts():
    if os.path.exists(CONTACT_FILE):
        try:
            with open(CONTACT_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


# Save contact data
def save_contacts(contacts):
    with open(CONTACT_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)


class DBManager:
    def __init__(self, host, user, password, port=3306, schemas=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.schemas = schemas or []
        self.admin_conn = None
        self._connect_admin()

        for s in self.schemas:
            self.create_schema_if_not_exists(s)

        self.ensure_basic_tables()
        self.populate_sample_data()
        self.setup_feedback_table()

    def setup_feedback_table(self):
        """Create feedback table if not exists"""
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    feedback_type VARCHAR(50),
                    message TEXT NOT NULL,
                    rating INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("setup_feedback_table error:", e)

    def _connect_admin(self):
        try:
            self.admin_conn = pymysql.connect(host=self.host, port=self.port,
                                              user=self.user, password=self.password,
                                              autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            messagebox.showerror("DB Error", f"Cannot connect to MySQL server: {e}")
            raise

    def create_schema_if_not_exists(self, schema):
        cur = self.admin_conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{schema}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cur.close()

    def get_conn(self, schema):
        return pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                               database=schema, autocommit=True, cursorclass=pymysql.cursors.DictCursor)

    def list_schemas(self):
        return list(self.schemas)

    def list_tables(self, schema):
        try:
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("SHOW TABLES;")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            tables = []
            for r in rows:
                values = list(r.values())
                if values:
                    tables.append(values[0])
            return tables
        except Exception as e:
            print("list_tables error:", e)
            return []

    def ensure_basic_tables(self):
        # Products table
        try:
            schema = self.schemas[0] if len(self.schemas) >= 1 else None
            if schema:
                conn = self.get_conn(schema)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(128),
                        price DECIMAL(10,2) NOT NULL,
                        qty INT DEFAULT 0,
                        img_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                cur.close()
                conn.close()
        except Exception as e:
            print("ensure_basic_tables/products error:", e)

        # Customers table
        try:
            schema = self.schemas[1] if len(self.schemas) >= 2 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    mobile VARCHAR(50),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/customers error:", e)

        # Sales tables
        try:
            schema = self.schemas[2] if len(self.schemas) >= 3 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bill_no VARCHAR(64) NOT NULL UNIQUE,
                    customer_name VARCHAR(255),
                    subtotal DECIMAL(12,2),
                    gst DECIMAL(12,2),
                    total DECIMAL(12,2),
                    payment_type VARCHAR(32),
                    payment_ref VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sale_id INT,
                    product_name VARCHAR(255),
                    qty INT,
                    price DECIMAL(12,2),
                    discount_percent DECIMAL(5,2) DEFAULT 0,
                    amount DECIMAL(12,2),
                    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS returns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bill_no VARCHAR(64),
                    product_name VARCHAR(255),
                    qty INT,
                    refund_amount DECIMAL(12,2),
                    reason VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/sales error:", e)

        # Users table
        try:
            schema = self.schemas[3] if len(self.schemas) >= 4 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'staff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/users error:", e)

        # Stock table
        try:
            schema = self.schemas[4] if len(self.schemas) >= 5 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_name VARCHAR(255) NOT NULL,
                    category VARCHAR(128),
                    current_stock INT DEFAULT 0,
                    min_stock_level INT DEFAULT 10,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/stock error:", e)

        # Suppliers table
        try:
            schema = self.schemas[5] if len(self.schemas) >= 6 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    contact_person VARCHAR(255),
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/suppliers error:", e)

        # Reports table
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    report_type VARCHAR(255) NOT NULL,
                    report_data JSON,
                    generated_by VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            cur.close()
            conn.close()
        except Exception as e:
            print("ensure_basic_tables/reports error:", e)

    def populate_sample_data(self):
        """Populate all databases with 58 sample records across different tables"""
        try:
            # Add users
            self._populate_users()

            # Add customers (10 records)
            self._populate_customers()

            # Add products (15 records)
            self._populate_products()

            # Add suppliers (8 records)
            self._populate_suppliers()

            # Add stock records (15 records)
            self._populate_stock()

            # Add sample sales (5 records)
            self._populate_sales()

            # Add sample reports (5 records)
            self._populate_reports()

            print("Successfully populated all databases with sample data")

        except Exception as e:
            print(f"Error populating sample data: {e}")

    def _populate_users(self):
        """Add 5 user records"""
        try:
            schema = self.schemas[3] if len(self.schemas) >= 4 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            users = [
                ("admin", "admin123", "admin"),
                ("manager", "manager123", "manager"),
                ("kartik", "1234", "staff"),
                ("sakshi", "sakshi123", "staff"),
                ("rahul", "rahul123", "staff")
            ]

            for username, password, role in users:
                cur.execute("INSERT IGNORE INTO users (username, password, role) VALUES (%s, %s, %s)",
                            (username, password, role))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 5 user records")
        except Exception as e:
            print(f"Error populating users: {e}")

    def _populate_customers(self):
        """Add 10 customer records"""
        try:
            schema = self.schemas[1] if len(self.schemas) >= 2 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            customers = [
                ("Rajesh Kumar", "9876543210", "123 Main St, Mumbai"),
                ("Priya Singh", "9876543211", "456 Park Ave, Delhi"),
                ("Amit Patel", "9876543212", "789 MG Road, Bangalore"),
                ("Sneha Sharma", "9876543213", "321 Church St, Chennai"),
                ("Vikram Joshi", "9876543214", "654 Marine Drive, Mumbai"),
                ("Anjali Gupta", "9876543215", "987 Connaught Place, Delhi"),
                ("Rohit Verma", "9876543216", "159 Jubilee Hills, Hyderabad"),
                ("Pooja Mehta", "9876543217", "753 Koregaon Park, Pune"),
                ("Sanjay Reddy", "9876543218", "486 Banjara Hills, Hyderabad"),
                ("Neha Kapoor", "9876543219", "264 Salt Lake, Kolkata")
            ]

            for name, mobile, address in customers:
                cur.execute("INSERT IGNORE INTO customers (name, mobile, address) VALUES (%s, %s, %s)",
                            (name, mobile, address))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 10 customer records")
        except Exception as e:
            print(f"Error populating customers: {e}")

    def _populate_products(self):
        """Add 15 product records from categories"""
        try:
            schema = self.schemas[0] if len(self.schemas) >= 1 else None
            if not schema:
                return

            conn = self.get_conn(schema)
            cur = conn.cursor()

            # Take first product from each category
            product_count = 0
            for category, products in categories.items():
                if products and product_count < 15:  # Limit to 15 products
                    product = products[0]
                    cur.execute("""
                        INSERT IGNORE INTO products (name, category, price, qty, img_url) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (product['name'], category, product['price'], product['qty'], product.get('img')))
                    product_count += 1

            conn.commit()
            cur.close()
            conn.close()
            print(f"Added {product_count} product records")
        except Exception as e:
            print(f"Error populating products: {e}")

    def _populate_suppliers(self):
        """Add 8 supplier records"""
        try:
            schema = self.schemas[5] if len(self.schemas) >= 6 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            suppliers = [
                ("Reliance Fresh", "Mr. Sharma", "9876543201", "contact@reliance.com", "Reliance Mart, Mumbai"),
                ("More Supermarket", "Ms. Patel", "9876543202", "info@more.com", "More Store, Delhi"),
                ("Big Bazaar", "Mr. Gupta", "9876543203", "support@bigbazaar.com", "Big Bazaar, Bangalore"),
                ("D-Mart Suppliers", "Mr. Kumar", "9876543204", "dmart@suppliers.com", "D-Mart HQ, Pune"),
                ("Metro Cash & Carry", "Mr. Singh", "9876543205", "metro@contact.com", "Metro Center, Hyderabad"),
                ("Star Bazaar", "Ms. Reddy", "9876543206", "star@bazaar.com", "Star Complex, Chennai"),
                ("Spencer's Retail", "Mr. Joshi", "9876543207", "spencers@retail.com", "Spencer Plaza, Kolkata"),
                ("HyperCity", "Ms. Kapoor", "9876543208", "hypercity@info.com", "HyperCity Mall, Mumbai")
            ]

            for name, contact, phone, email, address in suppliers:
                cur.execute(
                    "INSERT IGNORE INTO suppliers (name, contact_person, phone, email, address) VALUES (%s, %s, %s, %s, %s)",
                    (name, contact, phone, email, address))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 8 supplier records")
        except Exception as e:
            print(f"Error populating suppliers: {e}")

    def _populate_stock(self):
        """Add 15 stock records"""
        try:
            schema = self.schemas[4] if len(self.schemas) >= 5 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            # Get products to create stock entries
            product_schema = self.schemas[0] if len(self.schemas) >= 1 else None
            if product_schema:
                prod_conn = self.get_conn(product_schema)
                prod_cur = prod_conn.cursor()
                prod_cur.execute("SELECT name, category, qty FROM products LIMIT 15")
                products = prod_cur.fetchall()
                prod_cur.close()
                prod_conn.close()

                for product in products:
                    cur.execute("""
                        INSERT IGNORE INTO stock (product_name, category, current_stock, min_stock_level) 
                        VALUES (%s, %s, %s, %s)
                    """, (product['name'], product['category'], product['qty'], 10))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 15 stock records")
        except Exception as e:
            print(f"Error populating stock: {e}")

    def _populate_sales(self):
        """Add 5 sample sales records"""
        try:
            schema = self.schemas[2] if len(self.schemas) >= 3 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            # Sample sales data
            sales_data = [
                ("BILL-20240115-0001", "Rajesh Kumar", 1500.00, 75.00, 1575.00, "Cash", None),
                ("BILL-20240115-0002", "Priya Singh", 2300.00, 115.00, 2415.00, "Card", "CardLast4:1234"),
                ("BILL-20240115-0003", "Amit Patel", 800.00, 40.00, 840.00, "UPI", "upi@payment"),
                ("BILL-20240115-0004", "Sneha Sharma", 3200.00, 160.00, 3360.00, "Cash", None),
                ("BILL-20240115-0005", "Vikram Joshi", 950.00, 47.50, 997.50, "Card", "CardLast4:5678")
            ]

            for bill_no, customer, subtotal, gst, total, payment_type, payment_ref in sales_data:
                cur.execute("""
                    INSERT IGNORE INTO sales (bill_no, customer_name, subtotal, gst, total, payment_type, payment_ref) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (bill_no, customer, subtotal, gst, total, payment_type, payment_ref))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 5 sales records")
        except Exception as e:
            print(f"Error populating sales: {e}")

    def _populate_reports(self):
        """Add 5 sample report records"""
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            import json
            reports = [
                ("Daily Sales", '{"total_sales": 1575, "transactions": 1}', "admin"),
                ("Monthly Summary", '{"month": "January", "total_revenue": 9187.5}', "manager"),
                ("Stock Alert", '{"low_stock_items": 3, "out_of_stock": 0}', "system"),
                ("Customer Analysis", '{"new_customers": 5, "repeat_customers": 3}', "admin"),
                ("Payment Methods", '{"cash": 2, "card": 2, "upi": 1}', "manager")
            ]

            for report_type, report_data, generated_by in reports:
                cur.execute("INSERT IGNORE INTO reports (report_type, report_data, generated_by) VALUES (%s, %s, %s)",
                            (report_type, report_data, generated_by))

            conn.commit()
            cur.close()
            conn.close()
            print("Added 5 report records")
        except Exception as e:
            print(f"Error populating reports: {e}")

    def add_customer(self, name, mobile=None, address=None):
        try:
            schema = self.schemas[1] if len(self.schemas) >= 2 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("INSERT INTO customers (name, mobile, address) VALUES (%s,%s,%s)", (name, mobile, address))
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print("add_customer error:", e)
            return False

    def list_customers(self, limit=200):
        try:
            schema = self.schemas[1] if len(self.schemas) >= 2 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("SELECT id, name, mobile FROM customers ORDER BY id DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print("list_customers error:", e)
            return []

    def add_product(self, name, category, price, qty, img_url=None):
        try:
            schema = self.schemas[0] if len(self.schemas) >= 1 else None
            if not schema:
                return False
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("INSERT INTO products (name, category, price, qty, img_url) VALUES (%s,%s,%s,%s,%s)",
                        (name, category, price, qty, img_url))
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print("add_product error:", e)
            return False

    def list_products(self, limit=500):
        try:
            schema = self.schemas[0] if len(self.schemas) >= 1 else None
            if not schema:
                return []
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("SELECT id, name, category, price, qty FROM products ORDER BY id DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print("list_products error:", e)
            return []

    def add_feedback(self, username, email, feedback_type, message, rating=0):
        """Add feedback to database"""
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO feedback (username, email, feedback_type, message, rating)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, feedback_type, message, rating))
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print("add_feedback error:", e)
            return False

    def get_feedback_list(self):
        """Get all feedback entries"""
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("SELECT * FROM feedback ORDER BY created_at DESC")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print("get_feedback_list error:", e)
            return []

    def delete_feedback(self, feedback_id):
        """Delete feedback by ID"""
        try:
            schema = self.schemas[6] if len(self.schemas) >= 7 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print("delete_feedback error:", e)
            return False

    def register_user(self, username, password, email=None, role="staff"):
        """Register a new user"""
        try:
            schema = self.schemas[3] if len(self.schemas) >= 4 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()

            # Check if username already exists
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                cur.close()
                conn.close()
                return False, "Username already exists"

            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                        (username, password, role))
            cur.close()
            conn.close()
            return True, "Registration successful"
        except Exception as e:
            print("register_user error:", e)
            return False, f"Registration failed: {str(e)}"

    def check_user_credentials(self, username, password):
        """Check if user credentials are valid"""
        try:
            schema = self.schemas[3] if len(self.schemas) >= 4 else self.schemas[0]
            conn = self.get_conn(schema)
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()
            conn.close()
            return user
        except Exception as e:
            print("check_user_credentials error:", e)
            return None


# Instantiate DBManager
try:
    dbm = DBManager(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, port=MYSQL_PORT, schemas=DB_SCHEMAS)
except Exception as e:
    raise SystemExit("Failed to initialize DB manager. Fix MySQL credentials and make sure server is running.") from e


# ---------------- File helpers ----------------
def save_bill_txt(filename, content):
    path = os.path.join(BILLS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def parse_total_from_bill_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TOTAL:"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        amt_token = parts[-1].replace("₹", "").replace(",", "")
                        try:
                            return float(amt_token)
                        except:
                            return 0.0
    except Exception:
        pass
    return 0.0


# ---------------- PIL placeholder & image utils ----------------
def make_pil_placeholder(text, size=(260, 140), bg=(245, 245, 245), accent=(90, 140, 200)):
    img = Image.new("RGBA", size, bg + (255,))
    draw = ImageDraw.Draw(img)
    top_h = int(size[1] * 0.55)
    draw.rectangle([6, 6, size[0] - 6, top_h], fill=accent)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    try:
        font2 = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception:
        font2 = ImageFont.load_default()
    text_short = text if len(text) <= 18 else text[:16] + "..."
    try:
        bbox = draw.textbbox((0, 0), text_short, font=font)
        tw = bbox[2] - bbox[0];
        th = bbox[3] - bbox[1]
    except Exception:
        tw, th = draw.textsize(text_short, font=font)
    draw.text(((size[0] - tw) / 2, (top_h - th) / 2), text_short, fill=(255, 255, 255), font=font)
    nm = text if len(text) <= 36 else text[:34] + "..."
    try:
        bbox2 = draw.textbbox((0, 0), nm, font=font2)
        tw2 = bbox2[2] - bbox2[0];
        th2 = bbox2[3] - bbox2[1]
    except Exception:
        tw2, th2 = draw.textsize(nm, font=font2)
    draw.text(((size[0] - tw2) / 2, top_h + 8), nm, fill=(30, 30, 30), font=font2)
    img = ImageOps.expand(img, border=1, fill=(220, 220, 220))
    return img


def load_image_from_url(url, size=(220, 120)):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, stream=True, timeout=10, headers=headers)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        img.thumbnail(size, Image.LANCZOS)
        bg = Image.new("RGBA", size, (255, 255, 255, 255))
        bx = (size[0] - img.width) // 2
        by = (size[1] - img.height) // 2
        bg.paste(img, (bx, by), img if img.mode == "RGBA" else None)
        return bg
    except Exception as e:
        print("load image error:", e)
        return None


def pil_to_ctkimage(pil_img, size):
    try:
        return CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
    except Exception:
        return None


def ensure_sales_tables():
    try:
        schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
        conn = dbm.get_conn(schema)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bill_no VARCHAR(64) NOT NULL UNIQUE,
                customer_name VARCHAR(255),
                subtotal DECIMAL(12,2),
                gst DECIMAL(12,2),
                total DECIMAL(12,2),
                payment_type VARCHAR(32),
                payment_ref VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sale_id INT,
                product_name VARCHAR(255),
                qty INT,
                price DECIMAL(12,2),
                discount_percent DECIMAL(5,2) DEFAULT 0,
                amount DECIMAL(12,2),
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bill_no VARCHAR(64),
                product_name VARCHAR(255),
                qty INT,
                refund_amount DECIMAL(12,2),
                reason VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cur.close()
        conn.close()
    except Exception as e:
        print("ensure_sales_tables error:", e)


def get_next_bill_no():
    try:
        ensure_sales_tables()
        schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
        conn = dbm.get_conn(schema)
        cur = conn.cursor()
        today = datetime.now().strftime("%Y%m%d")
        like = f"BILL-{today}-%"
        cur.execute("SELECT bill_no FROM sales WHERE bill_no LIKE %s ORDER BY id DESC LIMIT 1000", (like,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        max_idx = 0
        for r in rows:
            bn = list(r.values())[0] if isinstance(r, dict) else r[0]
            m = re.search(rf"BILL-{today}-(\d+)", bn)
            if m:
                try:
                    v = int(m.group(1))
                    if v > max_idx: max_idx = v
                except:
                    pass
        nxt = max_idx + 1
        return f"BILL-{today}-{nxt:04d}"
    except Exception as e:
        print("get_next_bill_no error:", e)
        return f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def save_sale_to_db_record(bill_no, customer, subtotal, gst, total, payment_type, payment_ref, cart_items):
    try:
        schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
        conn = dbm.get_conn(schema)
        cur = conn.cursor()
        # insert sale
        cur.execute("""
            INSERT INTO sales (bill_no, customer_name, subtotal, gst, total, payment_type, payment_ref)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (bill_no, customer, subtotal, gst, total, payment_type, payment_ref))
        sale_id = cur.lastrowid
        # insert items
        for it in cart_items:
            disc = float(it.get("discount_percent", 0)) if it.get("discount_percent") is not None else 0.0
            gross = round(it['price'] * it['qty'], 2)
            amount = round(gross * (1 - disc / 100.0), 2)
            cur.execute("""
                INSERT INTO sale_items (sale_id, product_name, qty, price, discount_percent, amount)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (sale_id, it['name'], it['qty'], it['price'], disc, amount))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("save_sale_to_db_record error:", e)
        return False


def reduce_stock_in_db(cart_items):
    try:
        prod_schema = DB_SCHEMAS[0] if len(DB_SCHEMAS) >= 1 else None
        if not prod_schema:
            print("No product schema configured.")
            return False
        conn = dbm.get_conn(prod_schema)
        cur = conn.cursor()
        for it in cart_items:
            try:
                cur.execute("UPDATE products SET qty = GREATEST(qty - %s, 0) WHERE name = %s", (it['qty'], it['name']))
                if cur.rowcount == 0:
                    # fallback column name
                    cur.execute("UPDATE products SET stock = GREATEST(stock - %s, 0) WHERE name = %s",
                                (it['qty'], it['name']))
            except Exception as ie:
                print("reduce_stock_in_db inner error for", it['name'], ie)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("reduce_stock_in_db error:", e)
        return False


def generate_pdf_bill_from_lines(fname_pdf, lines, upi_text=None, attach_qr=True):
    try:
        if canvas is not None:
            c = canvas.Canvas(fname_pdf, pagesize=A4)
            w, h = A4
            margin = 20 * mm
            x = margin
            y = h - margin

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(w / 2, y, "D-MART BILL")
            y -= 10 * mm

            # Bill details
            c.setFont("Helvetica", 10)
            for ln in lines:
                if y < margin + 50:
                    c.showPage()
                    y = h - margin
                    c.setFont("Helvetica", 10)
                c.drawString(x, y, ln)
                y -= 5 * mm

            # UPI QR Code
            if upi_text and attach_qr and qrcode is not None:
                try:
                    qr_img = qrcode.make(upi_text)
                    qr_path = os.path.join(BILLS_DIR, "qr_temp.jpg")
                    qr_img.save(qr_path)

                    # Position QR code at bottom
                    qr_size = 60 * mm
                    qr_x = w - margin - qr_size
                    qr_y = margin

                    c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)

                    # UPI text below QR
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(qr_x, qr_y - 8, "Scan to Pay via UPI")
                    c.setFont("Helvetica", 8)
                    c.drawString(qr_x, qr_y - 16, upi_text)

                    try:
                        os.remove(qr_path)
                    except:
                        pass
                except Exception as e:
                    print("QR generation failed:", e)

            c.save()
            return True
        else:
            # PIL fallback to PDF
            try:
                from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageFont as PILImageFont
                font = None
                try:
                    font = PILImageFont.truetype("DejaVuSans.ttf", 12)
                except Exception:
                    font = PILImageFont.load_default()
                line_h = 16
                page_w, page_h = 595, 842
                img = PILImage.new("RGB", (page_w, page_h), "white")
                draw = PILImageDraw.Draw(img)
                y = 20
                for ln in lines:
                    draw.text((20, y), ln, fill="black", font=font)
                    y += line_h
                    if y > page_h - 120:
                        break
                if upi_text:
                    draw.text((20, page_h - 100), "UPI: " + upi_text, fill="black", font=font)
                img.save(fname_pdf, "PDF", resolution=100.0, save_all=True)
                return True
            except Exception as e:
                print("generate_pdf_bill PIL fallback error:", e)
                return False
    except Exception as e:
        print("generate_pdf_bill error:", e)
        return False


def record_return(bill_no, product_name, qty, refund_amount, reason=None):
    """Insert a return record and increment stock."""
    try:
        schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
        conn = dbm.get_conn(schema)
        cur = conn.cursor()
        cur.execute("INSERT INTO returns (bill_no, product_name, qty, refund_amount, reason) VALUES (%s,%s,%s,%s,%s)",
                    (bill_no, product_name, qty, refund_amount, reason))
        conn.commit()
        cur.close()
        conn.close()
        # increase stock in product schema
        prod_schema = DB_SCHEMAS[0] if len(DB_SCHEMAS) >= 1 else None
        if prod_schema:
            c2 = dbm.get_conn(prod_schema).cursor()
            try:
                c2.execute("UPDATE products SET qty = qty + %s WHERE name = %s", (qty, product_name))
            except Exception:
                try:
                    c2.execute("UPDATE products SET stock = stock + %s WHERE name = %s", (qty, product_name))
                except Exception:
                    pass
            c2.connection.commit()
            c2.close()
        return True
    except Exception as e:
        print("record_return error:", e)
        return False


def get_all_bills():
    """Get all bills from database"""
    try:
        schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
        conn = dbm.get_conn(schema)
        cur = conn.cursor()
        cur.execute("""
            SELECT bill_no, customer_name, subtotal, gst, total, payment_type, 
                   DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as bill_date 
            FROM sales 
            ORDER BY created_at DESC
        """)
        bills = cur.fetchall()
        cur.close()
        conn.close()
        return bills
    except Exception as e:
        print("get_all_bills error:", e)
        return []


# Email sending function
def send_feedback_email(subject, message, recipient_email=None):
    """Send feedback email to admin"""
    try:
        if not EMAIL_CONFIG["sender_email"] or EMAIL_CONFIG["sender_email"] == "dmart.billing@gmail.com":
            return False, "Email configuration not set up"

        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = recipient_email or EMAIL_CONFIG["admin_email"]
        msg['Subject'] = f"D-Mart Feedback: {subject}"

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG["sender_email"], msg['To'], text)
        server.quit()

        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"


# ---------------- Main App (DMartApp) ----------------
class DMartApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Advanced D-Mart Billing (MySQL)")
        try:
            self.state("zoomed")
        except:
            pass
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.cart = []
        self.logged_user = None
        self._img_cache = {}
        self.build_login()

    # ---------------- Enhanced Login with Registration ----------------
    def build_login(self):
        for w in self.winfo_children():
            w.destroy()

        if PIL_AVAILABLE:
            try:
                bg_img_path = "dmart11.jpg"
                bg_img = Image.open(bg_img_path)
                bg_ctk_img = CTkImage(light_image=bg_img, size=(1206, 790))
                bg_label = ctk.CTkLabel(self, image=bg_ctk_img, text="")
                bg_label.image = bg_ctk_img
                bg_label.place(x=927, y=400, anchor="center")
            except Exception as e:
                print("Background image load failed:", e)

        left = ctk.CTkFrame(self, fg_color="#1E8C50", width=320, corner_radius=0)
        left.pack(side="left", fill="y")

        if PIL_AVAILABLE:
            pil_logo = make_pil_placeholder("D-MART", size=(120, 120), bg=(255, 255, 255), accent=(34, 139, 34))
            logo_img = pil_to_ctkimage(pil_logo, size=(100, 100)) if pil_logo else None
            if logo_img:
                lbl_logo = ctk.CTkLabel(left, image=logo_img, text="")
                lbl_logo.image = logo_img
                lbl_logo.place(relx=0.5, rely=0.22, anchor="center")
            else:
                ctk.CTkLabel(left, text="D-MART", text_color="white", font=("Arial Black", 36)).place(relx=0.5,
                                                                                                      rely=0.22,
                                                                                                      anchor="center")
        else:
            ctk.CTkLabel(left, text="D-MART", text_color="white", font=("Arial Black", 36)).place(relx=0.5, rely=0.22,
                                                                                                  anchor="center")

        ctk.CTkLabel(left, text="Smart Billing System", text_color="white").place(relx=0.5, rely=0.3, anchor="center")

        outer_frame = ctk.CTkFrame(
            self,
            width=520,
            height=440,
            corner_radius=10,
            border_width=3,
            border_color="#2BAE66",
            fg_color="white"
        )
        outer_frame.place(relx=0.62, rely=0.6, anchor="center")

        ctk.CTkLabel(outer_frame, text="🔐 D-MART Login", font=("Arial", 22, "bold"), text_color="#2BAE66").pack(
            pady=(18, 12))

        self.login_user_entry = ctk.CTkEntry(outer_frame, placeholder_text="Username", width=370, height=42,
                                             corner_radius=6)
        self.login_user_entry.pack(pady=(10, 8), padx=10)

        self.login_pass_entry = ctk.CTkEntry(outer_frame, placeholder_text="Password", show="*", width=370, height=42,
                                             corner_radius=6)
        self.login_pass_entry.pack(pady=(8, 16), padx=10)

        login_btn_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        login_btn_frame.pack(pady=(8, 12))

        ctk.CTkButton(login_btn_frame, text="Login", fg_color="#2BAE66", hover_color="#239d59",
                      width=180, height=38, corner_radius=6, command=self.do_login).pack(side="left", padx=5)

        ctk.CTkButton(login_btn_frame, text="Register", fg_color="#3B82F6", hover_color="#2563EB",
                      width=180, height=38, corner_radius=6, command=self.open_registration_window).pack(side="left",
                                                                                                         padx=5)

        ctk.CTkLabel(
            outer_frame,
            text="Default credentials: kartik / 1234",
            font=("Arial", 10, "italic"),
            text_color="gray"
        ).pack(pady=5)

        # Add feedback/contact button
        feedback_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        feedback_frame.pack(pady=(10, 5))

        ctk.CTkButton(feedback_frame, text="Feedback/Contact Us", fg_color="#9C27B0", hover_color="#7B1FA2",
                      width=180, height=32, corner_radius=6, command=self.open_feedback_window).pack(side="left",
                                                                                                     padx=5)

        ctk.CTkButton(feedback_frame, text="View Feedback", fg_color="#FF9800", hover_color="#F57C00",
                      width=180, height=32, corner_radius=6, command=self.open_feedback_list_window).pack(side="left",
                                                                                                          padx=5)

    def do_login(self):
        u = self.login_user_entry.get().strip()
        p = self.login_pass_entry.get().strip()

        # Check database for user
        user = dbm.check_user_credentials(u, p)

        if user:
            self.logged_user = u
            self.build_main_ui()
            self.show_dashboard()
        else:
            messagebox.showerror("Login failed", "Invalid username or password")

    # ---------------- Registration Window ----------------
    def open_registration_window(self):
        reg_window = ctk.CTkToplevel(self)
        reg_window.title("User Registration")
        reg_window.geometry("500x550")
        reg_window.grab_set()
        reg_window.transient(self)

        # Center the window
        reg_window.update_idletasks()
        width = reg_window.winfo_width()
        height = reg_window.winfo_height()
        x = (reg_window.winfo_screenwidth() // 2) - (width // 2)
        y = (reg_window.winfo_screenheight() // 2) - (height // 2)
        reg_window.geometry(f'{width}x{height}+{x}+{y}')

        # Registration form
        ctk.CTkLabel(reg_window, text="🔐 New User Registration",
                     font=("Arial", 20, "bold"), text_color="#2BAE66").pack(pady=(20, 10))

        # Username
        ctk.CTkLabel(reg_window, text="Username:", anchor="w", font=("Arial", 12)).pack(fill="x", padx=40, pady=(10, 0))
        username_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter username", width=400, height=40)
        username_entry.pack(pady=(5, 10), padx=40)

        # Password
        ctk.CTkLabel(reg_window, text="Password:", anchor="w", font=("Arial", 12)).pack(fill="x", padx=40, pady=(5, 0))
        password_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter password", show="*", width=400, height=40)
        password_entry.pack(pady=(5, 10), padx=40)

        # Confirm Password
        ctk.CTkLabel(reg_window, text="Confirm Password:", anchor="w", font=("Arial", 12)).pack(fill="x", padx=40,
                                                                                                pady=(5, 0))
        confirm_password_entry = ctk.CTkEntry(reg_window, placeholder_text="Confirm password", show="*", width=400,
                                              height=40)
        confirm_password_entry.pack(pady=(5, 10), padx=40)

        # Email (optional)
        ctk.CTkLabel(reg_window, text="Email (optional):", anchor="w", font=("Arial", 12)).pack(fill="x", padx=40,
                                                                                                pady=(5, 0))
        email_entry = ctk.CTkEntry(reg_window, placeholder_text="Enter email address", width=400, height=40)
        email_entry.pack(pady=(5, 20), padx=40)

        def register_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm_password = confirm_password_entry.get().strip()
            email = email_entry.get().strip()

            # Validation
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required!")
                return

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                return

            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters!")
                return

            # Register user
            success, message = dbm.register_user(username, password, email)

            if success:
                messagebox.showinfo("Success", message)
                reg_window.destroy()
            else:
                messagebox.showerror("Registration Failed", message)

        # Buttons
        btn_frame = ctk.CTkFrame(reg_window, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Register", fg_color="#2BAE66", hover_color="#239d59",
                      width=180, height=40, corner_radius=8, command=register_user).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#E05656", hover_color="#C53030",
                      width=180, height=40, corner_radius=8, command=reg_window.destroy).pack(side="left", padx=10)

    # ---------------- Feedback/Contact Us Window ----------------
    def open_feedback_window(self):
        feedback_window = ctk.CTkToplevel(self)
        feedback_window.title("Feedback / Contact Us")
        feedback_window.geometry("600x700")
        feedback_window.grab_set()

        # Center the window
        feedback_window.update_idletasks()
        width = feedback_window.winfo_width()
        height = feedback_window.winfo_height()
        x = (feedback_window.winfo_screenwidth() // 2) - (width // 2)
        y = (feedback_window.winfo_screenheight() // 2) - (height // 2)
        feedback_window.geometry(f'{width}x{height}+{x}+{y}')

        # Title
        ctk.CTkLabel(feedback_window, text="📝 Feedback / Contact Us",
                     font=("Arial", 22, "bold"), text_color="#2BAE66").pack(pady=(20, 10))

        # Contact Information Frame
        contact_frame = ctk.CTkFrame(feedback_window, corner_radius=10)
        contact_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(contact_frame, text="📞 Contact Information",
                     font=("Arial", 16, "bold")).pack(pady=(10, 5))

        contact_info = """
        D-Mart Store
        Address: Satara
        Phone: +91 8956287267
        Email: support@dmart.com
        Hours: Mon-Sun: 8:00 AM - 10:00 PM
        """

        ctk.CTkLabel(contact_frame, text=contact_info, font=("Arial", 12),
                     justify="left").pack(pady=10, padx=20)

        # Feedback Form Frame
        form_frame = ctk.CTkFrame(feedback_window, corner_radius=10)
        form_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(form_frame, text="✍️ Send us your feedback",
                     font=("Arial", 16, "bold")).pack(pady=(10, 5))

        # Name
        ctk.CTkLabel(form_frame, text="Your Name:", anchor="w",
                     font=("Arial", 12)).pack(fill="x", padx=20, pady=(10, 0))
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your name",
                                  width=500, height=40)
        name_entry.pack(pady=(5, 10), padx=20)

        # Email
        ctk.CTkLabel(form_frame, text="Your Email:", anchor="w",
                     font=("Arial", 12)).pack(fill="x", padx=20, pady=(5, 0))
        email_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your email",
                                   width=500, height=40)
        email_entry.pack(pady=(5, 10), padx=20)

        # Feedback Type
        ctk.CTkLabel(form_frame, text="Feedback Type:", anchor="w",
                     font=("Arial", 12)).pack(fill="x", padx=20, pady=(5, 0))
        feedback_type = ctk.CTkComboBox(form_frame, values=["General Feedback", "Complaint",
                                                            "Suggestion", "Bug Report", "Other"],
                                        width=500, height=40)
        feedback_type.pack(pady=(5, 10), padx=20)
        feedback_type.set("General Feedback")

        # Rating
        ctk.CTkLabel(form_frame, text="Rating (1-5):", anchor="w",
                     font=("Arial", 12)).pack(fill="x", padx=20, pady=(5, 0))
        rating_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        rating_frame.pack(pady=(5, 10), padx=20)

        rating_var = ctk.IntVar(value=5)
        for i in range(1, 6):
            ctk.CTkRadioButton(rating_frame, text=str(i), variable=rating_var,
                               value=i, font=("Arial", 12)).pack(side="left", padx=10)

        # Message
        ctk.CTkLabel(form_frame, text="Your Message:", anchor="w",
                     font=("Arial", 12)).pack(fill="x", padx=20, pady=(10, 0))
        message_text = ctk.CTkTextbox(form_frame, width=500, height=150)
        message_text.pack(pady=(5, 15), padx=20)

        def submit_feedback():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            ftype = feedback_type.get()
            rating = rating_var.get()
            message = message_text.get("1.0", "end").strip()

            if not name:
                messagebox.showerror("Error", "Please enter your name!")
                return

            if not message:
                messagebox.showerror("Error", "Please enter your message!")
                return

            # Save to database
            success = dbm.add_feedback(name, email, ftype, message, rating)

            # Save to local file as backup
            try:
                contacts = load_contacts()
                feedback_data = {
                    "name": name,
                    "email": email,
                    "type": ftype,
                    "rating": rating,
                    "message": message,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                contacts.append(feedback_data)
                save_contacts(contacts)
            except Exception as e:
                print("Error saving feedback locally:", e)

            # Send email notification
            email_subject = f"{ftype} from {name}"
            email_message = f"""
            Name: {name}
            Email: {email}
            Type: {ftype}
            Rating: {rating}/5
            Message:
            {message}

            Received: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """

            email_success, email_msg = send_feedback_email(email_subject, email_message)

            if success:
                messagebox.showinfo("Success",
                                    f"Thank you for your feedback!\n\n{email_msg if email_success else 'Feedback saved locally.'}")
                feedback_window.destroy()
            else:
                messagebox.showwarning("Partial Success",
                                       "Feedback saved locally but not in database.")

        # Buttons
        btn_frame = ctk.CTkFrame(feedback_window, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Submit Feedback", fg_color="#2BAE66", hover_color="#239d59",
                      width=200, height=45, corner_radius=8, font=("Arial", 14, "bold"),
                      command=submit_feedback).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#E05656", hover_color="#C53030",
                      width=200, height=45, corner_radius=8, font=("Arial", 14),
                      command=feedback_window.destroy).pack(side="left", padx=10)

    # ---------------- Feedback List Window (Admin View) ----------------
    def open_feedback_list_window(self):
        feedback_list_window = ctk.CTkToplevel(self)
        feedback_list_window.title("Feedback List")
        feedback_list_window.geometry("1000x600")
        feedback_list_window.grab_set()

        # Title
        ctk.CTkLabel(feedback_list_window, text="📋 Feedback List",
                     font=("Arial", 22, "bold"), text_color="#2BAE66").pack(pady=(15, 10))

        # Search Frame
        search_frame = ctk.CTkFrame(feedback_list_window, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(side="left", padx=5)
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search feedback...", width=300)
        search_entry.pack(side="left", padx=5)

        def refresh_feedback():
            # Clear tree
            for item in tree.get_children():
                tree.delete(item)

            # Get feedback from database
            feedback_list = dbm.get_feedback_list()

            # Also get from local file
            local_feedback = load_contacts()

            # Add database feedback
            for fb in feedback_list:
                tree.insert("", "end", values=(
                    f"DB-{fb['id']}",
                    fb['username'],
                    fb['email'] or "N/A",
                    fb['feedback_type'],
                    fb['rating'],
                    fb['message'][:50] + "..." if len(fb['message']) > 50 else fb['message'],
                    fb['created_at'],
                    fb['status']
                ), tags=('database',))

            # Add local feedback
            for i, fb in enumerate(local_feedback):
                tree.insert("", "end", values=(
                    f"LOCAL-{i + 1}",
                    fb['name'],
                    fb['email'] or "N/A",
                    fb['type'],
                    fb['rating'],
                    fb['message'][:50] + "..." if len(fb['message']) > 50 else fb['message'],
                    fb['date'],
                    "Local"
                ), tags=('local',))

        ctk.CTkButton(search_frame, text="Refresh", fg_color="#3B82F6", hover_color="#2563EB",
                      command=refresh_feedback).pack(side="left", padx=5)

        # Treeview for feedback
        tree_frame = ctk.CTkFrame(feedback_list_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Email", "Type", "Rating", "Message", "Date", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Message" else 200)

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Configure tags for different sources
        tree.tag_configure('database', background='#e8f5e9')
        tree.tag_configure('local', background='#fff3e0')

        # Button Frame
        button_frame = ctk.CTkFrame(feedback_list_window, fg_color="transparent")
        button_frame.pack(pady=10)

        def view_selected_feedback():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a feedback entry to view.")
                return

            item = tree.item(selection[0])
            values = item['values']

            # Show detailed view
            detail_window = ctk.CTkToplevel(feedback_list_window)
            detail_window.title(f"Feedback Details - {values[0]}")
            detail_window.geometry("600x500")

            ctk.CTkLabel(detail_window, text="📄 Feedback Details",
                         font=("Arial", 20, "bold")).pack(pady=15)

            details = f"""
            ID: {values[0]}
            Name: {values[1]}
            Email: {values[2]}
            Type: {values[3]}
            Rating: {values[4]}/5
            Date: {values[6]}
            Status: {values[7]}

            Full Message:
            {self.get_full_message(values[0], values[5])}
            """

            text_widget = ctk.CTkTextbox(detail_window, width=550, height=350)
            text_widget.pack(padx=20, pady=10)
            text_widget.insert("1.0", details)
            text_widget.configure(state="disabled")

            ctk.CTkButton(detail_window, text="Close",
                          command=detail_window.destroy).pack(pady=10)

        def delete_selected_feedback():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a feedback entry to delete.")
                return

            item = tree.item(selection[0])
            fb_id = item['values'][0]

            if messagebox.askyesno("Confirm Delete", f"Delete feedback {fb_id}?"):
                if fb_id.startswith("DB-"):
                    # Delete from database
                    db_id = fb_id.split("-")[1]
                    success = dbm.delete_feedback(db_id)
                    if success:
                        tree.delete(selection[0])
                        messagebox.showinfo("Success", "Feedback deleted from database.")
                    else:
                        messagebox.showerror("Error", "Failed to delete from database.")
                else:
                    # Delete from local file
                    local_id = int(fb_id.split("-")[1]) - 1
                    contacts = load_contacts()
                    if 0 <= local_id < len(contacts):
                        del contacts[local_id]
                        save_contacts(contacts)
                        tree.delete(selection[0])
                        messagebox.showinfo("Success", "Feedback deleted from local storage.")

        def export_feedback():
            # Export feedback to CSV
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                try:
                    feedback_list = dbm.get_feedback_list()
                    local_feedback = load_contacts()

                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Source,ID,Name,Email,Type,Rating,Message,Date,Status\n")

                        # Write database feedback
                        for fb in feedback_list:
                            f.write(f"Database,{fb['id']},{fb['username']},{fb['email'] or ''},"
                                    f"{fb['feedback_type']},{fb['rating']},\"{fb['message']}\","
                                    f"{fb['created_at']},{fb['status']}\n")

                        # Write local feedback
                        for i, fb in enumerate(local_feedback):
                            f.write(f"Local,{i + 1},{fb['name']},{fb['email'] or ''},"
                                    f"{fb['type']},{fb['rating']},\"{fb['message']}\","
                                    f"{fb['date']},Local\n")

                    messagebox.showinfo("Success", f"Feedback exported to {filename}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

        ctk.CTkButton(button_frame, text="View Details", fg_color="#2BAE66",
                      command=view_selected_feedback).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Delete Selected", fg_color="#E05656",
                      command=delete_selected_feedback).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Export to CSV", fg_color="#3B82F6",
                      command=export_feedback).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Close", fg_color="#6B7280",
                      command=feedback_list_window.destroy).pack(side="left", padx=5)

        # Load initial data
        refresh_feedback()

    def get_full_message(self, fb_id, preview):
        """Get full message for a feedback entry"""
        if fb_id.startswith("DB-"):
            # Get from database
            try:
                db_id = fb_id.split("-")[1]
                schema = DB_SCHEMAS[6] if len(DB_SCHEMAS) >= 7 else DB_SCHEMAS[0]
                conn = dbm.get_conn(schema)
                cur = conn.cursor()
                cur.execute("SELECT message FROM feedback WHERE id = %s", (db_id,))
                result = cur.fetchone()
                cur.close()
                conn.close()
                return result['message'] if result else preview
            except:
                return preview
        else:
            # Get from local file
            local_id = int(fb_id.split("-")[1]) - 1
            contacts = load_contacts()
            if 0 <= local_id < len(contacts):
                return contacts[local_id]['message']
            return preview

    # ---------------- Enhanced Main UI with Feedback Button ----------------
    def build_main_ui(self):
        for w in self.winfo_children(): w.destroy()
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text="D-MART", font=("Arial", 20, "bold")).pack(pady=(18, 6))
        ctk.CTkLabel(self.sidebar, text=f"User: {self.logged_user}", font=("Arial", 11)).pack(pady=(0, 8))

        btn_kw = {"width": 200, "corner_radius": 8}
        ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="#2BAE66", command=self.show_dashboard, **btn_kw).pack(
            pady=8)
        ctk.CTkButton(self.sidebar, text="Products", fg_color="#2BAE66", command=self.open_categories_window,
                      **btn_kw).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="Customers", fg_color="#2BAE66", command=self.open_customers_window,
                      **btn_kw).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="Generate Bill", fg_color="#2BAE66", command=self.generate_report_from_cart,
                      **btn_kw).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="Past Bills", fg_color="#2BAE66", command=self.open_past_bills_window,
                      **btn_kw).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="Admin Panel", fg_color="#2BAE66", command=self.open_admin_panel,
                      **btn_kw).pack(pady=8)
        ctk.CTkButton(self.sidebar, text="Returns", fg_color="#2BAE66", command=self.open_returns_window,
                      **btn_kw).pack(pady=8)

        # NEW: Feedback/Contact Us button
        ctk.CTkButton(self.sidebar, text="Feedback/Contact Us", fg_color="#9C27B0",
                      command=self.open_feedback_window, **btn_kw).pack(pady=8)

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#E05656", command=self.logout, **btn_kw).pack(
            side="bottom", pady=18)

        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        self.cart_panel = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color="#F7F8F9")
        self.cart_panel.pack(side="right", fill="y")
        ctk.CTkLabel(self.cart_panel, text="Cart", font=("Arial", 16, "bold")).pack(pady=10)
        self.cart_textbox = ctk.CTkTextbox(self.cart_panel, width=320, height=420, state="disabled")
        self.cart_textbox.pack(padx=10, pady=(6, 8))
        self.subtotal_var = ctk.StringVar(value="Subtotal: ₹0.00")
        self.gst_var = ctk.StringVar(value="GST (5%): ₹0.00")
        self.total_var = ctk.StringVar(value="Total: ₹0.00")
        ctk.CTkLabel(self.cart_panel, textvariable=self.subtotal_var).pack(pady=(4, 0))
        ctk.CTkLabel(self.cart_panel, textvariable=self.gst_var).pack()
        ctk.CTkLabel(self.cart_panel, textvariable=self.total_var, font=("Arial", 12, "bold")).pack(pady=(2, 12))
        ctk.CTkButton(self.cart_panel, text="Generate Bill", fg_color="#2BAE66", command=self.generate_report_from_cart,
                      width=300).pack(pady=6)
        ctk.CTkButton(self.cart_panel, text="Clear Cart", fg_color="#E05656", command=self.clear_cart, width=300).pack(
            pady=(4, 12))
        ctk.CTkButton(self.cart_panel, text="Remove Selected", fg_color="#E05656",
                      command=self.remove_selected_cart_item, width=300).pack(pady=(0, 12))

    # ---------------- Dashboard ----------------
    def show_dashboard(self):
        for w in self.main_content.winfo_children(): w.destroy()
        from PIL import Image, ImageTk
        try:
            bg_image = Image.open("dmart1234.png")
            bg_image = bg_image.resize((1160, 690))
            bordered_image = ImageOps.expand(bg_image, border=5, fill="black")

            bg_ctk_image = ctk.CTkImage(light_image=bordered_image, dark_image=bordered_image, size=(1140, 670))

            bg_photo = ImageTk.PhotoImage(bg_image)

            bg_label = ctk.CTkLabel(self.main_content, image=bg_photo, text="")
            bg_label.image = bg_photo
            bg_label.place(relx=0.5, rely=0.6, anchor="center")
        except Exception as e:
            print("Dashboard background image error:", e)

        ctk.CTkLabel(self.main_content, text="Welcome to D-Mart Dashboard 🛒", font=("Arial", 26, "bold"),
                     text_color="#228B22").pack(pady=(24, 12))
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="#E8F5E9", corner_radius=12)
        stats_frame.pack(padx=40, pady=12, fill="x")

        total_products = sum(len(v) for v in categories.values())
        total_customers = len(dbm.list_customers())
        total_sales = 0.0
        for fname in os.listdir(BILLS_DIR):
            if fname.endswith(".txt"):
                total_sales += parse_total_from_bill_file(os.path.join(BILLS_DIR, fname))

        stat_text = f"Total Products: {total_products}    |    Total Customers: {total_customers}    |    Total Sales: ₹{total_sales:.2f}"
        ctk.CTkLabel(stats_frame, text=stat_text, font=("Arial", 14)).pack(pady=14, padx=12)

        ctk.CTkLabel(self.main_content,
                     text="Use 'Products' to browse categories → add to cart → use 'Generate Bill' to create bill.",
                     font=("Arial", 12)).pack(pady=(12, 0))

    def open_categories_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Categories")
        win.geometry("1000x700")
        win.grab_set()
        ctk.CTkLabel(win, text="Categories", font=("Arial", 20, "bold")).pack(pady=(12, 8))
        grid_parent = ctk.CTkFrame(win)
        grid_parent.pack(fill="both", expand=True, padx=12, pady=8)
        cols = 4
        grid = ctk.CTkFrame(grid_parent)
        grid.pack(fill="both", expand=True)
        for i in range(cols):
            grid.grid_columnconfigure(i, weight=1, uniform="catcol")
        row = 0;
        col = 0
        for cat in categories.keys():
            card = ctk.CTkFrame(grid, corner_radius=8, fg_color="white")
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            first_prod = categories[cat][0] if categories[cat] else None
            img_url = first_prod.get("img") if isinstance(first_prod, dict) else None
            pil_img = None
            if img_url:
                key = f"cat_{cat}"
                if key in self._img_cache:
                    img = self._img_cache[key]
                else:
                    pil_img = load_image_from_url(img_url, size=(150, 90))
                    if pil_img is None:
                        pil_img = make_pil_placeholder(cat, size=(150, 90))
                    img = pil_to_ctkimage(pil_img, size=(120, 80))
                    self._img_cache[key] = img
            else:
                pil_img = make_pil_placeholder(cat, size=(150, 90))
                img = pil_to_ctkimage(pil_img, size=(120, 80))
            if img:
                lbl = ctk.CTkLabel(card, image=img, text="")
                lbl.image = img
                lbl.pack(pady=(12, 4))

            ctk.CTkLabel(card, text=cat, font=("Arial", 12, "bold")).pack(pady=(4, 8))
            ctk.CTkButton(card, text="Open", fg_color="#2BAE66", width=120,
                          command=lambda c=cat: self.open_products_window(c)).pack(pady=(0, 12))
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def open_products_window(self, category):
        win = ctk.CTkToplevel(self)
        win.title(f"Products - {category}")
        win.geometry("1200x780")
        win.grab_set()
        ctk.CTkLabel(win, text=f"{category} - Products", font=("Arial", 18, "bold")).pack(pady=(12, 8))

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        inner = ctk.CTkFrame(scroll)
        inner.pack(fill="both", expand=True, padx=6, pady=6)

        plist = list(categories.get(category, []))
        cols = 3
        r = 0;
        c = 0
        for i in range(cols):
            inner.grid_columnconfigure(i, weight=1, uniform="prodcol")

        for prod in plist:
            pname = prod.get("name", "Unnamed")
            pprice = float(prod.get("price", 0.0))
            img_key = f"{category}_{pname}"
            if img_key in self._img_cache:
                img = self._img_cache[img_key]
            else:
                url = prod.get("img")
                pil_img = None
                if url:
                    pil_img = load_image_from_url(url, size=(220, 120))
                if pil_img is None:
                    pil_img = make_pil_placeholder(pname, size=(220, 120))
                img = pil_to_ctkimage(pil_img, size=(220, 120)) if pil_img is not None else None
                self._img_cache[img_key] = img

            card = ctk.CTkFrame(inner, corner_radius=8, fg_color="white")
            card.grid(row=r, column=c, padx=12, pady=12, sticky="n")

            if img:
                lbl = ctk.CTkLabel(card, image=img, text="")
                lbl.image = img
                lbl.pack(pady=(10, 6))
            else:
                ctk.CTkLabel(card, text=pname.split()[0], font=("Arial", 11, "bold")).pack(pady=(12, 6))

            ctk.CTkLabel(card, text=pname, font=("Arial", 12, "bold"), wraplength=240).pack(pady=(0, 6))
            mfg = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            exp = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
            price_bar = ctk.CTkFrame(card, fg_color="#e9eef6", corner_radius=6)
            price_bar.pack(fill="x", padx=8, pady=(4, 6))
            ctk.CTkLabel(price_bar, text=f"₹ {pprice:.2f}", font=("Arial", 11, "bold")).pack(padx=6, pady=6)
            ctk.CTkLabel(card, text=f"Mfg: {mfg}   Exp: {exp}", font=("Arial", 10)).pack(pady=(2, 4))

            qty_var = ctk.IntVar(value=1)
            sp = ttk.Spinbox(card, from_=1, to=100, width=5, textvariable=qty_var)
            sp.pack(pady=(2, 4))

            ctk.CTkButton(card, text="Add to Cart", fg_color="#2BAE66",
                          command=lambda cat=category, pd=prod, qv=qty_var: self.add_to_cart(cat, pd, qv.get())).pack(
                pady=(6, 10))

            c += 1
            if c >= cols:
                c = 0
                r += 1

    # ---------------- Add to cart (with per-item discount prompt) ----------------
    def add_to_cart(self, category, product_dict, qty):
        name = product_dict.get("name", "Unnamed")
        price = float(product_dict.get("price", 0.0))
        qty = int(qty)
        stock = product_dict.get("qty")
        if stock is not None and qty > stock:
            messagebox.showwarning("Stock", f"Only {stock} available for {name}.")
            return

        # Ask for per-item discount percentage (0-100) — optional
        try:
            disc = simpledialog.askfloat("Discount", f"Enter discount % for {name} (0 for none):", parent=self,
                                         minvalue=0.0, maxvalue=100.0)
        except Exception:
            disc = 0.0
        if disc is None:
            disc = 0.0
        disc = float(disc)

        # If item already in cart, just update qty and reuse discount
        for it in self.cart:
            if it["name"] == name:
                it["qty"] += qty
                # keep the same discount
                self.refresh_cart_view()
                messagebox.showinfo("Cart", f"Updated {name} qty → {it['qty']}")
                return

        self.cart.append({"name": name, "price": price, "qty": qty, "discount_percent": disc})
        self.refresh_cart_view()
        messagebox.showinfo("Cart", f"Added {name} x{qty} (discount {disc}%)")

    # ---------------- Refresh cart view (shows discount-aware totals) ----------------
    def refresh_cart_view(self):
        self.cart_textbox.configure(state="normal")
        self.cart_textbox.delete("1.0", "end")
        subtotal = 0.0
        for idx, it in enumerate(self.cart, start=1):
            gross = it['qty'] * it['price']
            disc = float(it.get('discount_percent', 0) or 0)
            net = round(gross * (1 - disc / 100.0), 2)
            line = f"{idx}. {it['name']} x{it['qty']}  @₹{it['price']:.2f}  disc:{disc:.1f}%  = ₹{net:.2f}\n"
            self.cart_textbox.insert("end", line)
            subtotal += net
        self.cart_textbox.configure(state="disabled")
        gst = round(subtotal * 0.05, 2)
        total = round(subtotal + gst, 2)
        self.subtotal_var.set(f"Subtotal: ₹{subtotal:.2f}")
        self.gst_var.set(f"GST (5%): ₹{gst:.2f}")
        self.total_var.set(f"Total: ₹{total:.2f}")

    # ---------------- Remove / Clear cart ----------------
    def remove_selected_cart_item(self):
        if not self.cart:
            return
        idx = simpledialog.askinteger("Remove", "Enter item number to remove (as shown in cart):", parent=self)
        if idx is None:
            return
        if not (1 <= idx <= len(self.cart)):
            messagebox.showwarning("Invalid", "Invalid item number.")
            return
        removed = self.cart.pop(idx - 1)
        messagebox.showinfo("Removed", f"Removed {removed['name']}")
        self.refresh_cart_view()

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear cart", "Clear all items from cart?"):
            self.cart = []
            self.refresh_cart_view()

    # ---------------- Past Bills Window ----------------
    def open_past_bills_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Past Bills")
        win.geometry("1000x600")
        win.grab_set()

        ctk.CTkLabel(win, text="Past Bills History", font=("Arial", 20, "bold")).pack(pady=(12, 8))

        # Search frame
        search_frame = ctk.CTkFrame(win)
        search_frame.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(search_frame, text="Search Bill No:").pack(side="left", padx=(10, 5))
        search_entry = ctk.CTkEntry(search_frame, width=200)
        search_entry.pack(side="left", padx=5)

        def search_bills():
            search_term = search_entry.get().strip().lower()
            for row in tree.get_children():
                tree.delete(row)
            bills = get_all_bills()
            for bill in bills:
                if search_term in bill['bill_no'].lower():
                    tree.insert("", "end", values=(
                        bill['bill_no'],
                        bill['bill_date'],
                        f"₹{bill['subtotal']:.2f}",
                        f"₹{bill['gst']:.2f}",
                        f"₹{bill['total']:.2f}",
                        bill['payment_type']
                    ))

        ctk.CTkButton(search_frame, text="Search", command=search_bills).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Show All", command=self.load_bills_to_tree).pack(side="left", padx=5)

        # Treeview for bills
        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        columns = ("bill_no", "date", "subtotal", "gst", "total", "payment")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        # Configure columns
        tree.heading("bill_no", text="Bill No")
        tree.heading("date", text="Date & Time")
        tree.heading("subtotal", text="Subtotal")
        tree.heading("gst", text="GST")
        tree.heading("total", text="Total")
        tree.heading("payment", text="Payment")

        tree.column("bill_no", width=180)
        tree.column("date", width=150)
        tree.column("subtotal", width=100)
        tree.column("gst", width=80)
        tree.column("total", width=100)
        tree.column("payment", width=100)

        tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=12, pady=8)

        def view_bill_details():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Select Bill", "Please select a bill to view details")
                return
            bill_no = tree.item(selection[0])['values'][0]
            self.show_bill_details(bill_no)

        ctk.CTkButton(btn_frame, text="View Bill Details", command=view_bill_details).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.load_bills_to_tree).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=5)

        self.load_bills_to_tree()

    def load_bills_to_tree(self):
        # Clear existing items
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Treeview):
                        for row in child.get_children():
                            child.delete(row)

        # Load bills from database
        bills = get_all_bills()
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Treeview):
                        for bill in bills:
                            child.insert("", "end", values=(
                                bill['bill_no'],
                                bill['bill_date'],
                                f"₹{bill['subtotal']:.2f}",
                                f"₹{bill['gst']:.2f}",
                                f"₹{bill['total']:.2f}",
                                bill['payment_type']
                            ))

    def show_bill_details(self, bill_no):
        """Show detailed bill information"""
        try:
            schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
            conn = dbm.get_conn(schema)
            cur = conn.cursor()

            # Get sale info
            cur.execute("SELECT * FROM sales WHERE bill_no = %s", (bill_no,))
            sale = cur.fetchone()

            # Get sale items
            cur.execute("""
                SELECT si.product_name, si.qty, si.price, si.discount_percent, si.amount 
                FROM sale_items si 
                JOIN sales s ON si.sale_id = s.id 
                WHERE s.bill_no = %s
            """, (bill_no,))
            items = cur.fetchall()

            cur.close()
            conn.close()

            if not sale:
                messagebox.showerror("Error", "Bill not found")
                return

            # Create bill details window
            details_win = ctk.CTkToplevel(self)
            details_win.title(f"Bill Details - {bill_no}")
            details_win.geometry("700x500")
            details_win.grab_set()

            # Bill header
            header_frame = ctk.CTkFrame(details_win)
            header_frame.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(header_frame, text=f"BILL NO: {bill_no}", font=("Arial", 16, "bold")).pack(pady=5)
            ctk.CTkLabel(header_frame, text=f"Date: {sale['created_at']}").pack(pady=2)
            ctk.CTkLabel(header_frame, text=f"Payment: {sale['payment_type']}").pack(pady=2)

            # Items frame
            items_frame = ctk.CTkFrame(details_win)
            items_frame.pack(fill="both", expand=True, padx=12, pady=8)

            # Create text widget for bill content
            text_widget = ctk.CTkTextbox(items_frame, width=650, height=300)
            text_widget.pack(fill="both", expand=True, padx=5, pady=5)

            # Format bill content
            bill_content = self.format_bill_content(sale, items)
            text_widget.insert("1.0", bill_content)
            text_widget.configure(state="disabled")

            # Buttons
            btn_frame = ctk.CTkFrame(details_win)
            btn_frame.pack(fill="x", padx=12, pady=8)

            ctk.CTkButton(btn_frame, text="Close", command=details_win.destroy).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill details: {str(e)}")

    def format_bill_content(self, sale, items):
        """Format bill content for display"""
        content = []
        content.append(" " * 20 + "D-MART BILL")
        content.append("=" * 60)
        content.append(f"Bill No: {sale['bill_no']}")
        content.append(f"Date: {sale['created_at']}")
        content.append("-" * 60)
        content.append(f"{'ITEM':<30} {'QTY':>5} {'PRICE':>10} {'AMOUNT':>12}")
        content.append("-" * 60)

        total_amount = 0
        for item in items:
            product_name = item['product_name'][:29] if len(item['product_name']) > 29 else item['product_name']
            line = f"{product_name:<30} {item['qty']:>5} {item['price']:>10.2f} {item['amount']:>12.2f}"
            content.append(line)
            if item['discount_percent'] > 0:
                content.append(f"  Discount: {item['discount_percent']:.1f}%")
            total_amount += item['amount']

        content.append("-" * 60)
        content.append(f"{'Subtotal:':<45} ₹{sale['subtotal']:>12.2f}")
        content.append(f"{'GST (5%):':<45} ₹{sale['gst']:>12.2f}")
        content.append(f"{'TOTAL:':<45} ₹{sale['total']:>12.2f}")
        content.append("-" * 60)
        content.append(f"Payment: {sale['payment_type']}")
        if sale['payment_ref']:
            content.append(f"Reference: {sale['payment_ref']}")
        content.append("=" * 60)
        content.append(" " * 15 + "Thank you for shopping with us!")
        content.append(" " * 10 + "Please visit again at D-Mart Store!")
        content.append("=" * 60)

        return "\n".join(content)

    # ---------------- Generate bill (TXT + PDF + DB insert + stock reduce) ----------------
    def generate_report_from_cart(self):
        ensure_sales_tables()

        if not self.cart:
            messagebox.showinfo("No items", "Cart is empty. Add products first.")
            return

        # ask customer
        cust = simpledialog.askstring("Customer", "Enter customer name (optional):", parent=self)
        if cust is None:
            return
        cust = cust.strip() if cust.strip() else "Walk-in Customer"

        # compute totals using discount-aware cart
        subtotal = 0.0
        for it in self.cart:
            gross = it['qty'] * it['price']
            disc = float(it.get('discount_percent', 0) or 0)
            net = round(gross * (1 - disc / 100.0), 2)
            subtotal += net
        gst = round(subtotal * 0.05, 2)
        total = round(subtotal + gst, 2)

        # Payment dialog with QR code option
        pay_win = ctk.CTkToplevel(self)
        pay_win.title("Payment")
        pay_win.geometry("500x500")
        pay_win.grab_set()

        ctk.CTkLabel(pay_win, text=f"Bill Summary", font=("Arial", 16, "bold")).pack(pady=(10, 4))
        ctk.CTkLabel(pay_win, text=f"Customer: {cust}", font=("Arial", 12)).pack(pady=(2, 2))
        ctk.CTkLabel(pay_win, text=f"Subtotal: ₹{subtotal:.2f}", font=("Arial", 12)).pack(pady=(2, 2))
        ctk.CTkLabel(pay_win, text=f"GST (5%): ₹{gst:.2f}", font=("Arial", 12)).pack(pady=(2, 2))
        ctk.CTkLabel(pay_win, text=f"Total: ₹{total:.2f}", font=("Arial", 14, "bold")).pack(pady=(2, 8))

        payment_type_var = ctk.StringVar(value="Cash")
        ctk.CTkLabel(pay_win, text="Payment Type:", anchor="w", font=("Arial", 12)).pack(fill="x", padx=12,
                                                                                         pady=(10, 5))
        payment_frame = ctk.CTkFrame(pay_win)
        payment_frame.pack(fill="x", padx=12, pady=5)

        # UPI QR Code section
        upi_frame = ctk.CTkFrame(pay_win)
        upi_frame.pack(fill="x", padx=12, pady=5)

        upi_id = "dmart.store@paytm"  # Default UPI ID
        ctk.CTkLabel(upi_frame, text="UPI Payment QR Code:", font=("Arial", 12, "bold")).pack(pady=(5, 2))

        # Generate and display QR code
        if qrcode is not None:
            try:
                qr_img = qrcode.open("qr1.jpg")

                # Convert PIL Image to CTkImage
                qr_img_ctk = CTkImage(light_image=qr_img, dark_image=qr_img, size=(150, 150))
                qr_label = ctk.CTkLabel(upi_frame, image=qr_img_ctk, text="")
                qr_label.image = qr_img_ctk
                qr_label.pack(pady=5)

                ctk.CTkLabel(upi_frame, text=f"UPI ID: {upi_id}", font=("Arial", 10)).pack(pady=2)
                ctk.CTkLabel(upi_frame, text="Scan QR code to pay", font=("Arial", 9)).pack(pady=2)
            except Exception as e:
                print("QR code generation error:", e)
                ctk.CTkLabel(upi_frame, text="QR Code not available", font=("Arial", 10)).pack(pady=5)

        ctk.CTkRadioButton(payment_frame, text="Cash", variable=payment_type_var, value="Cash").pack(side="left",
                                                                                                     padx=10)
        ctk.CTkRadioButton(payment_frame, text="Card", variable=payment_type_var, value="Card").pack(side="left",
                                                                                                     padx=10)
        ctk.CTkRadioButton(payment_frame, text="UPI", variable=payment_type_var, value="UPI").pack(side="left", padx=10)

        ref_entry = ctk.CTkEntry(pay_win, placeholder_text="Reference / Card last4 / UPI txn id (optional)")
        ref_entry.pack(padx=12, pady=(5, 10), fill="x")

        paid_amount_var = ctk.DoubleVar(value=total)
        ctk.CTkLabel(pay_win, text="Amount Paid:", anchor="w", font=("Arial", 12)).pack(fill="x", padx=12, pady=(5, 0))
        paid_entry = ctk.CTkEntry(pay_win, textvariable=paid_amount_var, font=("Arial", 12))
        paid_entry.pack(padx=12, pady=(5, 10), fill="x")

        def on_payment_type_change(choice):
            if choice == "Card":
                card = simpledialog.askstring("Card Details", "Enter card number (mock):", parent=pay_win)
                if card:
                    last4 = card.strip()[-4:]
                    ref_entry.delete(0, "end")
                    ref_entry.insert(0, f"CardLast4:{last4}")
            elif choice == "UPI":
                upi = simpledialog.askstring("UPI ID", "Enter UPI ID (for QR generation):", parent=pay_win)
                if upi:
                    ref_entry.delete(0, "end")
                    ref_entry.insert(0, upi)
            else:
                ref_entry.delete(0, "end")

        payment_type_var.trace_add("write", lambda *args: on_payment_type_change(payment_type_var.get()))

        def confirm_payment():
            payment_type = payment_type_var.get()
            payment_ref = ref_entry.get().strip() or None
            try:
                paid_amt = float(paid_amount_var.get())
            except:
                messagebox.showwarning("Invalid", "Enter a valid paid amount.")
                return
            if paid_amt < total - 0.001:
                if not messagebox.askyesno("Underpaid",
                                           f"Paid amount ₹{paid_amt:.2f} is less than total ₹{total:.2f}. Continue?"):
                    return

            # Build bill lines (text) - IMPROVED FORMATTING
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bill_no = get_next_bill_no()

            lines = []
            lines.append(" " * 20 + "D-MART BILL")
            lines.append("=" * 60)
            lines.append(f"Bill No: {bill_no}")
            lines.append(f"Date: {now}")
            lines.append("-" * 60)

            # Header for items
            lines.append(f"{'ITEM':<30} {'QTY':>5} {'PRICE':>10} {'AMOUNT':>12}")
            lines.append("-" * 60)

            # Items
            for it in self.cart:
                disc = float(it.get('discount_percent', 0) or 0)
                gross = it['qty'] * it['price']
                amount = round(gross * (1 - disc / 100.0), 2)

                # Truncate item name if too long
                item_name = it['name'][:29] if len(it['name']) > 29 else it['name']

                lines.append(f"{item_name:<30} {it['qty']:>5} {it['price']:>10.2f} {amount:>12.2f}")

                # Show discount if applied
                if disc > 0:
                    lines.append(f"  Discount: {disc:.1f}%")

            lines.append("-" * 60)

            # Totals with proper alignment
            lines.append(f"{'Subtotal:':<45} ₹{subtotal:>12.2f}")
            lines.append(f"{'GST (5%):':<45} ₹{gst:>12.2f}")
            lines.append(f"{'TOTAL:':<45} ₹{total:>12.2f}")
            lines.append(f"{'Paid:':<45} ₹{paid_amt:>12.2f}")

            # Calculate change if overpaid
            if paid_amt > total:
                change = paid_amt - total
                lines.append(f"{'Change:':<45} ₹{change:>12.2f}")

            lines.append("-" * 60)

            # Payment info
            if payment_ref:
                lines.append(f"Payment: {payment_type} - {payment_ref}")
            else:
                lines.append(f"Payment: {payment_type}")

            lines.append("=" * 60)
            lines.append(" " * 15 + "Thank you for shopping with us!")
            lines.append(" " * 10 + "Visit again at D-Mart Store!")
            lines.append("=" * 60)

            # Compose bill_no and file names
            fname_txt = f"{bill_no}.txt"
            path_txt = save_bill_txt(fname_txt, "\n".join(lines))

            # Create PDF bill + UPI QR if UPI chosen
            pdf_name = f"{bill_no}.pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_name)
            upi_text = None
            if payment_type == "UPI" and payment_ref:
                upi_text = payment_ref
            generate_pdf_bill_from_lines(pdf_path, lines, upi_text=upi_text, attach_qr=True)

            # Save to DB
            ok = save_sale_to_db_record(
                bill_no=bill_no,
                customer=cust,
                subtotal=round(subtotal, 2),
                gst=round(gst, 2),
                total=round(total, 2),
                payment_type=payment_type,
                payment_ref=payment_ref,
                cart_items=self.cart
            )

            # Reduce stock in DB
            reduce_stock_in_db(self.cart)

            pay_win.destroy()
            messagebox.showinfo("Bill Generated",
                                f"Bill generated successfully!\n\n"
                                f"Bill No: {bill_no}\n"
                                f"Total: ₹{total:.2f}\n"
                                f"Payment: {payment_type}\n\n"
                                f"Files saved:\n{path_txt}\n{pdf_path}")

            # clear cart and show
            self.cart = []
            self.refresh_cart_view()
            self.show_dashboard()
            self.show_text_popup(f"Bill - {bill_no}", "\n".join(lines))

        ctk.CTkButton(pay_win, text="Confirm & Generate Bill", fg_color="#2BAE66", command=confirm_payment).pack(
            pady=(8, 12), padx=12, fill="x")
        ctk.CTkButton(pay_win, text="Cancel", fg_color="#E05656", command=pay_win.destroy).pack(padx=12, pady=(0, 12),
                                                                                                fill="x")

    # ---------------- Admin Panel ----------------
    def open_admin_panel(self):
        # Admin panel window: show schemas, tables, and quick viewers
        win = ctk.CTkToplevel(self)
        win.title("Admin Panel - DB Manager")
        win.geometry("1000x700")
        win.grab_set()

        left = ctk.CTkFrame(win, width=260)
        left.pack(side="left", fill="y", padx=8, pady=8)
        ctk.CTkLabel(left, text="Schemas", font=("Arial", 12, "bold")).pack(pady=(8, 6))
        schema_listbox = ttk.Treeview(left, columns=("schema",), show="headings", height=12)
        schema_listbox.heading("schema", text="Schema")
        schema_listbox.pack(fill="both", expand=True, padx=8, pady=6)
        for s in dbm.list_schemas():
            schema_listbox.insert("", "end", values=(s,))

        btn_frame = ctk.CTkFrame(left)
        btn_frame.pack(pady=6)

        def refresh_schemas():
            for r in schema_listbox.get_children(): schema_listbox.delete(r)
            for s in dbm.list_schemas():
                schema_listbox.insert("", "end", values=(s,))

        ctk.CTkButton(btn_frame, text="Refresh", command=refresh_schemas, width=120).pack()

        right_top = ctk.CTkFrame(win)
        right_top.pack(side="top", fill="x", padx=8, pady=6)
        right_bottom = ctk.CTkFrame(win)
        right_bottom.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        tbl_label = ctk.CTkLabel(right_top, text="Tables:", font=("Arial", 12, "bold"))
        tbl_label.pack(side="left", padx=(6, 12))

        tables_combo = ttk.Combobox(right_top, values=[])
        tables_combo.pack(side="left")

        btns = ctk.CTkFrame(right_top)
        btns.pack(side="left", padx=8)

        def load_tables_for_selected():
            sel = schema_listbox.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a schema to list tables")
                return
            schema = schema_listbox.item(sel[0], "values")[0]
            tables = dbm.list_tables(schema)
            tables_combo['values'] = tables
            if tables:
                tables_combo.set(tables[0])

        ctk.CTkButton(btns, text="Load Tables", command=load_tables_for_selected, width=120).pack(side="left", padx=6)

        tree = ttk.Treeview(right_bottom, show="headings")
        tree.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(right_bottom, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)

        def view_table():
            sel = schema_listbox.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a schema")
                return
            schema = schema_listbox.item(sel[0], "values")[0]
            tbl = tables_combo.get().strip()
            if not tbl:
                messagebox.showinfo("Select", "Choose a table")
                return

            try:
                conn = dbm.get_conn(schema)
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM `{tbl}` LIMIT 500;")
                rows = cur.fetchall()
                cur.close();
                conn.close()

                for c in tree.get_children(): tree.delete(c)
                tree["columns"] = list(rows[0].keys()) if rows else ["(no rows)"]
                for col in tree["columns"]:
                    tree.heading(col, text=col)
                    tree.column(col, width=140, anchor="w")
                for r in rows:
                    tree.insert("", "end", values=tuple(r.values()))
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to read table {tbl}: {e}")

        ctk.CTkButton(right_top, text="View Table", command=view_table, width=120).pack(side="left", padx=6)

        # quick helpers to create customers/products tables (if absent)
        helper_frame = ctk.CTkFrame(left)
        helper_frame.pack(pady=(12, 6), padx=6)
        ctk.CTkLabel(helper_frame, text="Quick Helpers", font=("Arial", 11, "bold")).pack(pady=(4, 6))

        def create_customers_table():
            if messagebox.askyesno("Confirm", "Create customers table (if missing) in customers schema?"):
                dbm.ensure_basic_tables()
                refresh_schemas()
                messagebox.showinfo("Done", "Customers and products table created (if they were missing).")

        ctk.CTkButton(helper_frame, text="Ensure Default Tables", command=create_customers_table, width=200).pack(
            pady=6)

    # ---------------- Customers UI ----------------
    def open_customers_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Customers")
        win.geometry("640x520")
        win.grab_set()
        ctk.CTkLabel(win, text="Customers", font=("Arial", 16, "bold")).pack(pady=(12, 8))
        frame = ctk.CTkFrame(win);
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        tree = ttk.Treeview(frame, columns=("id", "name", "mobile"), show="headings", height=18)
        tree.heading("id", text="ID");
        tree.heading("name", text="Name");
        tree.heading("mobile", text="Mobile")
        tree.column("id", width=50);
        tree.column("name", width=300);
        tree.column("mobile", width=150)
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview);
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)

        def load_customers():
            for r in tree.get_children(): tree.delete(r)
            for row in dbm.list_customers():
                tree.insert("", "end", values=(row.get("id"), row.get("name"), row.get("mobile")))

        def add_customer():
            name = simpledialog.askstring("Add Customer", "Customer name:", parent=win)
            if not name: return
            mobile = simpledialog.askstring("Add Customer", "Mobile (optional):", parent=win)
            addr = simpledialog.askstring("Add Customer", "Address (optional):", parent=win)
            ok = dbm.add_customer(name.strip(), mobile.strip() if mobile else None, addr.strip() if addr else None)
            if ok:
                messagebox.showinfo("Added", "Customer added.")
            else:
                messagebox.showerror("Error", "Failed to add customer. Check DB logs.")
            load_customers()

        btnf = ctk.CTkFrame(win);
        btnf.pack(pady=8)
        ctk.CTkButton(btnf, text="Add Customer", command=add_customer, width=140).pack(side="left", padx=8)
        ctk.CTkButton(btnf, text="Refresh", command=load_customers, width=140).pack(side="left", padx=8)
        load_customers()

    # ---------------- Text popup ----------------
    def show_text_popup(self, title, text):
        win = ctk.CTkToplevel(self)
        win.title(title);
        win.geometry("760x560");
        win.grab_set()
        ctk.CTkLabel(win, text=title, font=("Arial", 14, "bold")).pack(pady=(8, 6))
        txt = ctk.CTkTextbox(win, width=720, height=480)
        txt.pack(padx=8, pady=6)
        txt.insert("end", text);
        txt.configure(state="disabled")

    # ---------------- Returns / Refunds UI ----------------
    def open_returns_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Refunds / Returns")
        win.geometry("720x480")
        win.grab_set()

        ctk.CTkLabel(win, text="Refunds / Returns", font=("Arial", 14, "bold")).pack(pady=(8, 6))
        frm = ctk.CTkFrame(win)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        topf = ctk.CTkFrame(frm)
        topf.pack(fill="x", padx=8, pady=6)
        bno_entry = ctk.CTkEntry(topf, placeholder_text="Enter bill_no (e.g. BILL-YYYYMMDD-0001)")
        bno_entry.pack(side="left", padx=6, pady=6, fill="x", expand=True)

        def load_sale_items():
            bill = bno_entry.get().strip()
            if not bill:
                messagebox.showwarning("Input", "Enter bill_no")
                return
            try:
                schema = DB_SCHEMAS[2] if len(DB_SCHEMAS) > 2 else DB_SCHEMAS[0]
                conn = dbm.get_conn(schema)
                cur = conn.cursor()
                cur.execute(
                    "SELECT s.id, s.bill_no, s.customer_name, si.product_name, si.qty, si.price, si.discount_percent, si.amount FROM sales s JOIN sale_items si ON si.sale_id = s.id WHERE s.bill_no = %s",
                    (bill,))
                rows = cur.fetchall()
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("DB", f"Failed to load sale: {e}")
                return
            # populate list
            for r in tree.get_children(): tree.delete(r)
            for r in rows:
                vals = tuple(r.values()) if isinstance(r, dict) else tuple(r)
                tree.insert("", "end", values=(vals[3], vals[4], vals[5], vals[6], vals[7]))

        ctk.CTkButton(topf, text="Load Sale Items", command=load_sale_items).pack(side="left", padx=6)

        columns = ("product", "qty", "price", "disc", "amount")
        tree = ttk.Treeview(frm, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        sb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview);
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)

        # refund controls
        def make_refund():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select an item to refund")
                return
            item = tree.item(sel[0], "values")
            prod_name = item[0];
            qty = int(item[1]);
            amount = float(item[4])
            rtn_q = simpledialog.askinteger("Return qty", f"Max {qty}. Qty to return:", parent=win, minvalue=1,
                                            maxvalue=qty)
            if rtn_q is None:
                return
            reason = simpledialog.askstring("Reason", "Enter reason for return (optional):", parent=win)
            unit_amount = amount / qty if qty else 0
            refund_amount = round(unit_amount * rtn_q, 2)
            bill = bno_entry.get().strip()
            ok = record_return(bill_no=bill, product_name=prod_name, qty=rtn_q, refund_amount=refund_amount,
                               reason=reason)
            if ok:
                messagebox.showinfo("Returned", f"Refund recorded: ₹{refund_amount:.2f}. Stock updated.")
                load_sale_items()
            else:
                messagebox.showerror("Failed", "Return failed. Check logs.")

        btnf = ctk.CTkFrame(frm)
        btnf.pack(fill="x", padx=8, pady=6)
        ctk.CTkButton(btnf, text="Make Refund / Return", command=make_refund).pack(side="left", padx=6)

    # ---------------- Logout + Exit ----------------
    def logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return
        self.cart = []
        self.logged_user = None
        self.build_login()


# ----------------- App Launcher -----------------
if __name__ == "__main__":
    app = DMartApp()
    app.mainloop()