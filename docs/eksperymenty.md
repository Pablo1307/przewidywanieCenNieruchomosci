# Eksperymenty

Nie wykonano jeszcze eksperymentów na danych Kaggle. Poniższe pola trzeba uzupełnić po pobraniu `train.csv` i uruchomieniu treningu. Myślnik oznacza brak wyniku.

## Informacje o uruchomieniu

- Data i wersja modelu: —
- Osoba uruchamiająca: —
- Wersja kodu / commit: —
- SHA-256 danych: —
- Wersja Pythona i bibliotek: —
- Liczba wierszy train / test: —
- Uwagi o danych: —

Konfiguracja: 80/20, random_state=42, KFold 5-fold, wybór według średniej RMSE. Szczegóły w `metodologia.md` i `models/<wersja>/metrics.json`.

## Walidacja krzyżowa

Przepisać średnią ± odchylenie standardowe z `comparison.csv`.

| Model | MAE (USD) | RMSE (USD) | R² | RMSLE |
| --- | --- | --- | --- | --- |
| LinearRegression | — | — | — | — |
| RandomForestRegressor | — | — | — | — |
| HistGradientBoostingRegressor | — | — | — | — |

Wybrany model i uzasadnienie na podstawie walidacji: —

## Końcowy test zwycięzcy

Źródło: `test.csv`. Nie używać tych wyników do zmiany wyboru modelu.

| Model | MAE (USD) | RMSE (USD) | R² | RMSLE |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

## EDA i wnioski

- Rozkład cen, braki i odstające obserwacje: —
- Najsilniejsze korelacje w treningu: —
- Czy hipotezy 1 i 2 zostały potwierdzone: —
- Dodatkowa analiza reszt do hipotezy 3 (jeśli wykonana): —
- Różnice między walidacją a testem: —
- Ograniczenia i możliwe dalsze prace: —

Dołączyć wykres `eda.png` i potrzebne tabele z katalogu danej wersji. Testy jednostkowe na syntetycznych danych nie są eksperymentami badawczymi.
