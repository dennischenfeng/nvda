"""Unit test for audio highlighting in speech (e.g. pitch changes, etc). """

from speech.audioHighlighting import splitOffSpecialCharacters, changePitchOnSpecialCharacters, changePitchOnSpecialCharactersOfString, SYMBOLS, changePitchOnStringMatch
from speech.commands import PitchCommand, EndUtteranceCommand

def test_changePitchOnSpecialCharacters():
    """Test changePitchOnSpecialCharacters"""
    specials = SYMBOLS
    seq = [PitchCommand(offset=20), "hello()"]
    result = changePitchOnSpecialCharacters(seq, specials, pitchOffset=100, pauses=False)

    assertPitchCommand(result[0], 20)
    assertPitchCommand(result[1], 0)
    assert result[2] == "hello"
    assertPitchCommand(result[3], 100)
    assert result[4] == "("
    assertPitchCommand(result[5], 100)
    assert result[6] == ")"
    

def test_changePitchOnSpecialCharactersOfString():
    """Test changePitchOnSpecialCharactersOfString"""
    specials = SYMBOLS
    pitchOffset = 90

    string1 = "hello()"
    seq = changePitchOnSpecialCharactersOfString(string1, specials, pitchOffset=pitchOffset, pauses=False)
    
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


def test_changePitchOnStringMatch():
    """Test changePitchOnStringMatch"""
    speechSequence = ["This is a heading test.", EndUtteranceCommand(), "heading", "Introduction"]

    # test with default kwargs
    result = changePitchOnStringMatch(speechSequence, ["heading"])
    r = iter(result)
    assertPitchCommand(next(r), 0)
    assert next(r) == "This is a heading test."
    assertPitchCommand(next(r), 0)
    assert isinstance(next(r), EndUtteranceCommand)
    assertPitchCommand(next(r), 100)
    assert next(r) == "heading"
    assertPitchCommand(next(r), 0)
    assert next(r) == "Introduction"

    # test with modified kwargs
    result = changePitchOnStringMatch(speechSequence, ["heading"], pitchOffset=40, changeNextItem=True)
    r = iter(result)
    assertPitchCommand(next(r), 0)
    assert next(r) == "This is a heading test."
    assertPitchCommand(next(r), 0)
    assert isinstance(next(r), EndUtteranceCommand)
    assertPitchCommand(next(r), 40)
    assert next(r) == "heading"
    assertPitchCommand(next(r), 40)
    assert next(r) == "Introduction"

def assertPitchCommand(obj, offset):
    assert isinstance(obj, PitchCommand)
    assert obj.offset == offset

    