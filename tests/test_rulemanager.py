import pytest

from cogs.utils.rulemanager import RuleManager

GUILD = 123456789


@pytest.fixture
def rules(tmp_path):
    # Trailing slash: RuleManager builds the file path as path + "<id>.json".
    return RuleManager(GUILD, str(tmp_path) + "/")


def test_new_manager_has_default_settings(rules):
    assert rules.get_settings("auto_update") == []
    assert rules.get_settings("react_rules") == []
    assert rules.get_settings("default_rule") is None


def test_add_and_get_rule(rules):
    assert rules.add_rule("Grunnloven", "the rules") is True
    # Names are stored lower-cased and looked up case-insensitively.
    assert rules.get_rule_text("grunnloven") == "the rules"
    assert rules.get_rule_text("GRUNNLOVEN") == "the rules"


def test_add_duplicate_rule_rejected(rules):
    rules.add_rule("lov", "a")
    assert rules.add_rule("lov", "b") is False
    assert rules.get_rule_text("lov") == "a"


def test_add_rule_with_no_text_defaults_to_empty(rules):
    rules.add_rule("lov", None)
    assert rules.get_rule_text("lov") == ""


def test_edit_rule(rules):
    rules.add_rule("lov", "old")
    assert rules.edit_rule("lov", "new") is True
    assert rules.get_rule_text("lov") == "new"


def test_edit_missing_rule_returns_false(rules):
    assert rules.edit_rule("missing", "x") is False


def test_alternate_text_is_separate_from_main(rules):
    rules.add_rule("lov", "norwegian")
    rules.edit_rule("lov", "english", alternate=True)
    assert rules.get_rule_text("lov") == "norwegian"
    assert rules.get_rule_text("lov", alternate=True) == "english"


def test_remove_rule(rules):
    rules.add_rule("lov", "x")
    assert rules.remove_rule("lov") is True
    assert rules.get_rule_text("lov") is None
    assert rules.remove_rule("lov") is False


def test_remove_rule_clears_default_and_links(rules):
    rules.add_rule("lov", "x")
    rules.change_setting("default_rule", "lov")
    rules.add_link_setting("auto_update", "lov", "link1")
    rules.remove_rule("lov")
    assert rules.get_settings("default_rule") is None
    assert rules.get_settings("auto_update") == []


def test_remove_alternate_only_clears_alternate(rules):
    rules.add_rule("lov", "main")
    rules.edit_rule("lov", "alt", alternate=True)
    assert rules.remove_rule("lov", alternate=True) is True
    assert rules.get_rule_text("lov") == "main"
    assert rules.get_rule_text("lov", alternate=True) is None


def test_add_link_setting(rules):
    rules.add_rule("lov", "x")
    assert rules.add_link_setting("auto_update", "lov", "link1") is True
    assert rules.get_settings("auto_update") == [{"name": "lov", "link": "link1"}]


def test_add_link_setting_duplicate_link_returns_minus_one(rules):
    rules.add_rule("lov", "x")
    rules.add_link_setting("auto_update", "lov", "link1")
    assert rules.add_link_setting("auto_update", "lov", "link1") == -1


def test_add_link_setting_for_missing_rule_returns_false(rules):
    assert rules.add_link_setting("auto_update", "nope", "link1") is False


def test_remove_link_setting(rules):
    rules.add_rule("lov", "x")
    rules.add_link_setting("auto_update", "lov", "link1")
    assert rules.remove_link_setting("auto_update", "link", "link1") is True
    assert rules.get_settings("auto_update") == []
    assert rules.remove_link_setting("auto_update", "link", "link1") is False


def test_rules_formatted_puts_default_first(rules):
    rules.add_rule("alpha", "a")
    rules.add_rule("beta", "b")
    rules.change_setting("default_rule", "beta")
    formatted = rules.get_rules_formatted()
    assert formatted.startswith("•Beta")
    assert "•Alpha" in formatted


def test_persistence_across_instances(rules, tmp_path):
    rules.add_rule("lov", "persisted")
    reloaded = RuleManager(GUILD, str(tmp_path) + "/")
    assert reloaded.get_rule_text("lov") == "persisted"
