from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils.crypto import get_random_string

from ..models import (
    GOAL_START_DATE, LEADERSHIP_LEVEL_AMOUNT, DjangoHero, Payment,
)
from ..templatetags.fundraising_extras import (
    display_django_heros, donation_form_with_heart,
)


class TestDonationFormWithHear(TestCase):
    def test_donors_count(self):
        # Donor with a Payment after GOAL_START_DATE
        donor1 = DjangoHero.objects.create()
        donation1 = donor1.donation_set.create()
        donation1.payment_set.create(amount=1, stripe_charge_id='a')
        donation1.payment_set.create(amount=2, stripe_charge_id='b')
        # Donor with a Payment before GOAL_START_DATE
        past_donor = DjangoHero.objects.create()
        past_donation = past_donor.donation_set.create()
        past_payment = past_donation.payment_set.create(amount=4, stripe_charge_id='c')
        Payment.objects.filter(pk=past_payment.pk).update(date=GOAL_START_DATE - timedelta(days=1))
        response = donation_form_with_heart({'user': None})
        self.assertEqual(response['total_donors'], 1)
        self.assertEqual(response['donated_amount'], Decimal('3.00'))


class TestDisplayDjangoHeros(TestCase):
    def test_display_django_heros(self):
        def create_hero_with_payment_amount(amount):
            hero = DjangoHero.objects.create(
                email='%s@djangoproject.com' % get_random_string(),
                approved=True,
                is_visible=True,
            )
            donation = hero.donation_set.create(interval='onetime')
            donation.payment_set.create(amount=amount, stripe_charge_id=get_random_string())
            return hero

        hero1 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT + 1)
        hero2 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT)
        hero3 = create_hero_with_payment_amount(LEADERSHIP_LEVEL_AMOUNT - 1)

        response = display_django_heros()
        self.assertEqual(response['leaders'], [hero1, hero2])
        self.assertEqual(response['heros'], [hero3])