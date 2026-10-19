from django.db import migrations

GROUP_NAME = 'Xodimlar'


def create_group(apps, schema_editor):
    """Fotostudiya xodimlari guruhi: galereya, mijozlar, fotosessiyalar va statistikaga kirish huquqi."""
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=GROUP_NAME)


def delete_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('photostudio', '0005_tag_client_user'),
    ]

    operations = [
        migrations.RunPython(create_group, delete_group),
    ]
