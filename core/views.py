import datetime

from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from lys import L, render, raw

from .models import Account, LoginToken

"""
security:
  - spam via login attempts / send money
  - account enumeration
  - tokens leak (?)
"""

def tpl_base(*content, title=''):
    return render((
        raw('<!DOCTYPE html>'),
        L.html / (
            L.head / (
                L.meta(charset='utf-8'),
                L.title / (((title + ' - ') if title else '') + 'Petal'),
                L.link(rel='stylesheet', href="/static/css/bootstrap.css"),
                L.link(rel='stylesheet', href="/static/css/base.css"),
            ),
            L.body / content,
        ),
    ))


def index(request):
    email = None
    message = None

    if 'token' in request.GET:
        try:
            token = LoginToken.objects.get(email=request.GET['email'], token=request.GET['token'])
            email = token.email
        except LoginToken.DoesNotExist:
            pass

    if email: # logged in
        account = Account.objects.get(email=email)

        if request.method == 'POST':
            # todo: atomize / transaction
            # todo: validate email
            dest_email = request.POST['email']
            dest_amount = -1
            message = 'invalid amount'
            try:
                dest_amount = int(request.POST['amount'])
            except ValueError:
                pass
            if account.amount >= dest_amount and dest_amount > 0: # TODO: else "not enough founds"
                try:
                    dest_account = Account.objects.get(email=dest_email)
                    dest_account.amount += dest_amount
                    dest_account.save()

                    send_mail('[petals.dam.io] %s sent you %d petals' % (email, dest_amount), """%s sent you %d petals.
    You current balance is now: %d petals
    https://petal.x.dam.io/
    """ % (email, dest_amount, dest_account.amount), 'petals@dam.io', [dest_email], fail_silently=False)
                except Account.DoesNotExist:
                    dest_account = Account.objects.create(email=dest_email, amount=dest_amount)
                account.amount -= dest_amount
                account.save()
                message = '%d sent' % dest_amount
    else:
        if request.method == 'POST':
            email = request.POST['email']
            try:
                account = Account.objects.get(email=email)
                token = get_random_string()
                LoginToken.objects.create(email=email, token=token, expire_on=datetime.date.today() + datetime.timedelta(days=1))
                send_mail('[petals.dam.io] link to connect to your account', """Here is a temporary link to connect to your account:
https://petal.x.dam.io/?token=%s&email=%s
""" % (token, email), 'petals@dam.io', [email], fail_silently=False)
                message = 'connection link sent to %s' % email
            except Account.DoesNotExist:
                pass
        email = None # lol

    total = sum([account.amount for account in Account.objects.all()])

    content = L.div('.container') / (
        L.div('.row') / (
            L.div('.col-sm-12') / (
                L.h3 / (L.a(href='/') / 'Petal'),
                L.strong / ('%d petals in circulation' % total),
                L.hr,
            ),
        ),
        (
            L.div('.row') / (
                L.div('.col-sm-3') / (
                    L.h3 / email,
                    L.p / ('You have %d petals' % account.amount),
                    L.h4 / 'send petals',
                    L.form(method='post') / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.div / (
                            L.label('control-label') / 'email', L.br, L.input(name='email'),
                        ),
                        L.div / (
                            L.label('control-label') / 'amount', L.br, L.input(name='amount', type='number'),
                        ),
                        # L.div / (
                        #     L.label('control-label') / 'message (optional)', L.br, L.input(name='message', max_length="140"),
                        # ),
                        L.br,
                        L.button(type='submit') / 'send',
                    ),
                    L.i / message,
                ),
            )
        ) if email else (
            L.div('.row') / (
                L.div('.col-sm-3') / (
                    L.h3 / 'see you account',
                    L.p / 'You will receive an email with a connection link',
                    L.form(method='post') / (
                        L.input(type='hidden', name='csrfmiddlewaretoken', value=get_token(request)),
                        L.div / (
                            L.label('control-label') / 'email', L.br, L.input(name='email'),
                        ),
                        L.br,
                        L.button(type='submit') / 'send'
                    ),
                    L.i / message,
                ),
            )
        )
    )
    return HttpResponse(tpl_base(content))
