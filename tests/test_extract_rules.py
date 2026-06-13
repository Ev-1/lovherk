from cogs.rules import extract_rules, remove_duplicates

# A realistic rule set, mirroring the §grunnloven format.
RULE_TEXT = (
    "**Grunnreglene for /r/Norge**\n"
    "\n"
    "**Diverse**\n"
    "§ 1: Denne discordserveren er norskspråklig.\n"
    "§ 4: Hold deg til riktig kanal.\n"
    "§ 4a: Et tillegg til regel fire.\n"
    "§ 13: Ikke noe NSFW eller NSFL.\n"
    "§ 14: Moderering blir ikke diskutert offentlig.\n"
)


def test_single_rule():
    # Typing "§13" -> "§ 13: Ikke noe NSFW eller NSFL."
    assert extract_rules(RULE_TEXT, ["13"]) == "§ 13: Ikke noe NSFW eller NSFL.\n"


def test_number_prefix_does_not_collide():
    # "1" must match "§ 1:" only, never "§ 13:" or "§ 14:".
    assert extract_rules(RULE_TEXT, ["1"]) == (
        "§ 1: Denne discordserveren er norskspråklig.\n"
    )


def test_multiple_rules_in_request_order():
    assert extract_rules(RULE_TEXT, ["13", "1"]) == (
        "§ 13: Ikke noe NSFW eller NSFL.\n"
        "§ 1: Denne discordserveren er norskspråklig.\n"
    )


def test_letter_suffix_rule():
    assert extract_rules(RULE_TEXT, ["4a"]) == "§ 4a: Et tillegg til regel fire.\n"


def test_duplicates_collapsed():
    assert extract_rules(RULE_TEXT, ["13", "13"]) == (
        "§ 13: Ikke noe NSFW eller NSFL.\n"
    )


def test_unknown_rule_returns_empty():
    assert extract_rules(RULE_TEXT, ["99"]) == ""


def test_no_numbers_returns_empty():
    assert extract_rules(RULE_TEXT, []) == ""


def test_mixed_known_and_unknown():
    # Unknown numbers are silently skipped; known ones still come through.
    assert extract_rules(RULE_TEXT, ["99", "14"]) == (
        "§ 14: Moderering blir ikke diskutert offentlig.\n"
    )


def test_remove_duplicates_preserves_order():
    assert remove_duplicates(["3", "1", "3", "2", "1"]) == ["3", "1", "2"]
