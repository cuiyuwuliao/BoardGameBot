import uuid
import random

class Player:
    ALL_PLAYERS = []
    #get player by id, if id out of range, loop around
    @staticmethod
    def get_player_by_id(player_id:int):
        if player_id > len(Player.ALL_PLAYERS):
            player_id = 0
        elif player_id < 0:
            player_id = len(Player.ALL_PLAYERS) - 1
        for player in Player.ALL_PLAYERS:
            if player.id == player_id:
                return player
        return None
    
    def __init__(self, name:str):
        self.name:str = name
        self.id:int = Player.ALL_PLAYERS.__len__()
        self.score:int = 0
        self.score_temp:int = 0 #only added to score when a round is over and the player is alive
        self.health:int = 6
        self.deck = []
        Player.ALL_PLAYERS.append(self)

    def change_health(self, amount:int):
        self.health += amount
        if self.health < 0:
            self.health = 0
        if self.health > 6:
            self.health = 6
        print(f"{self.name}'s health changed by {amount}. Current health: {self.health}")
        return self.health
    
    def reset(self):
        # self.score = self.backup["score"]
        self.health = 0
        self.deck = []
        self.score_temp = 0
        print(f"{self.name} has been reset to initial state.")

    def add_score(self, amount:int):
        self.score += amount
        print(f"{self.name}'s score increased by {amount}. Current score: {self.score}")



class Card:
    CARD_WIKI = {
        1: {"name": "古代巨龙", "amount": 1, "effect": "对所有玩家造成roll(1~6)点伤害, 施放失败时对自己造成伤害"},
        2: {"name": "黑暗幽灵", "amount": 2, "effect": "对所有玩家造成1点伤害, 自己获得1点生命"},
        3: {"name": "甜蜜的梦", "amount": 3, "effect": "使自己恢复roll(1~6)点生命"},
        4: {"name": "猫头鹰", "amount": 4, "effect": "从卡池查看并移除一张卡, 本轮结算时如果存活则额外获得1分"},
        5: {"name": "闪电风暴", "amount": 5, "effect": "对前后玩家各造成1点伤害"},
        6: {"name": "冰球", "amount": 6, "effect": "对前一个玩家造成1点伤害"},
        7: {"name": "火球", "amount": 6, "effect": "对后一个玩家造成1点伤害"},
        8: {"name": "魔法药水", "amount": 8, "effect": "使自己恢复1点生命"},
    } 
    CARD_MENU = "1. 古代巨龙\n2. 黑暗幽灵\n3. 甜蜜的梦\n4. 猫头鹰\n5. 闪电风暴\n6. 冰球\n7. 火球\n8. 魔法药水"

    ALL_CARDS = []  

    def generate_standard_deck():
        for card_type, info in Card.CARD_WIKI.items():
            for _ in range(info["amount"]):
                Card.ALL_CARDS.append(Card(card_type))
                random.shuffle(Card.ALL_CARDS)

    def __init__(self, type:int):
        self.type = type
        self.name = Card.CARD_WIKI[type]["name"]
        self.effect = Card.CARD_WIKI[type]["effect"]
        self.amount = Card.CARD_WIKI[type]["amount"]
        self.holder = "pool_unused"
        self.id = uuid.uuid4()
        Card.ALL_CARDS.append(self)



    def reset_deck():
        for card_type in Card.CARD_WIKI:
            yield Card(card_type)

    def change_holder(self, new_holder:str):
        self.holder = new_holder


    def __str__(self):
        return f"Card(Name: {self.name}, Effect: {self.effect})"
    

class Game:
    MAX_CARDS_IN_DECK = 5
    def __init__ (self):
        self.round_small = 1
        self.round_big = 1
        self.history = []
        Card.generate_standard_deck()
        Player("Alice")
        Player("Bob")
        Player("Charlie")
        for player in Player.ALL_PLAYERS:
            for _ in range(Game.MAX_CARDS_IN_DECK):
                self.draw_card(player)

    def use_card(self, player:Player, card_type:int):
        for card in player.deck:
            if card.type == card_type:
                card.change_holder("pool_used")
                player.deck.remove(card)
                print(f"{player.name} used card type {card_type}.")
                return card
        return None
    
    def draw_card(self, player:Player):
        random.shuffle(Card.ALL_CARDS)
        for card in Card.ALL_CARDS:
            if card.holder == "pool_unused":
                card.change_holder(player.id)
                player.deck.append(card)
                return card
        print("No more cards available to draw.")
        return None
    
    def roll_dice(self):
        return random.randint(1, 6)
    
    def trigger_card_effect(self, player:Player, card:Card):
        message = ""
        private_messages = []
        if card.type == 1:
            damage = self.roll_dice()
            message += f"{p.name} roll出了{damage}!\n"
            for p in Player.ALL_PLAYERS:
                if p.id != player.id:
                    p.change_health(-damage)
                    message += f"{p.name} 失去 {damage} 点生命\n"
        elif card.type == 2:
            message += f"{player.name} 获得 1 点生命\n"
            for p in Player.ALL_PLAYERS:
                if p.id != player.id:
                    p.change_health(-1)
                    message += f"{p.name} 失去 1 点生命\n"
        elif card.type == 3:
            heal = self.roll_dice()
            message += f"{p.name} roll出了{heal}!\n"
            player.change_health(heal)
            message += f"{player.name} 获得 {heal} 点生命\n"
        elif card.type == 4:
            message += f"{player.name} 尝试揭示一张牌\n"
            available_cards = [c for c in Card.ALL_CARDS if c.holder == "pool_unused"]
            if available_cards:
                removed_card = random.choice(available_cards)
                removed_card.change_holder("pool_used")
                private_messages.append({"name":player.name, "content":f"你秘密揭示了一张牌: {removed_card.type}-{removed_card.name}\n该牌已从牌池移除"})
                message += f"揭示成功! {player.name}分数+1, 一张牌已从池子移除\n"
            else:
                message += f"...但是已经没有牌了, 揭示失败\n"
        elif card.type == 5:
            front_player = Player.get_player_by_id((player.id - 1))
            back_player = Player.get_player_by_id((player.id + 1))
            front_player.change_health(-1)
            message += f"{front_player.name} 失去 1 点生命\n"
            if back_player.id != front_player.id:
                back_player.change_health(-1)
                message += f"{back_player.name} 失去 1 点生命\n"
        elif card.type == 6:
            front_player = Player.get_player_by_id((player.id - 1))
            front_player.change_health(-1)
            message += f"{front_player.name} 失去 1 点生命\n"
        elif card.type == 7:
            back_player = Player.get_player_by_id((player.id + 1))
            back_player.change_health(-1)
            message += f"{back_player.name} 失去 1 点生命\n"
        elif card.type == 8:
            player.change_health(1)
            message += f"{player.name} 获得 1 点生命\n"
        return message, private_messages

    def get_winners(game_state):
        highest_score = -1
        winner = []
        for player in Player.ALL_PLAYERS:
            if player.score > highest_score:
                highest_score = player.score
                winner = [player]
            elif player.score == highest_score: 
                winner.append(player)
        return winner
    
    def get_dead_players(self):
        dead_players = []
        for player in Player.ALL_PLAYERS:
            if player.health <= 0:
                dead_players.append(player)
        return dead_players
    
    def get_game_state(self):
        state = {}
        players_info = []
        cards_info = []
        game_info = {}
        for player in Player.ALL_PLAYERS:
            players_info.append({
                "name" : player.name,
                "id" : player.id,
                "health": player.health,
                "score": player.score,
                "score_temp" : player.score_temp,
                "deck": player.deck
            })
        for card in Card.ALL_CARDS:
            cards_info.append({
                "type": card.type,
                "name": card.name,
                "effect": card.effect,
                "amount": card.amount,
                "holder": card.holder,
                "id": str(card.id)
            })
        game_info["round_small"] = self.round_small
        game_info["round_big"] = self.round_big
        game_info["winners"] = self.get_winners()
        game_info["dead_players"] = self.get_dead_players()
        game_info["next_player_id"] = Player.get_player_by_id((self.round_small - 1) % len(Player.ALL_PLAYERS)).id
        state["game_info"] = game_info
        state["players_info"] = players_info
        state["cards_info"] = cards_info
        return state
    
    def load_game_state(self, state:dict):
        pass
    
    
    def send_message(self, message:str, recipient:str="all"):
        print(f"________to {recipient}_______\n{message}")

    def run(self, card_type:int):
        game_state = self.get_game_state()
        current_player = Player.get_player_by_id(game_state["game_info"]["next_player_id"])
        display_round_info = f"{self.round_big}-{self.round_small}({current_player.name}的回合)"
        if card_type == -1:
            self.send_message(display_round_info)
            for p in Player.ALL_PLAYERS:
                message = "————当前游戏状态————"
                for pp in Player.ALL_PLAYERS:
                    message += f"\n{pp.name}: 生命 {pp.health}, 分数 {pp.score}\n手牌: "
                    if pp.name != p.name:
                        for card in pp.deck:
                            message += f"{card.type}-{card.name} "
                    else:
                        for card in pp.deck:
                            message += f"x-xxxx "
                self.send_message(message, recipient=p.name)
            pool_unused_cards = [card for card in Card.ALL_CARDS if card.holder == "pool_unused"]
            self.send_message(f"牌池剩余牌数: {len(pool_unused_cards)}")
            self.send_message(f"{Card.CARD_MENU}\n{current_player.name}, 请施放一个法术:")
            return


        card = self.use_card(current_player, card_type)
        if card:
            card_message, card_private_messages = self.trigger_card_effect(current_player, card)
            self.send_message(card_message)
            for pm in card_private_messages:
                self.send_message(pm["content"], recipient=pm["name"])
        else:
            if card_type == 1:
                roll = self.roll_dice()
                self.send_message(f"{current_player.name} roll出了{roll}!")
                self.send_message(f"{current_player.name} 没有古代巨龙, 失去 {roll} 点生命...")
                current_player.change_health(-roll)
            else:
                self.send_message(f"{current_player.name}没有{card_type}号牌..., 失去1生命")
                current_player.change_health(-1)

        while len(current_player.deck) < Game.MAX_CARDS_IN_DECK:
            drawn_card = self.draw_card(current_player)
            if drawn_card:
                for p in Player.ALL_PLAYERS:
                    if p.id != current_player.id:
                        self.send_message(f"{current_player.name} 从牌池抽取了一张牌: {drawn_card.type}-{drawn_card.name}", recipient=p.name)
            else:
                self.send_message(f"池子没有牌了, {current_player.name} 无法继续抽牌")
                break
        self.round_small += 1
        

                


if __name__ == "__main__":
    game = Game()
    
    while True:
        game.run(-1)
        card_type = None
        while not isinstance(card_type, int):
            player_input = input()
            try:
                card_type = int(player_input.strip())
                if card_type not in Card.CARD_WIKI and card_type != 0:
                    game.send_message("请输入有效的法术编号。")
                    card_type = None
            except ValueError:
                game.send_message("请输入有效的法术编号。")
        game.run(card_type)
        input("按回车继续...")




            
