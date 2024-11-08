import re

# List of (regular expression, replacement) pairs for abbreviations in english:
abbreviations_de = [
    (re.compile("\\b%s\\." % x[0], re.IGNORECASE), x[1])
    for x in [
        ("Mrs", "Misess"),
        ("Mr", "Mister"),
        ("Dr", "Doktor"),
        ("Hr", "Herr"),
        ("Fr", "Frau"),
        ("%", " Prozent"),
        ("z.B.", "zum Beispiel"),
        ("u.a.", "unter anderem"),
        ("uvm.", "und vieles mehr"),
        ("usw.", "und so weiter"),
        ("z.Zt.", "zur Zeit"),
        ("d.h.", "das heißt"),
        ("bzw.", "beziehungsweise"),
        ("ca.", "circa"),
        ("etc.", "et cetera"),
        ("evtl.", "eventuell"),
        ("ggf.", "gegebenenfalls"),
        ("ggfs.", "gegebenenfalls"),
        ("ggf.", "gegebenenfalls"),
        ("ggfs.", "gegebenenfalls"),
        ("i.d.R.", "in der Regel"),
        ("i.d.F.", "in der Fassung"),
        ("i.d.S.", "im Sinne"),
        ("i.d.Z.", "in der Zukunft"),
        ("i.d.V.", "im Voraus"),
        ("i.d.G.", "im Gegenteil"),
        ("i.d.B.", "im Besonderen"),
        ("i.d.A.", "im Allgemeinen"),
        ("i.d.H.", "im Hinblick"),
        ("i.d.T.", "im Tagesverlauf"),
        ("i.d.W.", "im Wesentlichen"),
        ("i.d.Ü.", "im Übrigen"),
        ("–", "-"),
        ("ü", "ü"),
    ]
]

def expand_abbreviations(text, lang="de"):
    if lang == "de":
        _abbreviations = abbreviations_de
    else:
        raise NotImplementedError()
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text