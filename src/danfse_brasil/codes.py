"""Code descriptions used by the header.

Only values needed by the first implemented block are declared here. New codes
must be added with their normative source before they are rendered.
"""

from __future__ import annotations

from .exceptions import InvalidNFSeXmlError
from .models import MISSING_VALUE

TP_EMIT = {
    "1": "Prestador",
    "2": "Tomador",
    "3": "Intermediário",
}

CSTAT = {
    "100": "NFS-e Gerada",
    "102": "NFS-e de Decisão Judicial ou Administrativa",
    "103": "NFS-e Avulsa",
    "107": "NFS-e MEI",
}

FIN_NFSE = {
    "0": "NFS-e regular",
    "1": "NFS-e de crédito",
    "2": "NFS-e de débito",
}

TP_NFSE_DEBITO = {
    "01": "Transferência de créditos para Cooperativas",
    "02": "Anulação de Crédito por Saídas Imunes/Isentas",
    "03": "Débitos de notas fiscais não processadas na apuração",
    "04": "Multa e juros",
    "05": "Transferência de crédito na sucessão",
    "06": "Pagamento Antecipado",
}

TP_NFSE_CREDITO = {
    "01": "Multa e juros",
    "05": "Transferência de crédito na sucessão",
}

OP_SIMP_NAC = {
    "1": "Não Optante",
    "2": "Optante - Microempreendedor Individual (MEI)",
    "3": "Optante - Microempresa ou Empresa de Pequeno Porte (ME/EPP)",
    "4": "Optante Pendente",
}

REG_AP_TRIB_SN = {
    "1": "Regime de apuração dos tributos federais e municipal pelo SN",
    "2": "Regime de apuração dos tributos federais pelo SN e o ISSQN pela NFS-e conforme respectiva legislação municipal do tributo",
    "3": "Regime de apuração dos tributos federais e municipal pela NFS-e conforme respectivas legislações federal e municipal de cada tributo",
}

REG_AP_IBS_CBS_SN = {
    "1": "IBS e CBS apurados pelo SN",
    "2": "CBS apurada pelo SN e IBS apurado pelo regime regular",
    "3": "IBS e CBS apurados pelo regime regular",
}

C_ATV_SN = {
    "7": "Prestação de serviços, cessão de direitos, de uso ou de espaço com incidência do ISS, tributados exclusivamente pelo Anexo III",
    "8": "Prestação de serviços contábeis autorizados a pagar o ISS em valor fixo em guia do Município - Anexo III",
    "9": "Prestação de serviços - Sujeitos ao Fator R - Anexo III ou V",
    "10": "Prestação de serviços de transporte municipal rodoviário, metroviário, ferroviário e aquaviário de passageiros - Anexo III",
    "11": "Locação de bens móveis e operações com serviços, bens imateriais e direitos, inclusive com bens imóveis, sem incidência de ISS - Anexo III",
    "12": "Prestação de serviços da área da construção civil relacionados aos subitens 7.02 e 7.05 - Anexo III",
    "13": "Prestação de serviços da área da construção civil relacionados aos subitens 7.02 e 7.05 - Anexo IV",
    "14": "Prestação de serviços - Anexo IV",
    "90": "Operações não tributadas",
}

REG_ESP_TRIB = {
    "0": "Nenhum",
    "1": "Ato Cooperado (Cooperativa)",
    "2": "Estimativa",
    "3": "Microempresa Municipal",
    "4": "Notário ou Registrador",
    "5": "Profissional Autônomo",
    "6": "Sociedade de Profissionais",
    "9": "Outros",
}

TRIB_ISSQN = {
    "1": "Operação Tributável",
    "2": "Imunidade",
    "3": "Exportação de Serviço",
    "4": "Não Incidência",
}

TP_RET_ISSQN = {
    "1": "Não Retido",
    "2": "Retido pelo Tomador",
    "3": "Retido pelo Intermediário",
}

TP_IMUNIDADE_ISSQN = {
    "0": "Imunidade (tipo não informado na nota de origem)",
    "1": "Patrimônio, renda ou serviços, uns dos outros (CF88, Art 150, VI, a)",
    "2": "Entidades religiosas e templos de qualquer culto, inclusive suas organizações assistenciais e beneficentes (CF88, Art 150, VI, b)",
    "3": "Patrimônio, renda ou serviços dos partidos políticos, inclusive suas fundações, das entidades sindicais dos trabalhadores, das instituições de educação e de assistência social, sem fins lucrativos, atendidos os requisitos da lei (CF88, Art 150, VI, c)",
    "4": "Livros, jornais, periódicos e o papel destinado a sua impressão (CF88, Art 150, VI, d)",
    "5": "Fonogramas e videofonogramas musicais produzidos no Brasil contendo obras musicais ou literomusicais de autores brasileiros e/ou obras em geral interpretadas por artistas brasileiros",
}

TP_SUSP_ISSQN = {
    "1": "Exigibilidade Suspensa por Decisão Judicial",
    "2": "Exigibilidade Suspensa por Processo Administrativo",
}

TP_BM_ISSQN = {
    "1": "Isenção",
    "2": "Redução da BC em 'ppBM' %",
    "3": "Redução da BC em R$ 'vInfoBM'",
    "4": "Alíquota Diferenciada de 'aliqDifBM' %",
}

TP_RET_PIS_COFINS = {
    "0": "PIS/COFINS/CSLL Não Retidos",
    "1": "PIS/COFINS Retido",
    "2": "PIS/COFINS Não Retido",
    "3": "PIS/COFINS/CSLL Retidos",
    "4": "PIS/COFINS Retidos, CSLL Não Retido",
    "5": "PIS Retido, COFINS/CSLL Não Retido",
    "6": "COFINS Retido, PIS/CSLL Não Retido",
    "7": "PIS Não Retido, COFINS/CSLL Retidos",
    "8": "PIS/COFINS Não Retidos, CSLL Retido",
    "9": "COFINS Não Retido, PIS/CSLL Retidos",
}


def describe(mapping: dict[str, str], value: str | None) -> str:
    if value is None or value == "" or value == MISSING_VALUE:
        return MISSING_VALUE
    if value not in mapping:
        raise InvalidNFSeXmlError(f"Codigo sem descricao normativa mapeada: {value}")
    return mapping[value]
