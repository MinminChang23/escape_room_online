# game_logic.py


class EscapeRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.index = 0
        self.puzzle = "What has keys but can't open locks?"
        self.answer = "keyboard"
        self.solved = [False] * 100

    def add_player(self, ws,username):
        self.players.append((ws,username))

    def remove_player(self, ws,username):
        self.players.remove((ws,username))

    async def broadcast(self, message: str):
        for player in self.players:
            await player[0].send_text(message)

    async def check_answer(self, guess: str,index,solved: list):
        if guess.lower().strip() == self.answer:
            solved[self.room_id][index[self.room_id]] = True
            index[self.room_id] += 1
            await self.broadcast("✅ Super! Du hast das Rätsel bewältigt: " + str(index[self.room_id]))
        else:
            await self.broadcast(f"❌ Leider nicht! : {guess} ist falsch!")