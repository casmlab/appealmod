# Generated by Django 5.0.6 on 2024-09-22 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_alter_signupdata_subreddit_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banappealdata',
            name='allowed_comments',
            field=models.TextField(blank=True, null=True, verbose_name='Which of the following comment(s) do you think should be allowed in our community?'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='describe_actions',
            field=models.TextField(blank=True, null=True, verbose_name='Can you describe your actions that led to the ban and the circumstances that made you act that way?'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='describe_rule',
            field=models.TextField(blank=True, null=True, verbose_name='Can you describe the rule in your own words?'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='what_steps',
            field=models.TextField(blank=True, null=True, verbose_name="What steps will you take to ensure that you don't do this again?"),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='why_appealing',
            field=models.CharField(blank=True, max_length=254, null=True, verbose_name='Why are you appealing your ban?'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='why_banned',
            field=models.TextField(blank=True, null=True, verbose_name='Find and copy/paste here the note from mods on why you were banned'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='will_not_repeat',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Are you willing to pledge that you will not repeat such actions in the future?'),
        ),
        migrations.AlterField(
            model_name='banappealdata',
            name='wrong_actions',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Do you think your actions were wrong?'),
        ),
    ]
