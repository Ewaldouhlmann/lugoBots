import traceback
from abc import ABC
from typing import List

import lugo4py
from settings import get_my_expected_position, get_closestenemy_dist, get_closestally_position, Point, getDistance


class MyBot(lugo4py.Bot, ABC):
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("Disputando a bola")
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
            order_list = []
            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            opponent_goal_point = self.mapper.get_attack_goal()
            goal_region = self.mapper.get_region_from_point(opponent_goal_point.get_center())
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)
            me = inspector.get_me().position
            
            #se tiver oponente perto ele deve passar a bola para alguem do mesmo time
            closest_oponnentdis, closest_oponnent  = get_closestenemy_dist(inspector, my_region)

            

            if self.is_near(my_region, goal_region):
                #goleiro
                goalkeeper = inspector.get_opponent_players()[0]
                print(goalkeeper.position)
                if (goalkeeper.position.y < 5000):
                    target = Point(20000, 6200)
                    kick_order = inspector.make_order_kick_max_speed(target)
                elif (goalkeeper.position.y > 5000):
                    target = Point(20000, 3800)
                    kick_order = inspector.make_order_kick_max_speed(target)
                else:
                    target = Point(20000, 6200)
                    kick_order = inspector.make_order_kick_max_speed(target)
    
                order_list.append(kick_order)

            else:
                if (closest_oponnentdis < 2500000):
                    closest_allypos = get_closestally_position(inspector, my_region)
                    first_ally_position = list(closest_allypos.values())[0][0].position
                    

                    #percorrer os 3 aliados mais proximos e passar para algum deles que estiver mais a frente
                    pass_order = None
                    for ally_list in closest_allypos.values():
                        counter = 0
                        for ally in ally_list:
                            counter += 1
                            if ally.position.x > me.x and getDistance(me.x, me.y, ally.position.x, ally.position.y) > 300000:
                                pass_order = inspector.make_order_kick(first_ally_position,350)
                                break
                            if counter == 3:
                                break
                    
                    if (pass_order is None) and getDistance(me.x, me.y, ally.position.x, ally.position.y) > 300000:
                        #passa para o primeiro jogador no caso de nao ter definido um jogador que recebera a bo
                        print("Passando para o jogador mais proximo")
                        first_ally_position = list(closest_allypos.values())[0][0].position
                        pass_order = inspector.make_order_kick(first_ally_position,250)

                    order_list.append(pass_order)
            
            move_order = inspector.make_order_move_max_speed(self.mapper.get_attack_goal().get_center())
            order_list.append(move_order)

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
        max_distance = 1
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance