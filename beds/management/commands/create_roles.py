from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        roles = [
            "Administrator",
            "Health Information Officer",
            "Matron/Nurse",
            "Records Officer",
            "Doctor",
            "Management",
        ]

        for role in roles:

            group, created = Group.objects.get_or_create(
                name=role
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {role}"
                    )
                )
            else:
                self.stdout.write(
                    f"Role already exists: {role}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "All BedStats roles are ready."
            )
        )