from django.contrib import admin
from .models import Ward, Bed, Patient, Admission, Discharge, Transfer, Death


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward_type', 'total_beds')
    search_fields = ('name', 'ward_type')


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'ward', 'status')
    list_filter = ('ward', 'status')
    search_fields = ('bed_number',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_number',
        'first_name',
        'last_name',
        'sex',
        'age',
        'diagnosis',
        'registration_date'
    )
    list_filter = ('sex',)
    search_fields = (
        'patient_number',
        'first_name',
        'last_name',
        'diagnosis'
    )

    @admin.register(Admission)
    class AdmissionAdmin(admin.ModelAdmin):
        list_display = (
            'patient',
            'bed',
            'admission_date',
            'expected_discharge_date',
            'diagnosis',
            'attending_department',
            'status',
        )

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "bed":
                kwargs["queryset"] = Bed.objects.filter(status="Available")

            return super().formfield_for_foreignkey(
                db_field, request, **kwargs
            )
        list_filter = (
            'status',
            'bed__ward',
            'admission_date',
        )

        search_fields = (
            'patient__patient_number',
            'patient__first_name',
            'patient__last_name',
            'bed__bed_number',
            'diagnosis',
        )

        @admin.register(Discharge)
        class DischargeAdmin(admin.ModelAdmin):
            list_display = (
                'admission',
                'discharge_date',
                'discharge_reason',
                'remarks',
            )

            list_filter = (
                'discharge_date',
            )

            search_fields = (
                'admission__patient__patient_number',
                'admission__patient__first_name',
                'admission__patient__last_name',
            )

        @admin.register(Transfer)
        class TransferAdmin(admin.ModelAdmin):
            list_display = (
                'admission',
                'from_bed',
                'to_bed',
                'transfer_date',
                'reason',
            )

            list_filter = (
                'transfer_date',
                'from_bed__ward',
                'to_bed__ward',
            )

            search_fields = (
                'admission__patient__patient_number',
                'admission__patient__first_name',
                'admission__patient__last_name',
                'reason',
            )

            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                if db_field.name == 'to_bed':
                    kwargs['queryset'] = Bed.objects.filter(
                        status='Available'
                    )

                return super().formfield_for_foreignkey(
                    db_field, request, **kwargs
                )

            @admin.register(Death)
            class DeathAdmin(admin.ModelAdmin):
                list_display = (
                    'admission',
                    'death_date',
                    'cause_of_death',
                    'remarks',
                )

                list_filter = (
                    'death_date',
                )

                search_fields = (
                    'admission__patient__patient_number',
                    'admission__patient__first_name',
                    'admission__patient__last_name',
                    'cause_of_death',
                )

