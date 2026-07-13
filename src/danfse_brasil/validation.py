"""Validation helpers for implemented DANFSe blocks."""

from __future__ import annotations

from dataclasses import dataclass

from . import layout
from .models import DanfseData, MISSING_VALUE


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"


EXPECTED_BOXES = {
    "HEADER": layout.Box(1.16, 20.40, 0.30, 0.30),
    "LOGO": layout.Box(0.85, 4.00, 0.49, 0.44),
    "TITLE": layout.Box(1.16, 10.19, 5.41, 0.30),
    "MUNICIPALITY_ENV": layout.Box(1.16, 5.09, 15.62, 0.30),
    "MUNICIPALITY": layout.Box(0.64, 5.09, 15.62, 0.30),
    "GENERATOR_ENV": layout.Box(0.24, 5.09, 15.62, 0.97),
    "NATIONAL_ENV": layout.Box(0.24, 5.09, 15.62, 1.22),
    "NFSE_DATA": layout.Box(2.84, 20.40, 0.30, 1.48),
    "ACCESS_KEY": layout.Box(0.77, 15.30, 0.30, 1.48),
    "NFSE_NUMBER": layout.Box(0.67, 5.09, 0.30, 2.27),
    "COMPETENCE": layout.Box(0.67, 5.09, 5.41, 2.27),
    "NFSE_ISSUED_AT": layout.Box(0.67, 5.09, 10.51, 2.27),
    "DPS_NUMBER": layout.Box(0.67, 5.09, 0.30, 2.96),
    "DPS_SERIES": layout.Box(0.67, 5.09, 5.41, 2.96),
    "DPS_ISSUED_AT": layout.Box(0.67, 5.09, 10.51, 2.96),
    "ISSUER": layout.Box(0.67, 5.09, 0.30, 3.65),
    "STATUS": layout.Box(0.67, 5.09, 5.41, 3.65),
    "PURPOSE": layout.Box(0.67, 5.09, 10.51, 3.65),
    "QR_CODE": layout.Box(1.52, 1.52, 17.48, 1.67),
    "QR_COMPLEMENT": layout.Box(0.68, 4.72, 15.80, 3.36),
    "IDENTIFICATION_PROVIDER_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 4.30),
    "PROVIDER_BLOCK": layout.Box(2.57, 20.40, 0.30, 4.34),
    "PROVIDER_TITLE": layout.Box(0.63, 5.09, 0.30, 4.34),
    "PROVIDER_TAX_ID": layout.Box(0.63, 5.09, 5.41, 4.34),
    "PROVIDER_MUNICIPAL_REGISTRATION": layout.Box(0.63, 5.09, 10.51, 4.34),
    "PROVIDER_PHONE": layout.Box(0.63, 5.09, 15.62, 4.34),
    "PROVIDER_NAME": layout.Box(0.63, 10.19, 0.30, 4.98),
    "PROVIDER_MUNICIPALITY_STATE": layout.Box(0.63, 5.09, 10.51, 4.98),
    "PROVIDER_IBGE_CEP": layout.Box(0.63, 5.09, 15.62, 4.98),
    "PROVIDER_ADDRESS": layout.Box(0.63, 10.19, 0.30, 5.62),
    "PROVIDER_EMAIL": layout.Box(0.63, 10.19, 10.51, 5.62),
    "PROVIDER_SIMPLES_NACIONAL": layout.Box(0.63, 5.09, 0.30, 6.28),
    "PROVIDER_SN_TAX_REGIME": layout.Box(0.63, 10.19, 10.51, 6.28),
    "PROVIDER_CUSTOMER_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 6.89),
    "CUSTOMER_BLOCK": layout.Box(1.93, 20.40, 0.30, 6.92),
    "CUSTOMER_TITLE": layout.Box(0.63, 5.09, 0.30, 6.92),
    "CUSTOMER_TAX_ID": layout.Box(0.63, 5.09, 5.41, 6.92),
    "CUSTOMER_MUNICIPAL_REGISTRATION": layout.Box(0.63, 5.09, 10.51, 6.92),
    "CUSTOMER_PHONE": layout.Box(0.63, 5.09, 15.62, 6.92),
    "CUSTOMER_NAME": layout.Box(0.63, 10.19, 0.30, 7.56),
    "CUSTOMER_MUNICIPALITY_STATE": layout.Box(0.63, 5.09, 10.51, 7.56),
    "CUSTOMER_IBGE_CEP": layout.Box(0.63, 5.09, 15.62, 7.56),
    "CUSTOMER_ADDRESS": layout.Box(0.63, 10.19, 0.30, 8.22),
    "CUSTOMER_EMAIL": layout.Box(0.63, 10.19, 10.51, 8.22),
    "CUSTOMER_DESTINATION_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 8.84),
    "DESTINATION_BLOCK": layout.Box(0.63, 20.40, 0.30, 8.86),
    "DESTINATION_TITLE": layout.Box(0.63, 5.09, 0.30, 8.86),
    "DESTINATION_UNIDENTIFIED": layout.Box(0.63, 20.40, 0.30, 8.86),
    "DESTINATION_TAX_ID": layout.Box(0.63, 5.09, 5.41, 8.86),
    "DESTINATION_PHONE": layout.Box(0.63, 5.09, 15.62, 8.86),
    "DESTINATION_NAME": layout.Box(0.63, 10.19, 0.30, 9.50),
    "DESTINATION_MUNICIPALITY_STATE": layout.Box(0.63, 5.09, 10.51, 9.50),
    "DESTINATION_IBGE_CEP": layout.Box(0.63, 5.09, 15.62, 9.50),
    "DESTINATION_ADDRESS": layout.Box(0.63, 10.19, 0.30, 10.16),
    "DESTINATION_EMAIL": layout.Box(0.63, 10.19, 10.51, 10.16),
    "DESTINATION_INTERMEDIARY_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 10.78),
    "INTERMEDIARY_BLOCK": layout.Box(1.93, 20.40, 0.30, 10.80),
    "INTERMEDIARY_TITLE": layout.Box(0.63, 5.09, 0.30, 10.80),
    "INTERMEDIARY_UNIDENTIFIED": layout.Box(0.63, 20.40, 0.30, 10.80),
    "INTERMEDIARY_TAX_ID": layout.Box(0.63, 5.09, 5.41, 10.80),
    "INTERMEDIARY_MUNICIPAL_REGISTRATION": layout.Box(0.63, 5.09, 10.51, 10.80),
    "INTERMEDIARY_PHONE": layout.Box(0.63, 5.09, 15.62, 10.80),
    "INTERMEDIARY_NAME": layout.Box(0.63, 10.19, 0.30, 11.44),
    "INTERMEDIARY_MUNICIPALITY_STATE": layout.Box(0.63, 5.09, 10.51, 11.44),
    "INTERMEDIARY_IBGE_CEP": layout.Box(0.63, 5.09, 15.62, 11.44),
    "INTERMEDIARY_ADDRESS": layout.Box(0.63, 10.19, 0.30, 12.09),
    "INTERMEDIARY_EMAIL": layout.Box(0.63, 10.19, 10.51, 12.09),
    "INTERMEDIARY_SERVICE_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 12.72),
    "SERVICE_BLOCK": layout.Box(1.68, 20.40, 0.30, 12.74),
    "SERVICE_TITLE": layout.Box(0.63, 5.09, 0.30, 12.74),
    "SERVICE_TAXATION_CODE": layout.Box(0.63, 5.09, 5.41, 12.74),
    "SERVICE_NBS_CODE": layout.Box(0.63, 5.09, 10.51, 12.74),
    "SERVICE_LOCATION": layout.Box(0.63, 5.09, 15.62, 12.74),
    "SERVICE_TAXATION_DESCRIPTION": layout.Box(0.38, 20.40, 0.30, 13.39),
    "SERVICE_DESCRIPTION": layout.Box(0.63, 20.40, 0.30, 13.79),
    "SERVICE_MUNICIPAL_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 14.40),
    "MUNICIPAL_TAXATION_BLOCK": layout.Box(2.59, 20.40, 0.30, 14.43),
    "MUNICIPAL_TAXATION_TITLE": layout.Box(0.63, 5.09, 0.30, 14.43),
    "MUNICIPAL_TAXATION_NON_TAXABLE": layout.Box(0.63, 20.40, 0.30, 14.43),
    "MUNICIPAL_TAXATION_TYPE": layout.Box(0.63, 5.09, 0.30, 14.43),
    "MUNICIPAL_TAXATION_INCIDENCE_LOCATION": layout.Box(0.63, 10.19, 5.41, 14.43),
    "MUNICIPAL_TAXATION_SPECIAL_REGIME": layout.Box(0.63, 5.09, 0.30, 15.08),
    "MUNICIPAL_TAXATION_IMMUNITY_TYPE": layout.Box(0.63, 5.09, 5.41, 15.08),
    "MUNICIPAL_TAXATION_SUSPENSION": layout.Box(0.63, 5.09, 10.51, 15.08),
    "MUNICIPAL_TAXATION_SUSPENSION_PROCESS": layout.Box(0.63, 5.09, 15.62, 15.08),
    "MUNICIPAL_TAXATION_BENEFIT": layout.Box(0.63, 5.09, 0.30, 15.73),
    "MUNICIPAL_TAXATION_BM_CALCULATION": layout.Box(0.63, 5.09, 5.41, 15.73),
    "MUNICIPAL_TAXATION_TOTAL_DEDUCTIONS": layout.Box(0.63, 5.09, 10.51, 15.73),
    "MUNICIPAL_TAXATION_UNCONDITIONAL_DISCOUNT": layout.Box(0.63, 5.09, 15.62, 15.73),
    "MUNICIPAL_TAXATION_BASE": layout.Box(0.63, 5.09, 0.30, 16.37),
    "MUNICIPAL_TAXATION_APPLIED_RATE": layout.Box(0.63, 5.09, 5.41, 16.37),
    "MUNICIPAL_TAXATION_RETENTION": layout.Box(0.63, 5.09, 10.51, 16.37),
    "MUNICIPAL_TAXATION_ISSQN_AMOUNT": layout.Box(0.63, 5.09, 15.62, 16.37),
    "MUNICIPAL_FEDERAL_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 16.99),
    "FEDERAL_TAXATION_BLOCK": layout.Box(1.28, 20.40, 0.30, 17.02),
    "FEDERAL_TAXATION_TITLE": layout.Box(0.63, 5.09, 0.30, 17.02),
    "FEDERAL_TAXATION_IRRF": layout.Box(0.63, 5.09, 5.41, 17.02),
    "FEDERAL_TAXATION_CP": layout.Box(0.63, 5.09, 10.51, 17.02),
    "FEDERAL_TAXATION_SOCIAL": layout.Box(0.63, 5.09, 15.62, 17.02),
    "FEDERAL_TAXATION_PIS": layout.Box(0.63, 5.09, 0.30, 17.67),
    "FEDERAL_TAXATION_COFINS": layout.Box(0.63, 5.09, 5.41, 17.67),
    "FEDERAL_TAXATION_RETENTION_DESCRIPTION": layout.Box(0.63, 10.19, 10.51, 17.67),
    "FEDERAL_IBS_CBS_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 18.29),
    "IBS_CBS_TAXATION_BLOCK": layout.Box(2.57, 20.40, 0.30, 18.32),
    "IBS_CBS_TAXATION_TITLE": layout.Box(0.63, 5.09, 0.30, 18.32),
    "IBS_CBS_CST_CLASSIFICATION": layout.Box(0.63, 5.09, 5.41, 18.32),
    "IBS_CBS_OPERATION_INDICATOR": layout.Box(0.63, 10.19, 10.51, 18.32),
    "IBS_CBS_EXCLUSIONS_REDUCTIONS": layout.Box(0.63, 5.09, 0.30, 18.96),
    "IBS_CBS_BASE_AFTER_REDUCTIONS": layout.Box(0.63, 5.09, 5.41, 18.96),
    "IBS_CBS_RATE_REDUCTIONS": layout.Box(0.63, 5.09, 10.51, 18.96),
    "IBS_CBS_IBS_RATES": layout.Box(0.63, 5.09, 15.62, 18.96),
    "IBS_CBS_MUNICIPAL_EFFECTIVE_RATE": layout.Box(0.63, 5.09, 0.30, 19.61),
    "IBS_CBS_MUNICIPAL_AMOUNT": layout.Box(0.63, 5.09, 5.41, 19.61),
    "IBS_CBS_STATE_EFFECTIVE_RATE": layout.Box(0.63, 5.09, 10.51, 19.61),
    "IBS_CBS_STATE_AMOUNT": layout.Box(0.63, 5.09, 15.62, 19.61),
    "IBS_CBS_IBS_TOTAL": layout.Box(0.63, 5.09, 0.30, 20.26),
    "IBS_CBS_CBS_RATE": layout.Box(0.63, 5.09, 5.41, 20.26),
    "IBS_CBS_CBS_EFFECTIVE_RATE": layout.Box(0.63, 5.09, 10.51, 20.26),
    "IBS_CBS_CBS_TOTAL": layout.Box(0.63, 5.09, 15.62, 20.26),
    "IBS_CBS_TOTAL_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 20.87),
    "TOTAL_BLOCK": layout.Box(1.36, 20.40, 0.30, 20.90),
    "TOTAL_TITLE": layout.Box(0.67, 5.09, 0.30, 20.90),
    "TOTAL_SERVICE_AMOUNT": layout.Box(0.67, 5.09, 5.41, 20.90),
    "TOTAL_UNCONDITIONAL_DISCOUNT": layout.Box(0.67, 5.09, 10.51, 20.90),
    "TOTAL_CONDITIONAL_DISCOUNT": layout.Box(0.67, 5.09, 15.62, 20.90),
    "TOTAL_RETENTIONS": layout.Box(0.67, 5.09, 0.30, 21.59),
    "TOTAL_NET_AMOUNT": layout.Box(0.67, 5.09, 5.41, 21.59),
    "TOTAL_IBS_CBS": layout.Box(0.67, 5.09, 10.51, 21.59),
    "TOTAL_NET_AMOUNT_WITH_IBS_CBS": layout.Box(0.67, 5.09, 15.62, 21.59),
    "TOTAL_COMPLEMENTARY_SEPARATOR": layout.Box(0.00, 20.40, 0.30, 22.24),
    "COMPLEMENTARY_INFO_TITLE": layout.Box(0.39, 20.40, 0.30, 22.27),
    "COMPLEMENTARY_INFO_TEXT": layout.Box(5.40, 20.40, 0.30, 22.68),
    "RECEIPT_BLOCK": layout.Box(0.67, 20.40, 0.30, 28.10),
    "RECEIPT_ACKNOWLEDGEMENT_DATE": layout.Box(0.67, 5.09, 0.30, 28.10),
    "RECEIPT_IDENTIFICATION_SIGNATURE": layout.Box(0.67, 5.09, 5.41, 28.10),
    "RECEIPT_NFSE_NUMBER_ACCESS_KEY": layout.Box(0.67, 10.19, 10.51, 28.10),
}

FIELD_MAX_LENGTHS = {
    "header.access_key": 50,
    "header.nfse_number": 13,
    "header.competence_date": 10,
    "header.nfse_issued_at": 19,
    "header.dps_number": 15,
    "header.dps_series": 5,
    "header.dps_issued_at": 19,
    "header.issuer": 13,
    "header.status": 40,
    "header.purpose": 40,
    "provider.tax_id": 40,
    "provider.municipal_registration": 15,
    "provider.phone": 20,
    "provider.name": 80,
    "provider.municipality_state": 37,
    "provider.ibge_cep": 21,
    "provider.address": 80,
    "provider.email": 80,
    "provider.simples_nacional": 40,
    "provider.sn_tax_regime": 80,
    "customer.tax_id": 40,
    "customer.municipal_registration": 15,
    "customer.phone": 20,
    "customer.name": 80,
    "customer.municipality_state": 37,
    "customer.ibge_cep": 21,
    "customer.address": 80,
    "customer.email": 80,
    "customer.unidentified_message": 80,
    "destination.tax_id": 40,
    "destination.phone": 20,
    "destination.name": 80,
    "destination.municipality_state": 37,
    "destination.ibge_cep": 21,
    "destination.address": 80,
    "destination.email": 80,
    "destination.unidentified_message": 80,
    "intermediary.tax_id": 40,
    "intermediary.municipal_registration": 15,
    "intermediary.phone": 20,
    "intermediary.name": 80,
    "intermediary.municipality_state": 37,
    "intermediary.ibge_cep": 21,
    "intermediary.address": 80,
    "intermediary.email": 80,
    "intermediary.unidentified_message": 80,
    "service.taxation_code": 14,
    "service.nbs_code": 12,
    "service.location": 42,
    "service.taxation_description": 170,
    "service.service_description": 1300,
    "municipal_taxation.taxation_type": 21,
    "municipal_taxation.incidence_location": 42,
    "municipal_taxation.special_regime": 40,
    "municipal_taxation.immunity_type": 40,
    "municipal_taxation.suspension": 40,
    "municipal_taxation.suspension_process": 30,
    "municipal_taxation.municipal_benefit": 40,
    "municipal_taxation.bm_calculation": 15,
    "municipal_taxation.total_deductions_reductions": 15,
    "municipal_taxation.unconditional_discount": 15,
    "municipal_taxation.issqn_base": 15,
    "municipal_taxation.applied_rate": 4,
    "municipal_taxation.retention": 25,
    "municipal_taxation.issqn_amount": 15,
    "municipal_taxation.non_taxable_message": 80,
    "federal_taxation.irrf": 15,
    "federal_taxation.previdenciaria_retida": 15,
    "federal_taxation.sociais_retidas": 15,
    "federal_taxation.pis_debito": 15,
    "federal_taxation.cofins_debito": 15,
    "federal_taxation.retention_description": 35,
    "ibs_cbs_taxation.cst_classification": 12,
    "ibs_cbs_taxation.operation_indicator": 56,
    "ibs_cbs_taxation.exclusions_reductions": 15,
    "ibs_cbs_taxation.base_after_reductions": 15,
    "ibs_cbs_taxation.rate_reductions": 24,
    "ibs_cbs_taxation.ibs_rates": 16,
    "ibs_cbs_taxation.ibs_municipal_effective_rate": 4,
    "ibs_cbs_taxation.ibs_municipal_amount": 15,
    "ibs_cbs_taxation.ibs_state_effective_rate": 4,
    "ibs_cbs_taxation.ibs_state_amount": 15,
    "ibs_cbs_taxation.ibs_total": 15,
    "ibs_cbs_taxation.cbs_rate": 4,
    "ibs_cbs_taxation.cbs_effective_rate": 4,
    "ibs_cbs_taxation.cbs_total": 15,
    "total.service_amount": 15,
    "total.unconditional_discount": 15,
    "total.conditional_discount": 15,
    "total.total_retentions": 15,
    "total.nfse_net_amount": 15,
    "total.ibs_cbs_total": 15,
    "total.nfse_net_amount_with_ibs_cbs": 15,
    "complementary_info.text": 2000,
    "receipt.acknowledgement_date": 10,
    "receipt.identification_signature": 80,
    "receipt.nfse_number_access_key": 66,
}

NORMATIVE_REQUIRED_FIELDS = {
    "header.access_key": "NFSe/infNFSe/@Id",
    "header.nfse_number": "NFSe/infNFSe/nNFSe",
    "header.competence_date": "NFSe/infNFSe/DPS/infDPS/dCompet",
    "header.nfse_issued_at": "NFSe/infNFSe/dhProc",
    "header.dps_number": "NFSe/infNFSe/DPS/infDPS/nDPS",
    "header.dps_series": "NFSe/infNFSe/DPS/infDPS/serie",
    "header.dps_issued_at": "NFSe/infNFSe/DPS/infDPS/dhEmi",
    "header.issuer": "NFSe/infNFSe/DPS/infDPS/tpEmit",
    "header.status": "NFSe/infNFSe/cStat",
    "provider.tax_id": "NFSe/infNFSe/DPS/infDPS/prest/CNPJ|CPF|NIF",
    "provider.name": "NFSe/infNFSe/DPS/infDPS/prest/xNome",
    "service.taxation_code": "NFSe/infNFSe/DPS/infDPS/serv/cServ/cTribNac|cTribMun",
    "service.location": "NFSe/infNFSe/DPS/infDPS/serv/locPrest/cLocPrestacao",
    "service.service_description": "NFSe/infNFSe/DPS/infDPS/serv/cServ/xDescServ",
    "total.service_amount": "NFSe/infNFSe/DPS/infDPS/valores/vServPrest/vServ",
    "total.nfse_net_amount": "NFSe/infNFSe/valores/vLiq",
}


def validate_layout_constants() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name, expected in EXPECTED_BOXES.items():
        actual = getattr(layout, name)
        if actual != expected:
            issues.append(
                ValidationIssue(
                    "layout.box_mismatch",
                    f"{name}: esperado {expected}, encontrado {actual}.",
                )
            )
    return issues


def validate_danfse_data(data: DanfseData) -> list[ValidationIssue]:
    issues = validate_layout_constants()
    for path, max_length in FIELD_MAX_LENGTHS.items():
        value = _get_path(data, path)
        if value != MISSING_VALUE and len(value) > max_length:
            issues.append(
                ValidationIssue(
                    "data.max_length",
                    f"{path}: tamanho {len(value)} excede limite normativo {max_length}.",
                )
            )
    issues.extend(_validate_required_fields(data))
    issues.extend(_validate_rule_flags(data))
    return issues


def _get_path(data: DanfseData, path: str) -> str:
    current: object = data
    for name in path.split("."):
        current = getattr(current, name)
    return str(current)


def _validate_rule_flags(data: DanfseData) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    municipal = data.municipal_taxation
    if municipal.non_taxable_message:
        values = (
            municipal.taxation_type,
            municipal.incidence_location,
            municipal.special_regime,
            municipal.immunity_type,
            municipal.suspension,
            municipal.suspension_process,
            municipal.municipal_benefit,
            municipal.bm_calculation,
            municipal.total_deductions_reductions,
            municipal.unconditional_discount,
            municipal.issqn_base,
            municipal.applied_rate,
            municipal.retention,
            municipal.issqn_amount,
        )
        if any(value != MISSING_VALUE for value in values):
            issues.append(
                ValidationIssue(
                    "data.municipal.non_taxable_conflict",
                    "Bloco reduzido de tributação municipal não pode conter campos preenchidos.",
                )
            )

    if data.federal_taxation.show_legacy_piscofins_row:
        try:
            competence_year = int(data.header.competence_date[-4:])
        except ValueError:
            competence_year = 2026
        if competence_year > 2026:
            issues.append(
                ValidationIssue(
                    "data.federal.legacy_row_invalid",
                    "Linha de PIS/COFINS só pode ser impressa até o fim de 2026.",
                )
            )

    if data.header.purpose == "NFS-e de crédito" and data.header.credit_note_type == MISSING_VALUE:
        issues.append(
            ValidationIssue(
                "data.nt009.credit_type_missing",
                "NFS-e de crédito sem tpNFSeCredito em NFSe/infNFSe/DPS/infDPS/tpNFSeCredito.",
                "warning",
            )
        )

    if data.header.purpose == "NFS-e de débito" and data.header.debit_note_type == MISSING_VALUE:
        issues.append(
            ValidationIssue(
                "data.nt009.debit_type_missing",
                "NFS-e de débito sem tpNFSeDebito em NFSe/infNFSe/DPS/infDPS/tpNFSeDebito.",
                "warning",
            )
        )

    sn_values = (
        data.ibs_cbs_taxation.sn_ibs_rate,
        data.ibs_cbs_taxation.sn_ibs_amount,
        data.ibs_cbs_taxation.sn_cbs_rate,
        data.ibs_cbs_taxation.sn_cbs_amount,
    )
    if any(value != MISSING_VALUE for value in sn_values) and any(value == MISSING_VALUE for value in sn_values):
        issues.append(
            ValidationIssue(
                "data.nt009.gtribsn_partial",
                "Grupo gTribSN esta parcialmente preenchido; confira pIBSSN, vIBSSN, pCBSSN e vCBSSN.",
                "warning",
            )
        )
    return issues


def _validate_required_fields(data: DanfseData) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, xml_path in NORMATIVE_REQUIRED_FIELDS.items():
        value = _get_path(data, path)
        if value == MISSING_VALUE:
            issues.append(
                ValidationIssue(
                    "data.required_missing",
                    f"{path}: campo minimo ausente no caminho normativo {xml_path}; sera impresso como '-'.",
                    "warning",
                )
            )
    return issues
