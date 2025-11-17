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
    
    def __init__(self, player_info:dict):
        self.backup:dict = player_info.copy()
        self.name:str = player_info["name"]
        self.id:int = Player.ALL_PLAYERS.__len__()
        self.score:int = player_info["score"]
        self.health:int = player_info["health"]
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
        self.name = self.backup["name"]
        self.id = self.backup["id"]
        # self.score = self.backup["score"]
        self.health = self.backup["health"]
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

    ALL_CARDS = []  
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
    def use_card(self, player:Player, card_type:int):
        for card in player.deck:
            if card.type == card_type:
                card.change_holder("pool_used")
                player.deck.remove(card)
                print(f"{player.name} used card type {card_type}.")
                return card
        print(f"{player.name} does not have card type {card_type}.")
        return None
    
    def draw_card(self, player:Player):
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
        if card.type == 1:
            damage = self.roll_dice()
            for p in Player.ALL_PLAYERS:
                if p.id != player.id:
                    p.change_health(-damage)
                    print(f"{player.name} deals {damage} damage to {p.name}.")
        elif card.type == 2:
            for p in Player.ALL_PLAYERS:
                if p.id != player.id:
                    p.change_health(-1)
                    print(f"{player.name} deals {damage} damage to {p.name}.")
        elif card.type == 3:
            heal = self.roll_dice()
            player.change_health(heal)
            print(f"card type 3 {player.name} for {heal} health.")
        elif card.type == 4:
            available_cards = [c for c in Card.ALL_CARDS if c.holder == "pool_unused"]
            if available_cards:
                removed_card = random.choice(available_cards)
                removed_card.change_holder("pool_used")
                print(f"{player.name} removed card {removed_card.name} from the pool.")
        elif card.type == 5:
            front_player = Player.get_player_by_id((player.id - 1))
            back_player = Player.get_player_by_id((player.id + 1))
            front_player.change_health(-1)
            back_player.change_health(-1)
        elif card.type == 6:
            front_player = Player.get_player_by_id((player.id - 1))
            front_player.change_health(-1)
        elif card.type == 7:
            back_player = Player.get_player_by_id((player.id + 1))
            back_player.change_health(-1)
        elif card.type == 8:
            player.change_health(1)

    def round_check(self):
        winners = self.get_winners()
        dead_players = self.get_dead_players()
        if dead_players:
            print(f"dead_players:\n{dead_players}")
            print(f"Winners:\n{winners}")
            return winners, dead_players
        else:
            return False

    def get_winners(self):
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
        players_info = {}
        for player in Player.ALL_PLAYERS:
            players_info[player.name] = {
                "health": player.health,
                "score": player.score,
                "deck": [card.name for card in player.deck]
            }
        return state

    def main_game_loop(self):
        for player in Player.ALL_PLAYERS:
            if not player.is_alive():
                print(f"{player.name} is eliminated from the game.")
                continue
            drawn_card = self.draw_card(player)
            if drawn_card:
                self.trigger_card_effect(player, drawn_card)
        



            
