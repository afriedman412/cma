import click
from CMA.gui.functional_sql_gui import MusicDBGUI
from CMA.gui.playlist_builder import PlaylistBuilder

@click.command()
@click.option("-m", "--music_db", is_flag=True)
@click.option("-p", "--playlist_builder", is_flag=True)
def launch(music_db, playlist_builder):
    if music_db:
        MusicDBGUI()
        return

    if playlist_builder:
        PlaylistBuilder()
        return

if __name__=="__main__":
    launch()