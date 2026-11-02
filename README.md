# PrzewidywanieCenNieruchomosci

Projekt na przedmiot Wydziałowy projekt zespołowy. Aplikacja przewiduje ceny domów z Ames w Iowa na podstawie danych House Prices z Kaggle. Ceny są w USD, a powierzchnie w stopach kwadratowych (ft²). To historyczne dane amerykańskie, nie aktualne ceny mieszkań w Polsce.

Zespół: Paweł Jagłowski, Eryk Kretowicz, Karol Makarewicz, Damian Nowacki.
Termin oddania: 22 listopada 2026.

## Wymagania

- Python 3.11–3.13 (polecamy 3.11; przypięte biblioteki nie są przygotowane dla 3.14).
- Node.js 22.12+ i npm.
- Konto Kaggle do pobrania danych.

## Instalacja

Komendy dla PowerShell, zaczynając w katalogu projektu:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt -c backend/requirements-lock.txt
cd frontend
npm.cmd ci
cd ..
```

Jeśli `py` nie działa, podaj pełną ścieżkę do zainstalowanego Pythona 3.11 zamiast `py -3.11`. Nie trzeba aktywować środowiska ani zmieniać polityki wykonywania skryptów PowerShell. Na Linux/macOS środowisko tworzy się przez `python3.11 -m venv .venv`, a interpreter to `.venv/bin/python`; użyj `npm` zamiast `npm.cmd`.

`requirements-lock.txt` zapisuje również wersje zależności pośrednich ze sprawdzonego środowiska Python 3.11 na Windows. Frontend ma plik `package-lock.json`, używany przez `npm ci`.

## Dane

1. Otwórz [House Prices na Kaggle](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data).
2. Zaloguj się i zaakceptuj zasady konkursu, jeśli serwis o to poprosi.
3. Pobierz archiwum z danymi i wypakuj `train.csv` do `data/raw/train.csv`.
4. Warto pobrać też `data_description.txt`, który wyjaśnia kody cech. Plik `test.csv` z Kaggle nie jest potrzebny: własny zbiór testowy wydzielamy z `train.csv`.

Danych ani modeli nie dodajemy do repozytorium. Bez `train.csv` można uruchomić frontend, API i testy, ale nie można przeprowadzić treningu ani uzyskać rzeczywistej wyceny i EDA.

## Trening

Z katalogu głównego:

```powershell
cd backend
..\.venv\Scripts\python.exe -m scripts.train
```

Skrypt trenuje od zera LinearRegression, RandomForestRegressor i HistGradientBoostingRegressor. Używa 13 cech dostępnych w formularzu. Podział 80/20 i KFold 5-fold mają `random_state=42`. Najlepszy model wybierany jest według średniego RMSE w walidacji. Dopiero ten model oceniany jest na zbiorze testowym.

Każde uruchomienie tworzy katalog `models/<wersja>/` z:

- kompletnymi pipeline w plikach joblib,
- `metrics.json`: metryki, parametry, wersje bibliotek, suma SHA-256 danych i indeksy podziału,
- `comparison.csv`, `cv_folds.csv`, `test.csv`: wyniki do sprawozdania,
- `eda.json` i `eda.png`: analiza części treningowej.

Plik `models/current.json` wskazuje aktualny eksperyment. Po ponownym treningu zrestartuj działające API. Nie uruchamiaj dwóch treningów jednocześnie do tego samego katalogu. Własne ścieżki można podać argumentami `--data`, `--models` i `--output`. Ładuj wyłącznie własne, zaufane pliki joblib.

## Backend

W katalogu `backend`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Dokumentacja API: http://127.0.0.1:8000/docs. Uruchomienie API nie wykonuje treningu.

Endpointy:

- `GET /api/health` — stan API i dostępność modelu,
- `GET /api/model/info` — nazwa, wersja i cechy,
- `GET /api/model/metrics` — walidacja modeli i test zwycięzcy,
- `GET /api/features` — schemat formularza i jednostki,
- `GET /api/data/eda` — dane do wykresów EDA,
- `POST /api/predict` — prognoza ceny.

Przykładowe dane wejściowe (to przykład formularza, nie wynik eksperymentu):

```json
{"OverallQual": 7, "GrLivArea": 1500, "YearBuilt": 2000}
```

Pozostałe cechy są opcjonalne. Braki uzupełnia pipeline. Nieznane kategorie są obsługiwane przez encoder. API odrzuca dodatkowe pola i wartości spoza zakresów. Brak modelu daje błąd 503, a nieprawidłowe dane wejściowe 422.

Opcjonalne zmienne środowiskowe backendu:

- `MODEL_DIR` — pełna ścieżka do katalogu modeli,
- `CORS_ORIGINS` — adresy rozdzielone przecinkami; domyślnie `http://localhost:5173,http://127.0.0.1:5173`.

## Frontend

W drugim terminalu, z katalogu głównego:

```powershell
cd frontend
npm.cmd run dev
```

Otwórz http://127.0.0.1:5173. Vite przekazuje `/api` do backendu na porcie 8000. Dla innego adresu API skopiuj `frontend/.env.example` do `frontend/.env` i ustaw np. `VITE_API_URL=http://127.0.0.1:8000`. Po zmianie uruchom Vite ponownie. Przy osobnym hostowaniu buildu ustaw adres API przed buildem i dopisz adres strony do CORS backendu.

## Sprawdzenie projektu

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
cd ../frontend
npm.cmd run build
```

Testy nie potrzebują danych Kaggle. Niewielkie dane syntetyczne są używane tylko w testach i nie są zapisywane jako wyniki badań.

## Katalogi

`backend/app` zawiera API, walidację, obsługę modelu i ML. `backend/scripts` zawiera trening. `frontend` to React, Vite, Tailwind i Recharts. `data` i `models` przechowują lokalne dane i wyniki. W `docs` są konspekt, metodologia i szablon eksperymentów, a w `notebooks` instrukcja pracy z analizą.
