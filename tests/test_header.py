from pathlib import Path
import sys
import types
import tempfile
from unittest import TestCase

from danfse_nt008.models import CONSULTA_PUBLICA_URL
from danfse_nt008.xml import (
    parse_complementary_info,
    parse_customer,
    parse_danfse,
    parse_destination,
    parse_federal_taxation,
    parse_header,
    parse_ibs_cbs_taxation,
    parse_intermediary,
    parse_municipal_taxation,
    parse_service,
    parse_total,
    parse_receipt,
)
from danfse_nt008.html import render_danfse_html, render_header_html
from danfse_nt008.pdf import render_header_pdf
from danfse_nt008.compliance import REQUIRED_FONTS
from danfse_nt008.municipalities import describe_municipality_state
from danfse_nt008.validation import validate_danfse_data, validate_layout_constants


class HeaderParsingTest(TestCase):
    def setUp(self):
        self.document = parse_danfse(Path(__file__).resolve().parents[1] / "xml.xml")
        self.data = parse_header(Path(__file__).resolve().parents[1] / "xml.xml")

    def test_extracts_access_key_without_nfse_prefix(self):
        self.assertEqual(
            self.data.access_key,
            "42082031202378779002233000000064529626050261847801",
        )

    def test_extracts_identification_fields(self):
        self.assertEqual(self.data.nfse_number, "645296")
        self.assertEqual(self.data.competence_date, "29/05/2026")
        self.assertEqual(self.data.nfse_issued_at, "29/05/2026 17:43:37")
        self.assertEqual(self.data.dps_number, "738945")
        self.assertEqual(self.data.dps_series, "5000")
        self.assertEqual(self.data.dps_issued_at, "29/05/2026 03:10:04")
        self.assertEqual(self.data.issuer, "Prestador")
        self.assertEqual(self.data.status, "NFS-e Gerada")
        self.assertEqual(self.data.purpose, "-")

    def test_builds_header_context(self):
        self.assertEqual(self.data.municipality_line, "Município: ITAJAÍ / SC")
        self.assertEqual(self.data.generator_environment, "1")
        self.assertEqual(self.data.national_environment, "1")
        self.assertFalse(self.data.is_restricted_production)
        self.assertEqual(
            self.data.consultation_url,
            f"{CONSULTA_PUBLICA_URL}{self.data.access_key}",
        )

    def test_hides_municipality_for_national_tax_code_99(self):
        xml_path = Path(__file__).resolve().parents[1] / "xml.xml"
        xml = xml_path.read_text(encoding="utf-8").replace(
            "<cTribNac>100601</cTribNac>",
            "<cTribNac>990000</cTribNac>",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-8", delete=False) as tmp:
            tmp.write(xml)
            tmp_path = Path(tmp.name)
        try:
            data = parse_header(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertFalse(data.show_municipality)
        self.assertEqual(data.municipality_line, "")

    def test_renders_header_html(self):
        test_case = self

        class FakeImage:
            def save(self, buffer, format):
                test_case.assertEqual(format, "PNG")
                buffer.write(b"png")

        fake_qrcode = types.SimpleNamespace(make=lambda value: FakeImage())
        original = sys.modules.get("qrcode")
        sys.modules["qrcode"] = fake_qrcode
        try:
            html = render_header_html(self.data)
        finally:
            if original is None:
                del sys.modules["qrcode"]
            else:
                sys.modules["qrcode"] = original

        self.assertIn("DANFSe v2.0", html)
        self.assertIn("Documento Auxiliar da NFS-e", html)
        self.assertIn(self.data.access_key, html)
        self.assertIn("data:image/png;base64,cG5n", html)
        self.assertIn("left: .18cm;", html)
        self.assertIn("top: .18cm;", html)
        self.assertIn("font-size: 8pt;", html)
        self.assertIn("font-size: 6pt;", html)
        self.assertIn("font-size: 7pt;", html)

    def test_declares_required_normative_fonts(self):
        self.assertEqual(REQUIRED_FONTS, ("Arial", "Microsoft Sans Serif"))

    def test_extracts_provider_fields_without_using_emit_fallbacks(self):
        provider = self.document.provider
        self.assertEqual(provider.tax_id, "02.378.779/0022-33")
        self.assertEqual(provider.municipal_registration, "290355")
        self.assertEqual(provider.phone, "1332119500")
        self.assertEqual(provider.name, "-")
        self.assertEqual(provider.municipality_state, "-")
        self.assertEqual(provider.ibge_cep, "-")
        self.assertEqual(provider.address, "-")
        self.assertEqual(provider.email, "br241-nfe.brazil@msc.com")
        self.assertEqual(provider.simples_nacional, "Não Optante")
        self.assertEqual(provider.sn_tax_regime, "-")

    def test_extracts_customer_fields(self):
        customer = parse_customer(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(customer.tax_id, "12.487.655/0003-87")
        self.assertEqual(customer.municipal_registration, "312352")
        self.assertEqual(customer.phone, "4839522448")
        self.assertEqual(customer.name, "INEOS STYROLUTION DO BRASIL POLIMEROS LTDA")
        self.assertEqual(customer.municipality_state, "Itajaí / SC")
        self.assertEqual(customer.ibge_cep, "4208203 / 88.316-300")
        self.assertEqual(customer.address, "ITAIPAVA, 850, SALA 05, ITAIPAVA")
        self.assertEqual(customer.email, "sabrina.burchardt@pibernat.com.br")

    def test_describes_official_ibge_municipality_table(self):
        self.assertEqual(describe_municipality_state("3106200"), "Belo Horizonte / MG")

    def test_parses_customer_with_belo_horizonte_ibge_code(self):
        xml_path = Path(__file__).resolve().parents[1] / "xml.xml"
        xml = xml_path.read_text(encoding="utf-8").replace(
            "<cMun>4208203</cMun>",
            "<cMun>3106200</cMun>",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-8", delete=False) as tmp:
            tmp.write(xml)
            tmp_path = Path(tmp.name)
        try:
            customer = parse_customer(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertEqual(customer.municipality_state, "Belo Horizonte / MG")

    def test_extracts_unidentified_destination_when_missing(self):
        destination = parse_destination(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(
            destination.unidentified_message,
            "DESTINATÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
        )
        self.assertEqual(destination.tax_id, "-")

    def test_extracts_unidentified_intermediary_when_missing(self):
        intermediary = parse_intermediary(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(
            intermediary.unidentified_message,
            "INTERMEDIÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
        )
        self.assertEqual(intermediary.tax_id, "-")

    def test_extracts_service_fields(self):
        service = parse_service(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(service.taxation_code, "10.06.01")
        self.assertEqual(service.nbs_code, "1.0607.00.00")
        self.assertEqual(service.location, "Itajaí / SC")
        self.assertEqual(service.taxation_description, "10.06.01 Agenciamento marítimo.")
        self.assertIn("Taxa de liberacao", service.service_description)

    def test_extracts_municipal_taxation_fields(self):
        municipal = parse_municipal_taxation(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(municipal.taxation_type, "Operação Tributável")
        self.assertEqual(municipal.incidence_location, "Itajaí / SC")
        self.assertEqual(municipal.special_regime, "Nenhum")
        self.assertEqual(municipal.issqn_base, "1219.00")
        self.assertEqual(municipal.applied_rate, "3.00")
        self.assertEqual(municipal.retention, "Não Retido")
        self.assertEqual(municipal.issqn_amount, "36.57")
        self.assertFalse(municipal.suppress_optional_row_one)
        self.assertTrue(municipal.suppress_optional_row_two)

    def test_extracts_federal_taxation_fields(self):
        federal = parse_federal_taxation(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(federal.irrf, "-")
        self.assertEqual(federal.previdenciaria_retida, "-")
        self.assertEqual(federal.sociais_retidas, "-")
        self.assertEqual(federal.pis_debito, "92.64")
        self.assertEqual(federal.cofins_debito, "20.11")
        self.assertEqual(federal.retention_description, "PIS/COFINS/CSLL Não Retidos")
        self.assertTrue(federal.show_legacy_piscofins_row)

    def test_extracts_ibs_cbs_total_and_complementary_fields(self):
        ibs_cbs = parse_ibs_cbs_taxation(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(ibs_cbs.cst_classification, "-")
        self.assertEqual(ibs_cbs.operation_indicator, "-")
        self.assertEqual(ibs_cbs.exclusions_reductions, "149.32")
        self.assertEqual(ibs_cbs.base_after_reductions, "-")
        self.assertEqual(ibs_cbs.cbs_total, "-")

        total = parse_total(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(total.service_amount, "1219.00")
        self.assertEqual(total.unconditional_discount, "-")
        self.assertEqual(total.conditional_discount, "-")
        self.assertEqual(total.total_retentions, "-")
        self.assertEqual(total.nfse_net_amount, "1219.00")
        self.assertEqual(total.ibs_cbs_total, "-")
        self.assertEqual(total.nfse_net_amount_with_ibs_cbs, "-")

        complementary = parse_complementary_info(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertIn("Inf. Cont.:", complementary.text)
        self.assertIn("Totais Aproximados dos Tributos cfe. Lei nº 12.741/2012", complementary.text)
        self.assertIn("Federais: R$ 163.96", complementary.text)
        self.assertIn("Estaduais: R$ 0.00", complementary.text)
        self.assertIn("Municipais: R$ 32.55", complementary.text)

    def test_extracts_receipt_fields(self):
        receipt = parse_receipt(Path(__file__).resolve().parents[1] / "xml.xml")
        self.assertEqual(receipt.acknowledgement_date, "")
        self.assertEqual(receipt.identification_signature, "")
        self.assertEqual(
            receipt.nfse_number_access_key,
            "645296 / 42082031202378779002233000000064529626050261847801",
        )

    def test_renders_provider_block_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("Prestador / Fornecedor", html)
        self.assertIn("02.378.779/0022-33", html)
        self.assertIn("Não Optante", html)
        self.assertIn("horizontal-line", html)

    def test_renders_customer_block_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("Tomador / Adquirente", html)
        self.assertIn("12.487.655/0003-87", html)
        self.assertIn("Itajaí / SC", html)
        self.assertIn("4208203 / 88.316-300", html)

    def test_renders_destination_block_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("DESTINATÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e", html)
        self.assertIn('class="reduced-message"', html)
        self.assertIn("height:0.32cm", html)

    def test_renders_intermediary_and_service_blocks_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("INTERMEDIÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e", html)
        self.assertIn("Serviço Prestado", html)
        self.assertIn("10.06.01", html)
        self.assertIn("1.0607.00.00", html)
        self.assertIn("10.06.01 Agenciamento marítimo.", html)

    def test_renders_municipal_and_federal_blocks_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("Tipo de Tributação do ISSQN", html)
        self.assertIn("Operação Tributável", html)
        self.assertIn("BC ISSQN", html)
        self.assertIn("36.57", html)
        self.assertIn("Tributação Federal (Exceto CBS)", html)
        self.assertIn("92.64", html)
        self.assertIn("PIS/COFINS/CSLL Não Retidos", html)

    def test_renders_ibs_cbs_total_and_complementary_blocks_html(self):
        html = render_danfse_html(self.document)
        self.assertIn("Tributação IBS / CBS", html)
        self.assertIn("CST / cClassTrib", html)
        self.assertIn("Exclusões e Reduções da Base de Cálculo", html)
        self.assertIn("149.32", html)
        self.assertIn("Valor Total da NFS-e", html)
        self.assertIn("Valor da Operação / Serviço", html)
        self.assertIn("Valor Líquido da NFS-e + IBS/CBS", html)
        self.assertIn("Informações Complementares", html)
        self.assertIn("Totais Aproximados dos Tributos", html)
        self.assertIn("DATA CIENTIFICAÇÃO:", html)
        self.assertIn("IDENTIFICAÇÃO E ASSINATURA", html)
        self.assertIn("Nº NFS-e / CHAVE NFS-e", html)
        self.assertIn("645296 / 42082031202378779002233000000064529626050261847801", html)
        self.assertNotIn("top:28.07cm", html)

    def test_renders_reduced_municipal_block_when_trib_mun_missing(self):
        xml_path = Path(__file__).resolve().parents[1] / "xml.xml"
        xml = xml_path.read_text(encoding="utf-8").replace(
            "<tribMun><tribISSQN>1</tribISSQN><tpRetISSQN>1</tpRetISSQN></tribMun>",
            "",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".xml", encoding="utf-8", delete=False) as tmp:
            tmp.write(xml)
            tmp_path = Path(tmp.name)
        try:
            html = render_danfse_html(parse_danfse(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)

        self.assertIn("TRIBUTAÇÃO MUNICIPAL (ISSQN) - OPERAÇÃO NÃO SUJEITA AO ISSQN", html)
        self.assertIn('class="reduced-message"', html)

    def test_validates_layout_and_data(self):
        self.assertEqual(validate_layout_constants(), [])
        self.assertEqual(validate_danfse_data(self.document), [])

    def test_renders_header_pdf_with_weasyprint(self):
        class FakeHTML:
            def __init__(self, string, base_url):
                self.string = string
                self.base_url = base_url

            def write_pdf(self, output):
                Path(output).write_bytes(b"%PDF-1.7\n")

        fake_weasyprint = types.SimpleNamespace(HTML=FakeHTML)
        original = sys.modules.get("weasyprint")
        sys.modules["weasyprint"] = fake_weasyprint
        output = Path(__file__).resolve().parents[1] / "test-header-output.pdf"
        try:
            result = render_header_pdf(self.data, output)
            self.assertEqual(result, output)
            self.assertTrue(output.read_bytes().startswith(b"%PDF"))
        finally:
            output.unlink(missing_ok=True)
            if original is None:
                del sys.modules["weasyprint"]
            else:
                sys.modules["weasyprint"] = original
