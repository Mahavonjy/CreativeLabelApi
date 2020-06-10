#!/usr/bin/env python3
""" shebang """

from sources.tools.tools import merge_suggestion as merge_
from sources.tools.tools import by_user_genre_list
from sources.tools.tools import by_all_user_admire
from sources.models.medias.media import Media, MediaSchema
from operator import itemgetter

media_schema = MediaSchema()


def merge_all(songs_suggest) -> dict:
    """ delete album in dict if album created superior a 3 month """

    top_album = top_medias()
    top_new_song = new_songs()
    songs_suggest = [i for i in songs_suggest if i not in top_album]
    songs_suggest = sorted(songs_suggest, key=itemgetter('number_play'), reverse=True)[:10]
    all_news_song = [i for i in top_new_song if i not in top_album and songs_suggest]
    return dict(top_songs=top_album, songs_suggestion=songs_suggest, news_song=all_news_song)


def top_medias() -> list:
    """ top song in the 3 last month """

    all_, song_returned = Media.all_songs_in_three_last_month(), []
    for song in all_:
        song_returned.append(media_schema.dump(song))
    return song_returned


def new_songs() -> list:
    """ top 10 news song """

    all_, song_returned = Media.ten_last_songs("music"), []
    for song in all_:
        song_returned.append(media_schema.dump(song))
    return song_returned


def media_beat_suggestion(*args):
    """

    :param args: arg[0] is all list of user genre list, args[1] is music type and args[2] == user_id
    :return: all list of media merged
    """
    return merge_all(merge_(by_user_genre_list(args[0], args[1]) + by_all_user_admire(args[2], args[1])))
