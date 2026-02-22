from pydantic import BaseModel, Field, field_validator


class BookingRecord(BaseModel):
    id: str
    typeKey: str
    typeLabel: str
    typeDesc: str
    datetime: str
    name: str
    phone: str
    notes: str
    location: str
    status: str
    createdAt: int


class CreateBookingRequest(BaseModel):
    typeKey: str
    typeLabel: str
    typeDesc: str
    datetime: str
    name: str = Field(min_length=1, max_length=12)
    phone: str
    notes: str = Field(default="", max_length=60)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if len(v) != 11 or not v.isdigit() or not v.startswith("1"):
            raise ValueError("invalid phone")
        return v


class CreateBookingResponse(BaseModel):
    record: BookingRecord


class ListBookingsResponse(BaseModel):
    records: list[BookingRecord]
