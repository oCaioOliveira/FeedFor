# Generated by Django 4.2.13 on 2024-06-17 07:53

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('openai_api_key', models.CharField(max_length=255)),
                ('model', models.CharField(max_length=255)),
                ('system_content', models.TextField()),
                ('max_tokens', models.IntegerField()),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('external_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('model_settings', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='subjects', to='core.modelsettings')),
                ('students', models.ManyToManyField(related_name='subjects', to='core.student')),
                ('teachers', models.ManyToManyField(related_name='subjects', to='core.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='results', to='core.questionnaire')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='results', to='core.student')),
            ],
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='students',
            field=models.ManyToManyField(related_name='questionnaires', to='core.student'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='questionnaires', to='core.subject'),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('subcontent', models.CharField(max_length=255)),
                ('correct_answer', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='items', to='core.questionnaire')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.JSONField(default=list)),
                ('feedback_explanation', models.TextField(blank=True, null=True)),
                ('feedback_improve_suggestions', models.TextField(blank=True, null=True)),
                ('correct', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='answers', to='core.item')),
                ('students', models.ManyToManyField(related_name='answers', to='core.student')),
            ],
        ),
    ]
