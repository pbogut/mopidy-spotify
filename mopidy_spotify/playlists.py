from __future__ import unicode_literals

import logging

from mopidy import backend

from mopidy_spotify import translator, utils


logger = logging.getLogger(__name__)


class SpotifyPlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, backend):
        self._backend = backend
        self._timeout = self._backend._config['spotify']['timeout']

    def as_list(self):
        with utils.time_logger('playlists.as_list()'):
            username = self._backend._session.user_name
            web_playlists = self._backend._web_client.get(
                'users/' + username + '/playlists', params={})

            return [
                translator.web_to_playlist_ref(web_playlist, username=username)
                for web_playlist in web_playlists['items']]

    def get_items(self, uri):
        with utils.time_logger('playlist.get_items(%s)' % uri):
            web_tracks = self._backend._web_client.get(
                'users/' + self._user_from_uri(uri) + '/playlists/'
                + self._playlist_from_uri(uri) + '/tracks', params={})

            return [translator.web_to_track(web_track)
                    for web_track in web_tracks['items']]

    def lookup(self, uri):
        with utils.time_logger('playlists.lookup(%s)' % uri):
            username = self._backend._session.user_name
            web_playlist = self._backend._web_client.get(
                'users/' + self._user_from_uri(uri) + '/playlists/'
                + self._playlist_from_uri(uri), params={})

            return translator.web_to_playlist(web_playlist, username=username)

    def refresh(self):
        pass  # Not needed as long as we don't cache anything.

    def create(self, name):
        pass  # TODO

    def delete(self, uri):
        pass  # TODO

    def save(self, playlist):
        pass  # TODO

    def _user_from_uri(self, uri):
        return uri.split(':')[2]

    def _playlist_from_uri(self, uri):
        return uri.split(':')[4]


def on_container_loaded(sp_playlist_container):
    # Called from the pyspotify event loop, and not in an actor context.
    logger.debug('Spotify playlist container loaded')

    # This event listener is also called after playlists are added, removed and
    # moved, so since Mopidy currently only supports the "playlists_loaded"
    # event this is the only place we need to trigger a Mopidy backend event.
    backend.BackendListener.send('playlists_loaded')


def on_playlist_added(sp_playlist_container, sp_playlist, index):
    # Called from the pyspotify event loop, and not in an actor context.
    logger.debug(
        'Spotify playlist "%s" added to index %d', sp_playlist.name, index)

    # XXX Should Mopidy support more fine grained playlist events which this
    # event can trigger?


def on_playlist_removed(sp_playlist_container, sp_playlist, index):
    # Called from the pyspotify event loop, and not in an actor context.
    logger.debug(
        'Spotify playlist "%s" removed from index %d', sp_playlist.name, index)

    # XXX Should Mopidy support more fine grained playlist events which this
    # event can trigger?


def on_playlist_moved(
        sp_playlist_container, sp_playlist, old_index, new_index):
    # Called from the pyspotify event loop, and not in an actor context.
    logger.debug(
        'Spotify playlist "%s" moved from index %d to %d',
        sp_playlist.name, old_index, new_index)

    # XXX Should Mopidy support more fine grained playlist events which this
    # event can trigger?
