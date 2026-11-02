from pydantic import BaseModel, ConfigDict, Field, model_validator


class PropertyFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)

    OverallQual: int = Field(ge=1, le=10, title="Jakość wykończenia (1–10)")
    GrLivArea: float = Field(gt=0, le=20000, title="Powierzchnia nadziemna (ft²)")
    YearBuilt: int = Field(ge=1700, le=2100, title="Rok budowy")
    LotArea: float | None = Field(default=None, gt=0, le=1000000, title="Powierzchnia działki (ft²)")
    TotalBsmtSF: float | None = Field(default=None, ge=0, le=20000, title="Powierzchnia piwnicy (ft²)")
    GarageCars: int | None = Field(default=None, ge=0, le=10, title="Miejsca w garażu")
    FullBath: int | None = Field(default=None, ge=0, le=10, title="Pełne łazienki")
    BedroomAbvGr: int | None = Field(default=None, ge=0, le=20, title="Sypialnie nad ziemią")
    TotRmsAbvGrd: int | None = Field(default=None, ge=1, le=40, title="Pokoje nad ziemią (bez łazienek)")
    YearRemodAdd: int | None = Field(default=None, ge=1700, le=2100, title="Rok remontu / rozbudowy")
    Neighborhood: str | None = Field(default=None, min_length=1, max_length=50, title="Dzielnica (kod Ames)")
    HouseStyle: str | None = Field(default=None, min_length=1, max_length=50, title="Typ domu (kod Ames)")
    BldgType: str | None = Field(default=None, min_length=1, max_length=50, title="Rodzaj zabudowy (kod Ames)")

    @model_validator(mode="after")
    def consistent_years(self):
        if self.YearRemodAdd is not None and self.YearRemodAdd < self.YearBuilt:
            raise ValueError("Rok remontu nie może poprzedzać roku budowy.")
        return self


class Prediction(BaseModel):
    price_usd: float
    currency: str = "USD"
    model_name: str
    model_version: str
