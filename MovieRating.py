# filepath: c:\Scripts\Test area\MovieRating.py
# Import the correct module
from imdb import Cinemagoer
import random
import requests
import json
import tkinter as tk
from tkinter import ttk
from io import BytesIO
from PIL import Image, ImageTk
import threading

class MovieRatingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Rating App")
        self.root.geometry("800x600")
        
        # Set dark mode colors
        self.bg_color = "#1e1e1e"
        self.text_color = "#e0e0e0"
        self.accent_color = "#3a3a3a"
        self.highlight_color = "#3c5f91"
        
        self.root.configure(bg=self.bg_color)
        
        # Apply dark theme to ttk widgets
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", background=self.accent_color, foreground=self.text_color)
        self.style.configure("TEntry", fieldbackground=self.accent_color, foreground=self.text_color)
        self.style.map("TButton", background=[("active", self.highlight_color)])
        self.style.configure("Treeview", background=self.accent_color, foreground=self.text_color, fieldbackground=self.accent_color)
        self.style.map("Treeview", background=[("selected", self.highlight_color)])
        self.style.configure("TLabelframe", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.text_color)
        
        self.ia = Cinemagoer()
        self.current_movie = None
        self.movies = []
        self.poster_image = None
        
        # Create UI elements
        self.create_ui()
        
    def create_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="Movie Title:").pack(side="left", padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_movie())
        
        ttk.Button(search_frame, text="Search", command=self.search_movie).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Random Movie", command=self.pick_random_movie).pack(side="left", padx=5)
        
        # Results frame
        self.results_frame = ttk.Frame(self.root, padding="10")
        self.results_frame.pack(fill="both", expand=True, pady=10)
        
        # Left side - Movie list
        list_frame = ttk.LabelFrame(self.results_frame, text="Search Results")
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Create a treeview for movie list
        self.movie_list = ttk.Treeview(list_frame, columns=("title", "year"), show="headings", height=10)
        self.movie_list.heading("title", text="Movie Title")
        self.movie_list.heading("year", text="Year")
        self.movie_list.column("title", width=220, anchor="w")
        self.movie_list.column("year", width=60, anchor="center")
        self.movie_list.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar to the treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.movie_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.movie_list.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.movie_list.bind("<<TreeviewSelect>>", self.on_movie_select)
        
        # Right side - Movie details
        details_frame = ttk.LabelFrame(self.results_frame, text="Movie Details")
        details_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Movie details content
        self.poster_label = ttk.Label(details_frame)
        self.poster_label.pack(pady=10)
        
        self.title_label = ttk.Label(details_frame, font=("Arial", 14, "bold"), wraplength=350)
        self.title_label.pack(pady=5)
        
        # Rating frame with traffic light system - make it more prominent
        rating_frame = ttk.Frame(details_frame)
        rating_frame.pack(pady=15, fill="x")
        
        # Label for "Rating" text
        ttk.Label(rating_frame, text="RATING:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        self.rating_text = tk.StringVar()
        self.rating_label = ttk.Label(rating_frame, font=("Arial", 16, "bold"), textvariable=self.rating_text)
        self.rating_label.pack(side="left", padx=10)
        
        # Canvas for rating indicator - larger and more prominent
        self.rating_canvas = tk.Canvas(rating_frame, width=60, height=60, bg=self.bg_color, highlightthickness=0)
        self.rating_canvas.pack(side="left")
        
        # Genre and year info
        self.info_label = ttk.Label(details_frame, font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        self.plot_label = ttk.Label(details_frame, wraplength=350, justify="left")
        self.plot_label.pack(pady=5, fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def search_movie(self):
        movie_name = self.search_entry.get().strip()
        if not movie_name:
            self.status_var.set("Please enter a movie title")
            return
            
        self.status_var.set(f"Searching for '{movie_name}'...")
        self.root.update()
        
        # Clear previous search results
        for item in self.movie_list.get_children():
            self.movie_list.delete(item)
        
        # Search for movies in a separate thread
        threading.Thread(target=self._perform_search, args=(movie_name,), daemon=True).start()
    
    def _perform_search(self, movie_name):
        try:
            self.movies = self.ia.search_movie(movie_name)
            
            if not self.movies:
                self.root.after(0, lambda: self.status_var.set("No movies found."))
                return
                
            # Update UI in the main thread
            self.root.after(0, self._update_movie_list)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _update_movie_list(self):
        for movie in self.movies:
            title = movie.get("title", "Unknown Title")
            year = movie.get("year", "Unknown")
            self.movie_list.insert("", "end", text=title, values=(title, year), iid=movie.movieID)
        
        self.status_var.set(f"Found {len(self.movies)} movies")
    
    def on_movie_select(self, event):
        selected_item = self.movie_list.selection()
        if not selected_item:
            return
            
        movie_id = selected_item[0]
        
        # Start fetching movie details in a separate thread
        threading.Thread(target=self._fetch_movie_details, args=(movie_id,), daemon=True).start()
    
    def _fetch_movie_details(self, movie_id):
        self.root.after(0, lambda: self.status_var.set("Loading movie details..."))
        
        try:
            movie = self.ia.get_movie(movie_id)
            self.current_movie = movie
            
            # Update UI in the main thread
            self.root.after(0, self._update_movie_details)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _update_movie_details(self):
        movie = self.current_movie
        
        # Update title and rating
        title_text = f"{movie.get('title', 'Unknown Title')} ({movie.get('year', 'Unknown')})"
        self.title_label.config(text=title_text)
        
        # Update genres and additional info
        genres = movie.get("genres", [])
        genre_text = ", ".join(genres[:3]) if genres else "Unknown Genre"
        self.info_label.config(text=f"Genre: {genre_text}")
        
        # Update rating with traffic light system
        rating = movie.get("rating")
        if rating:
            # Clear previous rating indicator
            self.rating_canvas.delete("all")
            
            # Draw traffic light circle based on rating
            if rating >= 7.5:
                color = "#4CAF50"  # Green for good ratings
            elif rating >= 6:
                color = "#FFC107"  # Yellow/Amber for decent ratings
            else:
                color = "#F44336"  # Red for poor ratings
                
            # Display rating text
            self.rating_text.set(f"IMDb: {rating}/10")
            
            # Draw rating circle
            self.rating_canvas.create_oval(5, 5, 45, 45, fill=color, outline="white", width=2)
            
            # Add rating text in circle
            self.rating_canvas.create_text(25, 25, text=f"{rating}", fill="white", font=("Arial", 12, "bold"))
        else:
            self.rating_text.set("Not Rated")
            self.rating_canvas.delete("all")
            self.rating_canvas.create_oval(5, 5, 45, 45, fill="#555555", outline="white", width=2)
            self.rating_canvas.create_text(25, 25, text="N/A", fill="white", font=("Arial", 10, "bold"))
        
        # Update plot
        plot = movie.get("plot")
        if plot and len(plot) > 0:
            plot_text = plot[0].split("::")[0]  # Get first plot summary without author info
            self.plot_label.config(text=plot_text)
        else:
            self.plot_label.config(text="No plot summary available")
        
        # Try to get poster
        threading.Thread(target=self._load_poster, daemon=True).start()
        
        self.status_var.set(f"Loaded details for '{movie.get('title')}'")
    
    def _load_poster(self):
        movie = self.current_movie
        cover_url = movie.get("full-size cover url")
        
        if not cover_url:
            cover_url = movie.get("cover url")
        
        if cover_url:
            try:
                response = requests.get(cover_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    
                    # Resize image to fit the UI
                    max_width = 200
                    max_height = 300
                    
                    width_ratio = max_width / image.width
                    height_ratio = max_height / image.height
                    ratio = min(width_ratio, height_ratio)
                    
                    new_width = int(image.width * ratio)
                    new_height = int(image.height * ratio)
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update UI in the main thread
                    self.root.after(0, lambda: self._set_poster(photo))
                    return
            except Exception as e:
                print(f"Error loading poster: {e}")
        
        # If we get here, display a placeholder
        self.root.after(0, lambda: self.poster_label.config(image=None, text="No poster available"))
    
    def _set_poster(self, photo):
        # Keep a reference to prevent garbage collection
        self.poster_image = photo
        self.poster_label.config(image=photo)
    
    def pick_random_movie(self):
        self.status_var.set("Fetching a random popular movie...")
        
        # Start thread to fetch random movie
        threading.Thread(target=self._fetch_random_movie, daemon=True).start()
    
    def _fetch_random_movie(self):
        try:
            # Instead of relying on top250 which might have issues, 
            # let's use a list of popular movie IDs
            popular_movie_ids = [
                "0111161",  # The Shawshank Redemption
                "0068646",  # The Godfather
                "0071562",  # The Godfather Part II
                "0468569",  # The Dark Knight
                "0050083",  # 12 Angry Men
                "0108052",  # Schindler's List
                "0167260",  # The Lord of the Rings: The Return of the King
                "0110912",  # Pulp Fiction
                "0060196",  # The Good, the Bad and the Ugly
                "0120737",  # The Lord of the Rings: The Fellowship of the Ring
                "0137523",  # Fight Club
                "0109830",  # Forrest Gump
                "1375666",  # Inception
                "0080684",  # Star Wars: Episode V - The Empire Strikes Back
                "0167261",  # The Lord of the Rings: The Two Towers
                "0073486",  # One Flew Over the Cuckoo's Nest
                "0099685",  # Goodfellas
                "0133093",  # The Matrix
                "0047478",  # Seven Samurai
                "0317248",  # City of God
                "0114369",  # Se7en
                "0118799",  # Life Is Beautiful
                "0038650",  # It's a Wonderful Life
                "0102926",  # The Silence of the Lambs
                "0076759",  # Star Wars
                "0816692",  # Interstellar
                "0120689",  # The Green Mile
                "0103064",  # Terminator 2: Judgment Day
                "0120815",  # Saving Private Ryan
                "0245429",  # Spirited Away
            ]
            
            # Pick a random movie ID
            random_id = random.choice(popular_movie_ids)
            
            # Get detailed information for the movie
            self.status_var.set("Loading movie details...")
            movie = self.ia.get_movie(random_id)
            self.current_movie = movie
            
            # Update UI in the main thread
            self.root.after(0, lambda: self._update_random_movie(movie))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _update_random_movie(self, movie):
        # Clear and update the movie list
        for item in self.movie_list.get_children():
            self.movie_list.delete(item)
            
        # Add the random movie to the list with proper values for display
        title = movie.get("title", "Unknown Title")
        year = movie.get("year", "Unknown")
        self.movie_list.insert("", "end", text=title, 
                              values=(title, year), 
                              iid=movie.movieID)
                              
        # Select the movie in the list to trigger detail loading
        self.movie_list.selection_set(movie.movieID)
        
        self.status_var.set(f"Selected a random movie: {title}")


def get_movie_rating():
    """Legacy console-based function that uses Cinemagoer"""
    movie_name = input("What movie do you want rated? ")
    ia = Cinemagoer()
    movies = ia.search_movie(movie_name)
    if not movies:
        print("No movies found.")
        return
    
    print("Movies found:")
    for i, movie in enumerate(movies):
        print(f"{i + 1}: {movie.get('title', 'Unknown')} ({movie.get('year', 'Unknown year')})")
    
    choice = int(input("Select a movie by number: ")) - 1
    if 0 <= choice < len(movies):
        movie_id = movies[choice].movieID
        movie = ia.get_movie(movie_id)
        rating = movie.get("rating")
        if rating:
            print(f"The rating for '{movie.get('title')}' is {rating}/10.")
        else:
            print(f"No rating found for '{movie.get('title')}'.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    try:
        # Check if tkinter is available
        import tkinter
        
        # If tkinter is available, run the GUI app
        root = tk.Tk()
        app = MovieRatingApp(root)
        root.mainloop()
    except ImportError as e:
        print("Tkinter is not available. Running console version instead.")
        print(f"Error: {e}")
        get_movie_rating()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Falling back to console version.")
        get_movie_rating()
