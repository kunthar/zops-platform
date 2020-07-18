
from pyparsing import Word, alphanums, Forward, ZeroOrMore, Literal
import uuid


class SEXPParser(object):
    """
    Class for parsing the residents set of segments.

    A residents object is in the following structure:
        "residents": {
            "sets": {
                "a": {"key": "level", "relation": "=", "value": "10"}
                "b": {"key": "level", "relation": "=", "value": "10"}
                "c": {"key": "level", "relation": "=", "value": "10"}
            },
            "expression": "(a U b) - (b n c)"
        }

    SEXPParser object parses the given expression. It obtains the tokens of the expression by using
    the following language, and constructs an expression stack which includes the operands and their
    relations, an operand stack which only includes the operands and a raw stack which includes
    operands, operators and parantheses.

    operand := Word(alphanum)
    operator := n | U | -
    term := operand | (sexp)
    sexp := term [operator term]*

    Expression stack is used for obtaining the relation tree of the expression as in the examples
    below.

    Examples

    Ex: "(a U b) - (c n d)"

                            (a U b) - (c n d) // term operator term
                            /		|       \
                        (sexp)  operator   (sexp)
                        /                       \
        term operator term						term operator term
        /				\						/				\
    operand				operand 			operand				operand


    Ex: "(a U b) - (c n d)" -> [a, b, U, c, d, n, -]

        expression stack: [a, b, U, c, d, n, -]
        operands stack: [a, b, c, d]
        raw stack: [(, a, U, b, ), -, (, c, n, d, )]

                    -
                  /   \
                 U     n
                / \   / \
               a   b c   d


    Ex: "a n (b - c)" -> [a,b,c,-,n]

                    n
                  /   \
                 a     -
                      / \
                     b   c

    Ex: "(a U b) - c" -> [a,b,U,c,-]
                    -
                  /   \
                 U     c
                / \
               a   b

    """
    def __init__(self, sets, expression, redis_key_map, cache):
        """
        When a SEXPParser object initialized, the expression is parsed and checked once.

        For the evaluation of the expression a SEXPParser instance must be obtained.

        .. code-block:: python
            sexp = SEXPParser(residents["sets"], residents["expression"], redis_key_map, redis_instance)

            # sexp.expression_stack gives the parsed expression stack
            evaluated_set_redis_key = sexp.evaluate_stack()  # this is the final redis key
            # then, evaluate_stack method must be called to evaluate the stack.

        Args:
            sets (dict): dict of set definitions
            expression (str): expression defines the final set
            redis_key_map (dict): key map for set names and their redis keys
            cache (object): redis instance

        Examples:
            .. code-block:: python
            def evaluate_stack(stack):
                op = stack.pop()
                if op in "nU-":
                    op2 = self.evaluate_stack(stack)
                    op1 = self.evaluate_stack(stack)
                    return self.operators[op](self.set_redis_key_map[op1], self.set_redis_key_map[op2])
                else:
                    return op

            residents = {
                "sets": {
                    "a": {"key": "level", "relation": "=", "value": "10"},
                    "b": {"key": "level", "relation": "=", "value": "10"},
                    "c": {"key": "level", "relation": "=", "value": "10"},
                },
                "expression": "(a U b) - (b n c)"
            }
            cache = Redis()
            redis_key_map = {
                "a": "redis_key_a",
                "b": "redis_key_b",
                "c": "redis_key_c",
            }
            sexp = SEXPParser(residents["sets"], residents["expression"], redis_key_map, cache)
            final_results_redis_key = sexp.evaluate_stack(self.expression_stack[:])

        """
        self.sets = sets
        self.expression = expression
        self.set_redis_key_map = redis_key_map
        self.cache = cache

        self.expression_stack = []
        self.operand_stack = []
        self.raw_stack = []

        self.operators = {
            "n": self.intersection,
            "U": self.union,
            "-": self.diff
        }

        self.expression_instance = self.get_expression()
        self.parsed_expression = self.expression_instance.parseString(self.expression)
        if not self.check_expression():
            # todo decide what to do
            raise Exception()

    def push_first_expression_stack(self, strg, loc, toks):
        self.expression_stack.append(toks[0])

    def push_first_operand_stack(self, strg, loc, toks):
        if toks[0] not in ['n', 'U', '-']:
            self.operand_stack.append(toks[0])

    def push_first_raw_stack(self, strg, loc, toks):
        self.raw_stack.append(toks[0])

    def get_expression(self):
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        diff = Literal("-")
        intersection = Literal("n")
        union = Literal("U")

        operand = Word(alphanums)

        operator = diff | intersection | union

        sexp = Forward()
        term = operand.setParseAction(self.push_first_expression_stack) | lpar + sexp + rpar
        sexp << term + ZeroOrMore((operator + term).setParseAction(self.push_first_expression_stack))

        return sexp

    def get_operands(self):
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        diff = Literal("-").suppress()
        intersection = Literal("n").suppress()
        union = Literal("U").suppress()

        operand = Word(alphanums)

        operator = diff | intersection | union

        sexp = Forward()
        term = operand.setParseAction(self.push_first_operand_stack) | lpar + sexp + rpar
        sexp << term + ZeroOrMore((operator + term).setParseAction(self.push_first_operand_stack))

        sexp.parseString(self.expression)
        return self.operand_stack

    def get_raw_stack(self):
        lpar = Literal("(")
        rpar = Literal(")")

        diff = Literal("-")
        intersection = Literal("n")
        union = Literal("U")

        operand = Word(alphanums)

        operator = diff | intersection | union

        sexp = Forward()
        term = operand.setParseAction(self.push_first_raw_stack) | lpar.setParseAction(
            self.push_first_raw_stack) + sexp + rpar.setParseAction(self.push_first_raw_stack)
        sexp << term + ZeroOrMore((operator + term).setParseAction(self.push_first_raw_stack))

        sexp.parseString(self.expression)
        return self.raw_stack

    def check_expression(self):
        oprtr_count, oprnd_count = self.count_expression_stack()
        prnths_count = self.count_parantheses()
        check_list = [
            set(self.sets.keys()) == set(self.get_operands()),
            oprtr_count + 1 == oprnd_count,
            prnths_count + 1 == oprtr_count if oprtr_count > 0 else prnths_count == oprtr_count,
        ]
        return all(check_list)

    def count_expression_stack(self):
        operands_counter = 0
        operator_counter = 0
        for o in self.expression_stack:
            if o in ["-", "U", "n"]:
                operator_counter += 1
            else:
                operands_counter += 1
        return operator_counter, operands_counter

    def count_parantheses(self):
        lpar_count = 0
        rpar_count = 0
        fpar_count = 0
        self.get_raw_stack()
        for o in self.raw_stack:
            if o == '(' and lpar_count >= rpar_count:
                lpar_count += 1
            elif o == ')' and lpar_count > rpar_count:
                lpar_count -= 1
                fpar_count += 1
        return fpar_count if lpar_count == rpar_count == 0 else -1

    def evaluate_stack(self, stack):
        op = stack.pop()
        if op in "nU-":
            op2 = self.evaluate_stack(stack)
            op1 = self.evaluate_stack(stack)
            redis_key = uuid.uuid4().hex
            self.set_redis_key_map[redis_key] = redis_key
            return self.operators[op](redis_key, self.set_redis_key_map[op1],
                                      self.set_redis_key_map[op2])
        else:
            return op

    def intersection(self, key, key1, key2):
        self.cache.sinterstore(key, key1, key2)
        return key

    def union(self, key, key1, key2):
        self.cache.sunionstore(key, key1, key2)
        return key

    def diff(self, key, key1, key2):
        self.cache.sdiffstore(key, key1, key2)
        return key

