from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Customer, Order


# Welcome page
def home_view(request):
    return render(request, 'app/index.html')

# Create account or Login
def enter_view(request):
    if request.method == 'POST':
        # SIGN UP logic
        if request.POST.get('submit') == 'sign_up':
            username = request.POST.get('username')
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmpassword = request.POST.get('password-confirm')

            # account creation rules
            if User.objects.filter(username=username):
                messages.error(request, 'Username already registered in our database, please provide another credential.')
                return render(request, 'app/enter.html')
            if User.objects.filter(email=email):
                messages.error(request, 'Email already registered in our database, please provide another credential.')
                return render(request, 'app/enter.html')
            if password != confirmpassword:
                messages.error(request, 'the password provided does not match, use the same credential.')
                return render(request, 'app/enter.html')

            my_customer = User.objects.create_user( username, email, password)
            my_customer.first_name = name
            my_customer.last_name = surname
            my_customer.email = email
            my_customer.save()

            messages.success(request, 'Your Account has been created now you can Login')

            return render(request, 'app/enter.html')
        
        # SIGN IN logic
        elif request.POST.get('submit') == 'sign_in':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(username=username, password=password)
            if user.is_active:
                login(request, user)
                
                return redirect('User')

            else:
                messages.error(request, 'username or Password are incorrect, please provide valid credentials')
                return render(request, 'app/enter.html')

    return render(request, 'app/enter.html')

@login_required(login_url='Enter')
def user_view(request):
    # retrieve user information
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    
    # retrieve customer information
    customer = Customer.objects.get(user=user)
    balance_BTC = customer.balance_BTC
    balance_USD = customer.balance_USD
    
    #retrieve order information
    orders = Order.objects.filter(customer=customer).order_by('-date')
    all_orders = Order.objects.all()
    
    # form handler
    if request.method == 'POST':
        # charge $ in Customer
        if request.POST.get('submit') == 'charge_USD':
            charge_USD = request.POST.get('charge')
            charge_USD_float = float(charge_USD)
            customer_balance_USD = customer.balance_USD+charge_USD_float
            
            Customer.objects.filter(user=user).update(balance_USD=customer_balance_USD)
            messages.success(request, 'the transer is completed, the $ are been charged on your account. '
                            'reload the page to see the right amount in your Balance')

            redirect('User')
        # load want to buy order
        elif request.POST.get('submit') == 'wtb_BTC':
            want_to_buy = request.POST.get('amount')
            want_to_buy_float = float(want_to_buy)
            price = request.POST.get('price')
            price_float = float(price)
            
            # to insert two or + order change or drop the indexes in database mongoDB (app_order)
            if customer.balance_USD >= price_float:
                my_order = Order.objects.create(customer=customer,
                                                initial_want_to_sell = 0.0,
                                                want_to_sell=0.0,
                                                initial_want_to_buy = want_to_buy_float,
                                                want_to_buy=want_to_buy_float,
                                                initial_price = price_float,
                                                price=price_float,
                                                status='open')
                my_order.save()
                messages.success(request, 'WTB order correctly loaded')
            else:
                messages.error(request, 'You have entered an amount in $ that is higher than your budget')
                return redirect('User')
            
            b = my_order.want_to_buy
            a = my_order.price
            # some math + update in objects
            for order in all_orders:
                c = order.want_to_sell
                d = order.price
                # to avoid error in f
                if order.status == 'open' and order.want_to_sell != 0.0:
                    e = c/b
                    f = d/e
                # updating sell and buy orders
                if order.status == 'open' and order.want_to_sell != 0.0 and a>=f:
                    order.want_to_sell = c-b
                    order.price= d-a
                    order.save(force_update=True)
                    my_order.want_to_buy= b-c
                    my_order.price = a-d
                    my_order.save(force_update=True)
                # closing sell order, assign USD and retrieve BTC to customer
                    if order.want_to_sell <= 0.0 and order._id != my_order._id:
                        order.status = 'closed'
                        order_customer = order.customer
                        order_customer.balance_BTC = order_customer.balance_BTC - c
                        order_customer.balance_USD = order_customer.balance_USD + d
                        order_customer.trend_BTC = order_customer.trend_BTC - c
                        order_customer.trend_USD = order_customer.trend_USD + d
                        order.save(force_update=True)
                        order_customer.save(force_update=True)
                    # closing buy order, assign BTC and retrieve USD from customer
                    if my_order.want_to_buy <= 0.0 and order._id != my_order._id:
                        my_order.status = 'closed'
                        my_order_customer = my_order.customer
                        my_order_customer.balance_BTC = my_order_customer.balance_BTC + b
                        my_order_customer.trend_BTC = my_order_customer.trend_BTC + b
                        if a > d:
                            my_order_customer.balance_USD = my_order_customer.balance_USD - d
                            my_order_customer.trend_USD = my_order_customer.trend_USD - d
                        elif a <= d:
                            my_order_customer.balance_USD = my_order_customer.balance_USD - a
                            my_order_customer.trend_USD = my_order_customer.trend_USD - a
                        my_order.save(force_update=True)
                        my_order_customer.save(force_update=True)
            
            return redirect('User')
        # load want to sell order
        elif request.POST.get('submit') == 'wts_BTC':
            want_to_sell = request.POST.get('amount')
            want_to_sell_float = float(want_to_sell)
            price = request.POST.get('price')
            price_float = float(price)
            
            if customer.balance_BTC >= want_to_sell_float:
                # to insert two or + order change or drop the indexes in database mongoDB (app_order)
                my_order = Order.objects.create(customer=customer,
                                                initial_want_to_sell=want_to_sell_float,
                                                want_to_sell=want_to_sell_float,
                                                initial_want_to_buy=0.0,
                                                want_to_buy=0.0,
                                                initial_price=price_float,
                                                price=price_float,
                                                status='open')
                my_order.save()
                messages.success(request, 'WTS order correctly loaded')
            else:
                messages.error(request, 'You have entered an amount in BTC that is higher than your credit')
                return redirect('User')
            
            b = my_order.want_to_sell
            a = my_order.price
            # some math + update in objects
            for order in all_orders:
                c = order.want_to_buy
                d = order.price
                # to avoid error in f
                if order.status == 'open' and order.want_to_buy != 0.0:
                    e = c/b
                    f = d/e
                # updating sell and buy orders
                if order.status == 'open' and order.want_to_buy != 0.0 and a<=f:
                    order.want_to_buy = c-b
                    order.price= d-a
                    order.save(force_update=True)
                    my_order.want_to_sell= b-c
                    my_order.price = a-d
                    my_order.save(force_update=True)
                    # closing sell order, assign USD and retrieve BTC to customer
                    if order.want_to_buy <= 0.0 and order._id != my_order._id:
                        order.status = 'closed'
                        order_customer = order.customer
                        order_customer.balance_BTC = order_customer.balance_BTC + c
                        order_customer.trend_BTC = order_customer.trend_BTC + c
                        if a > d:
                            order_customer.balance_USD = order_customer.balance_USD - d
                            order_customer.trend_USD = order_customer.trend_USD - d
                        elif a <= d:
                            order_customer.balance_USD = order_customer.balance_USD - a
                            order_customer.trend_USD = order_customer.trend_USD - a
                        order.save(force_update=True)
                        order_customer.save(force_update=True)
                    # closing buy order, assign BTC and retrieve USD from customer
                    if my_order.want_to_sell <= 0.0 and order._id != my_order._id:
                        my_order.status = 'closed'
                        my_order_customer = my_order.customer
                        my_order_customer.balance_BTC = my_order_customer.balance_BTC - b
                        my_order_customer.trend_BTC = my_order_customer.trend_BTC - b
                        my_order_customer.balance_USD = my_order_customer.balance_USD + a
                        my_order_customer.trend_USD = my_order_customer.trend_USD + a
                        my_order.save(force_update=True)
                        my_order_customer.save(force_update=True)
                    
            return redirect('User')
        # close order
        elif request.POST.get('submit') == 'close_order':
            initial_wts = request.POST.get('order_initial_wts')
            initial_wtb = request.POST.get('order_initial_wtb')
            initial_order_price = request.POST.get('order_initial_price')
            wts = request.POST.get('order_close_wts')
            wtb = request.POST.get('order_close_wtb')
            order_price = request.POST.get('order_close_price')
            status = request.POST.get('order_close_status')
            
            initial_wts_float = float(initial_wts)
            initial_wtb_float = float(initial_wtb)
            initial_order_price_float = float(initial_order_price)
            wts_float = float(wts)
            wtb_float = float(wtb)
            order_price_float = float(order_price)
            
            order_to_close = Order.objects.filter(want_to_sell=wts_float, want_to_buy=wtb_float, price=order_price_float, status=status)
            # closing sell order and assign USD and retrieve BTC to customer
            if initial_wtb_float == 0.0:
                order_to_close.update(status='closed')
                difference_BTC = initial_wts_float - wts_float
                customer.balance_BTC = customer.balance_BTC - difference_BTC
                customer.trend_BTC = customer.trend_BTC - difference_BTC
                difference_USD = initial_order_price_float - order_price_float
                customer.balance_USD = customer.balance_USD + difference_USD
                customer.trend_USD = customer.trend_USD + difference_USD
                customer.save(force_update=True)
            # closing buy order and assign BTC and retrieve USD from customer
            elif initial_wts_float == 0.0:
                order_to_close.update(status='closed')
                difference_BTC = initial_wtb_float - wtb_float
                customer.balance_BTC = customer.balance_BTC + difference_BTC
                customer.trend_BTC = customer.trend_BTC + difference_BTC
                difference_USD = initial_order_price_float - order_price_float
                customer.balance_USD = customer.balance_USD - difference_USD
                customer.trend_USD = customer.trend_USD - difference_USD
                customer.save(force_update=True)
            messages.success(request, "order closed successfully")

            return redirect('User')
        # open a new order equal to the old order
        elif request.POST.get('submit') == 'open_order':
            wts = request.POST.get('order_open_wts')
            initial_wts = request.POST.get('order_initial_wts')
            wtb = request.POST.get('order_open_wtb')
            initial_wtb = request.POST.get('order_initial_wtb')
            order_price = request.POST.get('order_open_price')
            initial_order_price = request.POST.get('order_initial_price')
            
            initial_wts_float = float(initial_wts)
            wts_float = float(wts)
            initial_wtb_float = float(initial_wtb)
            wtb_float = float(wtb)
            initial_order_price_float = float(initial_order_price)
            order_price_float = float(order_price)
            
            # to insert two or + order change or drop the indexes in database mongoDB (app_order)
            if customer.balance_USD >= order_price_float or customer.balance_BTC >= initial_wts_float:
                my_order = Order.objects.create(customer=customer,
                                                initial_want_to_sell = initial_wts_float,
                                                want_to_sell=initial_wts_float,
                                                initial_want_to_buy = initial_wtb_float,
                                                want_to_buy=initial_wtb_float,
                                                initial_price = initial_order_price_float,
                                                price=initial_order_price_float,
                                                status='open')
                my_order.save()
                messages.success(request, 'new WTB order correctly loaded')
            else:
                messages.error(request, "You can't repeat the order - low credit")
                return redirect('User')
            
            # order changes according to sale or purchase - buy
            if my_order.want_to_sell == 0.0:
                b = my_order.want_to_buy
                a = my_order.price
                # some math + update in objects
                for order in all_orders:
                    c = order.want_to_sell
                    d = order.price
                    # to avoid error in f
                    if order.status == 'open' and order.want_to_sell != 0.0:
                        e = c/b
                        f = d/e
                    # updating sell and buy orders
                    if order.status == 'open' and order.want_to_sell != 0.0 and a>=f:
                        order.want_to_sell = c-b
                        order.price= d-a
                        order.save(force_update=True)
                        my_order.want_to_buy= b-c
                        my_order.price = a-d
                        my_order.save(force_update=True)
                        # closing sell order and assign USD and retrieve BTC to customer
                        if order.want_to_sell <= 0.0 and order._id != my_order._id:
                            order.status = 'closed'
                            order_customer = order.customer
                            order_customer.balance_BTC = order_customer.balance_BTC - c
                            order_customer.trend_BTC = order_customer.trend_BTC - c
                            order_customer.balance_USD = order_customer.balance_USD + d
                            order_customer.trend_USD = order_customer.trend_USD + d
                            order.save(force_update=True)
                            order_customer.save(force_update=True)
                        # closing buy order and assign BTC and retrieve USD from customer
                        if my_order.want_to_buy <= 0.0 and order._id != my_order._id:
                            my_order.status = 'closed'
                            my_order_customer = my_order.customer
                            my_order_customer.balance_BTC = my_order_customer.balance_BTC + b
                            my_order_customer.trend_BTC = my_order_customer.trend_BTC + b
                            if a > d:
                                my_order_customer.balance_USD = my_order_customer.balance_USD - d
                                my_order_customer.trend_USD = my_order_customer.trend_USD - d
                            elif a <= d:
                                my_order_customer.balance_USD = my_order_customer.balance_USD - a
                                my_order_customer.trend_USD = my_order_customer.trend_USD - a
                            my_order.save(force_update=True)
                            my_order_customer.save(force_update=True)
            # order changes according to sale or purchase - sell
            elif my_order.want_to_buy == 0.0:
                b = my_order.want_to_sell
                a = my_order.price
                # some math + update in objects
                for order in all_orders:
                    c = order.want_to_buy
                    d = order.price
                    # to avoid error in f
                    if order.status == 'open' and order.want_to_buy != 0.0:
                        e = c/b
                        f = d/e
                    # updating sell and buy orders
                    if order.status == 'open' and order.want_to_buy != 0.0 and a<=f:
                        order.want_to_buy = c-b
                        order.price= d-a
                        order.save(force_update=True)
                        my_order.want_to_sell= b-c
                        my_order.price = a-d
                        my_order.save(force_update=True)
                        # closing sell order and assign USD and retrieve BTC to customer
                        if order.want_to_buy <= 0.0 and order._id != my_order._id:
                            order.status = 'closed'
                            order_customer = order.customer
                            order_customer.balance_BTC = order_customer.balance_BTC + c
                            order_customer.trend_BTC = order_customer.trend_BTC + c
                            if a > d:
                                order_customer.balance_USD = order_customer.balance_USD - d
                                order_customer.trend_USD = order_customer.trend_USD - d
                            elif a <= d:
                                order_customer.balance_USD = order_customer.balance_USD - a
                                order_customer.trend_USD = order_customer.trend_USD - a
                            order.save(force_update=True)
                            order_customer.save(force_update=True)
                        # closing buy order and assign BTC and retrieve USD from customer
                        if my_order.want_to_sell <= 0.0 and order._id != my_order._id:
                            my_order.status = 'closed'
                            my_order_customer = my_order.customer
                            my_order_customer.balance_BTC = my_order_customer.balance_BTC - b
                            my_order_customer.trend_BTC = my_order_customer.trend_BTC - b
                            my_order_customer.balance_USD = my_order_customer.balance_USD + a
                            my_order_customer.trend_USD = my_order_customer.trend_USD + a
                            my_order.save(force_update=True)
                            my_order_customer.save(force_update=True)
        
            return redirect('User')
            
            
            
    return render(request, 'app/user.html', {'first_name': first_name,
                                            'last_name': last_name,
                                            'balance_BTC': balance_BTC,
                                            'balance_USD': balance_USD,
                                            'orders': orders})

@login_required(login_url='Enter')
def chart_view(request):
    # retrieve user information
    user = request.user
    
    # retrieve customer information
    user_customer = Customer.objects.get(user=user)
    
    # retrieve all customers information
    customers = Customer.objects.filter().order_by('-trend_BTC')
    
    return render(request, 'app/chart.html', {'user': user,
                                              'user_customer': user_customer,
                                              'customers': customers})

@login_required(login_url='Enter')
def orders_view(request):
    # retrieve user information
    user = request.user
    
    # retrieve customer information
    user_customer = Customer.objects.get(user=user)

    # retrieve all customers information
    customers = Customer.objects.filter().order_by('-trend_BTC')
    
    # retrieve all orders information
    orders = Order.objects.filter().order_by('-date')
    
    if request.method == 'POST':
        # buy option handler
        if request.POST.get('submit') == 'wtb_order':
            wts = request.POST.get('order_wts')
            initial_wts = request.POST.get('order_initial_wts')
            wtb = request.POST.get('order_wtb')
            initial_wtb = request.POST.get('order_initial_wtb')
            order_price = request.POST.get('order_price')
            initial_order_price = request.POST.get('order_initial_price')
            status = request.POST.get('order_status')
            
            initial_wts_float = float(initial_wts)
            wts_float = float(wts)
            initial_wtb_float = float(initial_wtb)
            wtb_float = float(wtb)
            initial_order_price_float = float(initial_order_price)
            order_price_float = float(order_price)
            
            order_to_buy = Order.objects.filter(want_to_sell=wts_float,
                                                initial_want_to_sell=initial_wts_float,
                                                initial_want_to_buy=initial_wtb_float,
                                                want_to_buy=wtb_float,
                                                initial_price=initial_order_price_float,
                                                price=order_price_float,
                                                status=status)
            
            if user_customer.balance_USD >= order_price_float and status == 'open':
                order_to_buy.update(status='closed',
                                    want_to_sell= wts_float - wts_float,
                                    price=order_price_float - order_price_float )
                
                user_customer.balance_BTC = user_customer.balance_BTC + wts_float
                user_customer.trend_BTC = user_customer.trend_BTC + wts_float
                user_customer.balance_USD = user_customer.balance_USD - order_price_float
                user_customer.trend_USD = user_customer.trend_USD - order_price_float
                user_customer.save(force_update=True)
                messages.success(request, 'Order purchased correctly')
            else:
                messages.error(request, 'An error has occured, check your balance or order status may be closed')
            return redirect('Orders')
        # sell option handler
        elif request.POST.get('submit') == 'wts_order':
            wts = request.POST.get('order_wts')
            initial_wts = request.POST.get('order_initial_wts')
            wtb = request.POST.get('order_wtb')
            initial_wtb = request.POST.get('order_initial_wtb')
            order_price = request.POST.get('order_price')
            initial_order_price = request.POST.get('order_initial_price')
            status = request.POST.get('order_status')
            
            initial_wts_float = float(initial_wts)
            wts_float = float(wts)
            initial_wtb_float = float(initial_wtb)
            wtb_float = float(wtb)
            initial_order_price_float = float(initial_order_price)
            order_price_float = float(order_price)
            
            order_to_sell = Order.objects.filter(want_to_sell=wts_float,
                                                initial_want_to_sell=initial_wts_float,
                                                initial_want_to_buy=initial_wtb_float,
                                                want_to_buy=wtb_float,
                                                initial_price=initial_order_price_float,
                                                price=order_price_float,
                                                status=status)
            
            if user_customer.balance_BTC >= wtb_float and status == 'open':
                order_to_sell.update(status='closed',
                                    want_to_buy= wtb_float - wtb_float,
                                    price=order_price_float - order_price_float )
                
                user_customer.balance_BTC = user_customer.balance_BTC - wtb_float
                user_customer.trend_BTC = user_customer.trend_BTC - wtb_float
                user_customer.balance_USD = user_customer.balance_USD + order_price_float
                user_customer.trend_USD = user_customer.trend_USD + order_price_float
                user_customer.save(force_update=True)
                messages.success(request, 'Order processed correctly')
            else:
                messages.error(request, 'An error has occured, check your balance or order status may be closed')
            return redirect('Orders')
    
    return render(request, 'app/orders.html', {'user': user,
                                              'user_customer': user_customer,
                                              'customers': customers,
                                              'orders': orders})

# logout
def logout_view(request):
    logout(request)
    return redirect('Enter')