import requests
import concurrent.futures
import json

class MovieInfoFetcher:
    """Busca informações de filmes"""
    
    def __init__(self):
        #configuração da chaves de API
        self.omdb_key = "bf74de83"
        self.tmdb_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZDI3N2U1YzAzMTJkNzEzMWQyYzk4YjVlMDAyNzIwNiIsIm5iZiI6MTc0MzEwMjEzNS4xODUsInN1YiI6IjY3ZTVhMGI3MjU4MGVlZjFlODAwNjEyOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nu3nIQa_mM7uiipM_wAnaD_3KWCdDtnCaY_JTP8zuiI"
        
        #configuração das URLs
        self.omdb_base_url = "http://www.omdbapi.com/"
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
        #configuração dos headers para TMDB
        self.tmdb_headers = {
            "Authorization": f"Bearer {self.tmdb_token}",
            "Accept": "application/json"
        }
    
    def get_omdb_info(self, title, year):
        """Busca sinopse do filme na API OMDB"""
        params = {
            "apikey": self.omdb_key,
            "t": title,
            "y": year
        }
        
        try:
            response = requests.get(self.omdb_base_url, params=params, timeout=10)
            response.raise_for_status()  #exceção para erros HTTP
            
            data = response.json()
            if data.get("Response") == "True" and "Plot" in data:
                return f"Sinopse: {data['Plot']}"
            else:
                return f"Sinopse: Não disponível. {data.get('Error', '')}"
        except Exception as e:
            return {"error": f"Falha ao obter dados do OMDB: {str(e)}"}
    
    def get_tmdb_reviews(self, title, year):
        """Busca reviews do filme na API TMDB"""
        #busca de ID do filme
        search_url = f"{self.tmdb_base_url}/search/movie"
        search_params = {
            "query": title,
            "primary_release_year": year,
            "language": "en-US"
        }
        
        try:
            #busca de ID do filme
            search_response = requests.get(
                search_url, 
                params=search_params, 
                headers=self.tmdb_headers,
                timeout=10
            )
            search_response.raise_for_status()
            
            search_data = search_response.json()
            if not search_data.get("results"):
                return "Filme não encontrado no TMDB."
            
            #usa o ID
            movie_id = search_data["results"][0]["id"]
            
            #procurando as reviews usando o ID do filme
            reviews_url = f"{self.tmdb_base_url}/movie/{movie_id}/reviews"
            reviews_response = requests.get(
                reviews_url,
                headers=self.tmdb_headers,
                timeout=10
            )
            reviews_response.raise_for_status()
            
            reviews_data = reviews_response.json()
            results = reviews_data.get("results", [])
            
            #configurando as reviews para no máximo 3
            if not results:
                return "Nenhuma review encontrada."
                
            formatted_reviews = []
            for i, review in enumerate(results[:3], 1):
                formatted_reviews.append(f"\nReview {i} - \n{review['content']}")
                
            return "".join(formatted_reviews)
            
        except Exception as e:
            return f"Erro ao buscar reviews: {str(e)}"
    
    def get_movie_info(self, title, year):
        """Busca informações do filme nas duas APIs"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #fazendo as funções em parelelo
            omdb_future = executor.submit(self.get_omdb_info, title, year)
            tmdb_future = executor.submit(self.get_tmdb_reviews, title, year)
            
            #pega os resultados
            omdb_data = omdb_future.result()
            tmdb_reviews = tmdb_future.result()
            
            #retorna os resultados
            return {
                "title": title,
                "year": year,
                "omdb": omdb_data,
                "tmdb": tmdb_reviews
            }

def main():
    #Inicio pedi os dados do filme ao usuário
    title = input("Titulo do Filme em inglês: ")
    year = input("Ano do Lançamento: ")
    
    #Cria a instância da classe e busca as informações com os dados obtidos
    fetcher = MovieInfoFetcher()
    movie_info = fetcher.get_movie_info(title, year)
    
    #resultados exibidos em tela
    print(f"Filme: {movie_info['title']} / Lançamento: {movie_info['year']}")
    print(f"\nOMDB: {movie_info['omdb']}")
    print(f"\nTMDB: {movie_info['tmdb']}")

if __name__ == "__main__":
    main()