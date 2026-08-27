import logoChindler from '../../logo_chindler_peq_nova.png';
import { sitePath } from '../site-paths';

type Props = { eyebrow: string; title: string; accent: string; intro: string; details: { title: string; copy: string }[]; highlight: string };

export default function CondominioPage({ eyebrow, title, accent, intro, details, highlight }: Props) {
  return <main className="inner-page">
    <header className="nav"><a className="brand" href={sitePath('/')} aria-label="Chindler, início"><img className="brand-logo" src={logoChindler.src} alt="Chindler" /></a><nav aria-label="Navegação principal"><a href={sitePath('/imoveis/')}>Balcão de Imóveis</a><div className="nav-dropdown"><button type="button" aria-haspopup="true">Condomínio <span aria-hidden="true">⌄</span></button><div className="dropdown-menu"><a href={sitePath('/condominio/servicos/')}>Serviços</a><a href={sitePath('/condominio/diferenciais/')}>Diferenciais da Chindler</a><a href={sitePath('/condominio/taxa-administrativa/')}>Taxa Administrativa</a></div></div><a href={sitePath('/#contato')}>Contato</a></nav><a className="nav-cta" href="https://admin107486.superlogica.net/clients/areadocondomino" target="_blank" rel="noreferrer">Portal do Cliente</a></header>
    <section className="inner-hero"><img className="inner-hero-image" src={sitePath('/guanabara-sunset.jpg')} alt="Baía de Guanabara ao pôr do sol" /><div className="inner-hero-shade" /><div className="inner-hero-content"><p className="breadcrumb"><a href={sitePath('/')}>Início</a><span>—</span>Condomínio</p><p className="eyebrow">{eyebrow}</p><h1>{title}<br /><em>{accent}</em></h1></div></section>
    <section className="inner-content"><div className="inner-intro"><p className="section-label">CHINDLER CONDOMÍNIOS</p><p>{intro}</p></div><div className="detail-grid">{details.map((detail,index)=><article className="detail-card" key={detail.title}><span>{String(index+1).padStart(2,'0')}</span><h2>{detail.title}</h2><p>{detail.copy}</p></article>)}</div></section>
    <section className="inner-cta"><p className="section-label">ATENDIMENTO PERSONALIZADO</p><h2>{highlight}</h2><a className="button light" href={sitePath('/#contato')}>Fale com a Chindler <span>→</span></a></section>
    <footer><div className="brand"><img className="brand-logo footer-logo" src={logoChindler.src} alt="Chindler" /></div><div className="footer-details"><p>Av. Rio Branco, 109 - 18º Andar<br />Centro - Rio de Janeiro - RJ</p><a className="footer-contact" href="tel:+552122216453"><span aria-hidden="true">☎</span> (21) 2221-6453</a></div><p>© 2026 Chindler</p></footer>
  </main>;
}
