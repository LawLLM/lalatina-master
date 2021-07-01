import copy
import pymongo
import dns
from bson.objectid import ObjectId
import config
import time

import copy

from pprint import pprint

import inspect


def inspeccionar(objeto):
    result = inspect.getmembers(objeto, lambda a: not(inspect.isroutine(a)))
    #result = inspect.getmembers(objeto)

    for item in result:
        print(item)


class PyMongoManager:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongoDb_connection)
        self.db_discord = self.client['db_panchessco']

#        self.collection_puzzles = self.db_discord['puzzles']
#
#        self.collection_puzzles_dataset = self.db_discord['puzzles_dataset']
#
#        self.collection_games_explorer = self.db_discord['games_explorer']
        
        self.collection_profiles = self.db_discord['profiles']
#        self.collection_chess_games = self.db_discord['chess_games']

        self.collection_guilds = self.db_discord['guild']

        self.shop = self.db_discord['shop']

        self.profile_base = {
            "user_id": None,
            "description": None,            # Chess Profile
            "birthday_date_day": None,
            "birthday_date_month": None,
            "birthday_number_attemps": 0,
            "thumbnail": "discord",
            "panchessco_money": 0,                      # Economy - Customize
            'legend_start_time': None,
            'legend_times': 0,
            'inventory': {}
        }

        self.guild_base = {
            "guild_id": None,
            "prefix": 'la!',
            "work_time": 300
        }

        self.object_base = {
            "name": None,
            "key": None,
            "value": 0,
            "description": None,
            "lot": None,
            "oldRoleAdded": 0,
            "newRoleAdded": False,
            "roleRemoved": 0,
            "channel_id": 0,
            "message": None,
            "log": False,
            "refund": False
        }


    # GUILD

    def get_guild(self, guild_id):
        myQuery = {'guild_id': guild_id}

        guild_dict = self.collection_guilds.find_one(myQuery)

        if not guild_dict:
            newData = copy.deepcopy(self.guild_base)
            newData['guild_id'] = guild_id

            guild_dict = newData

            self.collection_guilds.insert_one(newData)

        return guild_dict

    def update_discord_guild_prefix(self, guild_id, newPrefix):
        myQuery = {'guild_id': guild_id}

        if self.collection_guilds.count_documents(myQuery, limit=1):
            newValues = {'$set': {'prefix': newPrefix}}
            self.collection_guilds.update_one(myQuery, newValues)
        else:
            newData = copy.deepcopy(self.guild_base)
            newData['guild_id'] = guild_id
            newData['prefix'] = newPrefix
            
            self.collection_guilds.insert_one(newData)
    
    def get_users_birthday(self, month):
        myQuery = {'birthday_date_month': month}
        result = list(self.collection_profiles.find(myQuery))
        return result

    # ECONOMY

    def buy_item(self, user_id, category, item_id, final_balance):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$push': {category: item_id}, '$set': {'eris': final_balance}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData[category].append(item_id)
            newData['eris'] = final_balance

            self.collection_chess_players.insert_one(newData)

    def set_current_item(self, user_id, current_category, item_id):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$set': {current_category: item_id}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData[current_category] = item_id

            self.collection_chess_players.insert_one(newData)

    def update_money(self, user_id, new_balance):
        myQuery = {'user_id': user_id}

        if self.collection_profiles.count_documents(myQuery, limit=1):
            newValues = {'$set': {'panchessco_money': new_balance}}
            self.collection_profiles.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData['panchessco_money'] = new_balance

            self.collection_profiles.insert_one(newData)

    def update_daily(self, user_id, new_balance, time_last_daily, daily_multiplier):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$set': {'eris': new_balance, 'time_last_daily': time_last_daily, 'daily_multiplier': daily_multiplier}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData['eris'] = new_balance
            newData['time_last_daily'] = time_last_daily
            newData['daily_multiplier'] = daily_multiplier

            self.collection_chess_players.insert_one(newData)

    def get_time_remaining(self):
        myQuery = {'guild_id': 512830421805826048}
        result = self.collection_guilds.find_one(myQuery)
        return int(result['work_time'])
    
    def add_work_phrase(self, phrase):
        self.collection_guilds.update({'guild_id': 512830421805826048}, {'$push': {'work_phrases': phrase}})
        

    # PROFILE
    
    def set_thumbnail(self, user_id, thumbnail):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$set': {'thumbnail': thumbnail}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData['thumbnail'] = thumbnail

            self.collection_chess_players.insert_one(newData)


    def get_profile(self, user_id):
        myQuery = {'user_id': user_id}
        chess_profile = self.collection_profiles.find_one(myQuery)

        if chess_profile:
            return chess_profile
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            
            self.collection_profiles.insert_one(newData)
            return newData

    def get_profiles(self, user_id_list):
        user_id_dict_list = []
        for user_id in user_id_list:
            user_id_dict_list.append({'user_id': user_id})

        result = list(self.collection_profiles.find({'$or': user_id_dict_list}))

        return result

    def update_legend(self, user_id):
        myQuery = {'user_id': user_id}

        if self.collection_profiles.count_documents(myQuery, limit=1):
            newValues = {'$set': {'legend_start_time': time.time()}, '$inc': {'legend_times': 1}}
            return self.collection_profiles.find_one_and_update(myQuery, newValues, return_document=pymongo.ReturnDocument.AFTER)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData['legend_start_time'] = time.time()
            newData['legend_times'] = 1

            self.collection_profiles.insert_one(newData)

            return newData
    
    def update_birthday(self, user_id, day, month):
        myQuery = {'user_id': user_id}

        if self.collection_profiles.count_documents(myQuery, limit=1):
            newValues = {'$set': {'birthday_date_day': day, 'birthday_date_month': month}, '$inc': {'birthday_number_attemps': 1}}
            self.collection_profiles.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData['birthday_date_day'] = day
            newData['birthday_date_month'] = month
            newData['birthday_number_attemps'] = 1

            self.collection_profiles.insert_one(newData)

    # PUZZLE DATASET

    def get_puzzle_from_dataset(self, puzzle_id):
        myQuery = {'game_id': puzzle_id}

        puzzle_dict = self.collection_puzzles_dataset.find_one(myQuery)

        return puzzle_dict
    
    def get_puzzle_random(self):
        pipeline = [{'$sample': {'size': 1}}]
        return list(self.collection_puzzles_dataset.aggregate(pipeline))[0]

    def get_puzzle_by_theme(self, theme_id):
        pipeline = [{'$match': {'themes': theme_id}}, {'$sample': {'size': 1}}]
        return list(self.collection_puzzles_dataset.aggregate(pipeline))[0]

    def get_puzzle_by_difficulty(self, difficulty):
        if difficulty == 'easy':
            rating_min = 1100
            rating_max = 1900
        elif difficulty == 'medium':
            rating_min = 1901
            rating_max = 2700
        else:
            rating_min = 2701
            rating_max = 3400

        pipeline = [{'$match': {'rating': {'$gte': rating_min, '$lte': rating_max}}}, {'$sample': {'size': 1}}]
        return list(self.collection_puzzles_dataset.aggregate(pipeline))[0]
    
    def get_puzzle_by_limits(self, rating_min, rating_max):
        if rating_min > rating_max:
            min = rating_max
            max = rating_min
        else:
            min = rating_min
            max = rating_max

        pipeline = [{'$match': {'rating': {'$gte': min, '$lte': max}}}, {'$sample': {'size': 1}}]
        aggregation_list = list(self.collection_puzzles_dataset.aggregate(pipeline))

        if len(aggregation_list) > 0:
            return aggregation_list[0]
        else:
            return None

    def get_puzzle_by_theme_difficulty(self, theme_id, difficulty):
        if difficulty == 'easy':
            rating_min = 1100
            rating_max = 1900
        elif difficulty == 'medium':
            rating_min = 1901
            rating_max = 2700
        else:
            rating_min = 2701
            rating_max = 3400
        
        pipeline = [{'$match': {'themes': theme_id, 'rating': {'$gte': rating_min, '$lte': rating_max}}}, {'$sample': {'size': 1}}]
        aggregation_list = list(self.collection_puzzles_dataset.aggregate(pipeline))
        
        if len(aggregation_list) > 0:
            return aggregation_list[0]
        else:
            return None

    def get_puzzle_by_theme_limits(self, theme_id, rating_min, rating_max):
        if rating_min > rating_max:
            min = rating_max
            max = rating_min
        else:
            min = rating_min
            max = rating_max
        
        pipeline = [{'$match': {'themes': theme_id, 'rating': {'$gte': min, '$lte': max}}}, {'$sample': {'size': 1}}]
        aggregation_list = list(self.collection_puzzles_dataset.aggregate(pipeline))
        
        if len(aggregation_list) > 0:
            return aggregation_list[0]
        else:
            return None

    
    # GUILDS

    def get_panchessco_prefix(self):
        myQuery = {"guild_id": 512830421805826048}
        result = self.collection_guilds.find_one(myQuery)
        return result['prefix']

    def update_discord_guild_push_sar(self, guild_id, newData):
        myQuery = {"guild_id": guild_id}
        newValues = {"$push": {"self_assignable_roles": newData}}
        self.collection_guilds.update_one(myQuery, newValues)
    
    def update_discord_guild_pull_sar(self, guild_id, newData):
        myQuery = {"guild_id": guild_id}
        newValues = {"$pull": {"self_assignable_roles": newData}}
        self.collection_guilds.update_one(myQuery, newValues)

    def get_discord_guilds(self):
        return list(self.collection_guilds.find())

    # BUGS AND SUGGESTIONS

    def get_bug_count_and_increase_count(self):
        myQuery = { 'guild_id': 521521445134925834 }
        newValues = { '$inc': {'bug_count': 1} }
        return self.collection_guilds.find_one_and_update(myQuery, newValues)['bug_count']

    def get_suggestion_count_and_increase_count(self):
        myQuery = { 'guild_id': 521521445134925834 }
        newValues = { '$inc': {'suggestion_count': 1} }
        return self.collection_guilds.find_one_and_update(myQuery, newValues)['suggestion_count']

    def increase_suggestion_count(self):
        myQuery = { 'guild_id': 521521445134925834 }
        newValues = { '$inc': {'suggestion_count': 1} }
        self.collection_guilds.update_one(myQuery, newValues)
    
    # BANNEDS FROM USE AQUA

    def add_user_banned(self, user_id, category):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$set': {category: False}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData[category] = False

            self.collection_chess_players.insert_one(newData)

    def remove_user_banned(self, user_id, category):
        myQuery = {'user_id': user_id}

        if self.collection_chess_players.count_documents(myQuery, limit=1):
            newValues = {'$set': {category: True}}
            self.collection_chess_players.update_one(myQuery, newValues)
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            newData[category] = True

            self.collection_chess_players.insert_one(newData)
    
    def get_users_banneds(self, category):
        myQuery = {category: False}

        users = self.collection_chess_players.find(myQuery)

        ID_list = []
        for user in users:
            ID_list.append(user['user_id'])

        return ID_list

    # CHESS GAMES

    def insert_discord_chess_player(self, user_id):
        myQuery = {"user_id": user_id}

        if not self.collection_chess_players.count_documents(myQuery, limit=1):
            newData = copy.deepcopy(self.profile_base)
            newData['user_id'] = user_id    
            self.collection_chess_players.insert_one(newData)

    def get_discord_chess_player(self, user_id):
        myQuery = {'user_id': user_id}
        chess_profile = self.collection_chess_players.find_one(myQuery)

        if chess_profile:
            return chess_profile
        else:
            newData = copy.copy(self.profile_base)
            newData['user_id'] = user_id
            
            self.collection_chess_players.insert_one(newData)
            return newData
    
    def update_discord_chess_player(self, user_id, player):
        myQuery = {"user_id": user_id}
        newValues = {"$set": player}

        self.collection_chess_players.update_one(myQuery, newValues)

    def insert_chess_game(self, game):
        self.collection_chess_games.insert_one(game.get_game_dict())

    def get_discord_chess_games_from_user_id(self, user_id):
        myQuery = {"$or": [{"user_1_id": user_id}, {"user_2_id": user_id}]}

        return list(self.collection_chess_games.find(myQuery).sort('_id', pymongo.ASCENDING))

    def get_discord_chess_games_between_two_players(self, user_1_id, user_2_id):
        myQuery = {"$or": [{"user_1_id": user_1_id, "user_2_id": user_2_id}, {"user_1_id": user_2_id, "user_2_id": user_1_id}]}
        
        return list(self.collection_chess_games.find(myQuery).sort('_id', pymongo.ASCENDING))

    def get_discord_chess_game_from_object_id(self, object_id):
        try:
            myQuery = {'_id': ObjectId(object_id)}
            return self.collection_chess_games.find_one(myQuery)
        except:
            return None
        
    def update_discord_chess_game(self, user_id, newData):
        myQuery = {"$and": [{"$or": [{"user_1_id": user_id}, {"user_2_id": user_id}]}, {"game_result": "*"}]}
        newValues = {"$set": newData}

        self.collection_chess_games.update_one(myQuery, newValues)

    def get_current_game(self, user_id):
        return self.collection_chess_games.find_one({"$and": [{"$or": [{"user_1_id": user_id}, {"user_2_id": user_id}]}, {"game_result": "*"}]})

    def verifyPlayerOnGame(self, user_id):
        myQuery = {'$and': [{"$or": [{"user_1_id": user_id}, {"user_2_id": user_id}]}, {"game_result": "*"}]}

        return self.collection_chess_games.find_one(myQuery)

    #def get_discord_chess_archive

