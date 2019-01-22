import os
import requests
from IPython.display import display, HTML

class  CFMovieSystem:
    def __init__(self, cf_data_movie, cf_model):
        
        self.cf_data_movie = cf_data_movie
        self.cf_model = cf_model

    def _display_image_from_url_list(self, images, header=None, width="100%"): 
        
        if type(width)==type(1): width = "{}px".format(width)
        html = ["<table style='width:{}'><tr>".format(width)]
        if header is not None:
            html += ["<th>{}</th>".format(h) for h in header] + ["</tr><tr>"]

        for image in images:
            html.append("<td><img src='{}' /></td>".format(image))
        html.append("</tr></table>")
        display(HTML(''.join(html)))

    def show_recommended_movies(self, movie_name, k=10, tmdb_key=None, df_ml_imdb_id=None): 
        
        # Convert user-selected movie name to movie id then obtain the top-k similar movies
        movie_item_id = self.cf_data_movie.convert_name_to_id(movie_name)
        movie_neighbor_name = [self.cf_data_movie.convert_id_to_name(i) for i in self.cf_model.get_similar_item(movie_item_id, k)]
        movie_neighbor_id = [self.cf_data_movie.convert_name_to_id(i) for i in movie_neighbor_name]
        if tmdb_key is None:
            # Output the top-k recommended movieds in text
            print ("Movie you select is '%s'"%(movie_name))
            print ("Based on '%s', we recommend %d movies below:"%(movie_name, k))
            print (movie_neighbor_name)
        else:
            # Request the hyperlinks of movie poster from TMDB
            get_poster = TMDBPoster(tmdb_key)
            input_movie_imdb_id = int(df_ml_imdb_id[df_ml_imdb_id['movieId']==movie_item_id].iloc[0]['imdbId']) 
            input_poster_url = get_poster.get_poster_urls('tt{:07}'.format(input_movie_imdb_id))[0]
            # convert ml movie id to imdb movie id and request movie poster images from TMDB
            movie_neighbor_imdb_id = [int(df_ml_imdb_id[df_ml_imdb_id['movieId']==i].iloc[0]['imdbId']) for i in movie_neighbor_id]
            poster_urls = [get_poster.get_poster_urls('tt{:07}'.format(i))[0] for i in movie_neighbor_imdb_id]

            print ("Movie you select is '%s'"%(movie_name))
            self._display_image_from_url_list([input_poster_url], header='', width="10%" )
            print ("Based on '%s', we recommend %d movies below:"%(movie_name, k))
            self._display_image_from_url_list(poster_urls)
            print (movie_neighbor_name)


class TMDBPoster:
    def __init__(self, tmdb_key):
        self.CONFIG_PATTERN = 'http://api.themoviedb.org/3/configuration?api_key={key}'
        self.IMG_PATTERN = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={key}' 
        #self.KEY = '282533ba881379db7953301dee2ef238'
        self.KEY = tmdb_key
            
    def _get_json(self, url):
        r = requests.get(url)
        return r.json()
        
    def _download_images(self, urls, path='.', filename_prefix='poster'):
        """download all images in list 'urls' to 'path' """
    
        for nr, url in enumerate(urls):
            r = requests.get(url)
            filetype = r.headers['content-type'].split('/')[-1]
            #filename = 'poster_{0}.{1}'.format(nr+1,filetype)
            filename = filename_prefix + '_{0}.{1}'.format(nr+1,filetype)
            filepath = os.path.join(path, filename)
            with open(filepath,'wb') as w:
                w.write(r.content)
    
    def get_poster_urls(self, imdbid):
        
        config = self._get_json(self.CONFIG_PATTERN.format(key=self.KEY))
        base_url = config['images']['base_url']
        sizes = config['images']['poster_sizes']
    
       
        def size_str_to_int(x):
            return float("inf") if x == 'original' else int(x[1:])
        max_size = max(sizes, key=size_str_to_int)
    
        posters = self._get_json(self.IMG_PATTERN.format(key=self.KEY,imdbid=imdbid))['posters']
        poster_urls = []
        for poster in posters:
            rel_path = poster['file_path']
            url = "{0}{1}{2}".format(base_url, max_size, rel_path)
            poster_urls.append(url) 
    
        return poster_urls
    
    def download_tmdb_posters(self, imdbid, count=None, outpath='.'):    
        urls = self.get_poster_urls(imdbid)
        if count is not None:
            urls = urls[:count]
        self._download_images(urls, outpath, imdbid)
    
#if __name__=="__main__":
#    get_poster = TMDBPoster() 
#    get_poster.download_tmdb_posters('tt0114709', 1)
