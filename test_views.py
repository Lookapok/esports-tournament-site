from django.http import HttpResponse
from django.shortcuts import render

def test_view(request):
    return HttpResponse("<h1>Django 測試頁面</h1><p>如果你看到這個，Django 正在正常工作！</p>")

def test_admin_view(request):
    return HttpResponse("""
    <h1>Admin 測試頁面</h1>
    <p>這是一個測試 admin 路由的簡單頁面</p>
    <a href='/admin/'>前往真正的 Admin</a>
    """)
