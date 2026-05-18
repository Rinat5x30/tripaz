"""
Seed command: python manage.py seed_data
Creates demo users, guides, tours, bookings, reviews, chat messages.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for TripAZ'

    def handle(self, *args, **kwargs):
        from apps.accounts.models import TouristProfile
        from apps.guides.models import GuideProfile, Tour, GuideAvailability
        from apps.bookings.models import Booking, Payment
        from apps.reviews.models import Review
        from apps.chat.models import ChatMessage
        from apps.core.models import Notification

        self.stdout.write(self.style.WARNING('Seeding demo data...'))

        # ── Admin ─────────────────────────────────────────────
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@tripaz.az', 'role': 'admin', 'is_staff': True, 'is_superuser': True,
            'first_name': 'Admin', 'last_name': 'TripAZ',
        })
        admin.set_password('admin123')
        admin.save()

        # ── Support ───────────────────────────────────────────
        support, _ = User.objects.get_or_create(username='support', defaults={
            'email': 'support@tripaz.az', 'role': 'support', 'is_staff': True,
            'first_name': 'Support', 'last_name': 'Team',
        })
        support.set_password('support123')
        support.save()

        # ── Tourists ──────────────────────────────────────────
        tourist_data = [
            ('tourist1', 'john.doe@example.com', 'John', 'Doe', 'United States'),
            ('tourist2', 'emma.wilson@example.com', 'Emma', 'Wilson', 'United Kingdom'),
            ('tourist3', 'marco.rossi@example.com', 'Marco', 'Rossi', 'Italy'),
        ]
        tourists = []
        for uname, email, fn, ln, country in tourist_data:
            u, _ = User.objects.get_or_create(username=uname, defaults={
                'email': email, 'first_name': fn, 'last_name': ln, 'role': 'tourist',
            })
            u.set_password('tourist123')
            u.save()
            TouristProfile.objects.get_or_create(user=u, defaults={'country': country})
            tourists.append(u)

        # ── Guides ────────────────────────────────────────────
        guide_data = [
            {
                'username': 'guide_anar', 'email': 'anar@tripaz.az',
                'first_name': 'Anar', 'last_name': 'Mammadov',
                'bio': 'Born and raised in Baku, I have spent 10 years sharing the hidden gems of Azerbaijan with travelers from across the globe. From ancient petroglyphs to bustling Old City bazaars, I bring history to life.',
                'tagline': 'Your window into the soul of Azerbaijan',
                'city': 'baku', 'languages': 'english,russian,azerbaijani',
                'price_per_hour': Decimal('45.00'), 'experience_years': 10,
                'license_number': 'AZ-GUIDE-2847', 'rating': Decimal('4.9'), 'total_reviews': 127,
                'is_featured': True,
            },
            {
                'username': 'guide_leyla', 'email': 'leyla@tripaz.az',
                'first_name': 'Leyla', 'last_name': 'Aliyeva',
                'bio': 'Passionate about Azerbaijani cuisine and culture. I run exclusive food tours and cooking experiences in Baku\'s historic neighborhoods. A certified sommelier specializing in local wines.',
                'tagline': 'Taste the real Azerbaijan',
                'city': 'baku', 'languages': 'english,french,azerbaijani',
                'price_per_hour': Decimal('55.00'), 'experience_years': 7,
                'license_number': 'AZ-GUIDE-3102', 'rating': Decimal('4.8'), 'total_reviews': 89,
                'is_featured': True,
            },
            {
                'username': 'guide_kamran', 'email': 'kamran@tripaz.az',
                'first_name': 'Kamran', 'last_name': 'Hasanov',
                'bio': 'Adventure specialist and mountain guide based in Sheki. I organize treks through the Caucasus mountains, village homestays, and authentic rural experiences.',
                'tagline': 'Adventure beyond the tourist trail',
                'city': 'sheki', 'languages': 'english,russian',
                'price_per_hour': Decimal('40.00'), 'experience_years': 8,
                'license_number': 'AZ-GUIDE-1965', 'rating': Decimal('4.7'), 'total_reviews': 64,
                'is_featured': True,
            },
            {
                'username': 'guide_nigar', 'email': 'nigar@tripaz.az',
                'first_name': 'Nigar', 'last_name': 'Rzayeva',
                'bio': 'Architecture and photography enthusiast. Specialized in Baku\'s stunning contrast of ancient Old City and futuristic Flame Towers. Perfect guide for creatives and photographers.',
                'tagline': 'See Baku through a creative lens',
                'city': 'baku', 'languages': 'english,german,azerbaijani',
                'price_per_hour': Decimal('50.00'), 'experience_years': 5,
                'license_number': 'AZ-GUIDE-4231', 'rating': Decimal('4.6'), 'total_reviews': 43,
                'is_featured': False,
            },
            {
                'username': 'guide_rashad', 'email': 'rashad@tripaz.az',
                'first_name': 'Rashad', 'last_name': 'Guliyev',
                'bio': 'History PhD student turned full-time guide. Expert in Silk Road history, Zoroastrian sites, and Azerbaijan\'s ancient civilizations. Academic depth with engaging storytelling.',
                'tagline': 'History alive on every corner',
                'city': 'baku', 'languages': 'english,turkish,azerbaijani',
                'price_per_hour': Decimal('60.00'), 'experience_years': 6,
                'license_number': 'AZ-GUIDE-5517', 'rating': Decimal('4.9'), 'total_reviews': 98,
                'is_featured': True,
            },
        ]

        guides = []
        for gd in guide_data:
            u, _ = User.objects.get_or_create(username=gd['username'], defaults={
                'email': gd['email'], 'first_name': gd['first_name'],
                'last_name': gd['last_name'], 'role': 'guide',
            })
            u.set_password('guide123')
            u.save()

            profile, _ = GuideProfile.objects.get_or_create(user=u, defaults={
                'bio': gd['bio'], 'tagline': gd['tagline'],
                'city': gd['city'], 'languages': gd['languages'],
                'price_per_hour': gd['price_per_hour'],
                'experience_years': gd['experience_years'],
                'license_number': gd['license_number'],
                'verification_status': 'approved',
                'rating': gd['rating'], 'total_reviews': gd['total_reviews'],
                'is_featured': gd['is_featured'],
            })
            guides.append(profile)

            # Availability: next 30 days
            for i in range(30):
                d = date.today() + timedelta(days=i)
                if d.weekday() != 6:  # Closed Sundays
                    GuideAvailability.objects.get_or_create(guide=profile, date=d, defaults={'is_available': True})

        # ── Tours ─────────────────────────────────────────────
        tour_data = [
            {
                'guide': guides[0], 'title': 'Old City Baku Walking Tour',
                'description': 'Explore the UNESCO World Heritage Icheri Sheher (Old City). Visit the Palace of the Shirvanshahs, Maiden Tower, caravanserais and ancient mosques with fascinating stories at every turn.',
                'category': 'historical', 'duration_hours': Decimal('3.0'), 'max_people': 8,
                'price_per_person': Decimal('35.00'),
                'itinerary': 'Meeting Point: Old City Gate (Gosha Gala)\n09:00 - Welcome & Introduction\n09:15 - Maiden Tower (Qiz Qalasi)\n10:00 - Palace of Shirvanshahs\n11:00 - Old Caravanserai & Bazaar\n11:45 - Ancient Mosques & Bath Houses\n12:00 - End at the city walls',
                'meeting_point': 'Icheri Sheher Metro Station, Gate 1',
            },
            {
                'guide': guides[0], 'title': 'Modern Baku Architecture Tour',
                'description': 'Discover Baku\'s stunning modern architecture — Flame Towers, Heydar Aliyev Center by Zaha Hadid, Crystal Hall, and the Caspian seafront. Perfect blend of past and future.',
                'category': 'city_tour', 'duration_hours': Decimal('4.0'), 'max_people': 10,
                'price_per_person': Decimal('40.00'),
                'itinerary': '10:00 - Heydar Aliyev Center\n11:30 - Flame Towers viewpoint\n12:00 - Nizami Street walk\n13:00 - Baku Boulevard & Caspian Sea\n14:00 - Tour ends',
                'meeting_point': 'Heydar Aliyev Center, main entrance',
            },
            {
                'guide': guides[1], 'title': 'Baku Food & Market Tour',
                'description': 'A culinary journey through Baku\'s best food spots: traditional qutab at Taza Bazaar, pomegranate wine tasting, piti soup, and fresh local produce. Includes tastings.',
                'category': 'food', 'duration_hours': Decimal('3.5'), 'max_people': 6,
                'price_per_person': Decimal('55.00'),
                'itinerary': '10:00 - Taza Bazaar (central market)\n11:00 - Traditional qutab cooking class\n12:00 - Local restaurant lunch\n13:00 - Azerbaijani sweets & tea ceremony\n13:30 - End',
                'meeting_point': 'Taza Bazaar main entrance',
            },
            {
                'guide': guides[2], 'title': 'Sheki Silk Road Day Trip',
                'description': 'Full-day excursion to the ancient Silk Road city of Sheki. See the Khan\'s Palace, traditional workshops, shebeke (stained glass) craftsmen, and taste halva.',
                'category': 'day_trip', 'duration_hours': Decimal('10.0'), 'max_people': 12,
                'price_per_person': Decimal('85.00'),
                'itinerary': '07:00 - Departure from Baku\n10:30 - Sheki Khan\'s Palace\n12:00 - Traditional lunch\n13:00 - Shebeke workshop\n14:00 - Old caravanserai\n17:00 - Return journey\n20:00 - Arrive Baku',
                'meeting_point': 'Baku Central Bus Station',
            },
            {
                'guide': guides[3], 'title': 'Baku Photography Walk',
                'description': 'Specially designed for photography enthusiasts. Visit the most photogenic locations in Baku at golden hour: Old City walls, Flame Towers reflections, Bayil steps.',
                'category': 'photography', 'duration_hours': Decimal('3.0'), 'max_people': 6,
                'price_per_person': Decimal('45.00'),
                'itinerary': '17:30 - Golden hour start at Boulevard\n18:00 - Old City walls at sunset\n19:00 - Flame Towers golden light\n19:30 - Night shots of illuminated city\n20:30 - End',
                'meeting_point': 'Baku Boulevard, Flag Square',
            },
            {
                'guide': guides[4], 'title': 'Gobustan Petroglyphs & Mud Volcanoes',
                'description': 'UNESCO World Heritage Gobustan rock carvings dating back 40,000 years, followed by a visit to the world\'s largest mud volcano field. Includes museum entry.',
                'category': 'historical', 'duration_hours': Decimal('6.0'), 'max_people': 8,
                'price_per_person': Decimal('65.00'),
                'itinerary': '09:00 - Departure from Baku\n10:00 - Gobustan Museum\n11:00 - Petroglyphs site walk\n12:30 - Lunch at local café\n13:30 - Mud Volcanoes (Dashgil)\n16:00 - Return to Baku',
                'meeting_point': 'Meet at guide\'s location (confirmed by chat)',
            },
        ]

        created_tours = []
        for td in tour_data:
            tour, _ = Tour.objects.get_or_create(
                guide=td['guide'], title=td['title'],
                defaults={k: v for k, v in td.items() if k not in ['guide', 'title']}
            )
            created_tours.append(tour)

        # ── Bookings & Payments ───────────────────────────────
        if tourists and guides:
            for i, tourist in enumerate(tourists[:2]):
                guide = guides[i % len(guides)]
                tour = created_tours[i % len(created_tours)]
                bdate = date.today() - timedelta(days=random.randint(5, 30))

                booking, created = Booking.objects.get_or_create(
                    tourist=tourist, guide=guide, booking_date=bdate,
                    defaults={
                        'tour': tour, 'people_count': random.randint(1, 3),
                        'total_price': tour.price_per_person * random.randint(1, 3),
                        'status': 'completed', 'booking_time': '10:00',
                    }
                )

                if created:
                    Payment.objects.get_or_create(booking=booking, defaults={
                        'amount': booking.total_price,
                        'status': 'completed',
                        'mock_transaction_id': 'TXN-' + 'DEMO' + str(i).zfill(8),
                        'card_last4': '4242',
                    })

                    Review.objects.get_or_create(booking=booking, defaults={
                        'tourist': tourist, 'guide': guide,
                        'rating': random.randint(4, 5),
                        'title': random.choice([
                            'Incredible experience!', 'Highly recommend!',
                            'Best tour in Baku!', 'Amazing guide!'
                        ]),
                        'body': random.choice([
                            'Anar was an exceptional guide. His knowledge of Azerbaijani history is remarkable. We learned so much during our tour!',
                            'Absolutely loved every moment. The guide took us to hidden spots we never would have found on our own.',
                            'Professional, punctual, and incredibly knowledgeable. Will book again on our next trip to Baku.',
                            'The food tour was a highlight of our entire trip to Azerbaijan. Leyla knows every great spot in the city!',
                        ]),
                    })

            # Upcoming confirmed booking
            future_date = date.today() + timedelta(days=5)
            booking2, _ = Booking.objects.get_or_create(
                tourist=tourists[0], guide=guides[1], booking_date=future_date,
                defaults={
                    'tour': created_tours[2], 'people_count': 2,
                    'total_price': created_tours[2].price_per_person * 2,
                    'status': 'confirmed', 'booking_time': '10:00',
                }
            )
            if _:
                Payment.objects.get_or_create(booking=booking2, defaults={
                    'amount': booking2.total_price, 'status': 'completed',
                    'mock_transaction_id': 'TXN-DEMO-UPCOMING', 'card_last4': '4242',
                })

        # ── Demo Chat Messages ────────────────────────────────
        if tourists and guides:
            t = tourists[0]
            g = guides[0].user
            msgs = [
                (t, g, 'Hello! I\'m interested in your Old City tour. Is it available next Saturday?'),
                (g, t, 'Hi John! Great to hear from you. Yes, I have availability this Saturday. Shall we book for 9 AM?'),
                (t, g, 'Perfect! 9 AM works great. Will you provide water during the tour?'),
                (g, t, 'Of course! I always bring water and snacks. The tour lasts about 3 hours. Looking forward to showing you Baku!'),
            ]
            for sender, receiver, content in msgs:
                ChatMessage.objects.get_or_create(
                    sender=sender, receiver=receiver, content=content,
                    defaults={'is_read': True}
                )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('\n' + '-' * 50)
        self.stdout.write('Demo Accounts:')
        self.stdout.write('  Admin:     admin / admin123')
        self.stdout.write('  Support:   support / support123')
        self.stdout.write('  Tourists:  tourist1, tourist2, tourist3 / tourist123')
        self.stdout.write('  Guides:    guide_anar, guide_leyla, guide_kamran,')
        self.stdout.write('             guide_nigar, guide_rashad / guide123')
        self.stdout.write('-' * 50 + '\n')
