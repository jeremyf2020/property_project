from django.db import models
from api.coordinates.models import Coordinates
from api.utils import auto_assign_sector
from django.core.validators import MinValueValidator, MaxValueValidator

class School(models.Model):
    """
    Official UK School Entity.
    """
    # Identifiers
    name = models.CharField(max_length=255)
    urn = models.CharField(max_length=20, unique=True)
    
    # Location
    street = models.CharField(max_length=255, blank=True, null=True)
    locality = models.CharField(max_length=255, blank=True, null=True)
    address3 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=20)
    
    # Details
    school_type = models.CharField(max_length=100, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True, null=True)

    # Phase Flags
    is_primary = models.BooleanField(default=False)
    is_secondary = models.BooleanField(default=False)
    is_post16 = models.BooleanField(default=False)
    
    # Age Range (Integers allow for "Find schools for 4 year olds")
    minimum_age = models.IntegerField(null=True, blank=True)
    maximum_age = models.IntegerField(null=True, blank=True)

    # The Link
    postcode_sector = models.ForeignKey(Coordinates, on_delete=models.CASCADE, related_name='schools')

    def save(self, *args, **kwargs):
        """ auto-assign the sector """
        auto_assign_sector(self)
        super().save(*args, **kwargs)

    @property
    def phase(self):
        """
        Returns a single string describing the school phase.
        """
        if self.is_primary and self.is_secondary:
            return "All-through"
        if self.is_primary:
            return "Primary"
        if self.is_secondary:
            return "Secondary"
        if self.is_post16:
            return "Post-16"
        return "Not Specified"

    @property
    def age_range_str(self):
        """ Returns readable string '4-11' """
        if self.minimum_age is not None and self.maximum_age is not None:
            return f"{self.minimum_age}-{self.maximum_age}"
        return ""

    def __str__(self):
        return f"{self.name}"

class KS2Performance(models.Model):
    """
    Key Stage 2 (KS2) Results for Primary Schools
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='ks2_results')
    academic_year = models.IntegerField(
        validators=[MinValueValidator(1800), MaxValueValidator(2200)],
        help_text="The academic year of publication (Format: YYYY)"
    )    
    # Column: PTRWM_EXP (% meeting expected standard in Reading, Writing, Maths)
    pct_meeting_expected = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    
    # Column: READ_AVERAGE (Average Scaled Score in Reading)
    reading_score = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    
    # Column: MAT_AVERAGE (Average Scaled Score in Maths)
    maths_score = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    class Meta:
        unique_together = ('school', 'academic_year')

    def __str__(self):
        return f"{self.school.name} KS2 ({self.academic_year}): {self.pct_meeting_expected}%"

class KS4Performance(models.Model):
    """
    Key Stage 4 (KS4) / GCSE Results
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='ks4_results')
    academic_year = models.IntegerField(
        validators=[MinValueValidator(1800), MaxValueValidator(2200)],
        help_text="The academic year of publication (Format: YYYY)"
    )
    # Column: P8MEA (Progress 8 Score) (compare to KS2 added value)
    progress_8 = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    
    # Column: ATT8SCR (Attainment 8 Score) (average score across 8 subjects)
    attainment_8 = models.DecimalField(max_digits=5, decimal_places=1, null=True)

    class Meta:
        unique_together = ('school', 'academic_year')

    def __str__(self):
        return f"{self.school.name} KS4 ({self.academic_year}): P8 {self.progress_8}% | A8 {self.attainment_8}"


class KS5Performance(models.Model):
    """
    Key Stage 5 (A-Level / College) Results.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='ks5_results')
    academic_year = models.IntegerField(
        validators=[MinValueValidator(1800), MaxValueValidator(2200)],
        help_text="The academic year of publication (Format: YYYY)"
    )
    # A-Level Specifics
    # Column: TALLPPE_ALEV_1618 (Average Points Per Entry - A Level)
    a_level_points = models.DecimalField(max_digits=5, decimal_places=2, null=True, help_text="Average points per entry")
    
    # Column: TALLPPEGRD_ALEV_1618 (Average Grade - e.g. 'C+', 'B-')
    a_level_grade = models.CharField(max_length=5, null=True, blank=True, help_text="Average grade (e.g. B-)")

    # Academic Qualifications (Broader than just A-Levels)
    # Column: TALLPPE_ACAD_1618
    academic_points = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    # Column: TALLPPEGRD_ACAD_1618
    academic_grade = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        unique_together = ('school', 'academic_year')

    def __str__(self):
        return f"{self.school.name} KS5 ({self.academic_year}): {self.a_level_grade}"