from faketime import time

from flask import request

from constants import CONFIG_PATH, CRISIS_JSON_BASE_PATH, RUNE_JSON_PATH, CRISIS_V2_JSON_BASE_PATH
from utils import read_json, write_json


def crisisGetCrisisInfo():

    data = request.data
    selected_crisis = read_json(CONFIG_PATH)["crisisConfig"]["selectedCrisis"]

    if selected_crisis:
        rune = read_json(f"{CRISIS_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf-8")
        current_time = round(time())
        next_day = round(time()) + 86400

        rune["ts"] = current_time
        rune["playerDataDelta"]["modified"]["crisis"]["lst"] = current_time
        rune["playerDataDelta"]["modified"]["crisis"]["nst"] = next_day
        rune["playerDataDelta"]["modified"]["crisis"]["training"]["nst"] = next_day

        for i in rune["playerDataDelta"]["modified"]["crisis"]["season"]:
            rune["playerDataDelta"]["modified"]["crisis"]["season"][i]["temporary"] = {
                "schedule": "rg1",
                "nst": next_day,
                "point": -1,
                "challenge": {
                    "taskList": {
                        "dailyTask_1": {
                            "fts": -1,
                            "rts": -1
                        }
                    },
                    "topPoint": -1,
                    "pointList": {
                        "0": -1,
                        "1": -1,
                        "2": -1,
                        "3": -1,
                        "4": -1,
                        "5": -1,
                        "6": -1,
                        "7": -1,
                        "8": -1
                    }
                }
            }
    else:
        rune = {
            "ts": round(time()),
            "data": {},
            "playerDataDelta": {}
        }

    return rune


def crisisBattleStart():

    data = request.data
    data = request.get_json()
    selected_crisis = read_json(CONFIG_PATH)["crisisConfig"]["selectedCrisis"]
    rune_data = read_json(f"{CRISIS_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf8")["data"]["stageRune"][data["stageId"]]

    total_risks = 0
    for each_rune in data["rune"]:
        total_risks += rune_data[each_rune]["points"]

    write_json({
        "chosenCrisis": selected_crisis,
        "chosenRisks": data["rune"],
        "totalRisks": total_risks
    }, RUNE_JSON_PATH)
    
    data = {
        'battleId': 'abcdefgh-1234-5678-a1b2c3d4e5f6',
        'playerDataDelta': {
            'modified': {},
            'deleted': {}
        },
        'result': 0,
        'sign': "abcde",
        'signStr': "abcdefg"
    }

    return data


def crisisBattleFinish():

    total_risks = read_json(RUNE_JSON_PATH)["totalRisks"]

    data = request.data
    data = {
        "result": 0,
        "score": total_risks,
        "updateInfo": {
            "point": {
                "before": -1,
                "after": total_risks
            }
        },
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }

    return data

def crisisV2_getInfo():
    selected_crisis = read_json(CONFIG_PATH)[
        "crisisV2Config"
    ]["selectedCrisis"]
    if selected_crisis:
        rune = read_json(
            f"{CRISIS_V2_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf-8"
        )
    else:
        rune = {
            "info": {},
            "ts": 1700000000,
            "playerDataDelta": {
                "modified": {},
                "deleted": {}
            }
        }
    return rune


def crisisV2_battleStart():
    request_data = request.get_json()
    battle_data = {
        "mapId": request_data["mapId"],
        "runeSlots": request_data["runeSlots"]
    }
    write_json(battle_data, RUNE_JSON_PATH)
    return {"result": 0, "battleId": "abcdefgh-1234-5678-a1b2c3d4e5f6", "playerDataDelta": {"modified": {}, "deleted": {}}}


def crisisV2_battleFinish():
    battle_data = read_json(RUNE_JSON_PATH)
    mapId = battle_data["mapId"]
    runeSlots = battle_data["runeSlots"]
    scoreCurrent = [0, 0, 0, 0, 0, 0]
    selected_crisis = read_json(CONFIG_PATH)[
        "crisisV2Config"
    ]["selectedCrisis"]
    rune = read_json(
        f"{CRISIS_V2_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf-8"
    )

    for slot in runeSlots:
        runeId = rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"][slot]["runeId"]
        runeData = rune["info"]["mapDetailDataMap"][mapId]["runeDataMap"][runeId]
        scoreCurrent[runeData["dimension"]] += runeData["score"]
    return {"result": 0, "mapId": mapId, "runeSlots": runeSlots, "isNewRecord": False, "scoreRecord": [0, 0, 0, 0, 0, 0], "scoreCurrent": scoreCurrent, "runeCount": [0, 0], "commentNew": [], "commentOld": [], "ts": 1700000000, "playerDataDelta": {"modified": {}, "deleted": {}}}
