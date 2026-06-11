"""HTML renderer for the implemented DANFSe blocks."""

from __future__ import annotations

import base64
from html import escape
from io import BytesIO

from . import layout
from .models import (
    ComplementaryInfoData,
    CustomerData,
    DanfseData,
    DestinationData,
    FederalTaxationData,
    HeaderData,
    IbsCbsTaxationData,
    IntermediaryData,
    MunicipalTaxationData,
    NFSE_LOGO_URL,
    ProviderData,
    ReceiptData,
    ServiceData,
    TotalData,
)


def render_danfse_html(data: DanfseData) -> str:
    qr_code = _qr_code_data_uri(data.header.consultation_url)
    dynamic_blocks = _render_dynamic_blocks(data)
    legal_warning = (
        '<div class="legal-warning">NFS-e SEM VALIDADE JURÍDICA</div>'
        if data.header.is_restricted_production
        else ""
    )

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>DANFSe {escape(data.header.access_key)}</title>
  <style>
    @page {{ size: A4 portrait; margin: 0; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #fff; color: #000; }}
    .page {{
      position: relative;
      width: 21cm;
      height: 29.7cm;
      font-family: "Microsoft Sans Serif", Arial, sans-serif;
      page-break-after: always;
    }}
    .page-border {{
      position: absolute;
      left: .18cm;
      top: .18cm;
      width: 20.64cm;
      height: 29.34cm;
      border: 1pt solid #000;
    }}
    .box {{ position: absolute; overflow: hidden; }}
    .section-line {{ border-bottom: .5pt solid #000; }}
    .horizontal-line {{ position: absolute; background: #000; height: .5pt; }}
    .shaded {{ background: #f2f2f2; }}
    .logo {{ position: absolute; {layout.LOGO.css()} object-fit: contain; }}
    .title {{
      position: absolute; {layout.TITLE.css()}
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; font-family: Arial, sans-serif; font-size: 9pt; font-weight: 700;
      line-height: 1.25;
    }}
    .legal-warning {{ color: #f00; margin-top: 2pt; }}
    .municipality {{ position: absolute; {layout.MUNICIPALITY.css()} padding: 2pt; font-size: 8pt; }}
    .environment {{ position: absolute; padding: 0 2pt; font-size: 6pt; line-height: 1; }}
    .field {{
      position: absolute;
      border: 0;
      padding: 1pt 2pt;
      overflow: hidden;
    }}
    .receipt-field {{ border: .5pt solid #000; }}
    .label {{ display: block; font-family: Arial, sans-serif; font-size: 6pt; font-weight: 700; line-height: 1.05; white-space: nowrap; }}
    .identification-label {{ font-size: 7pt; text-transform: uppercase; }}
    .block-title {{ position: absolute; padding: 1pt 2pt; overflow: hidden; font-family: Arial, sans-serif; font-size: 7pt; font-weight: 700; text-transform: uppercase; line-height: 1.05; white-space: nowrap; }}
    .reduced-message {{
      position: absolute;
      padding: 0 2pt;
      overflow: hidden;
      font-size: 7pt;
      line-height: 1;
      text-align: center;
      white-space: nowrap;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .value {{ display: block; font-size: 7pt; line-height: 1.1; white-space: nowrap; }}
    .value.multiline-value {{ white-space: pre-wrap; line-height: 1.1; }}
    .qrcode {{ position: absolute; {layout.QR_CODE.css()} width: 1.52cm; height: 1.52cm; }}
    .qr-complement {{
      position: absolute; {layout.QR_COMPLEMENT.css()}
      font-size: 6pt; line-height: 1.08; text-align: center; overflow: hidden;
    }}
  </style>
</head>
<body>
  <main class="page">
    <div class="page-border"></div>
    <section class="box shaded section-line" style="{layout.HEADER.css()}"></section>
    <img class="logo" src="{NFSE_LOGO_URL}" alt="NFS-e">
    <section class="title">
      <div>DANFSe v2.0</div>
      <div>Documento Auxiliar da NFS-e</div>
      {legal_warning}
    </section>
    <section class="box" style="{layout.MUNICIPALITY_ENV.css()}"></section>
    <div class="municipality">{escape(data.header.municipality_line)}</div>
    <div class="environment" style="{layout.GENERATOR_ENV.css()}">Ambiente Gerador: {escape(data.header.generator_environment)}</div>
    <div class="environment" style="{layout.NATIONAL_ENV.css()}">Tipo de Ambiente: {escape(data.header.national_environment)}</div>

    <section class="box" style="{layout.NFSE_DATA.css()}"></section>
    {_field(layout.ACCESS_KEY, "Chave de Acesso da NFS-e", data.header.access_key, identification=True)}
    {_field(layout.NFSE_NUMBER, "Número da NFS-e", data.header.nfse_number, identification=True)}
    {_field(layout.COMPETENCE, "Competência da NFS-e", data.header.competence_date, identification=True)}
    {_field(layout.NFSE_ISSUED_AT, "Data e Hora da Emissão da NFS-e", data.header.nfse_issued_at, identification=True)}
    {_field(layout.DPS_NUMBER, "Número da DPS", data.header.dps_number, identification=True)}
    {_field(layout.DPS_SERIES, "Série da DPS", data.header.dps_series, identification=True)}
    {_field(layout.DPS_ISSUED_AT, "Data e Hora da Emissão da DPS", data.header.dps_issued_at, identification=True)}
    {_field(layout.ISSUER, "Emitente da NFS-e", data.header.issuer, shaded=True, identification=True)}
    {_field(layout.STATUS, "Situação da NFS-e", data.header.status, identification=True)}
    {_field(layout.PURPOSE, "Finalidade", data.header.purpose, identification=True)}
    <img class="qrcode" src="{qr_code}" alt="QR Code de consulta da NFS-e">
    <div class="qr-complement">A autenticidade desta NFS-e<br>pode ser verificada pela leitura deste código QR ou pela consulta da chave de<br>acesso no portal nacional da NFS-e</div>

    <div class="horizontal-line" style="{layout.IDENTIFICATION_PROVIDER_SEPARATOR.css()}"></div>
    <section class="box" style="{layout.PROVIDER_BLOCK.css()}"></section>
    {_block_title(layout.PROVIDER_TITLE, "Prestador / Fornecedor")}
    {_field(layout.PROVIDER_TAX_ID, "CNPJ / CPF / NIF", data.provider.tax_id)}
    {_field(layout.PROVIDER_MUNICIPAL_REGISTRATION, "Indicador Municipal (Inscrição)", data.provider.municipal_registration)}
    {_field(layout.PROVIDER_PHONE, "Telefone", data.provider.phone)}
    {_field(layout.PROVIDER_NAME, "Nome / Nome Empresarial", data.provider.name)}
    {_field(layout.PROVIDER_MUNICIPALITY_STATE, "Município / Sigla UF", data.provider.municipality_state)}
    {_field(layout.PROVIDER_IBGE_CEP, "Código IBGE / CEP", data.provider.ibge_cep)}
    {_field(layout.PROVIDER_ADDRESS, "Endereço", data.provider.address)}
    {_field(layout.PROVIDER_EMAIL, "Email", data.provider.email)}
    {_field(layout.PROVIDER_SIMPLES_NACIONAL, "Simples Nacional na Data de Competência", data.provider.simples_nacional)}
    {_field(layout.PROVIDER_SN_TAX_REGIME, "Regime de Apuração Tributária pelo SN", data.provider.sn_tax_regime)}

    <div class="horizontal-line" style="{layout.PROVIDER_CUSTOMER_SEPARATOR.css()}"></div>
    {dynamic_blocks}
  </main>
</body>
</html>
"""


def render_header_html(data: HeaderData) -> str:
    empty_provider = ProviderData("-", "-", "-", "-", "-", "-", "-", "-", "-", "-")
    empty_customer = CustomerData("-", "-", "-", "-", "-", "-", "-", "-")
    empty_destination = DestinationData("-", "-", "-", "-", "-", "-", "-")
    empty_intermediary = IntermediaryData("-", "-", "-", "-", "-", "-", "-", "-")
    empty_service = ServiceData("-", "-", "-", "-", "-")
    empty_municipal = MunicipalTaxationData("-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-")
    empty_federal = FederalTaxationData("-", "-", "-", "-", "-", "-")
    empty_ibs_cbs = IbsCbsTaxationData("-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-")
    empty_total = TotalData("-", "-", "-", "-", "-", "-", "-")
    empty_complementary = ComplementaryInfoData("-")
    empty_receipt = ReceiptData("-", "-", "-")
    return render_danfse_html(
        DanfseData(
            header=data,
            provider=empty_provider,
            customer=empty_customer,
            destination=empty_destination,
            intermediary=empty_intermediary,
            service=empty_service,
            municipal_taxation=empty_municipal,
            federal_taxation=empty_federal,
            ibs_cbs_taxation=empty_ibs_cbs,
            total=empty_total,
            complementary_info=empty_complementary,
            receipt=empty_receipt,
        )
    )


def _render_dynamic_blocks(data: DanfseData) -> str:
    current_top = layout.CUSTOMER_BLOCK.top_cm
    reduction_credit = 0.0

    customer_html, current_top, customer_credit = _render_customer(data.customer, current_top)
    reduction_credit += customer_credit
    destination_html, current_top, destination_credit = _render_destination(data.destination, current_top)
    reduction_credit += destination_credit
    intermediary_html, current_top, intermediary_credit = _render_intermediary(data.intermediary, current_top)
    reduction_credit += intermediary_credit
    service_html = _render_service(data.service, current_top, reduction_credit)
    municipal_html, current_top = _render_municipal_taxation(
        data.municipal_taxation,
        layout.MUNICIPAL_TAXATION_BLOCK.top_cm,
    )
    federal_html, current_top = _render_federal_taxation(data.federal_taxation, current_top)
    ibs_cbs_html, current_top = _render_ibs_cbs_taxation(data.ibs_cbs_taxation, current_top)
    total_html, current_top = _render_total(data.total, current_top)
    complementary_html = _render_complementary_info(data.complementary_info, current_top)
    receipt_html = _render_receipt(data.receipt)

    return (
        customer_html
        + destination_html
        + intermediary_html
        + service_html
        + municipal_html
        + federal_html
        + ibs_cbs_html
        + total_html
        + complementary_html
        + receipt_html
    )


def _render_customer(customer: CustomerData, top_cm: float) -> tuple[str, float, float]:
    offset = top_cm - layout.CUSTOMER_BLOCK.top_cm
    if customer.unidentified_message:
        box = layout.CUSTOMER_BLOCK.at_top(top_cm).with_height(_reduced_block_height())
        html = _reduced_message(box, customer.unidentified_message)
        return html, _next_block_top(top_cm, _reduced_block_height()), _full_party_height() - _reduced_block_height()

    html = (
        f'<section class="box" style="{layout.CUSTOMER_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.CUSTOMER_TITLE.shifted(offset), "Tomador / Adquirente")
        + _field(layout.CUSTOMER_TAX_ID.shifted(offset), "CNPJ / CPF / NIF", customer.tax_id)
        + _field(layout.CUSTOMER_MUNICIPAL_REGISTRATION.shifted(offset), "Indicador Municipal (Inscrição)", customer.municipal_registration)
        + _field(layout.CUSTOMER_PHONE.shifted(offset), "Telefone", customer.phone)
        + _field(layout.CUSTOMER_NAME.shifted(offset), "Nome / Nome Empresarial", customer.name)
        + _field(layout.CUSTOMER_MUNICIPALITY_STATE.shifted(offset), "Município / Sigla UF", customer.municipality_state)
        + _field(layout.CUSTOMER_IBGE_CEP.shifted(offset), "Código IBGE / CEP", customer.ibge_cep)
        + _field(layout.CUSTOMER_ADDRESS.shifted(offset), "Endereço", customer.address)
        + _field(layout.CUSTOMER_EMAIL.shifted(offset), "E-mail", customer.email)
    )
    return html, _next_block_top(top_cm, _full_party_height()), 0.0


def _render_destination(destination: DestinationData, top_cm: float) -> tuple[str, float, float]:
    html = _separator(top_cm)
    offset = top_cm - layout.DESTINATION_BLOCK.top_cm
    if destination.unidentified_message:
        box = layout.DESTINATION_UNIDENTIFIED.at_top(top_cm).with_height(_reduced_block_height())
        html += _reduced_message(box, destination.unidentified_message)
        return html, _next_block_top(top_cm, _reduced_block_height()), _full_party_height() - _reduced_block_height()

    html += (
        f'<section class="box" style="{layout.DESTINATION_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.DESTINATION_TITLE.shifted(offset), "Destinatário da Operação")
        + _field(layout.DESTINATION_TAX_ID.shifted(offset), "CNPJ / CPF / NIF", destination.tax_id)
        + _field(layout.DESTINATION_PHONE.shifted(offset), "Telefone", destination.phone)
        + _field(layout.DESTINATION_NAME.shifted(offset), "Nome / Nome Empresarial", destination.name)
        + _field(layout.DESTINATION_MUNICIPALITY_STATE.shifted(offset), "Município / Sigla UF", destination.municipality_state)
        + _field(layout.DESTINATION_IBGE_CEP.shifted(offset), "Código IBGE / CEP", destination.ibge_cep)
        + _field(layout.DESTINATION_ADDRESS.shifted(offset), "Endereço", destination.address)
        + _field(layout.DESTINATION_EMAIL.shifted(offset), "E-mail", destination.email)
    )
    return html, _next_block_top(top_cm, _full_party_height()), 0.0


def _render_intermediary(intermediary: IntermediaryData, top_cm: float) -> tuple[str, float, float]:
    html = _separator(top_cm)
    offset = top_cm - layout.INTERMEDIARY_BLOCK.top_cm
    if intermediary.unidentified_message:
        box = layout.INTERMEDIARY_UNIDENTIFIED.at_top(top_cm).with_height(_reduced_block_height())
        html += _reduced_message(box, intermediary.unidentified_message)
        return html, _next_block_top(top_cm, _reduced_block_height()), _full_party_height() - _reduced_block_height()

    html += (
        f'<section class="box" style="{layout.INTERMEDIARY_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.INTERMEDIARY_TITLE.shifted(offset), "Intermediário da Operação")
        + _field(layout.INTERMEDIARY_TAX_ID.shifted(offset), "CNPJ / CPF / NIF", intermediary.tax_id)
        + _field(layout.INTERMEDIARY_MUNICIPAL_REGISTRATION.shifted(offset), "Indicador Municipal (Inscrição)", intermediary.municipal_registration)
        + _field(layout.INTERMEDIARY_PHONE.shifted(offset), "Telefone", intermediary.phone)
        + _field(layout.INTERMEDIARY_NAME.shifted(offset), "Nome / Nome Empresarial", intermediary.name)
        + _field(layout.INTERMEDIARY_MUNICIPALITY_STATE.shifted(offset), "Município / Sigla UF", intermediary.municipality_state)
        + _field(layout.INTERMEDIARY_IBGE_CEP.shifted(offset), "Código IBGE / CEP", intermediary.ibge_cep)
        + _field(layout.INTERMEDIARY_ADDRESS.shifted(offset), "Endereço", intermediary.address)
        + _field(layout.INTERMEDIARY_EMAIL.shifted(offset), "E-mail", intermediary.email)
    )
    return html, _next_block_top(top_cm, _full_party_height()), 0.0


def _render_service(service: ServiceData, top_cm: float, reduction_credit: float) -> str:
    offset = top_cm - layout.SERVICE_BLOCK.top_cm
    description_box = layout.SERVICE_DESCRIPTION.shifted(offset).with_height(
        layout.SERVICE_DESCRIPTION.height_cm + reduction_credit
    )
    return (
        _separator(top_cm)
        + f'<section class="box" style="{layout.SERVICE_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.SERVICE_TITLE.shifted(offset), "Serviço Prestado")
        + _field(layout.SERVICE_TAXATION_CODE.shifted(offset), "Código de Tributação Nacional / Municipal", service.taxation_code)
        + _field(layout.SERVICE_NBS_CODE.shifted(offset), "Código da NBS", service.nbs_code)
        + _field(layout.SERVICE_LOCATION.shifted(offset), "Local da Prestação / Sigla UF / País", service.location)
        + _value_only(layout.SERVICE_TAXATION_DESCRIPTION.shifted(offset), service.taxation_description)
        + _field(description_box, "Descrição do Serviço", service.service_description, multiline=True)
    )


def _render_municipal_taxation(
    municipal: MunicipalTaxationData,
    top_cm: float,
) -> tuple[str, float]:
    html = _separator(top_cm)
    if municipal.non_taxable_message:
        box = layout.MUNICIPAL_TAXATION_NON_TAXABLE.at_top(top_cm).with_height(_reduced_block_height())
        html += _reduced_message(box, municipal.non_taxable_message)
        return html, _next_block_top(top_cm, _reduced_block_height())

    current_top = top_cm
    title_offset = current_top - layout.MUNICIPAL_TAXATION_TITLE.top_cm
    html += (
        f'<section class="box" style="{layout.MUNICIPAL_TAXATION_BLOCK.at_top(top_cm).css()}"></section>'
        + _field(
            layout.MUNICIPAL_TAXATION_TYPE.shifted(title_offset),
            "Tipo de Tributação do ISSQN",
            municipal.taxation_type,
            shaded=True,
        )
        + _field(
            layout.MUNICIPAL_TAXATION_INCIDENCE_LOCATION.shifted(title_offset),
            "Município / Sigla UF / País da Incidência do ISSQN",
            municipal.incidence_location,
        )
    )
    current_top = _next_row_top(current_top)

    if not municipal.suppress_optional_row_one:
        row_offset = current_top - layout.MUNICIPAL_TAXATION_SPECIAL_REGIME.top_cm
        html += (
            _field(layout.MUNICIPAL_TAXATION_SPECIAL_REGIME.shifted(row_offset), "Regime Especial de Tributação do ISSQN", municipal.special_regime)
            + _field(layout.MUNICIPAL_TAXATION_IMMUNITY_TYPE.shifted(row_offset), "Tipo de Imunidade do ISSQN", municipal.immunity_type)
            + _field(layout.MUNICIPAL_TAXATION_SUSPENSION.shifted(row_offset), "Suspensão da Exigibilidade do ISSQN", municipal.suspension)
            + _field(layout.MUNICIPAL_TAXATION_SUSPENSION_PROCESS.shifted(row_offset), "Número Processo Suspensão", municipal.suspension_process)
        )
        current_top = _next_row_top(current_top)

    if not municipal.suppress_optional_row_two:
        row_offset = current_top - layout.MUNICIPAL_TAXATION_BENEFIT.top_cm
        html += (
            _field(layout.MUNICIPAL_TAXATION_BENEFIT.shifted(row_offset), "Benefício Municipal", municipal.municipal_benefit)
            + _field(layout.MUNICIPAL_TAXATION_BM_CALCULATION.shifted(row_offset), "Cálculo do BM", municipal.bm_calculation)
            + _field(layout.MUNICIPAL_TAXATION_TOTAL_DEDUCTIONS.shifted(row_offset), "Total Deduções/Reduções", municipal.total_deductions_reductions)
            + _field(layout.MUNICIPAL_TAXATION_UNCONDITIONAL_DISCOUNT.shifted(row_offset), "Desconto Incondicionado", municipal.unconditional_discount)
        )
        current_top = _next_row_top(current_top, gap_cm=0.01)

    row_offset = current_top - layout.MUNICIPAL_TAXATION_BASE.top_cm
    html += (
        _field(layout.MUNICIPAL_TAXATION_BASE.shifted(row_offset), "BC ISSQN", municipal.issqn_base)
        + _field(layout.MUNICIPAL_TAXATION_APPLIED_RATE.shifted(row_offset), "Alíquota Aplicada", municipal.applied_rate)
        + _field(layout.MUNICIPAL_TAXATION_RETENTION.shifted(row_offset), "Retenção do ISSQN", municipal.retention)
        + _field(layout.MUNICIPAL_TAXATION_ISSQN_AMOUNT.shifted(row_offset), "ISSQN Apurado", municipal.issqn_amount)
    )
    return html, _next_block_top(current_top, 0.63)


def _render_federal_taxation(federal: FederalTaxationData, top_cm: float) -> tuple[str, float]:
    row_offset = top_cm - layout.FEDERAL_TAXATION_TITLE.top_cm
    html = _separator(top_cm) + (
        f'<section class="box" style="{layout.FEDERAL_TAXATION_BLOCK.at_top(top_cm).css()}"></section>'
        + _block_title(layout.FEDERAL_TAXATION_TITLE.shifted(row_offset), "Tributação Federal (Exceto CBS)")
        + _field(layout.FEDERAL_TAXATION_IRRF.shifted(row_offset), "IRRF", federal.irrf)
        + _field(layout.FEDERAL_TAXATION_CP.shifted(row_offset), "Contribuição Previdenciária - Retida", federal.previdenciaria_retida)
        + _field(layout.FEDERAL_TAXATION_SOCIAL.shifted(row_offset), "Contribuições Sociais - Retidas", federal.sociais_retidas)
    )
    if not federal.show_legacy_piscofins_row:
        return html, _next_block_top(top_cm, 0.63)

    next_top = _next_row_top(top_cm)
    row_offset = next_top - layout.FEDERAL_TAXATION_PIS.top_cm
    html += (
        _field(layout.FEDERAL_TAXATION_PIS.shifted(row_offset), "PIS - Débito Apuração Própria", federal.pis_debito)
        + _field(layout.FEDERAL_TAXATION_COFINS.shifted(row_offset), "COFINS - Débito Apuração Própria", federal.cofins_debito)
        + _field(
            layout.FEDERAL_TAXATION_RETENTION_DESCRIPTION.shifted(row_offset),
            "Descrição Contrib. Sociais - Retidas",
            federal.retention_description,
        )
    )
    return html, _next_block_top(next_top, 0.63)


def _render_ibs_cbs_taxation(ibs_cbs: IbsCbsTaxationData, top_cm: float) -> tuple[str, float]:
    offset = top_cm - layout.IBS_CBS_TAXATION_BLOCK.top_cm
    return (
        _separator(top_cm)
        + f'<section class="box" style="{layout.IBS_CBS_TAXATION_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.IBS_CBS_TAXATION_TITLE.shifted(offset), "Tributação IBS / CBS")
        + _field(layout.IBS_CBS_CST_CLASSIFICATION.shifted(offset), "CST / cClassTrib", ibs_cbs.cst_classification)
        + _field(layout.IBS_CBS_OPERATION_INDICATOR.shifted(offset), "Indicador de Operação / Código IBGE Incidência / Município Incidência / Sigla UF", ibs_cbs.operation_indicator)
        + _field(layout.IBS_CBS_EXCLUSIONS_REDUCTIONS.shifted(offset), "Exclusões e Reduções da Base de Cálculo", ibs_cbs.exclusions_reductions)
        + _field(layout.IBS_CBS_BASE_AFTER_REDUCTIONS.shifted(offset), "Base de Cálculo Após Exclusões e Reduções", ibs_cbs.base_after_reductions)
        + _field(layout.IBS_CBS_RATE_REDUCTIONS.shifted(offset), "Red. Alíquota IBS / Red. Alíquota CBS", ibs_cbs.rate_reductions)
        + _field(layout.IBS_CBS_IBS_RATES.shifted(offset), "Alíquota - IBS UF / IBS Mun", ibs_cbs.ibs_rates)
        + _field(layout.IBS_CBS_MUNICIPAL_EFFECTIVE_RATE.shifted(offset), "Alíq. Efetiva Municipal - IBS", ibs_cbs.ibs_municipal_effective_rate)
        + _field(layout.IBS_CBS_MUNICIPAL_AMOUNT.shifted(offset), "Valor Apurado Municipal - IBS", ibs_cbs.ibs_municipal_amount)
        + _field(layout.IBS_CBS_STATE_EFFECTIVE_RATE.shifted(offset), "Alíq. Efetiva Estadual - IBS", ibs_cbs.ibs_state_effective_rate)
        + _field(layout.IBS_CBS_STATE_AMOUNT.shifted(offset), "Valor Apurado Estadual - IBS", ibs_cbs.ibs_state_amount)
        + _field(layout.IBS_CBS_IBS_TOTAL.shifted(offset), "Valor Total Apurado - IBS", ibs_cbs.ibs_total)
        + _field(layout.IBS_CBS_CBS_RATE.shifted(offset), "Alíquota - CBS", ibs_cbs.cbs_rate)
        + _field(layout.IBS_CBS_CBS_EFFECTIVE_RATE.shifted(offset), "Alíquota Efetiva - CBS", ibs_cbs.cbs_effective_rate)
        + _field(layout.IBS_CBS_CBS_TOTAL.shifted(offset), "Valor Total Apurado - CBS", ibs_cbs.cbs_total),
        _next_block_top(top_cm, layout.IBS_CBS_TAXATION_BLOCK.height_cm),
    )


def _render_total(total: TotalData, top_cm: float) -> tuple[str, float]:
    offset = top_cm - layout.TOTAL_BLOCK.top_cm
    return (
        _separator(top_cm)
        + f'<section class="box" style="{layout.TOTAL_BLOCK.shifted(offset).css()}"></section>'
        + _block_title(layout.TOTAL_TITLE.shifted(offset), "Valor Total da NFS-e")
        + _field(layout.TOTAL_SERVICE_AMOUNT.shifted(offset), "Valor da Operação / Serviço", total.service_amount)
        + _field(layout.TOTAL_UNCONDITIONAL_DISCOUNT.shifted(offset), "Desconto Incondicionado", total.unconditional_discount)
        + _field(layout.TOTAL_CONDITIONAL_DISCOUNT.shifted(offset), "Desconto Condicionado", total.conditional_discount)
        + _field(layout.TOTAL_RETENTIONS.shifted(offset), "Total das Retenções (ISSQN / Federais)", total.total_retentions)
        + _field(layout.TOTAL_NET_AMOUNT.shifted(offset), "Valor Líquido da NFS-e", total.nfse_net_amount)
        + _field(layout.TOTAL_IBS_CBS.shifted(offset), "Total do IBS/CBS", total.ibs_cbs_total)
        + _field(layout.TOTAL_NET_AMOUNT_WITH_IBS_CBS.shifted(offset), "Valor Líquido da NFS-e + IBS/CBS", total.nfse_net_amount_with_ibs_cbs, shaded=True),
        _next_block_top(top_cm, layout.TOTAL_BLOCK.height_cm),
    )


def _render_complementary_info(complementary: ComplementaryInfoData, top_cm: float) -> str:
    offset = top_cm - layout.COMPLEMENTARY_INFO_TITLE.top_cm
    return (
        _separator(top_cm)
        + _block_title(layout.COMPLEMENTARY_INFO_TITLE.shifted(offset), "Informações Complementares")
        + _field(layout.COMPLEMENTARY_INFO_TEXT.shifted(offset), "Informações Complementares", complementary.text, multiline=True)
    )


def _render_receipt(receipt: ReceiptData) -> str:
    return (
        f'<section class="box" style="{layout.RECEIPT_BLOCK.css()}"></section>'
        + _receipt_field(layout.RECEIPT_ACKNOWLEDGEMENT_DATE, "DATA CIENTIFICAÇÃO:", receipt.acknowledgement_date)
        + _receipt_field(layout.RECEIPT_IDENTIFICATION_SIGNATURE, "IDENTIFICAÇÃO E ASSINATURA", receipt.identification_signature)
        + _receipt_field(layout.RECEIPT_NFSE_NUMBER_ACCESS_KEY, "Nº NFS-e / CHAVE NFS-e", receipt.nfse_number_access_key)
    )


def _field(
    box: layout.Box,
    label: str,
    value: str,
    shaded: bool = False,
    identification: bool = False,
    multiline: bool = False,
) -> str:
    classes = "field shaded" if shaded else "field"
    label_classes = "label identification-label" if identification else "label"
    value_classes = "value multiline-value" if multiline else "value"
    return (
        f'<div class="{classes}" style="{box.css()}">'
        f'<span class="{label_classes}">{escape(label)}</span>'
        f'<span class="{value_classes}">{escape(value)}</span>'
        "</div>"
    )


def _receipt_field(box: layout.Box, label: str, value: str) -> str:
    return (
        f'<div class="field receipt-field" style="{box.css()}">'
        f'<span class="label">{escape(label)}</span>'
        f'<span class="value">{escape(value)}</span>'
        "</div>"
    )


def _block_title(box: layout.Box, label: str) -> str:
    return f'<div class="block-title shaded" style="{box.css()}">{escape(label)}</div>'


def _reduced_message(box: layout.Box, message: str) -> str:
    return f'<div class="reduced-message" style="{box.css()}">{escape(message)}</div>'


def _value_only(box: layout.Box, value: str) -> str:
    return f'<div class="field" style="{box.css()}"><span class="value">{escape(value)}</span></div>'


def _separator(top_cm: float) -> str:
    box = layout.Box(0.0, 20.40, 0.30, max(0.0, top_cm - 0.03))
    return f'<div class="horizontal-line" style="{box.css()}"></div>'


def _full_party_height() -> float:
    return 1.93


def _reduced_block_height() -> float:
    return 0.32


def _next_block_top(top_cm: float, height_cm: float) -> float:
    return round(top_cm + height_cm + 0.01, 2)


def _next_row_top(top_cm: float, gap_cm: float = 0.02) -> float:
    return round(top_cm + 0.63 + gap_cm, 2)


def _qr_code_data_uri(value: str) -> str:
    try:
        import qrcode
    except ImportError as exc:
        raise RuntimeError("Dependencia qrcode nao instalada. Execute: pip install -e .") from exc

    image = qrcode.make(value)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
