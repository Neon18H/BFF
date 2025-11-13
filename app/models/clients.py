from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class IcaPeriodicity(str, Enum):
    mensual = "mensual"
    bimestral = "bimestral"
    trimestral = "trimestral"
    anual = "anual"


class TaxProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    identificacion_tipo: str = Field(alias="identificacionTipo", default="CC")
    periodicidad_iva: str = Field(alias="periodicidadIVA", default="bimestral")
    ica_municipio: Optional[str] = Field(alias="icaMunicipio", default=None)
    ica_periodicidad: IcaPeriodicity = Field(alias="icaPeriodicidad", default=IcaPeriodicity.bimestral)
    aplica_renta: bool = Field(alias="aplicaRenta", default=True)
    aplica_rete_fuente: bool = Field(alias="aplicaReteFuente", default=True)
    aplica_exogena: bool = Field(alias="aplicaExogena", default=True)
    usar_dv_en_calculo: bool = Field(alias="usarDVEnCalculo", default=False)


class DocumentRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    name: str
    type: str
    size_bytes: Optional[int] = Field(alias="sizeBytes", default=None)
    path: Optional[str] = None


class PaymentState(str, Enum):
    pendiente = "pendiente"
    pagado = "pagado"


class ClientBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name_or_business: str = Field(alias="nameOrBusiness")
    identificacion: str
    contact: Optional[str] = None
    notes: Optional[str] = None
    payment_state: PaymentState = Field(alias="paymentState")
    payment_amount: Optional[float] = Field(alias="paymentAmount", default=None)
    tags: List[str] = []
    documents: List[DocumentRef] = []
    tax_profile: Optional[TaxProfile] = Field(alias="taxProfile", default=None)


class Client(ClientBase):
    id: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name_or_business: Optional[str] = Field(alias="nameOrBusiness", default=None)
    identificacion: Optional[str] = None
    contact: Optional[str] = None
    notes: Optional[str] = None
    payment_state: Optional[PaymentState] = Field(alias="paymentState", default=None)
    payment_amount: Optional[float] = Field(alias="paymentAmount", default=None)
    tags: Optional[List[str]] = None
    documents: Optional[List[DocumentRef]] = None
    tax_profile: Optional[TaxProfile] = Field(alias="taxProfile", default=None)


class ClientList(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    items: List[Client]
    total: int
    page: int
    page_size: int


__all__ = [
    "IcaPeriodicity",
    "TaxProfile",
    "DocumentRef",
    "PaymentState",
    "Client",
    "ClientCreate",
    "ClientUpdate",
    "ClientList",
]
