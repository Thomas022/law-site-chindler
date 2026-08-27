import { sitePath } from './site-paths';

export default function MobileMenu() {
  return <details className="mobile-menu">
    <summary aria-label="Abrir menu de navegação"><span/><span/><span/></summary>
    <div className="mobile-menu-panel">
      <a href={sitePath('/imoveis/')}>Balcão de Imóveis</a>
      <details className="mobile-condo-menu">
        <summary className="mobile-condo-toggle">Condomínio</summary>
        <div className="mobile-condo-options">
          <a href={sitePath('/condominio/servicos/')}>Serviços</a>
          <a href={sitePath('/condominio/diferenciais/')}>Diferenciais da Chindler</a>
          <a href={sitePath('/condominio/taxa-administrativa/')}>Taxa Administrativa</a>
        </div>
      </details>
      <a href={sitePath('/#contato')}>Contato</a>
      <a className="mobile-portal" href="https://admin107486.superlogica.net/clients/areadocondomino" target="_blank" rel="noreferrer">Portal do Cliente</a>
    </div>
  </details>;
}
