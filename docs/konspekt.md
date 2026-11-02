# Konspekt

## Temat i cel

Przewidywanie cen nieruchomości z użyciem uczenia maszynowego. Chcemy stworzyć aplikację webową i porównać trzy samodzielnie wytrenowane modele regresji. Projekt realizujemy na Wydziałowy projekt zespołowy. Termin: 22 listopada 2026.

## Problem

Cena domu zależy m.in. od powierzchni, jakości, lokalizacji i wieku budynku. Badamy, jak dobrze można ją oszacować na podstawie danych tabelarycznych. Wynik ma charakter edukacyjny i dotyczy historycznego rynku Ames w Iowa.

## Hipotezy badawcze

1. Modele drzewiaste osiągną niższe średnie RMSE walidacyjne niż regresja liniowa.
2. Powierzchnia nadziemna i jakość wykończenia będą dodatnio skorelowane z ceną w części treningowej.
3. Domy o skrajnych cenach będą trudniejsze do przewidzenia niż typowe nieruchomości. Do sprawdzenia tej hipotezy potrzebna będzie dodatkowa analiza reszt na predykcjach walidacyjnych.

Hipotezy nie są wynikami. Potwierdzenie lub odrzucenie nastąpi po eksperymentach.

## Technologie i dane

React, Vite, Tailwind CSS, Recharts; Python 3.11+, FastAPI, Uvicorn, Pydantic; pandas, NumPy, scikit-learn, matplotlib, joblib i pytest.

Źródło: [Kaggle House Prices](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data). Korzystamy z `train.csv` z celem `SalePrice`. Jednostka ceny to USD, powierzchni ft². Dane pobiera się ręcznie po zapoznaniu z zasadami Kaggle. Nie dołączamy ich do repozytorium.

## Metodologia

Stały podział 80/20, EDA treningu, preprocessing wewnątrz pipeline, 5-fold CV i wybór według RMSE. Porównujemy LinearRegression, RandomForestRegressor i HistGradientBoostingRegressor. Testujemy wyłącznie zwycięzcę. Metryki: MAE, RMSE, R², RMSLE. Zapisujemy modele, wyniki i konfigurację. Nie korzystamy z gotowych wag ani notebooków konkursowych.

## Wstępny podział zadań

| Osoba | Proponowany zakres |
| --- | --- |
| Paweł Jagłowski | API, integracja, konfiguracja projektu |
| Eryk Kretowicz | Pobranie danych, EDA, opis zbioru |
| Karol Makarewicz | Pipeline, trening, walidacja, opis eksperymentów |
| Damian Nowacki | Interfejs, wizualizacje, testy integracji |

Podział jest propozycją do uzgodnienia. Dokumentację i końcowy przegląd wykonujemy wspólnie.

## Plan prac

- 2–7 listopada: przygotowanie środowiska, danych i EDA.
- 8–14 listopada: eksperymenty, API i formularz.
- 15–19 listopada: integracja, testy, opis rzeczywistych wyników.
- 20–22 listopada: sprawdzenie odtwarzalności, prezentacja i oddanie.
