"""XML parsing for the national NFS-e layout."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET

from .codes import (
    C_ATV_SN,
    CSTAT,
    FIN_NFSE,
    OP_SIMP_NAC,
    REG_AP_IBS_CBS_SN,
    REG_AP_TRIB_SN,
    REG_ESP_TRIB,
    TP_BM_ISSQN,
    TP_EMIT,
    TP_IMUNIDADE_ISSQN,
    TP_NFSE_CREDITO,
    TP_NFSE_DEBITO,
    TP_RET_ISSQN,
    TP_RET_PIS_COFINS,
    TP_SUSP_ISSQN,
    TRIB_ISSQN,
    describe,
)
from .exceptions import InvalidNFSeXmlError
from .formatting import (
    ellipsize,
    first_present,
    format_cep,
    format_cnpj,
    format_cpf,
    format_date,
    format_datetime,
    join_present,
    missing_if_blank,
    strip_nfse_prefix,
)
from .models import (
    ComplementaryInfoData,
    CustomerData,
    DanfseData,
    DestinationData,
    FederalTaxationData,
    HeaderData,
    IbsCbsTaxationData,
    IntermediaryData,
    MISSING_VALUE,
    MunicipalTaxationData,
    ProviderData,
    ReceiptData,
    ServiceData,
    TotalData,
)
from .municipalities import describe_municipality_state


def parse_danfse(xml_file: str | Path) -> DanfseData:
    root = ET.parse(xml_file).getroot()
    inf_nfse = _child(root, "infNFSe")
    if inf_nfse is None:
        raise InvalidNFSeXmlError("XML nao contem NFSe/infNFSe.")

    inf_dps = _path(inf_nfse, "DPS", "infDPS")
    if inf_dps is None:
        raise InvalidNFSeXmlError("XML nao contem NFSe/infNFSe/DPS/infDPS.")

    return DanfseData(
        header=_parse_header(inf_nfse, inf_dps),
        provider=_parse_provider(inf_dps),
        customer=_parse_customer(inf_dps),
        destination=_parse_destination(inf_dps),
        intermediary=_parse_intermediary(inf_dps),
        service=_parse_service(inf_nfse, inf_dps),
        municipal_taxation=_parse_municipal_taxation(inf_nfse, inf_dps),
        federal_taxation=_parse_federal_taxation(inf_dps),
        ibs_cbs_taxation=_parse_ibs_cbs_taxation(inf_nfse, inf_dps),
        total=_parse_total(inf_nfse, inf_dps),
        complementary_info=_parse_complementary_info(inf_nfse, inf_dps),
        receipt=_parse_receipt(inf_nfse),
    )


def parse_header(xml_file: str | Path) -> HeaderData:
    return parse_danfse(xml_file).header


def parse_provider(xml_file: str | Path) -> ProviderData:
    return parse_danfse(xml_file).provider


def parse_customer(xml_file: str | Path) -> CustomerData:
    return parse_danfse(xml_file).customer


def parse_destination(xml_file: str | Path) -> DestinationData:
    return parse_danfse(xml_file).destination


def parse_intermediary(xml_file: str | Path) -> IntermediaryData:
    return parse_danfse(xml_file).intermediary


def parse_service(xml_file: str | Path) -> ServiceData:
    return parse_danfse(xml_file).service


def parse_municipal_taxation(xml_file: str | Path) -> MunicipalTaxationData:
    return parse_danfse(xml_file).municipal_taxation


def parse_federal_taxation(xml_file: str | Path) -> FederalTaxationData:
    return parse_danfse(xml_file).federal_taxation


def parse_ibs_cbs_taxation(xml_file: str | Path) -> IbsCbsTaxationData:
    return parse_danfse(xml_file).ibs_cbs_taxation


def parse_total(xml_file: str | Path) -> TotalData:
    return parse_danfse(xml_file).total


def parse_complementary_info(xml_file: str | Path) -> ComplementaryInfoData:
    return parse_danfse(xml_file).complementary_info


def parse_receipt(xml_file: str | Path) -> ReceiptData:
    return parse_danfse(xml_file).receipt


def _parse_header(inf_nfse: ET.Element, inf_dps: ET.Element) -> HeaderData:
    emit_endereco = _path(inf_nfse, "emit", "enderNac")
    ibscbs = _path(inf_dps, "IBSCBS")
    national_tax_code = missing_if_blank(_text(_path(inf_dps, "serv", "cServ"), "cTribNac"))

    access_key = strip_nfse_prefix(inf_nfse.attrib.get("Id"))
    status = describe(CSTAT, _text(inf_nfse, "cStat"))
    purpose = describe(
        FIN_NFSE,
        first_present(
            _text(inf_dps, "finNFSe"),
            _text(ibscbs, "finNFSe") if ibscbs is not None else None,
        ),
    )

    return HeaderData(
        access_key=access_key,
        nfse_number=missing_if_blank(_text(inf_nfse, "nNFSe")),
        competence_date=format_date(_text(inf_dps, "dCompet")),
        nfse_issued_at=format_datetime(_text(inf_nfse, "dhProc")),
        dps_number=missing_if_blank(_text(inf_dps, "nDPS")),
        dps_series=missing_if_blank(_text(inf_dps, "serie")),
        dps_issued_at=format_datetime(_text(inf_dps, "dhEmi")),
        issuer=ellipsize(describe(TP_EMIT, _text(inf_dps, "tpEmit")), 13),
        status=ellipsize(status, 40),
        purpose=ellipsize(purpose, 40),
        issuer_city=missing_if_blank(_text(inf_nfse, "xLocEmi")),
        issuer_state=missing_if_blank(_text(emit_endereco, "UF") if emit_endereco is not None else None),
        generator_environment=missing_if_blank(_text(inf_nfse, "ambGer")),
        national_environment=missing_if_blank(_text(inf_dps, "tpAmb")),
        show_municipality=not national_tax_code.startswith("99"),
        debit_note_type=ellipsize(describe(TP_NFSE_DEBITO, _text(inf_dps, "tpNFSeDebito")), 80),
        credit_note_type=ellipsize(describe(TP_NFSE_CREDITO, _text(inf_dps, "tpNFSeCredito")), 80),
    )


def _parse_provider(inf_dps: ET.Element) -> ProviderData:
    prest = _child(inf_dps, "prest")
    if prest is None:
        raise InvalidNFSeXmlError("XML nao contem NFSe/infNFSe/DPS/infDPS/prest.")

    reg_trib = _child(prest, "regTrib")
    end = _child(prest, "end")
    end_nac = _child(end, "endNac")
    end_ext = _child(end, "endExt")

    return ProviderData(
        tax_id=_format_tax_id(prest),
        municipal_registration=missing_if_blank(_text(prest, "IM")),
        phone=missing_if_blank(_text(prest, "fone")),
        name=ellipsize(missing_if_blank(_text(prest, "xNome")), 80),
        municipality_state=_provider_municipality_state(end_nac, end_ext),
        ibge_cep=_provider_ibge_cep(end_nac, end_ext),
        address=ellipsize(
            join_present(
                _text(end, "xLgr"),
                _text(end, "nro"),
                _text(end, "xCpl"),
                _text(end, "xBairro"),
            ),
            80,
        ),
        email=missing_if_blank(_text(prest, "email")),
        simples_nacional=ellipsize(describe(OP_SIMP_NAC, _text(reg_trib, "opSimpNac")), 40),
        sn_tax_regime=ellipsize(describe(REG_AP_TRIB_SN, _text(reg_trib, "regApTribSN")), 80),
        ibs_cbs_sn_tax_regime=ellipsize(
            describe(REG_AP_IBS_CBS_SN, _text(reg_trib, "regApIBSCBSSN")),
            80,
        ),
    )


def _parse_customer(inf_dps: ET.Element) -> CustomerData:
    toma = _child(inf_dps, "toma")
    if toma is None:
        return CustomerData(
            tax_id="-",
            municipal_registration="-",
            phone="-",
            name="-",
            municipality_state="-",
            ibge_cep="-",
            address="-",
            email="-",
            unidentified_message="TOMADOR/ADQUIRENTE DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
        )

    end = _child(toma, "end")
    end_nac = _child(end, "endNac")
    end_ext = _child(end, "endExt")

    return CustomerData(
        tax_id=_format_tax_id(toma),
        municipal_registration=missing_if_blank(_text(toma, "IM")),
        phone=missing_if_blank(_text(toma, "fone")),
        name=ellipsize(missing_if_blank(_text(toma, "xNome")), 80),
        municipality_state=_party_municipality_state(end_nac, end_ext),
        ibge_cep=_party_ibge_cep(end_nac, end_ext),
        address=ellipsize(
            join_present(
                _text(end, "xLgr"),
                _text(end, "nro"),
                _text(end, "xCpl"),
                _text(end, "xBairro"),
            ),
            80,
        ),
        email=missing_if_blank(_text(toma, "email")),
    )


def _parse_destination(inf_dps: ET.Element) -> DestinationData:
    dest = _path(inf_dps, "IBSCBS", "dest")
    if dest is None:
        return DestinationData(
            tax_id="-",
            phone="-",
            name="-",
            municipality_state="-",
            ibge_cep="-",
            address="-",
            email="-",
            unidentified_message="DESTINATÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
        )

    end = _child(dest, "end")
    end_nac = _child(end, "endNac")
    end_ext = _child(end, "endExt")

    return DestinationData(
        tax_id=_format_tax_id(dest),
        phone=missing_if_blank(_text(dest, "fone")),
        name=ellipsize(missing_if_blank(_text(dest, "xNome")), 80),
        municipality_state=_party_municipality_state(end_nac, end_ext),
        ibge_cep=_party_ibge_cep(end_nac, end_ext),
        address=ellipsize(
            join_present(
                _text(end, "xLgr"),
                _text(end, "nro"),
                _text(end, "xCpl"),
                _text(end, "xBairro"),
            ),
            80,
        ),
        email=missing_if_blank(_text(dest, "email")),
    )


def _parse_intermediary(inf_dps: ET.Element) -> IntermediaryData:
    interm = _child(inf_dps, "interm")
    if interm is None:
        return IntermediaryData(
            tax_id="-",
            municipal_registration="-",
            phone="-",
            name="-",
            municipality_state="-",
            ibge_cep="-",
            address="-",
            email="-",
            unidentified_message="INTERMEDIÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
        )

    end = _child(interm, "end")
    end_nac = _child(end, "endNac")
    end_ext = _child(end, "endExt")

    return IntermediaryData(
        tax_id=_format_tax_id(interm),
        municipal_registration=missing_if_blank(_text(interm, "IM")),
        phone=missing_if_blank(_text(interm, "fone")),
        name=ellipsize(missing_if_blank(_text(interm, "xNome")), 80),
        municipality_state=_party_municipality_state(end_nac, end_ext),
        ibge_cep=_party_ibge_cep(end_nac, end_ext),
        address=ellipsize(
            join_present(
                _text(end, "xLgr"),
                _text(end, "nro"),
                _text(end, "xCpl"),
                _text(end, "xBairro"),
            ),
            80,
        ),
        email=missing_if_blank(_text(interm, "email")),
    )


def _parse_service(inf_nfse: ET.Element, inf_dps: ET.Element) -> ServiceData:
    service = _child(inf_dps, "serv")
    c_serv = _child(service, "cServ")
    loc_prest = _child(service, "locPrest")

    c_trib_nac = format_national_taxation_code(_text(c_serv, "cTribNac"))
    c_trib_mun = missing_if_blank(_text(c_serv, "cTribMun"))
    taxation_code = c_trib_nac if c_trib_mun == MISSING_VALUE else f"{c_trib_nac} / {c_trib_mun}"

    c_loc_prestacao = missing_if_blank(_text(loc_prest, "cLocPrestacao"))
    country = missing_if_blank(_text(loc_prest, "cPaisPrestacao"))
    if c_loc_prestacao != MISSING_VALUE:
        location = describe_municipality_state(c_loc_prestacao)
        if country != MISSING_VALUE:
            location = f"{location} / {country}"
    else:
        location = missing_if_blank(_text(inf_nfse, "xLocPrestacao"))

    taxation_description = first_present(_text(inf_nfse, "xTribMun"), _text(inf_nfse, "xTribNac"))

    return ServiceData(
        taxation_code=taxation_code,
        nbs_code=format_nbs_code(_text(c_serv, "cNBS")),
        location=ellipsize(location, 42),
        taxation_description=ellipsize(taxation_description, 170),
        service_description=ellipsize(missing_if_blank(_text(c_serv, "xDescServ")), 1300),
        simples_nacional_activity=ellipsize(describe(C_ATV_SN, _text(c_serv, "cAtvSN")), 80),
    )


def _parse_municipal_taxation(inf_nfse: ET.Element, inf_dps: ET.Element) -> MunicipalTaxationData:
    valores_nfse = _child(inf_nfse, "valores")
    trib = _path(inf_dps, "valores", "trib")
    trib_mun = _child(trib, "tribMun")
    reg_trib = _path(inf_dps, "prest", "regTrib")
    exig_susp = _child(trib_mun, "exigSusp")

    trib_issqn_code = _text(trib_mun, "tribISSQN")
    if missing_if_blank(trib_issqn_code) == MISSING_VALUE:
        return MunicipalTaxationData(
            taxation_type="-",
            incidence_location="-",
            special_regime="-",
            immunity_type="-",
            suspension="-",
            suspension_process="-",
            municipal_benefit="-",
            bm_calculation="-",
            total_deductions_reductions="-",
            unconditional_discount="-",
            issqn_base="-",
            applied_rate="-",
            retention="-",
            issqn_amount="-",
            non_taxable_message="TRIBUTAÇÃO MUNICIPAL (ISSQN) - OPERAÇÃO NÃO SUJEITA AO ISSQN",
        )

    special_regime = ellipsize(describe(REG_ESP_TRIB, _text(reg_trib, "regEspTrib")), 40)
    immunity_type = ellipsize(describe(TP_IMUNIDADE_ISSQN, _text(trib_mun, "tpImunidade")), 40)
    suspension = ellipsize(describe(TP_SUSP_ISSQN, _text(exig_susp, "tpSusp")), 40)
    suspension_process = ellipsize(missing_if_blank(_text(exig_susp, "nProcesso")), 30)
    municipal_benefit = ellipsize(describe(TP_BM_ISSQN, _text(valores_nfse, "tpBM")), 40)
    bm_calculation = _first_present_value(
        _text(valores_nfse, "vCalcBM"),
        _text(valores_nfse, "vRedBCBM"),
        _text(trib_mun, "vCalcBM"),
        _text(trib_mun, "vRedBCBM"),
    )
    total_deductions_reductions = _total_deductions_reductions(inf_nfse, inf_dps)
    unconditional_discount = _first_present_value(
        _path_text(_child(inf_dps, "valores"), "vDescCondIncond", "vDescIncond"),
        _text(_child(inf_dps, "valores"), "vDescIncond"),
    )

    suppress_optional_row_one = all(
        value == MISSING_VALUE
        for value in (special_regime, immunity_type, suspension, suspension_process)
    )
    suppress_optional_row_two = all(
        value == MISSING_VALUE
        for value in (
            municipal_benefit,
            bm_calculation,
            total_deductions_reductions,
            unconditional_discount,
        )
    )

    return MunicipalTaxationData(
        taxation_type=ellipsize(describe(TRIB_ISSQN, trib_issqn_code), 21),
        incidence_location=ellipsize(_incidence_location(inf_nfse, trib_mun), 42),
        special_regime=special_regime,
        immunity_type=immunity_type,
        suspension=suspension,
        suspension_process=suspension_process,
        municipal_benefit=municipal_benefit,
        bm_calculation=bm_calculation,
        total_deductions_reductions=total_deductions_reductions,
        unconditional_discount=unconditional_discount,
        issqn_base=_first_present_value(_text(valores_nfse, "vBC")),
        applied_rate=_first_present_value(_text(valores_nfse, "pAliqAplic")),
        retention=ellipsize(describe(TP_RET_ISSQN, _text(trib_mun, "tpRetISSQN")), 25),
        issqn_amount=_first_present_value(_text(valores_nfse, "vISSQN")),
        suppress_optional_row_one=suppress_optional_row_one,
        suppress_optional_row_two=suppress_optional_row_two,
    )


def _parse_federal_taxation(inf_dps: ET.Element) -> FederalTaxationData:
    trib_fed = _path(inf_dps, "valores", "trib", "tribFed")
    piscofins = _child(trib_fed, "piscofins")
    competence = missing_if_blank(_text(inf_dps, "dCompet"))

    return FederalTaxationData(
        irrf=_first_present_value(_text(trib_fed, "vRetIRRF")),
        previdenciaria_retida=_first_present_value(_text(trib_fed, "vRetCP")),
        sociais_retidas=_first_present_value(_text(trib_fed, "vRetCSLL")),
        pis_debito=_first_present_value(_text(piscofins, "vPis")),
        cofins_debito=_first_present_value(_text(piscofins, "vCofins")),
        retention_description=ellipsize(
            describe(TP_RET_PIS_COFINS, _text(piscofins, "tpRetPisCofins")),
            35,
        ),
        show_legacy_piscofins_row=competence == MISSING_VALUE or competence[:4] <= "2026",
    )


def _parse_ibs_cbs_taxation(inf_nfse: ET.Element, inf_dps: ET.Element) -> IbsCbsTaxationData:
    ibscbs_dps = _child(inf_dps, "IBSCBS")
    ibscbs_nfse = _child(inf_nfse, "IBSCBS")
    ibscbs_values = _path(ibscbs_nfse, "valores")
    g_ibscbs = _path(ibscbs_dps, "valores", "trib", "gIBSCBS")
    uf_values = _child(ibscbs_values, "uf")
    mun_values = _child(ibscbs_values, "mun")
    fed_values = _child(ibscbs_values, "fed")
    tot_cibs = _path(ibscbs_nfse, "totCIBS")
    g_ibs = _child(tot_cibs, "gIBS")
    g_ibs_mun = _child(g_ibs, "gIBSMunTot")
    g_ibs_uf = _child(g_ibs, "gIBSUFTot")
    g_cbs = _child(tot_cibs, "gCBS")
    g_trib_sn = _child(tot_cibs, "gTribSN")
    g_adjustment = _path(ibscbs_dps, "valores", "trib", "gIBSCBSAjuste")
    imovel = _child(ibscbs_dps, "imovel")
    linked_payments = _path(ibscbs_dps, "gPgtoVinc")

    return IbsCbsTaxationData(
        cst_classification=_join_values(
            _text(g_ibscbs, "CST"),
            _text(g_ibscbs, "cClassTrib"),
            max_chars=12,
        ),
        operation_indicator=ellipsize(_ibs_cbs_operation_indicator(ibscbs_dps, ibscbs_nfse), 56),
        exclusions_reductions=_ibs_cbs_exclusions_reductions(inf_nfse, inf_dps),
        base_after_reductions=_first_present_value(_text(ibscbs_values, "vBC")),
        rate_reductions=_join_values(
            _text(uf_values, "pRedAliqUF"),
            _text(mun_values, "pRedAliqMun"),
            _text(fed_values, "pRedAliqCBS"),
            max_chars=24,
        ),
        ibs_rates=_join_values(_text(uf_values, "pIBSUF"), _text(mun_values, "pIBSMun"), max_chars=16),
        ibs_municipal_effective_rate=_first_present_value(_text(mun_values, "pAliqEfetMun")),
        ibs_municipal_amount=_first_present_value(_text(g_ibs_mun, "vIBSMun")),
        ibs_state_effective_rate=_first_present_value(_text(uf_values, "pAliqEfetUF")),
        ibs_state_amount=_first_present_value(_text(g_ibs_uf, "vIBSUF")),
        ibs_total=_first_present_value(_text(g_ibs, "vIBSTot"), _text(g_trib_sn, "vIBSSN")),
        cbs_rate=_first_present_value(_text(fed_values, "pCBS"), _text(g_trib_sn, "pCBSSN")),
        cbs_effective_rate=_first_present_value(_text(fed_values, "pAliqEfetCBS")),
        cbs_total=_first_present_value(_text(g_cbs, "vCBS"), _text(g_trib_sn, "vCBSSN")),
        adjustment_ibs=_first_present_value(_text(g_adjustment, "vIBS")),
        adjustment_cbs=_first_present_value(_text(g_adjustment, "vCBS")),
        final_consumer_indicator=describe({"0": "Não", "1": "Sim"}, _text(ibscbs_dps, "indFinal")),
        sn_gross_revenue=_first_present_value(_text(ibscbs_values, "vReceitaBrutaSN")),
        sn_ibs_rate=_first_present_value(_text(g_trib_sn, "pIBSSN")),
        sn_ibs_amount=_first_present_value(_text(g_trib_sn, "vIBSSN")),
        sn_cbs_rate=_first_present_value(_text(g_trib_sn, "pCBSSN")),
        sn_cbs_amount=_first_present_value(_text(g_trib_sn, "vCBSSN")),
        real_estate_summary=_real_estate_summary(imovel),
        movable_property_count=_count_or_missing(_children(ibscbs_dps, "bensMoveis")),
        linked_payment_count=_count_or_missing(_children(linked_payments, "pgto")),
    )


def _parse_total(inf_nfse: ET.Element, inf_dps: ET.Element) -> TotalData:
    valores_nfse = _child(inf_nfse, "valores")
    valores_dps = _child(inf_dps, "valores")
    desconto = _child(valores_dps, "vDescCondIncond")
    ibscbs_nfse = _child(inf_nfse, "IBSCBS")
    tot_cibs = _child(ibscbs_nfse, "totCIBS")
    g_ibs = _path(tot_cibs, "gIBS")
    g_cbs = _path(tot_cibs, "gCBS")
    g_trib_sn = _path(tot_cibs, "gTribSN")

    return TotalData(
        service_amount=_first_present_value(_path_text(valores_dps, "vServPrest", "vServ")),
        unconditional_discount=_first_present_value(_text(desconto, "vDescIncond")),
        conditional_discount=_first_present_value(_text(desconto, "vDescCond")),
        total_retentions=_first_present_value(_text(valores_nfse, "vTotalRet")),
        nfse_net_amount=_first_present_value(_text(valores_nfse, "vLiq")),
        ibs_cbs_total=_sum_or_missing(
            _text(g_ibs, "vIBSTot"),
            _text(g_cbs, "vCBS"),
            _text(g_trib_sn, "vIBSSN"),
            _text(g_trib_sn, "vCBSSN"),
        ),
        nfse_net_amount_with_ibs_cbs=_first_present_value(_text(tot_cibs, "vTotNF")),
    )


def _parse_complementary_info(inf_nfse: ET.Element, inf_dps: ET.Element) -> ComplementaryInfoData:
    parts: list[str] = []
    info_compl = _path(inf_dps, "serv", "infoCompl")
    serv = _child(inf_dps, "serv")
    subst = _child(inf_dps, "subst")
    obra = _child(serv, "obra")
    imovel = _path(inf_dps, "IBSCBS", "imovel")
    atv_evento = _child(serv, "atvEvento")
    item_ped = _path(info_compl, "gItemPed")

    _append_prefixed(parts, "Inf. Cont.:", _text(info_compl, "xInfComp"))
    _append_prefixed(parts, "NFS-e Subst.:", _text(subst, "chSubstda"))
    _append_prefixed(parts, "Doc. Ref.:", _text(info_compl, "docRef"))
    _append_prefixed(parts, "Cod. Obra:", _text(obra, "cObra"))
    _append_prefixed(parts, "Insc. Imob.:", _text(imovel, "inscImobFisc"))
    _append_prefixed(parts, "Cod. Evt.:", _text(atv_evento, "idAtvEvt"))
    _append_prefixed(parts, "Doc. Tec.:", _text(info_compl, "idDocTec"))
    _append_prefixed(parts, "Núm. Ped.:", _text(info_compl, "xPed"))
    _append_prefixed(parts, "Item Ped.:", _text(item_ped, "xItemPed"))
    _append_prefixed(parts, "Inf. A. T. Mun.:", _text(info_compl, "xOutInf"))
    _append_prefixed(parts, "Totais Aproximados dos Tributos cfe. Lei nº 12.741/2012:", _approximate_taxes(inf_dps))

    return ComplementaryInfoData(text=ellipsize(" | ".join(parts) if parts else MISSING_VALUE, 2000))


def _parse_receipt(inf_nfse: ET.Element) -> ReceiptData:
    access_key = strip_nfse_prefix(inf_nfse.attrib.get("Id"))
    nfse_number = missing_if_blank(_text(inf_nfse, "nNFSe"))
    number_key = MISSING_VALUE
    if nfse_number != MISSING_VALUE and access_key != MISSING_VALUE:
        number_key = ellipsize(f"{nfse_number} / {access_key}", 66)
    return ReceiptData(
        acknowledgement_date="",
        identification_signature="",
        nfse_number_access_key=number_key,
    )


def _format_tax_id(prest: ET.Element) -> str:
    cnpj = _text(prest, "CNPJ")
    cpf = _text(prest, "CPF")
    nif = _text(prest, "NIF")
    if missing_if_blank(cnpj) != MISSING_VALUE:
        return format_cnpj(cnpj)
    if missing_if_blank(cpf) != MISSING_VALUE:
        return format_cpf(cpf)
    return missing_if_blank(nif)


def _provider_municipality_state(end_nac: ET.Element | None, end_ext: ET.Element | None) -> str:
    c_mun = missing_if_blank(_text(end_nac, "cMun") if end_nac is not None else None)
    if c_mun != MISSING_VALUE:
        return describe_municipality_state(c_mun)
    return missing_if_blank(_text(end_ext, "xCidade") if end_ext is not None else None)


def _provider_ibge_cep(end_nac: ET.Element | None, end_ext: ET.Element | None) -> str:
    return _party_ibge_cep(end_nac, end_ext)


def _party_municipality_state(end_nac: ET.Element | None, end_ext: ET.Element | None) -> str:
    c_mun = missing_if_blank(_text(end_nac, "cMun") if end_nac is not None else None)
    if c_mun != MISSING_VALUE:
        return describe_municipality_state(c_mun)
    return missing_if_blank(_text(end_ext, "xCidade") if end_ext is not None else None)


def _party_ibge_cep(end_nac: ET.Element | None, end_ext: ET.Element | None) -> str:
    c_mun = missing_if_blank(_text(end_nac, "cMun") if end_nac is not None else None)
    cep = missing_if_blank(_text(end_nac, "CEP") if end_nac is not None else None)
    c_end_post = missing_if_blank(_text(end_ext, "cEndPost") if end_ext is not None else None)
    if c_mun != MISSING_VALUE:
        return f"{c_mun} / {format_cep(cep)}" if cep != MISSING_VALUE else MISSING_VALUE
    return first_present(c_end_post)


def _incidence_location(inf_nfse: ET.Element, trib_mun: ET.Element | None) -> str:
    c_loc_incid = missing_if_blank(_text(inf_nfse, "cLocIncid"))
    c_pais_result = missing_if_blank(_text(trib_mun, "cPaisResult"))
    if c_loc_incid != MISSING_VALUE:
        location = describe_municipality_state(c_loc_incid)
    else:
        location = missing_if_blank(_text(inf_nfse, "xLocIncid"))
    if c_pais_result == MISSING_VALUE:
        return location
    if location == MISSING_VALUE:
        return c_pais_result
    return f"{location} / {c_pais_result}"


def _total_deductions_reductions(inf_nfse: ET.Element, inf_dps: ET.Element) -> str:
    valores_dps = _child(inf_dps, "valores")
    ajuste_bc = _child(valores_dps, "vAjusteBC")
    legacy_direct_value = _first_present_value(
        _text(valores_dps, "vDedRed"),
        _path_text(inf_nfse, "IBSCBS", "valores", "vDR"),
        _path_text(inf_dps, "IBSCBS", "valores", "vDR"),
    )
    if legacy_direct_value != MISSING_VALUE:
        return legacy_direct_value

    nt009_adjustment = _sum_decimal_strings(
        _text(ajuste_bc, "vAjusteBCISSQN"),
        _text(ajuste_bc, "vCalcAjusteBCISSQN"),
        _sum_adjustment_documents(ajuste_bc),
    )
    if nt009_adjustment != MISSING_VALUE:
        return nt009_adjustment

    return _sum_decimal_strings(
        _text(valores_dps, "vCalcDR"),
        _text(valores_dps, "vCalcReeRepRes"),
        _text(_child(inf_nfse, "valores"), "vCalcDR"),
        _text(_child(inf_nfse, "valores"), "vCalcReeRepRes"),
    )


def _sum_adjustment_documents(ajuste_bc: ET.Element | None) -> str:
    documents = _child(ajuste_bc, "documentos")
    if documents is None:
        return MISSING_VALUE
    values = [
        _text(doc, "vAjuteAplic")
        for doc in _children(documents, "docAjusteBC")
    ]
    return _sum_or_missing(*values)


def _first_present_value(*values: str | None) -> str:
    return first_present(*values)


def _sum_decimal_strings(*values: str | None) -> str:
    total = Decimal("0")
    found = False
    for value in values:
        normalized = missing_if_blank(value)
        if normalized == MISSING_VALUE:
            continue
        try:
            total += Decimal(normalized)
        except InvalidOperation as exc:
            raise InvalidNFSeXmlError(f"Valor decimal invalido no XML: {normalized}") from exc
        found = True
    if not found:
        return MISSING_VALUE
    return f"{total:.2f}"


def _sum_or_missing(*values: str | None) -> str:
    present = [value for value in values if missing_if_blank(value) != MISSING_VALUE]
    if not present:
        return MISSING_VALUE
    return _sum_decimal_strings(*present)


def _join_values(*values: str | None, max_chars: int) -> str:
    formatted = [missing_if_blank(value) for value in values]
    if all(value == MISSING_VALUE for value in formatted):
        return MISSING_VALUE
    return ellipsize(" / ".join(formatted), max_chars)


def _ibs_cbs_operation_indicator(ibscbs_dps: ET.Element | None, ibscbs_nfse: ET.Element | None) -> str:
    c_ind_op = missing_if_blank(
        first_present(
            _text(ibscbs_dps, "cIndOp"),
            _text(ibscbs_nfse, "cIndOp"),
        )
    )
    c_localidade = missing_if_blank(_text(ibscbs_nfse, "cLocalidadeIncid"))
    x_localidade = missing_if_blank(_text(ibscbs_nfse, "xLocalidadeIncid"))
    if c_localidade != MISSING_VALUE and x_localidade == MISSING_VALUE:
        x_localidade = describe_municipality_state(c_localidade)
    return _join_values(c_ind_op, c_localidade, x_localidade, max_chars=56)


def _ibs_cbs_exclusions_reductions(inf_nfse: ET.Element, inf_dps: ET.Element) -> str:
    valores_dps = _child(inf_dps, "valores")
    valores_nfse = _child(inf_nfse, "valores")
    ajuste_bc = _child(valores_dps, "vAjusteBC")
    piscofins = _path(valores_dps, "trib", "tribFed", "piscofins")
    return _sum_or_missing(
        _path_text(valores_dps, "vDescCondIncond", "vDescIncond"),
        _sum_adjustment_documents(ajuste_bc),
        _path_text(inf_nfse, "IBSCBS", "valores", "vCalcReeRepRes"),
        _text(valores_nfse, "vISSQN"),
        _text(piscofins, "vPis"),
        _text(piscofins, "vCofins"),
    )


def _real_estate_summary(imovel: ET.Element | None) -> str:
    if imovel is None:
        return MISSING_VALUE

    c_mun = missing_if_blank(_text(imovel, "cMun"))
    locacao = _child(imovel, "gLocacao")
    units = _children(imovel, "gUnidImob")
    parts: list[str] = []
    if c_mun != MISSING_VALUE:
        parts.append(f"Município: {describe_municipality_state(c_mun)}")
    _append_prefixed(parts, "Copropriedade:", _text(locacao, "pCopropriedade"))
    _append_prefixed(parts, "Valor total operação:", _text(locacao, "vTotOper"))
    if units:
        parts.append(f"Unidades: {len(units)}")
    return ellipsize(" | ".join(parts) if parts else MISSING_VALUE, 200)


def _count_or_missing(values: list[ET.Element]) -> str:
    if not values:
        return MISSING_VALUE
    return str(len(values))


def _append_prefixed(parts: list[str], label: str, value: str | None) -> None:
    formatted = missing_if_blank(value)
    if formatted != MISSING_VALUE:
        parts.append(f"{label} {formatted}")


def _approximate_taxes(inf_dps: ET.Element) -> str:
    total = _path(inf_dps, "valores", "trib", "totTrib", "vTotTrib")
    percent = _path(inf_dps, "valores", "trib", "totTrib", "pTotTrib")
    fed = missing_if_blank(_text(total, "vTotTribFed"))
    est = missing_if_blank(_text(total, "vTotTribEst"))
    mun = missing_if_blank(_text(total, "vTotTribMun"))
    suffix = "R$"
    if fed == MISSING_VALUE and est == MISSING_VALUE and mun == MISSING_VALUE:
        fed = missing_if_blank(_text(percent, "pTotTribFed"))
        est = missing_if_blank(_text(percent, "pTotTribEst"))
        mun = missing_if_blank(_text(percent, "pTotTribMun"))
        suffix = "%"
    if fed == MISSING_VALUE and est == MISSING_VALUE and mun == MISSING_VALUE:
        return MISSING_VALUE
    return f"Federais: {suffix} {fed}; Estaduais: {suffix} {est}; Municipais: {suffix} {mun}"


def _path_text(element: ET.Element | None, *names: str) -> str | None:
    target = _path(element, *names)
    if target is None:
        return None
    return target.text


def format_national_taxation_code(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE or len(value) != 6 or not value.isdigit():
        return value
    return f"{value[:2]}.{value[2:4]}.{value[4:]}"


def format_nbs_code(value: str | None) -> str:
    value = missing_if_blank(value)
    if value == MISSING_VALUE or len(value) != 9 or not value.isdigit():
        return value
    return f"{value[:1]}.{value[1:5]}.{value[5:7]}.{value[7:]}"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element: ET.Element | None, name: str) -> ET.Element | None:
    if element is None:
        return None
    for child in element:
        if _local_name(child.tag) == name:
            return child
    return None


def _children(element: ET.Element | None, name: str) -> list[ET.Element]:
    if element is None:
        return []
    return [child for child in element if _local_name(child.tag) == name]


def _path(element: ET.Element | None, *names: str) -> ET.Element | None:
    current = element
    for name in names:
        current = _child(current, name)
        if current is None:
            return None
    return current


def _text(element: ET.Element | None, name: str) -> str | None:
    child = _child(element, name)
    if child is None:
        return None
    return child.text
