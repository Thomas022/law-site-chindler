'use client';

import { useEffect, useMemo, useState } from 'react';
import logoChindler from '../../../logo_chindler_peq_nova.png';
import fallbackPhoto from '../../../Banner1.png';
import MobileMenu from '../../MobileMenu';
import { sitePath } from '../../site-paths';
import { fetchProperty, submitInterest, type ApiProperty, type InterestPayload } from '../imoveis';

function Header() {
  return <header className="nav detail-nav"><a className="brand" href={sitePath('/')} aria-label="Chindler, início"><img className="brand-logo" src={logoChindler.src} alt="Chindler" /></a><nav aria-label="Navegação principal"><a href={sitePath('/imoveis/')}>Balcão de Imóveis</a><div className="nav-dropdown"><button type="button" aria-haspopup="true">Condomínio <span aria-hidden="true">⌄</span></button><div className="dropdown-menu"><a href={sitePath('/condominio/servicos/')}>Serviços</a><a href={sitePath('/condominio/diferenciais/')}>Diferenciais da Chindler</a><a href={sitePath('/condominio/taxa-administrativa/')}>Taxa Administrativa</a></div></div><a href={sitePath('/#contato')}>Contato</a></nav><a className="nav-cta" href="https://admin107486.superlogica.net/clients/areadocondomino" target="_blank" rel="noreferrer">Portal do Cliente</a><MobileMenu /></header>;
}

function Footer() {
  return <footer><div className="brand"><img className="brand-logo footer-logo" src={logoChindler.src} alt="Chindler" /></div><div className="footer-details"><p>Av. Rio Branco, 109 - 18º Andar<br />Centro - Rio de Janeiro - RJ</p><a className="footer-contact" href="tel:+552122216453"><span aria-hidden="true">☎</span> (21) 2221-6453</a><br /><a className="footer-privacy" href={sitePath('/privacidade/')}>Política de Privacidade</a></div><p>© 2026 Chindler</p></footer>;
}

function InterestForm({ property }: { property: ApiProperty }) {
  const initialForm: InterestPayload = { name: '', phone: '', email: '', message: `Tenho interesse no imóvel: ${property.title}.`, consent: false, website: '' };
  const [form, setForm] = useState(initialForm);
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const update = (field: keyof InterestPayload, value: string | boolean) => setForm((current) => ({ ...current, [field]: value }));

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSending(true); setError('');
    try { await submitInterest(property.id, form); setSuccess(true); setForm(initialForm); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Não foi possível enviar seu interesse.'); }
    finally { setSending(false); }
  }

  if (success) return <div className="interest-success" role="status"><span>✓</span><h2>Interesse enviado.</h2><p>A equipe Chindler recebeu seus dados e poderá entrar em contato para dar continuidade ao atendimento.</p><button onClick={() => setSuccess(false)}>Enviar outra mensagem</button></div>;

  return <section className="interest-section" id="interesse"><div><p className="section-label">FALE COM A CHINDLER</p><h2>Tenho interesse neste <em>imóvel.</em></h2><p>Preencha seus dados e nossa equipe entrará em contato para esclarecer dúvidas ou agendar uma visita.</p></div><form onSubmit={handleSubmit}>
    <label>Nome completo<input required minLength={2} maxLength={150} autoComplete="name" value={form.name} onChange={(event) => update('name', event.target.value)} /></label>
    <div className="interest-form-row"><label>Telefone<input required minLength={8} maxLength={30} autoComplete="tel" inputMode="tel" placeholder="(21) 99999-9999" value={form.phone} onChange={(event) => update('phone', event.target.value)} /></label><label>E-mail<input required type="email" autoComplete="email" value={form.email} onChange={(event) => update('email', event.target.value)} /></label></div>
    <label>Mensagem<textarea required minLength={10} maxLength={2000} rows={4} value={form.message} onChange={(event) => update('message', event.target.value)} /></label>
    <label className="interest-honeypot" aria-hidden="true">Website<input tabIndex={-1} autoComplete="off" value={form.website} onChange={(event) => update('website', event.target.value)} /></label>
    <label className="interest-consent"><input required type="checkbox" checked={form.consent} onChange={(event) => update('consent', event.target.checked)} /><span>Autorizo a Chindler a utilizar estes dados para entrar em contato sobre este imóvel. Consulte nossa <a href={sitePath('/privacidade/')} target="_blank" rel="noreferrer">Política de Privacidade</a>.</span></label>
    {error && <p className="interest-error" role="alert">{error}</p>}
    <button className="interest-submit" disabled={sending} type="submit">{sending ? 'Enviando…' : 'Enviar interesse'} <span>→</span></button>
  </form></section>;
}

export default function PropertyDetailClient() {
  const [property, setProperty] = useState<ApiProperty | null>(null);
  const [activeImage, setActiveImage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);
  const images = useMemo(() => property?.images.filter((image) => image.url) ?? [], [property]);

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) {
      void Promise.resolve().then(() => { setError('O imóvel não foi informado.'); setLoading(false); });
      return;
    }
    const controller = new AbortController();
    fetchProperty(id, controller.signal).then((result) => {
      setProperty(result); document.title = `${result.title} | Chindler`;
    }).catch((reason: unknown) => {
      if (!(reason instanceof DOMException && reason.name === 'AbortError')) setError(reason instanceof Error ? reason.message : 'Não foi possível carregar o imóvel.');
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [reload]);

  if (loading) return <main className="property-detail-page"><Header /><div className="detail-feedback" role="status"><span className="loading-mark" />Carregando imóvel…</div></main>;
  if (error || !property) return <main className="property-detail-page"><Header /><div className="detail-feedback detail-feedback-error"><h1>Imóvel não encontrado.</h1><p>{error}</p><div><a className="detail-back" href={sitePath('/imoveis/')}>← Voltar ao Balcão</a><button onClick={() => { setLoading(true); setError(''); setReload((value) => value + 1); }}>Tentar novamente</button></div></div></main>;

  const current = images[activeImage];
  const featureItems = [
    property.bedrooms != null && ['Quartos', property.bedrooms],
    property.suites != null && ['Suítes', property.suites],
    property.bathrooms != null && ['Banheiros', property.bathrooms],
    property.parking_spaces != null && ['Vagas', property.parking_spaces],
    ['Área total', `${Number(property.total_area).toLocaleString('pt-BR')} m²`],
  ].filter(Boolean) as [string, string | number][];
  const mapUrl = property.map.visible && property.map.latitude && property.map.longitude
    ? `https://www.google.com/maps?q=${encodeURIComponent(`${property.map.latitude},${property.map.longitude}`)}&z=15&output=embed`
    : '';

  return <main className="property-detail-page"><Header />
    <section className="detail-gallery">
      <div className="detail-gallery-media">
        <img className="detail-main-image" src={current?.url ?? fallbackPhoto.src} alt={current?.alt_text || property.title} />
        {images.length > 1 && <div className="detail-gallery-counter"><button onClick={() => setActiveImage((value) => (value - 1 + images.length) % images.length)} aria-label="Imagem anterior">‹</button><span>{activeImage + 1} / {images.length}</span><button onClick={() => setActiveImage((value) => (value + 1) % images.length)} aria-label="Próxima imagem">›</button></div>}
      </div>
      {images.length > 1 && <div className="detail-thumbnails">{images.map((image, index) => <button className={index === activeImage ? 'active' : ''} onClick={() => setActiveImage(index)} key={`${image.url}-${index}`} aria-label={`Abrir imagem ${index + 1}`}><img src={image.url ?? fallbackPhoto.src} alt="" /></button>)}</div>}
    </section>
    <section className="detail-gallery-copy"><a href={sitePath('/imoveis/')}>← Voltar ao Balcão</a><div><p>{property.purpose_label} • {property.property_type_label}</p><h1>{property.title}</h1><span>{property.address.display}</span></div></section>
    <section className="detail-content"><div className="detail-description"><p className="section-label">SOBRE O IMÓVEL</p><h2>{property.property_type_label} em <em>{property.address.neighborhood}.</em></h2><p>{property.description}</p></div><aside className="detail-summary"><p>{property.purpose_label}</p><strong>{property.price_display}</strong>{property.purpose === 'rent' && property.price && <small>por mês</small>}{property.condominium_fee && <span>Condomínio: R$ {Number(property.condominium_fee).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>}<a href="#interesse">Tenho interesse <b>→</b></a></aside></section>
    <section className="detail-features" aria-label="Características do imóvel">{featureItems.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</section>
    <section className="detail-location"><div><p className="section-label">LOCALIZAÇÃO</p><h2>{property.address.display}</h2><p>{property.map.visible ? 'A posição exibida no mapa é aproximada para preservar a privacidade do imóvel.' : 'Entre em contato com a Chindler para obter mais informações sobre a localização.'}</p></div>{mapUrl && <iframe title={`Localização aproximada de ${property.title}`} src={mapUrl} loading="lazy" referrerPolicy="no-referrer-when-downgrade" />}</section>
    <InterestForm property={property} />
    <section className="inner-cta"><p className="section-label">ATENDIMENTO PERSONALIZADO</p><h2>Gostou deste <em>imóvel?</em></h2><p className="property-cta-copy">Converse com nossa equipe para esclarecer dúvidas e agendar uma visita.</p><a className="button light" href="#interesse">Enviar interesse <span>→</span></a></section>
    <Footer />
  </main>;
}
