import { useEffect, useState } from 'react';
import { ArrowRight, BarChart3, Building2, Check, Database, House, LayoutDashboard, Menu, RefreshCw, X } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { request } from './api';
import Dashboard from './Dashboard';
import { featureOptions } from './featureOptions';

const tabs = [
  ['dashboard', 'Dashboard', LayoutDashboard], ['predict', 'Wycena nieruchomości', House],
  ['models', 'Porównanie modeli', BarChart3], ['eda', 'Analiza danych', Database],
];
const money = value => new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
const number = value => new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 3 }).format(value);

function Notice({ children, error = false }) {
  return <div role={error ? 'alert' : 'status'} className={`notice ${error ? 'error' : ''}`}>{children}</div>;
}

function Chart({ data, x, y, currency = false }) {
  return <div className="chart" role="img" aria-label={`Wykres: ${y} według ${x}`}><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 15, right: 15, bottom: 45, left: 15 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e7edf6"/><XAxis dataKey={x} tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={65}/><YAxis tick={{ fontSize: 11 }} width={65}/><Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #dce5f5", boxShadow: "0 8px 30px #1b355515", fontSize: 12 }} cursor={{ fill: "#eff4fe" }} formatter={value => currency ? money(value) : number(value)}/><Bar dataKey={y} fill="#4679e7" radius={[6, 6, 0, 0]} maxBarSize={52}/></BarChart></ResponsiveContainer></div>;
}

function Predict({ featureSchema, info }) {
  const [values, setValues] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const schema = featureSchema?.schema;
  const groups = [
    { title: 'Podstawowe informacje', keys: ['OverallQual', 'GrLivArea', 'YearBuilt', 'YearRemodAdd'] },
    { title: 'Powierzchnie i pomieszczenia', keys: ['LotArea', 'TotalBsmtSF', 'GarageCars', 'FullBath', 'BedroomAbvGr', 'TotRmsAbvGrd'] },
    { title: 'Lokalizacja i zabudowa', keys: ['Neighborhood', 'HouseStyle', 'BldgType'] },
  ];
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError(''); setResult(null);
    try {
      const payload = Object.fromEntries(Object.entries(schema.properties).map(([key, field]) => {
        const type = field.type || field.anyOf?.find(item => item.type !== 'null')?.type;
        const value = values[key];
        return [key, value === undefined || value === '' ? null : type === 'string' ? value.trim() : Number(value)];
      }));
      setResult(await request('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }));
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }
  return <div className="prediction-layout"><section className="card"><span className="eyebrow">PARAMETRY DOMU</span><h3>Opisz swoją nieruchomość</h3><p className="muted">Pola z * są wymagane. Nie znasz wszystkich parametrów? Pola opcjonalne możesz zostawić puste. Powierzchnię podaj w ft² (m² × 10,764).</p>{!schema ? <Notice>Formularz wymaga połączenia z API. Uruchom backend i odśwież dane.</Notice> : <form onSubmit={submit}>{groups.map((group, index) => <fieldset className="form-section" key={group.title}><legend><span>0{index + 1}</span>{group.title}</legend><div className="form-grid">{group.keys.map(key => {
    const field = schema.properties[key];
    const definition = field.anyOf?.find(item => item.type !== 'null') || field;
    const numeric = definition.type !== 'string';
    const choices = featureOptions[key];
    const updateValue = event => {
      setValues(previous => ({ ...previous, [key]: event.target.value }));
      setResult(null);
    };
    return <label key={key} htmlFor={key}>
      {choices?.title || field.title}{schema.required.includes(key) ? ' *' : ''}
      {choices ? <>
        <select id={key} value={values[key] ?? ''} onChange={updateValue}
          required={schema.required.includes(key)} aria-describedby={`${key}-hint`}>
          <option value="">Nie wiem / nie podano</option>
          {choices.options.map(([code, label]) => <option key={code} value={code}>{label}</option>)}
        </select>
        <small className="field-hint" id={`${key}-hint`}>{choices.hint}</small>
      </> : <input id={key} type={numeric ? 'number' : 'text'} required={schema.required.includes(key)} min={definition.minimum ?? (definition.exclusiveMinimum != null ? definition.exclusiveMinimum + 0.01 : undefined)} max={definition.maximum} minLength={definition.minLength} maxLength={definition.maxLength} step={definition.type === 'integer' ? '1' : 'any'} value={values[key] ?? ''} placeholder="Wpisz wartość" onChange={updateValue}/>}
    </label>;
  })}</div></fieldset>)}{error && <Notice error>{error}</Notice>}<button className="button" disabled={loading || !info}>{loading ? 'Obliczanie…' : 'Oblicz przewidywaną cenę'}<ArrowRight size={17}/></button>{!info && <p className="muted mt-3">Wycena będzie dostępna po wytrenowaniu i wczytaniu modelu.</p>}</form>}</section><aside className="card result-card" aria-live="polite"><span className="eyebrow">TWOJA WYCENA</span><House size={40} className="result-icon"/>{result ? <><span className="price">{money(result.price_usd)}</span><h3>Przewidywana cena</h3><p>Model: {result.model_name}</p><small>Wersja: {result.model_version}</small></> : <><h3>Tu pojawi się wynik</h3><p>Uzupełnij parametry domu i uruchom wycenę.</p></>}<div className="result-note">Projekt badawczy dotyczy historycznych danych z Ames w USA. Wynik nie jest aktualną wyceną nieruchomości w Polsce.</div></aside></div>;
}

function Models({ metrics }) {
  if (!metrics) return <Empty title="Porównanie zaczyna się od eksperymentu" text="Uruchom trening, aby zobaczyć rzeczywiste metryki trzech modeli. Żadne wyniki nie zostały jeszcze wczytane."/>;
  const data = metrics.comparison.map(row => ({ model: row.model.replace('Regressor', ''), RMSE: row.cv_mean.RMSE }));
  return <><section className="card"><span className="eyebrow">WALIDACJA KRZYŻOWA · 5 FOLDÓW</span><h3>Porównanie jakości prognoz</h3><p className="muted">Niższe MAE, RMSE i RMSLE oznaczają mniejszy błąd. Wyższe R² oznacza lepsze dopasowanie. Tabela: średnia ± odchylenie standardowe.</p><Chart data={data} x="model" y="RMSE" currency/><div className="table-scroll"><table><thead><tr><th>Model</th>{['MAE (USD)', 'RMSE (USD)', 'R²', 'RMSLE'].map(key => <th key={key}>{key}</th>)}</tr></thead><tbody>{metrics.comparison.map(row => <tr key={row.model}><td>{row.model}{row.model === metrics.selected_model && <span className="winner"><Check size={12}/> Wybrany</span>}</td>{['MAE', 'RMSE', 'R2', 'RMSLE'].map(key => <td key={key}>{number(row.cv_mean[key])} ± {number(row.cv_std[key])}</td>)}</tr>)}</tbody></table></div></section><section className="card mt-6"><span className="eyebrow">KOŃCOWA OCENA · TEST 20%</span><h3>{metrics.selected_model}</h3><p className="muted">Test wykonano wyłącznie dla zwycięzcy wybranego na podstawie walidacji.</p><div className="metric-grid">{Object.entries(metrics.test).map(([key, value]) => <div key={key}><small>{key}</small><strong>{['MAE', 'RMSE'].includes(key) ? money(value) : number(value)}</strong></div>)}</div></section></>;
}

function Empty({ title, text }) { return <section className="card empty"><Database size={38}/><h3>{title}</h3><p>{text}</p><code>python -m scripts.train</code><small>Uruchom w katalogu backend po pobraniu train.csv.</small></section>; }

function Analysis({ eda }) {
  if (!eda) return <Empty title="Najpierw poznajmy dane" text="Wykresy powstaną z rzeczywistych danych podczas treningu. Pobierz train.csv z Kaggle i uruchom skrypt."/>;
  return <><Notice>{eda.scope} Liczba obserwacji: {eda.rows}.</Notice><div className="eda-grid"><section className="card"><h3>Rozkład cen sprzedaży</h3><p className="muted">Cena w USD · liczba nieruchomości w przedziale</p><Chart data={eda.histogram} x="price" y="count"/></section><section className="card"><h3>Korelacje z SalePrice</h3><p className="muted">15 najsilniejszych korelacji Pearsona</p><Chart data={eda.correlations} x="feature" y="value"/></section><section className="card"><h3>Brakujące wartości</h3>{eda.missing.length ? <><Chart data={eda.missing.slice(0, 12)} x="feature" y="count"/><details><summary>Pełna lista braków</summary><div className="table-scroll"><table><tbody>{eda.missing.map(row => <tr key={row.feature}><td>{row.feature}</td><td>{row.count}</td></tr>)}</tbody></table></div></details></> : <p>Brak brakujących wartości.</p>}</section><section className="card"><h3>Obserwacje odstające</h3><strong className="outlier-number">{eda.outliers.count}</strong><p className="muted">{eda.outliers.method}. Granice: {money(eda.outliers.lower)} – {money(eda.outliers.upper)}. Obserwacje pozostają w zbiorze.</p><details><summary>Typy kolumn ({Object.keys(eda.dtypes).length})</summary><div className="table-scroll"><table><tbody>{Object.entries(eda.dtypes).map(([key, value]) => <tr key={key}><td>{key}</td><td>{value}</td></tr>)}</tbody></table></div></details></section></div></>;
}

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const [menu, setMenu] = useState(false);
  const [state, setState] = useState({ loading: true, errors: [], info: null, metrics: null, eda: null, features: null });
  async function refresh() {
    setState(previous => ({ ...previous, loading: true, errors: [] }));
    const paths = ['/features', '/model/info', '/model/metrics', '/data/eda'];
    const results = await Promise.allSettled(paths.map(path => request(path)));
    const value = index => results[index].status === 'fulfilled' ? results[index].value : null;
    setState({ loading: false, features: value(0), info: value(1), metrics: value(2), eda: value(3), errors: [...new Set(results.filter(row => row.status === 'rejected').map(row => row.reason.message))] });
  }
  useEffect(() => { refresh(); }, []);
  useEffect(() => {
    if (!menu) return;
    function closeOnEscape(event) { if (event.key === 'Escape') setMenu(false); }
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [menu]);
  function navigate(key) { setTab(key); setMenu(false); }
  return <div className="app-shell">{menu && <button className="menu-backdrop" aria-label="Zamknij menu" onClick={() => setMenu(false)}/>}<aside className={`sidebar ${menu ? 'open' : ''}`}><a className="brand" href="#" onClick={event => { event.preventDefault(); navigate('dashboard'); }}><span className="brand-icon"><Building2 size={24}/></span><span>Dom<span className="brand-accent">etria</span><small>PRZEWIDYWANIE CEN</small></span></a><div className="nav-label">PRZESTRZEŃ PROJEKTU</div><nav id="main-navigation" aria-label="Nawigacja główna">{tabs.map(([key, label, Icon]) => <button key={key} aria-current={tab === key ? 'page' : undefined} className={`nav-item ${tab === key ? 'active' : ''}`} onClick={() => navigate(key)}><Icon size={19}/>{label}{tab === key && <span className="nav-dot"/>}</button>)}</nav></aside><div className="main-shell"><header className="topbar"><button className="mobile-menu" aria-expanded={menu} aria-controls="main-navigation" aria-label={menu ? 'Zamknij menu' : 'Otwórz menu'} onClick={() => setMenu(!menu)}>{menu ? <X/> : <Menu/>}</button><span>Projekt zespołowy <span className="crumb">/</span> <strong>{tabs.find(item => item[0] === tab)[1]}</strong></span></header><main><div className="page-heading"><div><span className="eyebrow">PRZEWIDYWANIE CEN NIERUCHOMOŚCI</span><h1>{tab === 'dashboard' ? 'Przegląd projektu' : tabs.find(item => item[0] === tab)[1]}</h1><p>{tab === 'dashboard' ? 'Dane, eksperymenty i prognozy — wszystko w jednym miejscu.' : 'Dane historyczne z Ames, Iowa · ceny w USD'}</p></div><button className="refresh" onClick={refresh} disabled={state.loading} aria-label="Odśwież dane"><RefreshCw size={16} className={state.loading ? 'animate-spin' : ''}/><span>Odśwież</span></button></div>{state.loading ? <Notice>Ładowanie danych projektu…</Notice> : state.errors.map(error => <Notice key={error} error>{error}</Notice>)}{tab === 'dashboard' && <Dashboard info={state.info} metrics={state.metrics} setTab={navigate}/>} {tab === 'predict' && <Predict featureSchema={state.features} info={state.info}/>} {tab === 'models' && <Models metrics={state.metrics}/>} {tab === 'eda' && <Analysis eda={state.eda}/>}</main></div></div>;
}
