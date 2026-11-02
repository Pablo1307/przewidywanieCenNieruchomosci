# Metodologia

## Dane i podział

Plik `train.csv` zawiera cel `SalePrice`. `Id` nie jest cechą predykcyjną. Przed analizą dzielimy wiersze przez `train_test_split(test_size=0.2, random_state=42)`. Test pozostaje poza wyborem modelu. Sprawdzamy wymagane kolumny, poprawność liczb i nieujemny cel bez braków. Nie usuwamy obserwacji odstających automatycznie.

EDA dotyczy tylko części treningowej: histogram cen, wykres pudełkowy, braki, typy kolumn i korelacje Pearsona. Odstające ceny wskazuje reguła 1,5 IQR. Analiza obejmuje też kolumny, których nie używamy w modelach. Korelacja nie dowodzi związku przyczynowego.

## Cechy

W pierwszej wersji świadomie wybieramy 13 cech możliwych do podania w formularzu. Ten sam zestaw obowiązuje wszystkie modele, walidację i API. Nie dobieramy cech na podstawie testu.

Liczbowe: `OverallQual`, `GrLivArea`, `YearBuilt`, `LotArea`, `TotalBsmtSF`, `GarageCars`, `FullBath`, `BedroomAbvGr`, `TotRmsAbvGrd`, `YearRemodAdd`.

Kategoryczne: `Neighborhood`, `HouseStyle`, `BldgType`.

W formularzu wymagane są jakość, powierzchnia nadziemna i rok budowy. Pozostałe wartości mogą być puste. Dzielnicę, typ domu i rodzaj zabudowy wybiera się z list z czytelnymi nazwami. Formularz wysyła odpowiadające im kody Kaggle. Opcja „Nie wiem / nie podano” wysyła null, który obsługuje imputacja w pipeline. Wszystkie powierzchnie są w ft²; przeliczenie: m² × 10,764. Model nie jest przeznaczony do współczesnych ofert w innych miastach.

## Preprocessing i modele

`ColumnTransformer` łączy dwie gałęzie. Liczbowe braki wypełnia mediana, a kategoryczne osobna wartość `Missing`. Puste w całości kolumny zachowujemy (`keep_empty_features=True`). `OneHotEncoder(handle_unknown='ignore')` obsługuje nowe kategorie. Nieznana kategoria ma zerowe kodowanie, więc nie należy traktować jej prognozy jak dobrze reprezentowanej kategorii.

Regresja liniowa ma dodatkowo `StandardScaler` i pomija pierwszą kategorię w kodowaniu. Modele drzewiaste nie wymagają skalowania. Wszystkie modele otrzymują gęstą macierz, kompatybilną z HistGradientBoostingRegressor. Przy trzech cechach kategorycznych taki wariant jest prosty i ma niewielki koszt pamięci; rozszerzenie na wszystkie kolumny wymaga ponownego sprawdzenia tego założenia.

Preprocessing i estymator są jednym `Pipeline`. W każdym foldzie tworzony jest nowy pipeline, dopasowany tylko na treningowej części foldu. Zapobiega to przenikaniu informacji z walidacji przez imputację, skalowanie lub kodowanie.

- LinearRegression: model bazowy, domyślne parametry.
- RandomForestRegressor: 300 drzew, `min_samples_leaf=2`, `random_state=42`, `n_jobs=1`.
- HistGradientBoostingRegressor: 200 iteracji, learning rate 0,08, `random_state=42`, `early_stopping=False`.

Nie przeprowadzamy strojenia hiperparametrów. Jeśli zostanie dodane, musi odbywać się wewnątrz treningu, bez użycia testu.

## Walidacja i metryki

`KFold(n_splits=5, shuffle=True, random_state=42)` działa wyłącznie na 80% danych. Wszystkie modele dostają te same foldy. Zapisujemy metryki każdego foldu, średnie i odchylenia standardowe próbki. Wygrywa najniższa średnia RMSE. Następnie oceniamy zwycięzcę raz na odłożonych 20%. Nie porównujemy trzech modeli na teście.

- MAE = średnia wartości bezwzględnych błędów; jednostka USD.
- RMSE = pierwiastek średniej kwadratów błędów; jednostka USD, silniej karze duże błędy.
- R² = 1 − suma kwadratów reszt / suma kwadratów odchyleń celu od średniej; może być ujemne.
- RMSLE = pierwiastek średniej kwadratów różnic `log1p(y)` i `log1p(prognoza)`.

Prognozy ujemne przycinamy do zera przed wszystkimi metrykami i w API. Dzięki temu ocena odpowiada zachowaniu aplikacji, a RMSLE ma poprawną dziedzinę. Cel musi być nieujemny. Nie używamy transformacji logarytmicznej celu podczas dopasowania.

## Odtwarzalność

Wymagane są te same dane (SHA-256), wersje bibliotek i konfiguracja. `metrics.json` zawiera parametry estymatorów, środowisko i indeksy podziału. Pełny preprocessing jest zapisany razem z modelem. Czas utworzenia daje unikalną wersję, ale nie wpływa na losowanie. Drobne różnice obliczeń między systemami są możliwe. API nie trenuje modeli. Po zmianie wersji należy je zrestartować.

## Ograniczenia

Wynik jest pojedynczą estymacją, nie przedziałem ufności. Nie uwzględnia aktualnej inflacji, kursów walut ani sytuacji polskiego rynku. Przyjęty podział losowy nie ocenia generalizacji w czasie lub na nowe miasta. Formularz ogranicza wartości technicznie, ale nie gwarantuje, że podany dom mieści się w rozkładzie treningowym. Nie formułujemy wniosków o skuteczności przed uruchomieniem eksperymentów.

Dokumentacja używanych narzędzi: [Pipeline](https://scikit-learn.org/stable/modules/compose.html), [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html).
