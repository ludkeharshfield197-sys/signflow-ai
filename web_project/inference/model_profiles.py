from pathlib import Path

CSL_37_LABELS_ZH = {
    "time": "\u65f6\u95f4",
    "you/your/this": "\u4f60/\u4f60\u7684/\u8fd9\u4e2a",
    "morning": "\u65e9\u4e0a",
    "9": "\u4e5d",
    "0": "\u96f6",
    "happy": "\u5f00\u5fc3",
    "new": "\u65b0",
    "wish": "\u795d\u613f",
    "please": "\u8bf7",
    "road": "\u8def",
    "birthday": "\u751f\u65e5",
    "flat": "\u5e73",
    "safe": "\u5b89\u5168",
    "friend": "\u670b\u53cb",
    "8": "\u516b",
    "know": "\u77e5\u9053",
    "business card": "\u540d\u7247",
    "marry/wife": "\u7ed3\u5a5a/\u59bb\u5b50",
    "tea": "\u8336",
    "have": "\u6709",
    "flavor": "\u5473\u9053",
    "today": "\u4eca\u5929",
    "door": "\u95e8",
    "stop": "\u505c\u6b62",
    "thank you": "\u8c22\u8c22",
    "slow": "\u6162",
    "walk": "\u8d70\u8def",
    "late/night": "\u665a/\u591c\u665a",
    "I/me": "\u6211",
    "love": "\u7231",
    "good": "\u597d",
    "person": "\u4eba",
    "what": "\u4ec0\u4e48",
    "name": "\u540d\u5b57",
    "introduce": "\u4ecb\u7ecd",
    "A": "A",
    "Z": "Z",
}


MODEL_PROFILES = {
    "asl-v8.pt": {
        "languageCode": "asl",
        "language": "\u7f8e\u56fd\u624b\u8bed\uff08ASL\uff09",
        "classCount": 80,
        "labelMap": {},
    },
    "csl.pt": {
        "languageCode": "csl",
        "language": "\u4e2d\u56fd\u624b\u8bed\uff08CSL\uff09",
        "classCount": 37,
        "labelMap": CSL_37_LABELS_ZH,
    },
}


def get_model_profile(file_path):
    """Return trusted metadata for a bundled model weight, matched by safe basename."""
    filename = Path(str(file_path or "")).name.lower()
    return MODEL_PROFILES.get(filename)
