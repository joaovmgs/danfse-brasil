# danfse-brasil: DANFSe PDF/HTML para NFS-e Nacional em Python

`danfse-brasil` e uma biblioteca Python para gerar **DANFSe em PDF ou HTML** a partir do **XML nacional da NFS-e**. O projeto implementa o Documento Auxiliar da Nota Fiscal de Servico Eletronica seguindo o layout da **Nota Tecnica 008/2026 SE/CGNFS-e** e inclui compatibilidades pontuais da **NT 009/2026** para campos RTC, IBS/CBS e CNPJ alfanumerico.

A biblioteca foi pensada para ERPs, sistemas fiscais, rotinas contabeis, portais de notas e backends Python que precisam converter XML da NFS-e Nacional em um PDF de DANFSe gerado localmente. O foco do projeto e entregar um renderizador previsivel, testavel e alinhado aos caminhos XML definidos pela documentacao tecnica.

## Quando usar

Use esta biblioteca quando a sua aplicacao ja possui o XML da NFS-e Nacional e precisa gerar o documento auxiliar em PDF ou HTML. Alguns exemplos de uso:

- gerar DANFSe em um ERP ou sistema fiscal;
- anexar PDF de NFS-e em um portal de notas;
- criar rotinas de arquivo XML/PDF para escritorios contabeis;
- validar campos esperados antes de imprimir o documento auxiliar;
- depurar o layout em HTML antes de gerar o PDF final.

O `danfse-brasil` separa leitura do XML, modelo de dados, validacao e renderizacao. Essa estrutura permite usar a biblioteca tanto pela CLI quanto diretamente no codigo Python, sem acoplar o DANFSe a uma aplicacao especifica.

O pacote nao substitui a validacao fiscal feita pelo emissor, prefeitura, Ambiente de Dados Nacional ou processos internos de cada empresa. Ele gera o documento auxiliar a partir dos dados existentes no XML recebido.

## Status normativo

A implementacao segue a documentacao oficial da NT 008:

https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/nt-008-se-cgnfse-danfse-20260505.pdf

Tambem existem compatibilidades pontuais com campos introduzidos ou ajustados pela NT 009:

https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/nt-009-se-cgnfse-v1-0-1.pdf

O PDF e os campos foram validados por implementacao local e testes automatizados da biblioteca, mas esta versao ainda nao foi homologada por um validador oficial externo.

## Recursos

- Gera DANFSe em PDF via WeasyPrint.
- Gera HTML para depuracao, preview ou integracao propria.
- Le XML nacional da NFS-e e monta os blocos do DANFSe.
- Gera QR Code com URL publica de consulta pela chave de acesso.
- Respeita regras de supressao/reducao de blocos previstas na NT 008.
- Mantem CNPJ alfanumerico sem formatacao indevida.
- Expoe validador com `error` e `warning` para campos ausentes, medidas e regras condicionais.
- Inclui CLI `danfse-brasil` para uso direto no terminal.

## Regra de preenchimento

O objetivo do projeto e reproduzir o DANFSe com os caminhos XML, descricoes, medidas, fontes e regras de supressao definidos na NT 008. A biblioteca nao inventa valores: quando uma tag exigida para um campo nao existe no XML, o campo e preenchido com `-`, conforme a nota 12 da tabela 2.4.5.

Isso significa que a biblioteca nao copia automaticamente dados entre grupos diferentes do XML. Exemplo: o nome do Prestador / Fornecedor e lido de `NFSe/infNFSe/DPS/infDPS/prest/xNome`. Se o XML possuir `NFSe/infNFSe/emit/xNome`, mas nao possuir `prest/xNome`, o DANFSe exibira `-` e o validador retornara um aviso.

## Instalacao

Requisitos principais:

- Python 3.10+
- `uv`
- WeasyPrint
- `qrcode[pil]`
- No Windows, runtime nativo do WeasyPrint via MSYS2
- Fontes Arial e Microsoft Sans Serif instaladas no sistema

### Ambiente local

Use Python 3.10 ou superior.

Instale o `uv`:

```powershell
pip install uv
```

No Windows, instale o MSYS2 e o runtime do WeasyPrint:

```powershell
pacman -S --noconfirm mingw-w64-x86_64-pango
```

O pacote carrega por padrao o diretorio:

```text
C:\msys64\mingw64\bin
```

Se o MSYS2 estiver em outro caminho, defina `WEASYPRINT_DLL_DIRECTORIES` apontando para o `mingw64\\bin`.

Instale as dependencias da biblioteca:

```powershell
cd "C:\caminho\para\danfse-brasil"
uv sync
```

Para instalar diretamente em outro projeto enquanto o pacote nao estiver publicado no PyPI:

```powershell
pip install "danfse-brasil @ git+https://github.com/joaovmgs/danfse-brasil.git"
```

## Uso rapido

Gerar PDF:

```powershell
uv run danfse-brasil xml.xml --output danfse.pdf
```

Gerar HTML:

```powershell
uv run danfse-brasil xml.xml --output danfse.html
```

Modo estrito de fontes:

```powershell
uv run danfse-brasil xml.xml --output danfse.pdf --strict-fonts
```

## Exemplo em Python

```python
from pathlib import Path

from danfse_brasil import parse_danfse, render_danfse_pdf, validate_danfse_data

data = parse_danfse("xml.xml")
issues = validate_danfse_data(data)

if issues:
    for issue in issues:
        print(issue.code, issue.message)
else:
    render_danfse_pdf(data, Path("danfse.pdf"))
```

## Exemplo de validacao

```python
from danfse_brasil import parse_danfse, validate_danfse_data

data = parse_danfse("xml.xml")
issues = validate_danfse_data(data)

for issue in issues:
    print(f"{issue.severity}: {issue.code}: {issue.message}")
```

## Validacao visual

O repositorio inclui um script para gerar um PDF de exemplo e, quando o PyMuPDF estiver disponivel, renderizar a primeira pagina em PNG para revisao visual:

```powershell
uv run --with pymupdf python scripts/visual_check.py xml.xml
```

Saida esperada:

- `tmp/pdfs/danfse-visual-check.pdf`
- `tmp/pdfs/danfse-visual-check-page1.png`

O script tambem valida que o PDF possui uma pagina em tamanho A4 aproximado. Avisos do validador nao bloqueiam a geracao; erros bloqueiam.

## Fontes exigidas

A NT 008 exige:

- Arial para titulos e labels
- Microsoft Sans Serif para conteudo dos demais campos

Se a fonte nao estiver instalada, a CLI avisa. Para checagem mais rigorosa, use `--strict-fonts`.

## Escopo implementado

- Cabecalho do DANFSe e identificacao da NFS-e
- Dados da NFS-e
- Prestador / Fornecedor
- Tomador / Adquirente
- Destinatario da Operacao
- Intermediario da Operacao
- Servico Prestado
- Tributacao Municipal (ISSQN)
- Tributacao Federal (Exceto CBS)
- Tributacao IBS / CBS
- Valor Total da NFS-e
- Informacoes Complementares
- Canhoto opcional

## Validacoes ja tratadas

- QR Code usando a URL publica da NFS-e com a chave de acesso
- Mensagem de homologacao quando `tpAmb == 2`
- Campos ausentes preenchidos com `-`
- Descricoes oficiais para codigos normativos mapeados
- Municipios resolvidos por tabela local gerada da API oficial do IBGE
- Supressao/reducao de Tomador, Destinatario, Intermediario e Tributacao Municipal quando aplicavel
- Linhas opcionais do ISSQN suprimidas quando todos os campos da linha nao existem no XML
- Linha PIS/COFINS da Tributacao Federal impressa somente para competencia ate o fim do ano-calendario de 2026, conforme nota 6
- Informacoes Complementares montadas na ordem definida pela NT
- Validador de medidas, tamanhos maximos de campos e regras condicionais implementadas
- Validador com avisos para campos minimos ausentes no caminho XML normativo

## Checklist visual NT 008

A revisao visual do DANFSe deve considerar os seguintes pontos da NT 008/2026:

- Papel A4 em orientacao retrato, uma unica pagina.
- Borda externa e blocos posicionados conforme medidas em centimetros da tabela 2.4.5.
- Margem interna preservada entre textos, linhas, sombreamentos e borda externa.
- Logomarca oficial da NFS-e no cabecalho, sem fundo preto e sem invadir a margem.
- Titulo `DANFSe v2.0` e `Documento Auxiliar da NFS-e` centralizados.
- QR Code com a URL publica de consulta pela chave de acesso.
- Mensagem `NFS-e SEM VALIDADE JURIDICA` apenas quando `tpAmb == 2`.
- Labels em Arial e conteudo em Microsoft Sans Serif, respeitando os tamanhos minimos.
- Supressoes/reducoes dos blocos permitidos: Tomador, Destinatario, Intermediario, Tributacao Municipal e Canhoto.
- Campos sem tag normativa impressos como `-`, sem fallback automatico entre grupos XML.

Limitacoes conhecidas:

- A biblioteca ainda nao possui homologacao em validador oficial externo.
- A validacao automatica confere constantes, tamanho A4, renderizacao e regras de dados, mas a comparacao fina com o Anexo I continua sendo uma revisao visual humana.
- A disponibilidade real de Arial e Microsoft Sans Serif depende do sistema operacional e do runtime do WeasyPrint.

## Compatibilidade com NT 009

- CNPJ alfanumerico e preservado sem formatacao quando nao for composto apenas por 14 digitos.
- `finNFSe` tambem e lido no caminho `NFSe/infNFSe/DPS/infDPS/finNFSe`.
- `tpNFSeCredito` e `tpNFSeDebito` sao lidos e descritos quando informados.
- `opSimpNac = 4` e descrito como `Optante Pendente`.
- `regApIBSCBSSN`, `cAtvSN`, `vReceitaBrutaSN` e `gTribSN` sao extraidos quando existem no XML.
- `gIBSCBSAjuste/vIBS` e `gIBSCBSAjuste/vCBS` sao preservados no modelo de dados.
- `indFinal` e lido como indicador de uso ou consumo pessoal.
- `imovel`, `bensMoveis` e `gPgtoVinc/pgto` sao identificados em campos de resumo/contagem no modelo de dados.
- O grupo `vAjusteBC` e considerado nos campos de deducoes/reducoes quando presente.
- Quando os totalizadores antigos de IBS/CBS nao existem, os valores de `gTribSN` podem compor os totais exibidos.

Essas compatibilidades nao alteram o layout visual do DANFSe definido na NT 008 e nao autorizam fallback automatico entre `emit` e `prest`. Campos da NT 009 que nao possuem posicao propria no DANFSe NT 008 ficam disponiveis no modelo para validacao, auditoria ou uso por aplicacoes consumidoras.

### Saida do validador

`validate_danfse_data` retorna objetos `ValidationIssue` com:

- `code`: codigo estavel da validacao.
- `message`: descricao do problema e, quando aplicavel, caminho XML esperado.
- `severity`: `error` ou `warning`.

A CLI bloqueia a geracao somente quando existe `severity == "error"`. Avisos sao impressos como diagnostico e o DANFSe continua sendo gerado.

## Desenvolvimento

Rodar testes:

```powershell
uv run python -m unittest discover -s tests -v
```

Checar compilacao:

```powershell
uv run python -m compileall -q src tests
```

## Observacoes

- Nao use fallback entre grupos diferentes do XML para preencher informacoes.
- Dados de exemplo, caches e artefatos gerados devem ficar fora do controle de versao.

## Licenca

Este projeto e publicado com uma licenca de uso propria, incluida em [LICENSE](LICENSE).

Uso comercial exige mencao visivel de que o produto, servico ou distribuicao utiliza `danfse-brasil`.

## Configuracao do repositorio

About sugerido para o GitHub:

```text
Biblioteca Python para gerar DANFSe PDF/HTML a partir do XML nacional da NFS-e, seguindo a NT 008/2026 e compatibilidades NT 009/2026.
```

Website sugerido:

```text
https://github.com/joaovmgs/danfse-brasil#readme
```

Topicos sugeridos:

```text
danfse, nfse, nfs-e, nfse-nacional, nota-fiscal, nota-fiscal-servico, python, pdf, xml, weasyprint, rtc, ibs, cbs, brasil
```
