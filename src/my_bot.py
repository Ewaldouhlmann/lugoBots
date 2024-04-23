import traceback
from abc import ABC
from typing import List

import lugo4py
from settings import get_my_expected_position,getDistance, Point
import math
from random import randint
from lugo4py import mapper


class MyBot(lugo4py.Bot, ABC):
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position

            # try the auto complete for reader.make_order_... there are other options
            move_order = inspector.make_order_move_max_speed(ball_position)

            # Try other methods to create Move Orders:
            # move_order = reader.make_order_move_by_direction(lugo4py.DIRECTION_FORWARD)
            # move_order = reader.make_order_move_from_vector(lugo4py.sub_vector(vector_a, vector_b))

            # we can ALWAYS try to catch the ball
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position

            move_order = inspector.make_order_move_max_speed(ball_position)
            # we can ALWAYS try to catch the ball
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            order_list = []
            opponent_goal_point = self.mapper.get_attack_goal()
            goal_region = self.mapper.get_region_from_point(opponent_goal_point.get_center())
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)
            me = inspector.get_me()
            
            if (inspector.get_my_team_side() == lugo4py.TeamSide.AWAY):
                #Jogando fora de casa
                close_to_goal = self.is_close_to_op_goal(me, inspector)
                if close_to_goal == True:
                    kick = self.make_shoot(inspector, inspector.get_my_team_side(), me)
                    order_list.append(kick)
                else:
                    #Tenta passar para um jogador livre que esta a frente do atual jogador
                    free_players_list = self.get_free_players(inspector)
                    order_pass = self.can_make_pass_forward(me, free_players_list, inspector)

                    if (order_pass != None):
                        order_list.append(order_pass)
                    else:
                        #Verifica a distancia pro inimigo mais próximo dele, se não for a distancia minima. 
                        #Ele se move, caso seja menor que a distancia minima, ele tenta passar para um jogador livre atras
                        #Caso não tenha jogador livre atras, ele tenta passar para um jogador que esta a frente
                        closestly_enemy_distance = self.getClosestEnemy(inspector, self.mapper)
                        minimum_distance = 1500000

                        print(closestly_enemy_distance  > minimum_distance)
                        if (closestly_enemy_distance > minimum_distance):
                            move_order = inspector.make_order_move_max_speed(opponent_goal_point.get_center())
                            order_list.append(move_order)
                        else:
                            #passa para um jogador atrás livre, ou então da um passe para a frente
                            order_pass, move_order = self.can_make_pass_back(me, free_players_list, inspector)
                            if (order_pass != None and move_order != None):
                                order_list.append(move_order)
                                order_list.append(order_pass)
                            else:
                                pass_order, move_order = self.make_random_front_pass(order_list, inspector)
                                order_list.append(move_order)
                                order_list.append(pass_order)

            elif (inspector.get_my_team_side() == lugo4py.TeamSide.HOME):
                #Jogando em casa
                close_to_goal = self.is_close_to_op_goal(me, inspector)
                if close_to_goal == True:
                    kick = self.make_shoot(inspector, inspector.get_my_team_side(), me)
                    order_list.append(kick)
                else:
                    #Tenta passar para um jogador livre que esta a frente do atual jogador
                    free_players_list = self.get_free_players(inspector)
                    order_pass = self.can_make_pass_forward(me, free_players_list, inspector)

                    if (order_pass != None):
                        order_list.append(order_pass)
                    else:
                        #Verifica a distancia pro inimigo mais próximo dele, se não for a distancia minima. 
                        #Ele se move, caso seja menor que a distancia minima, ele tenta passar para um jogador livre atras
                        #Caso não tenha jogador livre atras, ele tenta passar para um jogador que esta a frente
                        closestly_enemy_distance = self.getClosestEnemy(inspector, self.mapper)
                        minimum_distance = 1500000

                        print(closestly_enemy_distance  > minimum_distance)
                        if (closestly_enemy_distance > minimum_distance):
                            move_order = inspector.make_order_move_max_speed(opponent_goal_point.get_center())
                            order_list.append(move_order)
                        else:
                            #passa para um jogador atrás livre, ou então da um passe para a frente
                            order_pass, move_order = self.can_make_pass_back(me, free_players_list, inspector)
                            if (order_pass != None and move_order != None):
                                order_list.append(move_order)
                                order_list.append(order_pass)
                            else:
                                pass_order, move_order = self.make_random_front_pass(order_list, inspector)
                                order_list.append(move_order)
                                order_list.append(pass_order)
            return order_list

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            ball_holder_position = inspector.get_ball().position

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            ball_holder_region = self.mapper.get_region_from_point(ball_holder_position)
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)

            if self.is_near(ball_holder_region, my_region):
                move_dest = ball_holder_position
            else:
                move_dest = get_my_expected_position(inspector, self.mapper, self.number)

            move_order = inspector.make_order_move_max_speed(move_dest)
            return [move_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            position = inspector.get_ball().position

            if state != lugo4py.PLAYER_STATE.DISPUTING_THE_BALL:
                position = self.mapper.get_attack_goal().get_center()

            my_order = inspector.make_order_move_max_speed(position)

            return [my_order, inspector.make_order_catch()]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance
    
    def is_close_to_op_goal(self, me, inspector: lugo4py.GameSnapshotInspector):
        #Esta funcao verifica se está proximo ao gol adversário
        goal_point = self.mapper.get_attack_goal().get_center()
        distance = getDistance(me.position.x, me.position.y, goal_point.x, goal_point.y)
        distance_to_shot = 9000000

        if (distance < distance_to_shot):
            return True
        return False
    
    def make_shoot(self, inspector, side, me):
        #Esta funcao realiza o chute para o gol
        goalkeeper_pos = inspector.get_opponent_players()[0].position
        if (side == lugo4py.TeamSide.HOME):
            if (goalkeeper_pos.y < 5000):
                target = Point(20000, 6200)
                kick_order = inspector.make_order_kick_max_speed(target)
            elif (goalkeeper_pos.y > 5000):
                target = Point(20000, 3800)
                kick_order = inspector.make_order_kick_max_speed(target)
            else:
                value =  randint(0,1)
                if (value == 0):
                    target = Point(20000, 3800)
                else:
                    target = Point(20000, 6200)
                kick_order = inspector.make_order_kick_max_speed(target)
        else:
            if (goalkeeper_pos.y < 5000):
                target = Point(0, 6200)
                kick_order = inspector.make_order_kick_max_speed(target)
            elif (goalkeeper_pos.y > 5000):
                target = Point(0, 3800)
                kick_order = inspector.make_order_kick_max_speed(target)
            else:
                value = randint(0,1)
                if (value == 0):
                    target = Point(0, 3800)
                else:
                    target = Point(0, 6200)

                kick_order = inspector.make_order_kick_max_speed(target)
        return kick_order
    
    def get_free_players(self, inspector):
        #Retorna os jogadores que estão muito livres
        free_players = []
        opponents = inspector.get_opponent_players()
        allys = inspector.get_my_team_players()
        range_distance = 12250000
        for player in allys:
            closest_opponent_distance = math.inf
            for opponent in opponents:
                distance = getDistance(player.position.x, player.position.y, opponent.position.x, opponent.position.y)
                if (distance < closest_opponent_distance):
                    closest_opponent_distance = distance
                if (closest_opponent_distance > range_distance):
                    break

            if (closest_opponent_distance > range_distance):
                free_players.append(player)

        return free_players

    def can_make_pass_forward(self, me, free_players_list, inspector):
        #Tenta passar para um jogador livre que esta a frente do atual jogador
        pass_order = None
        
        if (inspector.get_my_team_side() == lugo4py.TeamSide.AWAY):
            for p in free_players_list:
                if (p.position.x < me.position.x):
                    move_order = inspector.make_order_move_max_speed(p.position)
                    velocity = self.calc_pass_speed(inspector, p.position)
                    print("Velocidade do passe: ", velocity)
                    pass_order = inspector.make_order_kick(free_players_list[0].position, velocity)
                    break

        elif (inspector.get_my_team_side() == lugo4py.TeamSide.HOME):
            for p in free_players_list:
                if (p.position.x > me.position.x):
                    move_order = inspector.make_order_move_max_speed(p.position)
                    velocity = self.calc_pass_speed(inspector, p.position)
                    print("Velocidade do passe: ", velocity)
                    pass_order = inspector.make_order_kick(free_players_list[0].position, velocity)
                    break
        return pass_order
    
    def getClosestEnemy(self, inspector: lugo4py.GameSnapshotInspector, my_mapper: mapper.Mapper):
        player_position = inspector.get_ball().position
        oponentes = inspector.get_opponent_players()

        minDistance = math.inf
        for opponent in oponentes:
            current_distance = getDistance(player_position.x, player_position.y, opponent.position.x, opponent.position.y)
            if (current_distance < minDistance):
                minDistance = current_distance
        return minDistance
    
    def can_make_pass_back(self,me, free_players_list, inspector: lugo4py.GameSnapshotInspector):
        pass_order = move_order = None
        goalkepper = inspector.get_my_team_goalkeeper()
        if (inspector.get_my_team_side() == lugo4py.TeamSide.AWAY):
            for p in free_players_list:
                if (p.position.x > me.position.x and me.number != p.number and p.number != goalkepper.number):
                    move_order = inspector.make_order_move_max_speed(p.position)
                    velocity = self.calc_pass_speed(inspector, p.position)
                    print("Velocidade do passe: ", velocity)
                    pass_order = inspector.make_order_kick(free_players_list[0].position, velocity)
                    break

        elif (inspector.get_my_team_side() == lugo4py.TeamSide.HOME):
            for p in free_players_list:  
                if (p.position.x < me.position.x and me.number != p.number and p.number != goalkepper.number):
                    move_order = inspector.make_order_move_max_speed(p.position)
                    velocity = self.calc_pass_speed(inspector, p.position)
                    print("Velocidade do passe: ", velocity)
                    pass_order = inspector.make_order_kick(free_players_list[0].position, velocity)
                    break
        
        return pass_order, move_order

    def make_random_front_pass(self, order_list, inspector: lugo4py.GameSnapshotInspector):
        value = randint(0,1)
        #pega algum jogador livre, e tenta passar na direcao dele 
        if (inspector.get_my_team_side() == lugo4py.TeamSide.AWAY):
            target = Point(randint(0,inspector.get_me().position.x), randint(0,10000))
        else:
            target = Point(randint(inspector.get_me().position.x,20000), randint(0,10000))

        move_order = inspector.make_order_move_max_speed(target)    
        kick_order = inspector.make_order_kick_max_speed(target)
        return move_order, kick_order

    def calc_pass_speed (self, inspector: lugo4py.GameSnapshotInspector, destino):
        #Calcula a velocidade do passe
        saida = inspector.get_ball().position

        #Calcula a distancia entre o jogador e o destino
        dist = getDistance(saida.x, saida.y, destino.x, destino.y)
        if (dist < 3000000):
            return 100
        elif (dist < 5000000):
            return 130
        elif (dist < 7500000):
            return 160
        elif (dist < 10000000):
            return 190
        else:
            return 400
