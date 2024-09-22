from games.models import Match, Bet
from users.models import CustomUser

correct_score = 10
winner_score = 5
wrong_score = -5


def calculate_score(params):
    user = CustomUser.objects.get(id=params['user'])
    matches = Match.objects.filter(date=params['date'])

    for match in matches:
        # match = Match.objects.get(id=params['id'])

        if match.status == 'finished':
            try:
                bet = Bet.objects.get(match=match,
                                      user=user)
                print("match result is : " + str(match.home_score) + " - " + str(match.away_score))
                print("user bet is : " + str(bet.home_score) + " - " + str(bet.away_score))

                if not bet.is_calculated:
                    if match.home_score == match.away_score:
                        if bet.home_score == bet.away_score and bet.home_score == match.home_score:
                            bet.score = bet.score + correct_score
                            bet.save()

                            user.score = user.score + correct_score
                            user.save()
                        elif bet.home_score == bet.away_score:
                            bet.score = bet.score + winner_score
                            bet.save()

                            user.score = user.score + winner_score
                            user.save()
                        else:
                            bet.score = bet.score + wrong_score
                            bet.save()

                            user.score = user.score + wrong_score
                            user.save()
                    elif match.home_score == bet.home_score and match.away_score == bet.away_score:
                        bet.score = bet.score + correct_score
                        bet.save()

                        user.score = user.score + correct_score
                        user.save()
                    elif match.home_score > match.away_score and bet.home_score > bet.away_score:
                        bet.score = bet.score + winner_score
                        bet.save()

                        user.score = user.score + winner_score
                        user.save()
                    elif match.away_score > match.home_score and bet.away_score > bet.home_score:
                        bet.score = bet.score + winner_score
                        bet.save()

                        user.score = user.score + winner_score
                        user.save()
                    else:
                        bet.score = bet.score + wrong_score
                        bet.save()

                        user.score = user.score + wrong_score
                        user.save()
                    bet.is_calculated = True
                    bet.save()
            except Bet.DoesNotExist:
                pass
