from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from enum import Enum


class CareerLevel(str, Enum):
    ENTRY = "ENTRY"
    MID = "MID"
    SENIOR = "SENIOR"
    EXECUTIVE = "EXECUTIVE"


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    ASSOCIATE = "ASSOCIATE"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    PHD = "PHD"


class CandidateStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    HIRED = "HIRED"
    REJECTED = "REJECTED"


class CandidateSource(str, Enum):
    ADVERTISING = "ADVERTISING"
    COLD_CALL = "COLD_CALL"
    EVENT = "EVENT"
    GITHUB = "GITHUB"
    JOB_BOARD = "JOB_BOARD"
    JOB_FAIR = "JOB_FAIR"
    LINKEDIN = "LINKEDIN"
    OTHER = "OTHER"
    REFERRAL = "REFERRAL"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    UNKNOWN = "UNKNOWN"
    WEBSITE = "WEBSITE"


class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    career_level: CareerLevel = CareerLevel.ENTRY
    years_of_experience: Optional[int] = None
    education_level: EducationLevel
    skills: List[str]
    languages: List[str]
    location: Optional[str] = None
    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    currency: str = "USD"
    notice_period: Optional[int] = 14
    notice_period_unit: Optional[str] = "days"
    visa_status: Optional[str] = None
    immigration_status: Optional[str] = None
    immigration_country: Optional[str] = None
    status: CandidateStatus = CandidateStatus.ACTIVE
    source: CandidateSource = CandidateSource.LINKEDIN
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: str
    tenant_id: Optional[str] = None
    created_at: int
    updated_at: int
