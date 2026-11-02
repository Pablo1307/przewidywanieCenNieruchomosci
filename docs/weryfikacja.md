# Sprawdzenie działania

Sprawdzono 2 listopada 2026 na Windows, Python 3.11.18 i Node.js 24.15.0.

- `python -m pytest -q` w katalogu backend: 21 testów zaliczonych, 18 ostrzeżeń, czas 9,39 s.
- `npm.cmd run build` w katalogu frontend: build zakończony powodzeniem, Vite 6.4.1.
- Kontrola składni plików Pythona: poprawna.

Testy obejmują endpointy, brak modelu, uszkodzone artefakty, walidację wejścia, CORS, predykcję z zapisanego pipeline, nieznane kategorie, braki danych, dopasowanie imputacji tylko na treningu i cały przebieg treningu na danych testowych w katalogu tymczasowym.

Ostrzeżenia dotyczą przestarzałych wywołań w zależnościach, oczekiwanej obsługi nowej kategorii oraz wykrywania liczby rdzeni na Windows. Build informuje o pliku JavaScript większym niż 500 kB (około 597 kB, gzip 174 kB). Nie blokuje to działania.

Nie sprawdzono wyglądu i interakcji w przeglądarce. Nie wykonano eksperymentów na danych Kaggle, ponieważ nie pobrano jeszcze `train.csv`. Testy na danych syntetycznych nie potwierdzają jakości modelu na rzeczywistych nieruchomościach.
