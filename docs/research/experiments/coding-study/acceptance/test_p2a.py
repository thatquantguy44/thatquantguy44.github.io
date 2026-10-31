"""Public P2A requirements over synthetic XML; no SDK implementation."""

import xml.etree.ElementTree as ET

import pytest

from quantsmith.test_engineering import junit


def rows(xml):
    return [(r.id, r.status, r.duration_s, r.message, r.file) for r in junit.parse_junit(xml)]


@pytest.mark.parametrize("declaration,prefix", [('xmlns="urn:study:junit"', ''),
                                                ('xmlns:j="urn:another-junit"', 'j:')])
def test_qualified_cases_and_status_children(declaration, prefix):
    p = prefix
    xml = f'''<{p}testsuite {declaration}>
      <{p}testcase classname="Suite" name="ok" time="1.25" file="test_a.py"/>
      <{p}testcase name="bad" time="n/a"><{p}failure>  assertion text  </{p}failure></{p}testcase>
      <{p}testcase name="crash" time="2"><{p}failure message="not chosen"/><{p}error message="  crashed  "/></{p}testcase>
      <{p}testcase name="skip"><{p}skipped message="  later  "/></{p}testcase>
    </{p}testsuite>'''
    assert rows(xml) == [('Suite::ok', 'passed', 1.25, '', 'test_a.py'),
                         ('bad', 'failed', 0.0, 'assertion text', ''),
                         ('crash', 'error', 2.0, 'crashed', ''),
                         ('skip', 'skipped', 0.0, 'later', '')]


def test_mixed_qualified_and_unqualified_cases_keep_document_order_and_text():
    xml = '''<testsuites xmlns:j="urn:junit">
      <j:testsuite><j:testcase name="first"><failure message="ns:unchanged"/></j:testcase></j:testsuite>
      <testsuite><testcase name="second" status="disabled"/><j:testcase name="third" status="fail"/></testsuite>
      <testcase name="fourth" result="suppressed"/>
    </testsuites>'''
    assert [(i, status, message) for i, status, _, message, _ in rows(xml)] == [
        ('first', 'failed', 'ns:unchanged'), ('second', 'skipped', ''),
        ('third', 'failed', ''), ('fourth', 'skipped', '')]


def test_qualified_failure_precedes_skipped_and_text_is_truncated():
    message = 'x' * 2100
    xml = f'<s:testsuite xmlns:s="urn:s"><s:testcase name="a"><s:skipped/><s:failure>{message}</s:failure></s:testcase></s:testsuite>'
    assert rows(xml) == [('a', 'failed', 0.0, 'x' * 2000, '')]


def test_empty_no_cases_malformed_and_size_limit_still_apply(monkeypatch):
    assert junit.parse_junit('  ') == []
    assert junit.parse_junit('<testsuite/>') == []
    with pytest.raises(ET.ParseError):
        junit.parse_junit('<testsuite>')
    monkeypatch.setattr(junit, 'MAX_BYTES', 10)
    with pytest.raises(ValueError):
        junit.parse_junit('<testsuite></testsuite>')


def test_existing_unqualified_statuses_preserved():
    xml = '<testsuite><testcase classname="C" name="p"/><testcase name="s" status="notrun"/><testcase name="f"><failure message="bad"/></testcase></testsuite>'
    assert rows(xml) == [('C::p', 'passed', 0.0, '', ''), ('s', 'skipped', 0.0, '', ''), ('f', 'failed', 0.0, 'bad', '')]
