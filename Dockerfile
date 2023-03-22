# Użyj oficjalnego obrazu Python jako bazy
FROM python:3.10-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt .

# Zainstaluj wymagane zależności
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj pozostałe pliki projektu do katalogu roboczego
COPY . .

# Zdefiniuj zmienną środowiskową, która wskazuje, gdzie przechowywać plik tracked_links.json
ENV DATA_FILE /data/tracked_links.json

# Opublikuj port 5000, na którym aplikacja będzie słuchać połączeń
EXPOSE 5000

# Uruchom aplikację
CMD ["python", "app_flask.py"]
