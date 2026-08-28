'use client';

import { useEffect, useMemo, useState } from 'react';
import logoChindler from '../../logo_chindler_peq_nova.png';
import fallbackPhoto from '../../Banner1.png';
import { emptyFilters, fetchFilterOptions, fetchProperties, type ApiProperty, type FilterOptions, type PropertyPage } from './imoveis';
import { sitePath } from '../site-paths';
import MobileMenu from '../MobileMenu';

function ImovelCard({ imovel }: { imovel: ApiProperty }) {
  const [foto, setFoto] = useState(0);
  const imagens = useMemo(() => imovel.images.filter((image) => image.url), [imovel.images]);
  const anterior = () => setFoto((atual) => (atual - 1 + imagens.length) % imagens.length);
  const proxima = () => setFoto((atual) => (atual + 1) % imagens.length);
  const imagem = imagens[foto];
  return <article className="property-card"><div className="property-photo">
    <img src={imagem?.url ?? fallbackPhoto.src} alt={imagem?.alt_text || `${imovel.title} — foto ${foto + 1}`} />
    {imovel.is_featured && <span className="featured">Destaque</span>}<span className="purpose">{imovel.purpose_label}</span>
    {imagens.length > 1 && <><div className="gallery-controls"><button type="button" onClick={anterior} aria-label={`Foto anterior de ${imovel.title}`}>‹</button><span>{foto + 1} / {imagens.length}</span><button type="button" onClick={proxima} aria-label={`Próxima foto de ${imovel.title}`}>›</button></div><div className="gallery-dots" aria-hidden="true">{imagens.map((_, index) => <i className={index === foto ? 'active' : ''} key={index} />)}</div></>}
  </div><div className="property-card-body">
    <p className="property-location">{imovel.property_type_label} • {imovel.address.neighborhood}</p><h3>{imovel.title}</h3>
    <div className="property-features">{!!imovel.bedrooms && <span>{imovel.bedrooms} quartos</span>}{!!imovel.bathrooms && <span>{imovel.bathrooms} banheiros</span>}<span>{Number(imovel.total_area).toLocaleString('pt-BR')} m²</span></div>
    <div className="property-price"><div><strong>{imovel.price_display}</strong>{imovel.purpose === 'rent' && imovel.price && <span>/mês</span>}</div><a href={`${sitePath('/imoveis/detalhes/')}?id=${encodeURIComponent(imovel.id)}`} aria-label={`Ver detalhes de ${imovel.title}`}>→</a></div>
  </div></article>;
}

export default function ImoveisPage() {
  const [purpose, setPurpose] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [neighborhood, setNeighborhood] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [page, setPage] = useState(1);
  const [properties, setProperties] = useState<PropertyPage | null>(null);
  const [filters, setFilters] = useState<FilterOptions>(emptyFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);

  useEffect(() => { const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 350); return () => window.clearTimeout(timer); }, [search]);
  useEffect(() => {
    const controller = new AbortController();
    fetchFilterOptions(controller.signal).then(setFilters).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === 'AbortError')) setError(reason instanceof Error ? reason.message : 'Não foi possível carregar os filtros.');
    });
    return () => controller.abort();
  }, [reload]);
  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({ page: String(page), ordering: 'featured' });
    if (purpose) params.set('purpose', purpose);
    if (propertyType) params.set('property_type', propertyType);
    if (neighborhood) params.set('neighborhood', neighborhood);
    if (debouncedSearch) params.set('search', debouncedSearch);
    fetchProperties(params, controller.signal).then(setProperties).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === 'AbortError')) setError(reason instanceof Error ? reason.message : 'Não foi possível carregar os imóveis.');
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [purpose, propertyType, neighborhood, debouncedSearch, page, reload]);

  const startRequest = () => { setLoading(true); setError(''); };
  const changeFilter = (setter: (value: string) => void, value: string) => { startRequest(); setter(value); setPage(1); };
  const limpar = () => { startRequest(); setPurpose(''); setPropertyType(''); setNeighborhood(''); setSearch(''); setPage(1); };

  return <main className="property-page">
    <header className="nav"><a className="brand" href={sitePath('/')} aria-label="Chindler, início"><img className="brand-logo" src={logoChindler.src} alt="Chindler" /></a><nav aria-label="Navegação principal"><a href={sitePath('/imoveis/')}>Balcão de Imóveis</a><div className="nav-dropdown"><button type="button" aria-haspopup="true">Condomínio <span aria-hidden="true">⌄</span></button><div className="dropdown-menu"><a href={sitePath('/condominio/servicos/')}>Serviços</a><a href={sitePath('/condominio/diferenciais/')}>Diferenciais da Chindler</a><a href={sitePath('/condominio/taxa-administrativa/')}>Taxa Administrativa</a></div></div><a href={sitePath('/#contato')}>Contato</a></nav><a className="nav-cta" href="https://admin107486.superlogica.net/clients/areadocondomino" target="_blank" rel="noreferrer">Portal do Cliente</a><MobileMenu /></header>
    <section className="property-hero"><div><p className="eyebrow">BALCÃO DE IMÓVEIS • RIO DE JANEIRO</p><h1>Encontre o lugar certo para <em>o seu momento.</em></h1><p>Imóveis selecionados para comprar ou alugar, com atendimento próximo e segurança em todas as etapas.</p></div></section>
    <section className="property-search" aria-label="Busca de imóveis"><div className="purpose-tabs"><button className={!purpose ? 'active' : ''} onClick={() => changeFilter(setPurpose, '')}>Todos</button>{filters.purposes.map((item) => <button key={item.value} className={purpose === item.value ? 'active' : ''} onClick={() => changeFilter(setPurpose, item.value)}>{item.label}</button>)}</div><div className="filter-row"><label>BUSCAR<input value={search} onChange={(event) => { startRequest(); setSearch(event.target.value); setPage(1); }} placeholder="Bairro ou palavra-chave" /></label><label>TIPO<select value={propertyType} onChange={(event) => changeFilter(setPropertyType, event.target.value)}><option value="">Todos</option>{filters.property_types.map((item) => <option value={item.value} key={item.value}>{item.label}</option>)}</select></label><label>BAIRRO<select value={neighborhood} onChange={(event) => changeFilter(setNeighborhood, event.target.value)}><option value="">Todos</option>{filters.neighborhoods.map((item) => <option key={item}>{item}</option>)}</select></label><div className="filter-count"><strong>{properties?.count ?? 0}</strong><span>imóveis encontrados</span></div></div></section>
    <section className="property-results" aria-busy={loading}><div className="results-head"><div><p className="section-label">IMÓVEIS SELECIONADOS</p><h2>Comprar ou alugar com <em>tranquilidade.</em></h2></div><p>A Chindler acompanha você da busca à assinatura do contrato.</p></div>
      {loading && <div className="property-status" role="status"><span className="loading-mark" />Carregando imóveis…</div>}
      {!loading && error && <div className="empty-results api-error"><h3>Não foi possível acessar o Balcão.</h3><p>{error}</p><button onClick={() => { startRequest(); setReload((value) => value + 1); }}>Tentar novamente</button></div>}
      {!loading && !error && properties?.results.length ? <><div className="property-grid">{properties.results.map((property) => <ImovelCard imovel={property} key={property.id} />)}</div>{(properties.previous || properties.next) && <nav className="property-pagination" aria-label="Paginação dos imóveis"><button disabled={!properties.previous} onClick={() => { startRequest(); setPage((value) => Math.max(1, value - 1)); }}>← Anterior</button><span>Página {page}</span><button disabled={!properties.next} onClick={() => { startRequest(); setPage((value) => value + 1); }}>Próxima →</button></nav>}</> : null}
      {!loading && !error && properties && !properties.results.length && <div className="empty-results"><h3>Nenhum imóvel encontrado.</h3><p>Tente remover algum filtro ou buscar por outro bairro.</p><button onClick={limpar}>Limpar filtros</button></div>}
    </section>
    <section className="inner-cta"><p className="section-label">ATENDIMENTO CHINDLER</p><h2>Não encontrou o imóvel ideal?</h2><p className="property-cta-copy">Conte o que você procura e nossa equipe ajuda a encontrar as melhores opções.</p><a className="button light" href={sitePath('/#contato')}>Fale com a Chindler <span>→</span></a></section>
    <footer><div className="brand"><img className="brand-logo footer-logo" src={logoChindler.src} alt="Chindler" /></div><div className="footer-details"><p>Av. Rio Branco, 109 - 18º Andar<br />Centro - Rio de Janeiro - RJ</p><a className="footer-contact" href="tel:+552122216453"><span aria-hidden="true">☎</span> (21) 2221-6453</a><br /><a className="footer-privacy" href={sitePath('/privacidade/')}>Política de Privacidade</a></div><p>© 2026 Chindler</p></footer>
  </main>;
}
