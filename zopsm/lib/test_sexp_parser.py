import pytest
from zopsm.lib.sexp_parser import SEXPParser
from pyparsing import ParseException
sets = {
        "a": {},
        "b": {},
        "c": {},
        "d": {}
    }


def clear_stacks(ins):
    ins.expression_stack = []
    ins.operand_stack = []
    ins.raw_stack = []


def test_valid_sexp_parser():
    sexp = SEXPParser(sets, "(a - b) - (c - d)", {})

    sexp.sets = {"a": {}}  # sets: {a}
    clear_stacks(sexp)

    sexp.expression = "a"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets["b"] = {}  # sets: {a, b}

    sexp.expression = "a n b"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'n']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U b"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'U']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - b"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', '-']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets["c"] = {}  # sets: {a, b, c}

    sexp.expression = "(a U b) - c"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'U', 'c', '-']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a n b) n c"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'n', 'c', 'n']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - (b - c)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'c', '-', '-']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a n (b U c)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'c', 'U', 'n']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets["d"] = {}  # sets: {a, b, c, d}

    sexp.expression = "(a n b) - (c U d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'n', 'c', 'd', 'U', '-']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a U b) n (c - d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'U', 'c', 'd', '-', 'n']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a - b) U (c n d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', '-', 'c', 'd', 'n', 'U']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a - b) - (c - d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', '-', 'c', 'd', '-', '-']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a n b) n (c n d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'n', 'c', 'd', 'n', 'n']
    assert sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "(a U b) U (c U d)"
    sexp.get_expression().parseString(sexp.expression)
    assert sexp.expression_stack == ['a', 'b', 'U', 'c', 'd', 'U', 'U']
    assert sexp.check_expression()
    clear_stacks(sexp)


def test_invalid_sexp_parser():
    sexp = SEXPParser(sets, "(a - b) - (c - d)", {})

    sexp.sets = {"-": {}}
    clear_stacks(sexp)

    sexp.expression = "-"
    with pytest.raises(ParseException):
        sexp.get_expression().parseString(sexp.expression)
        assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"U": {}}

    sexp.expression = "U"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"n": {}}

    sexp.expression = "n"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"a": {}, "n": {}}

    sexp.expression = "a n n"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - n"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U n"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"a": {}, "U": {}}

    sexp.expression = "a n U"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - U"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U U"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"a": {}, "-": {}}

    sexp.expression = "a n -"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - -"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U -"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.sets = {"a": {}, "b": {}, "c": {}}

    sexp.expression = "a n b n c"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a - b - c"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U b U c"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)

    sexp.expression = "a U (b U c"
    sexp.get_expression().parseString(sexp.expression)
    assert not sexp.check_expression()
    clear_stacks(sexp)










