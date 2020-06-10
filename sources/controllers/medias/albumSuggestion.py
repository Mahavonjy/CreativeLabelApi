#!/usr/bin/env python3
""" shebang """

from sources.models.admirations.admirations import AdmireSchema
from sources.models.medias.albums import Albums, AlbumSchema
from sources.controllers.tools.tools import by_user_genre_list
from sources.controllers.tools.tools import by_all_user_admire
from sources.controllers.tools.tools import merge_suggestion as merge_
from operator import itemgetter

albumSchema = AlbumSchema()
admire_schema = AdmireSchema()


def merge_all(list_albums: list) -> dict:
    """ delete album in dict if album created superior a 3 month """

    top_album = top_albums()
    news_albums = new_albums()
    # list_albums = sorted(list_albums, key=itemgetter('stream_total'), reverse=True)[:10]
    list_albums = sorted(list_albums, key=itemgetter('id'), reverse=True)[:10]
    list_albums = [i for i in list_albums if i not in top_album]
    news_albums = [i for i in news_albums if i not in top_album and list_albums]
    return dict(top_albums=top_album, albums_suggestion=list_albums, news_albums=news_albums)


def top_albums() -> list:
    """ get all album on 3 last month """

    all_albums, albums_returned = Albums.album_in_the_last_1_year(), []
    for album in all_albums:
        albums_returned.append(albumSchema.dump(album))
    return albums_returned


def new_albums() -> list:
    """ all new album """

    all_, album_returned = Albums.ten_last_albums(), []
    for album in all_:
        album_returned.append(albumSchema.dump(album))
    return album_returned


def top_album_and_suggestion(*args) -> dict:
    """ This is a function trie album """

    return merge_all(merge_(by_user_genre_list(args[0], "album") + by_all_user_admire(args[1], "album")))
