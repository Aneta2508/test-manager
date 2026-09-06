# Bierzemy gotowy obraz Pythona 3.11 jako punkt startowy
FROM python:3.11-slim

# Ustawiamy folder roboczy wewnątrz kontenera
WORKDIR /app

# Dodawanie czcionki z polskimi znakami (do raportów w pdf)
RUN apt-get update && apt-get install -y fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

# Kopiujemy plik z listy bibliotek do kontenera
COPY requirements.txt .

# Instalujemy wszystkie biblioteki z pliku requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy kod aplikacji do kontenera
COPY . .

# Tworzy folder media wewnątrz kontenera podczas budowania
RUN mkdir -p /app/media

# Mówimy Dockerowi że aplikacja będzie działać na porcie 8000
EXPOSE 8000

# Komenda która uruchomi się gdy kontener wystartuje
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]