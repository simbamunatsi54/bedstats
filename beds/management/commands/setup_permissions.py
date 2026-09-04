from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        # Administrator gets everything
        admin_group = Group.objects.get(name="Administrator")
        admin_group.permissions.set(
            Permission.objects.all()
        )

        # Health Information Officer
        hio = Group.objects.get(
            name="Health Information Officer"
        )

        hio_permissions = Permission.objects.filter(
            content_type__app_label="beds"
        )

        hio.permissions.set(hio_permissions)

        # Matron/Nurse
        nurse = Group.objects.get(
            name="Matron/Nurse"
        )

        nurse_permissions = Permission.objects.filter(
            content_type__app_label="beds",
            codename__in=[
                "view_ward",
                "view_bed",
                "change_bed",
                "view_patient",
                "view_admission",
                "add_admission",
                "change_admission",
                "view_discharge",
                "add_discharge",
                "view_transfer",
                "add_transfer",
            ]
        )

        nurse.permissions.set(nurse_permissions)

        # Records Officer
        records = Group.objects.get(
            name="Records Officer"
        )

        records_permissions = Permission.objects.filter(
            content_type__app_label="beds",
            codename__in=[
                "view_ward",
                "view_bed",
                "view_patient",
                "add_patient",
                "change_patient",
                "view_admission",
                "add_admission",
                "change_admission",
                "view_discharge",
                "add_discharge",
                "view_transfer",
                "view_death",
            ]
        )

        records.permissions.set(records_permissions)

        # Doctor
        doctor = Group.objects.get(
            name="Doctor"
        )

        doctor_permissions = Permission.objects.filter(
            content_type__app_label="beds",
            codename__in=[
                "view_ward",
                "view_bed",
                "view_patient",
                "view_admission",
                "add_admission",
                "change_admission",
                "view_discharge",
                "view_transfer",
                "view_death",
            ]
        )

        doctor.permissions.set(doctor_permissions)

        # Management - viewing only
        management = Group.objects.get(
            name="Management"
        )

        management_permissions = Permission.objects.filter(
            content_type__app_label="beds",
            codename__startswith="view_"
        )

        management.permissions.set(
            management_permissions
        )

        self.stdout.write(
            self.style.SUCCESS(
                "BedStats role permissions configured successfully."
            )
        )