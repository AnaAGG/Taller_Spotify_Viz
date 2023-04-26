import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("../")
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from datetime import datetime



def create_credentials():
    """_summary_

    Returns:
        spotify object: the object with the credentials for the Spotify API
    """
    # The above code is setting the client secret and client id to the environment variables.
    CLIENT_SECRET = os.getenv("client_Secret")
    CLIENT_ID = os.getenv("client_ID")

    # Creating a Spotify object that will be used to make requests to the Spotify API.
    credenciales = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = credenciales)

    return sp

def prepare_url(link):
    """_summary_

    Args:
        link (string): the complete playlist link obtained from the spotify app

    Returns:
        string: the URI of the selected spotify playlist 
    """
    playlist_URI = link.split("/")[-1].split("?")[0]
    return playlist_URI



def extract_songs(conexion, playlist_URI, numero_canciones):
    """_summary_

    Args:
        conexion (spotify object): object of spotify with the credentials of spotify API
        playlist_URI (string): string with the uri of the selected spotify playlist

    Returns:
        list: list with all the songs included in the selected spotify playlist
    """    
    numero_canciones = int(str(numero_canciones + 100)[0])
    offset = 0
    all_data = []
    for i in range(numero_canciones):
        all_data.append(conexion.playlist_tracks(playlist_URI, offset=offset)["items"])
        offset += 100
    return all_data



def clean_data(all_data):
    """_summary_

    Args:
        all_data (list): list with all the songs and their characteristics result of the playlist_tracks endpoint

    Returns:
        dataframe: dataframe with the selected information of the playlist_tracks endpoint
    """    
    basic_info = {"song": [], "artist": [], "date": [], "explicit": [], "uri_cancion": [], "popularity": [], "ironhacker": [], "links": [], 'uri_artista': []}
    for i in range(len(all_data)): 
        for z in range(len(all_data[i])): 
            artista = []
            uris = []
        
            basic_info["uri_cancion"].append(all_data[i][z]["track"]["uri"])
            basic_info["song"].append(all_data[i][z]["track"]["name"])
            basic_info["date"].append(all_data[i][z]["track"]["album"]["release_date"])
            basic_info["explicit"].append(all_data[i][z]["track"]["explicit"])
            basic_info["popularity"].append(all_data[i][z]["track"]["popularity"])
            basic_info["ironhacker"].append(all_data[i][z]["added_by"]["id"])
            basic_info["links"].append(all_data[i][z]["track"]["external_urls"]["spotify"])

            
            if len(all_data[i][z]["track"]["artists"]) == 1:
                basic_info["artist"].append(all_data[i][z]["track"]["artists"][0]["name"])
                basic_info["uri_artista"].append(all_data[i][z]["track"]["artists"][0]["id"])

            else:
                for x in range(len(all_data[i][z]["track"]["artists"])):
                    artista.append(all_data[i][z]["track"]["artists"][x]["name"])
                    uris.append(all_data[i][z]["track"]["artists"][x]["id"])
                basic_info["artist"].append(artista)
                basic_info["uri_artista"].append(uris)
                
     
    df = pd.DataFrame(basic_info)
    return df

def get_features(conexion, df_basic_info, list_uris_songs):
    
    features = []
    for track in list_uris_songs:
        features.append(conexion.audio_features(track))
        
        
    df = pd.DataFrame(features)
    df_features = df[0].apply(pd.Series)
    final = pd.merge(df_basic_info, df_features,  left_on='uri_cancion', right_on="uri")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    final.to_csv(f"../data/basic_info_{fecha_hoy}.csv")
    return final

def clean_df(df):
    """_summary_

    Args:
        df (dataframe): full dataframe results of the playlist_tracks endpoint 

    Returns:
        dataframe: dataframe woth the artist column exploded and columns filtered
    """    
    df = df.explode("artist")
    df = df.explode("uri_artista")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    df.to_csv(f"../data/basic_info_{fecha_hoy}.csv")
    return df[["song", "date", "popularity", "ironhacker", "artist", "uri_artista",  "uri_cancion"]]

def get_artist_album(conexion, artist_uri):
    
    df_artistas = pd.DataFrame()
    
    for artista in artist_uri:
        info_albumes = {"artist_name": [], 
                    "album_name": [], 
                    "release_date": [], 
                    "total_tracks": []}
    
        albumes = conexion.artist_albums(artista)["items"]
    
        for i in range(len(albumes)):
            info_albumes["artist_name"].append(albumes[i]["artists"][0]["name"])
            info_albumes["album_name"].append(albumes[i]["name"])
            info_albumes["release_date"].append(albumes[i]["release_date"])
            info_albumes["total_tracks"].append(albumes[i]["total_tracks"])
        
        df_album = pd.DataFrame(info_albumes)
    
        df_album["album_name"] = df_album["album_name"].str.title()
        df_album.drop_duplicates(subset = "album_name", inplace = True)
        
        df_artistas = pd.concat([df_artistas, df_album], axis = 0)
    
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')

    df_artistas.to_csv(f"../data/albums_artistas_{fecha_hoy}.csv")

    return df_artistas

def get_artist_data(conexion, artist_uri):
    
    df_artistas_info = pd.DataFrame()
    
    for artista in artist_uri:
        info_albumes = {"artist_name": [], 
                    "artist_id": [], 
                    "followers": [], 
                    "genres": [], 
                    "popularity":[]}
    
        info = conexion.artist(artista)
    
    
        info_albumes["artist_name"].append(info['name'])
        info_albumes["artist_id"].append(info['id'])
        info_albumes["followers"].append(info["followers"]["total"])
        info_albumes["genres"].append(info["genres"])
        info_albumes["popularity"].append(info["popularity"])

        
        df_artistas = pd.DataFrame(info_albumes)
    
        df_artistas.drop_duplicates(subset = "artist_name", inplace = True)
        
        df_artistas_info = pd.concat([df_artistas_info, df_artistas], axis = 0)
        
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    df_artistas_info.to_csv(f"../data/info_artistas_{fecha_hoy}.csv")

    return df_artistas_info

