"""Data models used by the DANFSe renderer."""

from __future__ import annotations

from dataclasses import dataclass


MISSING_VALUE = "-"
CONSULTA_PUBLICA_URL = "https://www.nfse.gov.br/ConsultaPublica/?tpc=1&chave="
NFSE_LOGO_URL = (
    "https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/logos-da-nfs-e/"
    "Logo%20-%20NFS-e%20-%20Horizontal.png/@@images/image"
)


@dataclass(frozen=True)
class HeaderData:
    """Header and identification data required in NT 008 section 2.1.2."""

    access_key: str
    nfse_number: str
    competence_date: str
    nfse_issued_at: str
    dps_number: str
    dps_series: str
    dps_issued_at: str
    issuer: str
    status: str
    purpose: str
    issuer_city: str
    issuer_state: str
    generator_environment: str
    national_environment: str
    show_municipality: bool = True
    debit_note_type: str = MISSING_VALUE
    credit_note_type: str = MISSING_VALUE

    @property
    def municipality_line(self) -> str:
        if not self.show_municipality:
            return ""
        if self.issuer_city == MISSING_VALUE and self.issuer_state == MISSING_VALUE:
            return MISSING_VALUE
        if self.issuer_state == MISSING_VALUE:
            return f"Município: {self.issuer_city}"
        return f"Município: {self.issuer_city} / {self.issuer_state}"

    @property
    def consultation_url(self) -> str:
        return f"{CONSULTA_PUBLICA_URL}{self.access_key}"

    @property
    def is_restricted_production(self) -> bool:
        return self.national_environment == "2"


@dataclass(frozen=True)
class ProviderData:
    """Provider/supplier data required in NT 008 section 2.1.3."""

    tax_id: str
    municipal_registration: str
    phone: str
    name: str
    municipality_state: str
    ibge_cep: str
    address: str
    email: str
    simples_nacional: str
    sn_tax_regime: str
    ibs_cbs_sn_tax_regime: str = MISSING_VALUE


@dataclass(frozen=True)
class CustomerData:
    """Customer/acquirer data required in NT 008 section 2.1.4."""

    tax_id: str
    municipal_registration: str
    phone: str
    name: str
    municipality_state: str
    ibge_cep: str
    address: str
    email: str
    unidentified_message: str = ""


@dataclass(frozen=True)
class DestinationData:
    """Destination data required in NT 008 section 2.1.5."""

    tax_id: str
    phone: str
    name: str
    municipality_state: str
    ibge_cep: str
    address: str
    email: str
    unidentified_message: str = ""


@dataclass(frozen=True)
class IntermediaryData:
    """Intermediary data required in NT 008 section 2.1.6."""

    tax_id: str
    municipal_registration: str
    phone: str
    name: str
    municipality_state: str
    ibge_cep: str
    address: str
    email: str
    unidentified_message: str = ""


@dataclass(frozen=True)
class ServiceData:
    """Service data required in NT 008 section 2.1.7."""

    taxation_code: str
    nbs_code: str
    location: str
    taxation_description: str
    service_description: str
    simples_nacional_activity: str = MISSING_VALUE


@dataclass(frozen=True)
class MunicipalTaxationData:
    """Municipal taxation data required in NT 008 section 2.1.8."""

    taxation_type: str
    incidence_location: str
    special_regime: str
    immunity_type: str
    suspension: str
    suspension_process: str
    municipal_benefit: str
    bm_calculation: str
    total_deductions_reductions: str
    unconditional_discount: str
    issqn_base: str
    applied_rate: str
    retention: str
    issqn_amount: str
    non_taxable_message: str = ""
    suppress_optional_row_one: bool = False
    suppress_optional_row_two: bool = False


@dataclass(frozen=True)
class FederalTaxationData:
    """Federal taxation data required in NT 008 section 2.1.9."""

    irrf: str
    previdenciaria_retida: str
    sociais_retidas: str
    pis_debito: str
    cofins_debito: str
    retention_description: str
    show_legacy_piscofins_row: bool = True


@dataclass(frozen=True)
class IbsCbsTaxationData:
    """IBS/CBS taxation data required in NT 008 section 2.1.10."""

    cst_classification: str
    operation_indicator: str
    exclusions_reductions: str
    base_after_reductions: str
    rate_reductions: str
    ibs_rates: str
    ibs_municipal_effective_rate: str
    ibs_municipal_amount: str
    ibs_state_effective_rate: str
    ibs_state_amount: str
    ibs_total: str
    cbs_rate: str
    cbs_effective_rate: str
    cbs_total: str
    adjustment_ibs: str = MISSING_VALUE
    adjustment_cbs: str = MISSING_VALUE
    final_consumer_indicator: str = MISSING_VALUE
    sn_gross_revenue: str = MISSING_VALUE
    sn_ibs_rate: str = MISSING_VALUE
    sn_ibs_amount: str = MISSING_VALUE
    sn_cbs_rate: str = MISSING_VALUE
    sn_cbs_amount: str = MISSING_VALUE
    real_estate_summary: str = MISSING_VALUE
    movable_property_count: str = MISSING_VALUE
    linked_payment_count: str = MISSING_VALUE


@dataclass(frozen=True)
class TotalData:
    """Total values required in NT 008 section 2.1.11."""

    service_amount: str
    unconditional_discount: str
    conditional_discount: str
    total_retentions: str
    nfse_net_amount: str
    ibs_cbs_total: str
    nfse_net_amount_with_ibs_cbs: str


@dataclass(frozen=True)
class ComplementaryInfoData:
    """Complementary information required in NT 008 section 2.1.12."""

    text: str


@dataclass(frozen=True)
class ReceiptData:
    """Optional receipt block required in NT 008 section 2.1.13 when printed."""

    acknowledgement_date: str
    identification_signature: str
    nfse_number_access_key: str


@dataclass(frozen=True)
class DanfseData:
    """Implemented DANFSe data blocks."""

    header: HeaderData
    provider: ProviderData
    customer: CustomerData
    destination: DestinationData
    intermediary: IntermediaryData
    service: ServiceData
    municipal_taxation: MunicipalTaxationData
    federal_taxation: FederalTaxationData
    ibs_cbs_taxation: IbsCbsTaxationData
    total: TotalData
    complementary_info: ComplementaryInfoData
    receipt: ReceiptData
