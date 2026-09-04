from django.core.management.base import BaseCommand
from beds.models import Ward, Bed


class Command(BaseCommand):
    help = "Create exactly 30 beds for each of the four hospital wards"

    def handle(self, *args, **kwargs):

        ward_prefixes = {
            "Childrens Ward": "CW",
            "Mental Health Unit Ward": "MHU",
            "Female Ward": "FW",
            "Male Ward": "MW",
        }

        for ward_name, prefix in ward_prefixes.items():

            try:
                ward = Ward.objects.get(name=ward_name)
            except Ward.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Ward not found: {ward_name}"
                    )
                )
                continue

            for number in range(1, 31):

                bed_number = f"{prefix}{number:02d}"

                Bed.objects.get_or_create(
                    ward=ward,
                    bed_number=bed_number,
                    defaults={"status": "Available"}
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Bed creation completed: 30 beds for each of the 4 wards."
            )
        )