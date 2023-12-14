import json
import os

import genanki
import requests
import tqdm

deckName = "word2anki words"
deckId = 1668036237

inputFile = "words.txt"
outputDir = "build"
outputApkg = "words.apkg"
cssFile = "anki.css"
queryCacheDir = os.path.join(outputDir, "cache")

# ?q={word}
apiURL = "https://www.bing.com/api/v7/dictionarywords/search?appid=371E7B2AF0F9B84EC491D731DF90A55719C7D209&mkt=zh-cn&pname=bingdict"


definitionTmpl = """
<script>play = (audio)=>{{(new Audio(audio)).play()}}</script>
<div class="pronunciation">
    <bold>美 [{pronunciation}]</bold>
    <button onclick="play('{pronunciationAudio}')">🔈</button>
</div>
{definitions}
<hr/>
{forms}
"""


# https://github.com/tisfeng/Easydict/blob/75abb86fc416e4098247022cc1fbd94727c65e5d/Easydict/Feature/Service/Model/EZQueryResult.m#L31
def partsOfSpeechMap(value):
    match value:
        case "形容词":
            return "adj."
        case "副词":
            return "adv."
        case "动词":
            return "v."
        case "系动词":
            return "linkv."
        case "助动词":
            return "auxv."
        case "情态动词":
            return "modalv."
        case "名词":
            return "n."
        case "代词":
            return "pron."
        case "介词":
            return "prep."
        case "连词":
            return "conj."
        case "感叹词":
            return "int."
        case "限定词":
            return "det."
        case "冠词":
            return "art."
        case "缩写":
            return "abbr."
        case "不定词":
            return "inf."
        case "分词":
            return "part."
        case "数词":
            return "num."
        case "网络":
            return "Web"
        case _:
            return value


def appendNote(deck, model):
    wordList = []
    with open(inputFile, "r") as f:
        for line in f:
            wordList.append(line.strip())
    print(f"loaded {len(wordList)} words")

    if not os.path.exists(queryCacheDir):
        os.makedirs(queryCacheDir)

    for word in tqdm.tqdm(wordList):
        if word == "":
            continue
        jsonData = {}
        definitionField = {}
        wordCache = os.path.join(queryCacheDir, f"{word}.json")
        try:
            if os.path.exists(wordCache):
                with open(wordCache, "r") as f:
                    jsonData = json.loads(f.read())
            if jsonData == {}:
                r = requests.get(
                    apiURL,
                    params={"q": word},
                )
                if r.status_code != 200:
                    raise Exception(f"api error: {r.reason} {r.content}")
                jsonData = r.json()
                with open(wordCache, "w") as f:
                    f.write(json.dumps(jsonData))
        except Exception as e:
            print(f"failed to query word [{word}]: {e}")
            continue

        try:
            if not isinstance(jsonData, dict):
                raise Exception("cannot parse json")
            data = jsonData.get("value", [])
            if len(data) < 1:
                raise Exception("bad data strucure")
            data = data[0]
            pronunciation = data.get("pronunciation", "")
            pronunciationAudio = data.get("pronunciationAudio", {}).get(
                "contentUrl", ""
            )
            definitions = ""
            forms = ""
            meaningGroups = data.get("meaningGroups", [])
            for item in meaningGroups:
                meanings = item["meanings"][0]
                partsOfSpeech = item["partsOfSpeech"][0]
                if (
                    "description" in partsOfSpeech
                    and partsOfSpeech["description"] == "快速释义"
                ):
                    t = partsOfSpeechMap(partsOfSpeech["name"])
                    elements = []
                    for i in meanings["richDefinitions"][0]["fragments"]:
                        elements.append(i["text"])
                    definitions += f"<p class='word-type'><span>{t}</span>: {'，'.join(elements)}</p>"
                if "name" in partsOfSpeech and partsOfSpeech["name"] == "变形":
                    for i in meanings["richDefinitions"][0]["fragments"]:
                        forms += f"{i['text']}; "
                    forms = f"<p>变形：{forms}</p>"
            definitionField = definitionTmpl.format(
                pronunciationAudio=pronunciationAudio,
                pronunciation=pronunciation,
                definitions=definitions,
                forms=forms,
            )
        except Exception as e:
            print(f"failed to parse [{word}]: {e}")

        if definitionField:
            deck.add_note(
                genanki.Note(
                    model=model,
                    fields=[word, definitionField],
                    guid=f"{deckName}-{word}",
                )
            )


if __name__ == "__main__":
    deck = genanki.Deck(deckId, deckName)
    model = genanki.Model(
        1668036237,
        "word2anki",
        fields=[{"name": "Word"}, {"name": "Definition"}],
        templates=[
            {
                "name": "word2anki",
                "qfmt": '<h1 class="word">{{Word}}</h1>',
                "afmt": '{{FrontSide}}<hr id="answer"><div class="definition-container"><div class="definition">{{Definition}}</div></div>',
            }
        ],
    )
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    with open(cssFile, "r") as f:
        model.css = f.read()

    appendNote(deck, model)
    genanki.Package(deck).write_to_file(os.path.join(outputDir, outputApkg))
