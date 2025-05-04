from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fastapi.websockets import WebSocket, WebSocketDisconnect

from game_logic import EscapeRoom

rooms={}
connections = []
app = FastAPI()
# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
# 加载 HTML 模板
templates = Jinja2Templates(directory="templates")

# 设定谜题（可以扩展）
puzzles =  [
    {
        "question": "1. Hoch oben auf dem Olymp, wo unsere Geschichte beginnt, versammelten sich die Götter. Sie sprachen über einen ganz besonderen Helden: Odysseus. Die (Göttin der Weisheit) setzte sich für ihn ein. "
                    "Währendessen leidet (der Sohn des Odysseus) unter den Freiern, die seine Mutter, die Königin von Ithaka, zur Hochzeit zwingen. Schließlich kommt Athene, als ein Priester getarnt, nach Ithaka und nimmt ihn auf eine Reise mit, um die Überreste von Odysseus zu finden. "
                    "Als erstes kommt er beim (König von Pylos) an. Dieser wusste leider nicht viel. Deswegen musste Thelemachos weiter segeln.",
        "selections":[ "a. Hera-Thelemachos-Menelaos" ,"b. Athene-Achyleus-Menelaos ", "c. Athene-Thelemachos-Nestor "], 
        "answer":   "c","hint":"a, b oder c"},
    {
        "question": "2. Als nächstes landete er in Sparta. Dort lebte der Held Menelaos. Zum Glück wusste dieser mehr: Odysseus lebte noch! Und er wusste auch paar Wörter die Odysseus möglicherweise beschreiben sollten. "
                    " Jedoch wusste er nicht mehr welches ihn beschreiben sollte (Finde raus welches!) improbus-fur-fortis ",
        "answer":   "fortis","hint":"Übersetze zuerst die Wörter!"},
    {
        "question": "3. Während all dies geschah sitzte Odysseus auf einer einsammen Insel fest wo eine Nymphe mit dem Namen Kalypso ihm Unsterblichkeit anbot. "
                    " Da die Götter beschlossen haben Odysseus ziehen zu lassen, machte er sich auf dem Weg. Jedoch kommt ihm Poseidon in die Quere und zerstört sein Schiff. "
                    " Er strandete völlig erschöpft. Am nächsten Morgen fanden ihn paar junge Damen, darunter war die Tochter des Königs. Wie heißt sie? (Nutze hier das Ausschlussprinzip) ","selections":[ "a. Hera" ,"b. Diana", "c. Nausikaa"],
        "answer":   "c", "hint":"a, b oder c"},
    {
        "question": "4. Sie gab ihm Kleidung und führte ihn in den Königspalast, wo ihn die Königin in Empfang nahm. Später gab es ein großes Fest wo Odysseus mit Kraft und Geschick alle beeindruckt. "
                    "Ulixes, ___(wettkämpfend), omnes superavit.(Setze das PPA ein von certare) ",
        "answer":   "certans","hint":"certare: wettkämpfen" },
    {
        "question": "5. Odysseus erzählte von den Abenteuern, die er erlebt hat. Doch mitten drin stockte er. Er wollte, dass die Zuhörer was zum Denken haben, also denkte er sich ein Entschlüsselungsrätsel aus: "
                    "Ich habe ein Ungeheuer überwältigt, dass so furchtlos und gesetzlos ist, dass ihr es vielleicht sogar kennt. Ihr müsst den Namen entziffern. Er lautet: Qpmzqifnvt (jeder Buchstabe -1 im Alphabet). Schließlich fragt Odysseus König Akinoos, ob er ihn wieder nach Ithaka bringen kann. "
                    "Dieser willigte ein und ließ am nächsten Morgen ihn nach Ithaka bringen. Odysseus schlief die ganze Fahrt lang und wachte nicht mal auf, als die Phaiaken ihn ablegten. Als er jedoch aufwachte wusste er nicht wo er war. ",
        "answer":   "polyphemus","hint":""},
    {
        "question": "6. Plötzlich erschien die Göttin Athene und sagte Odysseus wo er war. Außerdem berichtete sie ihm von den Gefahren in seinem Palast und schmiedete mit ihm einen Plan, wie er am Ende diese Gefahr überstehen konnte. Verkleidet als ein Bettler kommt Odysseus zu dem treuen Sauhirten Eumaios, den er seit Jahren nicht mehr gesehen hat. "
                    "Als er ankam erkannte Eumaios Odysseus nicht. Aber dieser behandelte Odysseus genau so wie sein bester Freund. Wörterteile: (ego, parare, cibum, hospiti) Satz: ___ debeo ___ ___ pro ___(Setzte die Wörter in den Satz ein damit er richtig ist!)(ACHTUNG! Du musst am Ende des Satzes ein Punkt setzen.) ",
        "answer":   "ego debeo cibum parare pro hospiti.","hint":"Punkt nicht vergessen!"},
    {
        "question": "7. Als Odysseus endlich den Palast seiner Heimat betrat, lachten die Freier ihn aus und behandelten ihn respektlos. Ulixes, ___ a procoribus deridebatur, dolorem celavit (Setze da richtige Relativpronomen ein). ",
        "answer":   "qui","hint":"qui, quae oder quod" },
    {
        "question": "8. Odysseus spricht, im verborgenem, mit Penelope und behauptet aus Kreta zu stammen. Er findet, dass dies noch nicht der richtige Zeitpunkt ist sein wahres Gesicht zu zeigen. Ulixes dixit se ex Creta venire. (Dieser Satz ist falsch! Setze veniere ins Infinitiv Perfekt um den Satz zu korrigieren.) ",
        "answer":   "venisse","hint":"Schreibe NUR den Inf. Perf. rein"},
    {
        "question": "9. Odysseus gibt sich schließlich einer seiner treuen Mägde zur Erkennung und befiehlt ihr die Freier im Palast einzusperren und erst nach einiger Zeit wieder in den Palast zurückzukehren. Am nächsten Tag stellt Penelope die Freier auf die Probe: Wer den schweren Bogen von Odysseus spannen und mit einem Pfeil durch zwölf Äxte schießen kann wird ihr neuer Gatte. "
                    "Kein einziger schafft es, bis Odysseus aus der Menge hervortritt. Odysseus, ___ (den Bogen prüfend), trat aus der Menge hervor (Setze den PPA von inspicere ein) ",
        "answer":   "inspiciens","hint":"" },
    {
        "question": "10. Odysseus schaft es mit Leichtigkeit den Bogen zu spannen und den Pfeil durch die zwölf Äxte zu schießen. Die Freier ignorierten seinen Sieg und wollten den Wettbewerb einfach wiederholen, als Odysseus sich zu erkennen gibt und einen Pfeil durch einen Freier schoss. "
                    "Es begann ein brutaler Kampf wobei Thelemachos, Eumaios und die Mägde ihm halfen. Bald erkannten die Freier, dass sie unmöglich siegen konnten und wollten fliehen, doch alle Türen wurden verriegelt. Die Freier, ___(verwundet), stürzten zu Boden (Setze verwundet ins PPP)(Setze hier die Endung -ti ein) ",
        "answer":   "vulnerati", "hint":"vulnerare: verwunden"}, 
    {
        "question": "11. Nach dem Kampf könnte man sagen, dass alles Gut ist. Doch da ist noch ein letztes Problem bevor es ein Happy End geben kann. Bringe die Satzteile in die richtige Reihenfolge und schreibe sie im folgendem Format: 54321 ",
        "selections":[ "1. Penelope zeigt sich kühl und reserviert gegen den Heimkehrer." ,"2. Odysseus wird von der Amme Eurykleia an seiner Narbe erkannt.", "3. Penelope stellt eine Falle, indem sie befiehlt, das Ehebatt weg zu tragen.","4. Odysseus protestiert - er hat es aus einen, mit dem Boden verwachsenem Baum geschnitzt.","5. Da wusste Penelope, dass es Odysseus ist und somit endet die Odyssee und er ist an den Ort zurückgekehrt, den er nie verlassen durfte."], 
        "answer": "21345","hint":"52413"},

    ]
# 获取数据库会话


@app.get("/start")
async def get():
    html = Path("templates/connect.html").read_text()
    return HTMLResponse(content=html)

connections = []
index = {}
solved={}
@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str,username: str):

    global connections,index,solved

    await websocket.accept()
    connections.append(websocket)



    if room_id not in rooms:
        rooms[room_id] = EscapeRoom(room_id)
        index[room_id]=0
        solved[room_id]=[False]*len(puzzles)
        print(f"Room {room_id} created")

    room = rooms[room_id]
    index[room_id] = index[room_id] % len(puzzles)
    print(f"index: {index}")
    puzzle = puzzles[index[room_id]]
    room.add_player(websocket,username)
    room.puzzle= puzzle["question"]
    room.answer= puzzle["answer"]

    await room.broadcast(f"🔔 {username} hat den Raum {room_id} betreten")

    #await websocket.send_text(f"🧩 Puzzle: {room.puzzle}")

    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("which puzzle"):
                await websocket.send_text(f"Index: {index[data.split(': ')[-1].strip()]}")
                continue

            await room.broadcast(
                f"🔔 {len(connections)} Spieler haben den Raum {room_id} betreten.")

            await websocket.send_text(data)

            #await room.check_answer(data, index)
            print(solved)
            print(index)
            if index[room_id]>=len(puzzles):
                await websocket.send_text("🎉 Alle Puzzle wurden gelöst! The index is: " + str(index[room_id]+1))
                continue
            if solved[room_id][index[room_id]]:
                await websocket.send_text("🎉 Puzzle wurde schon gelöst! The index is: " + str(index[room_id]+1))
            else:
                puzzle = puzzles[index[room_id]]
                room.puzzle = puzzle["question"]
                room.answer = puzzle["answer"]
                await room.check_answer(data,index,solved)
    except WebSocketDisconnect:
        room.remove_player(websocket,username)
        connections.remove(websocket)
        await room.broadcast(f"🚪 Spieler {username} hat den Raum {room_id} verlassen")


@app.get("/rooms/{room_id}/users")
def get_users_in_room(room_id: str):
    print("existing rooms: "+','.join(rooms.keys()))
    return {"users": [username for _, username in rooms[room_id].players]}
# 主页，展示第一个谜题
@app.get("/", response_class=HTMLResponse)
async def escape_room(request: Request,room_id: str,index: int = 0):
    if index >= len(puzzles):  # 逃脱成功
        return templates.TemplateResponse("success.html",
                                          {"request": request,
                                           "users":",".join(get_users_in_room(room_id)["users"])})
    else:
        return templates.TemplateResponse("index.html", {"request": request,
                                                     "puzzle": puzzles[index],
                                                     "puzzle_index": index,
                                                     "users":",".join(get_users_in_room(room_id)["users"]),
                                                     "room": room_id,
                                                     "message": ""})


# 处理答案提交
@app.post("/solve", response_class=HTMLResponse)
async def solve(
        request: Request=None,
        answer: str = Form(...),
        room: str = Form(...),
        puzzle_index: int = Form(...),
):
    print(f"answer: {answer}, puzzle_index: {puzzle_index}")
    correct_answer = puzzles[puzzle_index]["answer"]
    if correct_answer == answer.lower().strip():
        puzzle_index += 1
        if puzzle_index >= len(puzzles):  # 逃脱成功
            return templates.TemplateResponse("success.html",
                                              {"request": request,
                                               "users":",".join(get_users_in_room(room)["users"])})
        return templates.TemplateResponse("index.html", {"request": request,
                                                         "puzzle": puzzles[
                                                             puzzle_index],
                                                         "puzzle_index": puzzle_index,
                                                         "room": room,
                                                         "users":",".join(get_users_in_room(room)["users"]),
                                                         "message": "Correct！"})

    return templates.TemplateResponse("index.html", {"request": request,
                                                     "puzzle": puzzles[
                                                         puzzle_index],
                                                     "puzzle_index": puzzle_index,
                                                     "room": room,
                                                     "users": ",".join(get_users_in_room(room)["users"]),
                                                     "message": "Wrong answer, Try again！"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
