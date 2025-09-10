from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_message_user_alter_roommember_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]

