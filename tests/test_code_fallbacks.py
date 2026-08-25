from danfse_brasil.codes import CSTAT, describe
from danfse_brasil.models import MISSING_VALUE
from danfse_brasil.municipalities import describe_municipality_state


def test_unknown_normative_code_is_kept_instead_of_aborting_rendering() -> None:
    assert describe(CSTAT, "999") == "Código 999"


def test_missing_normative_code_keeps_existing_placeholder() -> None:
    assert describe(CSTAT, MISSING_VALUE) == MISSING_VALUE


def test_unknown_municipality_code_is_kept_instead_of_aborting_rendering() -> None:
    assert describe_municipality_state("9999999") == "Município 9999999"
