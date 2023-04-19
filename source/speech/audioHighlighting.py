"""Functions to add audio highlighting (e.g. pitch changes, etc) to speech sequences."""

from speech.types import SpeechSequence
from copy import deepcopy
from speech.commands import PitchCommand, EndUtteranceCommand
from typing import Dict, List, Any

SYMBOLS= [
	"(", ")", "[", "]", "{", "}", 
	".", ",", ":", 
	"-", "=", "+", "*", "/", "<", ">", 
	"!", "@", "#", "$", "%", "^", "&", 
]


def splitOffSpecialCharacters(text: str, specials: List[str]) -> Dict[str, Any]:
    """
    Splits string into a list of substrings, where each special character (from user-defined list) is a single-character string that's been split off. 
    Returns a dict that contains a list of the substrings, as well as a mask that indicates which substrings are specials.
    """
    substrings = []
    specialsMask = []
    start = 0
    stop = 0
    while stop < len(text):
        hasReachedSpecial = text[stop] in specials
        if hasReachedSpecial:
            if start != stop:
                substringWithoutSpecials= text[start:stop]
                substrings.append(substringWithoutSpecials)
                specialsMask.append(False)
            substrings.append(text[stop])
            specialsMask.append(True)

            stop += 1
            start = stop
        else:
            stop += 1
    
    if start != stop:
        substringWithoutSpecials= text[start:stop]
        substrings.append(substringWithoutSpecials)        
        specialsMask.append(False)
    
    return dict(substrings=substrings, specialsMask=specialsMask)


def changePitchOnSpecialCharacters(speechSequence: SpeechSequence, specials: List[str], pitchOffset: int = 100, pauses: bool = False) -> SpeechSequence:
    """
    Modifies a speech sequence by adding pitch changes for every special character. Also optionally adds pauses (EndUtteranceCommand) after every sequence.
    """
    newSpeechSequence = []
    for item in speechSequence:
        if not isinstance(item, str):
            newSpeechSequence.append(item)
        else:
            subsequence = changePitchOnSpecialCharactersOfString(item, specials, pitchOffset=pitchOffset, pauses=pauses)
            newSpeechSequence.extend(subsequence)
    return newSpeechSequence


def changePitchOnSpecialCharactersOfString(speechString: str, specials: List[str], pitchOffset: int = 100, pauses: bool = False) -> SpeechSequence:
    """
    Create a speech sequence that includes pitch changes (and optionally pauses) on occurence of special characters, of a fiven text string.
    """
    splitResult = splitOffSpecialCharacters(speechString, specials)
    speechSequence = []
    for s, isSpecial in zip(splitResult["substrings"], splitResult["specialsMask"]):
        offset= pitchOffset if isSpecial else 0
        subsequence = [PitchCommand(offset=offset), s]
        if pauses:
            subsequence.append(EndUtteranceCommand())
        speechSequence.extend(subsequence)
    return speechSequence



def changePitchOnStringMatch(speechSequence: SpeechSequence, pitchChangeStrings: Dict[int, List[str]], changeNextItem: bool = False) -> SpeechSequence:
    """
    Adds pitch change commands to all strings (in the given speech sequence) that match the given strings.
    """
    pitchOffsets = identifyPitchOffsets(speechSequence, pitchChangeStrings)
    if changeNextItem:
        pitchOffsets = _expandPitchChangesRightward(pitchOffsets)

    newSpeechSequence = []
    for offset, x in zip(pitchOffsets, speechSequence):
        newSpeechSequence.extend([PitchCommand(offset=offset), x])
    return newSpeechSequence


def identifyPitchOffsets(speechSequence: SpeechSequence, pitchChangeStrings: Dict[int, List[str]]) -> List[int]:
    """Generate the ordered list of pitch offsets (for each speech seuqnce item), given a dictionary that instructs which strings get which pitch offset. """
    pitchOffsets = []
    possibleOffsets = pitchChangeStrings.keys()
    for x in speechSequence:
        offset = 0
        for o in possibleOffsets:
            if x in pitchChangeStrings[o]:
                offset = o
                break
        pitchOffsets.append(offset)
    return pitchOffsets


def _expandPitchChangesRightward(pitchOffsets: List[int]) -> List[int]:
    """
    Generate a new pitch offsets list , where every nonzero item changes the item immediately to the right into a nonzero item too (with same offset value).
    """
    newPitchOffsets = deepcopy(pitchOffsets)
    for i, x in enumerate(pitchOffsets):
        if x != 0  and i < len(pitchOffsets) - 1:
            newPitchOffsets[i + 1] = pitchOffsets[i]
    return newPitchOffsets
