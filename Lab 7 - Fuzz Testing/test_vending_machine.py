
from hypothesis import given, strategies as st
from vending_machine import parse_coins, slot_position, change_due


# Test 1: parse_coins
@given(st.text() | st.none())
def test_parse_coins_no_crash(s):
    parse_coins(s)


# Test 2: slot_position
@given(st.text() | st.none())
def test_slot_position_no_crash(s):
    slot_position(s)


# Test 3: change_due
@given(st.text() | st.none())
def test_change_due_no_crash(s):
    change_due(s)
