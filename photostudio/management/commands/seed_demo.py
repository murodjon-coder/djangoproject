"""Namoyish uchun demo ma'lumotlar: python manage.py seed_demo

Buyruqni bir necha marta ishga tushirsa ham, bir xil yozuvlar takrorlanmaydi.
"""
import datetime
import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFilter

from photostudio.models import Category, Client, Photo, Session

PALETTES = {
    "To'y": ((250, 214, 196), (196, 120, 128), (90, 52, 70)),
    "Oilaviy": ((255, 226, 170), (230, 140, 80), (70, 60, 50)),
    "Bolalar": ((190, 228, 250), (120, 180, 230), (50, 90, 130)),
    "Portret": ((60, 56, 70), (120, 100, 110), (25, 22, 30)),
    "Studiya": ((235, 235, 235), (170, 170, 175), (40, 40, 45)),
    "Tabiat": ((200, 235, 210), (110, 170, 120), (40, 80, 55)),
}

CLIENTS = [
    ("Aziza Rahimova", "+998 90 123 45 67", "aziza@example.com"),
    ("Bekzod Tursunov", "+998 93 555 12 34", "bekzod@example.com"),
    ("Malika va Sardor Yo'ldoshevlar", "+998 97 700 80 90", ""),
    ("Nodira Ismoilova", "+998 99 321 65 87", "nodira@example.com"),
]

# (mijoz indeksi, fotograf, necha kun keyin (+) / oldin (-), soat, narx, holat, joy)
SESSIONS = [
    (2, "Murodjon", -40, 15, 2_500_000, Session.Status.DONE, "Botanika bog'i"),
    (0, "Dilnoza Karimova", -18, 11, 800_000, Session.Status.DONE, "Asosiy studiya"),
    (1, "Murodjon", -10, 16, 600_000, Session.Status.DONE, "Asosiy studiya"),
    (3, "Murodjon", -5, 10, 500_000, Session.Status.CANCELLED, "Asosiy studiya"),
    (0, "Murodjon", 3, 14, 900_000, Session.Status.PLANNED, "Asosiy studiya"),
    (3, "Dilnoza Karimova", 9, 12, 1_200_000, Session.Status.PLANNED, "Tashqi joy: Amir Temur xiyoboni"),
]

# (nomi, fotograf, kategoriya, sessiya indeksi)
PHOTOS = [
    ("Kelin-kuyov portreti", "Murodjon", "To'y", 0),
    ("Bog'dagi to'y lahzasi", "Murodjon", "Tabiat", 0),
    ("Oilaviy fotosessiya", "Dilnoza Karimova", "Oilaviy", 1),
    ("Bolalar fotosessiyasi", "Murodjon", "Bolalar", 1),
    ("Studiyadagi portret", "Murodjon", "Portret", 2),
    ("Biznes portret", "Murodjon", "Studiya", 2),
]


def make_image(palette, seed, size=(1200, 900)):
    """Fotosuratga o'xshash namuna rasm (gradient + yorug'lik + siluetlar)."""
    rnd = random.Random(seed)
    width, height = size
    top, mid, dark = palette
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(top[i] * (1 - t) + mid[i] * t) for i in range(3)))
    cx, cy, r = rnd.randint(200, width - 200), rnd.randint(120, 320), rnd.randint(70, 130)
    glow = Image.new("L", size, 0)
    ImageDraw.Draw(glow).ellipse((cx - 2 * r, cy - 2 * r, cx + 2 * r, cy + 2 * r), fill=110)
    img = Image.composite(Image.new("RGB", size, (255, 248, 230)), img, glow.filter(ImageFilter.GaussianBlur(80)))
    draw = ImageDraw.Draw(img)
    people = rnd.randint(1, 3)
    for k in range(people):
        px = int(width * (k + 1) / (people + 1)) + rnd.randint(-40, 40)
        scale = rnd.uniform(.85, 1.1)
        head, base = int(70 * scale), height - 40
        draw.ellipse((px - head, base - int(470 * scale), px + head, base - int(470 * scale) + 2 * head), fill=dark)
        draw.rounded_rectangle((px - int(150 * scale), base - int(320 * scale), px + int(150 * scale), height + 60),
                               radius=int(120 * scale), fill=dark)
    buffer = io.BytesIO()
    img.filter(ImageFilter.GaussianBlur(1.2)).save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()


class Command(BaseCommand):
    help = "Fotostudiya uchun demo ma'lumotlarni (kategoriya, mijoz, fotosessiya, surat) yaratadi."

    def handle(self, *args, **options):
        categories = {name: Category.objects.get_or_create(name=name)[0] for name in PALETTES}

        clients = [
            Client.objects.get_or_create(full_name=name, defaults={'phone': phone, 'email': email})[0]
            for name, phone, email in CLIENTS
        ]

        today = timezone.localdate()
        sessions = []
        for client_idx, photographer, days, hour, price, status, location in SESSIONS:
            when = timezone.make_aware(datetime.datetime.combine(
                today + datetime.timedelta(days=days), datetime.time(hour, 0),
            ))
            session, _ = Session.objects.get_or_create(
                client=clients[client_idx],
                photographer=photographer,
                status=status,
                price=price,
                defaults={'scheduled_at': when, 'location': location},
            )
            sessions.append(session)

        for i, (title, photographer, category_name, session_idx) in enumerate(PHOTOS):
            session = sessions[session_idx]
            photo, created = Photo.objects.get_or_create(
                title=title,
                defaults={
                    'photographer': photographer,
                    'date': timezone.localdate(session.scheduled_at),
                    'category': categories[category_name],
                },
            )
            if photo.session is None:
                photo.session = session
            if photo.category is None:
                photo.category = categories[category_name]
            if not photo.image:
                photo.image.save(f"demo_{i + 1}.jpg", ContentFile(make_image(PALETTES[category_name], seed=i)), save=False)
            photo.save()

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {Category.objects.count()} kategoriya, {Client.objects.count()} mijoz, "
            f"{Session.objects.count()} fotosessiya, {Photo.objects.count()} surat."
        ))
