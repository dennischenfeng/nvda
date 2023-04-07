"""Unit test for audio highlighting in speech (e.g. pitch changes, etc). """

from speech.audioHighlighting import splitOffSpecialCharacters, changePitchOnSpecialCharacters, changePitchOnSpecialCharactersOfString, SYMBOLS
from speech.commands import PitchCommand, EndUtteranceCommand

def test_changePitchOnSpecialCharactersOfString():
    """Test changePitchOnSpecialCharactersOfString"""
    specials = SYMBOLS
    pitchOffset = 90

    string1 = "hello()"
    seq = changePitchOnSpecialCharactersOfString(string1, specials, pitchOffset=pitchOffset, pauses=False)
    
    def assertPitchCommand(obj, offset):
        assert isinstance(obj, PitchCommand)
        assert obj.offset == offset

    assertPitchCommand(seq[0], 0)
    assert seq[1] == "hello"
    assertPitchCommand(seq[2], pitchOffset)
    assert seq[3] == "("
    assertPitchCommand(seq[4], pitchOffset)
    assert seq[5] == ")"

    string2 = "x = hello()"
    seq = changePitchOnSpecialCharactersOfString(string2, specials, pitchOffset=pitchOffset, pauses=True)
    assertPitchCommand(seq[0], 0)
    assert seq[1] == "x "
    assert isinstance(seq[2], EndUtteranceCommand)
    assertPitchCommand(seq[3], pitchOffset)
    assert seq[4] == "="
    assert isinstance(seq[5], EndUtteranceCommand)
    assertPitchCommand(seq[6], 0)
    assert seq[7] == " hello"
    assert isinstance(seq[8], EndUtteranceCommand)
    assertPitchCommand(seq[9], pitchOffset)
    assert seq[10] == "("
    assert isinstance(seq[11], EndUtteranceCommand)
    assertPitchCommand(seq[12], pitchOffset)
    assert seq[13] == ")"
    assert isinstance(seq[14], EndUtteranceCommand)
    
    
def test_splitOffSpecialCharacters():
    specials = SYMBOLS

    text1 = "hello()"
    expectedSubstrings1= ["hello", "(", ")"]
    expectedSpecialsMask1 = [False, True, True]
    actualResult1 = splitOffSpecialCharacters(text1, specials)
    assert actualResult1["substrings"] == expectedSubstrings1
    assert actualResult1["specialsMask"] == expectedSpecialsMask1

    text2 = "def hello(x: int, y: int) -> str:"
    expectedSubstrings2= ["def hello", "(", "x", ":", " int", ",", " y", ":", " int", ")", " ", "-", ">", " str", ":"]
    expectedSpecialsMask2 = [False, True, False, True, False, True, False, True, False, True, False, True, True, False, True]
    actualResult2 = splitOffSpecialCharacters(text2, specials)
    assert actualResult2["substrings"] == expectedSubstrings2
    assert actualResult2["specialsMask"] == expectedSpecialsMask2

