# TripAZ — Local Guide Marketplace for Azerbaijan

> A full-featured marketplace connecting foreign tourists with licensed local guides across Azerbaijan.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-gold)

</div>

---

## Overview

TripAZ is an MVP marketplace platform where tourists can discover verified local guides, book tours, chat in real time, and leave reviews — all in one place. Built with a mobile-first, dark-mode design system inspired by Azerbaijan's flag colors.

**Core user flows:**

- Tourist: Browse → Book → Pay → Chat → Review
- Guide: Apply → Get verified → Manage bookings → Earn
- Admin: Verify guides → Monitor KPIs → Handle support tickets

---

## Features

### For Tourists
- Register and browse guides by city, language, category, price, and rating
- View full guide profiles with bio, gallery, tours, availability calendar, and reviews
- Book a guide or tour with date, time, and people count
- Simulated payment processing with card preview
- Personal dashboard: booking history, favorites, status tracking
- Real-time chat with guides (AJAX polling)
- Leave reviews after completed bookings
- Save favorite guides with a heart toggle

### For Guides
- Submit an application with passport, license, and photo
- Admin-reviewed onboarding workflow
- Dashboard with revenue stats and booking management
- Accept or reject booking requests with a custom message
- Create, edit, and delete tours with photos and itinerary
- Manage an availability calendar
- Request withdrawals (tracked in DB)

### For Admins
- Custom web panel at `/admin-panel/` — no Django admin required for daily ops
- Guide verification workflow (approve / reject with message)
- Users list, booking overview, top-guide rankings
- Support ticket management
- Full Django admin at `/admin/` for power users

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Django 5.0 |
| Database | SQLite (zero-config) |
| Frontend | Vanilla HTML / CSS / JS — no frameworks |
| Auth | Django built-in auth + custom `User` model |
| File uploads | `ImageField` + Pillow |
| Templates | Django template engine + `django-widget-tweaks` |
| Chat | AJAX polling every 3 s |
| Deployment | Procfile (Heroku), railpack.json |

---

## Project Structure

```
TripAZ/
├── tripaz/              # Django project config (settings, urls, wsgi)
├── apps/
│   ├── accounts/        # User model, auth, tourist profiles & dashboard
│   ├── guides/          # Guide profiles, tours, availability
│   ├── bookings/        # Booking flow, mock payments, withdrawals
│   ├── chat/            # AJAX-polled messaging
│   ├── reviews/         # Review submission & rating aggregation
│   └── core/            # Home page, admin panel, notifications, support
├── templates/
│   ├── base.html        # Master layout (navbar, footer, flash messages)
│   ├── partials/        # Reusable includes
│   ├── core/            # Home, about, contacts, notifications, support
│   ├── accounts/        # Login, register, dashboards, favorites
│   ├── guides/          # Catalog, profile, tour pages, dashboard
│   ├── bookings/        # Booking form, payment, confirmation, detail
│   ├── chat/            # Inbox, conversation
│   ├── reviews/         # Review form
│   └── admin_panel/     # KPI dashboard, guide verification, user list
├── static/
│   ├── css/
│   │   ├── main.css     # Entry point (imports all CSS)
│   │   ├── tokens.css   # Design tokens: colors, spacing, motion
│   │   ├── base.css     # Reset, typography, layout utilities
│   │   ├── components.css  # Navbar, buttons, cards, forms, chat
│   │   └── pages.css    # Page-specific styles + responsive breakpoints
│   └── js/
│       ├── main.js      # Navbar, scroll reveal, favorites, price calc
│       └── chat.js      # AJAX polling, message send, auto-scroll
└── media/               # User-uploaded avatars, documents, tour images
```

---

## Quick Start

**Requirements:** Python 3.10+

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations and seed demo data
python manage.py migrate
python manage.py seed_data

# 3. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000**

---

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
MAPBOX_TOKEN=pk.your-mapbox-token-here
```

---

## Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Support | `support` | `support123` |
| Tourist | `tourist1` | `tourist123` |
| Tourist | `tourist2` | `tourist123` |
| Guide | `guide_anar` | `guide123` |
| Guide | `guide_leyla` | `guide123` |
| Guide | `guide_kamran` | `guide123` |
| Guide | `guide_nigar` | `guide123` |
| Guide | `guide_rashad` | `guide123` |

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page with hero search |
| `/guides/` | Guide catalog with sidebar filters |
| `/guides/<id>/` | Guide profile page |
| `/guides/tours/` | All tours catalog |
| `/accounts/login/` | Login |
| `/accounts/register/` | Tourist registration |
| `/guides/register/` | Guide application |
| `/accounts/dashboard/` | Tourist dashboard |
| `/guides/dashboard/` | Guide dashboard |
| `/chat/` | Messaging inbox |
| `/admin-panel/` | Admin analytics panel |
| `/admin/` | Django admin |

---

## Design System

The CSS is split into four layers loaded via `main.css`:

| File | Purpose |
|------|---------|
| `tokens.css` | CSS custom properties: color palette, spacing scale, typography, motion easing |
| `base.css` | Normalize, global typography, layout utilities, scroll-reveal animation |
| `components.css` | Navbar, buttons, guide cards (`.gc`), tour cards (`.tc`), forms, alerts, tables |
| `pages.css` | Hero, catalog, guide profile (`.gp-*`), booking wizard, chat, dashboard, footer |

**Palette highlights:** Navy spectrum (#060d18 → #254d85), gold accents, travel turquoise, sand neutrals.
**Responsive breakpoints:** 1024 px (tablet), 768 px (mobile), 480 px (small phone).

---

## Simulated / Mock Features

| Feature | Notes |
|---------|-------|
| Payment | Mock form — always succeeds, generates a fake transaction ID |
| Email | Console backend — emails are printed to the terminal |
| Withdrawals | Stored as `pending` in the DB; no real bank transfer |
| Chat | AJAX polling every 3 s — no WebSockets |
| Map | Mapbox JS ready — set `MAPBOX_TOKEN` in `.env` to activate |

---

## License

MIT — free to use, modify, and distribute.
